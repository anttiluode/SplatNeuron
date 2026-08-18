# Gate 11 — observation-map rate versus task distortion

Date: 2026-08-17

Status: **KEEP as a preregistered eight-split rate-distortion receipt.**

The protocol was frozen in [`GATE11_PREREG_RATE_DISTORTION.md`](GATE11_PREREG_RATE_DISTORTION.md) before results.

## Question

Gates 9-10 counted map scalars/coefficient entries. Gate 11 asks a more literal deployment question:

> **After training, how many fixed-rate serialized bytes are needed to describe the observation map before task accuracy degrades?**

This is not optimal entropy coding or MDL. It is an explicit fixed-rate codec with literal bit packing.

## Frozen protocol

Fresh sklearn-digits split IDs:

```text
7200..7207
```

Every family emits:

```text
16 real measurements
```

Every family uses the same full-FP32 linear head:

```text
16 -> 10
170 parameters
680 bytes
```

The head is frozen and **never retrained after map quantization**.

Families:

```text
Gabor geometry                32 normalized map scalars
Gaussian-derivative geometry  32 normalized map scalars
PCA-16                        16 x 64 = 1024 dense coefficients
DCT-16                        algorithmic map; 0 stored map bytes by protocol
```

Bit depths:

```text
2, 3, 4, 6, 8, 12, 16 bits/value
```

Compact geometry uses known `[0,1]` semantic ranges and therefore needs no stored scales.

PCA uses a deliberately strong row-wise codec:

```text
16 FP32 max-absolute row scales
+ fixed-rate signed coefficient codes
```

The PCA training mean is folded into the full-precision decoder bias before compression, so PCA is not charged an extra 64-value mean.

## Full-precision accuracy on the fresh splits

```text
Gabor                   94.13%
Gaussian derivative     94.03%
PCA-16                  93.92%
DCT-16                  90.73%
```

The three high-accuracy maps are close. Gate 11 is therefore mainly about their rate sensitivity, not a full-precision winner.

## Full rate curves

### Compact Gabor — 32 geometry values

```text
bits/value   map bytes   total bytes   accuracy   drop from full
----------------------------------------------------------------
2                 8          688        41.74%       52.40 pp
3                12          692        81.60%       12.53 pp
4                16          696        92.22%        1.91 pp
6                24          704        94.10%        0.03 pp
8                32          712        94.20%       -0.07 pp
12               48          728        94.13%        0.00 pp
16               64          744        94.13%        0.00 pp
FP32            128          808        94.13%
```

### Compact steerable Gaussian derivative — 32 geometry values

```text
bits/value   map bytes   total bytes   accuracy   drop from full
----------------------------------------------------------------
2                 8          688        55.45%       38.58 pp
3                12          692        84.93%        9.10 pp
4                16          696        92.01%        2.01 pp
6                24          704        93.68%        0.35 pp
8                32          712        94.06%       -0.03 pp
12               48          728        94.06%       -0.03 pp
16               64          744        94.03%        0.00 pp
FP32            128          808        94.03%
```

### PCA-16 — 1024 dense coefficients + 16 row scales

```text
bits/value   map bytes   total bytes   accuracy   drop from full
----------------------------------------------------------------
2               320         1000        83.72%       10.21 pp
3               448         1128        91.22%        2.71 pp
4               576         1256        93.65%        0.28 pp
6               832         1512        93.85%        0.07 pp
8              1088         1768        93.92%        0.00 pp
12             1600         2280        93.92%        0.00 pp
16             2112         2792        93.92%        0.00 pp
FP32            4096         4776        93.92%
```

### DCT-16

```text
map bytes       0
head bytes    680
accuracy      90.73%
```

This deliberately gives the analytic transform its strongest map-description interpretation.

## Boundary 1 — low precision hurts compact geometry more per value

Compact geometry is **not** magically quantization-robust.

At two and three bits per map value it degrades much more severely than PCA:

```text
                 2 bits/value   3 bits/value
------------------------------------------------
Gabor               41.74%         81.60%
Gaussian deriv.      55.45%         84.93%
PCA                  83.72%         91.22%
```

This makes sense mechanically: each compact geometry coordinate controls an entire generated receptive field, so a coarse coordinate error can move/rotate/retune many materialized coefficients at once.

The compact family wins by needing **far fewer values**, not by each value being cheap or unimportant.

## Boundary 2 — around 4-6 bits/value the small map count dominates

Smallest map payload reaching absolute mean-accuracy floors:

```text
accuracy floor   Gabor          Gaussian deriv.    PCA            DCT
--------------------------------------------------------------------------
90%              16 B / 92.22%  16 B / 92.01%      448 B / 91.22%  0 B / 90.73%
92%              16 B / 92.22%  16 B / 92.01%      576 B / 93.65%  unreached
94%              24 B / 94.10%  32 B / 94.06%      unreached       unreached
```

DCT correctly owns the lowest-description region: if roughly 90.7% accuracy is enough, its map payload is zero.

Above that region, the compact trainable maps enter the Pareto frontier.

At the `92%` floor:

```text
compact map payload       16 B
PCA map payload          576 B
map-only ratio            36x
```

Because the common 680-byte head dominates total state:

```text
compact total            696 B
PCA total               1256 B
total-state ratio        1.80x
```

Again, map-description compression and total-model compression are different currencies.

## Within one percentage point of each family's own full precision

```text
Gabor               24 B   6 bits/value   94.10%
Gaussian derivative 24 B   6 bits/value   93.68%
PCA                 576 B   4 bits/value   93.65%
DCT                   0 B   algorithmic    90.73%
```

For the three high-accuracy learned/fitted maps:

```text
PCA / compact map-payload ratio = 576 / 24 = 24x
```

Total deployment state with the common head:

```text
compact     24 + 680 = 704 B
PCA        576 + 680 = 1256 B
ratio                   1.78x
```

## What this supports

The float-count story survives a literal codec, but in a narrower form:

> **On this eight-split 8x8-digit protocol, compact structured observation maps preserve ~94% accuracy with roughly 24 bytes of serialized map geometry, while the preregistered row-scaled PCA codec requires roughly 576 map bytes for comparable accuracy. An algorithmic DCT map dominates the lower-accuracy, zero-map-payload corner.**

This is a real **observer rate-distortion frontier**, not a general compression theorem.

The frequency-specific story remains closed: Gabor and the nonoscillatory Gaussian-derivative family occupy nearly the same high-accuracy rate region.

## What this does not support

- optimal entropy-coded description length;
- a claim that PCA cannot be compressed better;
- a claim that 24 bytes is the Kolmogorov complexity of the observer;
- projection-compute savings;
- egress savings (all arms still emit 16 real values);
- physical sensing savings;
- a universal rate law across datasets or input dimensions.

The codecs were preregistered and deliberately simple. Do not now hand-design a special PCA codec or geometry codec on these same splits to rescue either side.

## Next question

The natural scale test is to apply the same fixed-rate observer codec idea to the frozen 28x28 MNIST setup from Gate 10.

There the dense map contains `12,544` coefficients while compact geometry still contains 32 values. If the compact rate needed for useful accuracy stays near tens of bytes while PCA's useful rate grows with `D`, the description-quality scaling story strengthens. If not, Gate 11 remains a small-input compression receipt.

Separately, SpectralNeuron supplies the next orthogonal distortion source: after the logical observation map is described, how much of its distinction survives a shared physical carrier with finite crosstalk?

## Reproduce

```bash
python experiments/gate11_map_rate_distortion.py --full
```
