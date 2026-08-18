# Orthogonal scaling design — separate sampled dimension from task complexity

Date: 2026-08-17

Status: **design note only; do not run until Gate 12 is interpreted.**

Claude's useful hypothesis is:

> compact structured observers should pay mainly for task/intrinsic complexity, whereas dense maps also pay explicitly for sampled input dimension.

Gate 11/11b varied sampled dimension but mostly kept the same digit/stroke task. Gate 12 switches dataset/task, but `intrinsic complexity` remains an informal label rather than a controlled variable.

A stronger test must vary the two axes independently.

## Desired object

Let

```text
D   sampled/ambient input dimension
K   controlled latent/task complexity
L*  minimum learned observation-map bits reaching a fixed common task-error target
M*  minimum logical width reaching that target
```

Measure a surface:

```text
L*(D, K)
M*(D, K)
```

for compact structured observers, dense PCA/learned-linear maps and algorithmic baselines.

## Factorial design

### Axis A — vary D at fixed K

Generate/render the same latent examples at multiple resolutions or sampling densities:

```text
D1 < D2 < D3 < D4
```

The latent identity, nuisance variables and class boundary must be identical across resolutions.

This asks whether extra samples alone force more observer description.

### Axis B — vary K at fixed D

Construct a controlled task family whose discriminative structure increases while image size stays fixed.

Candidate instruments:

1. **Multi-texture mixtures**
   - class depends on K independently placed/oriented texture components;
   - frequencies/orientations/positions drawn continuously;
   - nuisance components matched across classes.

2. **Multi-object compositional scenes**
   - fixed canvas;
   - class depends on relations among K small objects;
   - object count/relation order increases K.

3. **Latent Fourier/RBF mixtures**
   - fixed pixel grid;
   - discriminative signal contains K independent localized basis components;
   - random nuisance basis components prevent trivial single-probe solutions.

The synthetic instrument must include flat/unstructured and oracle controls so the chosen compact family does not win merely because the generator uses its own basis.

## Primary hypothesis

At fixed task error:

```text
compact family:
    required L* should respond more strongly to K than to D

dense M x D map:
    explicit coefficient representation retains a D-dependent cost
```

The claim is **not** that compact `L*` is mathematically independent of D. Expressivity may force more branches or precision as sampling changes.

## Kill conditions

- If compact `L*` grows mainly with D even at fixed K, the proposed task-complexity story fails.
- If compact `L*` does not increase with K because a fixed small map still solves every controlled task, the instrument may be too easy or the complexity variable is not load-bearing.
- If a zero/near-zero-description algorithmic transform plus decoder dominates the compact family across the surface, keep that result.
- If PCA/dense-map compression removes the apparent D dependence after a fair codec, update the dense-map side rather than preserving the slogan.

## Resource reporting

Use the multi-currency protocol:

```text
R_task
L_map
S_map
Q_map
M_logic
B_egress
S_decode
Q_decode
```

No single efficiency ratio.

## Why this could be stronger than dataset hopping

A CIFAR replication can falsify digit-specific overinterpretation, but it cannot identify a scaling variable.

A factorial `D x K` experiment can ask whether required observer description has separable sensitivities:

```text
partial L*/partial D
partial L*/partial K
```

That is the experiment needed before using language such as:

> compact maps pay for intrinsic task complexity.
