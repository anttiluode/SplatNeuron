# Boundary 0 — WAIT versus ROUTE with nonzero overlap

Date: 2026-08-17

Status: **quantitative boundary instrument. ROUTE is oracle and therefore not yet an algorithmic win.**

## Why this exists

Smoke 0 placed the A and B Gabors at essentially zero overlap, so WAIT was guaranteed to fail by construction.

This replacement asks the real resource question:

> When the current receiver carries a weak but nonzero version of the task signal, when is it cheaper to keep sampling there, and when is it worth paying to acquire a better view?

## Continuous geometry

The home receiver is a rendered normalized complex Gabor:

```text
x=.40, y=.50, sigma=.12, frequency=4, orientation=0
```

The hidden target slides continuously in x. It is not snapped to the 300-element bank.

For each target geometry the experiment renders both templates and computes the actual complex inner product

```text
c = <G(home), G(target)>
```

Every tested target has nonzero overlap with home.

The classifier projects the complex response onto the calibrated signal direction, so the relevant scalar signal magnitude is `|c|`; phase rotation from translation is not allowed to masquerade as lost information.

## Equal total observation budget

```text
total budget B = 8 observation units
```

WAIT spends all eight observations at home and averages them.

The ROUTE arm is deliberately an **oracle lower bound**. It pays a declared acquisition tax of three units and then receives only five observations at the true target geometry:

```text
WAIT:   8 samples at overlap |c|
ROUTE:  3 route-cost units + 5 samples at overlap 1
```

Signal amplitude and noise are identical across arms.

## Predicted crossover

For Gaussian measurement noise, both arms have the same classification SNR at

```text
|c| * sqrt(B) = sqrt(B - route_tax)
```

therefore

```text
|c|* = sqrt((8 - 3) / 8)
     = sqrt(5/8)
     ~= 0.790569
```

This is the boundary before running Monte Carlo.

The rendered Gabor geometry crosses that overlap at approximately `dx ~= .12` for the chosen scale/frequency.

So the preregistered shape is:

```text
small displacement / high overlap    -> WAIT wins
larger displacement / low overlap    -> ROUTE wins
```

Neither policy dominates globally.

## What is measured

`experiments/boundary0_wait_route_crossover.py` sweeps continuous offsets from `0.00` to `0.20`, renders the target Gabor at each offset, and compares Monte Carlo accuracy with the Gaussian prediction.

The automated checks require:

- all target overlaps remain positive;
- WAIT wins clearly near home;
- ROUTE wins clearly farther away;
- empirical accuracies agree with the analytic noise model;
- an empirical sign change is found near the predicted overlap crossover.

## Supported statement

If the checks pass, the supported claim is only:

> **For a receiver with nonzero task sensitivity, replication and receiver change occupy different sides of a measurable SNR/cost boundary.**

This repairs the logical weakness of Smoke 0. It does **not** show that a real router can discover the better continuous view within the route tax.

## What remains hard

The next real gate must remove the oracle:

```text
continuous off-grid target
<= 8 total samples
no target coordinates
no exhaustive bank scan
```

A routing policy must infer where to look next from observations it has already paid for.

Matched attackers must include:

- random continuous routing;
- local finite-difference / hill-climbing;
- a learned active-attention policy;
- fixed-capacity plastic receiver anchors;
- a simple route/address cache;
- an oracle route ceiling.

Only that experiment can tell us whether **geometry-guided route acquisition** earns something beyond a cache or a standard active sensor.
