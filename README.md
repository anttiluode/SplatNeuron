# SplatNeuron

> **How much description, compute, communication, and selectivity does a useful observation map require?**

SplatNeuron began as “splats as neurons.” Strong controls killed most of that story. The live project is now an **observer resource frontier**: how a rich input is reduced to a small set of consequences, how compactly that observation map can be described, how much downstream decoding it requires, and what happens when those consequences must share a physical medium.

No novelty, neuroscience, frequency-coding, or hardware claim is currently made.

## Ledger

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
```

The negative history is part of the result. See [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md).

## Gate 9: the missing PCA control changed Gate 6

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

What remained interesting was the map description:

```text
dense 16-channel map       16 * D coefficients
8 compact receivers        32 geometry scalars
ratio                       D / 2
```

At 8x8 (`D=64`): `32x` map-only description ratio.

See [`docs/GATE9_MEASUREMENT_MAP_CONTROLS.md`](docs/GATE9_MEASUREMENT_MAP_CONTROLS.md).

## Gate 10: scaling to 28x28 gives different answers in different currencies

The same compact receiver budget was moved to real MNIST without increasing its geometry parameter count:

```text
D                    784
logical outputs       16 real values
compact map           32 geometry scalars
seeds                 9100, 9101
```

Frozen two-seed result:

```text
                           mean accuracy
----------------------------------------
learned compact Gabor          88.33%
PCA-16                         85.23%
DCT-16                         83.39%
random compact Gabor + H7      85.95%
random compact Gabor + H48     91.58%
full 784 pixels + linear       90.82%
```

Three resource trends separate:

```text
map-description advantage
    32x at D=64  ->  392x at D=784          GROWS

matched tiny-decoder advantage
    +5.49 points -> +2.38 points             SHRINKS

generic dense digital MAC ratio
    ~1.92x -> ~1.086x                        COLLAPSES TOWARD 1
```

At `D=784`, PCA stores `12,544` projection coefficients while the compact map uses 32 geometry scalars. Including an explicit PCA mean and the common linear head at FP32:

```text
compact geometry + head       808 B
PCA map + mean + head       53992 B
```

But if both are materialized as dense digital filters, both still pay the common `16*784 = 12,544` projection MACs. **Description compression is not automatically compute compression.**

See [`docs/GATE10_MNIST_SCALE.md`](docs/GATE10_MNIST_SCALE.md).

## Gate 10b/c: frequency does not earn the scale result

Simple nonoscillatory compact maps initially lost:

```text
learned points                79.84%
Gaussian pair, best width     85.27%
Gabor                         88.33%
```

That might tempt a frequency story. A stronger matched nonoscillatory attacker kills it:

```text
8 steerable Gaussian-derivative branches
(x,y,scale,orientation)       32 map scalars
first + second derivatives    16 outputs
linear head                   same 170 params

Gaussian derivative           88.56%
Gabor                         88.33%
```

Two frozen seeds agree. The tiny difference is not a superiority claim; it is a falsification:

```text
GABOR_OR_FREQUENCY_SPECIFIC_KEEP = False
```

The surviving object is **compact structured localized selectivity**, not oscillation.

See [`docs/GATE10BC_COMPACT_FAMILY_ATTACKERS.md`](docs/GATE10BC_COMPACT_FAMILY_ATTACKERS.md).

## SpectralNeuron really does belong here — one rung lower

[`anttiluode/SpectralNeuron`](https://github.com/anttiluode/SpectralNeuron) asks a complementary question.

Its bucket collapses a waveform to total power; its resonant forks preserve selective channels. With three modulated carriers on one shared noisy wire, forks achieved about `3.1x` self/crosstalk separation versus `1.0x` for the bucket, with finite off-diagonal leakage.

That is ordinary frequency-division multiplexing in neuron-flavoured primitives. Its value here is that it exposes a resource Gate 6/9/10 fixed by fiat:

> **logical channels sharing one physical medium interfere.**

So the common pipeline is:

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

SplatNeuron has mostly studied the cost/quality of `C_theta` and `g_phi` while pretending `H=I`. SpectralNeuron studies selective `H/R` under crosstalk.

The common principle is **selectivity under resource constraints**, not “thought is frequency.”

See [`docs/SPECTRALNEURON_RELATION.md`](docs/SPECTRALNEURON_RELATION.md) and [`docs/OBSERVER_RESOURCE_FRONTIER.md`](docs/OBSERVER_RESOURCE_FRONTIER.md).

## Next: Gate 11 should measure description *bits*, not float counts

`32 geometry scalars versus 12,544 PCA coefficients` is still only a proxy for description length.

Both maps can be quantized or compressed. DCT is largely algorithmic. A serious next gate should therefore measure a rate-distortion curve for the observation operator itself:

```text
bits needed to serialize C
        versus
task accuracy after quantization/compression
```

For each map family report separately:

```text
map-description bits
materialized storage
projection MACs / FLOPs
wall time / memory traffic
logical egress width and bytes
physical-channel/crosstalk cost when present
downstream decoder state and compute
```

Do not collapse these into one number called “efficiency.” Gate 10 already shows they scale differently.

## Run

```bash
python -m pip install -e .
python -m unittest discover -s tests -v

pip install -e '.[gate6]'
python experiments/gate6_receiver_frontier.py --full
python experiments/gate9_measurement_map_controls.py --full

pip install -e '.[scale]'
python experiments/gate10_mnist_scale_v2.py --download
python experiments/gate10b_compact_family.py --download
python experiments/gate10c_gaussian_derivative.py --download
```

See [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) for occupied territory around compact learnable front ends and task-driven sensing.
