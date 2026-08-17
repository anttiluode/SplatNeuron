# SplatNeuron — current handoff

Date: 2026-08-17

## One-line state

> **The online-plasticity story mostly died. The strongest surviving result is a receiver-vs-decoder parameter-efficiency frontier: learning a narrow observation map can compile substantial downstream nonlinear computation into the front end.**

No novelty, neuroscience, or hardware claim is currently supported.

## Ledger

```text
Smoke 0    WAIT/ROUTE/CONSOLIDATE plumbing          original WAIT null constructed
Boundary0  WAIT <-> oracle ROUTE                     analytic nonzero-overlap crossover
Smoke 1    online branch growth                     fixed plastic capacity wins
Gate 2     continuous fixed-capacity ROUTE          address cache survives
Boundary1  cache <-> ROUTE vs drift                 sign/value region measured
Gate 3     hazard / PROBE admission                  best fixed threshold survives
Gate 4     within-run self-tuning admission          robust fixed threshold survives
Gate 5     Gabor vs matched generic manifold        generic RBF reproduces phase
Gate 6     learned receiver vs decoder              positive efficiency result
Gate 7     matched ~200 param mixed allocation      no interior optimum
Gate 8     private branch + local collapse frontier no interior Y block
```

## Closed branches

### Growth

Two preallocated plastic anchors beat online branch growth in the A/B recurring-view toy:

```text
grow       total work 1074.0
fixedcap   total work  613.2
```

Same final accuracy and steady state. Fair branch value is negative.

```text
GROWTH_EARNS_KEEP = False
```

This independently mirrors the `WildIdea` W3/K2 negative. Do not reopen growth unless recurring useful views greatly exceed fixed capacity and fixed-capacity replacement/cache policies are present from the start.

### Adaptive admission

Gate 3:

```text
fixed threshold .45    mean late overlap .595
hazard adaptive        .553
PROBE band             .583
```

Gate 4 then gave online adaptation its last fair excuse: the drift/noise regime changed **within the same run**, with no regime label. A robust fixed threshold `.55` and a one-scalar self-tuner were frozen on a separate validation sequence.

Fresh confirmation:

```text
fixed .55       mean overlap .5640
self-tune       mean overlap .5292
delta          -0.0348
95% CI         [-0.1573,+0.0842]
```

```text
ADMISSION_BRANCH_STATUS = CLOSED
```

Do not add a neural conductor or more hazard/PROBE knobs to this synthetic family.

### Gabor-specific ROUTE story

A generic diagonal RBF manifold was fitted to local Gabor overlap lengths and given the exact same fixed-capacity router/budget.

Fresh five-point drift sweep:

```text
drift     Gabor ROUTE-cache     RBF ROUTE-cache
0.0            -0.031               -0.026
0.5            -0.049               -0.021
1.0            +0.038               +0.184
2.0            +0.227               +0.301
4.0            +0.151               +0.044
```

```text
sign match                    5 / 5
benefit-profile correlation   .759
GABOR_SPECIFIC_CLAIM_EARNS_KEEP = False
```

So the early cache↔ROUTE phase is a generic smooth-observation-manifold result, not evidence for splats.

## Gate 6 — result that earned keep

Task: `sklearn` handwritten-digit classification.

Every constrained model transmits exactly **16 real measurements**.

Eight complex Gabor receivers learn only:

```text
x, y, frequency, orientation
```

Receiver geometry = `32` trainable scalars. Linear ten-class head = `170`.

```text
learned receiver + linear = 202 trainable parameters
```

The key attacker begins from the **same initial Gabor receiver geometry**, freezes it, and moves comparable trainable budget downstream.

Eight deterministic stratified splits:

```text
learned receiver + linear          202 params   95.24%
fixed receiver + H=7 MLP           199 params   89.76%
```

Paired gain:

```text
+5.49 percentage points
95% bootstrap CI [+3.40,+7.15]
```

Same-family controls on four splits:

