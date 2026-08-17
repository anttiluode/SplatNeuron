# SplatNeuron

> **Use can shorten the path to evidence — but only when changing the receiver is worth paying for.**

SplatNeuron is a research program about **plastic observation geometry**: a computation can change where/how it observes a field during operation, and repeated useful observation routes may become persistent receiver geometry.

The repo began with a stronger dendritic-growth story. Strong boring controls have repeatedly cut that story down. Those negatives are part of the result.

## Current ledger

```text
Smoke 0    ROUTE / CONSOLIDATE plumbing                 works; WAIT null was constructed
Boundary0  nonzero-overlap WAIT <-> oracle ROUTE        quantitative SNR/cost crossover
Smoke 1    ROUTE -> GROW                                growth loses to fixed plastic capacity
Gate 2     continuous off-grid ROUTE                    fails to separate from address cache
Boundary1  cache <-> ROUTE vs environmental drift       sign change measured
Gate 3     adaptive hazard / PROBE admission            validation-selected fixed rule survives
```

No novelty, neuroscience, performance, or hardware claim is made.

## The live object

A receiver is a continuous coordinate

```text
u = (x, y, log-frequency, orientation)
```

mapped to a localized complex Gabor template `G(u)` and observing a common field through

```text
z = <G(u), X>
```

The operational actions are:

```text
WAIT   spend more observations through the same receiver
PROBE  spend one observation reducing uncertainty about whether to move
ROUTE  spend observations changing the receiver
```

The plastic extension is simply that a successful route may update one of a fixed number of persistent receiver anchors.

Growth is currently **not** part of the surviving claim.

## Smoke 0 — the original WAIT result was constructed

The first A/B bank targets had essentially zero overlap:

```text
|Gram[home_A,target_B]| ~= 4e-14
```

so repeating the A receiver could never recover B in expectation. The experiment remains only as a plumbing test for routing, consolidation, regime-shift search spikes, and relearning.

See [`docs/GATE0_ROUTE_CONSOLIDATE.md`](docs/GATE0_ROUTE_CONSOLIDATE.md).

## Boundary 0 — when another view could repay its cost

Give the current receiver nonzero overlap `c`, equal Gaussian observation noise, total budget 8, and charge 3 units for acquiring a better view:

```text
WAIT SNR  ~ |c| sqrt(8)
ROUTE SNR ~ sqrt(5)
```

The predicted crossover is

```text
|c|* = sqrt(5/8) ~= 0.790569
```

so high current overlap favors WAIT while low overlap can justify another view.

The ROUTE arm is oracle here; this is a resource boundary, not an active-routing win.

See [`docs/BOUNDARY0_WAIT_ROUTE.md`](docs/BOUNDARY0_WAIT_ROUTE.md).

## Smoke 1 — growth loses to fixed plastic capacity

The original growth result compared a two-branch growing system against one moving receiver and looked strong. The missing attacker begins with **two plastic receiver anchors from the start**, second anchor random, growth disabled.

Across 20 deterministic seeds:

```text
grow       acc=1.000  totalW=1074.0
fixedcap   acc=1.000  totalW= 613.2
```

Both reach the same steady-state work. Growth merely pays repeated global searches before its second branch crystallizes.

```text
GROWTH_EARNS_KEEP = False
```

This independently reproduces the same negative shape recorded in `anttiluode/WildIdea` W3/K2: preallocated alternatives plus probing matched or beat manufacturing alternatives online.

See [`docs/GATE1_ROUTE_GROW.md`](docs/GATE1_ROUTE_GROW.md).

## Gate 2 — the actual continuous rewrite

Gate 2 removes the address-table escape hatch.

Every query directly renders `G(u)` and takes a true inner product against a rendered field. There is:

```text
no 300 x 300 Gram lookup
no nearest-bank snap
no target coordinate available to the policy
no exhaustive scan
```

The two hidden source views drift continuously in `x`, `y`, frequency, and orientation. All structured policies have the same fixed receiver capacity `K=2` and exactly **8 observations per episode**.

Policies:

```text
address_cache    probe two fixed addresses, then WAIT
hybrid_plastic   WAIT if evidence is strong;
                 otherwise local SPSA ROUTE and persist an improvement
hybrid_reset     same router, but reset geometry every episode
always_route     same plastic capacity, but ROUTE every episode
random           eight random continuous queries
oracle           query the hidden target coordinate
```

Development used seeds `0..19`, `1000..1019`, and `2000..2019`; untouched confirmation was `3000..3019`.

```text
policy               acc   overlap   lateAcc   lateOv
------------------------------------------------------
address_cache       0.656    0.682     0.622    0.583
hybrid_plastic      0.674    0.691     0.661    0.644
hybrid_reset        0.644    0.660     0.604    0.575
always_route        0.569    0.589     0.566    0.583
random              0.507    0.153     0.500    0.148
oracle              1.000    1.000     1.000    1.000
```

Critical paired contrasts:

```text
hybrid - address cache   +0.061  95% CI [-0.005,+0.124]  NOT SEPARATED
hybrid - reset router    +0.068  95% CI [+0.009,+0.126]
hybrid - always route    +0.061  95% CI [+0.007,+0.107]
```

