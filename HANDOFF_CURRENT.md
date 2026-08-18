# SplatNeuron — current handoff

Date: 2026-08-18

## One-line state

> **The live result is a conditional description-complexity frontier for observation maps: when task structure is spatially aligned, a compact local sensing vocabulary can spend task-specific configuration bits to reduce repeated logical measurement width; that advantage disappears as alignment/complexity worsen.**

This is **not** a neuron result, not a frequency result, not evidence for dendritic growth, and not a new general sensing theorem.

## Current ledger

```text
Smoke 0    WAIT/ROUTE plumbing                     original WAIT null constructed
Smoke 1    online branch growth                    fixed plastic capacity wins
Gate 2     continuous fixed-capacity ROUTE         address cache survives
Gate 3/4   adaptive admission                      strong fixed policies survive
Gate 5     Gabor-specific ROUTE                    generic smooth manifold reproduces phase
Gate 6     learned vs random-frozen receiver       large weak-baseline gap
Gate 7/8   mixed/pre-collapse allocation           no interior Y block
Gate 9     PCA/DCT fixed-basis attack              PCA closes Gate-6 headline
Gate 10    MNIST scale                             resource currencies diverge
Gate10c    Gabor/frequency specificity             Gaussian derivatives match Gabor
Gate 11    literal operator-map bits               compact family useful at 24 B on digits
Gate 11b   D=784 digit replication                 fixed family remains expressive
Gate 12    CIFAR complexity attack                 useful but not controlled K
Gate 13    D x K x structure factorial             conditional width/configuration frontier
Gate 13b   supervised index-only DCT attack        does not reduce K8 local M=48 endpoint
Gate 13c   generic learned Givens circuit attack   9/9 primary cells remain below T95
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

Do not reopen these without a genuinely new attacker/task.

## Gate 13 — current central result

Synthetic factorial:

```text
D          1024, 2304, 4096
K          2, 4, 8, 16 task-relevant latent factors
structure  local, mixed, dense
nuisance   32 independent latent factors
tasks      32 binary tasks
seeds      13100, 13101, 13102
M          8,16,24,32,48,64 logical measurements
```

The worlds are orthonormalized so latent rank/SNR are held fixed while alignment of task-relevant structure to the local observation family changes.

Primary T95 width-trade counts across 36 cells per structure:

```text
local   28 / 36
mixed   13 / 36
dense    3 / 36
```

For local `K=2,4,8`, the trade replicates in:

```text
27 / 27 cells
```

Median T95 local frontier:

```text
K      learned local map              zero/near-zero-map endpoint
2      M=8    ~16 B                   M=32
4      M=24   ~48 B                   M=32
8      M=32   ~96 B                   M=48
16     M=48  ~144 B                   M=48
```

Representative K=8 statement:

> **roughly 48–96 task-specific map bytes buy a 48 -> 24–32 logical-width reduction in the aligned world.**

At K=16 the benefit is essentially exhausted. Under dense rotation it largely disappears.

This is the key interaction. `geometry wins on a generator built from local structure` would be trivial; `geometry wins locally and loses after a controlled dense rotation of the same latent task` is the useful receipt.

## Gate 13 preflight / theory guards

- Signal-support fraction remains approximately constant as D changes within each structure regime.
- Task bank has full rank K.
- Seeded random projection behavior matches the isotropic-subspace prediction closely.
- The simple random theory explains why `M=48` recovers the K<=16 latent span.
- DCT/random own the zero/near-zero-task-specific-bit edge.
- Learned geometry pays real discovery debt: 3 restarts x 220 steps per trained configuration.

Do not infer science from workflow success; green CI only says the registered computation reproduced.

## Gate 13b — supervised shared-dictionary attack

Attackers:

```text
selected DCT
selected fixed-sign-DCT
```

Only subset indices are task-specific; charge:

```text
ceil(log2 binom(D,M)) bits
```

Frozen K=8/local/T95 result:

```text
selected DCT still needs M=48 in 9/9 cells
```

Important accounting correction:

```text
fixed DCT prefix       M=48   L_map=0 B       reaches T95
selected DCT           M=48   L_map=35–47 B   reaches T95
```

Therefore selected DCT is globally dominated by the original zero-byte DCT in the primary cells. It does **not** add a new frontier point and does not erase the geometry width reduction.

Pairwise-vs-geometry categories from the preregistered Gate13b analysis are still useful diagnostically, but must not be confused with the full multi-family Pareto frontier.

## Gate 13c — generic continuous structured attack

Attacker:

- start from Gate13b's task-selected 48-row DCT pool;
- apply a deterministic-topology learned Givens circuit;
- no spatial position, scale, orientation, frequency or locality parameters;
- only Givens angles are learned.

Registered sizes:

```text
rounds       1    2    4    8    16
angles R    24   48   96  192   384
M            24 or 32
training     3 restarts x 220 steps
```

Primary K=8/local/T95 result:

```text
ATTACKER_FAIL  9 / 9
```

No registered circuit reaches T95 at M=24 or M=32.

Best-M32 shortfall to T95 across the 9 cells:

```text
median   0.167 percentage points
minimum  0.033 pp
maximum  0.434 pp
```

The circuit is not inert. It raises selected-DCT M32 performance substantially:

```text
selected DCT M32     roughly 79–85%
best Givens M32      roughly 86.8–87.2%
local geometry       roughly 87.1–87.9%
T95                   roughly 87.0–87.4%
```

So the generic circuit recovers most of the task subspace but remains just below the registered receipt line.

### Useful description-language interpretation

A generic M-dimensional subspace of a 48-D pool has Grassmann dimension:

```text
M(48-M)
```

For K=8, if the useful M-dimensional subspace is constrained to contain the eight task-signal directions, the remaining family has dimension:

```text
(M-K)(48-M) = 384
```

for both M=24 and M=32.

The longest Gate13c circuit has 384 learned angles.

The local Gate13 M32 family uses 64 learned geometry coordinates before quantization.

This is **not a lower bound** and does not rule out better generic structured parameterizations. It gives the current empirical interpretation:

> **alignment makes the useful observation subspace compactly describable in the local vocabulary.**

That is an inductive-bias / description-language statement.

## Prior-art boundary

Broad ingredients are old:

```text
learned sensing / task-aware acquisition
sparse sensor placement
random projections
DCT / structured random transforms
Givens factorizations
Butterfly / Monarch / BTT structured matrices
operator quantization
multi-metric Pareto accounting
information-based complexity / n-widths
MDL / model-description accounting
```

Do not claim novelty from any one ingredient.

The candidate contribution, if it survives more attacks, is a **worked observer-resource protocol** with a surprisingly clean structure interaction, not discovery of structured sensing.

## Strongest supported statement

> **In the frozen synthetic D x K x structure factorial, a compact local observation family reduces the number of measurements required for a common task target when task-relevant factors are aligned with that family. The advantage weakens under mixing, disappears at high K/dense rotation, survives supervised DCT row selection, and survives the tested fixed-topology generic Givens circuit with up to 384 learned angles.**

Keep all qualifiers.

## What remains unresolved

- A stronger Butterfly/Monarch/BTT-style learned structured operator could still dominate.
- Gate13c topology is fixed and pair indices are not learned.
- The current output currency is **logical width M**, not literal transmitted/sample bits.
- Real datasets do not expose K or structure as clean controlled knobs.
- Novelty of the exact multi-currency protocol is not established.

## Next legitimate experiment

Do **not** build another neuron shape.

Make the repeated representation rate literal:

```text
L_map    one-time task-specific observation-operator bits
L_z      per-sample representation bits after quantization
R_task   held-out task distortion
```

Question:

> **Does paying one-time configuration bits for an aligned observer reduce the minimum per-sample representation bits needed at the same task error?**

This is the clean continuation of the original intuition `stable repeated use can justify persistent structure`, but in a form that can be killed.

Until this is measured, `M=32 < M=48` is only a logical-width result, not a communication-rate result.

## Workflow / branch state

- branch: `agent/route-grow`
- PR #1 remains **draft**
- `main` untouched
- Gate13 / Gate13b / Gate13c heavy workflows are completed and returned to manual dispatch
- routine CI remains lightweight

## Stop lines

- Do not reopen growth/admission/frequency stories.
- Do not call Gate13 a universal geometry law.
- Do not call Gate13c a proof against Butterfly/Monarch.
- Do not treat selected-DCT as a global frontier point at K8/local/T95; zero-byte DCT dominates it.
- Do not convert M directly into bits/sample without an explicit representation codec.
- Do not infer a scientific verdict from a green workflow badge.
