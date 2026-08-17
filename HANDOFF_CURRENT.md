# SplatNeuron — current handoff

Date: 2026-08-17

## One-line thesis still alive

> **Changing the observation map has a measurable value region, but increasingly intelligent online admission rules have not yet beaten strong boring fixed policies.**

The project is now much smaller than the morning's growth story.

## Current ledger

```text
Smoke 0    WAIT / ROUTE / CONSOLIDATE plumbing          works; WAIT null constructed
Boundary0  WAIT <-> oracle ROUTE                         analytic nonzero-overlap crossover
Smoke 1    ROUTE -> GROW                                 growth loses to fixed plastic capacity
Gate 2     continuous fixed-capacity ROUTE              FAIL vs address cache on confirmation
Boundary1  cache <-> ROUTE vs world drift               clear sign change / value region
Gate 3     adaptive admission / PROBE                    fixed validated threshold survives
```

## Smoke 0

The old A/B Gabor overlap is approximately machine zero, so 300 WAIT samples could never recover B in expectation. Keep only as plumbing. The script explicitly says:

```text
WAIT_VS_ROUTE_EVIDENCE_CLAIM = NOT_TESTED
```

## Boundary 0

With nonzero current overlap `c`, equal Gaussian noise, total budget 8, and a 3-unit route tax:

```text
WAIT SNR  ~ |c| sqrt(8)
ROUTE SNR ~ sqrt(5)
```

so the predicted crossover is

```text
|c|* = sqrt(5/8) ~= 0.790569
```

This asks when another view *could* repay its cost. ROUTE is oracle here.

## Smoke 1 — growth negative

The missing matched-capacity arm starts with two plastic anchors, second random, growth disabled.

```text
grow       acc=1.000  totalW=1074.0
fixedcap   acc=1.000  totalW= 613.2
```

Same steady state, less transient work for fixed capacity. Fair branch value is about `-461` observation units.

```text
GROWTH_EARNS_KEEP = False
```

This independently reproduces `WildIdea` W3/K2: having alternatives can matter while manufacturing them online earns no architectural importance.

Do not tune growth patience to rescue this.

## Gate 2 — continuous rewrite and strongest null

Gate 2 now does what the original bank implementation could not:

```text
continuous u=(x,y,log-frequency,orientation)
       -> render G(u) directly
       -> true inner product <G(u), X>
```

There is no receiver bank, nearest-index snap, target coordinate, or exhaustive scan.

All structured policies have fixed capacity `K=2` and exactly 8 observations per episode. The hidden source views drift continuously in all four receiver dimensions.

The hybrid policy:

```text
probe existing anchors
    |
    +-- strong evidence -> WAIT
    |
    `-- weak evidence   -> two local SPSA route steps
                           -> persist improved destination
```

Development used seeds `0..19`, `1000..1019`, and `2000..2019`. Untouched confirmation: `3000..3019`.

Confirmation late overlap:

```text
address_cache     0.583
hybrid_plastic    0.644
hybrid_reset      0.575
always_route      0.583
random            0.148
oracle            1.000
```

Paired seed-level contrasts:

```text
hybrid - cache        +0.061  95% CI [-0.005,+0.124]   NOT SEPARATED
hybrid - reset        +0.068  95% CI [+0.009,+0.126]   survives
hybrid - always       +0.061  95% CI [+0.007,+0.107]   survives
```

Therefore:

```text
GATE2_MECHANISM_KEEP = False
GATE2_TASK_PERFORMANCE_CLAIM = NOT_ESTABLISHED
```

Do not tune the drift or threshold to turn this frozen confirmation into a pass.

## Boundary 1 — cache versus ROUTE really is regime-dependent

Sweep environmental drift with capacity, budget, router, admission threshold, and field fixed:

```text
scale   cacheOv   routeOv   delta       95% CI
---------------------------------------------------
0.00     0.999     0.831   -0.168   [-0.211,-0.124]
0.25     0.961     0.753   -0.209   [-0.254,-0.162]
0.50     0.862     0.752   -0.110   [-0.165,-0.057]
0.75     0.707     0.603   -0.104   [-0.245,+0.022]
1.00     0.551     0.650   +0.099   [+0.029,+0.172]
1.50     0.340     0.561   +0.221   [+0.115,+0.324]
2.00     0.232     0.477   +0.244   [+0.154,+0.333]
3.00     0.135     0.323   +0.188   [+0.089,+0.293]
4.00     0.090     0.266   +0.175   [+0.130,+0.222]
```

At low drift, ROUTE is harmful because noisy admission triggers needless movement. At higher drift, stale fixed addresses lose observability and ROUTE repays its cost.

Important correction: this sign change is partly policy-specific. Development sweeps showed that lowering the fixed threshold from `0.72` toward `0.45-0.55` sharply reduces low-drift false routes. Therefore Boundary 1 is evidence for a value region, not evidence that a fancy adaptive conductor is necessary.

## Gate 3 — adaptive admission fails the best fixed threshold

A separate drift × noise validation grid selected the strongest boring fixed admission threshold from:

```text
0.25, 0.35, 0.45, 0.55, 0.65
```

Winner:

```text
fixed threshold = 0.45
```

Then two more intelligent policies were frozen:

```text
HAZARD
successful receiver displacement raises future willingness to ROUTE