So persistent geometry and admission show narrower mechanism effects, but the fixed address cache blocks a general ROUTE win. Task-performance superiority over cache/reset is also not established.

See [`docs/GATE2_CONTINUOUS_ROUTE.md`](docs/GATE2_CONTINUOUS_ROUTE.md).

## Boundary 1 — cache versus ROUTE changes sign

Instead of tuning Gate 2's frozen drift rate, Boundary 1 sweeps environmental motion while holding capacity, budget, router, admission threshold, and field fixed.

```text
 scale   cacheOv   routeOv     delta      95% CI
------------------------------------------------------
  0.00     0.999     0.831    -0.168   [-0.211,-0.124]
  0.25     0.961     0.753    -0.209   [-0.254,-0.162]
  0.50     0.862     0.752    -0.110   [-0.165,-0.057]
  0.75     0.707     0.603    -0.104   [-0.245,+0.022]
  1.00     0.551     0.650    +0.099   [+0.029,+0.172]
  1.50     0.340     0.561    +0.221   [+0.115,+0.324]
  2.00     0.232     0.477    +0.244   [+0.154,+0.333]
  3.00     0.135     0.323    +0.188   [+0.089,+0.293]
  4.00     0.090     0.266    +0.175   [+0.130,+0.222]
```

At low motion, ROUTE is actively harmful because noisy evidence can trigger needless movement. At higher motion, stale addresses lose observability and ROUTE repays its cost.

But this phase boundary does **not** prove a fancy adaptive conductor is needed; the low-drift penalty depends strongly on the chosen fixed admission threshold.

See [`docs/BOUNDARY1_CACHE_ROUTE_PHASE.md`](docs/BOUNDARY1_CACHE_ROUTE_PHASE.md).

## Gate 3 — the boring fixed admission rule wins again

A separate drift × noise validation grid selected the strongest fixed threshold from:

```text
0.25, 0.35, 0.45, 0.55, 0.65
```

Winner:

```text
0.45
```

Two more intelligent policies were then frozen:

```text
HAZARD
successful receiver displacement raises future willingness to ROUTE

PROBE BAND
strong evidence       -> WAIT
weak evidence         -> ROUTE
ambiguous evidence    -> confirm once, then decide
```

Fresh confirmation used nine unseen cells:

```text
drift = {0.25, 1, 3}
noise = {0.15, 0.24, 0.34}
seeds = 14000..14005
```

Mean late receiver-target overlap across the nine cells:

```text
fixed 0.45    0.595   cells won 6/9
hazard        0.553   cells won 0/9
PROBE band    0.583   cells won 3/9
```

Paired aggregate contrasts:

```text
hazard - fixed   -0.042   95% CI [-0.072,-0.007]
PROBE  - fixed   -0.012   95% CI [-0.039,+0.024]
```

Therefore:

```text
ADAPTIVE_HAZARD_EARNS_KEEP = False
PROBE_BAND_EARNS_KEEP = False
GATE3_FIXED_THRESHOLD_SURVIVES = True
```

The adaptive policies had recognizable local value regions, but neither beat a validation-selected fixed rule over unseen stationary regime families.

This echoes `WildIdea` W4b: an apparently intelligent adaptive increment can vanish once the boring fixed policy is selected honestly.

See [`docs/GATE3_ADMISSION.md`](docs/GATE3_ADMISSION.md).

## What survives now

The strongest current statement is not a new neuron architecture:

> **WAIT, PROBE and ROUTE have different value regions under receiver staleness and observation noise, but strong fixed policies remain extremely hard to beat in stationary synthetic families.**

Continuous receiver geometry is now real in code. Persistent receiver state sometimes matters. But SplatNeuron has not yet earned a distinct ML architecture claim.

## Legitimate next test

Do not tune another static drift/noise grid.

The next admissible workload should change operating regime **inside the same run** without telling the policy:

```text
quiet / low-noise
    -> high-noise interval
    -> fast geometric drift
    -> quiet again
```

Compare an online admission rule against the best robust fixed threshold selected before test. Score segment-wise regret, transition cost, recovery cost, and downstream task performance.

If adaptivity still fails there, close the admission branch rather than adding a neural router.

## Gabor-specific stopping line

Gate 2 finally makes Gabor geometry algebraically real rather than decorative list ordering. It still has not shown Gabors are necessary.

If an arbitrary smooth continuous coordinate field with matched response correlation gives the same behavior, keep the generic active-sensing result and drop the Gabor-specific claim.

## When growth may return

Growth stays dead until:

```text
M recurring useful views >> K fixed receiver slots
```

Only there can structural birth/death buy something preallocation cannot.

## Run

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python experiments/gate0_route_consolidate.py
python experiments/boundary0_wait_route_crossover.py
python experiments/gate1_route_grow.py
python experiments/gate2_continuous_route.py
python experiments/boundary1_cache_route_phase.py
python experiments/gate3_admission.py
```

Gate 3 is intentionally heavier and is not part of every CI run.

See [`HANDOFF_CURRENT.md`](HANDOFF_CURRENT.md) for current stopping lines.
