# SplatNeuron

> **How much description, compute, communication, and selectivity does a useful observation map require?**

SplatNeuron began as “splats as neurons.” Strong controls removed most of that story. The surviving project is an **observer-resource frontier**: how much one-time observer structure is required to expose a task-relevant subspace, how much repeated logical measurement width remains, and how those costs depend on task complexity and alignment to the observation vocabulary.

The full `agent/route-grow` research history has now been merged into `main` with its negative results preserved.

A separate biological continuation now lives at [`anttiluode/SplatNeuronPlusField`](https://github.com/anttiluode/SplatNeuronPlusField). Do not mix its field/ephaptic hypotheses back into the observer-resource claims here.

## Current ledger

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
Gate10c    frequency specificity                   Gaussian derivatives match Gabor
Gate 11    literal operator-map bits               compact family useful at 24 B on digits
Gate 11b   D=784 digit replication                 fixed family remains expressive
Gate 12    CIFAR complexity attack                 useful reality check, K uncontrolled
Gate 13    D x K x structure factorial             conditional width/configuration frontier
Gate 13b   supervised DCT row-selection attack     no new primary frontier point
Gate 13c   generic learned Givens attack           9/9 K8/local cells remain below T95
```

## Central result

Gate 13 independently swept:

```text
sampled dimension D     1024, 2304, 4096
task-relevant factors K 2, 4, 8, 16
structure               local, mixed, dense
logical width M         8, 16, 24, 32, 48, 64
world seeds              13100, 13101, 13102
```

At the common validation-defined `T95` target, cells where paying for a learned local observer reduced the required logical interface were:

```text
local   28 / 36
mixed   13 / 36
dense    3 / 36
```

For local `K=2,4,8`, the trade replicated in `27/27` cells.

Median local frontier:

```text
K      learned local observer       zero/near-zero-map endpoint
2      M=8    ~16 B                 M=32
4      M=24   ~48 B                 M=32
8      M=32   ~96 B                 M=48
16     M=48  ~144 B                 M=48
```

The useful interpretation is not “geometry wins.” It is:

> **A useful observation subspace can have a short description in one vocabulary and a long description in another. When the task-relevant structure aligns with a compact local vocabulary, one-time observer configuration can buy a smaller repeated logical interface. Dense rotation and higher task complexity remove that advantage.**

For the representative `K=8` aligned world, roughly `48–96` task-specific map bytes buy a reduction from `M=48` to `M=24–32`. Under dense rotation the exchange largely disappears.

## Attacks that matter

### Gate 13b — supervised shared transform

A shared DCT/sign-DCT dictionary with supervised row selection was charged only the subset index. On the primary `K=8/local/T95` cells it still required `M=48` in `9/9` cells. Ordinary fixed DCT already reaches at `M=48` with zero task-specific operator bytes, so selected DCT is not a new Pareto point there.

### Gate 13c — generic continuous structured operator

A generic fixed-topology Givens circuit was trained around a 48-row selected-DCT pool with up to `384` learned angles, no local position/scale/orientation vocabulary, and the same `M=24/32` targets.

Result:

```text
ATTACKER_FAIL  9 / 9
median best-M32 shortfall to T95  0.167 percentage points
closest miss                      0.033 pp
worst miss                        0.434 pp
```

The attacker was not inert; it recovered most of the missing task information and then stopped just short. This is therefore a **description-language** result, not a claim that generic structured matrices are weak.

## What is closed

```text
online branch growth                 CLOSED in matched-capacity toy
adaptive admission                   CLOSED
Gabor/frequency-specific mechanism   CLOSED
interior pre-collapse Y block        NOT FOUND
learned observer > strong PCA        NOT ESTABLISHED on Gate 9
universal geometry advantage         FALSE; dense rotation kills it
```

Do not reopen these without a genuinely new experiment.

## Resource currencies

Do not collapse these into one “efficiency” number:

```text
task error
operator-description bits
materialized operator RAM
observation compute
logical width
per-sample representation bits
physical carrier bandwidth / SNR / crosstalk
receiver state / compute
decoder state / compute
inference latency
training/search compute
training/search time / restarts
```

The current Gate 13 headline concerns **operator description versus logical width**. `M` is not bits/sample.

## Next legitimate continuation inside this repo

If SplatNeuron continues, the next experiment is the literal repeated-rate gate:

```text
L_map    one-time task-specific observer bits
L_z      per-sample representation bits after an explicit codec
R_task   held-out task distortion
```

Question:

> **Does paying one-time observer configuration bits reduce the minimum per-sample representation bits required at the same task error?**

For an observer reused `N` times, the natural amortized quantity is

```text
L_map / N + L_z
```

but the equation is not the contribution; the measured crossover under matched attackers would be.

## Prior-art boundary

The broad ingredients are established: learned sensing, task-aware acquisition, sensor placement, PCA/DCT/random projections, Givens/Butterfly/Monarch-like structured operators, quantization, MDL/model-description accounting, and multi-objective resource tradeoffs.

The candidate contribution is therefore modest and conditional: a worked observer-resource protocol plus the controlled `D x K x structure` interaction.

## Transition to SplatNeuronPlusField

The newer repo starts from a different question:

> **What changes when neuron-like units inhabit both an addressed synaptic graph and a metric extracellular coupling geometry, with quasi-static electric potential kept distinct from genuinely slow extracellular ionic state?**

That is not a continuation of Gate 13's empirical claim; it is a new hypothesis family with new attackers.

See [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md) for the frozen handoff and stop lines.
