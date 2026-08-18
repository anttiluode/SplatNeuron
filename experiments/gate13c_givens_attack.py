"""Gate 13c — generic compact learned Givens-circuit attacker.

Scientific design frozen first in:
    docs/GATE13C_PREREG_GIVENS_ATTACK.md

Primary only: K=8, local, T95, 3 D values x 3 world seeds.
The incumbent Gate-13 geometry is not retrained here.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

import gate13_dks_preflight as g
import gate13b_index_only_attackers as b

POOL = 48
M_VALUES = (24, 32)
ROUND_COUNTS = (1, 2, 4, 8, 16)
BITS = (4, 6, 8, 12, 16)
RESTARTS = 3
STEPS = 220
BATCH = 1024
LR = 0.03
K = 8
STRUCTURE = "local"
WORLD_SEEDS = (13100, 13101, 13102)


def round_robin_pairs(p: int):
    """Deterministic all-pairs tournament schedule for even p."""
    if p % 2:
        raise ValueError("p must be even")
    a = list(range(p))
    rounds = []
    for _ in range(p - 1):
        pairs = [(a[i], a[p - 1 - i]) for i in range(p // 2)]
        rounds.append(pairs)
        # Circle method: keep a[0] fixed, rotate the remainder right by one.
        a = [a[0], a[-1], *a[1:-1]]
    return rounds


PAIR_ROUNDS = round_robin_pairs(POOL)


def apply_circuit(x: torch.Tensor, angles: torch.Tensor, rounds: int) -> torch.Tensor:
    """Apply `rounds` disjoint-pair Givens stages to B x POOL features."""
    for r in range(rounds):
        pairs = PAIR_ROUNDS[r]
        ii = torch.tensor([q[0] for q in pairs], dtype=torch.long, device=x.device)
        jj = torch.tensor([q[1] for q in pairs], dtype=torch.long, device=x.device)
        ang = angles[r]
        c, s = torch.cos(ang)[None, :], torch.sin(ang)[None, :]
        xi, xj = x[:, ii], x[:, jj]
        yi = c * xi - s * xj
        yj = s * xi + c * xj
        vals = torch.stack((yi, yj), dim=2).reshape(x.shape[0], POOL)
        flat_idx = torch.stack((ii, jj), dim=1).reshape(-1)
        inv = torch.argsort(flat_idx)
        x = vals[:, inv]
    return x


def angle_from_raw(raw: torch.Tensor) -> torch.Tensor:
    return math.pi * torch.tanh(raw)


def quant_angle(a: torch.Tensor, bits: int) -> torch.Tensor:
    levels = (1 << bits) - 1
    u = torch.clamp((a + math.pi) / (2.0 * math.pi), 0.0, 1.0)
    uq = torch.round(u * levels) / levels
    return -math.pi + (2.0 * math.pi) * uq


def task_stats(z: torch.Tensor, y: torch.Tensor, h: torch.Tensor):
    x = torch.cat([z, torch.ones((len(z), 1))], dim=1)
    per = (((x @ h) >= 0.0) == (y >= 0.0)).float().mean(dim=0).numpy()
    return float(per.mean()), float(per.std()), float(np.quantile(per, 0.10))


def transformed(base: torch.Tensor, angles: torch.Tensor, rounds: int, m: int):
    return apply_circuit(base, angles, rounds)[:, :m]


def fit_one(pool_rows: torch.Tensor, data, m: int, rounds: int, seed: int):
    (z, y), (zv, yv), (zt, yt) = data
    tr = z @ pool_rows.T
    va = zv @ pool_rows.T
    te = zt @ pool_rows.T

    trials = []
    for restart in range(RESTARTS):
        rs = seed * 100_000 + m * 1_000 + rounds * 10 + restart
        torch.manual_seed(rs)
        raw = nn.Parameter(torch.randn((rounds, POOL // 2)) * 0.03)
        head = nn.Linear(m, g.TASKS)
        opt = torch.optim.Adam([raw, *head.parameters()], lr=LR)
        gen = torch.Generator().manual_seed(rs + 77)
        for _ in range(STEPS):
            idx = torch.randint(0, len(tr), (BATCH,), generator=gen)
            a = angle_from_raw(raw)
            zz = transformed(tr[idx], a, rounds, m)
            logits = head(zz)
            loss = F.binary_cross_entropy_with_logits(logits, (y[idx] + 1.0) * 0.5)
            opt.zero_grad()
            loss.backward()
            opt.step()

        a = angle_from_raw(raw.detach())
        ztr = transformed(tr, a, rounds, m)
        h = g.ridge_head(ztr, y)
        val = g.accuracy(transformed(va, a, rounds, m), yv, h)
        trials.append((val, restart, a, h))

    vals = [float(q[0]) for q in trials]
    chosen = max(trials, key=lambda q: q[0])
    return vals, chosen, tr, va, te


def evaluate_candidate(base_va, base_te, yv, yt, angles, rounds, m, h):
    zv = transformed(base_va, angles, rounds, m)
    zt = transformed(base_te, angles, rounds, m)
    val = g.accuracy(zv, yv, h)
    test, sd, p10 = task_stats(zt, yt, h)
    return val, test, sd, p10


def run(seed: int):
    data = g.data(K, seed)
    (z, y), (zv, yv), (zt, yt) = data
    href = g.ridge_head(z[:, :K], y)
    ref_val = g.accuracy(zv[:, :K], yv, href)
    ref_test = g.accuracy(zt[:, :K], yt, href)
    target = 0.5 + 0.95 * (ref_val - 0.5)
    out = {
        "world_seed": seed,
        "k": K,
        "structure": STRUCTURE,
        "reference": {"val": ref_val, "test": ref_test, "t95": target},
        "results": [],
    }
    print(f"REFERENCE seed={seed} K=8 val={ref_val:.4f} test={ref_test:.4f} T95={target:.4f}")

    for n in g.D_SIDES:
        d = n * n
        a = g.build_world(n, K, STRUCTURE, seed)
        all_rows = b.dct_latent_rows(a, n, None)
        pool_idx = b.choose_rows(all_rows, z, y, POOL)
        pool_rows = torch.tensor(all_rows[pool_idx], dtype=torch.float32)
        pool_bits = b.subset_code_bits(d, POOL)
        print(f"CELL seed={seed} D={d} pool={POOL} pool_bits={pool_bits}")

        for m in M_VALUES:
            for rounds in ROUND_COUNTS:
                vals, chosen, tr, va, te = fit_one(pool_rows, data, m, rounds, seed + d)
                full_val, selected_restart, angles, h = chosen
                angle_count = rounds * (POOL // 2)
                print(
                    f"  GIVENS M={m:2d} rounds={rounds:2d} R={angle_count:3d} "
                    f"restart_vals={[round(v,4) for v in vals]}"
                )

                # Full precision candidate, mainly for expressivity/discovery diagnostics.
                val, test, sd, p10 = evaluate_candidate(va, te, yv, yt, angles, rounds, m, h)
                out["results"].append({
                    "d": d, "m": m, "rounds": rounds, "angle_count": angle_count,
                    "bits": "fp32", "map_bits": pool_bits + 32 * angle_count,
                    "map_bytes": (pool_bits + 32 * angle_count + 7) // 8,
                    "val_accuracy": val, "test_accuracy": test,
                    "test_task_std": sd, "test_task_p10": p10,
                    "reaches": bool(val >= target),
                    "restart_vals": vals, "selected_restart": int(selected_restart),
                    "restarts": RESTARTS, "optimizer_steps": RESTARTS * STEPS,
                    "pool_index_bits": pool_bits,
                    "pool_indices": pool_idx.tolist(),
                })

                for bits in BITS:
                    aq = quant_angle(angles, bits)
                    val, test, sd, p10 = evaluate_candidate(va, te, yv, yt, aq, rounds, m, h)
                    map_bits = pool_bits + bits * angle_count
                    out["results"].append({
                        "d": d, "m": m, "rounds": rounds, "angle_count": angle_count,
                        "bits": f"{bits}b", "map_bits": map_bits,
                        "map_bytes": (map_bits + 7) // 8,
                        "val_accuracy": val, "test_accuracy": test,
                        "test_task_std": sd, "test_task_p10": p10,
                        "reaches": bool(val >= target),
                        "restart_vals": vals, "selected_restart": int(selected_restart),
                        "restarts": RESTARTS, "optimizer_steps": RESTARTS * STEPS,
                        "pool_index_bits": pool_bits,
                        "pool_indices": pool_idx.tolist(),
                    })
                    print(
                        f"    {bits:2d}b map={(map_bits+7)//8:4d}B "
                        f"val={val:.4f} test={test:.4f} reach={val >= target}"
                    )

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world-seed", type=int, required=True, choices=WORLD_SEEDS)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    torch.set_num_threads(2)
    result = run(args.world_seed)
    Path(args.output).write_text(json.dumps(result, indent=2))
    print("WROTE", args.output)


if __name__ == "__main__":
    main()
