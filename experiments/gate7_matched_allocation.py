"""Gate 7: ~200-parameter receiver-vs-decoder allocation.

Requires ``pip install -e '.[gate6]'``.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import nn

from gate6_receiver_frontier import GaborSensors, load_split, train_model


class PartialGabor(GaborSensors):
    """First m of eight receiver geometries learn; the rest stay fixed."""

    def __init__(self, raw: torch.Tensor, m: int) -> None:
        nn.Module.__init__(self)
        self.m = int(m)
        if self.m:
            self.learned_raw = nn.Parameter(raw[: self.m].clone())
        else:
            self.learned_raw = None
        self.register_buffer("fixed_raw", raw[self.m :].clone())
        yy, xx = torch.meshgrid(
            torch.linspace(0.0, 1.0, 8),
            torch.linspace(0.0, 1.0, 8),
            indexing="ij",
        )
        self.register_buffer("xx", xx.clone())
        self.register_buffer("yy", yy.clone())

    @property
    def raw(self):
        if self.learned_raw is None:
            return self.fixed_raw
        if len(self.fixed_raw) == 0:
            return self.learned_raw
        return torch.cat([self.learned_raw, self.fixed_raw], dim=0)


class AllocationModel(nn.Module):
    def __init__(self, sensors: nn.Module, hidden: int | None) -> None:
        super().__init__()
        self.sensors = sensors
        if hidden is None:
            self.head = nn.Linear(16, 10)
        else:
            self.head = nn.Sequential(
                nn.Linear(16, hidden), nn.Tanh(), nn.Linear(hidden, 10)
            )

    def forward(self, x):
        return self.head(self.sensors(x))


def logical_params(m: int, hidden: int | None) -> int:
    decoder = 170 if hidden is None else 27 * hidden + 10
    return 4 * m + decoder


def main():
    configs = (
        ("fixed_H7", 0, 7),
        ("interior_m7_H6", 7, 6),
        ("learned_linear", 8, None),
    )
    scores = {name: [] for name, _, _ in configs}

    for split in range(7000, 7004):
        data = load_split(split)
        generator = torch.Generator().manual_seed(500_000 + split)
        raw = torch.randn(8, 4, generator=generator) * 0.7
        for i, (name, m, hidden) in enumerate(configs):
            torch.manual_seed(600_000 + split * 100 + i)
            model = AllocationModel(PartialGabor(raw, m), hidden)
            scores[name].append(train_model(model, data, split * 100 + i))

    print("Gate 7 — matched ~200 parameter allocation")
    for name, m, hidden in configs:
        print(
            f"{name:<18} params={logical_params(m, hidden):<4} "
            f"mean={np.mean(scores[name]):.4f} values={scores[name]}"
        )
    print("INTERIOR_Y_BLOCK_EARNS_KEEP =", False)


if __name__ == "__main__":
    main()
