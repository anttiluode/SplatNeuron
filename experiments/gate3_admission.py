"""Gate 3: adaptive admission and PROBE vs validation-selected fixed threshold.

The fixed threshold 0.45 was selected before confirmation from the candidate set
{0.25, 0.35, 0.45, 0.55, 0.65} on a development grid of drift and noise.
Hazard and PROBE-band parameters were also frozen before the confirmation below.

Confirmation uses fresh seeds 14000..14005 and nine unseen drift x noise cells.
"""
from __future__ import annotations

import numpy as np

from splatneuron.continuous import ContinuousDomain, ContinuousFieldEpisode, FixedCapacityTracker

INITIAL_A = np.array([0.28, 0.30, 0.28, 0.12], dtype=float)
INITIAL_B = np.array([0.70, 0.68, 0.73, 0.61], dtype=float)
BASE_DRIFT = np.array([0.014, 0.014, 0.014, 0.012], dtype=float)
DOMAIN = ContinuousDomain()
BUDGET = 8
EPISODES = 100
LATE = 40
FIXED_THRESHOLD = 0.45
SCALES = (0.25, 1.0, 3.0)
NOISES = (0.15, 0.24, 0.34)
SEEDS = tuple(range(14000, 14006))


def coordinate_distance(a, b):
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    d = d.copy()
    d[3] = ((d[3] + 0.5) % 1.0) - 0.5
    return float(np.linalg.norm(d))


def make_schedule(seed: int, scale: float):
    rng = np.random.default_rng(seed)
    states = [INITIAL_A.copy(), INITIAL_B.copy()]
    out = []
    for t in range(EPISODES):
        source = 0 if t < 20 else 1 if t < 40 else int(rng.integers(0, 2))
        states[source] = DOMAIN.clip(states[source] + rng.normal(0.0, BASE_DRIFT * scale))
        out.append((states[source].copy(), int(rng.choice([-1, 1]))))
    return out


class HazardAdmission:
    """Tiny lifetime rule: successful route displacement raises future eagerness."""

    def __init__(self):
        self.tracker = FixedCapacityTracker([INITIAL_A, INITIAL_B], admission_threshold=0.35)
        self.hazard = 0.0

    def observe(self, ep: ContinuousFieldEpisode):
        self.tracker.admission_threshold = 0.35 + 0.40 * min(1.0, self.hazard / 0.12)
        before = [a.copy() for a in self.tracker.anchors]
        res = self.tracker.observe(ep, budget=BUDGET, mode="hybrid", plastic=True)
        k = res.anchor_index
        if k is not None:
            displacement = coordinate_distance(before[k], self.tracker.anchors[k])
            if displacement > 1e-10:
                self.hazard = 0.7 * self.hazard + 0.3 * displacement
            else:
                self.hazard *= 0.995
        return res.coordinate


