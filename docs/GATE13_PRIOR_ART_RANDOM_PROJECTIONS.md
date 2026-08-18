# Gate 13 prior-art boundary — random and adaptive projections

Date: 2026-08-18

Status: **novelty not established; attacker literature is mature.**

Gate 13 asks whether spending task-adapted observation-map description can buy a smaller logical width at a fixed task-error target, and whether that exchange depends on task/spatial alignment.

The broad ingredients are established. This note records why the result must be framed narrowly.

## Random projections for classification are established

**Durrant & Kaban, 2013 — Random Projections as Regularizers: Learning a Linear Discriminant Ensemble from Fewer Observations than Dimensions.**

Studies classification directly after random projection and derives guarantees linking the randomly projected classifier to the full-space classifier.

- PMLR: https://proceedings.mlr.press/v29/Durrant13.html

**Kaban, 2016 — Non-asymptotic Analysis of Compressive Fisher Discriminants in terms of the Effective Dimension.**

Provides dimension-free generalization analysis for compressive Fisher discriminants under mild assumptions and explicitly studies how random projection affects classification.

- PMLR: https://proceedings.mlr.press/v45/Kaban15a.html

Therefore Gate 13 cannot claim novelty from:

> a low-dimensional random observation can preserve classification-relevant information without paying explicitly for ambient D.

That is occupied.

## Short-description structured random maps are established

**Le, Sarlos & Smola, 2013 — Fastfood: Computing Hilbert Space Expansions in loglinear time.**

Uses structured random transforms to approximate dense random-feature maps with dramatically lower computation and memory.

- PMLR: https://proceedings.mlr.press/v28/le13.html

**Choromanski & Sindhwani, 2016 — Recycling Randomness with Structure for Sublinear time Kernel Expansions.**

Generalizes structured random embeddings to circulant, Toeplitz, Hankel and low-displacement-rank families and explicitly studies tradeoffs among structure, randomness, variance, computation and storage.

- PMLR: https://proceedings.mlr.press/v48/choromanski16.html

**Bojarski et al., 2017 — Structured adaptive and random spinners for fast machine learning computations.**

Studies a common structured projection framework in which the matrices can be randomized or learned, with theoretical and empirical comparisons to unstructured projections.

- PMLR: https://proceedings.mlr.press/v54/bojarski17a.html

Therefore even the attacker category

> compact algorithmic / seeded projections instead of explicitly storing M x D coefficients

is mature territory.

The exact convention `store one 32-bit PRNG seed under a shared family/M/D schema` is a resource-accounting choice in this repo, not a novelty claim.

## Task-adapted learned measurements are established

**Wu et al., 2019 — Learning a Compressed Sensing Measurement Matrix via Gradient Unrolling.**

Learns measurement matrices that exploit data structure beyond data-independent random sensing and reports improved measurement efficiency.

- PMLR: https://proceedings.mlr.press/v97/wu19b.html

The broader learned-sensing / compressed-classification literature already occupies:

> learn an observation/projection map from data or labels so fewer measurements are required.

Gate 13 therefore must not be sold as discovery of task-adapted sensing.

## Lightly parameterized adaptive structure is also established

**Yang et al., 2015 — A la Carte: Learning Fast Kernels.**

Learns properties of structured Fastfood-style expansions with O(m) stored parameters and O(m log d) compute.

- PMLR: https://proceedings.mlr.press/v38/yang15b.html

This is especially relevant to any future claim that a small number of learned observer parameters uniquely creates a middle ground between a fixed random map and a dense learned matrix.

That general middle ground is occupied.

## What Gate 13 is actually allowed to ask

The narrow empirical object is a **multi-currency exchange surface**:

```text
same task-error target

additional task-adapted L_map
        versus
reduction in logical width M / decoder state

as D, K and task/spatial alignment S are varied independently
```

The intended attacker ordering is:

```text
DCT / fixed seeded random      near-zero learned map payload
searched seeded random         same tiny deployed payload + explicit search debt
learned compact geometry       more map payload + possible lower M
PCA / dense oracle             larger materialized map payload / ceiling
```

No one-dimensional winner is expected or required.

## The structure interaction is the only potentially informative part

A local geometric observer should not be expected to dominate a rotationally invariant random projection in arbitrary worlds.

Gate 13 therefore preregisters a third axis:

```text
local -> mixed -> dense task/spatial alignment
```

while preserving an orthonormal latent map.

The useful possible receipt is not:

> learned geometry is better than random projection.

It is narrower:

> **the resource exchange between task adaptation and logical width changes predictably as task-relevant structure is aligned with, then rotated away from, the compact observer family.**

Even that would be a synthetic measured result, not a theorem or novelty claim about structured projections.

## Strong nulls

The following are scientifically useful and must be kept if observed:

1. fixed seeded random dominates compact geometry even in the local-alignment cell;
2. searched random dominates once equal search/restart debt is charged;
3. compact geometry is never Pareto-nondominated in `(L_map, M)`;
4. geometry performs similarly in local/mixed/dense cells, killing the proposed locality mechanism;
5. DCT owns both map-rate and width corners for some regimes;
6. PCA/dense structure closes any apparent compact middle band.

A negative Gate 13 would leave a useful protocol and a strong attacker result, but not a compact-observer contribution.
