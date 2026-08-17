"""Boundary 1: when does paying to ROUTE beat keeping fixed receiver addresses?"""
from __future__ import annotations

import numpy as np

from splatneuron.continuous import ContinuousDomain, ContinuousFieldEpisode, FixedCapacityTracker

BUDGET = 8
N = 180
LATE = 80
INITIAL_A = np.array([0.28, 0.30, 0.28, 0.12], dtype=float)
INITIAL_B = np.array([0.70, 0.68, 0.73, 0.61], dtype=float)
BASE_DRIFT = np.array([0.014, 0.014, 0.014, 0.012], dtype=float)
SCALES = (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0)
SEEDS = tuple(range(4000, 4012))


def make_schedule(seed: int, scale: float):
    rng = np.random.default_rng(seed)
    domain = ContinuousDomain()
    states = [INITIAL_A.copy(), INITIAL_B.copy()]
    out = []
    for t in range(N):
        source = 0 if t < 40 else 1 if t < 80 else int(rng.integers(0, 2))
        states[source] = domain.clip(states[source] + rng.normal(0.0, BASE_DRIFT * scale))
        out.append((states[source].copy(), int(rng.choice([-1, 1]))))
    return out


def run_seed(seed: int, scale: float):
    initial = [INITIAL_A.copy(), INITIAL_B.copy()]
    cache = FixedCapacityTracker(initial)
    route = FixedCapacityTracker(initial)
    record = {name: {"overlap": [], "routed": []} for name in ("cache", "route")}

    for t, (target, label) in enumerate(make_schedule(seed, scale)):
        for pi, name in enumerate(("cache", "route")):
            erng = np.random.default_rng(seed * 1_000_003 + t * 101 + pi * 10_007)
            ep = ContinuousFieldEpisode(target, label, erng)
            if name == "cache":
                res = cache.observe(ep, budget=BUDGET, mode="cache", plastic=False)
            else:
                res = route.observe(ep, budget=BUDGET, mode="hybrid", plastic=True)
            record[name]["overlap"].append(ep.true_overlap(res.coordinate))
            record[name]["routed"].append(res.action == "ROUTE")
    return record


def paired_ci(values: np.ndarray, draws: int = 10_000):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(20260817)
    boot = np.empty(draws, dtype=float)
    for i in range(draws):
        boot[i] = rng.choice(values, len(values), replace=True).mean()
    return float(values.mean()), tuple(float(x) for x in np.quantile(boot, [0.025, 0.975]))


def main():
    print("Boundary 1 — cache <-> ROUTE phase diagram")
    print("K=2 preallocated anchors; same 8-observation budget; continuous 4-D Gabor receiver geometry")
    print(f"{'scale':>6} {'cacheOv':>9} {'routeOv':>9} {'delta':>9} {'CIlo':>9} {'CIhi':>9} {'route%':>8}")
    print("-" * 70)
    rows = []
    for scale in SCALES:
        runs = [run_seed(seed, scale) for seed in SEEDS]
        cache = np.asarray([np.mean(r["cache"]["overlap"][LATE:]) for r in runs])
        route = np.asarray([np.mean(r["route"]["overlap"][LATE:]) for r in runs])
        delta, (lo, hi) = paired_ci(route - cache)
        route_fraction = float(np.mean([np.mean(r["route"]["routed"][LATE:]) for r in runs]))
        rows.append((scale, float(cache.mean()), float(route.mean()), delta, lo, hi, route_fraction))
        print(
            f"{scale:6.2f} {cache.mean():9.3f} {route.mean():9.3f} {delta:+9.3f} "
            f"{lo:+9.3f} {hi:+9.3f} {100*route_fraction:7.1f}%"
        )

    positive = [row[0] for row in rows if row[4] > 0.0]
    negative = [row[0] for row in rows if row[5] < 0.0]
    print()
    print("scales with CI entirely above zero:", positive)
    print("scales with CI entirely below zero:", negative)
    print("BOUNDARY1_COMPLETE = True")


if __name__ == "__main__":
    main()
