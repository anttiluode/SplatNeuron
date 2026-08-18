# Gate 13 preregistration — D × K × structure observer exchange surface

Date: 2026-08-18

Status: **FROZEN BEFORE RESULTS.**

## Why this gate exists

Gate 11/11b separated literal observation-map description from logical width and decoder state. Gate 12 attacks the digit-only result on CIFAR-10. Neither experiment identifies a scaling variable called `intrinsic task complexity`.

A fixed-size parametric map having `O(P)` description length is true by construction. The question that remains empirical is how much observer resource is required when sampled dimension, task-relevant latent dimension, and world structure are varied independently.

This gate therefore measures a surface rather than another dataset point.

## Primary object

Let

```text
D       sampled input dimension
K       task-relevant latent dimension
S       task/spatial alignment of the world map
L_map   learned/operator payload bytes
M       logical observer width
S_dec   decoder state bytes
C_find  observer discovery/search cost
R_task  task error
```

At a common task-error target, estimate the resource frontier

```text
F(D, K, S) = Pareto{L_map, M, S_dec, C_find}
```

The primary comparison is **not one scalar efficiency ratio**.

## Important correction: equal map bytes alone is not enough

A seeded random projection can generate an arbitrary `M × D` matrix from one short seed. Its learned/operator payload can therefore remain approximately constant while `M` grows.

That means the useful question is not simply:

> does learned geometry beat random projection at equal operator bytes?

It is:

> **How many additional task-adapted operator bits are worth paying to save logical width / decoder state at the same task error?**

The expected frontier shape is:

```text
DCT / seeded random      near-zero-map-rate edge, may pay larger M
learned local geometry   possible middle band: more L_map, smaller M
PCA / dense oracle       high-map-rate edge / ceiling
```

A middle band is a prediction, not a required positive result.

## Synthetic task generator

A synthetic generator is required because `K` must be a known knob rather than an informal property of MNIST or CIFAR.

Per example:

```text
z_sig   ~ N(0, I_K)       task-relevant latent factors
z_nuis  ~ N(0, I_U)       task-irrelevant nuisance factors
U       = 32              fixed across all cells
z       = [z_sig, z_nuis]
x       = A(D,K,S) z
```

The columns of `A` are orthonormal in every cell. Therefore changing `D` or `S` does not change latent singular values or inject an SNR advantage.

### Task bank

Use `T = 32` binary tasks sharing the same observer.

For task `t`:

```text
y_t_clean = 1[ w_t^T z_sig >= 0 ]
w_t       fixed random unit vector in R^K
```

The task bank is generated from a fixed master seed. For each `K`, use the first `K` coordinates of a fixed `T × K_max` matrix and renormalize each row. With `T=32` and `K<=16`, the task bank spans the task-relevant latent subspace with overwhelming probability.

Apply an independently generated `10%` label flip rate to every binary target. This keeps the attainable task accuracy below 1 without adding pixel-space noise that would make `D` itself change total noise energy.

The observer is shared across all 32 tasks; only the linear decoder produces the 32 logits. This prevents `K` from collapsing to one lucky scalar discriminant.

## Axes

### Sampled dimension D

Render the same continuous generator at square resolutions

```text
32 × 32   D = 1024
48 × 48   D = 2304
64 × 64   D = 4096
```

The latent variables and task definitions are unchanged.

### Task dimension K

```text
K in {2, 4, 8, 16}
```

The number of nuisance factors remains fixed at `U=32`.

### Structure S

The hidden map is the third axis because a local observer must not win merely because the generator was chosen to match it.

Use three task/spatial-alignment regimes:

```text
local
    task-relevant columns are compact smooth random patches at fixed
    continuous positions; nuisance columns are diffuse global mixtures

mixed
    orthonormalized 50/50 mixture of the local world and an independent
    dense global world

dense
    all task-relevant and nuisance columns are diffuse global mixtures
```

The compact local patches are **not Gaussian-derivative or Gabor atoms**. They are Gaussian-windowed random low-frequency mixtures. The compact observer therefore does not receive its own generating basis.

Every regime is QR-orthonormalized. Column ordering keeps task-relevant local columns first before diffuse nuisances are orthogonalized.

### Measured structure check

For each task-relevant column `a`, report its normalized participation support

```text
support_fraction(a) = 1 / (D * sum_i a_i^4)
```

The preflight must establish

