# SpectralNeuron relation — the egress/interference rung

Date: 2026-08-17

`anttiluode/SpectralNeuron` and SplatNeuron are best understood as experiments on different parts of the same **observation pipeline**.

```text
rich source x
    -> observation map C_theta
    -> logical consequences z
    -> physical/shared channel H
    -> receiver/demultiplexer R
    -> recovered consequences z_hat
    -> decoder g_phi
    -> task
```

SpectralNeuron mostly exposes `H/R`: selectivity and crosstalk on a shared physical carrier.

SplatNeuron mostly idealizes `H=I` and asks about `C_theta` / `g_phi`: observation-map description, logical width, and decoder cost.

## SpectralNeuron: selectivity preserves distinctions on a shared medium

SpectralNeuron compares:

```text
BUCKET   integrate total rectified energy
FORK     integrate energy near a selected resonance
```

At matched loud input power:

```text
40 Hz on-band     fork 20   bucket 21
120 Hz off-band   fork  0   bucket 20
broadband noise   fork  0   bucket 33
```

The bucket aliases spectrally different inputs into one total-power consequence. The fork preserves another coordinate by being selective.

Part B sums three modulated carriers onto **one shared noisy wire**:

```text
25 Hz / 45 Hz / 75 Hz
```

and reports roughly:

```text
fork    self-correlation ~0.62   crosstalk ~0.20   separation ~3.1x
bucket  self-correlation ~0.32   crosstalk ~0.32   separation  1.0x
```

with finite off-diagonal leakage up to about `0.34`.

This is ordinary frequency-division multiplexing expressed in neuron-flavoured primitives, not new signal-processing mathematics. Its value here is that it measures something SplatNeuron originally fixed by fiat:

> **selective logical channels sharing one physical carrier interfere.**

## SplatNeuron: description-quality and decoder allocation

Gate 9 on 8x8 digits:

```text
PCA-16 + linear             95.42%
learned Gabor + linear      95.24%
DCT-16 + linear             92.85%
```

PCA essentially closes the accuracy gap, so “task-trained sensing beats a good fixed basis” is not established.

The map descriptions differ:

```text
PCA projection              16 * D coefficients
8 compact branches          32 geometry scalars
DCT                          algorithmic / low stored map description
```

Gate 10 moves from `D=64` to `D=784` without increasing the 32-scalar compact-map budget.

Two-seed MNIST means:

```text
learned compact Gabor       88.33%
PCA-16                      85.23%
DCT-16                      83.39%
random Gabor + H48          91.58%
full pixels + linear        90.82%
```

The resulting resource laws diverge:

```text
map-description ratio       32x -> 392x        grows
tiny-decoder advantage      +5.49 -> +2.38 pp  shrinks
dense digital MAC ratio     ~1.92x -> ~1.086x  collapses toward 1
```

So map description, compute, logical width, and decoder capacity are separate currencies.

## Frequency is explicitly not the SplatNeuron result

Simple nonoscillatory compact maps initially lagged the MNIST Gabor:

```text
learned points                   79.84%
Gaussian pair                    85.27%
Gabor                            88.33%
```

A stronger matched nonoscillatory family removes the apparent frequency advantage:

```text
8 steerable Gaussian-derivative branches
(x,y,scale,orientation)          32 map scalars
first + second derivatives       16 outputs
same linear head

Gaussian derivative              88.56%
Gabor                            88.33%
```

Both frozen seeds tell the same story. The tiny mean difference is not a superiority claim; it is enough to reject the intended special-form claim:

```text
GABOR_OR_FREQUENCY_SPECIFIC_KEEP = False
```

Therefore the relation between the repos is **not**:

> SpectralNeuron proves frequency and SplatNeuron learns frequency.

It is:

> **SpectralNeuron demonstrates that selective channels can preserve distinctions while sharing a medium, with a measurable crosstalk cost. SplatNeuron asks how compactly a useful selective observation map can be described and how much downstream decoding is then required.**

Frequency is one excellent engineering coordinate for multiplexing. Steerable derivatives show it is not the unique compact observation form in the current vision task.

## Combined ladder

```text
1. INDISCRIMINATE COLLAPSE
   rich input -> one total-energy consequence
   -> distinctions alias
   -> SpectralNeuron bucket

2. SELECTIVE OBSERVERS
   preserve several relevant coordinates
   -> SpectralNeuron forks
   -> DCT / PCA / local derivative / Gabor banks

3. COMPACT PARAMETERIZED OBSERVERS
   describe useful selectivity with few scalars
   -> current SplatNeuron Gate 9/10 question

4. TASK-TRAINED COMPACT OBSERVERS
   tune that short description to the task
   -> useful on MNIST, but not uniquely Gabor/frequency

5. PHYSICAL SHARED-CARRIER REALIZATION
   logical consequences must coexist on finite physical bandwidth
   -> crosstalk / demultiplexing cost
   -> SpectralNeuron's missing contribution to SplatNeuron

6. ONLINE / STRUCTURAL OBSERVER PLASTICITY
   change observation geometry during operation
   -> current SplatNeuron growth/admission stories failed strong controls
   -> unearned
```

## Direct bridge experiment

Gate 10 still says `M=16 logical values` as though they are perfect independent wires. SpectralNeuron says real shared carriers leak.

A direct bridge should hold a **physical carrier budget** fixed:

```text
x -> C_theta -> z in R^M
                 |
                 v
          shared channel H
          physical width P < M
                 |
                 v
          selective receiver R
                 |
                 v
               z_hat
                 |
                 v
              decoder
```

Sweep:

```text
M                     logical observation width
P                     physical carrier width / count
map description bits  dense / structured / algorithmic
channel condition     crosstalk / noise / spacing
receiver cost         demultiplexer state/compute
decoder capacity
```

Measure jointly:

```text
task accuracy
full crosstalk matrix
map-description bits
physical bandwidth / carrier count
receiver/demux compute
decoder compute
```

Frequency-division multiplexing can be one arm, but a matched generic linear mixing/demixing channel is mandatory so frequency cannot win by narrative.

## One-line relation

> **SpectralNeuron measures the interference price of preserving several selective consequences on one physical medium; SplatNeuron measures the description and decoder price of producing useful selective consequences in the first place. They are consecutive resource-allocation rungs, not evidence that frequency itself is the general principle.**
