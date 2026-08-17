"""Gate 10: cross-scale test on MNIST (28x28, D=784).

The hypothesis under test is no longer "learned sensing beats fixed sensing".
Gate 9 showed PCA-16 essentially closes that gap on 8x8 sklearn digits.

Gate 10 asks whether a *compactly described* 16-channel measurement map remains
competitive when input dimension grows from D=64 to D=784.

Frozen width / receiver budget:

    8 complex receivers -> 16 real values
    4 geometry scalars per receiver -> 32 map-description scalars

Strong controls:

    PCA-16 + linear head
    DCT-16 + linear head
    same random compact Gabor map + H=7 decoder
    same random compact Gabor map + H=48 decoder
    full 784 pixels + linear head (width ceiling)

The script uses deterministic stratified subsets to keep the one-shot scale
experiment cheap enough for CI. It reports accuracy and analytic deployment
resource accounting separately; trainable parameter count is not treated as
FLOPs.

Run::

    pip install -e '.[scale]'
    python experiments/gate10_mnist_scale.py --download
"""
from __future__ import annotations

import argparse
import copy
import math
import time
from dataclasses import dataclass

import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from torch import nn
from torch.nn import functional as F
from torchvision.datasets import MNIST

N_RECEIVERS = 8
M = 16
D = 28 * 28
CLASSES = 10
GEOM_PARAMS = N_RECEIVERS * 4
LINEAR_HEAD_PARAMS = M * CLASSES + CLASSES
BATCH = 256
EPOCHS = 80
LR = 0.02
TRAIN_N = 6000
VAL_N = 1000
TEST_N = 5000
SEEDS = (9100, 9101)


torch.set_num_threads(2)


class GaborSensors28(nn.Module):
    """Eight complex Gabors on normalized 28x28 coordinates -> 16 real values."""

    def __init__(self, raw: torch.Tensor, trainable: bool) -> None:
        super().__init__()
        self.raw = nn.Parameter(raw.clone(), requires_grad=trainable)
        yy, xx = torch.meshgrid(
            torch.linspace(0.0, 1.0, 28),
            torch.linspace(0.0, 1.0, 28),
            indexing="ij",
        )
        self.register_buffer("xx", xx)
        self.register_buffer("yy", yy)

    def filters(self) -> tuple[torch.Tensor, torch.Tensor]:
        s = torch.sigmoid(self.raw)
        cx = 0.05 + 0.90 * s[:, 0]
        cy = 0.05 + 0.90 * s[:, 1]
        # Same normalized frequency range and envelope scale as Gate 6.
        freq = 0.7 + 3.3 * s[:, 2]
        theta = np.pi * s[:, 3]

        dx = self.xx[None] - cx[:, None, None]
        dy = self.yy[None] - cy[:, None, None]
        c = torch.cos(theta)[:, None, None]
        st = torch.sin(theta)[:, None, None]
        xr = c * dx + st * dy
        yr = -st * dx + c * dy

        sigma = 0.22
        envelope = torch.exp(-0.5 * (xr * xr + yr * yr) / (sigma * sigma))
        phase = 2.0 * np.pi * freq[:, None, None] * xr
        real = envelope * torch.cos(phase)
        imag = envelope * torch.sin(phase)
        real = real / (real.flatten(1).norm(dim=1)[:, None, None] + 1e-8)
        imag = imag / (imag.flatten(1).norm(dim=1)[:, None, None] + 1e-8)
        return real, imag

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        real, imag = self.filters()
        x = images[:, 0]
        zr = torch.einsum("bhw,nhw->bn", x, real)
        zi = torch.einsum("bhw,nhw->bn", x, imag)
        return torch.cat([zr, zi], dim=1)

    @torch.no_grad()
    def materialized_matrix(self) -> torch.Tensor:
        real, imag = self.filters()
        return torch.cat([real.flatten(1), imag.flatten(1)], dim=0)


class LearnedGaborLinear(nn.Module):
    def __init__(self, raw: torch.Tensor) -> None:
        super().__init__()
        self.sensors = GaborSensors28(raw, trainable=True)
        self.head = nn.Linear(M, CLASSES)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.sensors(x))


@dataclass
class Split:
    x: torch.Tensor
    y: torch.Tensor
    xv: torch.Tensor
    yv: torch.Tensor
    xt: torch.Tensor
    yt: torch.Tensor


