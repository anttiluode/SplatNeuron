"""Gate 5: does the cache<->ROUTE phase require Gabor/splat geometry?

A diagonal RBF observation kernel is fitted once to local correlation lengths of
rendered continuous Gabor receivers. The same fixed-capacity router and budget
are then run on Gabor and RBF media with fresh seeds.

The attacker wins if the generic manifold reproduces the qualitative ROUTE
value phase across environmental drift.
"""
from __future__ import annotations

import numpy as np

from splatneuron.continuous import ContinuousDomain, ContinuousFieldEpisode, FixedCapacityTracker
from splatneuron.core import complex_gabor

DOMAIN = ContinuousDomain()
A = np.array([0.28, 0.30, 0.28, 0.12])
B = np.array([0.70, 0.68, 0.73, 0.61])
DRIFT = np.array([0.014, 0.014, 0.014, 0.012])
SCALES = (0.0, 0.5, 1.0, 2.0, 4.0)
SEEDS = tuple(range(18000, 18012))
EPISODES = 160
LATE = 70
THRESHOLD = 0.55
BUDGET = 8
FIT_SEED = 123
FIT_PAIRS = 1600
SIZE = 20


def periodic_difference(a, b):
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    d = d.copy()
    d[3] = ((d[3] + 0.5) % 1.0) - 0.5
    return d


def fit_rbf_beta():
    """Fit a boring diagonal RBF metric to local Gabor overlap decay."""
    rng = np.random.default_rng(FIT_SEED)
    design = []
    target = []
    for _ in range(FIT_PAIRS):
        a = np.array(
            [
                rng.uniform(0.18, 0.82),
                rng.uniform(0.18, 0.82),
                rng.uniform(0.05, 0.95),
                rng.random(),
            ]
        )
        b = DOMAIN.clip(a + rng.normal(0.0, [0.10, 0.10, 0.13, 0.12]))
        ga = complex_gabor(DOMAIN.geometry(a), SIZE)
        gb = complex_gabor(DOMAIN.geometry(b), SIZE)
        overlap = max(abs(np.vdot(ga, gb)), 1e-5)
        d = periodic_difference(a, b)
        design.append(d * d)
        target.append(-np.log(overlap))
    beta = np.linalg.lstsq(np.asarray(design), np.asarray(target), rcond=None)[0]
    return np.maximum(beta, 1e-6)


RBF_BETA = fit_rbf_beta()


def rbf_kernel(a, b):
    d = periodic_difference(a, b)
    return float(np.exp(-np.dot(RBF_BETA, d * d)))


class RBFFieldEpisode:
    """Generic smooth observation manifold; no splats, pixels, phase, or FFT."""

    def __init__(
        self,
        target,
        label,
        rng,
        *,
        noise_sd=0.18,
        distractors=2,
        distractor_sd=0.08,
    ):
        self.domain = DOMAIN
        self.target = DOMAIN.clip(target)
        self.label = int(label)
        self.rng = rng
        self.noise_sd = float(noise_sd)
        self.observations = 0
        self.distractor_q = []
        self.distractor_a = []
        for _ in range(int(distractors)):
            self.distractor_q.append(
                np.array(
                    [
                        rng.uniform(DOMAIN.x_min, DOMAIN.x_max),
                        rng.uniform(DOMAIN.y_min, DOMAIN.y_max),
                        rng.random(),
                        rng.random(),
                    ]
                )
            )
            self.distractor_a.append(rng.normal(0.0, distractor_sd))

    def sample(self, coordinate):
        q = DOMAIN.clip(coordinate)
        z = self.label * rbf_kernel(q, self.target)
        for dq, amp in zip(self.distractor_q, self.distractor_a):
            z += amp * rbf_kernel(q, dq)
        z = complex(
            z + self.rng.normal(0.0, self.noise_sd),
            self.rng.normal(0.0, self.noise_sd),
        )
        self.observations += 1
        return z

    def true_overlap(self, coordinate):
        return rbf_kernel(coordinate, self.target)


