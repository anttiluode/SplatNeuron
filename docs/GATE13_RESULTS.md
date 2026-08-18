# Gate 13 results — the middle band exists, conditionally

Date: 2026-08-18

Status: **FULL FROZEN GRID COMPLETED, THREE WORLD SEEDS.**

This result is interpreted under the preregistration and analysis rules frozen before the full artifacts were inspected:

- `docs/GATE13_PREREG_DKS_EXCHANGE_SURFACE.md`
- `docs/GATE13_ANALYSIS_PLAN.md`
- `docs/GATE13_RANDOM_BASELINE_THEORY.md`
- `docs/GATE13_RANDOM_SEED_ACCOUNTING_CORRECTION.md`

The three GitHub Actions artifacts are from world seeds:

```text
13100
13101
13102
```

and the full workflow completed successfully for all three jobs.

## One-sentence result

> **A task-adapted compact local observation family buys a smaller logical measurement interface when the task subspace is spatially aligned with that family; the width advantage weakens under partial mixing and largely disappears after dense rotation.**

This is a synthetic resource-exchange result, **not** a new sparse-sensing theorem. Task-aware sensor placement, task-based acquisition/quantization, random projections, and restricted-information complexity are established prior art.

## The number that survived the attackers

The cleanest representative cell is `K=8` at the primary `T95` target.

Across the localized worlds, the median validation-selected frontier over all `3 D × 3 world-seed` cells is:

```text
learned compact observation geometry
    M = 32
    learned map payload = 96 B median

best near-zero-map attacker
    M = 48
    map payload = 0 B in every local T95 cell (DCT)
```

Thus the measured trade is roughly:

> **~96 task-specific operator bytes buy a 48 -> 32 reduction in logical measurements for the K=8 localized task family.**

The exact map payload is not universal: selected cells use different post-training precisions. The 96 B number is a median, not a constant law.

After dense rotation of the same latent task family:

```text
K=8, T95, dense
structured median M = 48
best low-map median M = 48
```

The middle band disappears.

That interaction is more important than the absolute byte count.

## Primary T95 median frontier

Medians below are across the nine `(3 D × 3 world-seed)` cells for each `(S,K)`.

```text
T95

structure   K    structured M   structured L_map   best low-map M
-------------------------------------------------------------------
local       2         8              16 B                32
local       4        24              48 B                32
local       8        32              96 B                48
local      16        48             144 B                48

mixed       2        32              72 B                48
mixed       4        32              96 B                48
mixed       8        48              96 B                48
mixed      16        48             144 B                48

dense       2        48             144 B                48
dense       4        48             144 B                48
dense       8        48             144 B                48
dense      16        64             192 B                48
```

The structure-family interaction is obvious in the table. Local task structure can be compressed into the restricted local observation family. Dense rotation destroys that privilege.

## Frozen WIDTH_TRADE counts

The analysis plan defined `WIDTH_TRADE` before the results as:

```text
structured reaches the common validation target
at least one DCT / random attacker also reaches it
structured uses smaller M than the best such low-map attacker
```

It deliberately does **not** call `UNIQUE_REACH` a measured bit/width trade. In the completed grid, every family reached the registered targets somewhere within the width sweep, so the observed classifications were only `WIDTH_TRADE` or `DOMINATED_OR_TIED`.

Counts across the 36 seed-cells per structure/target are:

```text
                 WIDTH_TRADE    DOMINATED_OR_TIED
--------------------------------------------------
local  T95           28                 8
mixed  T95           13                23
dense  T95            3                33

local  T90           31                 5
mixed  T90           23                13
dense  T90            5                31
```

This is the preregistered qualitative signature: width trades are concentrated in the aligned world and fade as alignment is destroyed.

## Replication at T95

The strongest result is not an average. For `K=2,4,8` in the **local** world, the width trade replicated in every registered sampled dimension and every world seed:

```text
              D=1024    D=2304    D=4096
K=2             3/3        3/3        3/3
K=4             3/3        3/3        3/3
K=8             3/3        3/3        3/3
K=16            0/3        0/3        1/3
```

