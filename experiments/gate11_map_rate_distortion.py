"""Gate 11 — fixed-rate compression of the observation map.

Preregistered in docs/GATE11_PREREG_RATE_DISTORTION.md before results.

Fresh sklearn-digits splits 7200..7207.  All arms emit 16 real values and use
a full-FP32 16->10 linear head (170 params / 680 bytes).  Only the observation
map is compressed after training/fitting; heads are frozen and never retrained
per bit rate.

Families:
  * learned compact Gabor geometry: 32 normalized scalars
  * learned compact steerable Gaussian-derivative geometry: 32 scalars
  * PCA-16 dense map: 1024 coefficients, per-row symmetric quantization
  * DCT-16 algorithmic map: zero payload under the shared protocol

Bit depths: 2,3,4,6,8,12,16 bits/value.
"""
from __future__ import annotations

import argparse
import copy
import math
from dataclasses import dataclass

import numpy as np
import torch
from sklearn.decomposition import PCA
from torch import nn
from torch.nn import functional as F

from gate6_receiver_frontier import (
    BATCH,
    EPOCHS,
    LR,
    LearnedReceiverLinear,
    load_split,
    train_model,
)
from gate9_measurement_map_controls import dct16_basis

BITS = (2, 3, 4, 6, 8, 12, 16)
SPLITS = tuple(range(7200, 7208))
M = 16
CLASSES = 10
HEAD_BYTES = (M * CLASSES + CLASSES) * 4  # FP32, frozen/common


torch.set_num_threads(2)


class GaussianDerivativeSensors8(nn.Module):
    """8 nonoscillatory steerable derivative branches -> 16 real channels."""

    def __init__(self, raw: torch.Tensor) -> None:
        super().__init__()
        self.raw = nn.Parameter(raw.clone())
        yy, xx = torch.meshgrid(
            torch.linspace(0.0, 1.0, 8),
            torch.linspace(0.0, 1.0, 8),
            indexing="ij",
        )
        self.register_buffer("xx", xx.clone())
        self.register_buffer("yy", yy.clone())

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return gaussian_derivative_features(images, torch.sigmoid(self.raw), self.xx, self.yy)


class LearnedDerivativeLinear(nn.Module):
    def __init__(self, raw: torch.Tensor) -> None:
        super().__init__()
        self.sensors = GaussianDerivativeSensors8(raw)
        self.head = nn.Linear(M, CLASSES)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.head(self.sensors(images))


def grid8(device=None):
    yy, xx = torch.meshgrid(
        torch.linspace(0.0, 1.0, 8, device=device),
        torch.linspace(0.0, 1.0, 8, device=device),
        indexing="ij",
    )
    return xx.clone(), yy.clone()


def gabor_features(images: torch.Tensor, s: torch.Tensor) -> torch.Tensor:
    """Gate-6 Gabor features from normalized geometry s in [0,1]^(8x4)."""
    xx, yy = grid8(images.device)
    cx = 0.05 + 0.90 * s[:, 0]
    cy = 0.05 + 0.90 * s[:, 1]
    freq = 0.7 + 3.3 * s[:, 2]
    theta = np.pi * s[:, 3]

    dx = xx[None] - cx[:, None, None]
    dy = yy[None] - cy[:, None, None]
    c = torch.cos(theta)[:, None, None]
    st = torch.sin(theta)[:, None, None]
    xr = c * dx + st * dy
    yr = -st * dx + c * dy

    sigma = 0.22
    env = torch.exp(-0.5 * (xr * xr + yr * yr) / (sigma * sigma))
    phase = 2.0 * np.pi * freq[:, None, None] * xr
    real = env * torch.cos(phase)
    imag = env * torch.sin(phase)
    real = real / (real.flatten(1).norm(dim=1)[:, None, None] + 1e-8)
    imag = imag / (imag.flatten(1).norm(dim=1)[:, None, None] + 1e-8)

    x = images[:, 0]
    return torch.cat(
        [
            torch.einsum("bhw,nhw->bn", x, real),
            torch.einsum("bhw,nhw->bn", x, imag),
        ],
        dim=1,
    )


