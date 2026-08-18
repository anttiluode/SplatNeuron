# Smoke 1 — ROUTE -> GROW

Date: 2026-08-17

Status: **growth claim fails against fixed plastic capacity.**

## Original question

The first version asked whether a second receiver branch grown after repeated useful distant routes could preserve two recurring views more cheaply than one moving receiver.

Sequence:

```text
A -> B -> A -> B
```

The initial comparison was:

```text
route_only     acc=1.000  totalW=18060
single_anchor  acc=1.000  totalW= 3095
grow           acc=1.000  totalW= 1074
```

Against the single-anchor arm, growth appeared to have a positive break-even value:

```text
(3095 - 1074) / 1 = +2021 observation units
```

That baseline was insufficient. One moving anchor cannot retain two views by construction.

## Missing attacker: fixed capacity with plasticity

The corrected experiment adds **two receiver anchors from the start**, with growth disabled.

The second anchor is initialized to a random bank geometry; it receives no oracle knowledge of B. Both anchors are plastic. Existing anchors are checked first, and if neither admits the current episode the arm pays the same exhaustive fallback ROUTE used by GROW. The nearest existing anchor then consolidates toward the successful routed destination.

Nothing else about the synthetic world changes.

Across 20 deterministic seeds, the independently reproduced result is:

```text
policy      accuracy   total work   B first5   B last10   second-B first5
----------------------------------------------------------------------------
grow          1.000      1074.0       180.80      2.00          2.00
fixedcap      1.000       613.2        88.31      2.00          2.00
```

Steady-state behavior is the same. Fixed capacity gets there more cheaply.

The growth patience of three is pure transient tax in this two-view world: the growing arm pays repeated global search before crystallizing capacity that the fixed-capacity arm already possesses and can move on the first successful route.

## Break-even inversion

Using the fair capacity-matched attacker:

```text
(fixedcap work - grow work) / grown branches
= (613.2 - 1074.0) / 1
~= -461 observation units
```

So the branch has **negative** value in this experiment.

The old `+2021` number remains historically useful only as a demonstration that the answer depended on comparing growth against an artificially capacity-limited one-anchor baseline.

## Cross-repo replication of a negative

This reproduces the shape already recorded in `anttiluode/WildIdea` W3/K2:

```text
fixed alternatives + targeted probing
~=
predictable chart growth + targeted probing
```

WildIdea's conclusion was that having alternative models earned the effect while manufacturing them online did not earn architectural importance in that toy.

SplatNeuron now has the same negative in a different representation:

> **Fixed plastic observation capacity explains the two-view benefit more cheaply than growth.**

That convergence should be treated as evidence *against* making branch birth central before a task forces it.

## What survives

The surviving object is smaller:

```text
plastic observation geometry
+
route amortization
```

not:

```text
structural growth is useful
```

Growth is reopened only when there are **more distinct useful views than any matched fixed-capacity system can hold**, with explicit branch costs and replacement/pruning decisions.

That becomes a capacity-allocation problem rather than the current two-view construction.

## Code verdict

`experiments/gate1_route_grow.py` now includes the fixed-capacity attacker and prints:

```text
SMOKE1_REPRODUCED = True
GROWTH_EARNS_KEEP = False
```

CI is green when this negative result reproduces. A negative scientific conclusion is not a software failure.

## Next real attacker

Do not tune `growth_patience` to rescue the current world.

The next experiment must first establish continuous budgeted routing with off-grid receivers and a fixed-capacity plastic baseline. Only after that should growth return in a world whose number of recurring useful views exceeds fixed capacity.