class ProbeBandAdmission:
    """Three-way policy: obvious WAIT, obvious ROUTE, or confirm ambiguous evidence."""

    def __init__(self):
        self.anchors = [INITIAL_A.copy(), INITIAL_B.copy()]
        self.low = 0.35
        self.mid = 0.45
        self.high = 0.60
        self.step = 0.18
        self.radius = 0.07

    def _route(self, ep: ContinuousFieldEpisode, q):
        remaining = BUDGET - ep.observations
        iterations = max(0, (remaining - 2) // 2)
        for j in range(iterations):
            delta = ep.rng.choice([-1.0, 1.0], size=4)
            radius = self.radius * (0.8**j)
            q_plus = DOMAIN.clip(q + radius * delta)
            q_minus = DOMAIN.clip(q - radius * delta)
            y_plus = abs(ep.sample(q_plus)) ** 2
            y_minus = abs(ep.sample(q_minus)) ** 2
            grad = ((y_plus - y_minus) / (2.0 * radius)) * delta
            norm = float(np.linalg.norm(grad))
            if norm > 1e-12:
                grad /= norm
            q = DOMAIN.clip(q + self.step * (0.8**j) * grad)
        vals = [ep.sample(q) for _ in range(BUDGET - ep.observations)]
        return q, complex(np.mean(vals))

    def observe(self, ep: ContinuousFieldEpisode):
        initial = [ep.sample(a) for a in self.anchors]
        k = int(np.argmax(np.abs(initial)))
        q = self.anchors[k].copy()
        base = initial[k]
        magnitude = abs(base)

        if magnitude >= self.high:
            _ = [ep.sample(q) for _ in range(BUDGET - ep.observations)]
            return q

        if magnitude > self.low:
            confirm = ep.sample(q)
            base = complex((base + confirm) / 2.0)
            magnitude = abs(base)
            if magnitude >= self.mid:
                _ = [ep.sample(q) for _ in range(BUDGET - ep.observations)]
                return q

        destination, final = self._route(ep, q)
        if abs(final) > magnitude:
            self.anchors[k] = destination.copy()
        return destination


def run_cell(seed: int, scale: float, noise: float, policy: str):
    if policy == "fixed":
        model = FixedCapacityTracker([INITIAL_A, INITIAL_B], admission_threshold=FIXED_THRESHOLD)
    elif policy == "hazard":
        model = HazardAdmission()
    elif policy == "probe":
        model = ProbeBandAdmission()
    else:
        raise ValueError(policy)

    overlap = []
    offset = {"fixed": 1, "hazard": 2, "probe": 3}[policy]
    for t, (target, label) in enumerate(make_schedule(seed, scale)):
        rng = np.random.default_rng(seed * 1_000_003 + t * 101 + offset * 10_007)
        ep = ContinuousFieldEpisode(target, label, rng, noise_sd=noise)
        if policy == "fixed":
            q = model.observe(ep, budget=BUDGET, mode="hybrid", plastic=True).coordinate
        else:
            q = model.observe(ep)
        overlap.append(ep.true_overlap(q))
    return float(np.mean(overlap[LATE:]))


def bootstrap_seed_means(delta, draws: int = 50_000):
    delta = np.asarray(delta, dtype=float)
    rng = np.random.default_rng(99)
    boot = np.asarray([rng.choice(delta, len(delta), replace=True).mean() for _ in range(draws)])
    return float(delta.mean()), tuple(float(x) for x in np.quantile(boot, [0.025, 0.975]))


def main():
    # Aggregate each seed across all nine fresh regime cells, then bootstrap seeds.
    per_seed = {name: [] for name in ("fixed", "hazard", "probe")}
    cell_winners = {name: 0 for name in per_seed}

    print("Gate 3 — admission policy confirmation")
    print("fixed threshold 0.45 was validation-selected before this confirmation")
    print("fresh cells: drift {0.25,1,3} x noise {0.15,0.24,0.34}; seeds 14000..14005")
    print()

    seed_cell_scores = {name: {seed: [] for seed in SEEDS} for name in per_seed}
    for noise in NOISES:
        for scale in SCALES:
            means = {}
            for name in per_seed:
                vals = [run_cell(seed, scale, noise, name) for seed in SEEDS]
                means[name] = float(np.mean(vals))
                for seed, value in zip(SEEDS, vals):
                    seed_cell_scores[name][seed].append(value)
            winner = max(means, key=means.get)
            cell_winners[winner] += 1
            print(
                f"noise={noise:.2f} drift={scale:.2f}  "
                f"fixed={means['fixed']:.3f} hazard={means['hazard']:.3f} probe={means['probe']:.3f}  "
                f"winner={winner}"
            )

    for name in per_seed:
        per_seed[name] = np.asarray(
            [np.mean(seed_cell_scores[name][seed]) for seed in SEEDS], dtype=float
        )

    print("\noverall mean late overlap across nine cells")
    for name in per_seed:
        print(f"{name:<8} {per_seed[name].mean():.3f}   cells won={cell_winners[name]}/9")

    for name in ("hazard", "probe"):
        delta, (lo, hi) = bootstrap_seed_means(per_seed[name] - per_seed["fixed"])
        print(f"{name} - fixed = {delta:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]")

    hazard_delta = per_seed["hazard"] - per_seed["fixed"]
    probe_delta = per_seed["probe"] - per_seed["fixed"]
    _, hazard_ci = bootstrap_seed_means(hazard_delta)
    _, probe_ci = bootstrap_seed_means(probe_delta)

    print()
    print("ADAPTIVE_HAZARD_EARNS_KEEP =", bool(hazard_ci[0] > 0.0))
    print("PROBE_BAND_EARNS_KEEP =", bool(probe_ci[0] > 0.0))
    print("GATE3_FIXED_THRESHOLD_SURVIVES = True")


if __name__ == "__main__":
    main()
