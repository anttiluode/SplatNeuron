# SplatNeuron

> **How much description, compute, communication, and selectivity does a useful observation map require?**

SplatNeuron began as “splats as neurons.” Strong controls killed most of that story. The live project is now an **observer resource frontier**: how a rich input is reduced to a small set of consequences, how compactly that observation map can be described, how much downstream decoding it requires, and what happens when those consequences must share a physical medium.

No novelty, neuroscience, frequency-coding, or hardware claim is currently made.

## Current ledger

```text
Smoke 0    WAIT/ROUTE plumbing                       original WAIT null constructed
Smoke 1    online branch growth                      fixed plastic capacity wins
Gate 2     continuous ROUTE                          address cache survives
Gate 3/4   adaptive admission                        strong fixed policies survive
Gate 5     Gabor-specific ROUTE                      generic smooth manifold reproduces it
Gate 6     learned vs random-frozen receiver         large small-budget gap
Gate 7/8   mixed/pre-collapse allocation             no interior Y block
Gate 9     PCA/DCT fixed-basis attack                PCA closes Gate-6 accuracy gap
Gate 10    28x28 MNIST scale                         resource currencies split
Gate10b/c  matched compact families                  Gaussian derivatives match Gabor
Gate 11    literal map-bit rate/distortion           compact high-accuracy frontier survives
Gate 11b   same codec at D=784                       fixed family remains expressive
Gate 12    CIFAR-10 complexity attack                preregistered / running
```

The negative history is part of the result. See [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md).

# Current scientific center

The strongest statement is **not**:

> a fixed-size structured map stays O(1) while a dense map grows O(D).

That follows from choosing a fixed-parameter family versus an unstructured dense matrix.

The empirical question is:

> **How much structured observer capacity is actually sufficient to reach a common task-error target as the data/task become more complex?**

Gate 11/11b showed that the same tiny structured family remained useful from 8x8 digits to 28x28 MNIST. That is an **expressivity receipt**, not a discovered asymptotic law.

The next attack, Gate 12, moves to CIFAR-10 and allows compact observer capacity to grow. The working hypothesis is that compact observer cost should track **task/intrinsic complexity**, while a dense projection also pays explicitly for sampled input dimension.

See [`docs/GATE12_PREREG_CIFAR_COMPLEXITY.md`](docs/GATE12_PREREG_CIFAR_COMPLEXITY.md).

# Gate 9: PCA kills the original Gate-6 interpretation

Gate 6 fixed egress at 16 real measurements and found on 8x8 sklearn digits:

```text
learned Gabor + linear head           95.24%
random-frozen same Gabor + H7 MLP     89.76%
```

But the frozen map was random. Gate 9 adds strong fixed bases on the same eight split IDs:

```text
PCA-16 + linear       95.42%
learned Gabor         95.24%
DCT-16 + linear       92.85%
```

Paired PCA-minus-Gabor:

```text
+0.17 percentage points
95% bootstrap CI [-0.87,+1.15]
```

So PCA and learned Gabor are not separated. Gate 6 does **not** establish that task-trained sensing beats a good fixed 16-channel basis.

# Gate 10: the resource currencies split

Move the same 32-scalar compact map from `D=64` to real 28x28 MNIST (`D=784`). Frozen two-seed means:

```text
learned compact Gabor          88.33%
PCA-16                         85.23%
DCT-16                         83.39%
random compact Gabor + H7      85.95%
random compact Gabor + H48     91.58%
full 784 pixels + linear       90.82%
```

Different resource currencies move in different directions:

```text
nominal dense/compact map-description ratio
    32x at D=64  ->  392x at D=784          UP

matched tiny-decoder advantage
    +5.49 points -> +2.38 points             DOWN

generic dense digital MAC ratio
    ~1.92x -> ~1.086x                        DOWN toward 1

logical egress
    16 -> 16                                  FLAT
```

This table is more important than any single ratio. There is no valid scalar called “the efficiency gain.”

# Gate 10c: frequency is not the mechanism

A matched nonoscillatory family closes the Gabor gap on MNIST:

```text
same 32 map scalars
same 16 outputs
same linear head

learned Gabor                         88.33%
steerable Gaussian derivatives        88.56%
```

The derivative map learns `(x,y,scale,orientation)` and emits first/second directional Gaussian derivatives. It has no sinusoidal carrier, learned frequency, or phase.

```text
GABOR_OR_FREQUENCY_SPECIFIC_KEEP = False
```

What survives is compact structured localized selectivity, not oscillation.

# Gate 11: literal observation-map bits

Gate 11 literally bit-packed post-training observation-map values. The linear decoder stayed frozen; no per-rate retraining was allowed.

Fresh 8x8 means:

```text
Gabor                   94.13%
Gaussian derivative     94.03%
PCA-16                  93.92%
DCT-16                  90.73%
```

