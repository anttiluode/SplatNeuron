from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class SplatGeometry:
    """Geometry of one localized complex Gabor receiver/emitter.

    x/y/sigma are fractions of image width/height. freq is cycles per image.
    theta and phase are radians.
    """

    x: float
    y: float
    sigma: float
    freq: float
    theta: float
    phase: float = 0.0


def _angle_distance(a: float, b: float) -> float:
    """Orientation distance for pi-periodic Gabors."""
    d = (a - b + np.pi / 2.0) % np.pi - np.pi / 2.0
    return float(abs(d))


def geometry_distance(a: SplatGeometry, b: SplatGeometry) -> float:
    """Dimensionless routing distance over position/frequency/orientation/scale."""
    dx = (a.x - b.x) / 0.25
    dy = (a.y - b.y) / 0.25
    df = np.log(max(a.freq, 1e-6) / max(b.freq, 1e-6)) / np.log(2.0)
    dt = _angle_distance(a.theta, b.theta) / (np.pi / 4.0)
    ds = np.log(max(a.sigma, 1e-6) / max(b.sigma, 1e-6)) / np.log(2.0)
    return float(np.sqrt(dx * dx + dy * dy + df * df + dt * dt + ds * ds))


def interpolate_geometry(a: SplatGeometry, b: SplatGeometry, rate: float) -> SplatGeometry:
    """Move receiver geometry toward b while respecting orientation periodicity."""
    r = float(np.clip(rate, 0.0, 1.0))
    dtheta = (b.theta - a.theta + np.pi / 2.0) % np.pi - np.pi / 2.0
    return SplatGeometry(
        x=(1.0 - r) * a.x + r * b.x,
        y=(1.0 - r) * a.y + r * b.y,
        sigma=float(np.exp((1.0 - r) * np.log(a.sigma) + r * np.log(b.sigma))),
        freq=float(np.exp((1.0 - r) * np.log(a.freq) + r * np.log(b.freq))),
        theta=float((a.theta + r * dtheta) % np.pi),
        phase=float(np.angle((1.0 - r) * np.exp(1j * a.phase) + r * np.exp(1j * b.phase))),
    )


def complex_gabor(geom: SplatGeometry, size: int = 24) -> np.ndarray:
    """Return an L2-normalized localized complex Gabor atom."""
    yy, xx = np.mgrid[0:size, 0:size]
    x = (xx + 0.5) / size
    y = (yy + 0.5) / size
    dx = x - geom.x
    dy = y - geom.y
    c = np.cos(geom.theta)
    s = np.sin(geom.theta)
    xr = c * dx + s * dy
    yr = -s * dx + c * dy
    env = np.exp(-0.5 * (xr * xr + yr * yr) / (geom.sigma * geom.sigma))
    carrier = np.exp(1j * (2.0 * np.pi * geom.freq * xr + geom.phase))
    atom = (env * carrier).astype(np.complex128).reshape(-1)
    norm = np.linalg.norm(atom)
    if norm <= 0:
        raise ValueError("degenerate Gabor atom")
    return atom / norm


def make_default_bank(size: int = 24) -> tuple[list[SplatGeometry], np.ndarray, np.ndarray]:
    """Create a modest multi-position/frequency/orientation Gabor receiver bank.

    Returns (geometries, template_matrix, complex Gram matrix), where templates
    has shape [N, pixels] and Gram[j, i] is receiver j's response to emitter i.
    """
    positions = np.linspace(0.14, 0.86, 5)
    freqs = (2.0, 4.0, 8.0)
    thetas = (0.0, np.pi / 4.0, np.pi / 2.0, 3.0 * np.pi / 4.0)
    geoms: list[SplatGeometry] = []
    for y in positions:
        for x in positions:
            for freq in freqs:
                for theta in thetas:
                    geoms.append(SplatGeometry(float(x), float(y), 0.105, freq, float(theta), 0.0))
    templates = np.stack([complex_gabor(g, size=size) for g in geoms], axis=0)
    gram = templates.conj() @ templates.T
    return geoms, templates, gram


class SplatWorld:
    """Synthetic common field assembled from bank atoms.

    This is intentionally inspectable: one strong task atom plus weak distractor
    atoms. A receiver only observes its complex inner product with the field.
    """

    def __init__(
        self,
        gram: np.ndarray,
        target_index: int,
        rng: np.random.Generator,
        *,
        distractors: int = 10,
        distractor_sd: float = 0.045,
        noise_sd: float = 0.03,
    ) -> None:
        self.gram = np.asarray(gram)
        self.target_index = int(target_index)
        self.rng = rng
        self.distractors = int(distractors)
        self.distractor_sd = float(distractor_sd)
        self.noise_sd = float(noise_sd)

    def episode(self, label: int) -> "FieldEpisode":
        n = self.gram.shape[0]
        pool = np.delete(np.arange(n), self.target_index)
        idx = self.rng.choice(pool, size=self.distractors, replace=False)
        amps = self.rng.normal(0.0, self.distractor_sd, size=self.distractors)
        base = self.gram[:, self.target_index] * float(label)
        base = base + self.gram[:, idx] @ amps
        return FieldEpisode(base_response=base, rng=self.rng, noise_sd=self.noise_sd, label=int(label))


@dataclass
class FieldEpisode:
    base_response: np.ndarray
    rng: np.random.Generator
    noise_sd: float
    label: int

    def sample(self, receiver_index: int) -> complex:
        noise = self.rng.normal(0.0, self.noise_sd) + 1j * self.rng.normal(0.0, self.noise_sd)
        return complex(self.base_response[int(receiver_index)] + noise)


