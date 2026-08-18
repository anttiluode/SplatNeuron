# Gate 13c preregistration — generic compact learned Givens circuit

Date: 2026-08-18

Status: **FROZEN BEFORE GATE 13C RESULTS.**

## Why this gate exists

Gate 13 established a conditional trade between task-specific observation-map description and logical measurement width. Gate 13b then attacked the result with task-adapted row selection from shared DCT / signed-DCT dictionaries.

Gate 13b did **not** erase the primary K=8/local/T95 middle band: all 9 primary cells remained Pareto tradeoffs. But row selection is still a discrete fixed-dictionary family.

Claude's stronger objection remains:

> generic continuously trainable structured operators may spend the same small description budget without carrying spatial/geometric semantics.

This gate attacks exactly that interpretation.

## Prior-art anchor

Givens rotations are a standard sparse factorization / learning mechanism for orthogonal matrices, and products of sparse factors are a standard route to generic compact trainable transforms. Relevant anchors include Shalit & Chechik (ICML 2014), Frerix & Bruna (ICML 2019), Dao et al.'s Butterfly factorization (ICML 2019), Monarch (ICML 2022), and later structured-matrix comparisons.

Gate 13c therefore does **not** claim novelty for Givens circuits or structured matrices.

## Frozen task cells

Primary only; do not widen the grid after seeing results:

```text
world seeds   13100, 13101, 13102
D             1024, 2304, 4096
K             8
S             local
primary target T95
```

This is the same 9-cell primary family used by Gate 13b.

The incumbent learned-geometry points remain frozen from the original Gate-13 artifacts. They are not retrained or reselected.

## Challenger construction

### Step 1 — shared dictionary and 48-row pool

Reuse Gate 13b's `selected_dct` procedure to choose a task-adapted pool of exactly `P=48` DCT rows from the shared full DCT dictionary using training labels only.

Pool index payload is charged exactly as Gate 13b:

```text
L_pool = ceil(log2 binom(D,48)) bits
```

The DCT algorithm itself is shared schema and free per deployment.

### Step 2 — generic orthogonal circuit

On the 48 pool coefficients, apply a product of trainable Givens-rotation rounds.

Each round contains 24 disjoint two-coordinate rotations. Pair topology follows a deterministic round-robin all-pairs schedule shared by every task/cell, so **pair indices cost zero task-specific bits**.

Only the rotation angles are learned.

Registered round counts:

```text
1, 2, 4, 8, 16
```

Thus learned angle counts are:

```text
R = 24, 48, 96, 192, 384
```

After the rotations, retain the first `M` coordinates as the logical interface.

Registered output widths:

```text
M = 24, 32
```

This family has no positions, scales, orientations, frequencies, locality coordinates, or image-space neighborhoods in its learned description.

## Training / discovery debt

For each `(D,seed,M,round_count)`:

```text
3 restarts
220 optimization steps / restart
same BCE task objective style as Gate 13
same training examples
same validation-only restart selection
```

The transient training head is discarded. The final output is evaluated with the same ridge linear decoder convention used by Gate 13.

Report restart validation accuracies and map-optimization step count.

## Quantization and map payload

Train angles in FP32, then post-training quantize the selected angle vector to:

```text
4, 6, 8, 12, 16 bits / angle
```

No per-rate angle retraining.

The final ridge decoder is fit once on the full-precision selected circuit and then frozen across angle precisions, matching the Gate-13 observation-map quantization convention.

Angle parameterization uses a bounded phase coordinate on `[-pi, pi)` with uniform circular quantization.

Task-specific deployment payload is:

```text
L_map = L_pool + R * angle_bits
```

rounded up only when reporting byte-aligned payload.

Shared circuit topology, D, K, M and quantizer schema are not charged.

## Primary comparison

For each of the 9 frozen K=8/local/T95 cells, compare the complete Gate-13c Pareto set in `(L_map,M)` against the frozen Gate-13 learned-geometry minimum-width point.

Use the same dominance categories as Gate 13b:

```text
ATTACKER_DOMINATES
STRUCTURED_DOMINATES
TRADEOFF
ATTACKER_FAIL
```

### Geometry-specific kill rule

The task-adapted sensing result itself is not at stake.

Kill the narrower interpretation that local geometry earns special middle-band importance if the generic Givens circuit `ATTACKER_DOMINATES` the frozen learned-geometry point in **5 or more of 9** primary cells.

Call the geometry point strongly surviving this attacker only if it remains Pareto-nondominated (`STRUCTURED_DOMINATES` or `TRADEOFF`) in **at least 8 of 9** cells.

Anything between is mixed/inconclusive.

## Predictions frozen now

1. A sufficiently long Givens circuit should eventually recover a useful lower-dimensional task subspace from the 48-row pool.
2. The critical question is **how many learned angles / bits** it needs, not whether a generic orthogonal transform can fit in principle.
3. If 24–48 angles suffice at `M=32`, the generic attacker is likely to be competitive with or dominate the geometry middle band.
4. If the generic circuit needs roughly 100+ angles before reaching T95, the local family's advantage can be reinterpreted as a compact **inductive-bias description**: spatial alignment lets a few geometry coordinates describe a task-relevant subspace that takes more generic rotation degrees of freedom to specify.
5. No universal geometry claim follows either way.

## Stop condition

Do not add learned pair indices, another dictionary, or a different circuit topology inside Gate 13c after seeing results.

A failure of the frozen circuit is retained as a failure of this attacker, not proof against all Butterfly/Monarch-like families.