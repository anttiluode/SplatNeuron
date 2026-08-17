# Prior-art boundary — structured observation-map rate

Date: 2026-08-17

Status: **novelty not established.**

This note records the targeted literature check prompted by Gate 11/11b. The broad ingredients are old. The repo should not claim novelty from any one of them.

## 1. Learned measurement operators are established

**Wu et al., 2019 — Learning a Compressed Sensing Measurement Matrix via Gradient Unrolling (ICML / PMLR 97).**

Learns a data-adapted compressed-sensing measurement matrix end to end. Therefore `learn the measurement map for the task/data` is occupied.

- PMLR: https://proceedings.mlr.press/v97/wu19b.html

**Mdrafi & Gurbuz, 2021 — Compressed Classification From Learned Measurements (ICCV Workshops).**

Learns sensing and classification jointly and evaluates direct classification from compressive measurements. Therefore `classify from learned low-dimensional measurements` is occupied.

- CVF Open Access: https://openaccess.thecvf.com/content/ICCV2021W/LCI/html/Mdrafi_Compressed_Classification_From_Learned_Measurements_ICCVW_2021_paper.html

## 2. Compact / structured replacements for dense matrices are established

**Dao et al., 2019 — Learning Fast Algorithms for Linear Transforms Using Butterfly Factorizations (ICML).**

Uses a structured butterfly parameterization as an efficient/compressible alternative to generic matrices and reports large parameter reductions together with faster inference.

- PMLR: https://proceedings.mlr.press/v97/dao19a.html

**Dao et al., 2022 — Monarch: Expressive Structured Matrices for Efficient and Accurate Training (ICML).**

Explicitly studies expressive structured matrices as replacements for dense matrices, motivated by memory and compute.

- PMLR: https://proceedings.mlr.press/v162/dao22a.html

**Qiu et al., 2024 — Compute Better Spent: Replacing Dense Layers with Structured Matrices (ICML).**

Systematically compares structured matrix families and measures scaling laws under compute. Therefore `different structured parameterizations occupy different quality/resource frontiers` is strongly occupied territory.

- PMLR: https://proceedings.mlr.press/v235/qiu24f.html

**Amsel et al., 2026 — Query Efficient Structured Matrix Learning (COLT).**

Studies learning approximations from structured matrix families in a general operator-learning/matrix-compression setting. This reinforces that `structured family complexity` is a mature mathematical axis, not a SplatNeuron invention.

- PMLR: https://proceedings.mlr.press/v336/amsel26a.html

## 3. Compact parameterized filters are established

Existing repo prior art already includes GaborNet, SincNet, LEAF and EfficientLEAF.

Also relevant:

**Imamura & Arizumi, 2021 — Gabor filter incorporated CNN for compression.**

Uses learned Gabor-parameterized filters to reduce early-layer filter count / model complexity.

- arXiv:2110.15644

Therefore `describe a useful filter using a few meaningful coordinates instead of all taps` is old.

## 4. Post-training quantization / model-bit scaling are established

**Lin, Talathi & Annapureddy, 2016 — Fixed Point Quantization of Deep Convolutional Networks (ICML).**

Optimizes fixed-point bit widths to reduce model storage with controlled accuracy loss.

- PMLR: https://proceedings.mlr.press/v48/linb16.html

**Dettmers & Zettlemoyer, 2023 — The case for 4-bit precision: k-bit Inference Scaling Laws (ICML).**

Explicitly studies performance as a function of parameter count and bit precision across model scales.

- PMLR: https://proceedings.mlr.press/v202/dettmers23a.html

Therefore `quantize parameters after training and plot accuracy versus bits` is not novel by itself.

## 5. Quantized measurements / bit budgets in compressive sensing are established

The compressed-sensing literature has long studied measurement bit depth and rate-distortion, including one-bit and multi-bit acquisition. Examples include Laska & Baraniuk's bit-depth-versus-measurement-rate analysis and later quantized compressed-sensing work.

This is importantly **not the same object as Gate 11**: those papers generally charge bits for the *measurements/data produced by a sensing matrix*, while Gate 11 charges bits for the *description of the sensing/observation operator itself*.

Do not blur these two rates:

```text
measurement/data rate       bits in z = C(x)
operator/map rate           bits needed to specify C
```

SplatNeuron Gate 11 currently studies the second while holding the first to a fixed logical width.

## 6. What the targeted search did not establish

The search did **not** establish that the following exact protocol is standard:

```text
classification observation operator C
structured parametric C versus dense PCA C
post-training quantize C itself
no decoder retraining per rate
literal fixed-width packing of C
common fixed-error target
separate accounting of:
    operator/map bytes
    materialized projection compute/storage
    logical egress width
    decoder state/compute
```

That absence is **not evidence of novelty**. It only says this specific measurement protocol was not immediately located in the targeted primary-source search.

Before publication, search more broadly in:

```text
learned sensing / task-driven sensing
operator compression / structured linear maps
quantized sensing matrices
optical encoder quantization
implicit / hypernetwork parameterizations of linear operators
minimum-description-length / rate-distortion views of model families
```

## 7. Correct novelty boundary after Gate 11b

Do not claim:

> a fixed-parameter structured map has O(1) description while a dense map has O(D).

That follows from the chosen parameterizations.

The empirical question is instead:

> **How much structured observer capacity is sufficient for a common task-error target as the task/data become more complex?**

What could have failed on MNIST, and did not, was **expressivity**: the same small family remained useful when resolution increased.

Gate 12 attacks that result on CIFAR-10 and allows compact capacity `M` to grow. If compact rate rises with task complexity while remaining on a useful Pareto frontier against PCA/DCT, the defensible contribution is a measured resource-allocation / operator-rate protocol, not discovery of structured matrices.

## 8. SpectralNeuron bridge boundary

A linear shared carrier plus noise and a linear demultiplexer is standard communications / MIMO territory. Frequency-division, code-division and generic linear mixing all have mature theory.

Therefore a bridge experiment is not interesting if it merely rediscovers channel capacity.

The potentially less trivial coupling question is:

> **Can spending description budget in the observation map change the separability/interference structure of the consequences that must traverse a constrained carrier?**

That is a joint frontier between:

```text
L_map     observation-map description
M_logic   logical width
I_cross   carrier interference/crosstalk
Q_decode  decoder/demultiplexer work
R_task    task error
```

Any future bridge must include generic linear/code-division attackers so FDM cannot win by construction.
