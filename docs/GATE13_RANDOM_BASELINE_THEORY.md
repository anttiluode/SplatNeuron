# Gate 13 analytic random-projection baseline

Date: 2026-08-18

Status: **derived while the three full Gate-13 jobs were running, before their result JSONs were inspected.**

This note gives a sanity prediction for the seeded Gaussian attacker. It is not a new theorem; it is elementary random-subspace geometry plus the Gaussian sign-agreement identity.

## Setup

Gate 13 generates

```text
z = [z_sig, z_nuis] ~ N(0, I_N)
N = K + U
U = 32
x = A z
A^T A = I_N
```

A seeded Gaussian observation matrix `R in R^(M x D)` produces

```text
q = R x = R A z = B z.
```

Because `A` has orthonormal columns and `R` is iid isotropic Gaussian, `B=RA` has the same rotationally invariant Gaussian distribution for every registered `D` and every structure regime `S`.

Therefore the random arm should be insensitive to `D` and `S` except for finite-seed / finite-sample variation.

## Fraction of one task direction captured

Let a clean binary task depend on a unit latent signal direction `w`:

```text
y_clean = sign(w^T z).
```

For `M < N`, the row space of a Gaussian `B` is a uniformly random `M`-dimensional subspace of `R^N`.

The expected squared projection of a fixed unit vector onto that subspace is

```text
E ||P_B w||^2 = M/N.
```

For a typical draw, use the approximation

```text
rho^2 ~ M/N
rho   ~ sqrt(M/N),
```

where `rho` is the correlation between the clean latent task variable and its optimal linear prediction from the random measurements.

For `M >= N`, `B` is full column rank almost surely and the complete latent vector is linearly recoverable in the noiseless population model.

## Gaussian sign agreement

For two zero-mean jointly Gaussian scalar variables with correlation `rho`, their sign agreement probability is

```text
A_clean = 1/2 + asin(rho)/pi.
```

Gate 13 then flips each binary label independently with probability `eta=0.10`, so the observed-label accuracy becomes

```text
A_flip = eta + (1 - 2*eta) * A_clean
       = 0.1 + 0.8 * A_clean.
```

Thus the preregistered random-arm sanity curve is approximately

```text
rho      = sqrt(min(M/N, 1))
A_random = 0.1 + 0.8 * (0.5 + asin(rho)/pi).
```

Finite training data, ridge estimation, a finite bank of 32 tasks and one random subspace will perturb this curve.

## Prediction made before full-grid inspection

For the already-audited implementation smoke cell `K=8`, `N=40`:

```text
M=16:
    rho ~ sqrt(16/40)
    predicted A_random ~ 0.674

M=32:
    rho ~ sqrt(32/40)
    predicted A_random ~ 0.782
```

The smoke implementation check produced random-search means in approximately those ranges. That agreement is a calibration check, not a full Gate-13 result.

More importantly, the registered full sweep contains `M=48`.

For `K=8`:

```text
N=40
M=48 >= N
```

so the seeded random arm is predicted to recover the entire latent span and approach the same finite-sample / 10%-flip ceiling as the latent reference.

Therefore the full-grid prediction made here is:

> **At K=8, a near-zero-map seeded random arm should close the T95 target by M=48. If the learned local observer still reaches T95 at M=32, the interesting receipt is a 48 -> 32 logical-width trade purchased with learned operator bytes, not an inability of random sensing to solve the task.**

The same rank argument predicts that the registered `M=48` reaches or nearly reaches the full latent span for all registered K:

```text
K=2   N=34
K=4   N=36
K=8   N=40
K=16  N=48
```

Thus Gate 13 contains its own strong low-map closing attacker rather than leaving the random frontier artificially censored below the latent dimension.

## Why this matters for interpretation

The random projection pays almost no learned operator payload under the shared-schema seed convention, but it observes signal and nuisance indiscriminately. Its width requirement is therefore expected to track the **total** latent span `K+U`.

A task-adapted local observer can earn a middle band only by using spatial alignment to suppress the 32 nuisance directions and preserve the K task directions with fewer logical outputs.

The mechanism being tested is consequently narrower than generic compression:

> **Does task/spatial alignment let a small learned observation map trade description bits for nuisance-rejecting logical width?**

In the dense-rotation regime the local family should lose that privilege and move back toward the random-width requirement or worse.

## Audit / falsification uses

After full results are available, check:

1. random accuracy versus the formula above for every `(K,M)`;
2. random invariance across `D,S`;
3. approach to the latent-reference ceiling once `M >= K+32`;
4. whether any apparent compact advantage is actually a lower-M nuisance-rejection effect rather than a mysterious description-rate law.

Large violations of 1–3 are reasons to inspect the instrument before interpreting geometry.
