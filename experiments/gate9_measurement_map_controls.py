"""Gate 9: fixed-basis attackers and measurement-map resource accounting.

Gate 6 compared a learned low-parameter receiver family against the *same*
receiver geometry frozen at random initialization.  That is not enough: a
well-chosen fixed basis can be much stronger than a random frozen one.

This gate adds two boring controls on sklearn digits:

* PCA-16: unsupervised, fitted on the training images only.
* DCT-16: label-free and data-free; the first 16 2-D DCT modes in zig-zag order.

All arms transmit exactly 16 real values and use the same 16 -> 10 linear head
(170 trainable parameters).  The script also prints inference/resource
accounting for a generic digital realization of the measurement map.

Requires::

    pip install -e '.[gate6]'

The important distinction is between:

* *materialized measurement coefficients* (e.g. a dense PCA matrix), and
* *description parameters* (e.g. 8 Gabor receivers x 4 geometry scalars).

A structured map can have a short description even when a digital
implementation ultimately materializes dense filters and therefore pays the
same O(MD) projection MACs.
"""
from __future__ import annotations

import argparse
import math

import numpy as np
import torch
from sklearn.decomposition import PCA
from torch import nn
from torch.nn import functional as F

from gate6_receiver_frontier import BATCH, LR, load_split

M = 16
N_COMPLEX = 8
GEOM_PER_RECEIVER = 4
CLASSES = 10
HEAD_PARAMS = M * CLASSES + CLASSES


def dct16_basis(n: int = 8) -> np.ndarray:
    """Return 16 orthonormal 2-D DCT-II basis vectors in zig-zag order."""
    modes: dict[tuple[int, int], np.ndarray] = {}
    for u in range(n):
        for v in range(n):
            au = math.sqrt(1.0 / n) if u == 0 else math.sqrt(2.0 / n)
            av = math.sqrt(1.0 / n) if v == 0 else math.sqrt(2.0 / n)
            b = np.empty((n, n), dtype=np.float32)
            for x in range(n):
                for y in range(n):
                    b[x, y] = (
                        au
                        * av
                        * math.cos(math.pi * (2 * x + 1) * u / (2 * n))
                        * math.cos(math.pi * (2 * y + 1) * v / (2 * n))
                    )
            modes[(u, v)] = b.reshape(-1)

    order: list[tuple[int, int]] = []
    for s in range(2 * n - 1):
        diagonal = [(u, s - u) for u in range(n) if 0 <= s - u < n]
        if s % 2 == 0:
            diagonal.reverse()
        order.extend(diagonal)
    return np.stack([modes[p] for p in order[:M]], axis=0)


def train_linear(z, y, zv, yv, zt, yt, seed: int, epochs: int = 180) -> float:
    z = torch.as_tensor(z, dtype=torch.float32)
    y = torch.as_tensor(y, dtype=torch.long)
    zv = torch.as_tensor(zv, dtype=torch.float32)
    yv = torch.as_tensor(yv, dtype=torch.long)
    zt = torch.as_tensor(zt, dtype=torch.float32)
    yt = torch.as_tensor(yt, dtype=torch.long)

    torch.manual_seed(seed)
    model = nn.Linear(M, CLASSES)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    best_state = None
    best_val = -1.0

    for epoch in range(epochs):
        generator = torch.Generator().manual_seed(seed * 1000 + epoch)
        perm = torch.randperm(len(z), generator=generator)
        for start in range(0, len(z), BATCH):
            idx = perm[start : start + BATCH]
            optimizer.zero_grad()
            F.cross_entropy(model(z[idx]), y[idx]).backward()
            optimizer.step()

        if (epoch + 1) % 5 == 0:
            with torch.no_grad():
                val = float((model(zv).argmax(1) == yv).float().mean())
            if val > best_val:
                best_val = val
                best_state = {
                    k: v.detach().clone() for k, v in model.state_dict().items()
                }

    assert best_state is not None
    model.load_state_dict(best_state)
    with torch.no_grad():
        return float((model(zt).argmax(1) == yt).float().mean())


def resource_row(d: int, dtype_bytes: int = 4) -> dict[str, float]:
    dense_coeffs = M * d
    pca_explicit = dense_coeffs + d  # projection plus centering mean
    gabor_desc = N_COMPLEX * GEOM_PER_RECEIVER
    projection_macs = M * d
    linear_head_macs = M * CLASSES
    return {
        "D": d,
        "dense_projection_coeffs": dense_coeffs,
        "pca_explicit_scalars": pca_explicit,
        "gabor_geometry_scalars": gabor_desc,
        "dense_over_gabor_description": dense_coeffs / gabor_desc,
        "egress_bytes_fp32": M * dtype_bytes,
        "projection_macs_if_materialized": projection_macs,
        "linear_head_macs": linear_head_macs,
        "gabor_plus_head_state_bytes": (gabor_desc + HEAD_PARAMS) * dtype_bytes,
        "pca_plus_head_state_bytes": (pca_explicit + HEAD_PARAMS) * dtype_bytes,
    }


def run(splits) -> None:
    basis = dct16_basis(8)
    pca_scores: list[float] = []
    dct_scores: list[float] = []

    for split in splits:
        x, y, xv, yv, xt, yt = load_split(split)
        x_np = x[:, 0].numpy().reshape(len(x), -1)
        xv_np = xv[:, 0].numpy().reshape(len(xv), -1)
        xt_np = xt[:, 0].numpy().reshape(len(xt), -1)

        pca = PCA(n_components=M, svd_solver="full")
        zp = pca.fit_transform(x_np)
        zpv = pca.transform(xv_np)
        zpt = pca.transform(xt_np)
        pca_acc = train_linear(zp, y, zpv, yv, zpt, yt, split + 1)
        pca_scores.append(pca_acc)

        zd = x_np @ basis.T
        zdv = xv_np @ basis.T
        zdt = xt_np @ basis.T
        dct_acc = train_linear(zd, y, zdv, yv, zdt, yt, split + 2)
        dct_scores.append(dct_acc)

        print(f"split {split}: PCA16={pca_acc:.4f} DCT16={dct_acc:.4f}")

    print("\nGate 9 — fixed measurement-map controls")
    print(f"PCA-16 + linear mean = {np.mean(pca_scores):.4f}")
    print(f"DCT-16 + linear mean = {np.mean(dct_scores):.4f}")
    print("All arms transmit 16 real values; linear head has 170 trainable params.")

    print("\nResource accounting (FP32; generic materialized digital projection)")
    for d in (64, 784):
        r = resource_row(d)
        print(
            f"D={d:<3} dense-map={int(r['dense_projection_coeffs']):<5} coeffs  "
            f"Gabor-desc={int(r['gabor_geometry_scalars']):<2} scalars  "
            f"ratio={r['dense_over_gabor_description']:.1f}x  "
            f"egress={int(r['egress_bytes_fp32'])} B  "
            f"projection={int(r['projection_macs_if_materialized'])} MACs"
        )
    r64 = resource_row(64)
    print(
        "\nDigits deployment-state examples (explicit PCA mean included):\n"
        f"  Gabor geometry + linear head: {int(r64['gabor_plus_head_state_bytes'])} B\n"
        f"  PCA matrix + mean + linear head: {int(r64['pca_plus_head_state_bytes'])} B\n"
        "  DCT basis can be algorithmic rather than stored densely; its accuracy is the\n"
        "  important zero/low-description-cost control."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="use splits 6000..6007")
    args = parser.parse_args()
    run(range(6000, 6008 if args.full else 6004))
