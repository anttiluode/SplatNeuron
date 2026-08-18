# Gate 11 preregistration — observation-map rate versus task distortion

Date: 2026-08-17

Status: **frozen before Gate 11 results.**

## Why this gate exists

Gates 9-10 count observation-map scalars/coefficient entries:

```text
compact structured map       32 scalars
PCA-16 on D=64             1024 coefficients
PCA-16 on D=784           12544 coefficients
```

That is only a proxy for description length. Dense maps can be quantized; compact geometry can also be quantized; DCT can be generated algorithmically with essentially no learned map payload.

Gate 11 therefore asks the more literal question:

> **How many serialized bits are required to describe an observation map before task accuracy degrades?**

This is a post-training fixed-rate compression experiment, not an optimal MDL claim.

## Dataset and fresh splits

Use 8x8 `sklearn` digits because the full rate curve is cheap enough to replicate.

Fresh split IDs, not used in Gates 6/9:

```text
7200..7207
```

Use the same train/validation/test split construction and training settings as Gate 6.

## Fixed logical interface

Every learned/dense map under comparison emits:

```text
16 real measurements
```

Every arm uses the same full-FP32 `16 -> 10` linear classifier:

```text
170 parameters = 680 bytes
```

The classifier is **not quantized** in Gate 11. This isolates compression of the observation map. Report both map bytes and total deployment bytes (`map + common head`).

## Map families

### 1. Compact Gabor geometry

```text
8 branches
(x,y,frequency,orientation)
32 normalized geometry values total
16 real outputs
```

### 2. Compact steerable Gaussian-derivative geometry

```text
8 branches
(x,y,scale,orientation)
32 normalized geometry values total
first + second directional derivative per branch
16 real outputs
```

This is the nonoscillatory compact attacker that matched/slightly beat Gabor in Gate 10c on MNIST.

### 3. PCA-16

Fit PCA on the training images only.

To avoid charging PCA for a centering vector unnecessarily, absorb the full-precision training mean into the linear decoder bias before map compression. The serialized observation map is therefore just the `16 x 64` projection matrix.

### 4. DCT-16

Use the same analytic first-16 2-D DCT modes as Gate 9.

Treat the map payload as:

```text
0 bytes
```

under a shared protocol where “DCT-16 on 8x8” is known to both sides. This intentionally gives the algorithmic fixed basis its strongest description-rate interpretation. Decoder bytes are still counted.

## Training and compression order

For Gabor, Gaussian derivative, and PCA:

1. Train/fit the full-precision observation map and linear head once.
2. Freeze the head.
3. Quantize **only the map** post-training.
4. Do **not** retrain or fine-tune the head at any bit rate.
5. Evaluate the same held-out test set.

This prevents each rate point from becoming a separately tuned model.

DCT has no learned map; train its linear head normally and evaluate once.

## Fixed-rate codecs

Bit depths:

```text
2, 3, 4, 6, 8, 12, 16 bits/value
```

### Compact geometry codec

The four geometry coordinates are represented internally as normalized values in `[0,1]` with known semantic ranges.

Quantize each of the 32 normalized values uniformly to `2^b` levels.

No per-dimension scale payload is needed because the ranges are part of the agreed map family.

Literal map payload:

```text
32 * b bits
```

packed into bytes.

### PCA codec

For each of the 16 PCA rows:

1. store one FP32 max-absolute scale (`32 bits`);
2. uniformly quantize the 64 signed coefficients within that row's `[-scale,+scale]` interval to `b` bits;
3. bit-pack the integer codes.

Literal PCA map payload:

```text
16 * 32 scale bits
+
1024 * b coefficient bits
```

This per-row scaling is deliberately a strong PCA baseline.

The PCA training mean is not stored in the map payload because it is folded into the full-precision decoder bias before compression.

### DCT codec

Algorithmic map payload:

```text
0 bits
```

Protocol/implementation code is excluded for all families.

## Metrics

For every split/family/rate report:

```text
test accuracy
map payload bytes
total deployment bytes = map payload + 680-byte head
accuracy drop from that family's full-precision map
```

Aggregate across eight splits.

Also report the smallest map payload that achieves each absolute accuracy floor:

```text
90%
92%
94%
```

and the smallest payload staying within:

```text
1 percentage point of that family's own full-precision accuracy.
```

If a family never reaches a floor, report `unreached`; do not extrapolate.

## Interpretation rules

### Compact-description result survives if

At a task-accuracy region reached by both compact structured and PCA maps, the compact map occupies a clearly lower serialized-map-rate point without relying on a different logical width or decoder.

### Compact-description story weakens if

PCA quantization closes the map-byte gap at comparable accuracy, or the compact map requires high precision such that its literal serialized rate no longer looks unusually small.

### DCT is allowed to win

If DCT reaches a target accuracy with zero learned map payload, that is a real result. Do not hide it by redefining the target.

### Frequency-specific claim remains closed

Gabor is not privileged. Gaussian derivatives are a mandatory matched compact family. Gate 11 cannot resurrect “frequency is the principle.”

## What Gate 11 does not measure

- optimal entropy coding / Kolmogorov complexity;
- quantized decoder cost;
- materialized dense-filter RAM;
- projection FLOPs;
- wall-clock latency;
- physical sensing energy;
- shared-carrier crosstalk.

Those remain separate axes in `OBSERVER_RESOURCE_FRONTIER.md`.

## Stop line

After Gate 11, do not continue hand-designing codecs to rescue a preferred family. If the result is ambiguous, the next step is either a second dataset or the SpectralNeuron shared-carrier bridge, not codec tuning on these same splits.
