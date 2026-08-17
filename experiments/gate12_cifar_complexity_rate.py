"""Gate 12 — CIFAR-10 intrinsic-complexity attack on observer rate.

Preregistered in docs/GATE12_PREREG_CIFAR_COMPLEXITY.md before results.

Primary question: at common validation targets defined by a full-pixel linear
reference, how much compact structured-observer payload / logical width is
needed on a genuinely non-digit task?

No per-rate retraining. Observation maps are quantized after fitting while
linear heads stay frozen. Report map bytes, decoder bytes and egress width
separately.
"""
from __future__ import annotations

import argparse
import copy
import math
from dataclasses import dataclass

import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from torch import nn
from torch.nn import functional as F
from torchvision.datasets import CIFAR10

from gate11_map_rate_distortion import BITS, quantize_pca_rows, quantize_unit

SEEDS = (9300, 9301)
M_VALUES = (16, 32, 64, 128)
TRAIN_N = 12_000
VAL_N = 3_000
BATCH = 256
EPOCHS = 60
LR = 0.02
CLASSES = 10
D = 32 * 32
TARGET_FRACS = (0.95, 0.90)
LUMA = np.array([0.299, 0.587, 0.114], dtype=np.float32)

torch.set_num_threads(2)


@dataclass
class SplitData:
    x: torch.Tensor
    y: torch.Tensor
    xv: torch.Tensor
    yv: torch.Tensor
    xt: torch.Tensor
    yt: torch.Tensor
    mean: float
    std: float


@dataclass
class HeadResult:
    head: nn.Linear
    val_accuracy: float
    test_accuracy: float


@dataclass
class Candidate:
    family: str
    m: int
    bits: str
    map_bytes: int
    head_bytes: int
    val_accuracy: float
    test_accuracy: float

    @property
    def total_bytes(self) -> int:
        return self.map_bytes + self.head_bytes


def _gray(data: np.ndarray) -> np.ndarray:
    x = data.astype(np.float32) / 255.0
    return np.tensordot(x, LUMA, axes=([3], [0])).astype(np.float32)


def load_data(root: str, download: bool, seed: int) -> SplitData:
    tr = CIFAR10(root=root, train=True, download=download)
    te = CIFAR10(root=root, train=False, download=download)

    y_all = np.asarray(tr.targets, dtype=np.int64)
    idx = np.arange(len(y_all))
    chosen, _ = train_test_split(
        idx,
        train_size=TRAIN_N + VAL_N,
        random_state=seed,
        stratify=y_all,
    )
    train_idx, val_idx = train_test_split(
        chosen,
        train_size=TRAIN_N,
        random_state=seed + 1,
        stratify=y_all[chosen],
    )

    x_all = _gray(tr.data)
    xt_np = _gray(te.data)
    x_np = x_all[train_idx]
    xv_np = x_all[val_idx]
    y_np = y_all[train_idx]
    yv_np = y_all[val_idx]
    yt_np = np.asarray(te.targets, dtype=np.int64)

    mean = float(x_np.mean())
    std = float(x_np.std() + 1e-6)
    x_np = (x_np - mean) / std
    xv_np = (xv_np - mean) / std
    xt_np = (xt_np - mean) / std

    def im(a: np.ndarray) -> torch.Tensor:
        return torch.tensor(a[:, None], dtype=torch.float32)

    return SplitData(
        x=im(x_np),
        y=torch.tensor(y_np, dtype=torch.long),
        xv=im(xv_np),
        yv=torch.tensor(yv_np, dtype=torch.long),
        xt=im(xt_np),
        yt=torch.tensor(yt_np, dtype=torch.long),
        mean=mean,
        std=std,
    )


def grid32(device=None):
    yy, xx = torch.meshgrid(
        torch.linspace(0.0, 1.0, 32, device=device),
        torch.linspace(0.0, 1.0, 32, device=device),
        indexing="ij",
    )
    return xx.clone(), yy.clone()


def derivative_kernels(s: torch.Tensor, device=None) -> tuple[torch.Tensor, torch.Tensor]:
    xx, yy = grid32(device if device is not None else s.device)
    cx = 0.03 + 0.94 * s[:, 0]
    cy = 0.03 + 0.94 * s[:, 1]
    sigma = 0.035 + 0.30 * s[:, 2]
    theta = math.pi * s[:, 3]

    dx = xx[None] - cx[:, None, None]
    dy = yy[None] - cy[:, None, None]
    co = torch.cos(theta)[:, None, None]
    si = torch.sin(theta)[:, None, None]
    xr = co * dx + si * dy
    yr = -si * dx + co * dy
    sg = sigma[:, None, None]

    env = torch.exp(-0.5 * (xr * xr + yr * yr) / (sg * sg))
    odd = (xr / sg) * env
    even = ((xr * xr) / (sg * sg) - 1.0) * env
    odd = odd / (odd.flatten(1).norm(dim=1)[:, None, None] + 1e-8)
    even = even / (even.flatten(1).norm(dim=1)[:, None, None] + 1e-8)
    return odd, even


