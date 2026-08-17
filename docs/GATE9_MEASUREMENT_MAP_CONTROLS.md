# Gate 9 — fixed-basis controls and measurement-map description cost

Date: 2026-08-17

Status: **Gate 6 interpretation narrowed. PCA-16 is a load-bearing attacker.**

## Why Gate 9 exists

Gate 6 compared a learned low-parameter Gabor receiver against the **same random initial Gabor geometry frozen**. That established a receiver-vs-decoder allocation effect, but it did not establish that receiver *learning* was the important reason.

A much stronger boring control is a fixed but well-chosen 16-channel basis.

Two such controls are now explicit:

```text
PCA-16   unsupervised; fit on training images only
DCT-16   data-free; first 16 2-D DCT modes in zig-zag order
```

Both feed the same `16 -> 10` linear head (170 trainable parameters) and transmit the same 16 real values as Gate 6.

## Independent reproduction on Gate 6 split IDs

Using deterministic linear-head training on the same eight split IDs `6000..6007`:

```text
PCA-16 + linear   mean 95.42%
DCT-16 + linear   mean 92.85%
```

The previously reported Gate 6 learned-Gabor mean on those eight split IDs is:

```text
learned Gabor + linear   95.24%
```

The exact decimal comparison depends on optimizer/initialization details for the linear head, so the supported conclusion is deliberately coarse:

> **PCA-16 essentially closes the Gate 6 accuracy gap. A large part of the original learned-vs-frozen result was 'random frozen Gabors are a poor 16-channel basis', not a unique advantage of task-trained receiver geometry.**

DCT-16 is also a strong zero-task-learning control: it clearly beats the original fixed-random-Gabor matched-budget arm, though it remains below PCA/learned-Gabor accuracy in this implementation.

## The more interesting axis: description cost of the measurement map

Let input dimension be `D` and transmitted width be `M=16`.

A dense linear measurement map stores:

```text
M * D
```

projection coefficients.

Eight complex Gabor receivers each use four geometric scalars:

```text
8 * 4 = 32
```

geometry parameters, while still emitting 16 real measurements.

Therefore the ratio between dense projection coefficients and Gabor geometry description is

```text
(16 D) / 32 = D / 2.
```

Examples:

```text
8x8 digits:    D=64    -> 1024 dense coefficients / 32 geometry scalars = 32x
28x28 images:  D=784   -> 12544 dense coefficients / 32 geometry scalars = 392x
```

PCA additionally needs a centering mean if implemented explicitly (`+D` scalars), although that offset can sometimes be folded into a later affine stage.

At FP32 on 8x8 digits:

```text
Gabor geometry + linear head
  (32 + 170) * 4 bytes = 808 B

PCA matrix + explicit mean + linear head
  (1024 + 64 + 170) * 4 bytes = 5032 B
```

This is now the sharper positive observation:

> **A compact geometrically parameterized measurement map can approach the quality of a much more richly described dense projection.**

This is a map-description/storage claim, not yet a scaling law.

## FLOPs: the 6.5x parameter headline does not survive unchanged

If the Gabor filters are materialized digitally at inference, both a Gabor map and a dense PCA map still compute 16 dot products over `D` input values.

For `D=64`:

```text
measurement projection             16 * 64 = 1024 MACs
```

Learned Gabor + linear decoder:

```text
projection                         1024 MACs
16 -> 10 linear head                160 MACs
--------------------------------------------
total                              1184 MACs
```

Fixed Gate-6 receiver + H=48 decoder:

```text
projection                         1024 MACs
16 -> 48                            768 MACs
48 -> 10                            480 MACs
--------------------------------------------
total                              2272 MACs
```

Ignoring activation-function cost, that is about `1.9x`, not the `~6.5x` suggested by trainable-parameter count.

Therefore Gate 6 should **not** be sold as a 6.5x compute reduction.

If the measurement is implemented physically or by specialized structured kernels, the compute accounting changes and must be measured rather than inferred from parameter count.

## Egress bytes

Gate 6 fixed transmitted width by construction:

```text
16 FP32 measurements = 64 bytes per sample
```

for all constrained arms.

So Gate 6 contains **no egress-bandwidth win** between learned Gabor, PCA, DCT, or frozen Gabor arms. It compares what happens *behind the same 16-value boundary*.

This is where `SpectralNeuron` becomes relevant: its multiplexing experiment explicitly studies interference/crosstalk when several selective channels share one physical medium. See `SPECTRALNEURON_RELATION.md`.

## Stronger scaling prediction

The compact-map hypothesis predicts something specific:

```text
structured map description per receiver   O(1)
dense unstructured map description        O(D)
```

Thus the storage/description advantage should grow with input dimension.

But **accuracy and compute need not follow the same law**. The next serious scale test must measure all of:

```text
accuracy
measurement-map description bytes
materialized model bytes
projection MACs / FLOPs
wall time
activation / memory traffic
egress bytes
```

across increasing input dimension and at least one external dataset.

Possible verdicts:

```text
accuracy exchange rate decays toward 1x    -> small compression note
holds while map-description ratio grows    -> useful edge/embedded design rule
grows with D while resources stay bounded  -> candidate allocation law
```

## Run

```bash
pip install -e '.[gate6]'
python experiments/gate9_measurement_map_controls.py --full
```

The script also prints the analytic resource table for `D=64` and `D=784`.