```text
mean support_fraction(local)
    < mean support_fraction(mixed)
    < mean support_fraction(dense)
```

at every `D`, while `||A^T A - I||` remains numerically small.

If this ordering fails, do not interpret the full experiment.

## Data sizes and seeds

Per world seed and K:

```text
train       8,000
validation  2,000
test        5,000
```

Use three preregistered world/data seeds in the full run:

```text
13100, 13101, 13102
```

No test-set selection.

## Common decoder

Every non-oracle observer feeds the same linear multi-label decoder

```text
M -> 32 logits
```

trained with binary cross-entropy.

The decoder is FP32 in this gate. Quantization applies to the observation map only, so map rate and decoder state remain separable currencies.

## Reference and common error targets

Do not use a full-pixel `D -> 32` classifier as the target reference because finite-sample estimation would make reference difficulty grow with `D`.

Instead train the same linear decoder directly on the hidden **task-relevant latent coordinates `z_sig`**. This is an oracle observation reference, not a deployable baseline. It removes `D` and `S` from the target definition while retaining the same decoder class and finite-sample learning problem.

Let its validation bit accuracy be `A_ref,val`.

Because the binary chance level is 0.5, define chance-normalized common targets:

```text
T95 = 0.5 + 0.95 * (A_ref,val - 0.5)   primary
T90 = 0.5 + 0.90 * (A_ref,val - 0.5)   secondary
```

Selection uses validation only. Report selected test accuracy on the untouched test split.

Also report per-task accuracy dispersion so an arm cannot silently sacrifice many tasks while preserving only the mean.

## Observer families

Sweep

```text
M in {8, 16, 24, 32, 48, 64}
```

### A. Learned compact geometry — primary adapted family

Use the same nonoscillatory steerable Gaussian-derivative observer family from Gate 10c/11/12.

One branch:

```text
(x, y, scale, orientation)  = 4 normalized learned values
2 real outputs              = odd/even directional derivative
```

Thus `M/2` branches contain `2M` learned normalized geometry values.

The generator does not use derivative atoms.

Train observer coordinates and the common linear head jointly.

For every `(D,K,S,M,world_seed)`, run **3 optimization restarts**. Select the restart by validation mean bit accuracy only. Report:

```text
all three validation accuracies
mean/std across restarts
selected restart
optimizer steps per restart
total restart count
observer-fit wall time
decoder-fit wall time when separable
```

The restart count is discovery debt; it is not hidden by the small serialized observer.

### B. Seeded Gaussian random projection — task-blind low-rate attacker

Generate an `M × D` iid Gaussian projection from a preregistered 32-bit seed. Do not fit it to labels or data.

Under the same shared family/schema and known `M,D`, charge the deployed seed as

```text
4 bytes
```

and report `M` separately.

Use Gaussian rather than a hand-shaped spatial random map because with orthonormal `A`, its distribution is rotationally invariant. Its expected performance should therefore be insensitive to `S` and approximately insensitive to `D`.

Report two versions:

```text
random_fixed
    one preregistered seed; no validation search over maps

random_search3
    three preregistered seeds; choose by validation; still store the chosen
    32-bit seed but charge all three trials to discovery/search cost
```

The second is a direct attacker against the compact family's three restarts.

### C. DCT — zero learned map payload

Use the deterministic 2-D DCT-II zig-zag basis at each resolution.

```text
L_map = 0 learned bytes
```

`M` and decoder state are still charged.

### D. PCA — data-adapted but task-blind dense map

Fit PCA only to training observations. Because the synthetic data lie in a known low-rank latent span, the implementation may compute the mathematically equivalent PCA through the latent training matrix and materialize the resulting pixel-space rows for rate accounting.

PCA is not label-adapted.

### E. Oracle task subspace — ceiling only

Use generator knowledge to construct the task-relevant pixel subspace as an oracle ceiling. Charge its materialized dense pixel coefficients normally.

It is **not** eligible to establish a practical win and must be labeled oracle in every table.

## Post-training map quantization

For the learned compact map and PCA, use the frozen Gate-11 bit depths:

```text
2, 3, 4, 6, 8, 12, 16 bits/value
```

No per-rate retraining.

Compact normalized coordinates use the Gate-11 fixed-width packer.

PCA uses the Gate-11 per-row symmetric codec with one FP32 scale per row.

The linear decoder remains frozen while evaluating map quantization.

Seeded random and DCT are regenerated algorithmically and are not coefficient-quantized in this gate.

