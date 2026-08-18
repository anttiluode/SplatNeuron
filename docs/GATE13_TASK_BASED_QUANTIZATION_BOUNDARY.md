# Gate 13 prior-art boundary — task-based acquisition / quantization

Date: 2026-08-18

Status: **conceptual neighborhood strongly occupied.**

Gate 13 must not claim discovery of the principle that a task-aware observation/combining stage can reduce the number or precision of downstream measurements required for a task.

## Hardware-limited task-based quantization

**Shlezinger, Eldar & Rodrigues, 2019 — Hardware-Limited Task-Based Quantization, IEEE Transactions on Signal Processing 67(20):5223–5238.**

This work designs data acquisition for the underlying task rather than faithful reconstruction of the input. Under practical scalar-ADC constraints, it jointly considers pre-quantization processing and digital recovery and shows that task-aware acquisition can obtain strong performance with relatively few bits.

- DOI: 10.1109/TSP.2019.2935864
- arXiv: 1807.08305

Therefore the broad statement

> task adaptation before a bottleneck can reduce required representation rate

is occupied.

## The number of scalar measurements / analog combining ratio is already a resource axis

**Shlezinger, Eldar & Rodrigues, 2020 — Asymptotic Task-Based Quantization with Application to Massive MIMO, IEEE Transactions on Signal Processing.**

The framework linearly combines a high-dimensional observation into a lower-dimensional representation before scalar quantization and explicitly studies an **analog combining ratio** controlling how the number of scalar quantizers grows with input size.

The paper analyzes task distortion versus quantization rate under practical hardware-limited structure and contrasts task-aware and task-ignorant acquisition.

Therefore Gate 13 cannot claim novelty from a trade such as

```text
task-aware combiner
    -> fewer scalar outputs / lower acquisition rate
    -> same task distortion
```

That conceptual exchange is established.

## Learned task-based acquisition is also established

**Shlezinger & Eldar, 2020 — Deep Task-Based Quantization.**

Uses deep learning to design task-oriented quantization mappings for parameter estimation and classification under bit constraints.

**Shlezinger et al., 2022 — Deep Task-Based Analog-to-Digital Conversion.**

Jointly learns task-oriented sampling / analog combining, ADC behavior and digital processing, and includes mechanisms for adapting sampling and quantization rate to the task.

Thus the following are also occupied in broad form:

```text
learn the acquisition operator from data
jointly optimize acquisition and task decoder
optimize acquisition width/rate for task performance
```

## What Gate 13 still measures differently

The existing task-based-quantization literature primarily treats acquisition/quantization rate, analog-combiner architecture, hardware constraints and task distortion as the key resources.

Gate 13 adds a different explicit currency:

```text
L_map = deployed description payload of the observation operator itself
```

and separately records:

```text
M         logical observation width
S_dec     decoder state
C_find    search/restart cost used to discover the map
R_task    task performance
```

The narrow remaining question is therefore not whether task-aware acquisition saves measurements. It is:

> **When several observation families can all implement task acquisition, what is the measured exchange between the description/search cost of the acquisition operator and the logical width it saves, and how does that exchange depend on alignment between world structure and operator family?**

This is a resource-accounting question *inside* an established task-based acquisition problem.

## Important novelty caution

The targeted search has not established that charging literal packed observation-operator description bytes alongside output width and discovery cost is standard in task-based quantization.

That absence is **not evidence of novelty**.

Before publication, search specifically for:

```text
analog combiner coefficient quantization
hybrid beamformer codebook / configuration overhead
measurement-matrix storage / feedback overhead
task-based sensing implementation complexity
hardware-aware learned sensing matrix compression
rate-distortion with encoder model-description cost
MDL / two-part coding of sensing operators
```

## Consequence for Gate 13 wording

Even a strong positive Gate 13 should not say:

> We discovered that task-aware observations reduce measurement width.

A defensible statement would be much narrower:

> **In a controlled task-based acquisition instrument, we measured how literal observation-operator description and discovery cost trade against logical measurement width across task complexity and operator/world alignment.**

Whether that measurement protocol is sufficiently novel or useful remains an open prior-art question.
