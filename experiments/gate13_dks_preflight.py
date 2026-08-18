"""Gate 13 preflight — validate the synthetic D x K x structure instrument.

The scientific design was frozen first in:
    docs/GATE13_PREREG_DKS_EXCHANGE_SURFACE.md

This preflight does NOT test whether learned geometry wins.  It tests that the
world generator has the intended orthonormality/locality structure, that every
task bank spans K, and that a task-blind Gaussian random projection is roughly
invariant to the structure/sampling axes.
"""
from __future__ import annotations

import math
import numpy as np
import torch

D_SIDES = (32, 48, 64)
K_VALUES = (2, 4, 8, 16)
STRUCTURES = ("local", "mixed", "dense")
TASKS = 32
NUISANCE = 32
K_MAX = 16
TRAIN_N = 8_000
VAL_N = 2_000
TEST_N = 5_000
FLIP_P = 0.10
RIDGE = 1e-2
WORLD_SEED = 13100
RANDOM_SEED_BASE = 73_000


def grid(n: int):
    yy, xx = np.meshgrid(
        np.linspace(0.0, 1.0, n, dtype=np.float64),
        np.linspace(0.0, 1.0, n, dtype=np.float64),
        indexing="ij",
    )
    return xx, yy


def qr_columns(a: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(a, mode="reduced")
    return q.astype(np.float32)


def local_signal_bank(n: int, seed: int) -> np.ndarray:
    """Compact smooth random patches; intentionally not Gabor/derivative atoms."""
    xx, yy = grid(n)
    centers = [((ix + 0.5) / 4.0, (iy + 0.5) / 4.0) for iy in range(4) for ix in range(4)]
    rng = np.random.default_rng(seed)
    cols = []
    for cx, cy in centers[:K_MAX]:
        sx = 0.075 + 0.01 * rng.random()
        sy = 0.075 + 0.01 * rng.random()
        dx, dy = xx - cx, yy - cy
        env = np.exp(-0.5 * ((dx / sx) ** 2 + (dy / sy) ** 2))
        theta = rng.uniform(0.0, math.pi)
        u = np.cos(theta) * dx + np.sin(theta) * dy
        v = -np.sin(theta) * dx + np.cos(theta) * dy
        f1, f2 = rng.uniform(4.0, 8.0), rng.uniform(2.0, 5.0)
        p1, p2 = rng.uniform(0.0, 2.0 * math.pi), rng.uniform(0.0, 2.0 * math.pi)
        patch = env * (
            0.65 * np.cos(2.0 * math.pi * f1 * u + p1)
            + 0.35 * np.sin(2.0 * math.pi * f2 * v + p2)
        )
        patch -= patch.mean()
        vec = patch.reshape(-1)
        vec /= np.linalg.norm(vec) + 1e-12
        cols.append(vec)
    return np.stack(cols, axis=1).astype(np.float32)


def dense_bank(n: int, count: int, seed: int) -> np.ndarray:
    xx, yy = grid(n)
    rng = np.random.default_rng(seed)
    cols = []
    for _ in range(count):
        field = np.zeros((n, n), dtype=np.float64)
        for _term in range(16):
            fx, fy = int(rng.integers(1, 13)), int(rng.integers(1, 13))
            phase, amp = rng.uniform(0.0, 2.0 * math.pi), rng.normal()
            field += amp * np.cos(2.0 * math.pi * (fx * xx + fy * yy) + phase)
        field -= field.mean()
        vec = field.reshape(-1)
        vec /= np.linalg.norm(vec) + 1e-12
        cols.append(vec)
    return np.stack(cols, axis=1).astype(np.float32)


def build_world(n: int, k: int, structure: str, seed: int) -> np.ndarray:
    signal = local_signal_bank(n, seed + 1)[:, :k]
    nuisance = dense_bank(n, NUISANCE, seed + 2)
    local = qr_columns(np.concatenate([signal, nuisance], axis=1))
    dense = qr_columns(dense_bank(n, k + NUISANCE, seed + 3))
    alpha = {"local": 0.0, "mixed": 0.5, "dense": 1.0}[structure]
    return qr_columns((1.0 - alpha) * local + alpha * dense)


def support_fraction(cols: np.ndarray) -> float:
    d = cols.shape[0]
    return float(np.mean(1.0 / (d * np.sum(cols.astype(np.float64) ** 4, axis=0))))


def task_weights(k: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed + 101)
    w = rng.normal(size=(TASKS, K_MAX)).astype(np.float32)[:, :k]
    w /= np.linalg.norm(w, axis=1, keepdims=True) + 1e-12
    return w


def split(k: int, count: int, seed: int, offset: int):
    w = task_weights(k, seed)
    rng = np.random.default_rng(seed + offset)
    zs = rng.normal(size=(count, k)).astype(np.float32)
    zn = rng.normal(size=(count, NUISANCE)).astype(np.float32)
    clean = zs @ w.T >= 0.0
    flips = rng.random(size=clean.shape) < FLIP_P
    y = np.logical_xor(clean, flips).astype(np.float32) * 2.0 - 1.0
    z = np.concatenate([zs, zn], axis=1)
    return torch.tensor(z), torch.tensor(y)


def data(k: int, seed: int):
    return split(k, TRAIN_N, seed, 1001), split(k, VAL_N, seed, 2001), split(k, TEST_N, seed, 3001)


def ridge_head(z: torch.Tensor, y: torch.Tensor):
    x = torch.cat([z, torch.ones((len(z), 1))], dim=1)
    eye = torch.eye(x.shape[1])
    eye[-1, -1] = 0.0
    return torch.linalg.solve(x.T @ x + RIDGE * eye, x.T @ y)


def accuracy(z: torch.Tensor, y: torch.Tensor, h: torch.Tensor) -> float:
    x = torch.cat([z, torch.ones((len(z), 1))], dim=1)
    return float((((x @ h) >= 0.0) == (y >= 0.0)).float().mean())


def random_b(a: np.ndarray, m: int, seed: int) -> torch.Tensor:
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0, 1.0 / math.sqrt(m), size=(m, a.shape[0])).astype(np.float32)
    return torch.tensor(r @ a)


