# SplatNeuron

> **How much description, compute, and communication does a useful observation map require?**

SplatNeuron began as a speculative “splats as neurons” project. Strong controls killed most of that story. The repository is now a narrower research program about **observation-map allocation**: what should be preserved by the receiver, how compactly can that receiver be described, and how much downstream computation is required afterward?

No novelty, neuroscience, or hardware claim is currently made.

## Current ledger

```text
Smoke 0    WAIT/ROUTE plumbing                          original WAIT null constructed
Smoke 1    online branch growth                         fixed plastic capacity wins
Gate 2     continuous ROUTE                             address cache survives
Gate 3/4   adaptive admission                           strong fixed policies survive
Gate 5     Gabor-specific ROUTE                         generic smooth manifold reproduces it
Gate 6     learned receiver vs random-frozen receiver   large parameter-count gap
Gate 7/8   interior/pre-collapse allocation             no interior Y block
Gate 9     PCA/DCT fixed-basis attack                    PCA closes Gate-6 accuracy gap
```

The full negative history is preserved in [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md).

## Gate 9 changes the interpretation of Gate 6

Gate 6 fixed the transmitted width at **16 real measurements** and compared:

```text
learned Gabor receiver + linear head     202 trainable params   95.24%
random-frozen same Gabor + H7 MLP        199 trainable params   89.76%
```

Increasing the decoder behind the same frozen measurements eventually recovered the learned-receiver score around `~1306` trainable decoder parameters.

That looked like a strong receiver-vs-decoder parameter frontier.

But the frozen receiver had been initialized randomly. Gate 9 adds the missing strong fixed bases on the same eight split IDs:

```text
PCA-16 + linear      ~95.42%
DCT-16 + linear      ~92.85%
learned Gabor        ~95.24%   (Gate 6 reported mean)
```

PCA therefore **essentially closes the Gate-6 accuracy gap** without task labels selecting the measurement subspace.

So the repo should not lead with:

> learning what to observe is uniquely powerful.

A large part of Gate 6 was simply:

> **random frozen Gabors are a poor 16-channel basis.**

See [`docs/GATE9_MEASUREMENT_MAP_CONTROLS.md`](docs/GATE9_MEASUREMENT_MAP_CONTROLS.md).

## The sharper surviving axis: measurement-map description cost

Let input dimension be `D` and transmitted width be `M=16`.

A dense linear map such as PCA stores:

```text
16 * D
```

projection coefficients.

Eight complex Gabor receivers emit the same 16 real values but are described by only four geometric scalars each:

```text
8 receivers * (x, y, frequency, orientation) = 32 scalars
```

Therefore the dense-projection / geometry-description ratio is:

```text
(16 D) / 32 = D / 2
```

Examples:

```text
8x8 input     D=64      1024 / 32 = 32x
28x28 input   D=784    12544 / 32 = 392x
```

At FP32 on the current 8x8 task, counting the explicit PCA mean:

```text
Gabor geometry + linear head           808 B
PCA matrix + mean + linear head       5032 B
```

The current candidate claim is therefore not about frequency and not primarily about receiver *learning*:

> **A compact structured measurement map may approach the quality of a much more richly described unstructured projection.**

That is only a small-data receipt until the exchange rate is tested with scale.

## Parameter count was overstating compute efficiency

If Gabor filters are materialized digitally at inference, both learned Gabor and PCA still perform 16 dot products over all `D` input values.

For `D=64`:

```text
measurement projection                  1024 MACs   (both)

learned Gabor + linear head
  projection + 16->10                   1184 MACs

fixed Gabor + H48 decoder
  projection + 16->48->10               2272 MACs
```

So the old `~6.5x` trainable-parameter ratio becomes only about **1.9x in this simple MAC accounting**, before activation/generation costs.

And all Gate-6/9 constrained arms emit exactly:

```text
16 FP32 values = 64 bytes/sample
```

so there is **no egress-bandwidth win** inside Gate 6.

## Why SpectralNeuron belongs on the same ladder

[`anttiluode/SpectralNeuron`](https://github.com/anttiluode/SpectralNeuron) asks the rung immediately below this one.

Its bucket detector collapses a shared signal to total power; its resonant forks preserve selective frequency channels. At matched loud power the fork distinguishes on-band from off-band input while the bucket aliases them, and three forks sharing one noisy wire recover their own messages with about `3.1x` self/crosstalk separation versus `1.0x` for buckets.

That does **not** make frequency the general principle. It makes **selectivity under a shared-medium interference budget** explicit.

The relation is:

```text
SpectralNeuron
    how much distinction survives a shared carrier?
    -> selectivity / multiplexing / crosstalk

SplatNeuron
    how costly is the selective observation map and decoder?
    -> map description / compute / transmitted width
```

See [`docs/SPECTRALNEURON_RELATION.md`](docs/SPECTRALNEURON_RELATION.md).

## Gate 8 remains a useful null

The hoped-for pre-collapse architecture did not appear.

At fixed 16-wide carrier and roughly `~750` trainable parameters, increasing private Gabor branches and collapsing them locally produced no interior winner:

```text
B8 direct / H27            96.11%
B10 collapse / H14         94.95%
B12 collapse / H11         94.63%
B14 collapse / H8          93.84%
B16 collapse / linear      95.46%
```

```text
INTERIOR_Y_BLOCK_EARNS_KEEP = False
```

See [`docs/GATE8_PRECOLLAPSE_FRONTIER.md`](docs/GATE8_PRECOLLAPSE_FRONTIER.md).

## The next decisive test is scale

The structured-map argument makes a concrete prediction:

```text
structured receiver description      O(1) per receiver
dense unstructured map               O(D) per channel
```

The open question is whether the **useful exchange rate** follows that storage law.

Measure across increasing input dimension / an external dataset:

```text
accuracy
map-description bytes
materialized model bytes
MACs / FLOPs
wall time
memory traffic
egress bytes
```

Possible outcomes:

```text
advantage decays toward 1x
    -> small representation-compression note

accuracy holds while description ratio grows
    -> useful edge/embedded allocation heuristic

accuracy/resource advantage itself grows with D
    -> candidate allocation law worth pursuing
```

Do not add another neuron metaphor before this test.

## Run

Core synthetic history:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Learning / measurement-map experiments:

```bash
pip install -e '.[gate6]'
python experiments/gate6_receiver_frontier.py --full
python experiments/gate9_measurement_map_controls.py --full
```

See [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) for the occupied territory around learnable front ends, structured filters, and task-driven sensing.
