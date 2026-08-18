# Gate 13 cross-seed analysis plan

Date: 2026-08-18

Status: **FROZEN WHILE THE THREE FULL WORLD-SEED JOBS ARE RUNNING, BEFORE THEIR RESULT JSONS WERE INSPECTED.**

This note prevents post-hoc choice of a favorable summary over the `D × K × S` grid.

## Unit of selection

For each world seed, `(D,K,S)` cell, family and target (`T95`, `T90`):

1. define the target from that seed's latent-reference validation accuracy exactly as preregistered;
2. choose configuration on validation only;
3. report the chosen configuration's untouched test accuracy and resources.

Do not pool seeds before configuration selection.

## Primary family representative

For the operator-bits versus logical-width question, use each family's **minimum-width validation-reaching configuration**, breaking ties by lower map payload, then lower total explicit state, then higher validation accuracy, exactly as the runner's `pick(..., mode="width")` rule.

This deliberately asks whether adaptation buys width. Separate minimum-map and minimum-total-state summaries remain secondary currencies and must not replace the primary summary after results are seen.

## Near-zero-map attackers

Define the low-map attacker set before aggregation as:

```text
DCT
random_fixed
random_search3
```

PCA is reported separately as a data-adapted task-blind dense map. The oracle signal subspace remains a ceiling only.

## Per-seed middle-band classification

For one seed/cell/target, let `m_struct` be the structured family's minimum target-reaching width, and let `m_low` be the minimum target-reaching width among DCT/random_fixed/random_search3.

Classify:

### WIDTH_TRADE

```text
structured reaches target
at least one low-map attacker reaches target
m_struct < m_low
```

This is the clean measured case in which additional learned operator payload buys a smaller logical interface within the registered width sweep.

Record:

```text
Delta_M = m_low - m_struct
rho_M   = m_low / m_struct
Delta_L = L_struct - L_low_selected
```

Do not divide `Delta_M` by `Delta_L` into a universal scalar efficiency score; the pair is the receipt.

### UNIQUE_REACH

```text
structured reaches target
no low-map attacker reaches target through M=64
```

This is **not** counted as a measured bit/width exchange because the low-map side of the trade is censored by the registered `M<=64` sweep.

Report it as a target-reach result only.

### DOMINATED_OR_TIED

```text
some low-map attacker reaches target
m_low <= m_struct
```

At the primary `(L_map,M)` frontier, the structured family has not bought a width advantage.

### NONE_REACH

Neither structured nor a low-map attacker reaches the target.

### STRUCTURED_FAIL_LOW_REACH

A low-map attacker reaches and structured does not. This is a direct compact-family loss.

## Replication rule across the three world seeds

Never call one positive seed a replicated effect.

For every `(D,K,S,target)` cell report counts out of 3:

```text
WIDTH_TRADE
UNIQUE_REACH
DOMINATED_OR_TIED
NONE_REACH
STRUCTURED_FAIL_LOW_REACH
```

Use the phrase **replicated width trade** only when `WIDTH_TRADE` occurs in all 3 world seeds.

Use **majority width trade** only for 2/3, and show the dissenting seed.

Do not collapse `WIDTH_TRADE + UNIQUE_REACH` into one positive count.

## Primary structure interaction

The main mechanistic prediction is not global structured superiority. It is interaction with task/spatial alignment.

For each `D,K,target`, compare the structured family's selected minimum width across:

```text
local -> mixed -> dense
```

Represent failure to reach the target as right-censored `>64`, not as an invented numerical width such as 65 when computing displayed tables.

Primary qualitative signature:

```text
structured resource need local <= mixed <= dense
```

with the strongest low-map-vs-structured width trades concentrated in `local` and weakened/lost in `dense`.

Do not require strict monotonicity in every noisy seed to call an interaction; report the full 3-seed table.

A particularly strong falsifier is:

```text
structured performs equally well in dense as local
```

because that would contradict the proposed locality mechanism.

## Random-projection sanity

At fixed `(K,M,world_seed)`, compare `random_fixed` validation/test accuracy across `D,S`.

Because the latent maps are orthonormal and the Gaussian arm is rotationally invariant, large systematic dependence on `S` is an instrument warning.

Report the span and standard deviation; do not use this check to tune random seeds.

## K and D scaling summaries

### K sensitivity

At fixed `D,S,target`, tabulate selected `M`/reach state against

```text
K = 2,4,8,16
```

for every family.

Do not fit a power-law exponent from four points unless the relationship is visibly regular and the fit is explicitly labeled descriptive/post-hoc. The preregistered result is the table/surface, not an exponent.

### D sensitivity

At fixed `K,S,target`, compare

```text
D = 1024,2304,4096
```

The intended test is whether changing sampling density has a weaker effect than changing K. Again, report the surface before any fitted slope.

## Discovery debt

For structured observations report, per selected point:

```text
3 restart validation accuracies
restart standard deviation
selected restart
660 total map-optimization steps
sum map-fit wall time
```

For `random_search3`, report the three seed trials as search debt even though only one 32-bit seed is deployed.

DCT has no map search. PCA map construction is a single task-blind fit.

Wall time is runner/hardware dependent and is descriptive, not a portable compute theorem. Optimizer-step/restart counts are the primary reproducible discovery-cost quantities.

## Task-dispersion guard

Alongside mean bit accuracy, report test per-task standard deviation and 10th-percentile task accuracy for selected configurations.

If a target-reaching mean is achieved by badly sacrificing a tail of tasks, flag it rather than hiding behind the mean.

## Test-set guard

The validation-selected configuration may fail the analogous held-out test target because of finite-sample selection noise.

Report this explicitly. Do not reselect on test.

A claimed replicated width trade should therefore show both:

```text
validation selection reached target as designed
held-out test performance remains near the intended target
```

without replacing the selected configuration.

## What counts as the strongest possible positive Gate 13 result

A strong result would have the following shape across all three world seeds:

```text
local:
    replicated WIDTH_TRADE at one or more K / targets

mixed:
    smaller or less frequent width trade

dense:
    low-map random catches/ties structured; compact middle band disappears

random arm:
    roughly structure-invariant

K:
    resource need increases as task-relevant dimension rises

D:
    materially weaker effect than K at fixed latent world
```

The defensible statement would remain synthetic and conditional:

> **When task-relevant latent structure is spatially aligned with a compact local observer family, spending task-adapted operator description can buy a smaller logical interface at fixed task error; that exchange weakens as the task subspace is rotated away from locality.**

## Strong negative outcomes

Any of these are valuable:

- low-map attackers tie/beat structured in local cells;
- no replicated WIDTH_TRADE anywhere;
- structured/local advantage does not weaken in dense worlds;
- random arm changes strongly with S, exposing an instrument problem;
- K does not affect required resources, exposing a weak task-complexity knob;
- D dominates K despite fixed latent structure;
- geometry requires unstable restarts and the apparent middle band is seed-fragile.

Keep the negative surface. Do not add another observer family inside Gate 13 after seeing it.
