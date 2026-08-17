# Prior art / attackers

SplatNeuron currently makes **no novelty claim**. Several nearby lines already own major pieces of the idea, and Antti's earlier repos supply directly relevant negative controls.

## Input-dependent sampling geometry

**Dai et al., 2017 — Deformable Convolutional Networks.** Deformable convolution augments fixed convolution sampling locations with learned, input-dependent offsets. This attacks any claim as broad as "neural receptive fields can move."

- arXiv:1703.06211

**Jaderberg et al., 2015 — Spatial Transformer Networks.** Spatial transformers learn input-conditioned spatial transformations inside networks.

- arXiv:1506.02025

**Mnih et al., 2014 — Recurrent Models of Visual Attention.** A recurrent agent adaptively selects a sequence of image locations and controls computation independently of total image size.

- arXiv:1406.6247

Therefore fast ROUTE alone is occupied territory.

## Plasticity during lifetime

**Miconi, Stanley & Clune, 2018 — Differentiable plasticity.** Hebbian/plastic recurrent connections continue changing during an agent's lifetime, while gradient descent learns how that plasticity should work.

- PMLR 80:3559-3568

Therefore lifetime adaptation alone is occupied territory.

## Learnable Gabor front ends

Gate 6 must not be interpreted as inventing learnable Gabor filters.

**Alekseev & Bobe, 2019 — GaborNet: Gabor filters with learnable parameters in deep convolutional neural networks.** Gabor parameters are learned by ordinary backpropagation inside a vision network.

- arXiv:1904.13204

**Luan et al., 2018 — Gabor Convolutional Networks.** Gabor structure is incorporated into CNNs and the authors explicitly report compact models / fewer learnable parameters while preserving representation capacity.

- IEEE TIP 27(9):4357-4366
- doi:10.1109/TIP.2018.2835143

**Zhong et al., 2019 — Learnable Gabor Convolutional Networks.** Another direct precedent for learning structured Gabor parameters rather than treating the filters as fixed hand-crafted features.

Therefore the Gate 6 statement "learned receiver geometry can make a compact downstream decoder work better" is **prior-art-adjacent by construction**. The receipt is useful as a controlled allocation frontier, not as a novelty claim.

## Task-driven / learned sensing

The broader principle of co-optimizing measurements/sensors with a downstream task is also established.

**Wu et al., ICML 2019 — Learning a Compressed Sensing Measurement Matrix via Gradient Unrolling.** Learns a data-dependent measurement matrix rather than accepting a fixed random sensing map.

- PMLR 97:6828-6839

**Sommerhoff et al., 2023/2024 — Differentiable Sensor Layouts for End-to-End Learning of Task-Specific Camera Parameters.** Explicitly treats sensing layout/parameters and downstream vision objectives as one differentiable optimization problem.

**Noboru, Ozasa & Tanaka, WACV 2026 — Joint Optimization of Camera Model and Deep Neural Network for Image Recognition.** Jointly optimizes camera sensor/ISP parameters and downstream recognition models.

**Yan, Bryson & Dansereau, WACV 2026 — JOCA: Task-Driven Joint Optimisation of Camera Hardware and Adaptive Camera Control Algorithms.** Extends task-driven camera co-design to adaptive runtime camera control.

These are strong attackers against any broad SplatNeuron claim of "learn what/how to sense instead of only learning the decoder."

The narrower quantity Gate 6 contributes to this repo is the **receiver-vs-decoder allocation curve under fixed 16-channel egress**, including the point where a frozen observation map needs much more decoder capacity to catch a low-parameter learned front end.

## Internal attacker: WildIdea W3/K2

`anttiluode/WildIdea` records an off-repo W3/K2 boundary in which a preallocated bank of three alternative charts plus disagreement-directed probing matched predictable online chart growth.

Reported switch/re-entry probe counts:

```text
fixed bank + random probes         84.6 / 56.8
fixed bank + disagreement probes    2.6 /  2.5
predictable growth + disagreement   3.3 /  1.9
```

WildIdea's frozen interpretation is that **having alternatives mattered; manufacturing them online did not earn architectural importance in that toy.**

SplatNeuron Smoke 1 independently reproduced the same shape with plastic Gabor receivers: two preallocated plastic anchors beat online branch growth at identical eventual accuracy and steady-state work.

This is mandatory against structural-growth claims in this repo.

## Structural plasticity in biology

These are biological motivation, not implementation evidence.

**Xu et al., 2009 — Rapid formation and selective stabilization of synapses for enduring motor memories.** Motor learning rapidly induced new dendritic spines; a subset was preferentially stabilized with subsequent training.

- Nature 462, 915-919. doi:10.1038/nature08389

**Fu et al., 2012 — Repetitive motor learning induces coordinated formation of clustered dendritic spines in vivo.** Repetitive training produced spatial clusters of new spines, and clustered spines were preferentially retained.

- Nature 483, 92-95. doi:10.1038/nature10844

These support only the modest biological statement that repeated experience can leave persistent spatial structural traces at synaptic/dendritic scale. They do **not** establish that dendrites move receptive Gabor splats or optimize an observation-work objective.

## Shared dynamical media / reservoirs

Liquid-state / reservoir computing already establishes that rich recurrent dynamics can provide transient state from which learned readouts extract task-relevant consequences. Therefore "a shared dynamical medium with learned readouts" is not the contribution.

## Current scientific boundary

After the current ladder:

```text
fast ROUTE / active sensing                        occupied prior art
lifetime plasticity                                occupied prior art
online structural growth needed                    no, killed in current toy
Gabor-specific cache/ROUTE phase                   no, generic RBF reproduces it
adaptive admission needed                          no, strong fixed policy survives
learned receiver improves small decoder            yes in Gate 6
fixed receiver destroys class information          no, large decoder/SVM recovers it
interior pre-collapse branch block beats endpoints no in Gate 8
```

So the useful live object is **not a new neural primitive yet**. It is a disciplined resource-allocation question:

> At fixed communication width, where should computation/parameters live: in task-aligned observation generation, in local collapse/reduction, or in the downstream decoder?

Any future architecture claim must keep the hard boring endpoints and task-driven-sensing prior art in the benchmark.