def gaussian_derivative_features(
    images: torch.Tensor,
    s: torch.Tensor,
    xx: torch.Tensor | None = None,
    yy: torch.Tensor | None = None,
) -> torch.Tensor:
    """First+second directional Gaussian derivatives from normalized geometry."""
    if xx is None or yy is None:
        xx, yy = grid8(images.device)
    cx = 0.05 + 0.90 * s[:, 0]
    cy = 0.05 + 0.90 * s[:, 1]
    sigma = 0.05 + 0.25 * s[:, 2]
    theta = np.pi * s[:, 3]

    dx = xx[None] - cx[:, None, None]
    dy = yy[None] - cy[:, None, None]
    c = torch.cos(theta)[:, None, None]
    st = torch.sin(theta)[:, None, None]
    xr = c * dx + st * dy
    yr = -st * dx + c * dy
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


def train_linear_return(
    z: torch.Tensor,
    y: torch.Tensor,
    zv: torch.Tensor,
    yv: torch.Tensor,
    seed: int,
) -> nn.Linear:
    torch.manual_seed(seed)
    model = nn.Linear(M, CLASSES)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    best_state = None
    best_val = -1.0

    for epoch in range(EPOCHS):
        generator = torch.Generator().manual_seed(seed * 1000 + epoch)
        perm = torch.randperm(len(z), generator=generator)
        model.train()
        for start in range(0, len(z), BATCH):
            idx = perm[start : start + BATCH]
            optimizer.zero_grad()
            F.cross_entropy(model(z[idx]), y[idx]).backward()
            optimizer.step()
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
    return model


def accuracy_from_features(head: nn.Module, features: torch.Tensor, labels: torch.Tensor) -> float:
    with torch.no_grad():
        return float((head(features).argmax(1) == labels).float().mean())


def pack_codes(codes: np.ndarray, bits: int) -> bytes:
    """Literal fixed-width bit packing, MSB first, padded only to final byte."""
    flat = np.asarray(codes, dtype=np.uint64).reshape(-1)
    shifts = np.arange(bits - 1, -1, -1, dtype=np.uint64)
    bit_array = ((flat[:, None] >> shifts[None, :]) & 1).astype(np.uint8).reshape(-1)
    return np.packbits(bit_array).tobytes()


def quantize_unit(values: torch.Tensor, bits: int):
    levels = (1 << bits) - 1
    q = torch.round(values.clamp(0, 1) * levels).to(torch.int64)
    payload = pack_codes(q.detach().cpu().numpy(), bits)
    deq = q.to(torch.float32) / float(levels)
    return deq, payload


def quantize_pca_rows(matrix: np.ndarray, bits: int):
    """Per-row symmetric fixed-rate codec; one FP32 maxabs scale per row."""
    w = np.asarray(matrix, dtype=np.float32)
    scales = np.maximum(np.max(np.abs(w), axis=1), np.float32(1e-12)).astype(np.float32)
    levels = (1 << bits) - 1
    unit = (w / scales[:, None] + 1.0) * 0.5
    q = np.rint(np.clip(unit, 0.0, 1.0) * levels).astype(np.uint64)
    deq = ((q.astype(np.float32) / levels) * 2.0 - 1.0) * scales[:, None]
    payload = scales.astype("<f4").tobytes() + pack_codes(q, bits)
    return deq.astype(np.float32), payload


@dataclass
class FamilyResult:
    full_accuracy: float
    full_map_bytes: int
    rate_accuracy: dict[int, float]
    rate_map_bytes: dict[int, int]


