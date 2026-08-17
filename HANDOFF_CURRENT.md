# SplatNeuron — current handoff

Date: 2026-08-17

## One-line thesis under test

> **Repeated useful computation can shorten its own future observation path by changing persistent receiver geometry.**

## What is executable now

```text
complex Gabor receiver bank
        |
        +-- FIXED
        +-- WAIT at same receiver
        +-- ROUTE across receiver geometries
        +-- CONSOLIDATE useful routes into persistent home geometry
        `-- GROW a persistent branch after repeated useful distant routes
```

No neural-network training is required for Gates 0/1. That is deliberate: they isolate the mechanism before adding learned routing, private recurrent state, or field write-back.

## Gate 0 receipt

A -> B -> A hidden regime shift.

```text
WAIT at B        300 samples, accuracy .486
ROUTE at B       300 mean work, accuracy 1.000
CONSOLIDATE B    first5 work 201.2 -> last10 1.0, accuracy 1.000
return A         first5 work 193.4 -> last10 1.05, accuracy 1.000
```

Interpretation: repeating an observation map that does not carry the label cannot recover it; routing can, and repeated routes can be amortized into persistent receiver geometry.

## Gate 1 receipt

A -> B -> A -> B, one dormant branch, no context label.

```text
route-only total work       18060
single moving anchor         3095
grow                         1074
accuracy                     1.000 all three
grown branches               1.00
break-even branch cost       2021 observation units
```

Once B crystallizes as a second branch, both A and B remain locally available.

## Largest cheats

1. target atoms are exact members of a 300-element receiver bank;
2. fallback ROUTE may exhaustively scan the full bank;
3. regimes are stationary blocks rather than drifting worlds;
4. admission threshold and geometry metric are hand-designed;
5. consolidation/growth rules are hand-designed, not learned;
6. logical observation count is not wall-clock/energy;
7. no strong active-sensing/plasticity baselines yet;
8. no trained SplatWorld basis yet;
9. no local private state or write-back yet.

## Immediate next gate

**Gate 2 — budgeted continuous ROUTE.**

Remove exact-address and exhaustive-search cheats:

```text
continuous off-grid hidden emitter
receiver can move in (x,y,f,theta)
strict <= 8 samples / episode
no access to hidden target geometry
```

Compare:

```text
random route
local gradient / finite-difference route
learned route policy
persistent consolidation
simple route-cache/table baseline
```

Then introduce drift and recurring manifolds.

The kill condition is severe: if a simple context/address cache produces the same amortization without any useful geometry, stop calling this a neuron and keep the cache result.

## Later, only if Gate 2 survives

Transplant onto a trained SplatWorld/SplatField packet basis. Then ask whether receiver geometry learned online discovers useful views of a real learned visual medium rather than a synthetic task bank.

Only after that add private recurrent state and write-back.