## Resource accounting

For every target-reaching candidate, report at least:

```text
R_task            validation-selected held-out test bit accuracy
L_map             deployed observation-map payload bytes
M                 logical width
B_repr             4*M bytes/sample if FP32 logical values are materialized
S_dec             (32*M + 32) * 4 bytes for FP32 linear decoder
total_state        L_map + S_dec
map_trials         number of map initializations / seeds evaluated
optimizer_steps    total map-optimization steps
map_fit_seconds    observer/map discovery time
decoder_fit_seconds
```

`B_repr` is a representation byte count, **not physical channel bandwidth**.

Do not collapse these currencies into a single score.

## Primary Pareto test

At `T95` and `T90`, construct the validation-selected non-dominated frontier in at least

```text
(L_map, M)
```

and separately report total state and discovery cost.

The compact observer earns a **middle band** only if, at the same common error target, it is non-dominated because additional map bytes buy a smaller `M` than the near-zero-map-rate task-blind arms.

A compact point is not a win merely because PCA has more bytes.

## Preregistered predictions

### P1 — low-map-rate edge

DCT and seeded random projection are expected to own the extreme low-`L_map` edge.

`DCT won the zero-byte corner` is not a failure of the experiment.

### P2 — possible compact middle band only when task structure is spatially aligned

At `S=local`, the learned compact observer may spend tens/hundreds of map bytes to ignore the 32 nuisance factors and reach the common target at smaller `M` than task-blind random/DCT.

This is the main positive possibility.

### P3 — structure interaction is load-bearing

The compact observer's width advantage over seeded random is predicted to shrink from

```text
local -> mixed -> dense
```

and may disappear completely in the dense cell.

If geometry wins only in the local cell, the correct statement is:

> task-adapted local observers can trade map description for logical width when task-relevant structure is spatially localized.

Do **not** generalize that to arbitrary worlds.

### P4 — random-projection sanity

Because the Gaussian random arm is rotationally invariant and every `A` has orthonormal columns, its mean frontier should be approximately invariant to `S` and `D` at fixed `K`.

A large systematic random-arm dependence on `S` is an implementation/instrument warning.

### P5 — K sensitivity

At fixed `D,S`, required observer width should rise as more independent task-relevant factors are introduced.

If the compact family reaches every `K` with the same tiny map/width, inspect whether the task bank actually spans the `K`-dimensional signal subspace before interpreting it as a discovery.

### P6 — weak D sensitivity at fixed latent world

At fixed `K,S`, increasing sampling density alone should not substantially change the oracle reference and should affect the compact/random required resources much less than increasing `K`.

This is empirical, not assumed.

### P7 — discovery debt

The compact arm is expected to show greater optimization/restart cost than DCT, random and PCA map construction. Any deployment advantage must be reported together with that discovery debt.

## Kill conditions

Kill the current compact-geometry story under this instrument if any of the following survives replication:

1. `random_fixed` or `random_search3` reaches the same target with **no larger M** and lower `L_map` in the local cell;
2. the compact observer is not Pareto-nondominated anywhere after matched random/DCT/PCA attackers;
3. compact performance does not interact with `S`, suggesting that the purported locality mechanism is not what is helping;
4. the task bank is rank-deficient or the measured structure axis fails its preflight;
5. results depend strongly on one geometry restart or one world seed and do not replicate.

If the compact arm loses, keep the observer-resource protocol and the negative frontier; do not invent another geometry family inside Gate 13.

## What this gate can and cannot establish

A positive result can establish a **measured resource exchange** in this synthetic family:

> extra task-adapted observer bits can buy lower logical width when task-relevant latent structure is aligned with the observer family, and the exchange changes as that alignment is destroyed.

It cannot establish:

```text
universal intrinsic complexity
biological dendritic efficiency
hardware/energy superiority
novel random projection theory
novel structured matrix theory
universal O(1)-vs-O(D) compression
```

## Stop lines

- Do not change `D`, `K`, `S`, nuisance count, task count, target fractions, `M`, codecs or restart counts after seeing full results.
- Do not select random seeds or geometry restarts on test accuracy.
- Do not add a new structured observer family to rescue a compact loss; that is a later attacker gate.
- Do not call a low map-payload point efficient if it merely pays with much larger `M`.
- Do not infer physical channel rate from logical width.
- Do not publish a universal scaling law from this synthetic instrument.
