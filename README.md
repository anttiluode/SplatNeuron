# SplatNeuron

> **Use can shorten the path to evidence — but only when changing the receiver is worth paying for.**

SplatNeuron is a research program about **plastic observation geometry**: a computation can change where/how it observes a field during operation, and repeated useful observation routes may become persistent receiver geometry.

The repo began with a stronger dendritic-growth story. Strong boring controls have repeatedly cut that story down. Those negatives are part of the result.

## Current ledger

```text
Smoke 0    ROUTE / CONSOLIDATE plumbing                 works; WAIT null was constructed
Boundary0  nonzero-overlap WAIT <-> oracle ROUTE        quantitative SNR/cost crossover
Smoke 1    ROUTE -> GROW                                growth loses to fixed plastic capacity
Gate 2     continuous off-grid ROUTE                    fails to separate from address cache
Boundary1  cache <-> ROUTE vs environmental drift       sign change measured
```

No novelty, neuroscience, performance, or hardware claim is made.

## The live object

A receiver is a continuous four-dimensional coordinate

```text
u = (x, y, log-frequency, orientation)
```

mapped to a localized complex Gabor template `G(u)`.

A receiver observes the current field through

```text
z = <G(u), X>
```

The core runtime distinction is:

```text
WAIT   = spend more observations through the same receiver
ROUTE  = spend observations changing the receiver
```

The plastic extension is:

```text
successful ROUTE
    -> persist an improved receiver address
    -> lower future route cost if the relationship recurs
```

Growth is currently **not** part of the surviving claim.

## Smoke 0 — useful plumbing, invalid WAIT receipt

The first A/B bank targets had essentially zero overlap:

```text
|Gram[home_A,target_B]| ~= 4e-14
```

So repeating the A receiver could never recover B in expectation. That experiment is retained only as a smoke test for routing, consolidation, regime-shift search spikes, and relearning.

The script explicitly prints:

```text
WAIT_VS_ROUTE_EVIDENCE_CLAIM = NOT_TESTED
```

See [`docs/GATE0_ROUTE_CONSOLIDATE.md`](docs/GATE0_ROUTE_CONSOLIDATE.md).

## Boundary 0 — when another view could repay its cost

The repaired WAIT/ROUTE experiment gives the current receiver nonzero overlap with an off-grid target.

Equal total observation budget:

```text
WAIT    8 observations at the current receiver
ROUTE   pay 3 units to acquire a better view + 5 observations there
```

For equal Gaussian observation noise the predicted crossover is

```text
|c|* = sqrt(5/8) ~= 0.790569
```

where `c=<G(home),G(target)>` is the actual rendered complex Gabor overlap.

So:

```text
high current overlap -> WAIT
low current overlap  -> ROUTE can repay the acquisition tax
```

The ROUTE arm is oracle in Boundary 0. It establishes a resource boundary, not an active-routing win.

See [`docs/BOUNDARY0_WAIT_ROUTE.md`](docs/BOUNDARY0_WAIT_ROUTE.md).

## Smoke 1 — growth loses to fixed plastic capacity

The original growth result compared a two-branch growing system against one moving receiver and looked strong. The missing attacker began with **two plastic receiver anchors from the start**, second anchor random, growth disabled.

Across 20 deterministic seeds:

```text
grow       acc=1.000  totalW=1074.0
fixedcap   acc=1.000  totalW= 613.2
```

Both end with the same steady-state work (`1/2/1/2` observations across the recurring A/B blocks). Growth merely pays three expensive global searches before its second branch crystallizes.

The fair morphology value therefore flips sign:

```text
vs single anchor    +2021 observation units
vs fixed capacity    -461 observation units
```

The repo now records:

```text
GROWTH_EARNS_KEEP = False
```

This independently reproduces the same negative shape recorded in `anttiluode/WildIdea` W3/K2: preallocated alternatives plus probing matched or beat manufacturing new alternatives online.

See [`docs/GATE1_ROUTE_GROW.md`](docs/GATE1_ROUTE_GROW.md).

## Gate 2 — the actual continuous rewrite

Gate 2 removes the bank/address-table escape hatch.

Every query directly renders `G(u)` and takes a true inner product against a rendered field. There is:

```text
no 300 x 300 Gram lookup
no nearest-bank snap
no target coordinate available to the policy
no exhaustive search
```

The two hidden source views drift continuously in `x`, `y`, frequency, and orientation. All structured policies have the same fixed receiver capacity `K=2` and the same exact budget of **8 observations per episode**.

Policies:

