# Gate 13c results — generic compact Givens circuit does not cross T95

Date: 2026-08-18

Status: **FULL FROZEN THREE-SEED PRIMARY ATTACK COMPLETED.**

Preregistered before results:

- `docs/GATE13C_PREREG_GIVENS_ATTACK.md`

Frozen incumbent:

- original Gate-13 learned-geometry points from `docs/GATE13_RESULTS.md`

Actions run:

```text
Gate 13c generic Givens attacker
run 32106627110
frozen experiment head c17bf5978d6cc1ff974d9d898bda34179a38aff6
```

All three matrix jobs completed successfully and emitted artifacts for world seeds `13100, 13101, 13102`. The scientific verdict below comes from the frozen outputs and preregistered target/dominance rule, not from workflow success.

## Question

Gate 13b showed that supervised index-only selection from a shared DCT/signed-DCT dictionary does not erase the K=8/local/T95 width trade.

Gate 13c asks a stronger question:

> **Can a generic continuously learned short-description orthogonal circuit recover the same `M=24–32` interface without using spatial/geometric coordinates?**

The challenger starts from a task-selected 48-row DCT pool and applies a deterministic-topology trainable Givens circuit. Only rotation angles are learned after the pool selection.

Registered circuit sizes:

```text
rounds       1    2    4    8    16
angles R    24   48   96  192   384
```

Registered logical widths:

```text
M = 24, 32
```

Each configuration receives the same discovery budget style as Gate 13:

```text
3 restarts x 220 Adam steps
```

## Frozen primary verdict

Primary cells:

```text
K=8
structure=local
D=1024,2304,4096
world seeds=13100,13101,13102
T95
```

All nine cells:

```text
ATTACKER_DOMINATES       0 / 9
STRUCTURED_DOMINATES     0 / 9
TRADEOFF                 0 / 9
ATTACKER_FAIL            9 / 9
```

No registered Givens candidate reaches T95 at either `M=24` or `M=32`.

Therefore the preregistered kill condition is not met and the geometry point strongly survives **this specific generic-circuit attack**:

```text
GEOMETRY_SPECIFIC_KEEP = survives_givens_attack
```

This does **not** imply that all Butterfly/Monarch/generic structured operators would fail.

## Cell table

The table shows the frozen learned-geometry minimum-width point and the best observed Givens validation accuracy at `M=32` over all registered round counts and precisions.

```text
seed   D       T95      geometry M/map/val       best Givens M32 val    shortfall
---------------------------------------------------------------------------------
13100  1024    .87234   M24 / 48B / .87303       .87088                 .1466 pp
13100  2304    .87234   M32 / 64B / .87273       .87202                 .0325 pp
13100  4096    .87234   M32 / 64B / .87539       .87169                 .0653 pp

13101  1024    .87026   M32 / 96B / .87186       .86748                 .2778 pp
13101  2304    .87026   M32 / 96B / .87144       .86881                 .1450 pp
13101  4096    .87026   M32 / 96B / .87292       .86859                 .1669 pp

13102  1024    .87437   M32 / 96B / .87916       .87133                 .3046 pp
13102  2304    .87437   M32 / 96B / .87748       .87203                 .2343 pp
13102  4096    .87437   M32 / 64B / .87528       .87003                 .4343 pp
```

Across the nine cells, the best-`M=32` Givens shortfall has:

```text
median   0.167 percentage points
minimum  0.033 pp
maximum  0.434 pp
```

The attacker is therefore **close but consistently below the registered receipt line**.

## The circuit is doing real work

The failure is not well described as `the Givens optimizer did nothing`.

At `M=32`, compare the supervised selected-DCT representation from Gate 13b, the best Gate-13c Givens circuit, and the frozen learned local geometry:

```text
seed   D       selected DCT      best Givens      local geometry     T95
---------------------------------------------------------------------------
13100  1024      .8466              .8709            .8730          .8723
13100  2304      .8444              .8720            .8727          .8723
13100  4096      .8461              .8717            .8754          .8723

13101  1024      .8457              .8675            .8719          .8703
13101  2304      .8448              .8688            .8714          .8703
13101  4096      .8537              .8686            .8729          .8703

13102  1024      .8508              .8713            .8792          .8744
13102  2304      .8465              .8720            .8775          .8744
13102  4096      .7942              .8700            .8753          .8744
```

The generic circuit recovers a large fraction of the missing task information, sometimes reaching within a few hundredths of a point of T95, but does not cross T95 within the registered family.

## Description-complexity interpretation

A generic `M`-dimensional subspace in a 48-dimensional pool has Grassmann dimension:

```text
M * (48 - M)
```

which is:

```text
M=32 -> 512 continuous degrees of freedom
M=24 -> 576
```

For the K=8 task, if the desired observation subspace is constrained to contain the eight-dimensional task-signal subspace, the remaining generic choice still has dimension:

```text
(M-K) * (48-M)
```

and equals `384` for both registered widths:

```text
M=32: (32-8)*(48-32) = 24*16 = 384
M=24: (24-8)*(48-24) = 16*24 = 384
```

The longest registered circuit also has `384` learned angles.

By contrast, Gate 13's local `M=32` family is parameterized by `64` learned geometry coordinates before quantization (`M/2` paired odd/even derivative observers, four coordinates per pair).

This does not prove a lower bound. It gives a useful interpretation of the empirical result:

> **when the task subspace is spatially aligned, the local observation family acts as a much lower-dimensional coordinate chart for useful measurements than a generic orthogonal vocabulary.**

That is an inductive-bias / description-language statement, not a claim that local geometry has greater universal expressive power.

## What survives

Gate 13c strengthens the following narrow synthetic statement:

> **For the frozen K=8 spatially aligned generator, a compact local observation vocabulary reaches the registered T95 target with 24–32 measurements and 48–96 task-specific map bytes. Supervised DCT row selection does not reduce the zero-byte DCT endpoint's 48-measurement width, and a generic fixed-topology Givens circuit with up to 384 learned angles improves the 32-measurement representation substantially but still does not reach T95 in any of nine preregistered cells.**

## What does not survive as a claim

Do not claim:

```text
Givens circuits are generally inferior
Butterfly is ruled out
Monarch/BTT is ruled out
local geometry is globally optimal
this is a new theorem about sensing
this validates biological dendrites
```

The surrounding literature already contains generic learned structured matrices, task-aware sensing, sensor placement and structured orthogonal approximations. Gate 13c is an adversarial instrument inside that old territory.

## Remaining structural attacker

A stronger generic attacker could learn pair topology / sparse factor structure itself or directly instantiate a Butterfly/Monarch/BTT family. Gate 13c's stop rule forbids adding that after seeing these results.

If such a future attacker dominates, retain the task-adapted observation-resource result and demote the geometry-specific interpretation.

## Next conceptual gate

If work continues, the most useful new measurement is no longer another small fixed-map baseline. It is to make the **repeated representation rate literal**:

```text
one-time task-specific operator bits     L_map
per-sample representation bits           L_z
held-out task distortion                 R_task
```

Then measure whether paying `L_map` for an aligned observation rule actually lowers the minimum `L_z` needed per future sample, rather than assuming that fewer floating-point measurements automatically means fewer transmitted bits.

That would turn the current width frontier into a two-rate task-sensing frontier and would directly test whether the width saving amortizes after repeated use.