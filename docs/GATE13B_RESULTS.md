# Gate 13b results — index-only adaptation does not erase the middle band

Date: 2026-08-18

Status: **FULL FROZEN THREE-SEED ATTACK COMPLETED.**

This result is interpreted under the preregistration written before Gate 13b outputs:

- `docs/GATE13B_PREREG_INDEX_ONLY_ATTACKERS.md`
- frozen Gate-13 incumbent points from `docs/GATE13_RESULTS.md`

The attack used the same world seeds `13100, 13101, 13102`, the same `D x K x structure` task generator, the same T95 target construction and the same registered logical widths.

## Question

Gate 13 showed that learned local observation geometry can spend nonzero task-specific map description to reduce logical measurement width in spatially aligned worlds.

A simpler explanation was still open:

> perhaps the task only needs supervised feature selection from a shared transform, and continuous observation geometry is decorative.

Gate 13b therefore gives the attacker a shared analytic dictionary and charges only the selected row indices.

## Attackers

```text
selected_dct
    complete 2-D DCT dictionary shared/free
    deterministic supervised row-subset selection
    only subset indices are task-specific

selected_signed_dct
    one shared fixed Rademacher pixel mask + DCT
    same supervised row-subset selection
    only subset indices are task-specific
```

Subset payload uses the attacker-favorable combinatorial code:

```text
L_index = ceil(log2 binom(D,M))
```

For `M=32` this is only approximately:

```text
D=1024     26 B
D=2304     30 B
D=4096     34 B
```

There is no gradient descent and no restart search.

## Frozen primary test: K=8, local, T95

The preregistered primary unit is all `3 D x 3 world seeds = 9` cells.

Under the preregistered **pairwise attacker-vs-structured** dominance rule:

```text
ATTACKER_DOMINATES       0 / 9
STRUCTURED_DOMINATES     0 / 9
TRADEOFF                 9 / 9
ATTACKER_FAIL            0 / 9
```

Therefore the preregistered geometry-specific kill condition (`ATTACKER_DOMINATES >= 5/9`) is **not** met, and the frozen geometry point remains pairwise Pareto-nondominated in `9/9` primary cells.

```text
GEOMETRY_SPECIFIC_KEEP = survives_index_attack
```

### Important post-result accounting correction

The pairwise `TRADEOFF` label is **not** the same as saying selected-DCT adds a new point to the global Gate-13 frontier.

In every K=8/local/T95 primary cell, the original zero-task-specific-byte DCT baseline already reaches T95 at `M=48`.

Gate 13b's selected dictionary also requires `M=48`, but now pays a nonzero subset-index payload.

Therefore, on the complete frontier:

```text
fixed DCT prefix       M=48    L_map=0 B       reaches T95
selected DCT           M=48    L_map=35–47 B   reaches T95
selected signed-DCT    M=48    L_map=35–47 B   reaches T95
```

The index-only attackers are **globally dominated by the original DCT point** in the primary cells.

So Gate 13b does not create a new low-description frontier point. It simply fails to remove the existing geometry-vs-DCT width trade.

## Primary learned-geometry points

The frozen structured points remain:

```text
seed   D       learned geometry        original zero-byte DCT
----------------------------------------------------------------
13100  1024    M=24   48 B             M=48    0 B
13100  2304    M=32   64 B             M=48    0 B
13100  4096    M=32   64 B             M=48    0 B

13101  1024    M=32   96 B             M=48    0 B
13101  2304    M=32   96 B             M=48    0 B
13101  4096    M=32   96 B             M=48    0 B

13102  1024    M=32   96 B             M=48    0 B
13102  2304    M=32   96 B             M=48    0 B
13102  4096    M=32   64 B             M=48    0 B
```

Gate 13b's supervised row selection never reduces that `M=48` low-description endpoint in the nine primary cells.

Thus the clean primary reading is still:

> **spend zero task-specific map bytes and emit 48 DCT measurements, or spend roughly 48–96 bytes on an aligned learned observation family and emit only 24–32 measurements.**

## Full T95 pairwise dominance surface

The following counts compare only the new index attacker against the frozen learned geometry point, as preregistered. They should not be mistaken for the complete multi-family Pareto frontier.

Counts are across `3 D x 3 world seeds = 9` cells per `(structure,K)`:

```text
local
K=2    STRUCTURED_DOMINATES 6   TRADEOFF 3
K=4    STRUCTURED_DOMINATES 1   TRADEOFF 8
K=8    TRADEOFF 9
K=16   ATTACKER_DOMINATES 8     TRADEOFF 1

mixed
K=2    TRADEOFF 6                ATTACKER_DOMINATES 3
K=4    TRADEOFF 5                ATTACKER_DOMINATES 4
K=8    TRADEOFF 1                ATTACKER_DOMINATES 8
K=16   TRADEOFF 2                ATTACKER_DOMINATES 7

dense
K=2    TRADEOFF 3                ATTACKER_DOMINATES 6
K=4    ATTACKER_DOMINATES 9
K=8    ATTACKER_DOMINATES 9
K=16   ATTACKER_DOMINATES 8      TRADEOFF 1
```

The pairwise pattern still supports a useful qualitative conclusion: as locality is destroyed or K rises, the local learned family loses its compact inductive-bias advantage. But global-frontier claims must always include the original DCT/random points.

## What Gate 13b kills

It kills the easy skeptical explanation:

> `the Gate-13 result is only because DCT used a fixed low-frequency prefix; supervised DCT row selection at the same width would erase it.`

That explanation is false for the frozen K=8/local/T95 primary cells. Selected DCT and selected signed-DCT still require `M=48` throughout the nine primary cells.

## What Gate 13b does not establish

Do **not** conclude:

```text
continuous local geometry is optimal
a Gabor/derivative family is uniquely special
Butterfly/Monarch would lose
all generic learned structured operators would lose
biological morphology is optimal sensing
```

Gate 13b is still a restricted shared-dictionary attacker. A generic compact continuously learned structured operator remains an important unresolved attacker.

## Updated strongest statement

After Gate 13 and Gate 13b, the defensible synthetic statement is:

> **When task-relevant structure is aligned with a restricted local sensing family, spending additional task-specific configuration description can buy a smaller repeated measurement interface. Supervised row selection from a shared DCT or signed-DCT dictionary does not reduce the zero-byte DCT endpoint's required width at K=8, so it does not erase the observed 48 -> 24–32 interface trade.**

That is a resource-frontier result, not a claim that geometry universally wins.

## Next kill test

Before opening a two-rate representation-quantization experiment, the remaining structural attacker should be a **generic trainable short-description operator family** rather than another handpicked fixed dictionary.

Gate 13c preregisters exactly that attack using a compact learned Givens-rotation circuit around the 48-row shared-transform pool.
