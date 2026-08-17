# SplatNeuron — current handoff

Date: 2026-08-17

## One-line thesis still alive

> **Repeated useful computation may shorten its future observation path by changing persistent receiver geometry.**

The word **may** is now important. The first two experiments were too favorable to support the stronger version.

## Current scientific state

```text
Smoke 0   WAIT / ROUTE / CONSOLIDATE plumbing          works, not a receipt
Boundary0 WAIT <-> ROUTE nonzero-overlap crossover     implemented; quantitative boundary
Smoke 1   ROUTE -> GROW                                growth loses to fixed plastic capacity
Gate 2    budgeted continuous ROUTE                    next real gate
```

## Smoke 0 — demoted

The original A/B receiver overlap is approximately machine zero:

```text
|Gram[home_A, target_B]| ~= 4e-14
```

Therefore WAIT's chance performance after 300 repeats was built into the geometry. The script now reports:

```text
SMOKE0_PASS = ...
WAIT_VS_ROUTE_EVIDENCE_CLAIM = NOT_TESTED
```

Keep it only as a mechanism test for ROUTE, receiver consolidation, regime-shift search spikes, and relearning.

## Boundary 0 — the repaired WAIT/ROUTE question

`experiments/boundary0_wait_route_crossover.py` uses continuous off-grid target geometry and **nonzero** home overlap.

Equal total budget:

```text
WAIT    8 observations at current receiver
ROUTE   pay 3 observation units to acquire a better view,
        then only 5 observations at that view
```

For Gaussian observation noise, the predicted crossover is

```text
|c|* = sqrt((8-3)/8) = sqrt(5/8) ~= 0.790569
```

where `c=<G(home),G(target)>` is the actual rendered complex Gabor overlap.

Near home, WAIT should win because it keeps all eight samples. Farther away, ROUTE should win because the better observation map repays the acquisition tax.

Important limitation: ROUTE is oracle in this boundary instrument. Gate 2 must discover the view without target coordinates.

## Smoke 1 — growth fails the missing fixed-capacity arm

The original comparison made growth look valuable:

```text
route_only      totalW 18060
single_anchor   totalW  3095
grow            totalW  1074
```

But `single_anchor` was a straw capacity baseline: it cannot hold two views by construction.

The corrected arm starts with **two plastic anchors**, the second at a random bank geometry, and disables growth. Same task, same fallback ROUTE, no oracle B location.

Across 20 seeds (independently reproduced before being committed):

```text
grow       acc=1.000  totalW=1074.0   B first5=180.80  B last10=2.00
fixedcap   acc=1.000  totalW= 613.2   B first5= 88.31  B last10=2.00
```

The fair break-even therefore inverts:

```text
(613.2 - 1074.0) / 1 ~= -461 observation units
```

So:

```text
GROWTH_EARNS_KEEP = False
```

Do not tune `growth_patience` to rescue it.

## Cross-repo negative

This matches the boundary already recorded in `anttiluode/WildIdea` W3/K2: preallocated alternative charts plus targeted probing matched predictable chart growth. The common lesson is now replicated in two different toy media:

> **Having useful alternative capacity can matter while manufacturing that capacity online earns nothing.**

That makes growth a later question, not the spine of SplatNeuron.

## What survives

The smaller live object is:

```text
plastic observation geometry
        +
active ROUTE
        +
use-dependent consolidation / route amortization
        +
explicit observation cost
```

This is still heavily attacked by active attention, deformable sampling, spatial transformers, differentiable plasticity, and simple address caches.

## Gate 2 — budgeted continuous ROUTE

This is now the first experiment allowed to carry architectural weight.

Required properties:

```text
continuous off-grid hidden emitter
receiver sampled by actual rendered inner product
strict <= 8 observations per episode
no hidden target coordinates
no exhaustive 300-item scan
no snapping continuous q back to a bank index
```

Required arms from the beginning:

```text
random continuous route
local finite-difference / hill-climb route
learned active route policy
fixed-capacity plastic anchors              <- mandatory after Smoke 1
persistent consolidation
simple address/cache baseline
oracle route ceiling
```

The useful question is not merely accuracy. Measure both task performance and observation work as the target drifts or regimes recur.

## Growth reopening condition

Growth remains dead until the world contains **more distinct recurring useful views than matched fixed capacity can hold**.

Example future attack:

```text
K fixed receiver slots
M recurring useful views, M >> K
```

Then the question becomes allocation:

```text
what should be retained?
what should be replaced?
when is a new branch worth its cost?
what should prune?
```

Only there can growth buy something fixed capacity cannot buy by preallocation.

## Engineering note

Gate 2 is a real rewrite. Gates 0/1 index a precomputed 300x300 Gram matrix and snap interpolated geometry back to a bank address. Gate 2 must evaluate continuous receiver geometry directly against a rendered field or an equivalent exact continuous inner product. Geometry has to do algebraic work, not just order a list search.

## Stop lines

- If a route/address cache matches continuous plastic geometry at lower cost, keep the cache and demote the neuron story.
- If fixed-capacity plastic receivers match growth whenever capacity is controlled, keep growth dead.
- If continuous geometry provides no useful directional/generalization structure beyond arbitrary coordinates, Gabors are decoration.
- Do not add private recurrent state or write-back until ROUTE itself earns something under these attackers.
