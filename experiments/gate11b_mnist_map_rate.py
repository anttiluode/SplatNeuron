"""Gate 11b — fixed-rate observation-map compression on 28x28 MNIST.

Preregistered in docs/GATE11B_PREREG_MNIST_RATE.md before results.
Fresh seeds 9200/9201; same 6000/1000/5000 protocol as Gate 10.
No per-rate retraining.  Heads stay FP32 and frozen.
"""
from __future__ import annotations

import argparse
import copy

import numpy as np
import torch
from sklearn.decomposition import PCA
from torch import nn
from torch.nn import functional as F

from gate10_mnist_scale_v2 import (
    BATCH,
    C,
    D,
    EPOCHS,
    LR,
    M,
    Gabor28,
    Learned,
    data,
    dct16,
    fit,
)
from gate10c_gaussian_derivative import Model as DerivativeModel
from gate11_map_rate_distortion import (
    BITS,
    accuracy_from_features,
    quantize_pca_rows,
    quantize_unit,
)

SEEDS = (9200, 9201)
HEAD_BYTES = (M * C + C) * 4

torch.set_num_threads(2)


def grid28(device=None):
    yy, xx = torch.meshgrid(
        torch.linspace(0.0, 1.0, 28, device=device),
        torch.linspace(0.0, 1.0, 28, device=device),
        indexing="ij",
    )
    return xx.clone(), yy.clone()


def gabor_features(images: torch.Tensor, s: torch.Tensor) -> torch.Tensor:
    xx, yy = grid28(images.device)
    cx = 0.05 + 0.90 * s[:, 0]
    cy = 0.05 + 0.90 * s[:, 1]
    freq = 0.7 + 3.3 * s[:, 2]
    theta = np.pi * s[:, 3]
    dx = xx[None] - cx[:, None, None]
    dy = yy[None] - cy[:, None, None]
    co = torch.cos(theta)[:, None, None]
    si = torch.sin(theta)[:, None, None]
    xr = co * dx + si * dy
    yr = -si * dx + co * dy
    sigma = 0.22
    env = torch.exp(-0.5 * (xr * xr + yr * yr) / (sigma * sigma))
    phase = 2.0 * np.pi * freq[:, None, None] * xr
    re = env * torch.cos(phase)
    im = env * torch.sin(phase)
    re = re / (re.flatten(1).norm(dim=1)[:, None, None] + 1e-8)
    im = im / (im.flatten(1).norm(dim=1)[:, None, None] + 1e-8)
    x = images[:, 0]
    return torch.cat(
        [
            torch.einsum("bhw,nhw->bn", x, re),
            torch.einsum("bhw,nhw->bn", x, im),
        ],
        dim=1,
    )


def derivative_features(images: torch.Tensor, s: torch.Tensor) -> torch.Tensor:
    xx, yy = grid28(images.device)
    cx = 0.05 + 0.90 * s[:, 0]
    cy = 0.05 + 0.90 * s[:, 1]
    sigma = 0.05 + 0.25 * s[:, 2]
    theta = np.pi * s[:, 3]
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
    x = images[:, 0]
    return torch.cat(
        [
            torch.einsum("bhw,nhw->bn", x, odd),
            torch.einsum("bhw,nhw->bn", x, even),
        ],
        dim=1,
    )


def train_linear_return(z, y, zv, yv, seed):
    torch.manual_seed(seed)
    model = nn.Linear(M, C)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    best = None
    best_val = -1.0
    for epoch in range(EPOCHS):
        perm = torch.randperm(
            len(z), generator=torch.Generator().manual_seed(seed * 1000 + epoch)
        )
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
                best = copy.deepcopy(model.state_dict())
    assert best is not None
    model.load_state_dict(best)
    model.eval()
    return model


def family(full_acc, full_map_bytes, rates):
    return {"full": full_acc, "full_map": full_map_bytes, "rates": rates}