def load_mnist(root: str, download: bool, seed: int) -> Split:
    train = MNIST(root, train=True, download=download)
    test = MNIST(root, train=False, download=download)

    x_all = train.data.numpy().astype("float32") / 255.0
    y_all = train.targets.numpy().astype("int64")
    xt_all = test.data.numpy().astype("float32") / 255.0
    yt_all = test.targets.numpy().astype("int64")

    idx = np.arange(len(x_all))
    keep, _ = train_test_split(
        idx,
        train_size=TRAIN_N + VAL_N,
        random_state=seed,
        stratify=y_all,
    )
    tr, va = train_test_split(
        keep,
        train_size=TRAIN_N,
        test_size=VAL_N,
        random_state=seed + 1000,
        stratify=y_all[keep],
    )

    tidx = np.arange(len(xt_all))
    te, _ = train_test_split(
        tidx,
        train_size=TEST_N,
        random_state=seed + 2000,
        stratify=yt_all,
    )

    return Split(
        torch.tensor(x_all[tr, None]),
        torch.tensor(y_all[tr]),
        torch.tensor(x_all[va, None]),
        torch.tensor(y_all[va]),
        torch.tensor(xt_all[te, None]),
        torch.tensor(yt_all[te]),
    )


def train_model(model: nn.Module, data: Split, seed: int, epochs: int = EPOCHS) -> float:
    optimizer = torch.optim.Adam(
        [p for p in model.parameters() if p.requires_grad], lr=LR
    )
    best_state = None
    best_val = -1.0

    for epoch in range(epochs):
        model.train()
        g = torch.Generator().manual_seed(seed * 1000 + epoch)
        perm = torch.randperm(len(data.x), generator=g)
        for start in range(0, len(data.x), BATCH):
            ii = perm[start : start + BATCH]
            optimizer.zero_grad()
            F.cross_entropy(model(data.x[ii]), data.y[ii]).backward()
            optimizer.step()
        if (epoch + 1) % 5 == 0:
            model.eval()
            with torch.no_grad():
                val = float(
                    (model(data.xv).argmax(1) == data.yv).float().mean()
                )
            if val > best_val:
                best_val = val
                best_state = copy.deepcopy(model.state_dict())

    assert best_state is not None
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        return float((model(data.xt).argmax(1) == data.yt).float().mean())


def train_feature_head(
    z: torch.Tensor,
    y: torch.Tensor,
    zv: torch.Tensor,
    yv: torch.Tensor,
    zt: torch.Tensor,
    yt: torch.Tensor,
    seed: int,
    hidden: int | None = None,
) -> float:
    torch.manual_seed(seed)
    if hidden is None:
        model: nn.Module = nn.Linear(z.shape[1], CLASSES)
    else:
        model = nn.Sequential(
            nn.Linear(z.shape[1], hidden),
            nn.Tanh(),
            nn.Linear(hidden, CLASSES),
        )
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    best_state = None
    best_val = -1.0
    for epoch in range(EPOCHS):
        g = torch.Generator().manual_seed(seed * 1000 + epoch)
        perm = torch.randperm(len(z), generator=g)
        for start in range(0, len(z), BATCH):
            ii = perm[start : start + BATCH]
            optimizer.zero_grad()
            F.cross_entropy(model(z[ii]), y[ii]).backward()
            optimizer.step()
        if (epoch + 1) % 5 == 0:
            with torch.no_grad():
                val = float((model(zv).argmax(1) == yv).float().mean())
            if val > best_val:
                best_val = val
                best_state = copy.deepcopy(model.state_dict())
    assert best_state is not None
    model.load_state_dict(best_state)
    with torch.no_grad():
        return float((model(zt).argmax(1) == yt).float().mean())


def dct16_basis(n: int = 28) -> np.ndarray:
    modes: dict[tuple[int, int], np.ndarray] = {}
    grid = np.arange(n, dtype=np.float64)
    for u in range(6):
        for v in range(6):
            au = math.sqrt(1 / n) if u == 0 else math.sqrt(2 / n)
            av = math.sqrt(1 / n) if v == 0 else math.sqrt(2 / n)
            bx = au * np.cos(math.pi * (2 * grid + 1) * u / (2 * n))
            by = av * np.cos(math.pi * (2 * grid + 1) * v / (2 * n))
            modes[(u, v)] = np.outer(bx, by).astype("float32").reshape(-1)
    order: list[tuple[int, int]] = []
    for s in range(10):
        diag = [(u, s - u) for u in range(6) if 0 <= s - u < 6]
        if s % 2 == 0:
            diag.reverse()
        order.extend(diag)
        if len(order) >= M:
            break
    return np.stack([modes[p] for p in order[:M]], axis=0)


def materialized_features(matrix: torch.Tensor, data: Split):
    def f(x):
        return x[:, 0].flatten(1) @ matrix.T
    with torch.no_grad():
        return f(data.x), f(data.xv), f(data.xt)