PROBE BAND
strong evidence       -> WAIT
weak evidence         -> ROUTE
ambiguous evidence    -> confirm once, then decide
```

Fresh confirmation:

```text
drift = {0.25, 1, 3}
noise = {0.15, 0.24, 0.34}
seeds = 14000..14005
```

Mean late overlap across all nine cells:

```text
fixed 0.45    0.595   cells won 6/9
hazard        0.553   cells won 0/9
PROBE band    0.583   cells won 3/9
```

Seed-paired aggregate contrasts:

```text
hazard - fixed   -0.042   95% CI [-0.072,-0.007]
PROBE  - fixed   -0.012   95% CI [-0.039,+0.024]
```

So:

```text
ADAPTIVE_HAZARD_EARNS_KEEP = False
PROBE_BAND_EARNS_KEEP = False
GATE3_FIXED_THRESHOLD_SURVIVES = True
```

The adaptive policies had recognizable local value regions, but neither beat a validation-selected fixed rule over unseen regimes.

This mirrors `WildIdea` W4b: once the boring fixed policy is selected honestly, an apparent adaptive increment can disappear.

Do not tune Gate 3 further. It is closed.

## What survives now

The strongest current result is not a new neuron architecture. It is a constrained observation-control fact:

> **WAIT, PROBE and ROUTE have different value regions under receiver staleness and observation noise, but simple fixed policies remain extremely strong in stationary synthetic families.**

Continuous receiver geometry is now real in code, and persistent receiver state sometimes matters, but SplatNeuron has not yet earned a distinct ML architecture claim.

## Legitimate next direction

Do **not** open another static drift/noise grid and tune a smarter policy.

A legitimate continuation needs the operating regime itself to change **within one run**, so a fixed validation-selected threshold cannot simply average over one stationary family.

For example:

```text
quiet / low-noise
    -> sudden high-noise period
    -> fast geometric drift
    -> quiet again
```

The strongest baseline must still be the best robust fixed threshold selected before test.

Measure **regret to the best action for each segment**, transition/recovery cost, and whether an online policy can identify that the regime changed without receiving a regime label.

If adaptive admission still fails there, close the admission branch and move to a different SplatNeuron claim.

## Gabor-specific stopping line

Gate 2 finally makes Gabor geometry algebraically real rather than decorative list ordering. It still has not shown Gabors are necessary.

If an arbitrary smooth continuous coordinate field with matched response correlation gives the same behavior, keep the generic active-sensing result and drop the Gabor-specific claim.

## Growth reopening condition

Growth stays dead until:

```text
M recurring useful views >> K fixed receiver slots
```

Only then can structural birth/death buy something preallocation cannot. Any future growth experiment must include fixed-capacity replacement/cache policies from the beginning.

## Stop lines

- Do not rescue Gate 2 by tuning its frozen operating point.
- Do not rescue Gate 3 by tuning adaptive parameters on its confirmation regimes.
- Do not rescue growth by weakening fixed-capacity baselines.
- Do not call higher receiver-target overlap an ML performance win unless downstream task performance also separates.
- Do not add private recurrent state/write-back until ROUTE/admission earns itself against strong fixed policies in a genuinely nonstationary task.
- Do not call the result Gabor-specific until a matched generic continuous geometry loses.
