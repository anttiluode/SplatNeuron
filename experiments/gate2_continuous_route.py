"""Gate 2: continuous off-grid ROUTE under fixed capacity and fixed budget.

Development history
-------------------
Seeds 0..19, 1000..1019, and 2000..2019 were exploratory/development. They
fixed the values below before the final confirmation run. The printed
confirmation uses seeds 3000..3019 and must not be retuned in response to that
result.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from splatneuron.continuous import ContinuousDomain, ContinuousFieldEpisode, FixedCapacityTracker

BUDGET = 8
EPISODES = 180
LATE_START = 80
CONFIRMATION_SEEDS = tuple(range(3000, 3020))

INITIAL_A = np.array([0.28, 0.30, 0.28, 0.12], dtype=float)
INITIAL_B = np.array([0.70, 0.68, 0.73, 0.61], dtype=float)
DRIFT_SD = np.array([0.014, 0.014, 0.014, 0.012], dtype=float)


@dataclass
class Trace:
    correct: list[bool]
    overlap: list[float]
    actions: list[str]
    work: list[int]


def make_schedule(seed: int, n: int = EPISODES):
    rng = np.random.default_rng(seed)
    domain = ContinuousDomain()
    states = [INITIAL_A.copy(), INITIAL_B.copy()]
    schedule = []
    for t in range(n):
        if t < 40:
            source = 0
        elif t < 80:
            source = 1
        else:
            source = int(rng.integers(0, 2))
        states[source] = domain.clip(states[source] + rng.normal(0.0, DRIFT_SD))
        label = int(rng.choice([-1, 1]))
        schedule.append((source, states[source].copy(), label))
    return schedule


def random_observer(ep: ContinuousFieldEpisode, budget: int = BUDGET):
    best_z = 0j
    best_q = None
    for _ in range(budget):
        q = np.array(
            [
                ep.rng.uniform(ep.domain.x_min, ep.domain.x_max),
                ep.rng.uniform(ep.domain.y_min, ep.domain.y_max),
                ep.rng.random(),
                ep.rng.random(),
            ]
        )
        z = ep.sample(q)
        if best_q is None or abs(z) > abs(best_z):
            best_z, best_q = z, q
    return best_z, best_q, "RANDOM"


def oracle_observer(ep: ContinuousFieldEpisode, budget: int = BUDGET):
    vals = [ep.sample(ep.target) for _ in range(budget)]
    return complex(np.mean(vals)), ep.target.copy(), "ORACLE"


def run_seed(seed: int):
    schedule = make_schedule(seed)
    initial = [INITIAL_A.copy(), INITIAL_B.copy()]
    policies = {
        "address_cache": FixedCapacityTracker(initial),
        "hybrid_plastic": FixedCapacityTracker(initial),
        "always_route": FixedCapacityTracker(initial),
    }
    traces = {
        name: Trace([], [], [], [])
        for name in (
            "address_cache",
            "hybrid_plastic",
            "hybrid_reset",
            "always_route",
            "random",
            "oracle",
        )
    }

    for t, (_source, target, label) in enumerate(schedule):
        for pi, name in enumerate(traces):
            erng = np.random.default_rng(seed * 1_000_003 + t * 101 + pi * 10_007)
            ep = ContinuousFieldEpisode(target, label, erng)

            if name == "address_cache":
                res = policies[name].observe(ep, budget=BUDGET, mode="cache", plastic=False)
                z, q, action, work = res.response, res.coordinate, res.action, res.work
            elif name == "hybrid_plastic":
                res = policies[name].observe(ep, budget=BUDGET, mode="hybrid", plastic=True)
                z, q, action, work = res.response, res.coordinate, res.action, res.work
            elif name == "always_route":
                res = policies[name].observe(ep, budget=BUDGET, mode="always_route", plastic=True)
                z, q, action, work = res.response, res.coordinate, res.action, res.work
            elif name == "hybrid_reset":
                reset = FixedCapacityTracker(initial)
                res = reset.observe(ep, budget=BUDGET, mode="hybrid", plastic=False)
                z, q, action, work = res.response, res.coordinate, res.action, res.work
            elif name == "random":
                z, q, action = random_observer(ep)
                work = ep.observations
            else:
                z, q, action = oracle_observer(ep)
                work = ep.observations

            tr = traces[name]
            tr.correct.append((1 if float(np.real(z)) >= 0.0 else -1) == label)
            tr.overlap.append(ep.true_overlap(q))
            tr.actions.append(action)
            tr.work.append(int(work))
    return traces


def bootstrap_paired(values: np.ndarray, *, draws: int = 20_000, seed: int = 8675309):
    rng = np.random.default_rng(seed)
    boot = np.empty(draws, dtype=float)
    for i in range(draws):
        boot[i] = rng.choice(values, size=len(values), replace=True).mean()
    return float(values.mean()), tuple(float(x) for x in np.quantile(boot, [0.025, 0.975]))


def summarize(seeds=CONFIRMATION_SEEDS):
    runs = [run_seed(int(seed)) for seed in seeds]
    names = tuple(runs[0].keys())
    out = {"policies": {}, "contrasts": {}}

    for name in names:
        correct = np.asarray([r[name].correct for r in runs], dtype=float)
        overlap = np.asarray([r[name].overlap for r in runs], dtype=float)
        work = np.asarray([r[name].work for r in runs], dtype=float)
        route_fraction = float(np.mean([[a == "ROUTE" for a in r[name].actions] for r in runs]))
        out["policies"][name] = {
            "accuracy": float(correct.mean()),
            "overlap": float(overlap.mean()),
            "late_accuracy": float(correct[:, LATE_START:].mean()),
            "late_overlap": float(overlap[:, LATE_START:].mean()),
            "mean_work": float(work.mean()),
            "route_fraction": route_fraction,
        }

    for baseline in ("address_cache", "hybrid_reset", "always_route", "random"):
        late_overlap_diff = np.asarray(
            [
                np.mean(r["hybrid_plastic"].overlap[LATE_START:])
                - np.mean(r[baseline].overlap[LATE_START:])
                for r in runs
            ],
            dtype=float,
        )
        late_acc_diff = np.asarray(
            [
                np.mean(r["hybrid_plastic"].correct[LATE_START:])
                - np.mean(r[baseline].correct[LATE_START:])
                for r in runs
            ],
            dtype=float,
        )
        ov_mean, ov_ci = bootstrap_paired(late_overlap_diff)
        acc_mean, acc_ci = bootstrap_paired(late_acc_diff)
        out["contrasts"][baseline] = {
            "late_overlap_delta": ov_mean,
            "late_overlap_ci95": ov_ci,
            "late_accuracy_delta": acc_mean,
            "late_accuracy_ci95": acc_ci,
        }
    return out


def verdict(out):
    p = out["policies"]
    c = out["contrasts"]
    return {
        "all_policies_use_exact_budget": all(abs(v["mean_work"] - BUDGET) < 1e-12 for v in p.values()),
        "continuous_route_beats_address_cache_on_observability": c["address_cache"]["late_overlap_ci95"][0] > 0.0,
        "persistent_geometry_beats_reset_router_on_observability": c["hybrid_reset"]["late_overlap_ci95"][0] > 0.0,
        "admission_beats_always_route_on_observability": c["always_route"]["late_overlap_ci95"][0] > 0.0,
        "continuous_route_beats_random_on_observability": c["random"]["late_overlap_ci95"][0] > 0.0,
    }


def print_report(out, checks):
    print("Gate 2 — continuous off-grid ROUTE with fixed capacity")
    print("confirmation seeds 3000..3019; K=2; budget=8 observations/episode")
    print("targets drift continuously in x, y, frequency, orientation")
    print()
    print(f"{'policy':<16} {'acc':>7} {'overlap':>9} {'lateAcc':>9} {'lateOv':>9} {'route%':>8} {'work':>6}")
    print("-" * 72)
    for name, v in out["policies"].items():
        print(
            f"{name:<16} {v['accuracy']:7.3f} {v['overlap']:9.3f} "
            f"{v['late_accuracy']:9.3f} {v['late_overlap']:9.3f} "
            f"{100*v['route_fraction']:7.1f}% {v['mean_work']:6.1f}"
        )
    print("\npaired confirmation contrasts: hybrid_plastic minus baseline")
    for name, v in out["contrasts"].items():
        lo, hi = v["late_overlap_ci95"]
        alo, ahi = v["late_accuracy_ci95"]
        print(
            f"  vs {name:<13} late overlap {v['late_overlap_delta']:+.3f} "
            f"95% CI [{lo:+.3f}, {hi:+.3f}] | "
            f"late accuracy {v['late_accuracy_delta']:+.3f} "
            f"95% CI [{alo:+.3f}, {ahi:+.3f}]"
        )
    print()
    for key, ok in checks.items():
        print(f"{key:<62} {'PASS' if ok else 'FAIL'}")
    print(f"\nGATE2_MECHANISM_KEEP = {all(checks.values())}")
    print("GATE2_TASK_PERFORMANCE_CLAIM = NOT_ESTABLISHED")


def main():
    out = summarize()
    checks = verdict(out)
    print_report(out, checks)
    # A failed scientific gate is a recorded result, not a software failure.
    # CI verifies reproducibility and therefore exits zero after printing verdicts.


if __name__ == "__main__":
    main()
