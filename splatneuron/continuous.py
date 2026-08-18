"""Continuous off-grid observation geometry for SplatNeuron.

Unlike the smoke-test bank in :mod:`splatneuron.core`, this module never snaps a
receiver to a precomputed bank index. A query coordinate is rendered directly
as a complex Gabor receiver and dotted with the current rendered field.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .core import SplatGeometry, complex_gabor


@dataclass(frozen=True)
class ContinuousDomain:
    """Normalized four-dimensional receiver domain.

    Coordinates are ``u=(x, y, log_frequency, orientation)``. ``x`` and ``y``
    are image fractions, log-frequency runs from 2 to 8 cycles/image, and
    orientation is pi-periodic. Sigma is held fixed in Gate 2 so that all four
    routed dimensions have an interpretable bounded range.
    """

    x_min: float = 0.12
    x_max: float = 0.88
    y_min: float = 0.12
    y_max: float = 0.88
    freq_min: float = 2.0
    freq_max: float = 8.0
    sigma: float = 0.13

    def clip(self, u: Iterable[float]) -> np.ndarray:
        q = np.asarray(tuple(u), dtype=float).copy()
        if q.shape != (4,):
            raise ValueError("continuous receiver coordinate must have shape (4,)")
        q[0] = np.clip(q[0], self.x_min, self.x_max)
        q[1] = np.clip(q[1], self.y_min, self.y_max)
        q[2] = np.clip(q[2], 0.0, 1.0)
        q[3] = q[3] % 1.0
        return q

    def geometry(self, u: Iterable[float]) -> SplatGeometry:
        q = self.clip(u)
        ratio = self.freq_max / self.freq_min
        freq = self.freq_min * ratio ** float(q[2])
        return SplatGeometry(
            x=float(q[0]),
            y=float(q[1]),
            sigma=float(self.sigma),
            freq=float(freq),
            theta=float(np.pi * q[3]),
            phase=0.0,
        )


@dataclass
class ContinuousObservation:
    response: complex
    coordinate: np.ndarray
    work: int
    action: str
    anchor_index: int | None

    @property
    def prediction(self) -> int:
        return 1 if float(np.real(self.response)) >= 0.0 else -1


class ContinuousFieldEpisode:
    """Rendered continuous field with no receiver bank or nearest-index snap.

    Policies may call :meth:`sample`; :meth:`true_overlap` is evaluation-only
    and deliberately exposes hidden target geometry only to experiment scoring.
    """

    def __init__(
        self,
        target: Iterable[float],
        label: int,
        rng: np.random.Generator,
        *,
        domain: ContinuousDomain | None = None,
        size: int = 20,
        noise_sd: float = 0.18,
        distractors: int = 2,
        distractor_sd: float = 0.08,
    ) -> None:
        self.domain = domain or ContinuousDomain()
        self.target = self.domain.clip(target)
        self.label = int(label)
        self.rng = rng
        self.size = int(size)
        self.noise_sd = float(noise_sd)
        self.observations = 0
        self._template_cache: dict[tuple[float, ...], np.ndarray] = {}

        self._target_template = complex_gabor(self.domain.geometry(self.target), self.size)
        field = float(self.label) * self._target_template.copy()
        for _ in range(int(distractors)):
            q = np.array(
                [
                    rng.uniform(self.domain.x_min, self.domain.x_max),
                    rng.uniform(self.domain.y_min, self.domain.y_max),
                    rng.random(),
                    rng.random(),
                ],
                dtype=float,
            )
            amp = rng.normal(0.0, float(distractor_sd))
            field += amp * complex_gabor(self.domain.geometry(q), self.size)
        self.field = field

    def _template(self, coordinate: Iterable[float]) -> np.ndarray:
        q = self.domain.clip(coordinate)
        key = tuple(float(v) for v in np.round(q, 9))
        tpl = self._template_cache.get(key)
        if tpl is None:
            tpl = complex_gabor(self.domain.geometry(q), self.size)
            self._template_cache[key] = tpl
        return tpl

    def sample(self, coordinate: Iterable[float]) -> complex:
        q = self.domain.clip(coordinate)
        z = np.vdot(self._template(q), self.field)
        noise = self.rng.normal(0.0, self.noise_sd) + 1j * self.rng.normal(0.0, self.noise_sd)
        self.observations += 1
        return complex(z + noise)

    def true_overlap(self, coordinate: Iterable[float]) -> float:
        """Evaluation-only task sensitivity of a receiver to the hidden target."""
        return float(abs(np.vdot(self._template(coordinate), self._target_template)))


class FixedCapacityTracker:
    """K preallocated plastic receiver anchors; no growth.

    Gate 2 uses ``K=2`` throughout. The policy first probes all existing anchors.
    ``mode='cache'`` spends the remaining budget at the strongest current address.
    ``mode='hybrid'`` does the same if admitted evidence is already strong; if it
    is weak, it spends the remaining budget on a two-point SPSA route in continuous
    receiver coordinates. ``mode='always_route'`` performs that route even when
    an existing view is already good.

    When ``plastic=True``, an improved routed destination replaces only the
    selected anchor. Capacity is fixed; no branch is created.
    """

    def __init__(
        self,
        anchors: Iterable[Iterable[float]],
        *,
        domain: ContinuousDomain | None = None,
        admission_threshold: float = 0.72,
        route_step: float = 0.18,
        probe_radius: float = 0.07,
    ) -> None:
        self.domain = domain or ContinuousDomain()
        self.anchors = [self.domain.clip(a) for a in anchors]
        if not self.anchors:
            raise ValueError("at least one receiver anchor is required")
        self.admission_threshold = float(admission_threshold)
        self.route_step = float(route_step)
        self.probe_radius = float(probe_radius)

    def copy(self) -> "FixedCapacityTracker":
        return FixedCapacityTracker(
            [a.copy() for a in self.anchors],
            domain=self.domain,
            admission_threshold=self.admission_threshold,
            route_step=self.route_step,
            probe_radius=self.probe_radius,
        )

    def observe(
        self,
        episode: ContinuousFieldEpisode,
        *,
        budget: int = 8,
        mode: str = "hybrid",
        plastic: bool = True,
    ) -> ContinuousObservation:
        if mode not in {"cache", "hybrid", "always_route"}:
            raise ValueError(f"unknown mode: {mode}")
        k = len(self.anchors)
        if budget < k + 2:
            raise ValueError("budget must cover anchor probes plus a final estimate")

        start_work = episode.observations
        initial = [episode.sample(a) for a in self.anchors]
        anchor_index = int(np.argmax(np.abs(initial)))
        q = self.anchors[anchor_index].copy()
        z0 = initial[anchor_index]

        should_wait = mode == "cache" or (
            mode == "hybrid" and abs(z0) >= self.admission_threshold
        )
        if should_wait:
            remaining = budget - (episode.observations - start_work)
            vals = [z0] + [episode.sample(q) for _ in range(remaining)]
            z = complex(np.mean(vals))
            return ContinuousObservation(
                response=z,
                coordinate=q,
                work=episode.observations - start_work,
                action="WAIT",
                anchor_index=anchor_index,
            )

        # Reserve two observations for the final estimate. Every SPSA iteration
        # costs exactly two observations regardless of dimensionality.
        available = budget - (episode.observations - start_work) - 2
        iterations = max(0, available // 2)
        for it in range(iterations):
            delta = episode.rng.choice([-1.0, 1.0], size=4)
            radius = self.probe_radius * (0.8**it)
            q_plus = self.domain.clip(q + radius * delta)
            q_minus = self.domain.clip(q - radius * delta)
            y_plus = abs(episode.sample(q_plus)) ** 2
            y_minus = abs(episode.sample(q_minus)) ** 2
            grad = ((y_plus - y_minus) / (2.0 * radius)) * delta
            norm = float(np.linalg.norm(grad))
            if norm > 1e-12:
                grad /= norm
            q = self.domain.clip(q + self.route_step * (0.8**it) * grad)

        remaining = budget - (episode.observations - start_work)
        final_values = [episode.sample(q) for _ in range(remaining)]
        z = complex(np.mean(final_values))
        if plastic and abs(z) > abs(z0):
            self.anchors[anchor_index] = q.copy()

        return ContinuousObservation(
            response=z,
            coordinate=q,
            work=episode.observations - start_work,
            action="ROUTE",
            anchor_index=anchor_index,
        )
