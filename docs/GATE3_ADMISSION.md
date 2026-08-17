# Gate 3 — admission policy

Date: 2026-08-17

Status: **adaptive hazard FAIL; PROBE band not separated; validation-selected fixed threshold survives.**

## Why this gate exists

Boundary 1 showed that the value of ROUTE changes sign with environmental motion. A fixed admission threshold of `0.72` was too eager in quiet worlds and generated expensive false routes.

The obvious next story was that the receiver should learn environmental hazard or use an extra PROBE when evidence is ambiguous.

Before giving those mechanisms architectural importance, Gate 3 attacks them with a boring baseline:

> select one fixed admission threshold honestly on a separate drift × noise validation grid.

Candidate fixed thresholds were:

```text
0.25, 0.35, 0.45, 0.55, 0.65
```

The validation grid used different drift/noise settings from confirmation. `0.45` had the best mean receiver-target overlap and was frozen before the final run.

## Contenders

### Fixed `0.45`

Same two-anchor plastic router as Gate 2, with one constant admission threshold.

### Hazard-adaptive

Starts conservatively at `0.35`. Successful route displacement is exponentially accumulated as a crude environmental-hazard estimate. As observed displacement rises, the admission threshold rises toward `0.75`, making the receiver more willing to route.

### PROBE band

```text
strong evidence       -> WAIT
weak evidence         -> ROUTE
intermediate evidence -> take one confirming sample
                         then WAIT or ROUTE
```

The extra confirmation consumes from the same eight-observation budget, so a stale receiver that PROBEs has less budget left for routing.

All parameters were frozen before the confirmation below.

## Fresh confirmation

Nine unseen environment cells:

```text
drift scale = {0.25, 1.0, 3.0}
noise sd    = {0.15, 0.24, 0.34}
```

Fresh seeds:

```text
14000..14005
```

Mean late receiver-target overlap across all nine cells:

```text
fixed 0.45    0.595   cells won 6 / 9
hazard        0.553   cells won 0 / 9
PROBE band    0.583   cells won 3 / 9
```

Seed-paired aggregate contrasts:

```text
hazard - fixed   -0.042   95% CI [-0.072, -0.007]
PROBE  - fixed   -0.012   95% CI [-0.039, +0.024]
```

So:

```text
ADAPTIVE_HAZARD_EARNS_KEEP = False
PROBE_BAND_EARNS_KEEP = False
GATE3_FIXED_THRESHOLD_SURVIVES = True
```

## Interpretation

The two adaptive ideas had recognizable value regions:

- hazard adaptation could help when the world was actually moving quickly;
- PROBE could help quiet but noisy cases by rejecting a false low reading;
- PROBE could hurt fast-drift cases because the confirmation sample stole budget from ROUTE.

But neither beat a strong fixed threshold across the unseen regime mixture.

This is another version of a pattern already recorded in `WildIdea` W4b: a seemingly intelligent adaptive increment can disappear once the boring fixed policy is selected on honest validation data.

## Supported statement

> **The existence of different WAIT/PROBE/ROUTE value regions does not imply that an online adaptive admission controller is necessary. In this synthetic family, a validation-selected fixed threshold remained the strongest overall policy.**

## What not to do

Do not tune the hazard update, PROBE band, or confirmation regimes until adaptivity wins. Gate 3 is closed.

A legitimate continuation needs a workload where the operating regime itself changes *within a run*, so a fixed validation-selected threshold cannot merely average over a stationary environment family. Even there, the attacker must be the best robust fixed policy selected before test.
