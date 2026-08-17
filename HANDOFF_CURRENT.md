# SplatNeuron — current handoff

Date: 2026-08-17

## One-line state

> **The live result is an observer-resource / expressivity frontier, not a neuron, frequency, or universal O(1)-versus-O(D) scaling law.**

A fixed-size parametric map has fixed description length by construction. The empirical question is whether such a small structured family remains expressive enough as the task/data become more complex, and how much map rate / logical width must be added when it does not.

No novelty, neuroscience, frequency-coding, FLOP, energy, or hardware claim is currently supported.

## Ledger

```text
Smoke 0    WAIT/ROUTE plumbing                     original WAIT null constructed
Smoke 1    online branch growth                    fixed plastic capacity wins
Gate 2     continuous fixed-capacity ROUTE         address cache survives
Gate 3/4   adaptive admission                      strong fixed policies survive
Gate 5     Gabor-specific ROUTE                    generic RBF reproduces phase
Gate 6     learned vs random-frozen receiver       large small-budget gap
Gate 7/8   mixed/pre-collapse allocation           no interior Y block
Gate 9     PCA/DCT fixed-basis attack              PCA closes Gate-6 accuracy gap
Gate 10    28x28 MNIST scale                       resource currencies diverge
Gate10b/c  compact-family attacker                 nonoscillatory derivatives match Gabor
Gate 11    literal operator-bit rate               compact family reaches high-rate corner
Gate 11b   same codec at D=784                     fixed family remains useful on MNIST
Gate 12    CIFAR-10 intrinsic-complexity attack    preregistered / running
```

## Closed stories

```text
online branch growth               CLOSED in current matched-capacity toy
adaptive admission                 CLOSED
Gabor/frequency-specific mechanism CLOSED
interior pre-collapse Y block      NOT FOUND
learned observer > strong PCA      NOT ESTABLISHED on Gate 9
```

Gate 10c is the clean frequency kill:

```text
Gabor                         88.33%
steerable Gaussian derivative 88.56%
```

Same 32 map scalars, same 16 outputs, same linear head.

## Gate 9 — missing PCA control changed the project

8x8 digits:

```text
PCA-16 + linear        95.42%
learned Gabor          95.24%
DCT-16 + linear        92.85%
```

Paired PCA-minus-Gabor:

```text
+0.17 percentage points
95% bootstrap CI [-0.87,+1.15]
```

Therefore the original learned-vs-random-frozen Gate-6 separation was not a strong fixed-sensing result.

## Gate 10 — currencies move in opposite directions

From `D=64` to `D=784`:

```text
nominal dense/compact description ratio  32x -> 392x        UP by construction
learned-vs-H7 accuracy gap               +5.49 -> +2.38 pp  DOWN
dense digital MAC ratio                  ~1.92x -> ~1.086x  DOWN toward 1
logical egress                            16 -> 16            FLAT
```

This worked counterexample is important: `N times more efficient` is meaningless unless the resource currency is named.

## Gate 11 / 11b — literal operator bits

Post-training map quantization only; decoder frozen; actual bit packing.

Diagnostic `within 1 pp of own full precision`:

```text
                         D=64        D=784
compact structured       24 B         24 B
PCA                     576 B       4768 B
DCT                       0 B          0 B
```

Compact coordinates are fragile at 2-3 bits. Their advantage comes from **few high-leverage values**, not robust individual values.

The old wording that the `rate law scales with D` is too strong. The map-only ratio grows arithmetically because the compact family has fixed parameter count while PCA has `M*D` coefficients.

The empirical receipt is narrower:

> **On both digit tasks, the same 32-value structured family remained expressive enough to retain useful task performance at a 24-byte map payload.**

That could have failed at higher resolution, but MNIST is still the same centered stroke task. Gate 12 attacks the actual expressivity question.

## Gate 11 reporting correction

`within 1 point of each family's own ceiling` is not iso-accuracy.

Keep it as a diagnostic, not the headline.

From Gate 12 onward:

```text
common validation-defined task-error target
validation-only configuration selection
held-out test reporting
```

and always report separately:

```text
map bytes
head / decoder bytes
total explicit state
logical egress width
projection compute/materialization cost
```

## Gate 12 — CIFAR-10 complexity attack

Preregistered before results in `docs/GATE12_PREREG_CIFAR_COMPLEXITY.md`.

Dataset:

```text
CIFAR-10 -> fixed luminance
32x32, D=1024
12k train / 3k validation / 10k standard test
fresh seeds 9300, 9301
```

Capacity sweep:

```text
M = 16, 32, 64, 128
structured nonoscillatory derivative family
PCA-M
DCT-M
full-pixel linear reference
```

Common targets:

```text
T95 = 95% of full-pixel validation accuracy
T90 = 90% of full-pixel validation accuracy
```

The load-bearing old setting is explicitly attacked:

```text
M=16
32 geometry values
6 bits/value
24 map bytes
```

Possible outcomes:

```text
24 B still reaches T95
    -> stronger-than-expected expressivity result

compact needs larger M / more bytes
    -> observer cost tracks task complexity; report required resource vector

nothing through M=128 reaches T90
    -> current structured family fails expressivity; record kill

PCA/DCT dominates at common target
    -> compact description loses on this task
```

Do not change M, codecs, targets or grayscale preprocessing after results.

## Prior-art boundary

Broad ingredients are occupied:

```text
learned measurement matrices       old
structured alternatives to dense   old (Butterfly / Monarch / related)
compact parameterized front ends   old
post-training quantization          old
bit-precision scaling laws          old
```

See `docs/PRIOR_ART_OBSERVER_RATE.md`.

The candidate contribution, if anything survives, is a **measurement protocol / worked Pareto frontier**, not a new structured-matrix idea.

## SpectralNeuron / shared-carrier boundary tightened again

Common pipeline:

```text
x -> observation map C_theta -> logical z
  -> physical/shared channel H
  -> receiver/demux -> z_hat
  -> decoder -> task
```

SpectralNeuron is relevant because it makes physical crosstalk visible, but FDM/MIMO itself is standard.

More importantly, the broader coupling `learn task-relevant features that survive a noisy bandwidth-limited channel` is already heavily occupied by **task-oriented / semantic communications and deep joint source-channel coding**.

So do **not** build a bridge merely to show that task-shaped features survive a bad channel.

A bridge only earns work if there is a sharper resource-accounting question not already answered by that literature, with generic linear/code-division controls from the start.

## Stop lines

- Do not reopen growth/admission/frequency stories.
- Do not quote parameter-count ratios as FLOP ratios.
- Do not call fixed-P vs dense-P scaling a discovery.
- Do not call own-ceiling rate comparisons iso-accuracy.
- Do not call operator bytes materialized-filter RAM.
- Do not retune Gate-11 codecs on the same digit data.
- Do not build a Spectral bridge before checking task-oriented JSCC / semantic-communications prior art.

## Next legitimate work

1. Finish Gate 12 exactly as preregistered.
2. If it survives, replicate on another genuinely different modality/task or formalize the multi-currency frontier.
3. Reassess the shared-carrier bridge only after the semantic-communications prior-art boundary is explicit.
