# SplatNeuron — current handoff

Date: 2026-08-17

## One-line state

> **The biology-shaped online-plasticity ideas mostly died. The live object is now an observer resource frontier: task quality versus observation-map description, logical width, physical-channel interference, and decoder cost.**

No novelty, neuroscience, frequency-coding, or hardware claim is currently supported.

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
Gate 10    28x28 MNIST scale                       description and compute laws diverge
Gate10b/c  matched compact family attack           Gaussian derivatives match Gabor
```

## Closed branches

### Growth

Two preallocated plastic anchors beat online branch growth in the recurring A/B toy:

```text
grow       total work 1074.0
fixedcap   total work  613.2
```

Same final accuracy and steady state. `GROWTH_EARNS_KEEP = False`.

Do not reopen growth unless useful recurring views greatly exceed fixed capacity and fixed-capacity replacement/cache policies are included from the start.

### Adaptive admission

Gate 3 and Gate 4 failed robust fixed admission policies, including a within-run nonstationary sequence.

```text
ADMISSION_BRANCH_STATUS = CLOSED
```

### Gabor/frequency-specific online ROUTE

A generic smooth RBF observation manifold reproduced the cache<->ROUTE phase.

```text
GABOR_SPECIFIC_ROUTE_KEEP = False
```

## Gate 6 — useful result, weak baseline revealed

8x8 sklearn digits, fixed 16-real-value egress:

```text
learned Gabor + linear              202 p   95.24%
random-frozen same Gabor + H7       199 p   89.76%
```

A larger H48 decoder behind the same fixed features eventually approached the learned map, so no information-ceiling claim survived.

## Gate 9 — PCA is the load-bearing missing control

Same eight split IDs:

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

Therefore PCA and learned Gabor are not separated. The original +5.49 point story was substantially “random frozen Gabors are a poor 16-channel basis.”

Do not center the repo on “learning what to observe beats fixed sensing.”

## The surviving axis after Gate 9: compact map description

With input dimension `D` and logical output width `M=16`:

```text
dense linear map          16D coefficients
compact 8-branch map      32 geometry scalars
map-only ratio            D/2
```

```text
D=64      ratio 32x
D=784     ratio 392x
```

This is only nominal description complexity until literal bit-rate is measured.

## Gate 10 — MNIST scale splits the currencies

Frozen real-MNIST protocol:

```text
D                  784
train/val/test      6000 / 1000 / 5000
seeds               9100, 9101
logical outputs     16 real values
compact map         32 geometry scalars
```

Results:

```text
                           seed9100   seed9101   mean
-----------------------------------------------------
learned compact Gabor       88.66%      88.00%   88.33%
PCA-16                      85.32%      85.14%   85.23%
DCT-16                      83.46%      83.32%   83.39%
random Gabor + H7           86.30%      85.60%   85.95%
random Gabor + H48          91.98%      91.18%   91.58%
full pixels + linear        90.54%      91.10%   90.82%
```

Only two seeds: treat as a cross-scale receipt, not a general statistical law.

Observed scaling:

```text
map-description ratio              32x -> 392x        grows
learned-vs-H7 accuracy gap         +5.49 -> +2.38 pp  shrinks
H48 vs learned compact             -0.94 -> +3.25 pp  decoder-heavy wins at scale
dense digital compute ratio        ~1.92x -> ~1.086x  collapses toward 1
```

At D=784:

```text
compact geometry + linear head            808 B FP32 state
PCA matrix + mean + linear head          53992 B
logical egress                            64 B/sample for both
materialized projection                   12544 MACs for both
```

So:

> **Description compression grows with input dimension, while ordinary dense digital compute advantage and the original receiver-vs-decoder allocation advantage do not.**

There is no single “efficiency gain.”

## Gate 10b/c — frequency-specific scale story dies

Simple compact nonoscillatory families:

```text
points                       79.84%
Gaussian pair best           85.27%
Gabor reference              88.33%
```

A stronger matched nonoscillatory selective family closes the gap completely:

```text
8 steerable Gaussian-derivative branches
(x,y,scale,orientation)      32 map scalars
first + second derivatives   16 outputs
same linear head

seed9100                     88.60%
seed9101                     88.52%
mean                         88.56%
```

Versus Gabor `88.33%`.

The tiny difference is not a superiority result. It is a clean falsification:

```text
GABOR_OR_FREQUENCY_SPECIFIC_KEEP = False
```

What survives is **compact structured localized selectivity**, not oscillation.

See `docs/GATE10BC_COMPACT_FAMILY_ATTACKERS.md`.

## SpectralNeuron relation

`anttiluode/SpectralNeuron` remains directly related, but not because frequency is the general substrate.

Its bucket collapses a shared waveform to total power; its resonant forks preserve selective channels. Three channels sharing one noisy wire achieved about:

```text
fork self/crosstalk ratio    3.1x
bucket ratio                 1.0x
```

with finite off-diagonal leakage.

That measures a resource SplatNeuron mostly idealized away: **logical consequences interfere when they share a physical carrier.**

Common pipeline:

```text
x -> observation map C_theta -> logical z
  -> shared channel H -> receiver R -> z_hat
  -> decoder g_phi -> task
```

SplatNeuron has mostly studied `C_theta` / `g_phi`; SpectralNeuron probes `H/R`.

Common abstraction:

```text
selectivity
+
map-description cost
+
logical width
+
physical carrier / crosstalk
+
decoder cost
```

not frequency-coded thought.

## Gate 8 remains a null

At fixed 16-wide carrier and roughly ~750 trainable parameters, private Gabor branches plus local collapse produced no interior winner:

```text
B8 direct / H27            96.11%
B10 collapse / H14         94.95%
B12 collapse / H11         94.63%
B14 collapse / H8          93.84%
B16 collapse / linear      95.46%
```

```text
INTERIOR_Y_BLOCK_EARNS_KEEP = False
```

Do not architecture-search a reducer toward a win.

## Current decisive next gate: map rate-distortion

`32 scalars versus 12,544 coefficients` is still a proxy, not literal description length.

Both compact geometry and PCA can be quantized/compressed. DCT is largely algorithmic.

Gate 11 should measure:

```text
bits needed to serialize observation map C
        versus
task accuracy after quantization/compression
```

At minimum compare:

```text
compact steerable derivative or Gabor map
PCA-16
DCT / algorithmic anchor
```

and report separately:

```text
map-description bits
materialized map storage
projection compute
logical egress bytes
physical-channel/crosstalk cost if any
decoder state/compute
```

This is a rate-distortion question about the observer, not another neuron-shape contest.

## Stop lines

- Admission branch closed.
- Growth branch closed for capacity-matched two-view worlds.
- Gabor/frequency-specific claim closed by Gaussian-derivative attacker.
- No interior pre-collapse Y block found.
- Gate 6 no longer establishes learned sensing versus a good fixed basis; PCA closes it.
- Do not quote trainable-parameter ratios as FLOP ratios.
- Do not call 16-channel width an egress win; every constrained arm emits the same 64 FP32 bytes.
- Do not call float-count ratio a description-bit law until Gate 11 quantizes/serializes the maps.
