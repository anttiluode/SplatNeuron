# Gate 12 pre-result caveats — reference ceiling and target normalization

Date: 2026-08-17

Status: **recorded after the frozen Gate-12 run started but before any scientific output/result was available. No protocol setting is changed.**

## 1. Weak reference ceiling

Gate 12 defines common validation targets relative to a full-pixel **linear** CIFAR-10 classifier:

```text
T95 = 0.95 * A_full_pixel_linear,val
T90 = 0.90 * A_full_pixel_linear,val
```

This is a clean common target within the deliberately linear-decoder comparison, but it may be a weak absolute task target because a linear raw-pixel classifier can be far below strong CIFAR-10 performance.

Therefore a positive Gate-12 result would support only:

> **compact observer expressivity under the shared linear-decoder regime at a common validation-defined target.**

It would not establish that the compact observer preserves enough information for strong CIFAR-10 classification in general.

## 2. Raw-accuracy fractions are not chance-normalized

For a ten-class task, chance accuracy is about `0.10`. Defining `T95 = .95 * A_full` does not mean preserving exactly 95% of the reference's **excess accuracy over chance**.

A chance-normalized alternative would have been:

```text
T95_excess = 0.10 + 0.95 * (A_full - 0.10)
```

Gate 12 does **not** use that alternative because the raw-accuracy target was already preregistered and the run had started before this caveat was written.

If the reference accuracy is low, this distinction can matter. Report the actual absolute target values in the result doc and do not translate `T95` into language such as “95% of useful information preserved.”

## Do not change Gate 12 now

If Gate 12 survives, a separate preregistered attacker should raise the task/reference ceiling while keeping the resource accounting explicit, for example:

```text
same observer families
same post-training map codec discipline
stronger but matched downstream decoder
strong full-input reference
common fixed-error target
```

A future protocol may also use a chance-normalized target, but that would be a new gate.

The important point is to avoid using a weak reference ceiling or convenient target normalization to turn a low absolute accuracy into an inflated expressivity claim.