So the local T95 result is **27/27 WIDTH_TRADE seed-cells for K=2,4,8**.

At `K=16`, the compact family's advantage is exhausted: DCT usually reaches the same target at the same `M=48`, and the learned geometry no longer earns its extra map payload.

### Mixed world, T95

The width trade weakens as preregistered:

```text
              D=1024    D=2304    D=4096
K=2             3/3        3/3        1/3
K=4             2/3        1/3        2/3
K=8             1/3        0/3        0/3
K=16            0/3        0/3        0/3
```

### Dense world, T95

Only three isolated `K=2` seed-cells are width trades:

```text
              D=1024    D=2304    D=4096
K=2             1/3        1/3        1/3
K=4             0/3        0/3        0/3
K=8             0/3        0/3        0/3
K=16            0/3        0/3        0/3
```

There is **no dense T95 width trade for K>=4**.

## K moves the frontier much more than sampled D in the aligned world

At local T95, median structured minimum width by K is:

```text
K=2   M=8
K=4   M=24
K=8   M=32
K=16  M=48
```

At the same time, pooling K and comparing the three sampling dimensions gives medians:

```text
D=1024   M=28
D=2304   M=32
D=4096   M=32
```

At local T90 the median structured width is `M=16` at all three D values.

This supports the deliberately narrow scaling statement for this generator:

> increasing task-relevant latent dimension changes required observer resources much more strongly than increasing sampling density from 1024 to 4096 while the continuous task structure is held fixed.

Do **not** turn this into a universal exponent or universal `intrinsic complexity` law.

## The random-projection calibration behaved as predicted

The analytic note predicted for the iid Gaussian attacker, while the full jobs were still running:

```text
N = K + 32
rho ~ sqrt(M/N), M < N
A_random ~ 0.1 + 0.8 * (0.5 + asin(rho)/pi)
```

Across the full artifacts, for `M<=32` the mean absolute difference between this simple population prediction and the observed `random_fixed` validation mean is about:

```text
0.31 percentage points
```

with a maximum across the registered `(K,M)` summary points of about:

```text
0.89 percentage points
```

The registered `M=48` attacker closes the latent span for `K<=16` (`K+32 <= 48`) and approaches the finite-sample latent-reference ceiling as predicted.

This matters because the structured local result is **not** caused by stopping the random arm before it can solve the problem. The low-map side of the frontier is present inside the registered sweep.

In local cells, DCT is in fact the minimum-width low-map attacker at both T95 and T90 throughout the grid. The learned family therefore has to buy width against a deterministic zero-learned-payload basis, not merely a bad random projection.

## Held-out test guard

Configuration selection was performed on validation only.

Among the 28 local T95 `WIDTH_TRADE` selections:

```text
structured selected point clears analogous held-out T95: 22 / 28
low-map selected point clears analogous held-out T95:     28 / 28
```

The six structured misses are very small. The worst miss is:

```text
0.075 percentage points below the analogous test target
```

and the median miss among those six is about:

```text
0.037 percentage points
```

Therefore the correct reading is:

- validation-selected width trades replicate strongly;
- held-out performance stays essentially on the target boundary;
- the zero-map comparator has more margin;
- do not claim a magically robust generalization advantage for learned geometry.

## Task-tail guard

The learned local solutions do not preserve only the mean while destroying a large subset of the 32 tasks.

Median held-out 10th-percentile per-task accuracies at local T95 are approximately:

```text
K=2    87.02%
K=4    86.95%
K=8    86.41%
K=16   86.73%
```

These remain close to the mean selected accuracies, so the shared observer is not obviously sacrificing a hidden tail of tasks.

## Discovery debt

The compact map is **not free to discover**.

Every learned structured `(D,K,S,M)` map pays:

```text
3 optimization restarts
220 steps / restart
660 map-optimization steps total
```

and validation chooses the restart.

The comparison arms pay:

```text
DCT             no map search
random_fixed    no map search
random_search3  three fixed seed trials, validation-selected
PCA             one task-blind fit
```