def run_seed(root: str, seed: int, download: bool):
    d = data(root, download, seed)
    raw = torch.randn(
        8, 4, generator=torch.Generator().manual_seed(100_000 + seed)
    ) * 0.7

    # Compact Gabor.
    torch.manual_seed(200_000 + seed)
    gm = Learned(raw)
    gfull = fit(gm, d.x, d.y, d.xv, d.yv, d.xt, d.yt, seed)
    gs = torch.sigmoid(gm.sensor.raw.detach())
    grates = {}
    for b in BITS:
        sq, payload = quantize_unit(gs, b)
        grates[b] = (
            accuracy_from_features(gm.head, gabor_features(d.xt, sq), d.yt),
            len(payload),
        )

    # Matched nonoscillatory steerable derivative family.
    torch.manual_seed(600_000 + seed)
    dm = DerivativeModel(raw)
    dfull = fit(dm, d.x, d.y, d.xv, d.yv, d.xt, d.yt, seed + 300)
    ds = torch.sigmoid(dm.s.raw.detach())
    drates = {}
    for b in BITS:
        sq, payload = quantize_unit(ds, b)
        drates[b] = (
            accuracy_from_features(dm.h, derivative_features(d.xt, sq), d.yt),
            len(payload),
        )

    # PCA-16; absorb centering into decoder bias before compression.
    x = d.x[:, 0].flatten(1).numpy()
    xv = d.xv[:, 0].flatten(1).numpy()
    xt = d.xt[:, 0].flatten(1).numpy()
    pca = PCA(n_components=M, svd_solver="randomized", random_state=seed)
    zp = torch.tensor(pca.fit_transform(x), dtype=torch.float32)
    zpv = torch.tensor(pca.transform(xv), dtype=torch.float32)
    ph_center = train_linear_return(zp, d.y, zpv, d.yv, 700_000 + seed)
    w = np.asarray(pca.components_, dtype=np.float32)
    mean = np.asarray(pca.mean_, dtype=np.float32)
    mean_proj = torch.tensor(mean @ w.T, dtype=torch.float32)
    ph = nn.Linear(M, C)
    with torch.no_grad():
        ph.weight.copy_(ph_center.weight)
        ph.bias.copy_(ph_center.bias - ph_center.weight @ mean_proj)
    pfull = accuracy_from_features(
        ph, torch.tensor(xt @ w.T, dtype=torch.float32), d.yt
    )
    prates = {}
    for b in BITS:
        wq, payload = quantize_pca_rows(w, b)
        prates[b] = (
            accuracy_from_features(
                ph, torch.tensor(xt @ wq.T, dtype=torch.float32), d.yt
            ),
            len(payload),
        )

    # DCT algorithmic anchor.
    db = torch.tensor(dct16(), dtype=torch.float32)
    zd = d.x[:, 0].flatten(1) @ db.T
    zdv = d.xv[:, 0].flatten(1) @ db.T
    zdt = d.xt[:, 0].flatten(1) @ db.T
    dh = train_linear_return(zd, d.y, zdv, d.yv, 800_000 + seed)
    dacc = accuracy_from_features(dh, zdt, d.yt)

    return {
        "gabor": family(gfull, 32 * 4, grates),
        "derivative": family(dfull, 32 * 4, drates),
        "pca": family(pfull, M * D * 4, prates),
        "dct": family(dacc, 0, {}),
    }


def aggregate(rows):
    out = {}
    for fam in ("gabor", "derivative", "pca", "dct"):
        item = {
            "full": float(np.mean([r[fam]["full"] for r in rows])),
            "full_map": rows[0][fam]["full_map"],
            "rates": {},
        }
        if fam != "dct":
            for b in BITS:
                item["rates"][b] = {
                    "acc": float(np.mean([r[fam]["rates"][b][0] for r in rows])),
                    "map": rows[0][fam]["rates"][b][1],
                }
        out[fam] = item
    return out


def smallest(item, floor):
    candidates = []
    if item["full"] >= floor:
        candidates.append((item["full_map"], "fp32", item["full"]))
    for b, r in item["rates"].items():
        if r["acc"] >= floor:
            candidates.append((r["map"], f"{b}b", r["acc"]))
    return min(candidates, key=lambda q: (q[0], -q[2])) if candidates else None


def report(out):
    print("Gate 11b — MNIST map rate scaling; fresh seeds 9200/9201")
    print(f"common head={HEAD_BYTES}B; D={D}; M={M}")
    for fam in ("gabor", "derivative", "pca", "dct"):
        q = out[fam]
        print(
            f"\n{fam:<11} full_acc={q['full']:.4f} "
            f"full_map={q['full_map']}B total={q['full_map']+HEAD_BYTES}B"
        )
        for b in BITS:
            if b in q["rates"]:
                r = q["rates"][b]
                print(
                    f"  {b:>2}b/value map={r['map']:>5}B total={r['map']+HEAD_BYTES:>5}B "
                    f"acc={r['acc']:.4f} drop={q['full']-r['acc']:+.4f}"
                )

    print("\nSmallest map payload reaching absolute mean-accuracy floors")
    for floor in (0.80, 0.85, 0.88):
        print(f"  floor {floor:.2f}")
        for fam in ("gabor", "derivative", "pca", "dct"):
            q = out[fam]
            ans = (
                (0, "algorithmic", q["full"])
                if fam == "dct" and q["full"] >= floor
                else (None if fam == "dct" else smallest(q, floor))
            )
            if ans is None:
                print(f"    {fam:<11} unreached")
            else:
                print(f"    {fam:<11} {ans[0]:>5}B {ans[1]:>11} acc={ans[2]:.4f}")

    print("\nSmallest map payload within 1 percentage point of own full precision")
    for fam in ("gabor", "derivative", "pca", "dct"):
        q = out[fam]
        target = q["full"] - 0.01
        ans = (0, "algorithmic", q["full"]) if fam == "dct" else smallest(q, target)
        print(
            f"  {fam:<11} target={target:.4f} -> {ans[0]}B ({ans[1]}) acc={ans[2]:.4f}"
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".mnist-data")
    ap.add_argument("--download", action="store_true")
    args = ap.parse_args()
    rows = []
    for seed in SEEDS:
        r = run_seed(args.root, seed, args.download)
        rows.append(r)
        print(
            f"seed {seed}: gabor={r['gabor']['full']:.4f} "
            f"deriv={r['derivative']['full']:.4f} pca={r['pca']['full']:.4f} "
            f"dct={r['dct']['full']:.4f}"
        )
    print()
    report(aggregate(rows))


if __name__ == "__main__":
    main()
