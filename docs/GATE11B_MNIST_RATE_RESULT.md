# Gate 11b — MNIST observation-map rate scaling

Date: 2026-08-17

Status: **KEEP as a preregistered two-seed cross-scale rate receipt.**

The protocol was frozen in [`GATE11B_PREREG_MNIST_RATE.md`](GATE11B_PREREG_MNIST_RATE.md) before results.

## Question

Gate 11 on fresh 8x8 digits found that compact 32-value maps stayed within one percentage point of their full-precision accuracy at a literal `24-byte` map payload, while the preregistered row-scaled PCA codec required `576 map bytes`.

Gate 11b asks whether that rate advantage grows when input dimension increases from:

```text
D=64 -> D=784
```

while compact geometry remains 32 values and PCA grows from 1024 to 12,544 coefficients.

## Frozen MNIST protocol

```text
fresh seeds          9200, 9201
train / val / test   6000 / 1000 / 5000
image                28 x 28
D                    784
logical outputs      16 real values
common decoder       FP32 16 -> 10 linear
head state           680 bytes
```

Same Gate-11 codecs and bit depths:

```text
2, 3, 4, 6, 8, 12, 16 bits/value
```

No per-rate retraining.

## Full-precision result

```text
                           seed 9200   seed 9201    mean
--------------------------------------------------------
compact Gabor                 88.94%      89.04%     88.99%
compact Gaussian derivative   87.88%      88.90%     88.39%
PCA-16                        86.24%      85.82%     86.03%
DCT-16                        83.96%      83.92%     83.94%
```

Two seeds are not enough for a broad accuracy claim. They are notably consistent about the rate-curve shape below.

## Rate curves

### Compact Gabor — 32 geometry values

```text
bits/value   map bytes   total bytes   accuracy   drop from full
----------------------------------------------------------------
2                 8          688        31.00%       57.99 pp
3                12          692        67.80%       21.19 pp
4                16          696        86.05%        2.94 pp
6                24          704        88.90%        0.09 pp
8                32          712        88.97%        0.02 pp
12               48          728        88.98%        0.01 pp
16               64          744        88.99%        0.00 pp
FP32            128          808        88.99%
```

### Compact steerable Gaussian derivative

```text
bits/value   map bytes   total bytes   accuracy   drop from full
----------------------------------------------------------------
2                 8          688        23.98%       64.41 pp
3                12          692        54.29%       34.10 pp
4                16          696        83.08%        5.31 pp
6                24          704        88.10%        0.29 pp
8                32          712        88.40%       -0.01 pp
12               48          728        88.38%        0.01 pp
16               64          744        88.39%        0.00 pp
FP32            128          808        88.39%
```

### PCA-16 — 12,544 coefficients + 16 FP32 row scales

```text
bits/value   map bytes   total bytes   accuracy   drop from full
----------------------------------------------------------------
2              3200         3880        83.92%        2.11 pp
3              4768         5448        85.78%        0.25 pp
4              6336         7016        86.01%        0.02 pp
6              9472        10152        86.00%        0.03 pp
8             12608        13288        86.02%        0.01 pp
12            18880        19560        86.04%       -0.01 pp
16            25152        25832        86.03%        0.00 pp
FP32           50176        50856        86.03%
```

### DCT-16

```text
map bytes       0
head bytes    680
accuracy      83.94%
```

DCT again owns the zero-map-payload / lower-accuracy corner.

## The load-bearing scaling result

Smallest map payload within one percentage point of each family's own full precision:

```text
8x8 Gate 11
-----------------------------------
Gabor                 24 B
Gaussian derivative   24 B
PCA                   576 B
DCT                     0 B

28x28 Gate 11b
-----------------------------------
Gabor                 24 B
Gaussian derivative   24 B
PCA                  4768 B
DCT                     0 B
```

The compact maps remain at **exactly 24 bytes** when `D` increases by `12.25x`.

PCA's useful fixed-rate map payload grows by:

```text
4768 / 576 = 8.28x
```

Even though PCA actually needs *fewer bits per coefficient* at scale:

```text
8x8    4 bits/coefficient
28x28  3 bits/coefficient
```

