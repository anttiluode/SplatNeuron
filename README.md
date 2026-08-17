# SplatNeuron

> **Where should a constrained computation spend its budget: on what it observes, on local collapse, or on decoding what was observed?**

SplatNeuron began as a speculative “splats as neurons” project. The repository is now a much narrower and more defensible research program about **observation geometry and computation placement**.

Strong controls killed most of the original story. One result survived clearly enough to become the new center of the repo.

## Current ledger

```text
Smoke 0    WAIT/ROUTE/CONSOLIDATE plumbing              useful only as plumbing
Boundary0  WAIT <-> oracle ROUTE                         analytic SNR/cost crossover
Smoke 1    ROUTE -> GROW                                 growth loses to fixed capacity
Gate 2     continuous off-grid ROUTE                     address cache survives
Boundary1  cache <-> ROUTE vs world drift               value region exists
Gate 3     adaptive hazard / PROBE                       strong fixed threshold survives
Gate 4     within-run self-tuning admission              fixed robust policy survives
Gate 5     Gabor vs matched generic smooth manifold      generic manifold reproduces phase
Gate 6     learned receiver vs decoder frontier          KEEP: parameter-efficiency result
Gate 7     ~200-param mixed allocation                   no interior optimum
Gate 8     pre-collapse private branch frontier          no interior Y block
```

No novelty, neuroscience, or hardware claim is made.

## The result that survived — Gate 6

On `sklearn` handwritten digits, every constrained model receives the same **16 real measurements**.

The learned-receiver model uses eight complex Gabor receivers. Each receiver learns only:

```text
x, y, frequency, orientation
```

so receiver geometry costs `8 x 4 = 32` trainable scalars. A linear ten-class decoder costs `170` more:

```text
learned receiver + linear decoder = 202 trainable parameters
```

The load-bearing baseline starts from the **exact same receiver geometry**, freezes it, and spends essentially the same trainable budget downstream:

```text
fixed receiver + H=7 nonlinear decoder = 199 parameters
```

Across eight deterministic stratified splits:

```text
learned receiver + linear          202 params    95.24%
fixed receiver + H=7 MLP           199 params    89.76%
```

Paired difference:

```text
+5.49 percentage points
95% bootstrap CI [+3.40, +7.15]
```

The effect is not specific to Gabors. On four family-control splits:

```text
learned point receivers + linear       92.64%
fixed same point receivers + MLP       85.35%

learned Gaussian-pair receivers        90.83%
fixed same Gaussian-pair + MLP         84.10%
```

So the surviving broad statement is:

> **At fixed transmitted width and a small trainable budget, learning what to observe can be substantially more parameter-efficient than freezing the observation map and spending the same budget on the decoder.**

See [`docs/GATE6_RECEIVER_DECODER_FRONTIER.md`](docs/GATE6_RECEIVER_DECODER_FRONTIER.md).

## But fixed receivers did not destroy the information

Gate 6 also attacks the stronger claim.

Keep the same fixed 16 Gabor measurements and increase only downstream decoder capacity:

```text
hidden H   trainable params   mean accuracy
-------------------------------------------
7               199              89.76%
24              658              92.85%
32              874              93.61%
40             1090              93.99%
48             1306              94.31%
```

The 202-parameter learned receiver remains at `95.24%`.

The learned-vs-fixed difference becomes statistically indistinguishable around the `H=48 / 1306 parameter` decoder. An RBF-SVM on the same fixed receiver features also reaches about `95%` on the first four splits.

Therefore:

> **Receiver learning did not create otherwise inaccessible class information. It compiled a difficult downstream decision surface into a task-aligned front end.**

That is a computation-placement / parameter-efficiency statement, not an information-theoretic one.

Run the reported frontier with:

```bash
pip install -e '.[gate6]'
python experiments/gate6_receiver_frontier.py --full
```

## Gate 8 — the hoped-for pre-collapse Y block did not appear

Gate 6 naturally suggests a stronger architecture: use **more private receiver branches than transmitted channels**, collapse locally to the same 16-wide carrier, and trade that local budget against downstream decoder capacity.

Gate 8 holds total trainable parameters near `~750` and carrier width at `16`:

```text
configuration             params   private branches   downstream
-----------------------------------------------------------------
B8 direct / H27             771          8             H=27
B10 collapse / H14          764         10             H=14
B12 collapse / H11          755         12             H=11
B14 collapse / H8           746         14             H=8
B16 collapse / linear       762         16             linear
```

Combined six-split means:

```text
B8 direct / H27            96.11%
B10 collapse / H14         94.95%
B12 collapse / H11         94.63%
B14 collapse / H8          93.84%
B16 collapse / linear      95.46%
```

The two hard endpoints are fairly close, but **no interior allocation beats them**.

```text
INTERIOR_Y_BLOCK_EARNS_KEEP = False
```

See [`docs/GATE8_PRECOLLAPSE_FRONTIER.md`](docs/GATE8_PRECOLLAPSE_FRONTIER.md).

## Earlier routing / plasticity results

The early online-plasticity branch remains useful mainly because it established stopping lines:

- the first WAIT null was constructed by machine-zero receiver/target overlap;
- a repaired nonzero-overlap test gives an analytic WAIT↔ROUTE SNR/cost boundary;
- online branch growth lost to two preallocated plastic receiver anchors;
- continuous ROUTE failed to separate from a fixed address cache on its frozen confirmation;
- cache vs ROUTE changes sign as environmental drift increases;
- hazard-adaptive admission and a PROBE band both failed to beat a validation-selected fixed threshold;
- even a within-run self-tuning threshold failed a robust fixed policy;
- a matched generic RBF observation manifold reproduced the Gabor cache↔ROUTE phase.

Those experiments live in `docs/GATE0...` through `docs/GATE5...` and are summarized in [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md).

## Prior art boundary

The live Gate 6 effect is intentionally framed as a **controlled frontier**, not a discovery of task-driven sensing.

Learnable Gabor front ends, learned measurement matrices, differentiable sensor layouts, and joint camera/perception optimization already occupy the broad territory. See [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md).

## What SplatNeuron is now

The repo is no longer centered on:

```text
"neurons are splats"
```

or:

```text
"geometry creates information"
```

The current useful question is:

```text
fixed communication width
        +
limited total trainable/compute budget
        ↓
where should computation live?

receiver / feature generation
        vs
local pre-collapse reduction
        vs
downstream decoder
```

Gate 6 says receiver adaptation can be a very efficient place to spend a small budget.

Gate 8 says simply adding more private branches and a dense local collapse does **not** produce the hoped-for interior architecture.

That is the current scientific state.
