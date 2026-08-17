# Gate 4 — within-run nonstationary admission

Date: 2026-08-17

Status: **self-tuning admission FAIL; admission branch closed.**

## Why Gate 4 was allowed after Gate 3

Gate 3 showed that hazard adaptation and a three-way PROBE band did not beat a validation-selected fixed threshold over unseen but stationary drift/noise regime cells.

The only legitimate remaining excuse for online admission was **within-run nonstationarity**: perhaps a fixed policy can average across a family, but cannot react when the operating regime itself changes during one lifetime.

Gate 4 therefore changes drift and observation noise inside each run without giving the policy a regime label.

## Frozen development choices

A separate validation sequence used:

```text
(50, drift .2, noise .12)
(50, drift .2, noise .34)
(70, drift 3.0, noise .20)
(50, drift .4, noise .12)
```

Candidate fixed thresholds:

```text
.25 .35 .45 .55 .65
```

Best robust fixed threshold on validation:

```text
0.55
```

The deliberately tiny adaptive rule had one parameter: threshold step size. Candidate values:

```text
.01 .03 .05 .08
```

Best validation value:

```text
0.05
```

The self-tuner starts at threshold `0.45`. After a ROUTE:

```text
route improved/persisted receiver -> threshold += .05
route failed to improve receiver  -> threshold -= .05
```

clipped to `[.25,.75]`.

No hazard estimate, noise estimate, regime label, or neural policy is used.

## Untouched confirmation

The confirmation changes segment order, strengths, and durations:

```text
(45, drift .8, noise .18)
(55, drift .3, noise .36)
(65, drift 2.5, noise .16)
(45, drift .1, noise .12)
(60, drift 2.0, noise .30)
```

Fresh seeds:

```text
16000..16009
```

## Result

```text
fixed 0.55 mean overlap      0.5640
self-tune mean overlap       0.5292
self - fixed                -0.0348
95% CI                      [-0.1573, +0.0842]

fixed route fraction         0.303
self route fraction          0.230
self final threshold mean    0.425
```

Segment detail:

```text
seg1 drift .8  noise .18   fixed .919  self .917  delta -.003
seg2 drift .3  noise .36   fixed .543  self .581  delta +.038
seg3 drift 2.5 noise .16   fixed .488  self .350  delta -.138
seg4 drift .1  noise .12   fixed .624  self .554  delta -.070
seg5 drift 2.0 noise .30   fixed .354  self .365  delta +.012
```

The self-tuner helped in two segments and lost badly in the fast, relatively clean segment. Its threshold drifted downward, making it too reluctant to move exactly when aggressive routing was valuable.

For interpretation only, hindsight best fixed thresholds by segment varied substantially (`.25` to `.65`), so the environment genuinely changed which fixed action rule was best. The online rule nevertheless failed to track that change well enough to beat the robust `0.55` incumbent.

## Verdict

```text
SELF_TUNING_EARNS_KEEP = False
FIXED_ROBUST_POLICY_SURVIVES = True
ADMISSION_BRANCH_STATUS = CLOSED
```

## Supported statement

> **Even when the value of routing changes within a run, a tiny online adaptation rule did not beat a strong robust fixed admission threshold. The current SplatNeuron testbed provides no evidence that an adaptive conductor is needed.**

## Stopping line

Do not add a neural admission policy, a richer hazard estimator, or another tuned PROBE band to this synthetic family.

Future SplatNeuron work must move to a different claim. The next critical attacker is whether the complex Gabor/splat geometry itself contributes anything beyond a generic smooth continuous observation manifold.