def schedule(seed, scale):
    rng = np.random.default_rng(seed)
    states = [A.copy(), B.copy()]
    out = []
    for t in range(EPISODES):
        source = 0 if t < 35 else 1 if t < 70 else int(rng.integers(0, 2))
        states[source] = DOMAIN.clip(states[source] + rng.normal(0.0, DRIFT * scale))
        out.append((states[source].copy(), int(rng.choice([-1, 1]))))
    return out


def run(seed, scale, medium, policy):
    tracker = FixedCapacityTracker([A, B], admission_threshold=THRESHOLD)
    overlap = []
    actions = []
    for t, (target, label) in enumerate(schedule(seed, scale)):
        medium_offset = 1 if medium == "gabor" else 2
        policy_offset = 0 if policy == "cache" else 10
        rng = np.random.default_rng(
            seed * 1_000_003 + t * 101 + (medium_offset + policy_offset) * 10_007
        )
        if medium == "gabor":
            episode = ContinuousFieldEpisode(target, label, rng, size=SIZE)
        else:
            episode = RBFFieldEpisode(target, label, rng)
        result = tracker.observe(
            episode,
            budget=BUDGET,
            mode="cache" if policy == "cache" else "hybrid",
            plastic=policy != "cache",
        )
        overlap.append(episode.true_overlap(result.coordinate))
        actions.append(result.action == "ROUTE")
    return float(np.mean(overlap[LATE:])), float(np.mean(actions[LATE:]))


def paired_ci(values, draws=20_000):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(555)
    boot = np.asarray(
        [rng.choice(values, len(values), replace=True).mean() for _ in range(draws)]
    )
    return float(values.mean()), tuple(float(x) for x in np.quantile(boot, [0.025, 0.975]))


def main():
    print("Gate 5 — generic smooth geometry attacker")
    print("RBF beta", RBF_BETA)
    print("effective lengths", np.sqrt(1.0 / (2.0 * RBF_BETA)))
    print("fresh seeds 18000..18011")
    print()
    print(f"{'scale':>5} {'medium':>7} {'cache':>8} {'route':>8} {'delta':>8} {'CIlo':>8} {'CIhi':>8} {'route%':>8}")

    rows = {}
    for scale in SCALES:
        for medium in ("gabor", "rbf"):
            cache = np.asarray([run(s, scale, medium, "cache")[0] for s in SEEDS])
            routed = np.asarray([run(s, scale, medium, "route")[0] for s in SEEDS])
            route_fraction = float(
                np.mean([run(s, scale, medium, "route")[1] for s in SEEDS])
            )
            delta, (lo, hi) = paired_ci(routed - cache)
            rows[(scale, medium)] = (delta, lo, hi)
            print(
                f"{scale:5.1f} {medium:>7} {cache.mean():8.3f} {routed.mean():8.3f} "
                f"{delta:+8.3f} {lo:+8.3f} {hi:+8.3f} {100*route_fraction:7.1f}%"
            )

    gabor = np.asarray([rows[(s, "gabor")][0] for s in SCALES])
    rbf = np.asarray([rows[(s, "rbf")][0] for s in SCALES])
    sign_match = int(np.sum(np.sign(gabor) == np.sign(rbf)))
    profile_correlation = float(np.corrcoef(gabor, rbf)[0, 1])
    reproduced = sign_match >= 4 and profile_correlation >= 0.7

    print()
    print("sign match", sign_match, "/", len(SCALES))
    print("delta-profile correlation", profile_correlation)
    print("GENERIC_MANIFOLD_REPRODUCES_PHASE =", reproduced)
    print("GABOR_SPECIFIC_CLAIM_EARNS_KEEP =", False if reproduced else "UNRESOLVED")


if __name__ == "__main__":
    main()
