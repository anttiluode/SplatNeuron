# SplatNeuron — frozen handoff

Date: 2026-08-18

## One-line state

> **The strongest surviving result is a conditional observer-description frontier: when task-relevant structure aligns with a compact local observation vocabulary, spending one-time task-specific map bits can reduce repeated logical measurement width; the advantage weakens with mixing and disappears under high task complexity/dense rotation.**

This is not a neuron result, not a frequency result, not a growth result, and not a universal sensing theorem.

## Repository state

- `agent/route-grow` has been merged to `main` with the experimental history preserved.
- `main` is now the canonical branch for this project.
- heavy Gate 13/13b/13c workflows remain completed/manual; routine CI should stay lightweight.
- the new biological/field hypothesis family has moved to `anttiluode/SplatNeuronPlusField`.

## Ledger through the split

```text
Smoke 0    WAIT/ROUTE plumbing                     original WAIT null constructed
Smoke 1    online branch growth                    fixed plastic capacity wins
Gate 2     continuous fixed-capacity ROUTE         address cache survives
Gate 3/4   adaptive admission                      strong fixed policies survive
Gate 5     Gabor-specific ROUTE                    generic smooth manifold reproduces phase
Gate 6     learned vs random-frozen receiver       large weak-baseline gap
Gate 7/8   mixed/pre-collapse allocation           no interior Y block
Gate 9     PCA/DCT attack                          PCA closes Gate-6 headline
Gate 10    MNIST scale                             resource currencies diverge
Gate10c    Gabor/frequency specificity             Gaussian derivatives match Gabor
Gate 11    literal operator-map bits               compact family useful at 24 B on digits
Gate 11b   D=784 digit replication                 fixed family remains expressive
Gate 12    CIFAR complexity attack                 useful reality check, K uncontrolled
Gate 13    D x K x structure factorial             conditional width/configuration frontier
Gate 13b   supervised DCT selection                no new primary frontier point
Gate 13c   generic learned Givens circuit          9/9 K8/local cells remain below T95
```

## Closed stories

```text
online branch growth               CLOSED in matched-capacity toy
adaptive admission                 CLOSED
Gabor/frequency-specific mechanism CLOSED
interior pre-collapse Y block      NOT FOUND
learned observer > strong PCA      NOT ESTABLISHED on Gate 9
universal geometry advantage       FALSE; dense rotation kills it
```

Do not reopen these without a genuinely different hypothesis/attacker.

## Gate 13 central result

Frozen factorial:

```text
D          1024, 2304, 4096 sampled dimensions
K          2, 4, 8, 16 task-relevant latent factors
structure  local, mixed, dense
nuisance   32 independent latent factors
tasks      32 binary tasks
seeds      13100, 13101, 13102
M          8, 16, 24, 32, 48, 64 logical measurements
```

Primary `T95` width-trade counts:

```text
local   28 / 36
mixed   13 / 36
dense    3 / 36
```

For local `K=2,4,8`, the trade replicated in `27/27` cells.

Median local frontier:

```text
K      learned local map              zero/near-zero-map endpoint
2      M=8    ~16 B                   M=32
4      M=24   ~48 B                   M=32
8      M=32   ~96 B                   M=48
16     M=48  ~144 B                   M=48
```

Representative supported statement:

> **roughly 48–96 task-specific map bytes buy a 48 -> 24–32 logical-width reduction in the aligned K=8 world; the exchange largely disappears after dense rotation of the same latent task.**

This says alignment to the observation vocabulary is load-bearing.

## Gate 13b attack

Supervised task-adapted DCT/sign-DCT row selection was charged only subset-index bits. In the primary `K=8/local/T95` cells it still required `M=48` in `9/9` cells.

Important accounting:

```text
fixed DCT prefix       M=48   L_map=0 B       reaches
selected DCT           M=48   L_map=35–47 B   reaches
```

Therefore selected DCT does not create a better primary Pareto point.

## Gate 13c attack

Generic fixed-topology Givens circuits around the 48-row selected-DCT pool:

```text
rounds       1    2    4    8    16
angles R    24   48   96  192   384
M            24 or 32
training     3 restarts x 220 steps
```

Primary result:

```text
ATTACKER_FAIL  9 / 9
median best-M32 shortfall to T95  0.167 percentage points
minimum                            0.033 pp
maximum                            0.434 pp
```

The circuit recovered most of the missing information; this is not evidence that generic structured matrices are weak.

Useful interpretation:

> **the aligned local vocabulary appears to provide a shorter coordinate chart for this useful observation subspace than the tested generic parameterization.**

No lower bound or uniqueness claim follows.

## Resource accounting that must remain explicit

```text
task error
operator-description bits
materialized operator RAM
observation compute
logical width
per-sample representation bits
physical channel cost
receiver state/compute
decoder state/compute
latency
training/search compute
training/search time and restarts
```

The current result is `L_map <-> M`. It is **not yet** `L_map <-> L_z`.

## Next legitimate SplatNeuron gate

If this repo is resumed, make the repeated representation rate literal:

```text
L_map    one-time task-specific observation-operator bits
L_z      per-sample representation bits after quantization/codec
R_task   held-out task distortion
```

Question:

> **Does paying one-time configuration bits for an aligned observer reduce minimum per-sample representation bits at the same task error?**

Until then `M=32 < M=48` is a logical-interface statement, not a bandwidth statement.

## Prior-art boundary

Broad ingredients are occupied: learned sensing, sensor placement, random projections, PCA/DCT, structured learned transforms, Givens/Butterfly/Monarch-style operators, quantization, MDL, model-description accounting, and multi-resource Pareto analysis.

The possible contribution is a worked resource protocol plus the controlled alignment interaction, not any one ingredient.

## Split to SplatNeuronPlusField

A separate thread emerged after this observer work:

```text
synaptic topology       addressed / rewireable
extracellular geometry  metric / position-and-orientation induced
```

with the additional physics distinction:

```text
quasi-static electric potential   memoryless instantaneous operator
slow ionic/metabolic milieu       genuine shared dynamical state
```

That hypothesis family now lives in `SplatNeuronPlusField` so that it can fail independently without contaminating the Gate 13 observer result.

## Stop lines

- do not call Gate 13 a universal geometry law;
- do not call Gate 13c a proof against Butterfly/Monarch/BTT;
- do not convert `M` directly into bits/sample;
- do not resurrect frequency/phase as mechanism from this branch;
- do not resurrect growth without matched fixed-capacity controls;
- do not import ephaptic/field claims into this repo's empirical result;
- never infer science from a green CI badge.
