# SplatNeuron

> **Use can shorten the path to evidence.**

SplatNeuron is a research program about **plastic observation geometry**: a computation can change where/how it observes a field during operation, and repeated useful observation routes may become cheaper through persistent geometry.

The repo began with a stronger structural-growth story. The first adversarial control cut that story down. That correction is now part of the project rather than hidden history.

## Current ledger

```text
Smoke 0    ROUTE / CONSOLIDATE plumbing                 works; WAIT null was constructed
Boundary0  nonzero-overlap WAIT <-> ROUTE crossover     implemented as quantitative boundary
Smoke 1    ROUTE -> GROW                                 growth loses to fixed plastic capacity
Gate 2     budgeted continuous ROUTE                    next architectural gate
```

No novelty, neuroscience, performance, or hardware claim is made.

## The live idea

A receiver is parameterized by continuous Gabor geometry:

```text
q = (x, y, sigma, frequency, orientation, phase)
```

and observes a common complex field by inner product with its localized template.

The key operational distinction is:

```text
WAIT   = spend more observations through the same map C
ROUTE  = change C
```

The plastic extension is:

```text
successful repeated ROUTE
        -> persistent receiver geometry
        -> lower future observation/search work
```

This is deliberately stronger than ordinary caching only if the geometry itself helps acquire/generalize routes. If a plain address table matches it, keep the table and kill the stronger story.

## Smoke 0 — useful mechanism, weak experiment

The original A/B targets were chosen at opposite corners/frequencies/orientations of a 300-Gabor bank.

The actual overlap is essentially zero:

```text
|Gram[home_A,target_B]| ~= 4e-14
```

Therefore 300 WAIT samples at A cannot recover B in expectation. The old WAIT failure was true by construction.

The script is kept as a smoke test because it still verifies:

```text
regime shift -> expensive ROUTE
repeated useful route -> receiver consolidation
stable regime -> cheap observation again
```

but it now prints:

```text
WAIT_VS_ROUTE_EVIDENCE_CLAIM = NOT_TESTED
```

See [`docs/GATE0_ROUTE_CONSOLIDATE.md`](docs/GATE0_ROUTE_CONSOLIDATE.md).

## Boundary 0 — where WAIT should beat ROUTE, and vice versa

The repaired experiment uses a continuous off-grid target whose overlap with the current receiver is **nonzero**.

Equal total observation budget:

```text
WAIT    8 observations at current receiver
ROUTE   3-unit acquisition tax + 5 observations at the better receiver
```

For equal Gaussian observation noise the analytic crossover is

```text
|c|* = sqrt((8-3)/8)
     = sqrt(5/8)
     ~= 0.790569
```

where

```text
c = <G(home), G(target)>
```

is measured from actual rendered complex Gabor templates.

So this experiment predicts **before Monte Carlo**:

```text
high current overlap -> WAIT wins
low current overlap  -> ROUTE wins
```

This is a resource boundary, not a universal ROUTE win.

The ROUTE arm is intentionally oracle here. It only establishes when acquiring another view *could* repay its cost. Gate 2 must earn that view without target access.

See [`docs/BOUNDARY0_WAIT_ROUTE.md`](docs/BOUNDARY0_WAIT_ROUTE.md).

## Smoke 1 — growth does not earn its keep

The first version compared a growing two-branch receiver against one moving anchor:

```text
route_only      acc 1.000   totalW 18060
single_anchor   acc 1.000   totalW  3095
grow            acc 1.000   totalW  1074
```

That made growth look valuable, but the single anchor cannot hold two views by construction.

The missing attacker is **fixed capacity with plasticity**: two anchors exist from the start, the second begins at a random bank geometry, both can consolidate, and growth is disabled.

Across 20 deterministic seeds the independently reproduced result is:

```text
grow       acc=1.000  totalW=1074.0   B first5=180.80  B last10=2.00
fixedcap   acc=1.000  totalW= 613.2   B first5= 88.31  B last10=2.00
```

Identical steady state, less transient work for fixed capacity.

The morphology break-even therefore flips sign:

```text
break-even vs single anchor   +2021
break-even vs fixed capacity   -461
```

So the repo now records:

```text
GROWTH_EARNS_KEEP = False
```

This reproduces the same negative shape already recorded independently in `anttiluode/WildIdea` W3/K2, where preallocated alternative charts plus targeted probing matched predictable chart growth.

The lesson is not “growth never matters.” It is narrower:

> **Do not credit growth for an effect explained by already having enough plastic capacity.**

See [`docs/GATE1_ROUTE_GROW.md`](docs/GATE1_ROUTE_GROW.md).

## Why Gabors are not allowed to be decoration

The current smoke tests still use a precomputed 300x300 Gram matrix, and interpolated receiver geometry is snapped back to the nearest bank index. In that form, geometry largely acts as a metric for ordering list search.

That is not enough.

The next gate must use **continuous receiver geometry directly**:

```text
receiver q
   -> render/evaluate G(q)
   -> true inner product with current field
```

No nearest-bank snap.

If arbitrary coordinates or a route cache perform the same job, the Gabor story dies.

## Gate 2 — budgeted continuous ROUTE

This is now the first experiment allowed to carry architectural weight.

Required task properties:

```text
continuous off-grid hidden emitter
strict <= 8 observations per episode
no hidden target coordinates
no exhaustive 300-view scan
useful destination drifts / recurs
```

Required arms from the start:

```text
random continuous routing
local finite-difference / hill climbing
learned active route policy
fixed-capacity plastic anchors
persistent consolidation
simple address/cache baseline
oracle route ceiling
```

The primary plot should be a **performance / observation-work frontier**, not a single accuracy number.

The claim to earn is:

> **Persistent plasticity of an observation map can amortize repeated active sensing under a strict observation budget in a way that is not explained by fixed capacity, a simple address cache, or standard active sampling.**

## When growth may return

Growth stays dead until the task contains more recurring useful views than a matched fixed-capacity system can hold.

Then, with `K` receiver slots and `M >> K` recurring useful views, structural birth/death becomes a real allocation problem:

```text
which view deserves a slot?
which old view should be replaced?
when does a new branch repay its cost?
what should prune?
```

Only such a world can let growth buy something preallocation cannot.

## Prior art / attackers

Strong neighboring ideas already include:

- recurrent visual attention / learned glimpses;
- spatial transformers;
- deformable convolution / input-dependent sampling;
- differentiable lifetime plasticity;
- learned routing and sparse retrieval;
- reservoir/liquid-state readouts;
- simple caches of previously useful routes.

See [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md).

## Run

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python experiments/gate0_route_consolidate.py
python experiments/boundary0_wait_route_crossover.py
python experiments/gate1_route_grow.py
```

Requires Python 3.10+ and NumPy.

See [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md) for the live stopping lines and next experiment.
