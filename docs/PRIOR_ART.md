# Prior art / attackers

SplatNeuron currently makes **no novelty claim**. The broad ideas around active sensing, learnable front ends, compact structured filters, and sensor/task co-design are well occupied. The useful contribution of this repo, if any, has to be a **measured resource frontier with strong boring controls**.

## Input-dependent sampling geometry

**Dai et al., 2017 — Deformable Convolutional Networks.** Learned input-dependent offsets modify convolution sampling locations.

- arXiv:1703.06211

**Jaderberg et al., 2015 — Spatial Transformer Networks.** Learns input-conditioned spatial transformations inside networks.

- arXiv:1506.02025

**Mnih et al., 2014 — Recurrent Models of Visual Attention.** A recurrent agent adaptively chooses image locations / glimpses.

- arXiv:1406.6247

Therefore fast ROUTE alone is occupied territory.

## Plasticity during lifetime

**Miconi, Stanley & Clune, 2018 — Differentiable plasticity.** Trains networks whose Hebbian/plastic synapses continue changing during an agent's lifetime.

- PMLR 80:3559-3568

Therefore lifetime adaptation alone is occupied territory.

## Compact parameterized front ends

This is now the most relevant prior-art family for Gate 9.

**Alekseev & Bobe, 2019 — GaborNet.** Constrains early vision filters to Gabor functions and learns the Gabor parameters by backpropagation.

- arXiv:1904.13204

**Ravanelli & Bengio, 2018 — SincNet.** Replaces unconstrained raw-waveform convolution filters with parameterized sinc band-pass filters, learning only cutoff frequencies rather than every filter tap. The paper explicitly motivates this as a compact, interpretable front end.

- arXiv:1812.05920

**Zeghidour et al., 2021 — LEAF: A Learnable Frontend for Audio Classification.** A lightweight learnable alternative to fixed mel-filterbanks, learning filtering/pooling/compression/normalization with a small parameter cost.

- ICLR 2021
- arXiv:2101.08596

**Schlüter & Gutenbrunner, 2022 — EfficientLEAF.** Particularly important as an attacker: it reports similar accuracy at much lower frontend compute and also notes that learnable front ends do not consistently beat a fixed mel-filterbank across tasks.

- arXiv:2207.05508

These papers already own broad claims such as:

```text
structured filters can use far fewer learned coefficients
learnable front ends can be task adapted
compact physical/meaningful parameterizations can work well
```

So Gate 9 cannot claim discovery of compact learned sensing.

## Strong fixed-basis attackers

Gate 6 originally compared learned geometry against the **same random receiver geometry frozen**. Gate 9 showed why that is insufficient.

Mandatory fixed-basis attackers now include:

```text
PCA / unsupervised dense subspace
DCT or related analytic transform
strong task-independent filterbanks
```

On the current 8x8 digits protocol:

```text
PCA-16 + linear      ~95.4%
learned Gabor        ~95.2%
DCT-16 + linear      ~92.9%
```

Therefore any claim of 'learning the receiver is better than fixing it' is currently dead on this task.

The interesting residual is **description/storage cost of the map**:

```text
dense PCA map        M * D coefficients
compact geometry     O(1) parameters per receiver
analytic DCT         near-zero learned map description
```

DCT is especially important because it attacks the idea that a short map description itself is sufficient for novelty.

## Task-driven optics / sensing

The broader principle of optimizing the measurement process jointly with downstream inference is established.

**Inagaki et al., ECCV 2018 — Learning to Capture Light Fields through a Coded Aperture Camera.** Learns acquisition and reconstruction jointly and validates on a camera prototype.

**Chang & Wetzstein, ICCV 2019 — Deep Optics for Monocular Depth Estimation and 3D Object Detection.** End-to-end optimizes optical coding and neural inference; includes a physical prototype.

**Metzler et al., CVPR 2020 — Deep Optics for Single-Shot High-Dynamic-Range Imaging.** Jointly trains an optical encoder and electronic decoder and fabricates the optimized optical element.

More recent camera co-design work continues this line, including joint optimization of camera parameters and task-specific perception.

Therefore:

> 'computation can be moved into observation' is occupied ground.

SplatNeuron must quantify a narrower tradeoff rather than reuse that slogan as a novelty claim.

## Internal attacker: WildIdea W3/K2

`anttiluode/WildIdea` records a boundary where preallocated alternative charts plus disagreement-directed probing matched predictable online chart growth.

Reported switch/re-entry probe counts:

```text
fixed bank + random probes         84.6 / 56.8
fixed bank + disagreement probes    2.6 /  2.5
predictable growth + disagreement   3.3 /  1.9
```

SplatNeuron independently reproduced the same negative shape: two preallocated plastic anchors beat online branch growth.

This remains mandatory against structural-growth claims.

## Structural plasticity in biology

These are biological motivation only.

**Xu et al., 2009 — Rapid formation and selective stabilization of synapses for enduring motor memories.** Motor learning rapidly induced new dendritic spines and selectively stabilized a subset.

- Nature 462, 915-919. doi:10.1038/nature08389

**Fu et al., 2012 — Repetitive motor learning induces coordinated formation of clustered dendritic spines in vivo.** Repeated training induced clustered new spines with preferential persistence.

- Nature 483, 92-95. doi:10.1038/nature10844

These do not establish SplatNeuron's computational rules.

## SpectralNeuron is prior internal evidence for selectivity, not novelty

`anttiluode/SpectralNeuron` rebuilds frequency-division multiplexing with resonant integrate/fire/reset units.

It demonstrates that:

```text
total-power collapse aliases spectral distinctions
selective resonant channels preserve them
multiple selective channels on one shared carrier pay finite crosstalk
```

That is standard FDM/signal-processing territory, but useful internally because it makes **egress interference** explicit. SplatNeuron Gate 6/9 instead fixes 16 logical output values by fiat.

See `SPECTRALNEURON_RELATION.md`.

## Current scientific boundary

After Gates 0-9:

```text
fast ROUTE / active sensing                         occupied prior art
lifetime plasticity                                 occupied prior art
online structural growth needed                     no in current toy
Gabor-specific routing phase                        no, generic RBF reproduces it
adaptive admission needed                           no, strong fixed policy survives
learned receiver beats random frozen receiver       yes
learned receiver beats strong fixed PCA basis       no
fixed receiver destroys class information           no, large decoder/SVM recovers it
interior pre-collapse block beats endpoints          no
compact structured map can rival dense PCA           plausible small-data receipt
```

The live question is therefore:

> **As input dimension grows, what accuracy can be achieved per byte of measurement-map description, per unit of projection/decoder compute, and per byte crossing the receiver boundary?**

That is the claim that still has to be earned.
