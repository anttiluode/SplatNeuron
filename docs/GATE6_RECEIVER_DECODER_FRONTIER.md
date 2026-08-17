# Gate 6 — learned receiver vs decoder frontier

Date: 2026-08-17

Status: **positive parameter-efficiency result; information-ceiling claim rejected.**

## Question

The routing work progressively killed three stronger stories:

- online branch growth was unnecessary once fixed capacity was controlled;
- adaptive admission did not beat strong fixed policies;
- the cache↔ROUTE phase was reproduced by a generic smooth manifold, so it was not Gabor-specific.

That leaves a different part of the original idea:

> **Can learning the observation map make a downstream computation simpler?**

Gate 6 tests this directly on `sklearn` handwritten digits.

## Fixed communication width

Every constrained model receives exactly **16 real measurements** from the image.

The learned Gabor receiver has eight complex filters, each emitting real and imaginary responses:

```text
8 complex receivers -> 16 real channels
```

Each receiver learns four geometry parameters:

```text
(x, y, frequency, orientation)
```

with fixed envelope width. Receiver geometry therefore contributes only `8 x 4 = 32` trainable scalars.

A linear ten-class decoder has `16 x 10 + 10 = 170` parameters, giving:

```text
learned receiver + linear head = 202 trainable parameters
```

## Matched downstream-state attacker

For each split the fixed-Gabor models start from **the exact same initial receiver geometry** as the learned-Gabor model, but receiver coordinates are frozen.

The matched-budget attacker spends its trainable parameters downstream:

```text
16 measurements -> hidden MLP -> 10 classes
```

At hidden width `H=7` it has `199` trainable parameters, essentially identical to the learned-receiver model's `202`.

## First deterministic replication

Four fresh stratified splits (`6000..6003`), deterministic model/optimizer initialization:

```text
model                                      params   mean test accuracy
---------------------------------------------------------------------
learned Gabor receivers + linear              202        94.51%
fixed same Gabor receivers + H=7 MLP           199        88.82%
learned 16 point receivers + linear            202        92.64%
learned Gaussian-pair receivers + linear       202        90.83%
fixed random dense projection + H=7 MLP        199        85.21%
full 64 pixels + linear                        650        96.53%
```

Paired learned-Gabor contrasts over those four splits:

```text
vs fixed same Gabor + matched MLP      +5.69 points  95% bootstrap CI [+4.44,+7.22]
vs learned point receivers             +1.87 points  CI includes zero
vs learned Gaussian-pair receivers     +3.68 points  CI positive
vs fixed random projection + MLP       +9.31 points  CI positive
```

The Gabor-vs-learned-point contrast is **not separated**, so this does not resurrect a Gabor-specific claim.

## Same-family geometry controls

To make sure the result was not merely an unfair Gabor-vs-other-family comparison, the generic observer families were also attacked with their own exact initial geometry frozen and the matched `H=7` MLP placed downstream.

Four splits:

```text
learned point geometry + linear       92.64%
fixed same point geometry + MLP       85.35%
delta                                 +7.29 points  CI [+4.44,+10.14]

learned Gaussian-pair geometry        90.83%
fixed same Gaussian-pair + MLP        84.10%
delta                                 +6.74 points  CI [+3.75,+10.76]
```

So the broad effect occurs in more than one receiver family:

> moving trainable budget into **what is observed** can outperform spending the same budget on a nonlinear decoder behind a fixed observation map.

## Does fixed observation destroy information?

This was the load-bearing attacker.

If a fixed receiver truly destroyed the class distinction, no downstream decoder should recover the learned-receiver score.

It did recover it.

With the same fixed 16 Gabor measurements, increase only hidden decoder width:

```text
hidden H   trainable params   mean accuracy over 8 splits
---------------------------------------------------------
7               199                    89.76%
24              658                    92.85%
32              874                    93.61%
40             1090                    93.99%
48             1306                    94.31%
```

The learned-receiver model over the same eight splits:

```text
202 params      95.24%
```

Paired learned-minus-fixed frontier:

```text
fixed H=7    (199 params)    +5.49 points   95% CI [+3.40,+7.15]
fixed H=24   (658 params)    +2.40 points   CI [+1.11,+3.68]
fixed H=32   (874 params)    +1.63 points   CI [+0.49,+2.71]
fixed H=40  (1090 params)    +1.25 points   CI [+0.31,+2.19]
fixed H=48  (1306 params)    +0.94 points   CI [-0.07,+1.94]
```

A validation-selected RBF-SVM on the fixed 16 Gabor features reached about `95.0%` on the first four splits.

Therefore the strong information-ceiling claim is false:

> **The fixed receiver still contains enough information. The learned receiver makes the required downstream map much cheaper.**

## Supported statement

The current positive SplatNeuron result is:

> **At fixed 16-channel communication width on handwritten-digit classification, jointly learning a low-parameter observation geometry can compile substantial downstream nonlinear computation into the receiver. In this experiment, a 202-parameter learned-observer/linear-decoder model reached the performance region that a fixed observation map required roughly a 1.3k-parameter nonlinear decoder to match.**

This is a **parameter-efficiency / computation-placement** result, not a novelty claim.

## Relation to the original idea

The phrase “learning creates an observable distinction” was too strong here. The distinction was already recoverable from fixed observations by a powerful enough decoder.

A better description is:

```text
fixed receiver
    -> awkward representation
    -> expensive downstream decision surface

learned receiver
    -> task-aligned representation
    -> cheap linear decision surface
```

In that sense, learning the receiver **compiles part of the computation into observation geometry**.

## Important limitations

- `sklearn` digits is a small, low-resolution dataset.
- Four splits were used for the broad family controls; eight for the main receiver-decoder frontier.
- The learned receivers adapt during training, not within lifetime/inference.
- Gabor-specific superiority is not established; learned point receivers are a strong attacker.
- Parameter count is not FLOPs, wall time, memory traffic, or energy.
- A full 64-pixel linear model remains a stronger accuracy ceiling at larger communication width.
- This is closely related to ordinary feature learning / learned front ends; no claim of a new ML principle is made yet.

## Next gate

The next useful test is a **pre-collapse receiver frontier** rather than another neuron metaphor:

```text
fixed transmitted width
fixed or carefully accounted total compute/parameters
trade budget between:
    receiver / local feature generation
    downstream reducer / decoder
```

Then ask whether an interior allocation beats both hard endpoints across more than this one small dataset.

That is the point where the SplatNeuron result can connect back to the broader receiver-relative / Y-block work without pretending the current digits experiment already proves it.
