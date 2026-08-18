"""Gate 8: private receiver branches before a fixed 16-wide carrier.

Requires ``pip install -e '.[gate6]'``.

Default runs the three development splits. ``--confirm`` runs the frozen fresh
confirmation splits reported in docs/GATE8_PRECOLLAPSE_FRONTIER.md.
"""
from __future__ import annotations

import argparse

import numpy as np
import torch
from torch import nn

from gate6_receiver_frontier import GaborSensors, load_split, train_model


class BranchModel(nn.Module):
    def __init__(
        self,
        raw: torch.Tensor,
        branches: int,
        hidden: int | None,
        use_reducer: bool,
    ) -> None:
        super().__init__()
        self.sensors = GaborSensors(raw[:branches], trainable=True)
        self.reducer = (
            nn.Linear(2 * branches, 16) if use_reducer else nn.Identity()
        )
        if hidden is None:
            self.head = nn.Linear(16, 10)
        else:
            self.head = nn.Sequential(
                nn.Linear(16, hidden),
                nn.Tanh(),
                nn.Linear(hidden, 10),
            )

    def forward(self, x):
        return self.head(self.reducer(self.sensors(x)))


def count_params(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def run(splits):
    configs = (
        ("B8_identity_H27", 8, 27, False),
        ("B10_reduce_H14", 10, 14, True),
        ("B12_reduce_H11", 12, 11, True),
        ("B14_reduce_H8", 14, 8, True),
        ("B16_reduce_linear", 16, None, True),
    )
    scores = {name: [] for name, *_ in configs}
    params = {}

    for split in splits:
        data = load_split(split)
        generator = torch.Generator().manual_seed(900_000 + split)
        raw = torch.randn(16, 4, generator=generator) * 0.7
        for i, (name, branches, hidden, reducer) in enumerate(configs):
            torch.manual_seed(910_000 + split * 100 + i)
            model = BranchModel(raw, branches, hidden, reducer)
            params[name] = count_params(model)
            scores[name].append(train_model(model, data, split * 100 + i))

    print("Gate 8 — pre-collapse receiver frontier")
    print("carrier width = 16 real channels")
    for name, *_ in configs:
        print(
            f"{name:<20} params={params[name]:<4} "
            f"mean={np.mean(scores[name]):.4f} values={scores[name]}"
        )
    print("INTERIOR_Y_BLOCK_EARNS_KEEP =", False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    run(range(9000, 9003) if args.confirm else range(8000, 8003))