@dataclass
class ObservationResult:
    prediction: int
    work: int
    receiver_index: int
    response: complex


def classify_response(z: complex) -> int:
    return 1 if float(np.real(z)) >= 0.0 else -1


def wait_same_receiver(episode: FieldEpisode, receiver_index: int, repeats: int) -> ObservationResult:
    """WAIT: spend more samples without changing the observation map."""
    vals = np.asarray([episode.sample(receiver_index) for _ in range(int(repeats))])
    z = complex(vals.mean())
    return ObservationResult(classify_response(z), int(repeats), int(receiver_index), z)


def route_receiver(
    episode: FieldEpisode,
    geoms: list[SplatGeometry],
    anchor: SplatGeometry,
    *,
    threshold: float = 0.72,
) -> ObservationResult:
    """ROUTE: search receiver geometries nearest-first until evidence is strong.

    Search work is fully charged as one receiver observation per visited geometry.
    """
    order = sorted(range(len(geoms)), key=lambda i: geometry_distance(anchor, geoms[i]))
    last_i = order[-1]
    last_z = 0j
    for work, i in enumerate(order, start=1):
        z = episode.sample(i)
        last_i, last_z = i, z
        if abs(z) >= threshold:
            return ObservationResult(classify_response(z), work, i, z)
    return ObservationResult(classify_response(last_z), len(order), last_i, last_z)


class ReceiverAnchor:
    """Persistent receiver geometry changed by repeated useful routes.

    This is the smallest 'use shortens the path' rule: a successful/high-evidence
    route pulls the home receiver toward the geometry that produced the admitted
    consequence. No gradient descent updates the anchor during the experiment.
    """

    def __init__(self, geometry: SplatGeometry, plasticity_rate: float = 0.28) -> None:
        self.geometry = geometry
        self.plasticity_rate = float(plasticity_rate)

    def consolidate(self, destination: SplatGeometry, evidence: float, threshold: float = 0.72) -> None:
        if float(evidence) < float(threshold):
            return
        self.geometry = interpolate_geometry(self.geometry, destination, self.plasticity_rate)


def nearest_geometry_index(geoms: Iterable[SplatGeometry], query: SplatGeometry) -> int:
    geoms_list = list(geoms)
    return min(range(len(geoms_list)), key=lambda i: geometry_distance(query, geoms_list[i]))


class BranchingReceiver:
    """Persistent set of receiver anchors with use-dependent branch growth.

    Existing branches are checked cheaply first. If none produces admitted
    evidence, the receiver pays for a global ROUTE. Repeated successful routes to
    a destination far from all existing branches can crystallize a new branch.
    """

    def __init__(
        self,
        initial: SplatGeometry,
        *,
        max_branches: int = 4,
        growth_patience: int = 3,
        far_threshold: float = 2.0,
        cluster_threshold: float = 0.9,
    ) -> None:
        self.branches = [initial]
        self.max_branches = int(max_branches)
        self.growth_patience = int(growth_patience)
        self.far_threshold = float(far_threshold)
        self.cluster_threshold = float(cluster_threshold)
        self._candidate: SplatGeometry | None = None
        self._candidate_hits = 0
        self.growth_events = 0

    def _nearest_branch_distance(self, geom: SplatGeometry) -> float:
        return min(geometry_distance(b, geom) for b in self.branches)

    def _record_route(self, destination: SplatGeometry, evidence: float, threshold: float) -> bool:
        if evidence < threshold or len(self.branches) >= self.max_branches:
            return False
        if self._nearest_branch_distance(destination) < self.far_threshold:
            self._candidate = None
            self._candidate_hits = 0
            return False

        if self._candidate is not None and geometry_distance(self._candidate, destination) <= self.cluster_threshold:
            self._candidate_hits += 1
            self._candidate = interpolate_geometry(self._candidate, destination, 1.0 / self._candidate_hits)
        else:
            self._candidate = destination
            self._candidate_hits = 1

        if self._candidate_hits >= self.growth_patience:
            self.branches.append(self._candidate)
            self.growth_events += 1
            self._candidate = None
            self._candidate_hits = 0
            return True
        return False

    def observe(
        self,
        episode: FieldEpisode,
        geoms: list[SplatGeometry],
        *,
        threshold: float = 0.72,
    ) -> tuple[ObservationResult, bool]:
        """Observe with branches first, then route globally if necessary.

        Returns (result, grew_branch_now).
        """
        probed: set[int] = set()
        work = 0
        for branch in self.branches:
            i = nearest_geometry_index(geoms, branch)
            if i in probed:
                continue
            probed.add(i)
            work += 1
            z = episode.sample(i)
            if abs(z) >= threshold:
                return ObservationResult(classify_response(z), work, i, z), False

        remaining = [i for i in range(len(geoms)) if i not in probed]
        remaining.sort(key=lambda i: min(geometry_distance(b, geoms[i]) for b in self.branches))
        last_i = remaining[-1]
        last_z = 0j
        for i in remaining:
            work += 1
            z = episode.sample(i)
            last_i, last_z = i, z
            if abs(z) >= threshold:
                grew = self._record_route(geoms[i], abs(z), threshold)
                return ObservationResult(classify_response(z), work, i, z), grew
        return ObservationResult(classify_response(last_z), work, last_i, last_z), False