The GitHub runner logs show the expected pattern: low-width or badly aligned structured configurations can have substantial restart spread, while target-reaching higher-width local configurations are generally much more stable. This is a discovery-cost liability, not a deployment payload.

Wall-clock timings are retained in the JSON artifacts but should not be treated as portable compute theory.

## Random-seed payload correction

The runner serialized a random seed as 4 B. Before the full outputs were inspected we recorded a stronger accounting convention:

```text
random_fixed
    0 task-specific bits if the one fixed seed is shared schema

random_search3
    2 ideal task-specific bits to choose among three shared seeds
    (1 B in a simple byte-aligned serialization)
```

No model was rerun or reselected.

This only strengthens the low-map attacker. It does not change any logical-width comparison.

## What Gate 13 actually establishes

Under this controlled synthetic task family:

1. the latent Bayes/task problem is held fixed while task/spatial alignment is changed;
2. a restricted learned local observation family can exploit aligned structure to reject nuisance with fewer logical measurements;
3. this benefit is bought with nonzero task-specific observation-map description and optimization/search debt;
4. the benefit fades when the task subspace is rotated out of the observation family;
5. increasing K changes the required resource frontier much more than increasing sampled D at fixed continuous structure.

The compact observer therefore occupies a genuine **middle band** in the resource frontier, but only under favorable structure.

## What it does NOT establish

Gate 13 does **not** establish any of these:

```text
novel sparse sensor placement
novel task-based sensing
novel compressed classification
novel random projection theory
novel information-based complexity
universal compact-vs-dense scaling
universal O(1) description law
Gabor/frequency-specific computation
biological dendritic optimality
hardware or energy superiority
```

Those stronger stories are either prior art, already killed in this repo, or unmeasured.

## Prior-art boundary

The local-width effect itself is unsurprising in light of established work:

- sparse sensor placement for classification explicitly learns small sets of task-informative sensor locations;
- task-based quantization/acquisition explicitly designs pre-bottleneck processing for the downstream task;
- compressed sensing / optimal recovery already formalizes measurement complexity and restricted information;
- structured/random sensing already occupies the low-storage measurement-map regime.

See:

- `docs/GATE13_SENSOR_PLACEMENT_BOUNDARY.md`
- `docs/GATE13_TASK_BASED_QUANTIZATION_BOUNDARY.md`
- `docs/GATE13_PRIOR_ART_RANDOM_PROJECTIONS.md`

The narrow remaining experimental seam is the **configuration cost of the sensing rule itself** alongside the measurement width it saves.

## The next question is two-rate task sensing, not another neuron shape

Gate 13 measures the one-time observation-map payload and logical width, but it does **not** measure the actual per-sample representation rate.

That suggests a cleaner next object:

```text
L_map    task-specific bits paid once to configure the observer
L_z      task-relevant representation bits paid per sample
N        number of future samples using the same observer
```

with an amortized description term:

```text
L_effective/sample(N) = L_map / N + L_z
```

plus decoder/discovery currencies reported separately.

This reconnects to the original intuition in a much less mystical form:

> **persistent regularities can justify paying one-time structural specialization if that specialization makes every future observation cheaper.**

But task-based quantization and cost-aware sensing already occupy much of that conceptual territory. A next gate must therefore measure a literal **two-rate distortion surface** rather than merely state the intuition.

The next experiment, if pursued, should quantize `z` itself after the observation map is frozen and measure common task error over:

```text
(operator configuration bits, representation bits/sample)
```

for DCT, fixed/search random, learned compact geometry, PCA/structured attackers, and a task-based learned acquisition baseline.

Only then can we compute a real reuse/amortization crossover rather than substituting `4*M` FP32 storage for communication rate.

## Bottom line

The day's strongest surviving receipt is not:

> `24 bytes beats PCA.`

It is:

> **The cost of a task-adapted sensing rule and the width of the representation it emits are different currencies. In a controlled aligned world, spending a small one-time configuration payload buys a smaller repeated interface; destroy the alignment and the exchange disappears.**

That is narrower than SplatNeuron, but it is now measured rather than metaphorical.
