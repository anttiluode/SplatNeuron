# Gate 12 pre-result caveat — weak reference ceiling

Date: 2026-08-17

Status: **recorded after the frozen Gate-12 run started but before any scientific output/result was available. No protocol setting is changed.**

Gate 12 defines common validation targets relative to a full-pixel **linear** CIFAR-10 classifier:

```text
T95 = 0.95 * A_full_pixel_linear,val
T90 = 0.90 * A_full_pixel_linear,val
```

This is a clean iso-target within the deliberately linear-decoder comparison, but it may be a weak absolute task target because a linear raw-pixel classifier can be far below modern CIFAR-10 performance.

Therefore a positive Gate-12 result would support only:

> **compact observer expressivity under the shared linear-decoder regime at a common validation-defined target.**

It would not establish that the compact observer preserves enough information for strong CIFAR-10 classification in general.

Do not change Gate 12 now.

If Gate 12 survives, a separate preregistered attacker should raise the task/reference ceiling while keeping the resource accounting explicit, for example:

```text
same observer families
same post-training map codec discipline
stronger but matched downstream decoder
strong full-input reference
common fixed-error target
```

The important point is to avoid using a weak reference ceiling to turn a low absolute accuracy into an inflated expressivity claim.
