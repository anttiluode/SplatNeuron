# Gate 10 — MNIST scale: different resource currencies obey different laws

Date: 2026-08-17

Status: **KEEP as a two-seed cross-scale receipt, not yet a general scaling law.**

## Why Gate 10 exists

Gate 9 changed the interpretation of Gate 6.

On 8x8 sklearn digits, PCA-16 essentially tied the learned 32-scalar Gabor measurement map:

```text
learned Gabor + linear   95.24%
PCA-16 + linear          95.42%
DCT-16 + linear          92.85%
```

The compact-map hypothesis then made a concrete scale prediction:

```text
structured map description      O(1) per receiver
dense linear map description    O(D) per output channel
```

At fixed 16-value egress, increasing input dimension from `D=64` to `D=784` changes the dense/Gabor map-description ratio from:

```text
32x  ->  392x
```

What was unknown was whether the *useful accuracy/decoder exchange rate* would also improve.

## Frozen MNIST protocol

Real 28x28 MNIST:

```text
D                 784
training subset   6000
validation        1000
test              5000
seeds             9100, 9101
batch             256
epochs            80
Adam LR           .02
```

Every constrained measurement arm emits exactly:

```text
M = 16 real values
```

The compact learned map remains:

```text
8 complex Gabor receivers
4 geometry scalars each: x,y,frequency,orientation
32 map-description / trainable geometry scalars total
+ 170-parameter linear ten-class head
= 202 trainable parameters
```

No geometry parameter count was increased when image dimension grew from 64 to 784.

Controls:

```text
PCA-16 + linear
DCT-16 + linear
same random compact Gabor map + H7 MLP
same random compact Gabor map + H48 MLP
full 784-pixel linear classifier
```

The first Actions run failed only because non-cloned `torch.meshgrid` buffers could not be restored by `load_state_dict`. The rerun changed only that plumbing detail and CPU installation; all scientific settings remained frozen.

## Result

```text
                           seed 9100   seed 9101    mean
--------------------------------------------------------
learned compact Gabor        88.66%      88.00%     88.33%
PCA-16                       85.32%      85.14%     85.23%
DCT-16                       83.46%      83.32%     83.39%
random Gabor + H7            86.30%      85.60%     85.95%
random Gabor + H48           91.98%      91.18%     91.58%
full 784 pixels + linear     90.54%      91.10%     90.82%
```

The two seeds are strikingly consistent, but `n=2` is far too small for a serious uncertainty claim. Treat the differences below as observed receipts, not population estimates.

## Result 1 — compact map versus PCA improves on this scale test

Mean:

```text
learned compact Gabor   88.33%
PCA-16                  85.23%
------------------------------
delta                   +3.10 percentage points
```

At 8x8, PCA and learned Gabor were statistically indistinguishable. At 28x28, the two frozen seeds both favor the compact task-trained map by about three points.

Meanwhile the explicit measurement-map descriptions are:

```text
Gabor geometry            32 scalars
PCA projection         12544 coefficients
```

or:

```text
392x map-description ratio
```

Including a stored PCA centering mean and the common linear head at FP32:

```text
Gabor geometry + head          808 B
PCA matrix + mean + head     53992 B
```

roughly `66.8x` total explicit stored state at these representations.

Supported narrow statement:

> **In this two-seed MNIST scale test, a 32-scalar task-trained geometric measurement map outperformed PCA-16 while the dense PCA map required 12,544 stored projection coefficients.**

This is promising evidence for a description-quality frontier, not a claim that Gabors are uniquely optimal.

## Result 2 — the original receiver-vs-decoder advantage shrinks

Original 8x8 Gate 6 matched-budget contrast:

```text
learned compact + linear      95.24%
random compact + H7           89.76%
delta                         +5.49 points
```

MNIST:

```text
learned compact + linear      88.33%
random compact + H7           85.95%
delta                         +2.38 points
```

So the advantage from spending the tiny trainable budget on receiver geometry rather than the H7 decoder **decays**, rather than growing, in this scale move.

## Result 3 — a larger downstream decoder wins

MNIST:

```text
random compact Gabor + H48     91.58%
learned compact + linear       88.33%
------------------------------------
H48 advantage                  +3.25 points
```

The receiver-heavy endpoint is therefore not the best accuracy allocation at this scale.

This reverses the small 8x8 shape where the learned 202-parameter receiver was still slightly ahead of H48 on average.

So there is no general law of:

> spend parameters in the receiver rather than downstream.

The useful allocation depends on task/scale/budget.

## Result 4 — full linear input also beats the 16-value compact bottleneck

```text
full 784 pixels + linear      90.82%
compact 16-value Gabor        88.33%
```

The fixed 16-value egress itself now has a visible task cost.

This matters for the SpectralNeuron bridge: logical channel width is a resource, not an innocent constant.

## Compute and communication accounting

All 16-value constrained arms emit:

```text
16 FP32 values = 64 bytes / sample
```

so there is no egress-width difference among Gabor/PCA/DCT/frozen-Gabor arms.

For a generic **materialized dense digital implementation**:

```text
16 * 784 = 12544 projection MACs/sample
```

Approximate totals:

```text
compact Gabor + linear     12544 + 160        = 12704 MACs
fixed Gabor + H48          12544 + 768 + 480  = 13792 MACs
```

Ratio:

```text
13792 / 12704 ~= 1.086x
```

So the digital compute advantage has nearly vanished even while the map-description advantage grew from `32x` to `392x`.

This is the most important scaling correction:

```text
map-description advantage       GROWS with D
dense digital MAC advantage     SHRINKS toward 1x
matched tiny-decoder advantage  SHRINKS in observed accuracy
```

There is no single valid number called "the efficiency gain."

## What Gate 10 supports

The strongest current statement is:

> **A compact structured observation map can occupy a useful description-quality point that becomes increasingly cheap to specify relative to a dense map as input dimension grows, even though its advantage in ordinary dense digital compute and in receiver-vs-decoder parameter allocation need not grow with it.**

This is substantially narrower than 'computation moved into observation is more efficient'.

## Mandatory next attackers

Before claiming a Gabor or frequency-specific scale effect, add matched compact non-oscillatory maps with the same description budget:

```text
learned point samplers
learned Gaussian/local-average samplers
possibly another compact local structured family
```

Gate 6 already suggested learned points nearly close the Gabor gap on 8x8. Gate 10b should ask whether receptive *shape* matters when D=784.

Also retain:

```text
DCT / analytic low-description basis
PCA / strong dense unsupervised basis
large decoder behind fixed compact map
```

## SpectralNeuron bridge

Gate 10 makes the bridge more concrete:

- SplatNeuron shows a 16-logical-value bottleneck has an accuracy/resource tradeoff.
- SpectralNeuron shows several logical selective channels sharing one physical carrier have finite crosstalk.

The next combined frontier should therefore vary logical width `M`, physical carrier width/interference, observation-map description, and decoder cost jointly rather than treating `M=16` as free.

See [`SPECTRALNEURON_RELATION.md`](SPECTRALNEURON_RELATION.md) and [`OBSERVER_RESOURCE_FRONTIER.md`](OBSERVER_RESOURCE_FRONTIER.md).

## Reproduce

```bash
pip install -e '.[scale]'
python experiments/gate10_mnist_scale_v2.py --download
```

The frozen two-seed run was also executed successfully in GitHub Actions.