def run_split(split: int) -> dict[str, FamilyResult]:
    data = load_split(split)
    x, y, xv, yv, xt, yt = data
    raw_generator = torch.Generator().manual_seed(100_000 + split)
    raw = torch.randn(8, 4, generator=raw_generator) * 0.7

    # Compact Gabor: exact Gate-6 training protocol.
    torch.manual_seed(200_000 + split * 100)
    gabor = LearnedReceiverLinear(raw)
    _ = train_model(gabor, data, split * 100)
    gabor_s = torch.sigmoid(gabor.sensors.raw.detach())
    with torch.no_grad():
        gabor_full = accuracy_from_features(gabor.head, gabor_features(xt, gabor_s), yt)
    gabor_rate_acc = {}
    gabor_rate_bytes = {}
    for b in BITS:
        sq, payload = quantize_unit(gabor_s, b)
        gabor_rate_acc[b] = accuracy_from_features(gabor.head, gabor_features(xt, sq), yt)
        gabor_rate_bytes[b] = len(payload)

    # Compact nonoscillatory steerable derivative family.
    torch.manual_seed(300_000 + split * 100)
    deriv = LearnedDerivativeLinear(raw)
    _ = train_model(deriv, data, split * 100 + 17)
    deriv_s = torch.sigmoid(deriv.sensors.raw.detach())
    with torch.no_grad():
        deriv_full = accuracy_from_features(
            deriv.head, gaussian_derivative_features(xt, deriv_s), yt
        )
    deriv_rate_acc = {}
    deriv_rate_bytes = {}
    for b in BITS:
        sq, payload = quantize_unit(deriv_s, b)
        deriv_rate_acc[b] = accuracy_from_features(
            deriv.head, gaussian_derivative_features(xt, sq), yt
        )
        deriv_rate_bytes[b] = len(payload)

    # PCA: train linear head on centered PCA coordinates, then absorb mean into
    # the head bias so deployment/quantization needs only the projection matrix.
    x_np = x[:, 0].flatten(1).numpy()
    xv_np = xv[:, 0].flatten(1).numpy()
    xt_np = xt[:, 0].flatten(1).numpy()
    pca = PCA(n_components=M, svd_solver="full")
    zp = torch.tensor(pca.fit_transform(x_np), dtype=torch.float32)
    zpv = torch.tensor(pca.transform(xv_np), dtype=torch.float32)
    pca_head_centered = train_linear_return(zp, y, zpv, yv, 400_000 + split)

    w = np.asarray(pca.components_, dtype=np.float32)
    mean = np.asarray(pca.mean_, dtype=np.float32)
    mean_proj = torch.tensor(mean @ w.T, dtype=torch.float32)
    pca_head = nn.Linear(M, CLASSES)
    with torch.no_grad():
        pca_head.weight.copy_(pca_head_centered.weight)
        pca_head.bias.copy_(
            pca_head_centered.bias - pca_head_centered.weight @ mean_proj
        )
    pca_full_features = torch.tensor(xt_np @ w.T, dtype=torch.float32)
    pca_full = accuracy_from_features(pca_head, pca_full_features, yt)
    pca_rate_acc = {}
    pca_rate_bytes = {}
    for b in BITS:
        wq, payload = quantize_pca_rows(w, b)
        zq = torch.tensor(xt_np @ wq.T, dtype=torch.float32)
        pca_rate_acc[b] = accuracy_from_features(pca_head, zq, yt)
        pca_rate_bytes[b] = len(payload)

    # DCT: algorithmic zero-map-payload anchor.
    dct = torch.tensor(dct16_basis(8), dtype=torch.float32)
    zd = x[:, 0].flatten(1) @ dct.T
    zdv = xv[:, 0].flatten(1) @ dct.T
    zdt = xt[:, 0].flatten(1) @ dct.T
    dct_head = train_linear_return(zd, y, zdv, yv, 500_000 + split)
    dct_acc = accuracy_from_features(dct_head, zdt, yt)

    return {
        "gabor": FamilyResult(
            gabor_full, 32 * 4, gabor_rate_acc, gabor_rate_bytes
        ),
        "derivative": FamilyResult(
            deriv_full, 32 * 4, deriv_rate_acc, deriv_rate_bytes
        ),
        "pca": FamilyResult(
            pca_full, 16 * 64 * 4, pca_rate_acc, pca_rate_bytes
        ),
        "dct": FamilyResult(dct_acc, 0, {}, {}),
    }


