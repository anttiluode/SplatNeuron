# Gate 8 — pre-collapse receiver frontier

Date: 2026-08-17

Status: **no interior Y block found.**

## Question

Gate 7 could not spend much extra budget on the receiver side once all eight transmitted receivers were learnable.

Gate 8 therefore gives the receiver private capacity that does **not** widen the carrier:

```text
B private complex Gabor branches
        ↓
learned local linear collapse
        ↓
16 real transmitted channels
        ↓
downstream decoder
```

Carrier width is fixed at `16` for every policy.

The total trainable parameter budget is kept in the same neighborhood (`~746-771`). As private branch count rises, downstream hidden width falls.

## Frozen frontier

```text
configuration                params   private branches   downstream
------------------------------------------------------------------
B8_identity_H27               771          8             H=27
B10_reduce_H14                764         10             H=14
B12_reduce_H11                755         12             H=11
B14_reduce_H8                 746         14             H=8
B16_reduce_linear             762         16             linear
```

`B8_identity_H27` is the ordinary-carrier/downstream-heavy endpoint: its 16 receiver outputs already match carrier width, so no local reducer is inserted.

`B16_reduce_linear` is the branch-heavy endpoint: twice as many complex private branches are locally reduced to the same 16-wide carrier and the downstream decoder is linear.

## Development (3 splits)

```text
B8_identity_H27      96.20%
B10_reduce_H14       94.72%
B12_reduce_H11       94.63%
B14_reduce_H8        94.07%
B16_reduce_linear    95.00%
```

The ordinary endpoint won. No architecture was changed after seeing that result.

## Fresh confirmation (3 new splits)

```text
B8_identity_H27      96.02%
B10_reduce_H14       95.19%
B12_reduce_H11       94.63%
B14_reduce_H8        93.61%
B16_reduce_linear    95.93%
```

The branch-heavy endpoint nearly tied the ordinary endpoint on confirmation, but the interior allocations remained below both.

Combined six-split means:

```text
B8_identity_H27      96.11%
B10_reduce_H14       94.95%
B12_reduce_H11       94.63%
B14_reduce_H8        93.84%
B16_reduce_linear    95.46%
```

Paired ordinary-endpoint minus contender bootstrap intervals:

```text
B10   +1.16 points   CI [+0.42,+1.85]
B12   +1.48 points   CI [+0.79,+2.08]
B14   +2.27 points   CI [+0.42,+3.89]
B16   +0.65 points   CI touches zero
```

## Verdict

The preregistered ambition was:

> If an interior sparse/local receiver allocation beats both hard endpoints at fixed transmitted width and comparable total budget, treat it as evidence for a distinct pre-collapse block.

That did **not** happen.

```text
INTERIOR_Y_BLOCK_EARNS_KEEP = False
```

More hidden local branches are not automatically useful just because they can be collapsed before communication.

## Important boundary

This test used a **dense linear local reducer**. Its failure is not a theorem that every structured/sparse local reducer must fail. But the correct reaction is not to tune a fancier reducer until one wins.

A different reducer should be opened only for an independently motivated reason and must keep these two hard endpoints in the benchmark.

## What survives

Gate 6 remains the stronger result:

> learning the 16-channel observation geometry itself can substantially reduce the downstream decoder complexity needed for the same task.

Gate 8 says that simply expanding to more private Gabor branches before a dense collapse does not improve that story.
