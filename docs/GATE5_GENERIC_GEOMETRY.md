# Gate 5 — generic smooth geometry attacker

Date: 2026-08-17

Status: **generic manifold reproduces the phase; Gabor-specific claim does not earn keep.**

## Question

Gate 2 finally made receiver geometry continuous and real, but that did not show that complex Gabors/splats were responsible for the cache↔ROUTE behavior.

Gate 5 asks the direct attacker:

> If a boring smooth coordinate manifold has approximately the same local correlation lengths, does it show the same value-of-ROUTE transition?

If yes, keep the generic active-sensing result and demote the Gabor story.

## Matched generic manifold

Receiver coordinates remain

```text
u = (x, y, log-frequency, orientation)
```

but the field no longer contains pixels, Gabors, phase, oscillatory carriers, FFTs, or splats.

A diagonal RBF kernel is fitted once to local magnitude-overlap decay of rendered Gabor receiver pairs:

```text
k(a,b) = exp(-sum_j beta_j (a_j-b_j)^2)
```

with pi-periodic orientation distance.

Fitted coefficients:

```text
beta = [22.1169, 16.8105, 10.1608, 49.8821]
```

Approximate effective Gaussian lengths:

```text
[0.1504, 0.1725, 0.2218, 0.1001]
```

The same target amplitudes, distractor amplitudes, observation noise, fixed capacity (`K=2`), observation budget (`8`), admission threshold (`0.55`), and local ROUTE policy are then used in both media.

## Fresh confirmation

Seeds:

```text
18000..18011
```

Late receiver-target overlap:

```text
scale  medium   cache   route   delta      95% CI
-------------------------------------------------------
0.0    Gabor    1.000   0.969  -0.031   [-0.061,-0.006]
0.0    RBF      0.999   0.973  -0.026   [-0.056,-0.004]

0.5    Gabor    0.835   0.786  -0.049   [-0.102,+0.006]
0.5    RBF      0.789   0.767  -0.021   [-0.078,+0.036]

1.0    Gabor    0.549   0.587  +0.038   [-0.111,+0.185]
1.0    RBF      0.475   0.659  +0.184   [+0.121,+0.257]

2.0    Gabor    0.252   0.479  +0.227   [+0.084,+0.366]
2.0    RBF      0.173   0.474  +0.301   [+0.242,+0.367]

4.0    Gabor    0.070   0.222  +0.151   [+0.047,+0.255]
4.0    RBF      0.041   0.085  +0.044   [+0.011,+0.079]
```

The sign of ROUTE-minus-cache matches at all five drift scales.

```text
sign match                   5 / 5
ROUTE-benefit profile corr   0.759
```

Therefore:

```text
GENERIC_MANIFOLD_REPRODUCES_PHASE = True
GABOR_SPECIFIC_CLAIM_EARNS_KEEP = False
```

## Interpretation

The current cache↔ROUTE phase is not evidence for a special computational role of complex Gabor splats. A generic smooth observation manifold with matched local correlation lengths produces the same qualitative resource transition.

This is useful because it cleanly separates two ideas that had been fused:

```text
value of changing an observation map           survives as generic phenomenon
special value of Gabor/splat receiver geometry not supported here
```

At some drift rates the generic RBF router even gains more from ROUTE than the Gabor system.

## What this does not kill

This does not prove Gabors can never matter in a learned visual medium. It kills the claim that the **current synthetic routing receipts require them**.

A later experiment may still use SplatWorld/SplatField as a concrete learned medium, but any advantage must come from structure not reproduced by a matched generic smooth manifold.

## Next legitimate question

The original brain/AI idea contained a stronger hypothesis that these routing tests have not addressed:

> **Can learning construct an observation map under which a task-relevant distinction becomes locally recoverable?**

That is different from navigating a receiver geometry whose useful coordinates were already supplied by the experimenter.

The next gate should therefore compare learned receiver geometry against fixed/random receivers and matched generic learnable observation maps on a task where the observable distinction itself has to be acquired.
