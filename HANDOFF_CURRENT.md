# SplatNeuron — current handoff

Date: 2026-08-17

## One-line state

> **The current result is an observer description-rate scaling receipt, not a neuron or frequency result.**

Across preregistered 8x8 and 28x28 tests, a 32-value structured observation map stayed near its own full task accuracy at a constant **24-byte serialized map payload**, while the preregistered row-scaled PCA-16 payload grew from **576 B to 4,768 B**.

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
Gate 11    literal map-bit rate/distortion         24B compact vs 576B PCA near-own-full
Gate 11b   same codec at D=784                     24B compact vs 4768B PCA
```

## Dead / closed stories

### Growth

```text
grow       total work 1074.0
fixedcap   total work  613.2
```

Same steady state; fixed plastic capacity wins.

```text
GROWTH_EARNS_KEEP = False
```

### Adaptive admission

Gate 3/4 failed robust fixed policies, including within-run nonstationarity.

```text
ADMISSION_BRANCH_STATUS = CLOSED
```

### Gabor/frequency specificity

Gate 5 generic RBF reproduced the online phase. Gate 10c then matched/slightly beat Gabor on MNIST with a nonoscillatory steerable Gaussian-derivative observer at identical 32-map-scalar / 16-output / linear-head budgets:

```text
Gabor                 88.33%
Gaussian derivative   88.56%
```

```text
GABOR_OR_FREQUENCY_SPECIFIC_KEEP = False
```

### Interior pre-collapse Y block

No interior branch/collapse allocation beat the hard endpoints.

```text
INTERIOR_Y_BLOCK_EARNS_KEEP = False
```

## Gate 9 — PCA removed the old Gate-6 story

8x8 digits, same eight split IDs:

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

So the original `learned vs random-frozen` Gate-6 separation does not establish that learned sensing beats a good fixed basis.

## Gate 10 — resource currencies split under scale

At D=784 on frozen MNIST seeds 9100/9101:

```text
learned compact Gabor       88.33%
PCA-16                      85.23%
DCT-16                      83.39%
random compact + H7         85.95%
random compact + H48        91.58%
full pixels + linear        90.82%
```

Observed scaling from D=64 -> D=784:

```text
nominal dense/compact map description   32x -> 392x        grows
learned-vs-H7 accuracy gap              +5.49 -> +2.38 pp  shrinks
dense digital MAC ratio                 ~1.92x -> ~1.086x  collapses
```

No single efficiency factor is valid.

## Gate 11 — literal map bits on fresh 8x8 splits

Fresh split IDs `7200..7207`; post-training fixed-rate quantization; same FP32 680-byte linear head; no per-rate retraining.

Full means:

```text
Gabor                 94.13%
Gaussian derivative   94.03%
PCA-16                93.92%
DCT-16                90.73%
```

Smallest map payload within one percentage point of own full precision:

```text
Gabor                  24 B   6 bits/value
Gaussian derivative    24 B   6 bits/value
PCA                    576 B   4 bits/value + row scales
DCT                      0 B   algorithmic
```

Map-only ratio:

```text
576 / 24 = 24x
```

Total observer+head state:

```text
compact   704 B
PCA      1256 B
ratio     1.78x
```

DCT owns the zero-map/lower-accuracy corner.

Compact geometry is more brittle per coordinate at 2-3 bits; its win comes from having few high-leverage coordinates, not robust coordinates.

## Gate 11b — the description-rate gap grows at D=784

Fresh MNIST seeds `9200/9201`, same fixed-rate codecs.

Full means:

```text
Gabor                 88.99%
Gaussian derivative   88.39%
PCA-16                86.03%
DCT-16                83.94%
```

Within one point of own full precision:

```text
Gabor                  24 B   88.90%
Gaussian derivative    24 B   88.10%
PCA                   4768 B   85.78%
DCT                      0 B   83.94%
```

Cross-scale comparison:

```text
                         D=64        D=784
------------------------------------------------
compact useful map       24 B         24 B
PCA useful map          576 B       4768 B
map-only ratio           24x        198.7x
compact+head            704 B        704 B
PCA+head               1256 B       5448 B
total-state ratio       1.78x        7.74x
```

Input dimension increased `12.25x`. Compact useful payload stayed constant. PCA payload grew `8.28x` even though its useful precision dropped from 4 to 3 bits/coefficient.

This is the strongest current result.

Supported statement:

> **Across these preregistered digit experiments, a 32-value structured observation map retained near-full task accuracy at a constant 24-byte serialized map payload when input dimension increased from 64 to 784, while the fixed-rate PCA-16 payload grew from 576 to 4,768 bytes.**

Do not call this universal yet: only two input dimensions; MNIST n=2; fixed scalar codecs; digit tasks.

## SpectralNeuron relation

`anttiluode/SpectralNeuron` measures the adjacent physical-channel resource.

Common pipeline:

```text
x -> C_theta -> logical consequences z
  -> shared physical channel H
  -> receiver/demultiplexer R -> z_hat
  -> decoder g_phi -> task
```

SplatNeuron Gates 9-11b now measure the **description-rate / quality cost of C_theta** while mostly assuming an ideal logical channel.

SpectralNeuron demonstrates that selective logical consequences sharing one physical waveform have finite crosstalk: roughly `3.1x` self/crosstalk separation for its resonant forks versus `1.0x` for a total-energy bucket.

This is standard FDM territory, but it supplies the missing physical-interference axis.

The common abstraction is:

```text
selectivity
+
observer description rate
+
logical width
+
physical carrier / crosstalk
+
decoder cost
```

not frequency-coded thought.

## Current stopping lines

- Growth closed for capacity-matched two-view worlds.
- Admission branch closed.
- Gabor/frequency-specific story closed.
- No interior Y block found.
- PCA closes the 8x8 learned-vs-good-fixed accuracy story.
- Do not quote parameter ratios as FLOP ratios.
- Do not call 16 logical outputs an egress win; all constrained arms use the same logical width.
- Do not call map-description bytes materialized-filter RAM; a dense digital implementation may still expand structured filters.
- Do not tune Gate-11 codecs on the same data after seeing the result.

## Next allowed work

Only two directions currently earn more compute:

1. **Replication/generalization of the observer rate law** — more fresh seeds or a non-digit dataset with codecs frozen.
2. **SpectralNeuron bridge** — force logical consequences through a controlled shared physical channel and measure task distortion versus carrier width/noise/crosstalk, with a generic mixing baseline so frequency cannot win by narrative.
