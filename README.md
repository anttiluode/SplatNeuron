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
Gate 11b   same codec at D=784                       description-rate advantage scales
```

The negative history is part of the result. See [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md).

# The strongest current result

The surviving claim is not “neurons should be Gabors” and not “move computation into observation.” Those ideas are too broad or already occupied.

The current receipt is narrower:

> **A compact structured observation map can retain useful task performance with a serialized description whose size stays nearly constant as input dimension grows, while a dense fitted projection requires a description that grows with input dimension.**

The critical point is that this is about **observer description rate**. It is not automatically a projection-FLOP, wall-time, RAM, energy, or physical-egress advantage.

## Gate 9: PCA kills the original Gate-6 interpretation

Gate 6 fixed egress at **16 real measurements** and found on 8x8 sklearn digits:

```text
learned Gabor + linear head           202 trainable params   95.24%
random-frozen same Gabor + H7 MLP     199 trainable params   89.76%
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

See [`docs/GATE9_MEASUREMENT_MAP_CONTROLS.md`](docs/GATE9_MEASUREMENT_MAP_CONTROLS.md).

## Gate 10: different resource currencies scale differently

The same 32-scalar compact receiver budget was moved from `D=64` to real 28x28 MNIST (`D=784`) without increasing geometry parameter count.

Frozen two-seed means:

```text
learned compact Gabor          88.33%
PCA-16                         85.23%
DCT-16                         83.39%
random compact Gabor + H7      85.95%
random compact Gabor + H48     91.58%
full 784 pixels + linear       90.82%
```

Three resource trends immediately separate:

```text
nominal dense/compact map-description ratio
    32x at D=64  ->  392x at D=784          GROWS

matched tiny-decoder advantage
    +5.49 points -> +2.38 points             SHRINKS

generic dense digital MAC ratio
    ~1.92x -> ~1.086x                        COLLAPSES TOWARD 1
```

There is no single valid number called “the efficiency gain.”

See [`docs/GATE10_MNIST_SCALE.md`](docs/GATE10_MNIST_SCALE.md).

## Gate 10b/c: frequency does not earn the result

Simple nonoscillatory compact maps initially lagged the Gabor on MNIST, but a stronger matched family closes the gap:

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

What survives is **compact structured localized selectivity**, not oscillation.

See [`docs/GATE10BC_COMPACT_FAMILY_ATTACKERS.md`](docs/GATE10BC_COMPACT_FAMILY_ATTACKERS.md).

# Gate 11: literal observation-map bits

Counting 32 geometry floats versus 1024 PCA coefficients was still only a proxy for description length. Gate 11 was preregistered before results and literally bit-packed post-training map values.

Fresh 8x8 split IDs `7200..7207`, same 16-value logical interface, same 680-byte FP32 linear head, no per-rate retraining.

Full accuracies:

```text
Gabor                   94.13%
Gaussian derivative     94.03%
PCA-16                  93.92%
DCT-16                  90.73%
```

Smallest map payload within one percentage point of each family's own full precision:

```text
Gabor                   24 B   6 bits/value   94.10%
Gaussian derivative     24 B   6 bits/value   93.68%
PCA-16                 576 B   4 bits/value   93.65%
DCT-16                   0 B   algorithmic    90.73%
```

So at the high-accuracy part of this task:

```text
PCA / compact map payload     576 / 24 = 24x
```

But the common head reduces the total deployment-state ratio:

```text
compact   24 + 680 = 704 B
PCA      576 + 680 = 1256 B
ratio                 1.78x
```

DCT correctly owns the zero-map-payload / lower-accuracy corner. At roughly `90.7%`, no learned map description is needed at all under the shared analytic-DCT protocol.

Also, compact geometry is **more brittle per value** at 2–3 bits. Its win comes from having very few high-leverage values, not from those values being individually robust.

See [`docs/GATE11_RATE_DISTORTION_RESULT.md`](docs/GATE11_RATE_DISTORTION_RESULT.md).