```text
address_cache    fixed two-address capacity, probe then WAIT
hybrid_plastic   WAIT if current evidence is strong;
                 otherwise local SPSA ROUTE and persist an improvement
hybrid_reset     same router, but reset receiver geometry every episode
always_route     same plastic capacity, but ROUTE every episode
random           eight random continuous queries
oracle           query the hidden target coordinate
```

Development used seeds `0..19`, `1000..1019`, and `2000..2019`. The untouched confirmation was `3000..3019`.

Confirmation:

```text
policy               acc   overlap   lateAcc   lateOv   route%  work
---------------------------------------------------------------------
address_cache       0.656    0.682     0.622    0.583     0.0%   8.0
hybrid_plastic      0.674    0.691     0.661    0.644    41.2%   8.0
hybrid_reset        0.644    0.660     0.604    0.575    46.3%   8.0
always_route        0.569    0.589     0.566    0.583   100.0%   8.0
random              0.507    0.153     0.500    0.148     0.0%   8.0
oracle              1.000    1.000     1.000    1.000     0.0%   8.0
```

Primary score is receiver-target overlap, evaluated only after the policy acts.

Critical paired contrasts over late-block seed means:

```text
hybrid_plastic - address_cache   +0.061  CI [-0.005, +0.124]  NOT SEPARATED
hybrid_plastic - hybrid_reset    +0.068  CI [+0.009, +0.126]  survives
hybrid_plastic - always_route    +0.061  CI [+0.007, +0.107]  survives
```

So Gate 2 **fails the strongest baseline**.

What survives is narrower:

- persistent receiver geometry helped relative to running the same router from reset geometry;
- admission mattered: routing only when evidence was weak beat routing constantly;
- the fixed two-address cache remained statistically viable;
- task-accuracy superiority over cache/reset was not established.

See [`docs/GATE2_CONTINUOUS_ROUTE.md`](docs/GATE2_CONTINUOUS_ROUTE.md).

## Boundary 1 — cache versus ROUTE changes sign

Instead of tuning Gate 2's drift until ROUTE wins, Boundary 1 sweeps environmental motion while holding capacity, budget, router, admission rule, and field fixed.

Late receiver-target overlap:

```text
 scale   cacheOv   routeOv     delta      95% CI
------------------------------------------------------
  0.00     0.999     0.831    -0.168   [-0.211,-0.124]
  0.25     0.961     0.753    -0.209   [-0.254,-0.162]
  0.50     0.862     0.752    -0.110   [-0.165,-0.057]
  0.75     0.707     0.603    -0.104   [-0.245,+0.022]
  1.00     0.551     0.650    +0.099   [+0.029,+0.172]
  1.50     0.340     0.561    +0.221   [+0.115,+0.324]
  2.00     0.232     0.477    +0.244   [+0.154,+0.333]
  3.00     0.135     0.323    +0.188   [+0.089,+0.293]
  4.00     0.090     0.266    +0.175   [+0.130,+0.222]
```

At low motion, ROUTE is actively harmful: noisy admission triggers unnecessary receiver movement. As the world moves faster, stale addresses lose observability and the sign flips around the `0.75 -> 1.0` drift-scale region.

The supported statement is therefore not "plastic geometry wins":

> **Receiver motion has a value region. If the current observation map remains aligned with the world, leave it alone. Once environmental change makes that map stale enough, paying to ROUTE becomes worthwhile.**

See [`docs/BOUNDARY1_CACHE_ROUTE_PHASE.md`](docs/BOUNDARY1_CACHE_ROUTE_PHASE.md).

## What Gabors have and have not earned

Gate 2 now genuinely uses continuous rendered Gabor geometry; it is no longer decorative list ordering.

But that does **not** establish that Gabors themselves are special. The current local SPSA router only needs a navigable response surface. A generic continuous sensor geometry may behave similarly.

So the next attacker is not another prettier splat visualization. It is to ask whether the admission/route policy can estimate **expected value of changing the observation map** from observable evidence and generalize to fresh drift/noise regimes.

If arbitrary continuous coordinates plus the same policy match the result, keep the generic active-sensing result and drop the Gabor-specific story.

## When growth may return

Growth remains dead until the world contains more distinct recurring useful views than matched fixed capacity can hold:

```text
K fixed receiver slots
M recurring useful views, M >> K
```

Only then does birth/death become a real allocation problem rather than a slower way of obtaining capacity that could have existed from the start.

## Run

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python experiments/gate0_route_consolidate.py
python experiments/boundary0_wait_route_crossover.py
python experiments/gate1_route_grow.py
python experiments/gate2_continuous_route.py
python experiments/boundary1_cache_route_phase.py
```

Requires Python 3.10+ and NumPy.

See [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md) for the live stopping lines.
