# Gate 6 — learned receiver vs decoder frontier

Date: 2026-08-17

Status: **useful receiver-vs-decoder experiment, but its original interpretation is superseded by Gate 9.**

> **Important correction:** Gate 6's fixed structured receiver started from random Gabor geometry. Gate 9 adds strong fixed PCA/DCT bases. PCA-16 essentially closes the learned-Gabor accuracy gap. Therefore Gate 6 does **not** establish that task-trained observation geometry beats a good fixed 16-channel basis. Read [`GATE9_MEASUREMENT_MAP_CONTROLS.md`](GATE9_MEASUREMENT_MAP_CONTROLS.md) before quoting this gate.

## Question originally tested

The routing work progressively killed three stronger stories:

- online branch growth was unnecessary once fixed capacity was controlled;
- adaptive admission did not beat strong fixed policies;
- the cache↔ROUTE phase was reproduced by a generic smooth manifold, so it was not Gabor-specific.

Gate 6 then asked:

> **Can moving a small trainable budget into the observation map make the downstream classifier much simpler than leaving a randomly initialized structured map frozen?**

That narrower question still has a clear positive answer.

## Fixed communication width

Every constrained model receives exactly **16 real measurements** from the image.

The learned Gabor receiver has eight complex filters, each emitting real and imaginary responses:

```text
8 complex receivers -> 16 real channels
```

Each receiver learns four geometry parameters:

```text
(x, y, frequency, orientation)
```

with fixed envelope width. Receiver geometry therefore contributes only `8 x 4 = 32` trainable scalars.

A linear ten-class decoder has `16 x 10 + 10 = 170` parameters, giving:

```text
learned receiver + linear head = 202 trainable parameters
```

## Original matched downstream-state attacker

For each split the fixed-Gabor models start from **the exact same random initial receiver geometry** as the learned-Gabor model, but receiver coordinates are frozen.

The matched-budget attacker spends its trainable parameters downstream:

```text
16 measurements -> hidden MLP -> 10 classes
```

At hidden width `H=7` it has `199` trainable parameters, essentially identical to the learned-receiver model's `202`.

## Deterministic result

Eight stratified splits (`6000..6007`):

```text
learned Gabor receivers + linear       202 params    95.24%
fixed same random Gabor + H=7 MLP      199 params    89.76%
```

Paired learned-minus-fixed:

```text
+5.49 percentage points
95% bootstrap CI [+3.40,+7.15]
```

This says **learning substantially repairs a poor random structured observation map more efficiently than a tiny matched-budget decoder does**.

It does not say the learned map is uniquely good.

## Same-family geometry controls

On the first four splits:

```text
learned point geometry + linear       92.64%
fixed same point geometry + MLP       85.35%

learned Gaussian-pair geometry        90.83%
fixed same Gaussian-pair + MLP        84.10%
```

So the random-frozen-versus-learned effect occurs in several receiver families and is not uniquely Gabor.

## Fixed observation did not destroy the information

Keep the same frozen 16 random-Gabor measurements and increase only decoder capacity:

```text
hidden H   trainable params   mean accuracy over 8 splits
---------------------------------------------------------
7               199                    89.76%
24              658                    92.85%
32              874                    93.61%
40             1090                    93.99%
48             1306                    94.31%
```

The learned-receiver model remains:

```text
202 params      95.24%
```

Paired learned-minus-fixed frontier:

```text
fixed H=7    (199 params)    +5.49 points   95% CI [+3.40,+7.15]
fixed H=24   (658 params)    +2.40 points   CI [+1.11,+3.68]
fixed H=32   (874 params)    +1.63 points   CI [+0.49,+2.71]
fixed H=40  (1090 params)    +1.25 points   CI [+0.31,+2.19]
fixed H=48  (1306 params)    +0.94 points   CI [-0.07,+1.94]
```

A validation-selected RBF-SVM on the same frozen features also reached about `95%` on the first four splits.

Therefore the strong information-ceiling claim was false:

> **The frozen receiver still contains enough information; it simply presents it to a small decoder in an awkward coordinate system.**

## Gate 9 fixed-basis attack

Gate 6 omitted the load-bearing representation baseline: a **good fixed 16-channel basis**.

Gate 9's independent deterministic run on the same split IDs gives approximately:

```text
PCA-16 + linear      95.42%
DCT-16 + linear      92.85%
learned Gabor        95.24%   (this gate's reported mean)
```

PCA therefore essentially closes the accuracy gap.

The repo should no longer summarize Gate 6 as:

> task-aligned receiver learning makes the downstream map uniquely cheap.

The defensible summary is:

> **A compact trainable structured map can repair a bad low-width representation with very few trainable scalars, but a strong unsupervised fixed subspace can already be just as good on this task.**

That redirects the interesting question from *learned versus fixed* toward **measurement-map description cost**.

## Parameter count is not compute

The earlier `202` versus `~1306` parameter comparison should not be read as `~6.5x` inference compute.

For a generic digital implementation at `D=64`, both systems first pay `16*64 = 1024` projection MACs.

Approximate totals:

```text
learned Gabor + linear      1024 + 160             = 1184 MACs
fixed Gabor + H48           1024 + 16*48 + 48*10  = 2272 MACs
```

So the simple MAC ratio is about `1.9x`, not `6.5x`.

All constrained arms also emit the same 16 FP32 measurements = `64 bytes/sample`, so Gate 6 contains no egress-width advantage.

## What remains useful about Gate 6

Gate 6 still supplies a controlled **receiver-vs-decoder allocation curve** behind a deliberately narrow communication boundary. It showed:

```text
poor observation coordinates + tiny decoder   -> bad
same poor coordinates + large decoder         -> recoverable
compact trainable observation map + tiny head  -> good
```

Gate 9 adds:

```text
good fixed dense subspace + tiny head          -> also good
```

Together the live question is:

> **How much map description/storage and downstream compute are needed to produce a useful low-width consequence?**

## Important limitations

- `sklearn` digits is small and 8x8.
- PCA-16 is now a stronger accuracy baseline than the random-frozen receiver family.
- Gabor-specific superiority is not established.
- trainable parameter count does not measure MACs, memory traffic, wall time, energy, or physical sensing cost.
- all current 16-channel arms fix egress width by construction.
- task-driven/learnable front ends and sensor co-design are established prior art.

## Next test

The compact-parameterization argument predicts a scaling law in **map description cost**:

```text
structured map description      O(1) per receiver
dense linear map                O(D) per output channel
```

At fixed 16-channel output, the dense/Gabor description ratio is `D/2`: `32x` at 8x8 and `392x` at 28x28.

The next external-scale experiment must ask whether useful accuracy/compute efficiency holds or grows as that description ratio grows.
