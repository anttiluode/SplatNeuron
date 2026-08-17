# SpectralNeuron relation — the egress/interference rung

Date: 2026-08-17

`anttiluode/SpectralNeuron` and SplatNeuron are best understood as experiments on the same object: an **observation operator** `C` that maps a richer medium into a smaller set of receiver-visible consequences.

They test different coordinates of that operator.

## SpectralNeuron: does selectivity preserve distinctions on a shared medium?

SpectralNeuron compares two integrate/fire/reset units:

```text
BUCKET   integrates total rectified energy
FORK     integrates energy near a selected resonance
```

At matched loud input power:

```text
40 Hz on-band     fork 20   bucket 21
120 Hz off-band   fork  0   bucket 20
broadband noise   fork  0   bucket 33
```

So the bucket's observation is effectively a severe collapse: many spectrally different inputs map to the same total-power consequence.

The fork preserves another coordinate of the input by being selective.

Part B then puts three modulated carriers on **one shared noisy wire**:

```text
25 Hz / 45 Hz / 75 Hz
```

and reports:

```text
fork    self-correlation ~0.62   crosstalk ~0.20   separation ~3.1x
bucket  self-correlation ~0.32   crosstalk ~0.32   separation  1.0x
```

with finite off-diagonal leakage up to about `0.34`.

This is ordinary frequency-division multiplexing expressed in neuron-flavoured primitives, not new signal-processing mathematics. But it measures something SplatNeuron Gate 6 does not:

> **selective channels sharing one carrier interfere, and the egress/channel budget has a measurable crosstalk price.**

## SplatNeuron Gate 6/9: how expensive is the observation map itself?

Gate 6 fixes output width at 16 real measurements and asks where a small trainable budget should live.

Gate 9 adds the missing strong fixed-basis controls and shifts the surviving question toward **measurement-map description cost**:

```text
PCA-16 + linear             ~95.4%
learned Gabor + linear      ~95.2%
DCT-16 + linear             ~92.9%
```

on the current 8x8 digits protocol.

PCA essentially closes the accuracy gap, so 'task-trained sensing beats good fixed sensing' is not established.

But the map descriptions differ sharply:

```text
PCA projection              16 * D coefficients
8 complex Gabor geometry     8 * 4 = 32 scalars
DCT                          algorithmic / very low description cost
```

At `D=64`, dense PCA uses 1024 projection coefficients versus 32 Gabor geometry scalars. At `D=784`, the ratio becomes 12544 versus 32.

## The combined ladder

The two repos compose into a more useful ladder than 'neurons think in frequency':

```text
1. NO SELECTIVITY
   collapse rich input to total energy / one indiscriminate consequence
   -> distinctions alias
   -> SpectralNeuron bucket

2. FIXED SELECTIVE OBSERVERS
   preserve several task-relevant coordinates
   -> multiplexing becomes possible but finite crosstalk appears
   -> SpectralNeuron forks
   -> DCT / PCA / fixed receiver banks

3. COMPACT PARAMETERIZED OBSERVERS
   describe a selective observation map with far fewer parameters than
   a dense unstructured matrix
   -> current SplatNeuron Gate 9 question

4. TASK-TRAINED OBSERVERS
   tune the compact parameterization to the task
   -> Gate 6 showed this beats random frozen geometry
   -> PCA control shows learning is not automatically better than a
      strong fixed subspace

5. ONLINE / STRUCTURAL OBSERVER PLASTICITY
   change the observation map during operation
   -> most current SplatNeuron routing/growth claims failed strong controls
   -> remains unearned
```

## What frequency does and does not mean

SpectralNeuron proves a **specific selective basis** can separate signals that a total-energy detector aliases.

SplatNeuron Gate 5 then showed that its cache<->ROUTE phase was reproduced by a generic smooth RBF observation manifold, and Gate 6 found learned point receivers close to learned Gabors.

Therefore the surviving abstraction is not:

> computation is fundamentally frequency-coded.

It is:

> **a receiver must preserve the distinctions required by its downstream use; selectivity, observation-map complexity, and interference determine the cost of doing so.**

Frequency is one excellent engineering coordinate because oscillatory carriers naturally multiplex, but it is not currently the unique computational ingredient.

## The missing experiment joining the repos

Gate 6 currently says `16 channels` by fiat. SpectralNeuron shows that real shared channels have leakage.

A direct bridge would hold a **single physical/shared carrier budget** fixed and compare observation maps under controlled interference:

```text
source / image features
        |
        v
M selectively encoded channels on one shared medium
        |
   finite crosstalk
        |
        v
receiver bank
        |
        v
task decoder
```

Sweep:

```text
M                     number of logical channels
map description cost  dense / structured / algorithmic
channel spacing/Q      or a generic matched interference parameter
decoder capacity
```

Measure jointly:

```text
task accuracy
crosstalk matrix
bytes / physical carrier count
map-description bytes
decoder compute
```

That would put SpectralNeuron's measured egress/interference budget and SplatNeuron's receiver/decoder allocation budget on the **same frontier**.

## One-line relation

> **SpectralNeuron asks how much distinction survives when selective receivers share a medium; SplatNeuron asks how cheaply the selective observation map and its downstream decoder can be represented. They are consecutive resource-allocation rungs, not evidence that frequency itself is the general principle.**
