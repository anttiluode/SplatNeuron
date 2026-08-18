# Observer resource frontier

Date: 2026-08-17

This note is the abstraction that survived the SpectralNeuron/SplatNeuron comparison.

## One pipeline

```text
rich source x
    -> observation map C_theta
    -> logical consequences z
    -> physical/shared channel H
    -> received medium y
    -> receiver/demultiplexer R
    -> recovered consequences z_hat
    -> decoder g_phi
    -> task output
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

The bucket readout collapses the medium to total power. Resonant forks implement selective demultiplexers.

Measured three-channel result:

```text
fork    mean self correlation ~0.62
        mean crosstalk        ~0.20
        self/crosstalk ratio   3.1x

bucket  mean self correlation ~0.32
        mean crosstalk        ~0.32
        ratio                  1.0x
```

So SpectralNeuron exposes a resource most SplatNeuron gates fixed by fiat:

> **logical observation channels sharing a physical medium have finite separation and crosstalk.**

Frequency is one implementation of selective `H/R`, not the general principle.

## SplatNeuron varies observer description and decoder cost

Most SplatNeuron learning gates idealize the physical channel and fix:

```text
logical width M = 16 real values
```

Then they ask how costly it is to produce and decode those sixteen consequences.

Gate 9 on 8x8 digits:

```text
PCA-16 + linear           95.42%
learned compact Gabor     95.24%
DCT-16 + linear           92.85%
```

PCA closes the full-precision accuracy gap. The remaining question became observer description rate.

Gate 10c then killed frequency specificity:

```text
Gabor                          88.33% on MNIST
steerable Gaussian derivative  88.56%
```

at the same 32-map-scalar / 16-output / linear-head budget.

So the compact family should be understood as **structured localized selectivity**, not as frequency coding.

## Resource vector

Do not compress all costs into the word `efficiency`.

For an observation/decoder system report at least:

```text
R_task      task error / accuracy
L_map       serialized description bits/bytes for C_theta
S_map       materialized measurement-map storage
Q_sense     sensing/projection MACs, FLOPs or physical work
M_logic     logical consequence width
B_egress    bytes crossing the logical receiver boundary
P_phys      number/bandwidth of physical carriers
I_cross     crosstalk / interference matrix or summary
Q_decode    downstream compute
S_decode    downstream state/model bytes
latency     measured wall time where relevant
```

The scientific object is the Pareto frontier

```text
R_task versus (L_map, S_map, Q_sense, M_logic,
                B_egress, P_phys, I_cross,
                Q_decode, S_decode, latency)
```

not one parameter-count ratio.

# What Gates 11/11b added: L_map is now measured, not guessed

Gates 9-10 only counted nominal map scalars/coefficient entries.

Gate 11 preregistered a literal fixed-rate codec, froze the common FP32 decoder, quantized **only the observation map**, and physically bit-packed the codes.

Compact maps:

```text
32 normalized geometry values
known semantic ranges
no stored scale payload
```

PCA:

```text
16 dense rows
one FP32 maxabs scale per row
fixed-rate signed coefficient codes
training mean folded into decoder bias
```

DCT:

```text
algorithmic map
0 stored map bytes under shared protocol
```

## D=64

Fresh 8x8 splits `7200..7207`.

Smallest map payload within one percentage point of own full precision:

```text
Gabor                  24 B   94.10%
Gaussian derivative    24 B   93.68%
PCA                   576 B   93.65%
DCT                     0 B   90.73%
```

```text
PCA / compact map-rate ratio = 24.0x
```

The common 680-byte head reduces total-state ratio to:

```text
1256 / 704 = 1.78x
```

## D=784

Fresh MNIST seeds `9200/9201`, same codecs.

Within one point of own full precision:

```text
Gabor                   24 B   88.90%
Gaussian derivative     24 B   88.10%
PCA                   4768 B   85.78%
DCT                      0 B   83.94%
```

```text
PCA / compact map-rate ratio = 198.7x
```

Total observer+common-head state:

```text
5448 / 704 = 7.74x
```

## The empirical scaling receipt

```text
input dimension                  64 -> 784       12.25x
compact useful map payload       24 -> 24 B       1.00x
PCA useful map payload          576 -> 4768 B     8.28x
map-rate ratio                   24 -> 198.7x     8.28x
```

PCA's useful scalar precision actually **decreased** from four to three bits/coefficient at scale. The total payload still grew because the map remained dense.

This is the strongest current evidence for a real observer-description scaling effect.

## Compact parameters are high-leverage, not individually robust

At very low bits/value the compact map degrades much more sharply than PCA.

Gate 11, two bits/value:

```text
Gabor                 41.74%
Gaussian derivative   55.45%
PCA                   83.72%
```

Gate 11b, two bits/value:

```text
Gabor                 31.00%
Gaussian derivative   23.98%
PCA                   83.92%
```

A single compact coordinate moves/rotates/rescales an entire generated receptive field. Its quantization error is high leverage.

The compact rate win appears because six reasonably precise bits on **32 values** remain cheap, not because the values tolerate brutal quantization.

# Why description rate is not compute rate

If compact filters are materialized as dense digital dot products, all 16-channel maps still pay approximately:

```text
16D projection MACs
```

At D=784 the common projection cost dominates the decoder differences.

Likewise all current constrained arms emit:

```text
16 FP32 logical values = 64 bytes/sample
```

So Gates 11/11b do **not** establish:

```text
projection FLOP savings
logical egress savings
physical bandwidth savings
energy savings
```

A 24-byte serialized observer may still expand into a large dense filter bank before execution.

Those currencies remain separate.

# Direct SpectralNeuron bridge

The next missing experiment should stop treating sixteen logical consequences as sixteen perfect wires.

Take an observation map producing `M` logical consequences and force them through a controlled shared physical channel:

```text
x -> C_theta -> z in R^M
                 |
                 v
          shared channel H
          physical width P < M
                 |
                 v
          receiver R
                 |
                 v
               z_hat
                 |
                 v
              decoder
```

Compare under matched:

```text
M logical width
P physical carrier width / samples / bandwidth
channel noise
map-description budget
receiver/demultiplexer budget
decoder budget
```

Sweep:

```text
M / P packing ratio
channel condition / crosstalk
receiver selectivity
input dimension D
```

Measure jointly:

```text
task accuracy
full crosstalk matrix
serialized map bytes
physical carrier count/bandwidth
receiver/demux compute
decoder compute
```

Frequency-division multiplexing can be one arm, but a matched generic linear/code-division mixing baseline is mandatory so frequency cannot win by narrative.

# Candidate allocation law

A strong result would not be:

> frequency is how neurons compute.

Nor:

> learning the sensor is new.

The current candidate is narrower:

> **For a fixed task region, the cost of an observer is distributed across at least three separable currencies: the rate needed to describe the observation map, the physical resources needed to transmit its logical consequences with acceptable interference, and the downstream resources needed to decode them. Compact structured observation families can occupy a useful part of that frontier when their serialized map rate grows more slowly than a dense measurement matrix.**

Gates 11/11b now support the first clause empirically on two digit scales. The physical-channel clause is the next untested rung.
