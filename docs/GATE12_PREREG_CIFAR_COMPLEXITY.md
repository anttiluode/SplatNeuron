# Gate 12 preregistration — CIFAR-10 intrinsic-complexity attack

Date: 2026-08-17

Status: **FROZEN BEFORE RESULTS.**

## Why this gate exists

Gate 11/11b showed that a compact 32-value observation map could be quantized to 24 map bytes and retain near-full accuracy on both 8x8 sklearn digits and 28x28 MNIST, while a dense PCA-16 map required more coefficients as input dimension grew.

That is not, by itself, a discovered scaling law. A fixed-size parametric family has `O(P)` description length by construction, while a dense `M x D` map has `O(MD)` coefficients. The arithmetic ratio therefore grows with `D` whether or not the compact family is scientifically interesting.

The empirical question is instead:

> **Does a fixed-size structured observation family remain expressive enough as task structure becomes genuinely more complex, and if not, how much observer description / logical width must be added to recover a fixed task-error target?**

The working hypothesis is therefore:

> **Compact observer cost should track task/intrinsic complexity more than raw sampled input dimension.**

Gate 12 deliberately switches away from centered stroke digits to CIFAR-10 natural images.

## Dataset and preprocessing

Use torchvision CIFAR-10.

To keep the first non-digit gate cheap and remove a free learned color model, convert RGB to a fixed algorithmic luminance channel:

```text
Y = 0.299 R + 0.587 G + 0.114 B
```

Images are therefore `32 x 32`, `D=1024`.

The task is still materially different from MNIST: natural backgrounds, textures, pose, object shape and intra-class variability.

Per seed:

```text
train subset       12,000
validation          3,000
standard test      10,000
fresh seeds         9300, 9301
```

Train/validation subsets are stratified and deterministic from the 50k CIFAR training set.

A single training-set scalar mean/std normalization is common to every arm. It is preprocessing, not charged to one observation family.

## Observation capacities

Sweep logical width:

```text
M in {16, 32, 64, 128}
```

The compact primary family is the nonoscillatory steerable Gaussian-derivative map from Gate 10c/11:

```text
one branch = (x, y, scale, orientation) = 4 normalized geometry values
one branch emits 2 real measurements = odd/even directional derivatives
branches = M / 2
compact map values = 2M
```

Thus compact map-value count is:

```text
M=16     32 values
M=32     64 values
M=64    128 values
M=128   256 values
```

No Gabor/frequency claim is tested here.

## Attackers

At each `M`, compare:

```text
structured derivative map + linear head
PCA-M + linear head
DCT-M + linear head
```

Also train a full `D=1024 -> 10` linear classifier as a task reference only.

PCA is fitted only on the training subset. Its centering mean is absorbed into the linear-head bias before map quantization, as in Gate 11.

DCT is a data-free 2-D DCT-II zig-zag basis and is charged **zero learned map payload**. Its logical width and decoder state are still reported.

## Training and quantization

Frozen settings:

```text
batch                 256
epochs                  60
Adam LR               0.02
validation checkpoint every 5 epochs
```

For every learned/fitted map:

1. train/fix the full-precision observation map and linear head;
2. freeze the head;
3. post-training quantize **only the observation map**;
4. never retrain or fine-tune per bit depth.

Use the exact Gate-11 bit depths:

```text
2, 3, 4, 6, 8, 12, 16 bits/value
```

Compact normalized coordinates use the exact Gate-11 fixed-width bit packer.

PCA uses the exact Gate-11 per-row symmetric codec:

```text
one FP32 max-abs scale per PCA row
+
fixed-width packed coefficients
```

No entropy coding, vector quantization or learned codec is introduced in this gate.

## Fixed-error targets — primary reporting rule

Gate 11's `within 1 point of each family's own ceiling` is not iso-accuracy and must no longer be the headline comparison.

For each seed, first obtain the full-pixel linear validation accuracy `A_full,val`.

Preregister two common targets:

```text
primary target     T95 = 0.95 * A_full,val
secondary target   T90 = 0.90 * A_full,val
```

For every family, select configurations using **validation only**.

Report on the held-out standard test set:

```text
selected M
selected bit depth
map payload bytes
linear-head bytes
total explicit state bytes
logical egress M
test accuracy
full-pixel test accuracy
whether the selected test accuracy also reaches 95% / 90% of the full-pixel test reference
```

Because map bytes, egress width and decoder bytes are different currencies, do not collapse them into one efficiency number.

For each target, report at least:

1. minimum map-payload configuration reaching the validation target;
2. minimum total-state configuration reaching the validation target;
3. minimum logical width reaching the validation target.

DCT may therefore own the zero-map-payload corner while paying in `M` / head state.

## Load-bearing prediction / kill conditions

The old 24-byte result is **not** predicted to remain enough automatically.

### Prediction A — 24-byte M=16 should be attacked

Gate-11-style compact setting:

```text
M=16
32 geometry values
6 bits/value
24 map bytes
```

is expected **not** to reach `T95` on CIFAR-10.

If it does reach `T95`, that is a stronger-than-expected expressivity result and must be reported without changing the gate.

### Prediction B — compact cost should rise with task complexity

If the compact family remains useful, the expected shape is that a larger `M` and therefore a larger packed map is required on CIFAR-10 than the 24-byte digit result.

A plausible outcome is tens to a few hundred map bytes, not a fixed 24-byte law.

### Kill — compact family fails the task

If no compact configuration through `M=128` reaches `T90`, stop calling the current four-coordinate derivative family a generally useful observation map. Record an expressivity failure.

### Kill — dense / analytic attacker owns the target frontier

If PCA or DCT reaches the same common target with a resource vector that dominates the compact family (map bytes, egress, decoder state), the compact-description claim loses on this task.

## Why this is stronger than another resolution test

`8x8 digits -> 28x28 MNIST` changed sampled dimensionality much more than semantic task complexity.

Gate 12 changes the data distribution and visual structure. The quantity of interest is not whether the compact parameter count is mathematically independent of `D`; that is true by construction.

The quantity of interest is:

> **How much structured observer capacity is empirically required to preserve a fixed fraction of useful task performance?**

If compact cost rises with natural-image complexity while staying far below a dense projection's coefficient payload, the defensible statement becomes:

> **Structured observers pay primarily for the complexity their family must express, whereas an unstructured dense map also pays explicitly for sampled input dimension.**

That is a hypothesis to test, not a conclusion of this preregistration.

## Stop lines

- Do not alter `M`, bit depths, codecs, targets or preprocessing after seeing results.
- Do not add color parameters if grayscale hurts; that would be a new gate.
- Do not compare families at their own ceilings as the headline.
- Do not infer a universal scaling exponent from one CIFAR test.
- Do not resurrect frequency/Gabor language.
