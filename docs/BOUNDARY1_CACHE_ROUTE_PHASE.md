# Boundary 1 — cache ↔ ROUTE phase diagram

Date: 2026-08-17

Gate 2 failed to separate hybrid plastic routing from a fixed two-address cache at one frozen drift rate. Rather than tune that rate toward a win, Boundary 1 sweeps environmental motion systematically.

## Fixed conditions

```text
receiver capacity K = 2
observation budget  = 8 per episode
same warm-start receiver addresses
same continuous 4-D Gabor field
same hybrid admission threshold / SPSA router
same late-block score
```

Only target drift is scaled.

Base per-update standard deviation in normalized receiver coordinates:

```text
(x, y, log-frequency, orientation)
(0.014, 0.014, 0.014, 0.012)
```

The sweep multiplies that vector by:

```text
0, .25, .5, .75, 1, 1.5, 2, 3, 4
```

Each point uses the same 12 deterministic seeds (`4000..4011`). Primary score is late receiver-target overlap.

## Result

```text
 scale   cacheOv   routeOv     delta      CIlo      CIhi   route%
----------------------------------------------------------------------
  0.00     0.999     0.831    -0.168    -0.211    -0.124    24.3%
  0.25     0.961     0.753    -0.209    -0.254    -0.162    34.2%
  0.50     0.862     0.752    -0.110    -0.165    -0.057    34.2%
  0.75     0.707     0.603    -0.104    -0.245    +0.022    47.2%
  1.00     0.551     0.650    +0.099    +0.029    +0.172    46.7%
  1.50     0.340     0.561    +0.221    +0.115    +0.324    55.4%
  2.00     0.232     0.477    +0.244    +0.154    +0.333    68.2%
  3.00     0.135     0.323    +0.188    +0.089    +0.293    81.2%
  4.00     0.090     0.266    +0.175    +0.130    +0.222    87.8%
```

The sign change is the result.

At low environmental motion, ROUTE is actively harmful. With a stationary target the fixed addresses are nearly perfect, while noisy single-sample admission causes false routes about 24% of the time.

As drift increases, stale receiver addresses lose observability. Around the `0.75 → 1.0` scale transition the value of routing changes sign. Above that region the local router remains imperfect, but paying to change the observation map is better than continuing to reuse stale addresses.

## Supported statement

> Receiver motion has a value region. When the existing observation map remains sufficiently aligned with the world, leave it alone; once environmental change makes that map stale enough, paying to ROUTE becomes worthwhile.

This is a boundary result, not a novelty claim. Active sensing and adaptive sampling are established fields. What matters for SplatNeuron/Kynnys is that the repo now has a measurable admission problem rather than a slogan:

```text
world changes slowly  -> cache / WAIT
transition region      -> uncertainty about whether ROUTE repays its cost
world changes faster   -> ROUTE
```

## Important negative inside the positive

The fixed `0.72` admission threshold is not optimal across the sweep. False ROUTEs at low drift are expensive, and at very high drift the router still remains far below the oracle. Do not tune one threshold on this same sweep and call that a new result.

A legitimate continuation is to ask whether an admission rule can estimate its own expected value of information from observable quantities, then test that rule on fresh drift/noise regimes.
