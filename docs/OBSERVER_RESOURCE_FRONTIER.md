# Observer resource frontier

Date: 2026-08-17

This note is the abstraction that survived the SpectralNeuron/SplatNeuron comparison.

## One pipeline

Write the system as

```text
rich source x
    |
    v
observation map C_theta
    |
    v
logical consequences z
    |
    v
physical/shared channel H
    |
    v
received medium y
    |
    v
receiver/demultiplexer R
    |
    v
recovered consequences z_hat
    |
    v
decoder g_phi
    |
    v
task output t_hat
```

or

```text
z      = C_theta(x)
y      = H(z) + noise
z_hat  = R(y)
t_hat  = g_phi(z_hat)
```

Different repos froze different pieces of this pipeline.

## SpectralNeuron varies selectivity and physical interference

In `anttiluode/SpectralNeuron`, several modulated signals are summed onto one noisy wire.

The bucket readout collapses the medium to total power. The resonant forks implement selective demultiplexers.

Measured three-channel result:

```text
fork    mean self correlation ~0.62
        mean crosstalk        ~0.20
        self/crosstalk ratio   3.1x

bucket  mean self correlation ~0.32
        mean crosstalk        ~0.32
        ratio                  1.0x
```

So SpectralNeuron exposes a resource that most SplatNeuron gates fixed by fiat:

> **logical observation channels sharing a physical medium have finite separation and crosstalk.**

Frequency is only one implementation of selective `R`/`H`.

## SplatNeuron Gate 6/9 varies observation-map and decoder cost

Gate 6/9 effectively sets the physical channel to an ideal identity and fixes:

```text
logical width M = 16 real values
```

Then it asks how to produce/use those 16 values.

Current 8x8 digits controls:

```text
PCA-16 + linear           ~95.4%
learned compact Gabor     ~95.2%
DCT-16 + linear           ~92.9%
```

The important difference is map description:

```text
PCA map      M*D dense coefficients
Gabor map    32 geometry scalars for 8 complex receivers
DCT          algorithmic / near-zero learned map description
```

and the decoder cost behind the map.

## Resource vector

A future claim should not compress all costs into one word such as "efficiency".

For an observation/decoder system report at least:

```text
R_task      task error / accuracy
L_map       description bits/bytes for C_theta
S_map       materialized measurement-map storage
Q_sense     sensing/projection MACs, FLOPs or physical work
M_logic     logical consequence width
B_egress    bytes crossing the receiver boundary
P_phys      number/bandwidth of physical carriers
I_cross     crosstalk / interference matrix or summary
Q_decode    downstream compute
S_decode    downstream state/model bytes
latency     measured wall time where relevant
```

The scientific object is the Pareto frontier

```text
R_task  versus  (L_map, S_map, Q_sense, M_logic,
                  B_egress, P_phys, I_cross,
                  Q_decode, S_decode, latency)
```

not a single parameter-count ratio.

## Why this matters for the current data

Gate 9 already shows that two resource axes scale in opposite directions for a generic digital implementation:

```text
input dimension D grows

PCA/Gabor map-description ratio
    (16D)/32 = D/2
    -> grows linearly

fixed-H48 / compact-linear digital MAC ratio
    (16D + 1248)/(16D + 160)
    -> tends to 1
```

Thus a compact parameterization can become dramatically cheaper to *describe/store* while becoming almost no cheaper to evaluate as dense software.

If the receiver is implemented physically, procedurally, sparsely, or with a specialized kernel, that compute conclusion may change. It must be measured.

## Direct bridge experiment

The missing experiment should stop treating 16 logical channels as sixteen perfect wires.

Take a learned/fixed observation map producing `M` logical consequences, then force them through a controlled shared physical channel:

```text
x -> C_theta -> z in R^M
                 |
                 v
          shared channel H
          physical width P < M
                 |
                 v
          selective receiver R
                 |
                 v
               z_hat
                 |
                 v
              decoder
```

Compare observation maps under matched:

```text
M logical width
P physical carrier width
channel noise
map-description budget
receiver/demultiplexer budget
decoder budget
```

Sweep:

```text
M / P compression ratio
crosstalk / channel condition
receiver selectivity
input dimension D
```

Measure jointly:

```text
task accuracy
full crosstalk matrix
map description bytes
physical carrier count/bandwidth
receiver compute
decoder compute
```

Frequency-division multiplexing can be one arm, but a matched generic linear mixing/demixing channel is mandatory so frequency cannot win by narrative.

## The possible allocation law

A strong result would not be:

> frequency is how neurons compute.

Nor:

> learning the sensor is new.

It would look more like:

> **For a fixed task error, there is a measurable exchange rate between how richly an observation map is described, how many consequences it exports, how much those consequences interfere on the physical carrier, and how much downstream decoding is required. Structured observation families can occupy a useful part of that frontier when their map description grows more slowly than an unstructured measurement matrix.**

Gate 10 tests only one slice of that statement: whether the compact-map accuracy survives when `D` increases from 64 to 784.
