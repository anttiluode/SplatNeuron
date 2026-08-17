# Gate 0 — ROUTE -> CONSOLIDATE

Date: 2026-08-17

Status: **PASS as a controlled synthetic capability test.**

## Question

Can repeated use shorten the observation path when the task-relevant distinction is outside the current receiver's support?

The intended separation is:

```text
WAIT   = collect more samples through the same observation map
ROUTE  = change the observation map
```

and then:

```text
successful repeated ROUTE
        -> persistent receiver movement
        -> lower future ROUTE work
```

## Field

The experiment uses 300 actual normalized complex 2-D Gabor atoms:

```text
5 x positions
5 y positions
3 spatial frequencies
4 orientations
```

Each receiver's response to an emitter is the complex inner product between the two rendered Gabor templates. The full bank therefore has an explicit complex Gram matrix.

An episode contains one strong task atom with amplitude equal to the label in `{-1,+1}`, ten weak distractor atoms, and complex observation noise. Regime A places the task atom at one extreme of position/frequency/orientation. Regime B places it at the opposite extreme. The receiver starts at A.

## Policies

`FIXED` samples the original A receiver once. `WAIT` samples the exact same A receiver 300 times and averages. `ROUTE` searches the 300 receiver geometries in distance order from the original A home and stops when evidence magnitude crosses the admission threshold. `CONSOLIDATE` searches as above, but when a routed observation crosses the evidence threshold, persistent home geometry moves 28% toward that destination.

No gradient training changes receiver geometry during the experiment.

## Gate criteria

The implementation fails unless all of these hold:

```text
fixed off-support accuracy <= .65
WAIT off-support accuracy <= .65
ROUTE off-support accuracy >= .95
CONSOLIDATE off-support accuracy >= .95
regime shift causes >=5x search spike
late shifted work <=35% of early shifted work
late CONSOLIDATE work <=35% of ROUTE-only work
return to old regime spikes again
return regime is relearned
```

## Result

20 deterministic seeds, 50 episodes per block:

```text
policy         block     acc     meanW   first5W   last10W
----------------------------------------------------------
fixed          A1     1.000      1.00      1.00      1.00
fixed          B      0.463      1.00      1.00      1.00
fixed          A2     1.000      1.00      1.00      1.00
wait           A1     1.000    300.00    300.00    300.00
wait           B      0.486    300.00    300.00    300.00
wait           A2     1.000    300.00    300.00    300.00
route          A1     1.000      1.00      1.00      1.00
route          B      1.000    300.00    300.00    300.00
route          A2     1.000      1.00      1.00      1.00
consolidate    A1     1.000      1.00      1.00      1.00
consolidate    B      1.000     21.28    201.20      1.00
consolidate    A2     1.000     20.46    193.42      1.05
```

All criteria passed.

## Supported statement

> In this controlled Gabor-bank world, replication through a receiver whose support does not carry the label stays at chance even with 300 samples; changing receiver geometry recovers the distinction, and a simple persistent use-dependent geometry update amortizes repeated search while preserving classification accuracy.

## What this does not support

Do not claim that WAIT is generally useless; receiver movement is novel; this is a competitive active-vision algorithm; exhaustive routing scales; the Gabor bank is learned; the consolidation rule is a biological Hebbian rule; logical receiver samples predict wall-clock or energy cost; or the result survives off-grid targets or drifting worlds.

The test is intentionally favorable: both hidden targets are exact members of the bank and the router may scan every receiver.

## Why keep it

The receipt isolates one useful distinction before private state, recurrent write-back, or learned routing can muddy it:

```text
more evidence through C
!=
changing C
```

and demonstrates the proposed amortization shape:

```text
stable relationship  -> cheap observation
hidden shift         -> search spike
repeated use         -> geometry adapts
new stable relation  -> cheap observation again
```