def aggregate(runs: list[dict[str, FamilyResult]]):
    families = ("gabor", "derivative", "pca", "dct")
    out = {}
    for family in families:
        full = np.array([r[family].full_accuracy for r in runs], dtype=float)
        item = {
            "full_accuracy": float(full.mean()),
            "full_map_bytes": runs[0][family].full_map_bytes,
            "rates": {},
        }
        if family != "dct":
            for b in BITS:
                vals = np.array([r[family].rate_accuracy[b] for r in runs], dtype=float)
                item["rates"][b] = {
                    "accuracy": float(vals.mean()),
                    "map_bytes": runs[0][family].rate_map_bytes[b],
                }
        out[family] = item
    return out


def smallest_payload_for_floor(item, floor: float):
    candidates = []
    if item["full_accuracy"] >= floor:
        candidates.append((item["full_map_bytes"], "fp32", item["full_accuracy"]))
    for b, r in item["rates"].items():
        if r["accuracy"] >= floor:
            candidates.append((r["map_bytes"], f"{b}b", r["accuracy"]))
    if not candidates:
        return None
    return min(candidates, key=lambda x: (x[0], -x[2]))


def print_report(out, split_count: int):
    print(f"Gate 11 — map rate/distortion, {split_count} fresh splits")
    print(f"common FP32 head bytes = {HEAD_BYTES}; logical egress = 16 real values")
    print()

    for family in ("gabor", "derivative", "pca", "dct"):
        item = out[family]
        print(
            f"{family:<11} full_acc={item['full_accuracy']:.4f} "
            f"full_map={item['full_map_bytes']}B total={item['full_map_bytes']+HEAD_BYTES}B"
        )
        for b in BITS:
            if b in item["rates"]:
                r = item["rates"][b]
                drop = item["full_accuracy"] - r["accuracy"]
                print(
                    f"  {b:>2}b/value map={r['map_bytes']:>4}B "
                    f"total={r['map_bytes']+HEAD_BYTES:>4}B "
                    f"acc={r['accuracy']:.4f} drop={drop:+.4f}"
                )
        print()

    print("Smallest map payload reaching absolute mean-accuracy floors")
    for floor in (0.90, 0.92, 0.94):
        print(f"  floor {floor:.2f}")
        for family in ("gabor", "derivative", "pca", "dct"):
            item = out[family]
            if family == "dct":
                ans = (0, "algorithmic", item["full_accuracy"]) if item["full_accuracy"] >= floor else None
            else:
                ans = smallest_payload_for_floor(item, floor)
            if ans is None:
                print(f"    {family:<11} unreached")
            else:
                print(f"    {family:<11} {ans[0]:>4}B  {ans[1]:>11}  acc={ans[2]:.4f}")

    print("\nSmallest map payload within 1 percentage point of own full precision")
    for family in ("gabor", "derivative", "pca", "dct"):
        item = out[family]
        target = item["full_accuracy"] - 0.01
        if family == "dct":
            ans = (0, "algorithmic", item["full_accuracy"])
        else:
            ans = smallest_payload_for_floor(item, target)
        print(
            f"  {family:<11} target={target:.4f} -> "
            f"{ans[0]}B ({ans[1]}) acc={ans[2]:.4f}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="run all eight preregistered splits")
    args = parser.parse_args()
    splits = SPLITS if args.full else SPLITS[:4]
    runs = []
    for split in splits:
        r = run_split(split)
        runs.append(r)
        print(
            f"split {split}: "
            f"gabor={r['gabor'].full_accuracy:.4f} "
            f"deriv={r['derivative'].full_accuracy:.4f} "
            f"pca={r['pca'].full_accuracy:.4f} "
            f"dct={r['dct'].full_accuracy:.4f}"
        )
    out = aggregate(runs)
    print()
    print_report(out, len(splits))


if __name__ == "__main__":
    main()
