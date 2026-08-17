# SplatNeuron — current handoff

Date: 2026-08-17

## One-line thesis still alive

> **Changing the observation map is useful only in a measurable regime where the current receiver has become stale enough to justify the acquisition cost.**

This is smaller and more defensible than the morning's growth story.

## Current ledger

```text
Smoke 0    WAIT / ROUTE / CONSOLIDATE plumbing          works; WAIT null constructed
Boundary0  WAIT <-> oracle ROUTE                         analytic nonzero-overlap crossover
Smoke 1    ROUTE -> GROW                                 growth loses to fixed plastic capacity
Gate 2     continuous fixed-capacity ROUTE              FAIL vs address cache on confirmation
Boundary1  cache <-> ROUTE vs world drift               clear sign change / value region
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
GATE2_MECHANISM_KEEP = False   # strongest baseline survived
GATE2_TASK_PERFORMANCE_CLAIM = NOT_ESTABLISHED
```

Do not tune the drift or threshold to turn this frozen confirmation into a pass.

## Boundary 1 — the useful thing Gate 2 exposed

Instead of tuning one operating point, sweep environmental drift with capacity, budget, router, admission threshold, and field fixed.

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

This is the current strongest SplatNeuron result.

At low drift, ROUTE is harmful because noisy admission triggers needless movement. At higher drift, stale fixed addresses lose observability and ROUTE repays its cost. The sign flips around the `0.75 -> 1.0` drift-scale region.

So the live question is no longer "should neurons move?" It is:

> **Can a receiver estimate the expected value of changing its own observation map from information it can actually observe?**

That is Kynnys-like admission applied inside the receiver itself.

## Immediate next gate

Do **not** tune one fixed admission threshold on Boundary 1 and declare victory.

Next build should learn/derive an admission policy from observable quantities such as:

```text
current evidence magnitude
recent evidence trend
receiver age / time since last route
route success history
local probe disagreement
estimated environmental hazard
```

and compare it against:

```text
fixed threshold sweep
always WAIT
always ROUTE
best validation-selected fixed threshold
simple Bayesian / hazard rule
```

Then freeze it and test on **new combinations of drift and observation noise**, not the Boundary 1 sweep used to design it.

A useful win condition would be a lower regret to the per-regime oracle action (`WAIT` or `ROUTE`) across unseen regimes, not merely better performance at one hand-picked drift rate.

## Gabor-specific stopping line

Gate 2 finally makes Gabor geometry algebraically real rather than decorative list ordering. It still has not shown Gabors are necessary.

If an arbitrary smooth continuous coordinate field with matched response correlation gives the same admission/routing behavior, keep the generic active-sensing result and drop the Gabor-specific claim.

## Growth reopening condition

Growth stays dead until:

```text
M recurring useful views >> K fixed receiver slots
```

Only then can structural birth/death buy something preallocation cannot. Any future growth experiment must include fixed-capacity replacement/cache policies from the beginning.

## Stop lines

- Do not rescue Gate 2 by tuning its frozen operating point.
- Do not rescue growth by weakening fixed-capacity baselines.
- Do not call higher receiver-target overlap an ML performance win unless downstream task performance also separates.
- Do not add private recurrent state/write-back until admission/ROUTE earns itself against strong fixed policies on unseen regimes.
- Do not call the result Gabor-specific until a matched generic continuous geometry loses.