# Gate 11b: the bit-rate advantage scales

Gate 11b froze the same codec before moving to fresh MNIST seeds `9200/9201`.

Full means:

```text
compact Gabor             88.99%
compact Gaussian deriv.   88.39%
PCA-16                    86.03%
DCT-16                    83.94%
```

Smallest map payload within one percentage point of own full precision:

```text
                         D=64 Gate11     D=784 Gate11b
-------------------------------------------------------
compact Gabor                24 B             24 B
compact Gaussian deriv.      24 B             24 B
PCA                          576 B           4768 B
DCT                            0 B              0 B
```

Input dimension increased:

```text
784 / 64 = 12.25x
```

The compact useful map payload stayed **exactly 24 bytes**.

PCA's useful payload grew:

```text
4768 / 576 = 8.28x
```

although PCA needed fewer bits per coefficient at scale (`3b` instead of `4b`). Coefficient count dominated.

The observed map-only rate ratio therefore grows from:

```text
24.0x  ->  198.7x
```

and the total observer+common-head state ratio grows from:

```text
1.78x  ->  7.74x
```

At the absolute `85%` MNIST floor:

```text
Gabor       16 map B    86.05%
Derivative  24 map B    88.10%
PCA       4768 map B    85.78%
DCT       unreached
```

This is the strongest current SplatNeuron receipt:

> **Across the preregistered 8x8 and 28x28 tests, a 32-value structured observation map retained near-full task accuracy at a constant 24-byte serialized map payload, while the preregistered row-scaled PCA-16 payload grew from 576 to 4,768 bytes.**

Important limitations remain: only two input dimensions, only two MNIST seeds, a specific fixed-rate PCA codec, digit tasks, and no claim about dense projection compute.

See [`docs/GATE11B_MNIST_RATE_RESULT.md`](docs/GATE11B_MNIST_RATE_RESULT.md).

# Why SpectralNeuron belongs on the same ladder

[`anttiluode/SpectralNeuron`](https://github.com/anttiluode/SpectralNeuron) asks the rung immediately after logical observation.

Its bucket collapses a waveform to total power; its resonant forks preserve selective channels. With three modulated carriers on one shared noisy wire, forks achieved about `3.1x` self/crosstalk separation versus `1.0x` for the bucket, with finite off-diagonal leakage.

That is ordinary frequency-division multiplexing in neuron-flavoured primitives. Its relevance is that it exposes a resource Gates 6-11 mostly fixed by fiat:

> **logical consequences sharing one physical medium interfere.**

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

SplatNeuron now has evidence about the **description rate of `C_theta`**. SpectralNeuron supplies a toy instrument for the **crosstalk cost of `H/R`**.

The common principle is selectivity under resource constraints, not “thought is frequency.”

See [`docs/SPECTRALNEURON_RELATION.md`](docs/SPECTRALNEURON_RELATION.md) and [`docs/OBSERVER_RESOURCE_FRONTIER.md`](docs/OBSERVER_RESOURCE_FRONTIER.md).

# What is still not earned

```text
online branch growth                no
adaptive admission                  no
Gabor/frequency-specific mechanism  no
interior pre-collapse Y block       no
learned observer > good fixed PCA   no on 8x8 Gate 9
FLOP scaling from map compression   no
egress-bandwidth reduction          no; logical width is fixed at 16
physical energy/hardware benefit    no
universal compression law           no
```

# Next legitimate work

The allowed next steps are now much narrower:

1. **Replicate/generalize the description-rate result** on more fresh MNIST seeds or a non-digit dataset without changing the codecs.
2. **Bridge to SpectralNeuron** by putting the 16 logical consequences through a controlled shared physical channel and measuring task error versus crosstalk / carrier budget.

Do not tune Gate-11 codecs on the same data, and do not reopen the frequency or neuron-shape stories.

## Run

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
```

See [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) for occupied territory around compact learnable front ends and task-driven sensing.
