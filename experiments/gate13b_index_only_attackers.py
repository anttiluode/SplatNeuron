"""Gate 13b — task-adapted index-only dictionary attackers.

Scientific design frozen first in:
    docs/GATE13B_PREREG_INDEX_ONLY_ATTACKERS.md

This runner does NOT retrain Gate-13 geometry.  It evaluates two new attackers
on the identical synthetic world/task instrument and emits JSON for later
comparison to the frozen Gate-13 artifacts:

    selected_dct
    selected_signed_dct

Only row-subset indices are task-specific payload.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch

import gate13_dks_preflight as g

M_VALUES = (8, 16, 24, 32, 48, 64)
WORLD_SEEDS = (13100, 13101, 13102)


def dct1(n: int) -> np.ndarray:
    x = np.arange(n, dtype=np.float64)
    out = np.empty((n, n), dtype=np.float64)
    for u in range(n):
        alpha = math.sqrt(1.0 / n) if u == 0 else math.sqrt(2.0 / n)
        out[u] = alpha * np.cos(math.pi * (2.0 * x + 1.0) * u / (2.0 * n))
    return out.astype(np.float32)


def dct_latent_rows(a: np.ndarray, n: int, sign: np.ndarray | None = None) -> np.ndarray:
    """Return all D 2-D-DCT dictionary rows restricted to latent world A."""
    c = dct1(n)
    imgs = a.reshape(n, n, a.shape[1]).astype(np.float32)
    if sign is not None:
        imgs = imgs * sign.reshape(n, n, 1)
    tmp = np.einsum("ui,ijn->ujn", c, imgs, optimize=True)
    coef = np.einsum("ujn,vj->uvn", tmp, c, optimize=True)
    return coef.reshape(n * n, a.shape[1]).astype(np.float32)


def shared_sign_mask(n: int) -> np.ndarray:
    """One universal Rademacher mask per sampled side; no task-specific seed."""
    rng = np.random.default_rng(913_000 + n)
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=n * n)


def subset_code_bits(d: int, m: int) -> int:
    # Exact ceil(log2(C(d,m))) without floating-point overflow.
    choices = math.comb(d, m)
    return int((choices - 1).bit_length()) if choices > 1 else 0


def choose_rows(b_all: np.ndarray, z: torch.Tensor, y: torch.Tensor, m: int) -> np.ndarray:
    """Deterministic supervised diverse-correlation selection from training only.

    Each candidate row is represented by its normalized covariance vector with
    the 32 tasks.  Gram-Schmidt selection favors candidates adding a new task-
    covariance direction; any remaining slots are filled by original score.
    """
    zn = z.numpy().astype(np.float64, copy=False)
    yn = y.numpy().astype(np.float64, copy=False)
    latent_task_cov = (zn.T @ yn) / float(len(zn))
    task_cov = b_all.astype(np.float64) @ latent_task_cov
    var = np.sum(b_all.astype(np.float64) ** 2, axis=1)
    norm_cov = task_cov / np.sqrt(np.maximum(var, 1e-12))[:, None]
    original_score = np.sum(norm_cov * norm_cov, axis=1)
    original_score[var < 1e-10] = -np.inf

    residual = norm_cov.copy()
    chosen: list[int] = []
    used = np.zeros(len(b_all), dtype=bool)

    for _ in range(min(m, g.TASKS)):
        score = np.sum(residual * residual, axis=1)
        score[used] = -np.inf
        j = int(np.argmax(score))
        if not np.isfinite(score[j]) or score[j] < 1e-14:
            break
        chosen.append(j)
        used[j] = True
        v = residual[j]
        nv = float(np.linalg.norm(v))
        if nv > 1e-12:
            v = v / nv
            residual -= (residual @ v)[:, None] * v[None, :]
        residual[j] = 0.0

    if len(chosen) < m:
        order = np.argsort(original_score)[::-1]
        for jj in order:
            j = int(jj)
            if not used[j] and np.isfinite(original_score[j]):
                chosen.append(j)
                used[j] = True
                if len(chosen) == m:
                    break

    if len(chosen) != m:
        raise RuntimeError(f"could only select {len(chosen)} of requested {m} rows")
    return np.array(sorted(chosen), dtype=np.int64)


def task_stats(z: torch.Tensor, y: torch.Tensor, h: torch.Tensor):
    x = torch.cat([z, torch.ones((len(z), 1))], dim=1)
    per = (((x @ h) >= 0.0) == (y >= 0.0)).float().mean(dim=0).numpy()
    return float(per.mean()), float(per.std()), float(np.quantile(per, 0.10))


def fit_one(family: str, d: int, k: int, structure: str, m: int,
            b_all: np.ndarray, data, target: float):
    (z, y), (zv, yv), (zt, yt) = data
    idx = choose_rows(b_all, z, y, m)
    b = torch.tensor(b_all[idx], dtype=torch.float32)
    h = g.ridge_head(z @ b.T, y)
    va = g.accuracy(zv @ b.T, yv, h)
    te, sd, p10 = task_stats(zt @ b.T, yt, h)
    bits = subset_code_bits(d, m)
    return {
        "family": family,
        "d": d,
        "k": k,
        "structure": structure,
        "m": m,
        "index_bits": bits,
        "map_bytes": (bits + 7) // 8,
        "val_accuracy": va,
        "test_accuracy": te,
        "test_task_std": sd,
        "test_task_p10": p10,
        "target": target,
        "reaches": bool(va >= target),
        "dictionary_rows_scored": d,
        "gradient_steps": 0,
        "restarts": 0,
        "selected_indices": idx.tolist(),
    }


def run(seed: int):
    out = {"world_seed": seed, "results": [], "references": []}
    for k in g.K_VALUES:
        data = g.data(k, seed)
        (z, y), (zv, yv), (zt, yt) = data
        href = g.ridge_head(z[:, :k], y)
        ref_val = g.accuracy(zv[:, :k], yv, href)
        ref_test = g.accuracy(zt[:, :k], yt, href)
        target = 0.5 + 0.95 * (ref_val - 0.5)
        out["references"].append({"k": k, "val": ref_val, "test": ref_test, "t95": target})
        print(f"REFERENCE seed={seed} K={k} val={ref_val:.4f} test={ref_test:.4f} T95={target:.4f}")

        for n in g.D_SIDES:
            d = n * n
            sign = shared_sign_mask(n)
            for structure in g.STRUCTURES:
                a = g.build_world(n, k, structure, seed)
                dictionaries = {
                    "selected_dct": dct_latent_rows(a, n, None),
                    "selected_signed_dct": dct_latent_rows(a, n, sign),
                }
                print(f"CELL seed={seed} D={d} K={k} S={structure}")
                for family, b_all in dictionaries.items():
                    for m in M_VALUES:
                        r = fit_one(family, d, k, structure, m, b_all, data, target)
                        out["results"].append(r)
                        print(
                            f"  {family:19s} M={m:2d} map={r['map_bytes']:3d}B "
                            f"val={r['val_accuracy']:.4f} test={r['test_accuracy']:.4f} "
                            f"reach={r['reaches']}"
                        )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world-seed", type=int, required=True, choices=WORLD_SEEDS)
    ap.add_argument("--output", type=str, required=True)
    args = ap.parse_args()
    torch.set_num_threads(2)
    result = run(args.world_seed)
    Path(args.output).write_text(json.dumps(result, indent=2))
    print("WROTE", args.output)


if __name__ == "__main__":
    main()