```text
learned point geometry + linear        92.64%
fixed same point geometry + MLP        85.35%

learned Gaussian-pair geometry         90.83%
fixed same Gaussian-pair + MLP         84.10%
```

So the broad effect is **not uniquely Gabor**.

### Load-bearing information attack

Keep the 16 Gabor measurements fixed and increase only decoder capacity:

```text
H=7      199 params    89.76%
H=24     658 params    92.85%
H=32     874 params    93.61%
H=40    1090 params    93.99%
H=48    1306 params    94.31%
```

Learned receiver remains:

```text
202 params             95.24%
```

Paired learned-minus-fixed:

```text
H7     +5.49   CI [+3.40,+7.15]
H24    +2.40   CI [+1.11,+3.68]
H32    +1.63   CI [+0.49,+2.71]
H40    +1.25   CI [+0.31,+2.19]
H48    +0.94   CI [-0.07,+1.94]
```

An RBF-SVM on the same fixed features also reached about `95%` on the first four splits.

Therefore **fixed observation did not destroy the information**. A sufficiently powerful downstream function recovers it.

Supported interpretation:

> **Task-aligned receiver learning makes the downstream decision surface much cheaper. It compiles computation into the observation map.**

This is the current strongest SplatNeuron result.

## Gate 7 — tiny-budget interior does not win

Near 200 total parameters:

```text
fixed receivers + H7 decoder          199 p   ~89.9%
7/8 learned receivers + H6 decoder    200 p   ~93.1%
8/8 learned receivers + linear        202 p   ~95.5%
```

The interior allocation beats the downstream-heavy endpoint but not the all-receiver endpoint.

No Y block yet.

## Gate 8 — true pre-collapse branch frontier

Carrier remains fixed at **16 real channels**, but private receiver branches may exceed transmitted width.

```text
private Gabor branches
        -> learned local linear collapse to 16
        -> downstream decoder
```

Comparable ~750-param allocations:

```text
configuration             params   six-split mean
-------------------------------------------------
B8 direct / H27             771        96.11%
B10 collapse / H14          764        94.95%
B12 collapse / H11          755        94.63%
B14 collapse / H8           746        93.84%
B16 collapse / linear       762        95.46%
```

The two hard endpoints are close; every interior allocation is lower.

```text
INTERIOR_Y_BLOCK_EARNS_KEEP = False
```

Do not tune a fancier reducer until one wins. A new local reducer must have an independent motivation and keep both hard endpoints in the comparison.

## Prior art boundary

Gate 6 is not a novelty claim. Learnable Gabor filters, learned measurement matrices, differentiable sensor layouts, and joint sensor/camera + perception optimization already occupy the broad principle of task-driven sensing.

See `docs/PRIOR_ART.md`.

## Current research question

SplatNeuron is no longer primarily an online-plasticity project.

The live question is:

> **At fixed communication width and controlled total resources, where should computation live: task-aligned receiver/feature generation, local pre-collapse reduction, or the downstream decoder?**

Current answer on this tiny digit task:

```text
small budget     -> receiver learning is extremely efficient
larger budget    -> a big decoder can recover fixed-observer information
private branches -> dense local collapse gives no interior win
```

## Legitimate next moves

1. **Generalize Gate 6 to another dataset / modality** before treating the 6.5x-ish parameter frontier as more than a small-data receipt.
2. Measure FLOPs, wall time, memory movement and not just trainable parameter count.
3. Test independently motivated sparse/local reducers against both Gate 8 endpoints; do not architecture-search toward a win.
4. If returning to a brain model, use Gate 6 only as the modest computational analogy: learning can reshape a representation so that downstream readout becomes simpler. Do not claim that neurons literally implement these Gabor receivers.

## Stop lines

- Admission branch is closed.
- Growth branch is closed for capacity-matched two-view worlds.
- Gabor-specific ROUTE story is closed.
- No interior pre-collapse Y block has been found.
- Do not call Gate 6 novel without a much stronger prior-art comparison and external-task replication.