The coefficient count dominates.

### Map-only rate ratio

```text
8x8     576 / 24 = 24.0x
28x28  4768 / 24 = 198.7x
```

### Total deployment-state ratio with the same 680-byte head

```text
8x8
compact    24 + 680 = 704 B
PCA       576 + 680 = 1256 B
ratio                  1.78x

28x28
compact     24 + 680 = 704 B
PCA       4768 + 680 = 5448 B
ratio                   7.74x
```

So the map-rate advantage grew enough that it no longer disappears behind the common decoder state.

## Absolute accuracy floors

```text
floor 80%
  DCT            0 B    83.94%
  Gabor         16 B    86.05%
  derivative    16 B    83.08%
  PCA          3200 B   83.92%

floor 85%
  Gabor         16 B    86.05%
  derivative    24 B    88.10%
  PCA          4768 B   85.78%
  DCT          unreached

floor 88%
  Gabor         24 B    88.90%
  derivative    24 B    88.10%
  PCA           unreached
  DCT           unreached
```

At the `85%` floor, the observed Gabor/PCA map payloads differ by:

```text
4768 / 16 = 298x
```

and total deployment state differs by:

```text
5448 / 696 = 7.83x
```

Do not treat the `298x` number as universal; it depends on this task, accuracy floor, and preregistered codec.

## Same brittleness boundary reappears

Compact geometry remains more brittle **per coordinate** at very low precision.

At 2 bits/value:

```text
Gabor              31.00%
Gaussian derivative 23.98%
PCA                83.92%
```

At 4 bits/value:

```text
Gabor              86.05%
Gaussian derivative 83.08%
PCA                86.01%
```

The compact family becomes attractive because a few additional bits on 32 high-leverage coordinates cost almost nothing in total payload.

Again:

> **Few high-leverage parameters, not individually robust parameters.**

## What actually scaled

The earlier resource split is now empirical at the map-bit level:

```text
observer description rate       compact advantage grows strongly with D
ordinary dense projection MACs  no corresponding advantage; same 16D dot-product work
egress width                    no advantage; all arms still emit 16 real values
decoder compute                 held equal in Gate 11/11b
```

The compact description law therefore survived a literal fixed-rate codec while the digital-compute story remains separate.

## Supported statement

> **Across the preregistered 8x8 and 28x28 tests, a 32-value structured observation map retained its own near-full task accuracy at a constant 24-byte serialized map payload, while the preregistered row-scaled PCA-16 payload required 576 bytes at D=64 and 4,768 bytes at D=784. The corresponding total observer+linear-decoder state ratio grew from about 1.8x to 7.7x.**

This is the strongest current SplatNeuron result.

It is a **description-rate scaling receipt**, not yet a universal law or a runtime-compute advantage.

## Frequency remains irrelevant to the claim

The nonoscillatory steerable Gaussian-derivative observer shows the same key compression behavior:

```text
24 map bytes on 8x8
24 map bytes on 28x28
```

Therefore neither Gate 11 nor Gate 11b resurrects a Gabor/frequency-specific story.

## Limitations / strongest remaining attacks

- only two input dimensions (`64`, `784`);
- MNIST rate test has only two fresh seeds;
- PCA uses a preregistered scalar codec, not entropy coding / vector quantization / learned compression;
- DCT demonstrates that an algorithmic basis can have near-zero map payload at a lower accuracy point;
- map-description bytes are not materialized-filter RAM if the structured map is expanded ahead of inference;
- both compact and PCA maps still pay roughly `16D` dense digital projection MACs if materialized naively;
- no physical shared-carrier/crosstalk cost is present yet;
- no non-digit external task yet.

## Next directions that are allowed

1. **Replication/generalization:** more fresh MNIST seeds or a non-digit dataset, without changing codecs.
2. **Shared-carrier bridge:** introduce the SpectralNeuron resource axis after the logical observation map: physical carrier width/noise/crosstalk versus task accuracy.

Do **not** optimize the Gate-11 codecs on these same data now.

## Reproduce

```bash
python experiments/gate11b_mnist_map_rate.py --download
```
