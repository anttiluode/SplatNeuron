# Post-Gate-12 mandatory attackers — do not let dense PCA be the strawman

Date: 2026-08-17

Status: **recorded before Gate-12 scientific results were available. Not part of Gate 12.**

A compact local observer versus dense PCA is not enough for a broad description-rate claim.

PCA is a dense `M x D` projection by construction. A short-description family will automatically have a favorable nominal description scaling relative to it if it remains sufficiently expressive.

Gate 12 correctly includes DCT as a zero-learned-map analytic anchor, but a positive result must next survive **other trainable / selectable short-description operator families**.

## Mandatory families

At a common task-error target, add at least some of:

```text
separable / Kronecker projection
low-rank factorized projection
Butterfly structured transform
Monarch / block-diagonal structured transform
sparse learned projection with indices charged
seeded random projection with seed charged
random convolution / circulant projection with seed/kernel charged
learned convolutional filter bank with matched logical width
```

The exact family should be chosen from primary prior art, not invented to lose.

## Accounting rule

For every attacker charge the representation it actually needs under a shared schema:

```text
learned numeric values
indices / permutations if not algorithmically fixed
random seed if the map is generated from one
row/column scales for quantization
structural metadata not common to all configurations
```

Also report materialized storage and compute separately. A butterfly may have low description **and** fast execution; a compact Gabor/derivative map may have low description but still expand to dense `M x D` filters in naive software.

## Why this matters

The defensible question is not:

> can a compact geometric map beat a dense PCA map in bytes?

It is:

> **among multiple operator families with different inductive biases and description complexities, which families lie on the common-error Pareto frontier in map payload, logical width, decoder state and execution cost?**

If a generic structured matrix family dominates the local geometric observer, keep that result and stop centering SplatNeuron on spatial receiver geometry.

## Prior-art anchors

Relevant established families include:

- Dao et al. 2019, *Learning Fast Algorithms for Linear Transforms Using Butterfly Factorizations*.
- Dao et al. 2022, *Monarch: Expressive Structured Matrices for Efficient and Accurate Training*.
- Qiu et al. 2024, *Compute Better Spent: Replacing Dense Layers with Structured Matrices*.
- Zhao et al. 2017, low-displacement-rank neural-network matrices.

The existence of these families means any eventual contribution is a measured observer/resource frontier, not discovery that structured matrices compress dense ones.