def derivative_features(images: torch.Tensor, s: torch.Tensor) -> torch.Tensor:
    odd, even = derivative_kernels(s, images.device)
    x = images[:, 0]
    return torch.cat(
        [
            torch.einsum("bhw,nhw->bn", x, odd),
            torch.einsum("bhw,nhw->bn", x, even),
        ],
        dim=1,
    )


class DerivativeSensors(nn.Module):
    def __init__(self, branches: int, seed: int) -> None:
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.raw = nn.Parameter(torch.randn(branches, 4, generator=g) * 0.7)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return derivative_features(images, torch.sigmoid(self.raw))


class StructuredLinear(nn.Module):
    def __init__(self, m: int, seed: int) -> None:
        super().__init__()
        assert m % 2 == 0
        self.sensors = DerivativeSensors(m // 2, seed)
        self.head = nn.Linear(m, CLASSES)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.head(self.sensors(images))


def evaluate_model(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> float:
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for start in range(0, len(x), 1000):
            xb = x[start : start + 1000]
            yb = y[start : start + 1000]
            pred = model(xb).argmax(1)
            correct += int((pred == yb).sum())
            total += len(yb)
    return correct / total


def evaluate_sensor_head(head: nn.Module, x: torch.Tensor, y: torch.Tensor, s: torch.Tensor) -> float:
    head.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        odd, even = derivative_kernels(s, x.device)
        for start in range(0, len(x), 1000):
            xb = x[start : start + 1000, 0]
            feat = torch.cat(
                [
                    torch.einsum("bhw,nhw->bn", xb, odd),
                    torch.einsum("bhw,nhw->bn", xb, even),
                ],
                dim=1,
            )
            yb = y[start : start + 1000]
            pred = head(feat).argmax(1)
            correct += int((pred == yb).sum())
            total += len(yb)
    return correct / total


def fit_structured(model: StructuredLinear, d: SplitData, seed: int) -> HeadResult:
    torch.manual_seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    best_state = None
    best_val = -1.0

    for epoch in range(EPOCHS):
        perm = torch.randperm(len(d.x), generator=torch.Generator().manual_seed(seed * 1000 + epoch))
        model.train()
        for start in range(0, len(d.x), BATCH):
            ii = perm[start : start + BATCH]
            opt.zero_grad()
            F.cross_entropy(model(d.x[ii]), d.y[ii]).backward()
            opt.step()
        if (epoch + 1) % 5 == 0:
            val = evaluate_model(model, d.xv, d.yv)
            if val > best_val:
                best_val = val
                best_state = copy.deepcopy(model.state_dict())

    assert best_state is not None
    model.load_state_dict(best_state)
    return HeadResult(model.head, evaluate_model(model, d.xv, d.yv), evaluate_model(model, d.xt, d.yt))


def fit_linear(z, y, zv, yv, zt, yt, seed: int) -> HeadResult:
    torch.manual_seed(seed)
    model = nn.Linear(z.shape[1], CLASSES)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    best_state = None
    best_val = -1.0

    for epoch in range(EPOCHS):
        perm = torch.randperm(len(z), generator=torch.Generator().manual_seed(seed * 1000 + epoch))
        model.train()
        for start in range(0, len(z), BATCH):
            ii = perm[start : start + BATCH]
            opt.zero_grad()
            F.cross_entropy(model(z[ii]), y[ii]).backward()
            opt.step()
        if (epoch + 1) % 5 == 0:
            model.eval()
            with torch.no_grad():
                val = float((model(zv).argmax(1) == yv).float().mean())
            if val > best_val:
                best_val = val
                best_state = copy.deepcopy(model.state_dict())

    assert best_state is not None
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        va = float((model(zv).argmax(1) == yv).float().mean())
        ta = float((model(zt).argmax(1) == yt).float().mean())
    return HeadResult(model, va, ta)


def dct_basis(n: int, m: int) -> np.ndarray:
    one = np.empty((n, n), dtype=np.float32)
    coords = np.arange(n, dtype=np.float32)
    for u in range(n):
        alpha = math.sqrt(1.0 / n) if u == 0 else math.sqrt(2.0 / n)
        one[u] = alpha * np.cos(math.pi * (2.0 * coords + 1.0) * u / (2.0 * n))

    order: list[tuple[int, int]] = []
    for s in range(2 * n - 1):
        diag = [(u, s - u) for u in range(n) if 0 <= s - u < n]
        if s % 2 == 0:
            diag.reverse()
        order.extend(diag)
    modes = [np.outer(one[u], one[v]).reshape(-1) for u, v in order[:m]]
    return np.stack(modes, axis=0).astype(np.float32)


def dense_features(x: torch.Tensor) -> torch.Tensor:
    return x[:, 0].flatten(1)


def head_bytes(m: int) -> int:
    return (m * CLASSES + CLASSES) * 4


def full_pixel_reference(d: SplitData, seed: int) -> HeadResult:
    return fit_linear(
        dense_features(d.x), d.y,
        dense_features(d.xv), d.yv,
        dense_features(d.xt), d.yt,
        seed,
    )


def structured_candidates(d: SplitData, m: int, seed: int) -> tuple[list[Candidate], float, float]:
    model = StructuredLinear(m, 100_000 + seed + m)
    res = fit_structured(model, d, 200_000 + seed + m)
    s = torch.sigmoid(model.sensors.raw.detach())
    out = [Candidate("structured", m, "fp32", s.numel() * 4, head_bytes(m), res.val_accuracy, res.test_accuracy)]
    for b in BITS:
        sq, payload = quantize_unit(s, b)
        out.append(
            Candidate(
                "structured", m, f"{b}b", len(payload), head_bytes(m),
                evaluate_sensor_head(model.head, d.xv, d.yv, sq),
                evaluate_sensor_head(model.head, d.xt, d.yt, sq),
            )
        )
    return out, res.val_accuracy, res.test_accuracy


def pca_candidates(d: SplitData, m: int, seed: int) -> tuple[list[Candidate], float, float]:
    x = dense_features(d.x).numpy()
    xv = dense_features(d.xv).numpy()
    xt = dense_features(d.xt).numpy()
    pca = PCA(n_components=m, svd_solver="randomized", random_state=seed)
    zp = torch.tensor(pca.fit_transform(x), dtype=torch.float32)
    zpv = torch.tensor(pca.transform(xv), dtype=torch.float32)
    centered = fit_linear(
        zp, d.y, zpv, d.yv,
        torch.tensor(pca.transform(xt), dtype=torch.float32), d.yt,
        300_000 + seed + m,
    )

    w = np.asarray(pca.components_, dtype=np.float32)
    mean = np.asarray(pca.mean_, dtype=np.float32)
    mean_proj = torch.tensor(mean @ w.T, dtype=torch.float32)
    head = nn.Linear(m, CLASSES)
    with torch.no_grad():
        head.weight.copy_(centered.head.weight)
        head.bias.copy_(centered.head.bias - centered.head.weight @ mean_proj)
    head.eval()

    def acc(a: np.ndarray, y: torch.Tensor) -> float:
        z = torch.tensor(a, dtype=torch.float32)
        with torch.no_grad():
            return float((head(z).argmax(1) == y).float().mean())

    full_val = acc(xv @ w.T, d.yv)
    full_test = acc(xt @ w.T, d.yt)
    out = [Candidate("pca", m, "fp32", w.size * 4, head_bytes(m), full_val, full_test)]
    for b in BITS:
        wq, payload = quantize_pca_rows(w, b)
        out.append(
            Candidate(
                "pca", m, f"{b}b", len(payload), head_bytes(m),
                acc(xv @ wq.T, d.yv), acc(xt @ wq.T, d.yt),
            )
        )
    return out, full_val, full_test


def dct_candidate(d: SplitData, m: int, seed: int) -> Candidate:
    b = torch.tensor(dct_basis(32, m), dtype=torch.float32)
    z = dense_features(d.x) @ b.T
    zv = dense_features(d.xv) @ b.T
    zt = dense_features(d.xt) @ b.T
    res = fit_linear(z, d.y, zv, d.yv, zt, d.yt, 400_000 + seed + m)
    return Candidate("dct", m, "algorithmic", 0, head_bytes(m), res.val_accuracy, res.test_accuracy)


def pick(candidates: list[Candidate], target: float, mode: str) -> Candidate | None:
    ok = [c for c in candidates if c.val_accuracy >= target]
    if not ok:
        return None
    if mode == "map":
        key = lambda c: (c.map_bytes, c.m, c.total_bytes, -c.val_accuracy)
    elif mode == "total":
        key = lambda c: (c.total_bytes, c.map_bytes, c.m, -c.val_accuracy)
    elif mode == "egress":
        key = lambda c: (c.m, c.total_bytes, c.map_bytes, -c.val_accuracy)
    else:
        raise ValueError(mode)
    return min(ok, key=key)


def describe(c: Candidate | None) -> str:
    if c is None:
        return "UNREACHED"
    return (
        f"M={c.m:<3} {c.bits:<11} map={c.map_bytes:>6}B "
        f"head={c.head_bytes:>5}B total={c.total_bytes:>6}B "
        f"val={c.val_accuracy:.4f} test={c.test_accuracy:.4f}"
    )


def run_seed(root: str, download: bool, seed: int) -> dict:
    d = load_data(root, download, seed)
    full = full_pixel_reference(d, 500_000 + seed)
    targets = {f: f * full.val_accuracy for f in TARGET_FRACS}

    family_candidates: dict[str, list[Candidate]] = {"structured": [], "pca": [], "dct": []}
    full_rows = []

    for m in M_VALUES:
        sc, sva, sta = structured_candidates(d, m, seed)
        family_candidates["structured"].extend(sc)
        pc, pva, pta = pca_candidates(d, m, seed)
        family_candidates["pca"].extend(pc)
        dc = dct_candidate(d, m, seed)
        family_candidates["dct"].append(dc)
        full_rows.append((m, sva, sta, pva, pta, dc.val_accuracy, dc.test_accuracy))
        print(
            f"seed {seed} M={m}: structured={sva:.4f}/{sta:.4f} "
            f"pca={pva:.4f}/{pta:.4f} dct={dc.val_accuracy:.4f}/{dc.test_accuracy:.4f}"
        )

    m16_6 = next(c for c in family_candidates["structured"] if c.m == 16 and c.bits == "6b")

    selected = {}
    for frac, target in targets.items():
        selected[frac] = {}
        for fam, cs in family_candidates.items():
            selected[frac][fam] = {mode: pick(cs, target, mode) for mode in ("map", "total", "egress")}

    return {
        "seed": seed,
        "full_val": full.val_accuracy,
        "full_test": full.test_accuracy,
        "targets": targets,
        "m16_6": m16_6,
        "selected": selected,
        "full_rows": full_rows,
    }


def report_seed(r: dict) -> None:
    print("\n" + "=" * 88)
    print(f"Gate 12 seed {r['seed']} — CIFAR-10 grayscale intrinsic-complexity attack")
    print(f"full-pixel linear: val={r['full_val']:.4f} test={r['full_test']:.4f}")
    c = r["m16_6"]
    print(f"Gate11-style structured M16/6b/24B: val={c.val_accuracy:.4f} test={c.test_accuracy:.4f}")
    for frac in TARGET_FRACS:
        target = r["targets"][frac]
        test_target = frac * r["full_test"]
        print(f"\nT{int(frac*100)} validation target={target:.4f}; analogous test threshold={test_target:.4f}")
        for fam in ("structured", "pca", "dct"):
            print(f"  {fam}")
            for mode in ("map", "total", "egress"):
                c = r["selected"][frac][fam][mode]
                suffix = ""
                if c is not None:
                    suffix = " TEST_HIT" if c.test_accuracy >= test_target else " TEST_MISS"
                print(f"    min-{mode:<6} {describe(c)}{suffix}")


def aggregate(rows: list[dict]) -> None:
    print("\n" + "#" * 88)
    print("Gate 12 aggregate — preregistered fresh CIFAR-10 seeds 9300/9301")
    print(
        f"full-pixel linear mean val={np.mean([r['full_val'] for r in rows]):.4f} "
        f"test={np.mean([r['full_test'] for r in rows]):.4f}"
    )
    print(
        "M16/6b/24B structured mean val="
        f"{np.mean([r['m16_6'].val_accuracy for r in rows]):.4f} test="
        f"{np.mean([r['m16_6'].test_accuracy for r in rows]):.4f}"
    )

    for frac in TARGET_FRACS:
        print(f"\nT{int(frac*100)} selections (per-seed validation selection; then held-out test)")
        for fam in ("structured", "pca", "dct"):
            for mode in ("map", "total", "egress"):
                cs = [r["selected"][frac][fam][mode] for r in rows]
                if any(c is None for c in cs):
                    print(f"  {fam:<10} min-{mode:<6} UNREACHED on at least one seed")
                    continue
                assert all(c is not None for c in cs)
                print(
                    f"  {fam:<10} min-{mode:<6} "
                    f"M={np.mean([c.m for c in cs]):5.1f} "
                    f"map={np.mean([c.map_bytes for c in cs]):7.1f}B "
                    f"total={np.mean([c.total_bytes for c in cs]):7.1f}B "
                    f"test={np.mean([c.test_accuracy for c in cs]):.4f}"
                )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".cifar-data")
    ap.add_argument("--download", action="store_true")
    args = ap.parse_args()

    rows = []
    for seed in SEEDS:
        r = run_seed(args.root, args.download, seed)
        rows.append(r)
        report_seed(r)
    aggregate(rows)


if __name__ == "__main__":
    main()
