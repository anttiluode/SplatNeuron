# Gate 2 — continuous off-grid ROUTE

Date: 2026-08-17

Status: **FAIL against the strongest boring baseline; partial mechanism positives survive.**

## Why Gate 2 exists

Smoke 0/1 used a 300-view precomputed Gabor bank. The targets were exact bank members and receiver interpolation snapped back to a bank index. That made the geometry largely an address table.

Gate 2 removes that escape hatch.

A receiver is a continuous coordinate

```text
u = (x, y, log-frequency, orientation)
```

and every observation renders the corresponding complex Gabor template and takes a true inner product with the rendered field. There is no receiver bank and no nearest-index operation.

## Fair fixed-capacity setup

Growth is disabled. Every structured policy begins with exactly two receiver anchors (`K=2`), already allocated. This directly incorporates the fixed-capacity attack that killed Smoke 1.

The two hidden source views drift continuously in all four routed dimensions. The policy is not given source identity or target coordinates. Each episode receives exactly eight receiver observations.

Policies:

```text
address_cache    probe both fixed addresses; WAIT at the stronger one
hybrid_plastic   probe both; WAIT if evidence is strong, otherwise ROUTE;
                 persist an improved destination in the selected anchor
hybrid_reset     same router, but reset anchors every episode
always_route     same plastic capacity, but ROUTE on every episode
random           eight random continuous receiver queries
oracle           eight queries at the hidden target coordinate
```

ROUTE uses two SPSA-style two-point perturbations. It only sees returned complex responses.

## Development / confirmation discipline

Seeds `0..19`, `1000..1019`, and `2000..2019` were exploratory/development. Hyperparameters were frozen before the final confirmation.

The untouched confirmation set was:

```text
3000..3019
```

## Confirmation result

```text
policy               acc   overlap   lateAcc   lateOv   route%  work
---------------------------------------------------------------------
address_cache       0.656    0.682     0.622    0.583     0.0%   8.0
hybrid_plastic      0.674    0.691     0.661    0.644    41.2%   8.0
hybrid_reset        0.644    0.660     0.604    0.575    46.3%   8.0
always_route        0.569    0.589     0.566    0.583   100.0%   8.0
random              0.507    0.153     0.500    0.148     0.0%   8.0
oracle              1.000    1.000     1.000    1.000     0.0%   8.0
```

Primary quantity is **receiver-target overlap**: the magnitude of the true Gabor inner product, computed only for evaluation. It measures how much of the task emitter is accessible through the selected receiver.

Paired bootstrap contrasts over seed-level late-block means:

```text
hybrid_plastic - address_cache
late overlap  +0.061   95% CI [-0.005, +0.124]   FAIL to separate
late accuracy +0.040   95% CI [-0.033, +0.112]

hybrid_plastic - hybrid_reset
late overlap  +0.068   95% CI [+0.009, +0.126]   survives
late accuracy +0.058   95% CI [+0.003, +0.112]

hybrid_plastic - always_route
late overlap  +0.061   95% CI [+0.007, +0.107]   survives
late accuracy +0.096   95% CI [+0.048, +0.142]

hybrid_plastic - random
late overlap  +0.496   95% CI [+0.427, +0.559]
```

## Verdict

The strongest claim does **not** pass:

> Continuous plastic ROUTE was not separated from a two-address cache on the untouched confirmation set.

Two narrower mechanism results survive:

1. keeping receiver geometry across episodes beat running the same local router from reset geometry;
2. admission matters — ROUTE only when current evidence is weak beat ROUTE on every episode.

So the state after Gate 2 is:

```text
growth                       no
continuous geometry exists   yes
persistent receiver state    useful in this task
always ROUTE                  no
ROUTE > fixed address cache  not established
ML task-performance win      not established
```

Do not retune the drift or admission threshold to convert this gate into a pass. The correct next experiment is a **phase boundary** over environmental drift, asking where cache versus ROUTE changes sign.
