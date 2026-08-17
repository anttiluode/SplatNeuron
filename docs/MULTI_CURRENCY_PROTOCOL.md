# Multi-currency observer protocol

Date: 2026-08-17

This is the most general object currently supported by the SplatNeuron experiments.

Do **not** summarize a sensing/observer architecture with one number called `efficiency`.

## Pipeline

```text
input x
  -> observation operator C_theta
  -> M logical consequences z
  -> optional physical/shared channel H
  -> receiver / demultiplexer R
  -> recovered consequences z_hat
  -> task decoder g_phi
  -> output
```

## Resource vector

For each system report, at minimum:

```text
R_task      held-out task error / accuracy
L_map       learned operator-description payload (bits/bytes)
S_map       materialized operator storage if expanded
Q_map       observation/projection compute or physical work
M_logic     logical consequence width
B_egress    data bytes crossing the logical boundary per sample
P_phys      physical carrier count / bandwidth where applicable
I_cross     crosstalk/interference measure or matrix
S_rx        receiver/demultiplexer state
Q_rx        receiver/demultiplexer compute
S_decode    task-decoder state
Q_decode    task-decoder compute
latency     measured wall time
```

Also state which algorithmic family description is treated as shared side information. `L_map` is therefore a conditional learned-parameter payload, not Kolmogorov complexity.

## Fixed-error rule

Comparing each family `within 1 point of its own ceiling` is useful for quantization robustness but is **not** an iso-task comparison.

Primary frontier comparisons should use a common target chosen without test leakage.

Gate 12 protocol:

```text
1. train full-pixel reference
2. define common target from validation performance
3. fit candidate observation families
4. quantize observation map after training
5. never retrain decoder per bit rate
6. select candidate rate/capacity using validation only
7. report selected system on held-out test
```

## Why currencies can move in opposite directions

For a dense `M x D` digital map and a compact structured map with `P` learned geometry values:

```text
operator-description count
    dense        ~ M D
    structured   ~ P
```

If `P` and `M` stay fixed while `D` grows, the description ratio grows automatically. That arithmetic is **not** an empirical discovery.

But a materialized dense digital implementation may still require approximately:

```text
Q_map ~ M D MACs/sample
```

for both the dense and structured map once structured filters are expanded.

Thus:

```text
operator description advantage can grow
while
runtime dense-MAC advantage tends toward 1
```

This is exactly the shape observed between the 8x8 and MNIST experiments.

The empirical question is whether the structured family can keep `P` / `M` small enough to meet a common task-error target as the data become more complex.

## Current worked counterexample

Existing Gates 9-11b produced the qualitative table:

```text
D up

nominal map-description ratio       up strongly
ordinary dense digital MAC ratio    down toward 1
small-decoder allocation advantage  down
logical egress width                flat
```

So the phrase:

> `N x more efficient`

is scientifically incomplete unless `N` is attached to a named resource axis and a common task target.

## Pareto reporting

Never hide one cost inside another without also exposing the components.

At a common target, report at least three selections:

```text
minimum map payload
minimum total explicit state
minimum logical egress width
```

and show the full resource vector for each selected point.

A zero-map algorithmic transform such as DCT can legitimately own the `L_map=0` corner while paying more in logical width, decoder state or task error.

Likewise, a compact parametric map can own a low-`L_map` corner without being faster in dense software.

## What would count as a stronger law

A useful empirical allocation law would relate **required** resources at a common error target, for example:

```text
required L_map versus task complexity
required M_logic versus task complexity
required Q_decode versus L_map
required L_map versus I_cross under a shared carrier
```

not merely compare nominal parameterization dimensions.

Gate 12 is the first experiment in the repo designed around this corrected rule.
