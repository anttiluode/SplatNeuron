from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from splatneuron import SplatGeometry, complex_gabor


@dataclass(frozen=True)
class Row:
    offset: float
    overlap: float
    wait_accuracy: float
    route_accuracy: float
    wait_theory: float
    route_theory: float


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def projected_stat(samples: np.ndarray, coefficient: complex) -> np.ndarray:
    """Project a complex receiver response onto its calibrated signal direction."""
    if abs(coefficient) < 1e-15:
        return np.real(samples)
    unit = np.conj(coefficient) / abs(coefficient)
    return np.real(unit * samples)


def simulate_offset(
    offset: float,
    *,
    seed: int,
    episodes: int = 20000,
    total_budget: int = 8,
    route_tax: int = 3,
    signal_amplitude: float = 0.25,
    noise_sd: float = 0.70,
    size: int = 32,
) -> Row:
    """Compare WAIT and an oracle ROUTE lower bound at one nonzero-overlap distance.

    WAIT spends the full observation budget at the home receiver. ROUTE pays a
    declared route-acquisition tax, then spends the remaining budget at the true
    target receiver. The ROUTE arm is intentionally oracle: this experiment only
    measures the crossover at which changing C could be worth its acquisition cost.
    A later gate must earn the route without target access.
    """
    if route_tax >= total_budget:
        raise ValueError("route_tax must leave at least one target observation")

    home = SplatGeometry(x=0.40, y=0.50, sigma=0.12, freq=4.0, theta=0.0)
    target = SplatGeometry(x=0.40 + float(offset), y=0.50, sigma=0.12, freq=4.0, theta=0.0)

    home_atom = complex_gabor(home, size=size)
    target_atom = complex_gabor(target, size=size)
    coefficient = complex(np.vdot(home_atom, target_atom))
    overlap = float(abs(coefficient))

    rng = np.random.default_rng(seed)
    labels = rng.choice(np.asarray([-1.0, 1.0]), size=episodes)

    wait_noise = rng.normal(0.0, noise_sd, size=(episodes, total_budget)) + 1j * rng.normal(
        0.0, noise_sd, size=(episodes, total_budget)
    )
    wait_samples = labels[:, None] * signal_amplitude * coefficient + wait_noise
    wait_mean = wait_samples.mean(axis=1)
    wait_stat = projected_stat(wait_mean, coefficient)
    wait_pred = np.where(wait_stat >= 0.0, 1.0, -1.0)

    route_samples_n = total_budget - route_tax
    route_noise = rng.normal(0.0, noise_sd, size=(episodes, route_samples_n)) + 1j * rng.normal(
        0.0, noise_sd, size=(episodes, route_samples_n)
    )
    route_samples = labels[:, None] * signal_amplitude + route_noise
    route_mean = route_samples.mean(axis=1)
    route_pred = np.where(np.real(route_mean) >= 0.0, 1.0, -1.0)

    wait_accuracy = float(np.mean(wait_pred == labels))
    route_accuracy = float(np.mean(route_pred == labels))

    wait_snr = signal_amplitude * overlap * math.sqrt(total_budget) / noise_sd
    route_snr = signal_amplitude * math.sqrt(route_samples_n) / noise_sd

    return Row(
        offset=float(offset),
        overlap=overlap,
        wait_accuracy=wait_accuracy,
        route_accuracy=route_accuracy,
        wait_theory=normal_cdf(wait_snr),
        route_theory=normal_cdf(route_snr),
    )


def run():
    total_budget = 8
    route_tax = 3
    offsets = np.arange(0.0, 0.201, 0.01)
    rows = [
        simulate_offset(
            float(offset),
            seed=731_009 + i * 104_729,
            total_budget=total_budget,
            route_tax=route_tax,
        )
        for i, offset in enumerate(offsets)
    ]

    predicted_overlap = math.sqrt((total_budget - route_tax) / total_budget)
    predicted_cross = min(rows, key=lambda row: abs(row.overlap - predicted_overlap))

    empirical_cross = None
    for left, right in zip(rows[:-1], rows[1:]):
        left_gap = left.wait_accuracy - left.route_accuracy
        right_gap = right.wait_accuracy - right.route_accuracy
        if left_gap >= 0.0 and right_gap < 0.0:
            empirical_cross = (left.offset, right.offset)
            break

    print("Boundary 0 — WAIT versus ROUTE with nonzero overlap")
    print("continuous off-grid target geometry; actual rendered Gabor inner products")
    print(f"total observation budget = {total_budget}")
    print(f"declared oracle route tax = {route_tax}")
    print(f"predicted crossover overlap = sqrt((B-tax)/B) = {predicted_overlap:.6f}")
    print()
    print(f"{'dx':>5} {'|<home,target>|':>16} {'WAIT':>8} {'ROUTE':>8} {'W theory':>9} {'R theory':>9}")
    print("-" * 65)
    for row in rows:
        print(
            f"{row.offset:5.2f} {row.overlap:16.6f} {row.wait_accuracy:8.3f} "
            f"{row.route_accuracy:8.3f} {row.wait_theory:9.3f} {row.route_theory:9.3f}"
        )

    near = {round(row.offset, 2): row for row in rows}
    checks = {
        "all_overlaps_positive": min(row.overlap for row in rows) > 0.10,
        "WAIT_wins_near_home": near[0.05].wait_accuracy > near[0.05].route_accuracy + 0.02,
        "ROUTE_wins_farther_away": near[0.15].route_accuracy > near[0.15].wait_accuracy + 0.02,
        "theory_matches_empirical_each_arm": max(
            max(abs(row.wait_accuracy - row.wait_theory), abs(row.route_accuracy - row.route_theory))
            for row in rows
        ) < 0.025,
        "empirical_crossover_found": empirical_cross is not None,
        "empirical_crossover_near_predicted": empirical_cross is not None
        and empirical_cross[0] <= predicted_cross.offset + 0.02
        and empirical_cross[1] >= predicted_cross.offset - 0.02,
    }

    print()
    print(
        f"predicted discrete crossover near dx={predicted_cross.offset:.2f}, "
        f"overlap={predicted_cross.overlap:.3f}"
    )
    print(f"empirical sign-change interval = {empirical_cross}")
    print()
    for key, ok in checks.items():
        print(f"{key:<44} {'PASS' if ok else 'FAIL'}")

    passed = all(checks.values())
    print(f"\nBOUNDARY0_PASS = {passed}")
    print("Interpretation: WAIT and ROUTE occupy different sides of a measurable cost/SNR boundary.")
    print("The ROUTE arm is oracle; this does NOT show that a search policy can find the better view cheaply.")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