def main() -> None:
    torch.set_num_threads(2)
    seed = WORLD_SEED
    print("Gate 13 preflight — D x K x structure")

    for n in D_SIDES:
        supports = []
        for structure in STRUCTURES:
            a = build_world(n, 8, structure, seed)
            orth = float(np.max(np.abs(a.T @ a - np.eye(a.shape[1], dtype=np.float32))))
            sig = support_fraction(a[:, :8])
            nui = support_fraction(a[:, 8:])
            supports.append(sig)
            print(
                f"D={n*n:4d} S={structure:5s} orth={orth:.3e} "
                f"signal_support={sig:.4f} nuisance_support={nui:.4f}"
            )
            assert orth < 2e-5
        assert supports[0] < supports[1] < supports[2]

    for k in K_VALUES:
        rank = int(np.linalg.matrix_rank(task_weights(k, seed)))
        print(f"TASK_BANK K={k:2d} rank={rank}")
        assert rank == k

    k, m = 8, 32
    (z, y), (zv, yv), (zt, yt) = data(k, seed)
    href = ridge_head(z[:, :k], y)
    ref_val = accuracy(zv[:, :k], yv, href)
    ref_test = accuracy(zt[:, :k], yt, href)
    t95 = 0.5 + 0.95 * (ref_val - 0.5)
    print(f"REFERENCE K=8 val={ref_val:.4f} test={ref_test:.4f} T95={t95:.4f}")

    means = []
    for n in D_SIDES:
        for structure in STRUCTURES:
            a = build_world(n, k, structure, seed)
            vals = []
            for j in range(3):
                rs = RANDOM_SEED_BASE + 9_000_000 + j * 100_003
                b = random_b(a, m, rs)
                h = ridge_head(z @ b.T, y)
                vals.append(accuracy(zv @ b.T, yv, h))
            mean = float(np.mean(vals))
            means.append(mean)
            print(
                f"RANDOM_SANITY D={n*n:4d} S={structure:5s} "
                f"vals={[round(v,4) for v in vals]} mean={mean:.4f}"
            )

    span = max(means) - min(means)
    print(f"RANDOM_SANITY mean_span={span:.4f} (warning threshold 0.05)")
    if span > 0.05:
        print("PRECHECK_WARNING = random-arm span exceeds 0.05")
    print("GATE13_PREFLIGHT_PASS = True")


if __name__ == "__main__":
    main()
