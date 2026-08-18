"""Gate 6: learned receiver geometry versus downstream decoder capacity.

This experiment is intentionally separate from the online ROUTE gates. It asks
whether training the observation map can simplify the downstream classifier at
fixed transmitted width.

Requires the optional ``gate6`` dependencies::

    pip install -e '.[gate6]'

Default mode runs four deterministic stratified splits. ``--full`` runs the
eight-split frontier reported in docs/GATE6_RECEIVER_DECODER_FRONTIER.md.
"""
from __future__ import annotations

import argparse

import numpy as np
import torch
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from torch import nn
from torch.nn import functional as F

N_RECEIVERS = 8
EPOCHS = 160
BATCH = 128
LR = 0.02
FRONTIER_H = (7, 24, 32, 40, 48)


torch.set_num_threads(2)


class GaborSensors(nn.Module):
    """Eight learned/fixed complex Gabor receivers -> sixteen real channels."""

    def __init__(self, raw: torch.Tensor, trainable: bool) -> None:
        super().__init__()
        self.raw = nn.Parameter(raw.clone(), requires_grad=trainable)
        yy, xx = torch.meshgrid(
            torch.linspace(0.0, 1.0, 8),
            torch.linspace(0.0, 1.0, 8),
            indexing="ij",
        )
        self.register_buffer("xx", xx.clone())
        self.register_buffer("yy", yy.clone())

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        s = torch.sigmoid(self.raw)
        cx = 0.05 + 0.90 * s[:, 0]
        cy = 0.05 + 0.90 * s[:, 1]
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

        x = images[:, 0]
        zr = torch.einsum("bhw,nhw->bn", x, real)
        zi = torch.einsum("bhw,nhw->bn", x, imag)
        return torch.cat([zr, zi], dim=1)


class LearnedReceiverLinear(nn.Module):
    def __init__(self, raw: torch.Tensor) -> None:
        super().__init__()
        self.sensors = GaborSensors(raw, trainable=True)
        self.head = nn.Linear(16, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.sensors(x))


def load_split(split_seed: int):
    digits = load_digits()
    x = (digits.images.astype("float32") / 16.0)[:, None]
    y = digits.target.astype("int64")
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.20,
        random_state=split_seed,
        stratify=y,
    )
    x_train, x_val, y_train, y_val = train_test_split(
        x_train,
        y_train,
        test_size=0.20,
        random_state=split_seed + 1000,
        stratify=y_train,
    )
    return tuple(
        torch.tensor(v)
        for v in (x_train, y_train, x_val, y_val, x_test, y_test)
    )


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def train_model(model: nn.Module, data, seed: int) -> float:
    x, y, xv, yv, xt, yt = data
    optimizer = torch.optim.Adam(
        [p for p in model.parameters() if p.requires_grad], lr=LR
    )
    best_state = None
    best_val = -1.0

    for epoch in range(EPOCHS):
        model.train()
        generator = torch.Generator().manual_seed(seed * 10_000 + epoch)
        perm = torch.randperm(len(x), generator=generator)
        for start in range(0, len(x), BATCH):
            idx = perm[start : start + BATCH]
            optimizer.zero_grad()
            F.cross_entropy(model(x[idx]), y[idx]).backward()
            optimizer.step()

        if (epoch + 1) % 5 == 0:
            model.eval()
            with torch.no_grad():
                val = float((model(xv).argmax(1) == yv).float().mean())
            if val > best_val:
                best_val = val
                best_state = {
                    k: v.detach().clone() for k, v in model.state_dict().items()
                }

    assert best_state is not None
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        return float((model(xt).argmax(1) == yt).float().mean())


def train_fixed_head(
    z,
    y,
    zv,
    yv,
    zt,
    yt,
    hidden: int,
    seed: int,
) -> float:
    torch.manual_seed(seed)
    model = nn.Sequential(
        nn.Linear(16, hidden),
        nn.Tanh(),
        nn.Linear(hidden, 10),
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    best_state = None
    best_val = -1.0

    for epoch in range(180):
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


def bootstrap_ci(values, draws: int = 50_000):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(20260817)
    boot = np.asarray(
        [rng.choice(values, len(values), replace=True).mean() for _ in range(draws)]
    )
    return float(values.mean()), tuple(
        float(x) for x in np.quantile(boot, [0.025, 0.975])
    )


def run(splits):
    learned_scores = []
    fixed_scores = {h: [] for h in FRONTIER_H}

    for split in splits:
        data = load_split(split)
        x, y, xv, yv, xt, yt = data
        generator = torch.Generator().manual_seed(100_000 + split)
        raw = torch.randn(N_RECEIVERS, 4, generator=generator) * 0.7

        torch.manual_seed(200_000 + split * 100)
        learned = LearnedReceiverLinear(raw)
        learned_acc = train_model(learned, data, split * 100)
        learned_scores.append(learned_acc)

        fixed = GaborSensors(raw, trainable=False)
        fixed.eval()
        with torch.no_grad():
            z = fixed(x)
            zv = fixed(xv)
            zt = fixed(xt)

        for hidden in FRONTIER_H:
            acc = train_fixed_head(
                z,
                y,
                zv,
                yv,
                zt,
                yt,
                hidden,
                split * 100 + hidden,
            )
            fixed_scores[hidden].append(acc)

        print(
            f"split {split}: learned202={learned_acc:.4f} "
            + " ".join(
                f"H{h}={fixed_scores[h][-1]:.4f}" for h in FRONTIER_H
            )
        )

    learned_scores = np.asarray(learned_scores)
    print("\nGate 6 — receiver / decoder frontier")
    print(
        f"learned receiver + linear: params=202 "
        f"mean={learned_scores.mean():.4f}"
    )
    for hidden in FRONTIER_H:
        scores = np.asarray(fixed_scores[hidden])
        delta, (lo, hi) = bootstrap_ci(learned_scores - scores)
        params = 27 * hidden + 10
        print(
            f"fixed receiver H={hidden:<2} params={params:<4} "
            f"mean={scores.mean():.4f} "
            f"learned-fixed={delta:+.4f} CI[{lo:+.4f},{hi:+.4f}]"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="run all eight reported splits instead of the four-split quick replication",
    )
    args = parser.parse_args()
    splits = range(6000, 6008 if args.full else 6004)
    run(splits)
