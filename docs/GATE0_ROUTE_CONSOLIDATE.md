# Smoke 0 — ROUTE -> CONSOLIDATE

Date: 2026-08-17

Status: **construction smoke test, not an evidence receipt.**

## Why the status changed

The original run treated the WAIT-vs-ROUTE contrast as evidence that repeating the same observation map cannot restore a missing distinction.

That interpretation was too strong.

For the selected A/B targets the actual rendered Gabor overlap is approximately machine zero:

```text
|Gram[home_A, target_B]| ~= 4e-14
```

So the B label is deliberately absent from the A receiver. Averaging 300 samples at A therefore cannot recover the target signal in expectation. The old criterion

```text
WAIT off-support accuracy <= .65
```

was effectively guaranteed by construction rather than exposed to falsification.

The script now prints that overlap and labels itself `SMOKE0_PASS`; it explicitly reports:

```text
WAIT_VS_ROUTE_EVIDENCE_CLAIM = NOT_TESTED
```

## What the smoke test still checks

The experiment remains useful as plumbing:

```text
A -> B -> A
```

with a 300-element complex Gabor receiver bank.

It verifies that:

- ROUTE can change receiver address and find the constructed target;
- a persistent receiver anchor can consolidate toward a repeatedly useful route;
- a hidden regime change causes search work to spike;
- repeated use reduces that search work again;
- returning to the old regime produces another spike and relearning.

Representative original numbers across 20 deterministic seeds:

```text
WAIT at B        accuracy .486, work 300
ROUTE at B       accuracy 1.000, work 300
CONSOLIDATE B    first5 work 201.2 -> last10 1.0
return A         first5 work 193.4 -> last10 1.05
```

Those numbers demonstrate that the mechanism executes. They do **not** establish a general WAIT/ROUTE advantage.

## Replacement experiment

The real WAIT-vs-ROUTE question is now moved to:

```text
experiments/boundary0_wait_route_crossover.py
```

There the home receiver has **nonzero** overlap with every target. WAIT genuinely improves SNR as `sqrt(n)`, while ROUTE pays an explicit acquisition tax before observing from a better geometry.

That produces a measurable crossover rather than a constructed null.

## Scientific boundary

Keep this file in the history because it records a useful correction:

> A correct qualitative statement can still be a weak experiment if the benchmark geometry makes the answer true by identity.

The current research claim must therefore be earned by the nonzero-overlap boundary and, later, by a router that has to discover a useful continuous view under a strict budget.
