# Gate 13b preregistration — index-only task-adapted attackers

Date: 2026-08-18

Status: **FROZEN BEFORE GATE 13B RESULTS.**

## Why this gate exists

Gate 13 found a conditional middle band: in spatially aligned synthetic worlds, a learned local observation family can spend nonzero operator description to reduce the logical measurement width relative to zero/near-zero-map DCT and seeded-random baselines.

That does **not** show that continuous local geometry is the right way to spend those task-specific bits.

A much stronger short-description attacker is to keep a large observation dictionary shared and algorithmic, then encode only the task-selected subset of rows.

This gate asks:

> **Does the Gate-13 middle band survive task-adapted row selection from a shared non-geometric dictionary?**

If not, keep the more generic task-adapted sensing result and stop centering the receipt on learned local geometry.

## Frozen world/task instrument

Reuse Gate 13 without retuning:

```text
world seeds   13100, 13101, 13102
D             1024, 2304, 4096
K             2, 4, 8, 16
S             local, mixed, dense
nuisance      32 latent factors
tasks         32 binary tasks
widths M      8, 16, 24, 32, 48, 64
primary target T95 = 0.5 + .95*(latent-reference validation accuracy - 0.5)
```

The original Gate-13 artifacts remain frozen. Gate 13b does not retrain or reselect the learned-geometry arm.

## Attackers

### 1. selected-DCT

The complete 2-D DCT basis is shared schema and therefore costs zero task-specific numeric coefficients.

For each training cell:

1. compute every DCT row's response to the latent world;
2. compute its normalized training-label covariance vector across the 32 tasks;
3. choose a diverse task-correlated subset using deterministic Gram-Schmidt selection in the 32-dimensional task-covariance space;
4. fit the same ridge linear decoder used in Gate 13;
5. select no hyperparameters on validation other than the already registered width sweep.

Only the chosen row subset is task-specific.

### 2. selected signed-DCT

Apply one globally fixed, shared Rademacher sign mask in pixel space before the same DCT dictionary. The sign-mask seed is part of shared schema, not task-specific payload.

Then perform the identical deterministic supervised row-subset selection.

This arm is a generic randomized orthogonal dictionary attacker. It should not receive any locality narrative.

## Subset payload

For D candidate rows and an unordered subset of M distinct rows, charge the ideal combinatorial index code:

```text
L_index = ceil(log2 binom(D,M)) bits
```

The deployed ordering is canonical ascending row index, so no permutation payload is charged.

Also report byte-aligned payload:

```text
ceil(L_index / 8)
```

This is stronger than charging `M*ceil(log2 D)` bits and is intentionally favorable to the attacker.

The common transform algorithm, D, M and task schema are not charged per deployment, consistent with the shared-codebook correction already applied to fixed random and DCT baselines.

## Discovery debt

Report separately:

```text
D dictionary rows scored once
one deterministic subset-selection pass
no gradient descent
no restarts
one ridge decoder fit per M
```

The attacker is allowed task labels during row selection; it is explicitly task-adapted.

## Primary comparison

Primary cell family:

```text
K=8
S=local
T95
all 3 D x all 3 world seeds = 9 cells
```

Compare the frozen Gate-13 structured minimum-width point to the best Gate-13b index-only attacker under the same validation target.

For each cell classify the new attacker against learned geometry in `(L_map, M)`:

```text
ATTACKER_DOMINATES
    attacker reaches target
    attacker M <= structured M
    attacker L_map <= structured L_map
    at least one inequality strict

STRUCTURED_DOMINATES
    structured reaches target
    structured M <= attacker M
    structured L_map <= attacker L_map
    at least one inequality strict

TRADEOFF
    both reach but neither dominates in (L_map,M)

ATTACKER_FAIL
    structured reaches; no index-only attacker reaches through M=64
```

Do not combine these categories after seeing results.

### Geometry-specific kill rule

The Gate-13 **task-adapted sensing** result is not at stake here.

The narrower claim that learned local geometry occupies a special middle-band frontier is killed if an index-only attacker `ATTACKER_DOMINATES` the frozen structured point in **5 or more of the 9 primary K=8/local/T95 cells**.

It survives this attacker strongly only if the frozen structured point remains Pareto-nondominated (`STRUCTURED_DOMINATES` or `TRADEOFF`) in **at least 8 of 9** primary cells.

Anything between those thresholds is reported as mixed/inconclusive.

## Secondary full-surface analysis

Report the same dominance categories over all `(D,K,S,T95)` cells and show how the selected index payload and minimum reaching M vary with K and S.

Do not add a new dictionary after results are seen.

## Predictions frozen now

1. **selected-DCT is likely to be a serious local-world attacker**, because Gate 13 already showed that the zero-map DCT prefix reaches T95 with only moderately larger M.
2. Task-adapted row selection may recover much of the 48 -> 32 width gap while costing fewer than the learned geometry's map bytes.
3. The fixed signed-DCT dictionary may be stronger after dense rotation, where local geometry loses its inductive-bias advantage.
4. If either index-only dictionary dominates the K=8 local middle band, the correct conclusion is not that Gate 13 failed. The corrected conclusion is:

> task adaptation buys measurement width, but continuous local geometry did not earn architectural importance.

## Prior-art boundary

This is not a novelty claim for feature selection, random orthogonal transforms, or structured random projections. Supervised feature selection is established, and randomized fast orthogonal transforms / random-feature constructions are established.

Relevant surrounding work includes supervised feature-selection methods and fast structured random transforms such as Fastfood / randomized orthogonal transforms.

The purpose here is adversarial control of the Gate-13 interpretation.