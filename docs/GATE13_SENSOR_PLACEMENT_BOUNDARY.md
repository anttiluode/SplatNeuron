# Gate 13 prior-art boundary — sparse / task-aware sensor placement

Date: 2026-08-18

Status: **the local-geometry mechanism is established prior art.**

Gate 13 must not claim novelty if a learned local observation family uses fewer logical measurements than task-blind/random sensing when the task-relevant signal is spatially localized.

That phenomenon is directly adjacent to sparse sensor-placement literature.

## Sparse sensor placement for classification

**Brunton, Brunton, Proctor & Kutz, 2016 — Sparse Sensor Placement Optimization for Classification, SIAM Journal on Applied Mathematics 76(5):2099–2122.**

The paper asks how to choose a limited set of sensor locations that best inform a classification decision in a high-dimensional system. Its SSPOC method exploits low-dimensional structure and learns sparse sensor locations from data; the authors emphasize that when only classification is required, one can often use far fewer measurements than are needed for reconstruction.

- DOI: 10.1137/15M1036713
- Earlier arXiv version: 1310.4217, "Optimal Sensor Placement and Enhanced Sparsity for Classification"

The paper demonstrates learned sparse sensors on physical systems, image recognition and biological classification data.

Therefore the broad Gate-13 observation

> learn spatial measurements that are aligned with the task and use fewer measurements than generic sensing

is occupied.

## Data-driven sparse sensing versus universal/random sensing

**Manohar, Brunton, Kutz & Brunton, 2018 — Data-Driven Sparse Sensor Placement for Reconstruction.**

This work uses tailored data-derived features with SVD / QR-pivot sensor placement and explicitly contrasts optimized sensing that exploits known patterns with universal compressed sensing. It reports large reductions in required sensor count in examples including faces and fluid fields.

- arXiv: 1701.07569

This is conceptually close to Gate 13's `local` cell: a sensing family that can exploit known spatial organization should not be expected to need as many outputs as a task-blind isotropic random projection.

## Optimized sparse sampling of dynamical systems

**Manohar, Kaiser, Brunton & Kutz, 2019 — Optimized Sampling for Multiscale Dynamics, Multiscale Modeling & Simulation 17(1):117–136.**

Uses modal libraries and QR pivoting to select sparse sensor locations for reconstruction and dynamical-regime classification, again demonstrating accurate global inference from a small optimized sensor set.

- DOI: 10.1137/17M1162366

## Implication for Gate 13

If the frozen experiment produces

```text
local world:
    learned spatial observer reaches target with M=32
    random sensing needs M=48

dense world:
    learned spatial observer loses that advantage
```

that is a good mechanistic calibration of the instrument, but it is **not discovery of task-aware sparse sensing**.

The more defensible remaining measurement is:

```text
what task-specific description payload was required
    to specify the learned sensing geometry
versus
how much logical sensor/output width that geometry saved
```

Classical sparse sensor-placement work strongly centers **number and position of sensors** and task/reconstruction performance. Gate 13 additionally serializes the observation-policy parameters and separately records discovery cost and decoder state.

## Current narrow question

> **When an optimized sensing geometry can save sensors, what is the explicit description/search cost of specifying that geometry, and where does that cost sit on a Pareto frontier against fixed algorithmic/random sensing?**

This is a resource-accounting question built on top of established sensor-placement and task-based sensing results.

## Novelty warning

The targeted search has not established that this exact description-cost-versus-sensor-count ledger is absent from experimental-design, sensing-hardware or sensor-placement literature.

Before publication, search specifically for:

```text
sensor placement communication overhead
sensor configuration description length
sensor placement codebooks / index cost
optimal design with deployment/configuration cost
minimum-description-length experimental design
two-part coding sensor design
sensor-network topology coding / configuration bits
```

Absence from the current search is not evidence of novelty.
