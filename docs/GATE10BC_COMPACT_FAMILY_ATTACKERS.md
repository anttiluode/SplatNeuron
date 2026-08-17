# Gate 10b/c — matched compact-family attackers on MNIST

Date: 2026-08-17

Status: **frequency/Gabor-specific interpretation rejected.**

Gate 10 found that a 32-scalar learned Gabor measurement map reached `88.33%` mean accuracy on the frozen two-seed MNIST protocol while PCA-16 reached `85.23%`.

That did **not** establish that oscillation or frequency was the important compact structure. Gate 10b/c therefore keep these fixed:

```text
map-description scalars      32
logical outputs              16 real values
classifier                   16 -> 10 linear head
head parameters              170
MNIST splits                 seeds 9100, 9101
train / val / test           6000 / 1000 / 5000
epochs / optimizer           80 / Adam(.02)
```

Only the compact observation family changes.

## Gate 10b — simple nonoscillatory families

Learned points use 16 bilinear samples x 2 coordinates = 32 scalars and 16 outputs.

Learned Gaussian pairs use 8 branches x `(x,y,separation,orientation)` = 32 scalars. Each branch emits two positive Gaussian-lobe integrals. Two fixed lobe widths were reported rather than tuning one toward the Gabor result.

```text
family                         seed 9100   seed 9101    mean
----------------------------------------------------------------
Gabor reference                   88.66%      88.00%     88.33%
points                            79.78%      79.90%     79.84%
Gaussian pair sigma=.12           85.48%      85.06%     85.27%
Gaussian pair sigma=.22           70.88%      71.66%     71.27%
```

The strongest simple nonoscillatory attacker remained about three points below the Gabor. That was **not** enough to infer that oscillation mattered: point samples and positive local averages are a much poorer shape family than oriented signed filters.

## Gate 10c — steerable Gaussian derivatives

The stronger attacker removes oscillation while preserving local oriented signed selectivity:

```text
8 branches
(x, y, scale, orientation)      4 scalars each
                                32 scalars total

output 1                        first directional Gaussian derivative
output 2                        second directional Gaussian derivative
                                16 real outputs total
```

There is no sinusoidal carrier, learned frequency, phase, or repeated oscillation.

```text
family                         seed 9100   seed 9101    mean
----------------------------------------------------------------
Gabor reference                   88.66%      88.00%     88.33%
Gaussian derivative               88.60%      88.52%     88.56%
```

The nonoscillatory steerable derivative family slightly exceeds the Gabor mean on both frozen seeds.

With only two seeds this tiny difference is not a superiority claim. It is more than enough for the intended falsification:

```text
GABOR_OR_FREQUENCY_SPECIFIC_KEEP = False
```

## Supported interpretation

> **A compact structured family of localized, task-trainable selective measurements can occupy a strong description-quality point. On this task, oscillatory Gabors and nonoscillatory steerable Gaussian derivatives occupy essentially the same point at identical map-description and egress budgets.**

This is consistent with Gate 5, where a generic smooth manifold reproduced the online cache<->ROUTE phase.

## SpectralNeuron implication

SpectralNeuron's frequency channels work because frequency is a convenient selective coordinate for multiplexing on one shared waveform. It does **not** follow that frequency is the general abstraction behind SplatNeuron.

The common object is:

```text
selective observation
+
compact description of that selectivity
+
finite logical/physical channel budget
+
interference / crosstalk
+
downstream decoder cost
```

Frequency division is one implementation of the channel/selectivity side. A steerable derivative bank is another observation family with no oscillatory coding.

## Next gate

Stop searching compact filter families merely to decide whether Gabors win.

The next invariant question is literal **description rate versus task distortion**:

```text
bits needed to describe C
        versus
accuracy after C is quantized / compressed
```

The current `32 scalars versus 12,544 PCA coefficients` comparison is only a float-count proxy for description length. Both structured geometry and dense PCA can be quantized/compressed; DCT is largely algorithmic.

Gate 11 should quantize/serialize the observation map and report a rate-distortion frontier rather than counting nominal float parameters.

## Reproduce

```bash
pip install -e '.[scale]'
python experiments/gate10b_compact_family.py --download
python experiments/gate10c_gaussian_derivative.py --download
```
