# Shared-carrier bridge — prior-art boundary

Date: 2026-08-17

Status: **bridge novelty is much narrower than initially assumed.**

## Standard communications boundary

A set of logical channels mixed through a linear noisy carrier and recovered by a linear demultiplexer is standard communications / MIMO territory. Frequency-division, code-division, orthogonal transforms, linear precoding and channel-capacity questions are mature.

Therefore a SplatNeuron/SpectralNeuron bridge does not earn novelty by showing that selective carriers reduce crosstalk.

## Task-oriented / semantic communications is the more important overlap

The broader idea:

> learn source features / semantic consequences specifically so they can survive a constrained noisy channel and still support a downstream task

is also established.

Examples found in the targeted search:

**Lyu et al., 2023 — Semantic Communications for Image Recovery and Classification via Deep Joint Source and Channel Coding.**

Jointly learns image features for reconstruction and direct classification under communication constraints, including adaptive feature pruning with channel conditions.

- arXiv:2304.02317

**Xu et al., 2022 — Deep Joint Source-Channel Coding for Semantic Communications.**

Frames semantic communication as deep joint source-channel coding in which only task-relevant information needs to be conveyed under latency/bandwidth/power constraints.

- arXiv:2211.08747

**Huang et al., 2023 — Joint Task and Data Oriented Semantic Communications.**

Formulates rate-distortion with semantic/task distortion for image transmission and classification.

- arXiv:2302.13580

**Kutay & Yener, 2024 — Classification-Oriented Semantic Wireless Communications.**

Explicitly optimizes semantic representations / quantization for classification across a wireless channel.

- arXiv:2401.18069

Thus even the coupling:

> spend encoder/observation capacity to make task-relevant consequences survive a bad channel

is not new in broad form.

## What remains potentially useful

A SplatNeuron bridge only earns work if it asks a narrower measurement question, for example a controlled Pareto study in which the *observer-map description itself* is charged separately from:

```text
L_map       bits describing the observation operator
M_logic     logical consequence width
B_channel   physical channel budget
I_cross     crosstalk / interference
S_rx        receiver/demux state
Q_rx        receiver/demux compute
S_decode    task-decoder state
Q_decode    task-decoder compute
R_task      task error
```

and compares **matched structured and unstructured observation families** under the same carrier.

Even that should be framed as a worked resource-accounting experiment unless a deeper literature search finds a real gap.

## Mandatory attackers for any bridge

```text
FDM / resonant carriers
generic orthogonal linear coding
random linear mixing + optimal/regularized linear demux
code-division / spread-spectrum style baseline where appropriate
oracle SVD / channel-aware precoder if the channel is linear and known
task-oriented learned JSCC / semantic-communication baseline
```

If the bridge only rediscovers MIMO capacity or learned JSCC, stop.

## Current ordering

Gate 12 non-digit observer expressivity comes first.

Do not spend compute on the shared-carrier bridge until the observer-rate result survives a genuinely different task and the semantic-communications literature is searched more deeply.
