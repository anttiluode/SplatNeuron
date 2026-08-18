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

Result:

```text
ATTACKER_DOMINATES       0 / 9
STRUCTURED_DOMINATES     0 / 9
TRADEOFF                 9 / 9
ATTACKER_FAIL            0 / 9
```

Therefore the preregistered geometry-specific kill condition (`ATTACKER_DOMINATES >= 5/9`) is **not** met.

The stronger survival condition — frozen geometry remains Pareto-nondominated in at least `8/9` primary cells — is met in **9/9**.

```text
GEOMETRY_SPECIFIC_KEEP = survives_index_attack
```

This does **not** mean geometry is uniquely optimal. Every primary cell is a tradeoff, not a structured domination.

## The actual primary frontier

Across all nine K=8/local/T95 cells, the index-only attacker reaches the target at `M=48`.

The frozen structured points are:

```text
seed   D       learned geometry       selected dictionary attacker
--------------------------------------------------------------------
13100  1024    M=24   48 B            M=48   35 B
13100  2304    M=32   64 B            M=48   42 B
13100  4096    M=32   64 B            M=48   47 B

13101  1024    M=32   96 B            M=48   35 B
13101  2304    M=32   96 B            M=48   42 B
13101  4096    M=32   96 B            M=48   47 B

13102  1024    M=32   96 B            M=48   35 B
13102  2304    M=32   96 B            M=48   42 B
13102  4096    M=32   64 B            M=48   47 B
```

So the new attacker sharpens rather than removes the resource exchange:

> **a smaller operator description is available if one accepts a wider repeated interface; the learned local family spends more task-specific configuration bits to reduce that interface from 48 measurements to 24–32.**

The old representative `~96 B buys 48 -> 32` statement remains a useful median description, but Gate 13b shows that its low-configuration counterpart can itself be task-adapted rather than purely task-blind.

## Full T95 dominance surface

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

This is more informative than a single win/loss:

1. **aligned, low-K tasks:** learned local geometry often strictly dominates index-only selection;
2. **aligned, intermediate K:** both families occupy the Pareto frontier;
3. **aligned K=16:** the local family exhausts its useful bias and the cheaper shared dictionary usually dominates;
4. **mixed/dense tasks:** index-only generic structure increasingly dominates as expected when locality is no longer a privileged description.

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

> **When task-relevant structure is aligned with a restricted local sensing family, spending additional task-specific configuration description can buy a smaller repeated measurement interface. A supervised index-only shared transform does not erase that exchange at K=8, but it becomes increasingly competitive and eventually dominant as task complexity rises or spatial alignment is destroyed.**

That is a resource-frontier result, not a claim that geometry universally wins.

## Next kill test

Before opening a two-rate representation-quantization experiment, the remaining structural attacker should be a **generic trainable short-description operator family** rather than another handpicked fixed dictionary.

Good candidates include:

```text
small learned Givens-rotation / orthogonal circuit around a shared transform
Butterfly-like sparse orthogonal stages
small learned block/Monarch transform
```

The test should hold deployment description and logical width explicit and should not give the local family an architectural vocabulary unavailable to the generic structured attacker.

If a generic compact learned transform dominates the Gate-13 local points, retain the task-adapted sensing exchange and retire the geometry-specific interpretation.