def run_seed(root: str, seed: int, download: bool) -> dict[str, float]:
    data = load_mnist(root, download, seed)
    g = torch.Generator().manual_seed(100_000 + seed)
    raw = torch.randn(N_RECEIVERS, 4, generator=g) * 0.7

    torch.manual_seed(200_000 + seed)
    learned = LearnedGaborLinear(raw)
    t0 = time.perf_counter()
    learned_acc = train_model(learned, data, seed)
    learned_train_s = time.perf_counter() - t0

    fixed_sensor = GaborSensors28(raw, trainable=False)
    fixed_matrix = fixed_sensor.materialized_matrix()
    zg, zgv, zgt = materialized_features(fixed_matrix, data)
    fixed_h7 = train_feature_head(zg, data.y, zgv, data.yv, zgt, data.yt, seed + 7, 7)
    fixed_h48 = train_feature_head(zg, data.y, zgv, data.yv, zgt, data.yt, seed + 48, 48)

    x_np = data.x[:, 0].flatten(1).numpy()
    xv_np = data.xv[:, 0].flatten(1).numpy()
    xt_np = data.xt[:, 0].flatten(1).numpy()

    pca = PCA(n_components=M, svd_solver="randomized", random_state=seed)
    zp = torch.tensor(pca.fit_transform(x_np), dtype=torch.float32)
    zpv = torch.tensor(pca.transform(xv_np), dtype=torch.float32)
    zpt = torch.tensor(pca.transform(xt_np), dtype=torch.float32)
    pca_acc = train_feature_head(zp, data.y, zpv, data.yv, zpt, data.yt, seed + 1)

    dct = torch.tensor(dct16_basis(), dtype=torch.float32)
    zd, zdv, zdt = materialized_features(dct, data)
    dct_acc = train_feature_head(zd, data.y, zdv, data.yv, zdt, data.yt, seed + 2)

    full = train_feature_head(
        data.x[:, 0].flatten(1),
        data.y,
        data.xv[:, 0].flatten(1),
        data.yv,
        data.xt[:, 0].flatten(1),
        data.yt,
        seed + 3,
    )

    return {
        "learned_gabor": learned_acc,
        "fixed_gabor_h7": fixed_h7,
        "fixed_gabor_h48": fixed_h48,
        "pca16": pca_acc,
        "dct16": dct_acc,
        "full_linear": full,
        "learned_train_s": learned_train_s,
    }


def print_resources() -> None:
    dense_coeffs = M * D
    pca_explicit = dense_coeffs + D
    dense_over_geom = dense_coeffs / GEOM_PARAMS
    learned_state = GEOM_PARAMS + LINEAR_HEAD_PARAMS
    pca_state = pca_explicit + LINEAR_HEAD_PARAMS
    projection_macs = M * D
    learned_macs = projection_macs + M * CLASSES
    h48_macs = projection_macs + M * 48 + 48 * CLASSES

    print("\nGate 10 analytic resource accounting (FP32)")
    print(f"input D={D}, transmitted M={M}, egress={M*4} bytes/sample")
    print(f"dense projection coefficients = {dense_coeffs}")
    print(f"compact Gabor description = {GEOM_PARAMS} scalars")
    print(f"dense/Gabor description ratio = {dense_over_geom:.1f}x")
    print(f"Gabor geometry + linear state = {learned_state*4} bytes")
    print(f"PCA matrix + mean + linear state = {pca_state*4} bytes")
    print(f"materialized projection = {projection_macs} MACs/sample")
    print(f"Gabor + linear total ~= {learned_macs} MACs/sample")
    print(f"fixed Gabor + H48 total ~= {h48_macs} MACs/sample")
    print(f"digital MAC ratio H48/linear ~= {h48_macs/learned_macs:.3f}x")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".mnist-data")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--one-seed", action="store_true")
    args = parser.parse_args()

    seeds = SEEDS[:1] if args.one_seed else SEEDS
    rows = []
    for seed in seeds:
        row = run_seed(args.root, seed, args.download)
        rows.append(row)
        print(
            f"seed {seed}: "
            f"learned={row['learned_gabor']:.4f} "
            f"PCA={row['pca16']:.4f} DCT={row['dct16']:.4f} "
            f"fixedH7={row['fixed_gabor_h7']:.4f} "
            f"fixedH48={row['fixed_gabor_h48']:.4f} "
            f"full={row['full_linear']:.4f} "
            f"learned_train_s={row['learned_train_s']:.1f}"
        )

    print("\nGate 10 — MNIST scale means")
    for key in (
        "learned_gabor",
        "pca16",
        "dct16",
        "fixed_gabor_h7",
        "fixed_gabor_h48",
        "full_linear",
    ):
        print(f"{key:<20} {np.mean([r[key] for r in rows]):.4f}")
    print_resources()


if __name__ == "__main__":
    main()
