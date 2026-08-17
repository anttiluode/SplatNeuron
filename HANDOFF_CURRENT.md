# SplatNeuron — current handoff

Date: 2026-08-17

## One-line state

> **The biology-shaped online-plasticity ideas mostly died. The live question is now a resource-allocation frontier: how much description, compute, and communication does a useful observation map require?**

No novelty, neuroscience, or hardware claim is currently supported.

## Ledger

```text
Smoke 0    WAIT/ROUTE plumbing                     original WAIT null constructed
Smoke 1    online branch growth                    fixed plastic capacity wins
Gate 2     continuous fixed-capacity ROUTE         address cache survives
Gate 3/4   adaptive admission                      strong fixed policies survive
Gate 5     Gabor-specific ROUTE                    generic RBF reproduces phase
Gate 6     learned vs random-frozen receiver       large parameter-count gap
Gate 7/8   mixed/pre-collapse allocation           no interior Y block
Gate 9     PCA/DCT fixed-basis attack              PCA closes Gate-6 accuracy gap
```

## Closed branches

### Growth

Two preallocated plastic anchors beat online branch growth in the recurring A/B toy:

```text
grow       total work 1074.0
fixedcap   total work  613.2
```

Same final accuracy and steady state. Fair branch value is negative.

```text
GROWTH_EARNS_KEEP = False
```

Do not reopen growth unless recurring useful views greatly exceed fixed capacity and fixed-capacity replacement/cache policies are present from the start.

### Adaptive admission

Gate 3 and Gate 4 both failed to beat robust fixed admission policies, including a within-run nonstationary sequence.

```text
ADMISSION_BRANCH_STATUS = CLOSED
```

Do not add a neural conductor or more hazard/PROBE knobs to the same synthetic family.

### Gabor-specific online ROUTE

A generic smooth RBF observation manifold reproduced the cache<->ROUTE sign change across all five drift scales.

```text
GABOR_SPECIFIC_CLAIM_EARNS_KEEP = False
```

Frequency/splat geometry is not the demonstrated cause of the online routing phase.

## Gate 6 — useful result, now narrowed

Task: `sklearn` handwritten-digit classification.

Every constrained model transmits exactly **16 real measurements**.

Eight complex Gabor receivers learn only:

```text
x, y, frequency, orientation
```

Receiver geometry = `32` trainable scalars. Linear ten-class head = `170`.

```text
learned receiver + linear = 202 trainable parameters
```

Original matched-budget attacker:

```text
same random initial Gabor geometry, frozen
+ H=7 downstream MLP
= 199 trainable params
```

Eight splits:

```text
learned receiver + linear          202 p   95.24%
random-frozen Gabor + H7 MLP       199 p   89.76%
```

Increasing only downstream decoder capacity behind the same frozen 16 values gave:

```text
H=7      199 p    89.76%
H=24     658 p    92.85%
H=32     874 p    93.61%
H=40    1090 p    93.99%
H=48    1306 p    94.31%
```

So a large decoder could recover the information. The strong information-ceiling claim was already false.

## Gate 9 — missing strong fixed basis changes the center again

Gate 6's fixed receiver was **random**. That was a weak representation baseline.

Gate 9 adds:

```text
PCA-16   unsupervised training-set subspace
DCT-16   fixed data-free low-frequency basis
```

Both emit the same 16 real values and use the same 170-parameter linear head.

Independent deterministic reproduction on split IDs `6000..6007`:

```text
PCA-16 + linear      95.42%
DCT-16 + linear      92.85%
```

Compare Gate 6 reported learned Gabor mean:

```text
learned Gabor        95.24%
```

Therefore:

> **PCA essentially closes the Gate-6 accuracy gap. The original +5.49-point story was substantially 'random frozen Gabors are a bad 16-channel basis'.**

Do not center the repo on 'learning what to observe beats fixed sensing'.

## What actually survives: compact measurement-map description

Let input dimension be `D`; output width remains `M=16`.

Dense linear measurement map:

```text
16 * D coefficients
```

Eight complex Gabor receivers:

```text
8 * 4 geometry scalars = 32
```

Description ratio:

```text
(16D)/32 = D/2
```

Examples:

```text
D=64    ->   1024 dense coefficients / 32 geometry = 32x
D=784   ->  12544 dense coefficients / 32 geometry = 392x
```

PCA also needs a `D`-value centering mean if stored explicitly.

At FP32 on the 8x8 task:

```text
Gabor geometry + linear head           808 B
PCA matrix + mean + linear head       5032 B
```

The candidate statement is now:

> **A short structured description of an observation map can approach the task quality of a much more richly described dense projection.**

This is not yet a scaling law.

## FLOP / egress correction

The old ~6.5x trainable-parameter headline does not imply ~6.5x compute.

If the filters are digitally materialized, all 16-channel linear measurements pay roughly:

```text
16 * D projection MACs
```

For `D=64`:

```text
learned Gabor + linear             1024 + 160 = 1184 MACs
fixed Gabor + H48 decoder          1024 + 768 + 480 = 2272 MACs
```

So the simple inference-MAC advantage is about `1.9x`, ignoring nonlinear/generation costs.

All Gate-6/9 arms also cross the receiver boundary with exactly:

```text
16 FP32 values = 64 bytes/sample
```

so Gate 6 contains no egress-bandwidth advantage.

## SpectralNeuron relation

`anttiluode/SpectralNeuron` is the rung below this one on the same observation-operator ladder.

Its bucket collapses a shared waveform to total power; its resonant forks preserve selective frequency channels. Three channels on one noisy wire achieved roughly:

```text
fork self/crosstalk ratio     3.1x
bucket ratio                  1.0x
```

with finite off-diagonal leakage up to about `.34`.

That experiment measures something Gate 6 fixed by fiat: **logical channels sharing a physical medium interfere**.

The combined abstraction is not 'frequency computation'. It is:

```text
selectivity
    +
measurement-map description cost
    +
shared-medium / egress interference
    +
downstream decoder cost
```

See `docs/SPECTRALNEURON_RELATION.md`.

## Gate 8 remains a null

At fixed 16-wide carrier and roughly ~750 trainable parameters, increasing private Gabor branches and locally collapsing them did not produce an interior winner:

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

## Current decisive question: does the exchange rate scale?

The structured-map hypothesis predicts:

```text
structured description       O(1) per receiver
dense map description        O(D) per output channel
```

The ratio therefore grows automatically with input dimension. What is **not** automatic is whether useful accuracy/compute efficiency grows with it.

Next serious experiment must change `D` / dataset while keeping:

```text
16 transmitted values
8 compact receiver objects
same geometry parameter count
strong PCA/DCT fixed bases
matched fixed structured receiver + decoder frontier
```

Measure:

```text
accuracy
map-description bytes
materialized model bytes
MACs/FLOPs
wall time
memory traffic
egress bytes
```

Verdicts:

```text
accuracy exchange rate decays -> note / compression curiosity
holds while description ratio grows -> useful edge/embedded rule
grows with D -> candidate allocation law
```

## Stop lines

- Admission branch closed.
- Growth branch closed for capacity-matched two-view worlds.
- Gabor-specific online routing claim closed.
- No interior pre-collapse Y block found.
- Gate 6 no longer establishes learned sensing vs a good fixed basis; PCA closes that gap.
- Do not quote the 6.5x parameter ratio as a FLOP ratio.
- Do not call 16-channel width an egress win; every Gate-6/9 arm emits the same 64 FP32 bytes.
- Do not claim frequency is the general mechanism; SpectralNeuron demonstrates selectivity/FDM, not unique frequency computation.
- The next claim must survive scale and strong fixed-basis controls.
