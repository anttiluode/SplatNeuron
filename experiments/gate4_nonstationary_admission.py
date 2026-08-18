"""Gate 4: last admission test on within-run regime changes.

Frozen from a separate validation sequence:
- robust fixed admission threshold = 0.55
- self-tuning step size = 0.05
- self-tuner initial threshold = 0.45

Confirmation changes segment order/strength/noise and uses untouched seeds
16000..16009. This file intentionally closes the admission branch if the
self-tuner does not beat the fixed incumbent.
"""
from __future__ import annotations

import numpy as np

from splatneuron.continuous import ContinuousDomain, ContinuousFieldEpisode, FixedCapacityTracker

A = np.array([0.28, 0.30, 0.28, 0.12])
B = np.array([0.70, 0.68, 0.73, 0.61])
D = np.array([0.014, 0.014, 0.014, 0.012])
DOMAIN = ContinuousDomain()
SEGMENTS = (
    (45, 0.8, 0.18),
    (55, 0.3, 0.36),
    (65, 2.5, 0.16),
    (45, 0.1, 0.12),
    (60, 2.0, 0.30),
)
SEEDS = tuple(range(16000, 16010))
FIXED_THRESHOLD = 0.55
SELF_STEP = 0.05
FIXED_CANDIDATES = (0.25, 0.35, 0.45, 0.55, 0.65)
BUDGET = 8


def coordinate_distance(a, b):
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    d = d.copy()
    d[3] = ((d[3] + 0.5) % 1.0) - 0.5
    return float(np.linalg.norm(d))


def schedule(seed):
    rng = np.random.default_rng(seed)
    states = [A.copy(), B.copy()]
    out = []
    for si, (length, drift_scale, noise_sd) in enumerate(SEGMENTS):
        for _ in range(length):
            source = int(rng.integers(0, 2))
            states[source] = DOMAIN.clip(
                states[source] + rng.normal(0.0, D * drift_scale)
            )
            out.append((si, states[source].copy(), int(rng.choice([-1, 1])), noise_sd))
    return out


class SelfTuningThreshold:
    """One-scalar lifetime controller; no regime/noise/hazard label.

    A routed observation that actually moves the persistent anchor raises the
    future threshold (more willingness to ROUTE). A route that fails to improve
    the anchor lowers it. Nothing else is learned.
    """

    def __init__(self):
        self.tracker = FixedCapacityTracker([A, B], admission_threshold=0.45)
        self.threshold = 0.45

    def observe(self, episode):
        self.tracker.admission_threshold = self.threshold
        before = [a.copy() for a in self.tracker.anchors]
        result = self.tracker.observe(episode, budget=BUDGET, mode="hybrid", plastic=True)
        if result.action == "ROUTE" and result.anchor_index is not None:
            k = result.anchor_index
            changed = coordinate_distance(before[k], self.tracker.anchors[k]) > 1e-10
            self.threshold = float(
                np.clip(
                    self.threshold + (SELF_STEP if changed else -SELF_STEP),
                    0.25,
                    0.75,
                )
            )
        return result


def run(seed, kind, threshold=None):
    if kind == "fixed":
        model = FixedCapacityTracker([A, B], admission_threshold=float(threshold))
    else:
        model = SelfTuningThreshold()

    values = []
    segment_values = [[] for _ in SEGMENTS]
    actions = []
    thresholds = []
    for t, (si, target, label, noise_sd) in enumerate(schedule(seed)):
        offset = 1 if kind == "fixed" else 2
        rng = np.random.default_rng(seed * 1_000_003 + t * 101 + offset * 10_007)
        episode = ContinuousFieldEpisode(target, label, rng, noise_sd=noise_sd)
        if kind == "fixed":
            result = model.observe(episode, budget=BUDGET, mode="hybrid", plastic=True)
            thresholds.append(float(threshold))
        else:
            result = model.observe(episode)
            thresholds.append(model.threshold)
        overlap = episode.true_overlap(result.coordinate)
        values.append(overlap)
        segment_values[si].append(overlap)
        actions.append(result.action)

    return {
        "mean": float(np.mean(values)),
        "segments": [float(np.mean(v)) for v in segment_values],
        "route_fraction": float(np.mean([a == "ROUTE" for a in actions])),
        "thresholds": thresholds,
    }


def paired_ci(delta, draws=50_000):
    delta = np.asarray(delta, dtype=float)
    rng = np.random.default_rng(20260817)
    boot = np.asarray(
        [rng.choice(delta, len(delta), replace=True).mean() for _ in range(draws)]
    )
    return float(delta.mean()), tuple(float(x) for x in np.quantile(boot, [0.025, 0.975]))


def main():
    fixed_runs = {
        th: [run(seed, "fixed", th) for seed in SEEDS]
        for th in FIXED_CANDIDATES
    }
    fixed = fixed_runs[FIXED_THRESHOLD]
    adaptive = [run(seed, "self") for seed in SEEDS]

    fixed_mean = float(np.mean([r["mean"] for r in fixed]))
    adaptive_mean = float(np.mean([r["mean"] for r in adaptive]))
    delta, ci = paired_ci(
        [a["mean"] - f["mean"] for a, f in zip(adaptive, fixed)]
    )

    print("Gate 4 — within-run nonstationary admission")
    print("frozen from validation: fixed=.55; self-step=.05; self initial=.45")
    print("confirmation seeds 16000..16009")
    print()
    print(f"fixed mean overlap      {fixed_mean:.4f}")
    print(f"self-tune mean overlap  {adaptive_mean:.4f}")
    print(f"self - fixed            {delta:+.4f} 95% CI [{ci[0]:+.4f}, {ci[1]:+.4f}]")
    print(f"fixed route fraction    {np.mean([r['route_fraction'] for r in fixed]):.3f}")
    print(f"self route fraction     {np.mean([r['route_fraction'] for r in adaptive]):.3f}")
    print()

    for si, segment in enumerate(SEGMENTS):
        f = float(np.mean([r["segments"][si] for r in fixed]))
        a = float(np.mean([r["segments"][si] for r in adaptive]))
        d, segment_ci = paired_ci(
            [r1["segments"][si] - r0["segments"][si] for r1, r0 in zip(adaptive, fixed)]
        )
        scores = {
            th: float(np.mean([r["segments"][si] for r in fixed_runs[th]]))
            for th in FIXED_CANDIDATES
        }
        best_th = max(scores, key=scores.get)
        print(
            f"seg{si+1} {segment}: fixed={f:.3f} self={a:.3f} "
            f"delta={d:+.3f} CI[{segment_ci[0]:+.3f},{segment_ci[1]:+.3f}] "
            f"hindsight_best_fixed={best_th:.2f} ({scores[best_th]:.3f})"
        )

    print()
    print("self final threshold mean", np.mean([r["thresholds"][-1] for r in adaptive]))
    print("SELF_TUNING_EARNS_KEEP =", bool(ci[0] > 0.0))
    print("FIXED_ROBUST_POLICY_SURVIVES =", bool(ci[0] <= 0.0))
    print("ADMISSION_BRANCH_STATUS = CLOSED")


if __name__ == "__main__":
    main()