The old report used “within one percentage point of each family's own full precision” as a useful diagnostic:

```text
Gabor                   24 B
Gaussian derivative     24 B
PCA-16                 576 B
DCT-16                   0 B
```

That is **not iso-accuracy** and should not be the publication headline. Gate 12 switches to common validation-defined error targets and held-out test reporting.

One robust qualitative finding remains: compact geometry is more brittle per coordinate at 2–3 bits. It wins by having **few high-leverage values**, not unusually robust values.

# Gate 11b: what actually survived the resolution increase

With the same frozen codec on fresh 28x28 MNIST seeds:

```text
full means
compact Gabor             88.99%
compact Gaussian deriv.   88.39%
PCA-16                    86.03%
DCT-16                    83.94%
```

For the same within-own-ceiling diagnostic:

```text
                         D=64          D=784
compact useful map        24 B           24 B
PCA useful map           576 B         4768 B
```

The arithmetic growth of the ratio is not surprising by itself: fixed-P structured descriptions do not grow with D while dense coefficient arrays do.

What could have failed, but did not on MNIST, is that **32 structured geometry values remained enough to retain useful task performance at the higher sampling resolution.**

That is the result Gate 12 now attacks on natural images.

# Gate 12: common-error / intrinsic-complexity attack

Gate 12 is frozen before results.

Dataset:

```text
CIFAR-10 -> fixed grayscale luminance
32 x 32, D=1024
12k train / 3k validation / 10k standard test
fresh seeds 9300, 9301
```

Capacity sweep:

```text
M = 16, 32, 64, 128 logical outputs
structured derivative map = 2M geometry values
PCA-M
DCT-M
full-pixel linear reference
```

Common targets are defined from the full-pixel **validation** reference:

```text
T95 = 0.95 * full-pixel validation accuracy
T90 = 0.90 * full-pixel validation accuracy
```

Configurations are selected using validation only and then reported on the untouched standard test set.

For each target report separately:

```text
map payload bytes
linear-head bytes
total explicit state
logical egress M
test accuracy
```

The preregistered attack is specifically aimed at the old 24-byte setting:

```text
M=16
32 geometry values
6 bits/value
24 map bytes
```

If it still reaches T95 on CIFAR-10, that is a genuinely stronger expressivity result. If compact capacity must grow, record the required bytes/channels. If nothing through M=128 reaches T90, the current compact family fails the task.

# Why SpectralNeuron belongs on the same ladder

[`anttiluode/SpectralNeuron`](https://github.com/anttiluode/SpectralNeuron) probes the next resource after logical observation.

Its resonant forks versus total-energy bucket are ordinary frequency-division/selectivity experiments, but they expose something Gates 6-12 mostly idealize away:

> **logical consequences interfere when they must share a physical medium.**

The combined pipeline is:

```text
rich input x
    -> observation map C_theta
    -> M logical consequences z
    -> shared physical channel H
    -> receiver/demultiplexer R
    -> recovered consequences
    -> decoder g_phi
    -> task
```

A bridge that merely compares FDM with a bad mixer would rediscover communications theory. The interesting coupling question is narrower:

> **Can spending description budget in C_theta make the exported consequences more separable on a constrained carrier?**

Any such bridge needs matched generic linear/code-division attackers and must name the MIMO/channel-capacity literature explicitly.

# Prior-art boundary

The broad ingredients are occupied:

```text
learned sensing matrices                old
structured replacements for dense maps  old
compact parameterized filters           old
post-training quantization               old
bit-depth scaling laws                   old
FDM / shared-channel demultiplexing      old
```

The current candidate contribution, if it survives, is a **measurement protocol / worked resource frontier**: common task-error targets, literal packed operator bytes, and separate accounting of map description, materialized compute/storage, logical egress, carrier interference and decoder cost.

See [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) and [`docs/PRIOR_ART_OBSERVER_RATE.md`](docs/PRIOR_ART_OBSERVER_RATE.md).

# What is still not earned

```text
online branch growth                no
adaptive admission                  no
Gabor/frequency-specific mechanism  no
interior pre-collapse Y block       no
learned observer > good fixed PCA   no on 8x8 Gate 9
universal compact-map scaling law   no
FLOP scaling from map compression   no
egress-bandwidth reduction          no
physical energy/hardware benefit    no
novel structured-matrix idea        no
```

# Run

```bash
python -m pip install -e .
python -m unittest discover -s tests -v

pip install -e '.[gate6]'
python experiments/gate9_measurement_map_controls.py --full
python experiments/gate11_map_rate_distortion.py --full

pip install -e '.[scale]'
python experiments/gate10_mnist_scale_v2.py --download
python experiments/gate10c_gaussian_derivative.py --download
python experiments/gate11b_mnist_map_rate.py --download
python experiments/gate12_cifar_complexity_rate.py --download
```
