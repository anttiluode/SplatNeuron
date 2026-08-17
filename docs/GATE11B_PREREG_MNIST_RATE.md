# Gate 11b preregistration — does observer description rate scale to MNIST?

Date: 2026-08-17

Status: **frozen before Gate 11b results.**

## Motivation

Gate 11 on fresh 8x8 digits found a literal fixed-rate observer frontier:

```text
within 1 percentage point of own full precision

compact Gabor              24 map bytes
compact Gaussian derivative 24 map bytes
PCA-16                    576 map bytes
DCT-16                      0 map bytes at lower 90.73% accuracy
```

The compact/PCA map-payload ratio was `24x`, but the common 680-byte linear head reduced the total-deployment ratio to only `1.78x`.

Gate 11b asks whether this changes when input dimension grows from `D=64` to `D=784` while compact geometry remains 32 values and PCA grows from 1024 to 12,544 coefficients.

## Fresh MNIST protocol

Use the same data/training construction as Gate 10, but fresh seeds not used in Gate 10/10b/10c:

```text
seeds             9200, 9201
train / val / test 6000 / 1000 / 5000
image dimension   28 x 28 = 784
logical outputs   16 real values
head              16 -> 10 linear, FP32
```

Two seeds are a scale receipt, not a population-level uncertainty estimate.

## Families

Exactly the same four families as Gate 11:

```text
compact Gabor geometry                32 normalized map values
compact steerable Gaussian derivative 32 normalized map values
PCA-16                                16 x 784 = 12,544 coefficients
DCT-16                                algorithmic zero-map-payload anchor
```

No point/Gaussian-pair family search is reopened. Gate 10c already killed the Gabor/frequency-specific interpretation.

## Compression

Use exactly the Gate 11 fixed-rate codecs and bit depths:

```text
2, 3, 4, 6, 8, 12, 16 bits/value
```

Compact geometry:

```text
32 normalized [0,1] values
fixed known semantic ranges
literal payload = 32*b bits
```

PCA:

```text
one FP32 maxabs scale per row
+ 12,544 fixed-rate signed coefficient codes
training mean folded into decoder bias
```

DCT:

```text
0 stored map bytes under shared algorithm protocol
```

Train/fit the full-precision map and linear head once, freeze the head, then quantize only the map. No per-rate retraining or fine-tuning.

## Metrics

Report:

```text
full-precision accuracy
accuracy at each bit depth
literal packed map bytes
total deployment bytes = map + common 680-byte head
accuracy loss from own full precision
```

Absolute accuracy floors for this harder scale task:

```text
80%
85%
88%
```

Also report the smallest map payload within 1 percentage point of each family's own full-precision mean.

## Prediction under test

The **map-count arithmetic** predicts a much larger potential payload gap:

```text
compact at 6 bits/value      24 bytes
PCA at 4 bits/value        6336 bytes
ratio                       264x
```

But accuracy may invalidate that comparison. The gate passes no family by construction.

### Description-scaling story strengthens if

The compact family still reaches a useful high-accuracy region with tens of map bytes while PCA requires thousands of bytes for a comparable region.

Because PCA map storage now greatly exceeds the 680-byte common head, a real map-rate advantage should also produce a much larger **total deployment-state** ratio than Gate 11's 1.78x.

### Story weakens if

Compact geometry needs much higher precision at `D=784`, its accuracy falls into the DCT region, or quantized PCA closes the total-state gap at comparable accuracy.

### DCT is allowed to own the low-rate region

If DCT's zero map payload reaches an accuracy floor, report it as the rate winner for that floor.

## Stop line

Do not tune bit depths, PCA row scaling, geometry ranges, or training after seeing Gate 11b. If the two-seed result is interesting, the next action is replication on more seeds / another dataset or the shared-carrier bridge—not codec search on MNIST.
