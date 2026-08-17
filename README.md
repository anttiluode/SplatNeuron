# SplatNeuron

> **Use can shorten the path to evidence.**

SplatNeuron is a research program about **plastic observation geometry**.

The starting point is deliberately narrower than "a brain made of splats":

> A computation may repeatedly need information that its current receiver cannot observe. Instead of only adding memory or repeating the same measurement, the receiver can **ROUTE** to a different view. If the same route proves useful repeatedly, the route can be **CONSOLIDATED** into persistent receiver geometry; if no existing branch can cheaply provide that view, repeated use can **GROW** a new branch.

The current code is an inspectable capability test using a bank of real complex 2-D Gabor atoms. It is **not** yet a trained neural architecture, a biological model, or a novelty claim.

## Why this repo exists

A fixed linear field can often be diagonalized into independent modes. If the observation map is also fixed, geometry may reduce to a basis choice plus time constants. That kills a large class of "geometry computes" stories.

SplatNeuron starts at the escape hatch:

```text
fixed observation map C
        -> repeat / integrate / remember

state-dependent observation map C(t)
        -> change what is observable
```

The key distinction is:

```text
WAIT   = spend more samples through the same receiver
ROUTE  = change the receiver
```

and the developmental extension is:

```text
repeated useful ROUTE
        -> persistent geometry
        -> less future observation/search work
```

In this repo, a receiver is parameterized by Gabor geometry:

```text
q = (x, y, sigma, frequency, orientation, phase)
```

and a receiver observes a common complex field by inner product with its localized Gabor template.

## Current receipts

### Gate 0 — ROUTE -> CONSOLIDATE

One hidden task atom occupies regime A, then moves to a far-away position/frequency/orientation in regime B, then returns to A. The task label is the sign of that atom. A fixed receiver starts on A.

Policies:

```text
FIXED        one receiver sample
WAIT         300 repeated samples at the same receiver
ROUTE        search receiver geometries, but reset home each episode
CONSOLIDATE  ROUTE, then pull persistent home geometry toward useful views
```

Across 20 deterministic seeds:

```text
policy         block     acc     meanW   first5W   last10W
----------------------------------------------------------
fixed          A1     1.000      1.00      1.00      1.00
fixed          B      0.463      1.00      1.00      1.00
wait           B      0.486    300.00    300.00    300.00
route          B      1.000    300.00    300.00    300.00
consolidate    B      1.000     21.28    201.20      1.00
consolidate    A2     1.000     20.46    193.42      1.05
```

So more observation through the same map did not recover the missing distinction, while changing the observation map did. Repeated useful routes were then amortized into receiver geometry: after a regime shift, search work spiked and then collapsed while accuracy stayed at 1.0.

This is a **synthetic capability receipt**. The informative atom is exactly in the available bank and ROUTE performs exhaustive search. Logical receiver samples are counted, not CPU/GPU wall time.

See [`docs/GATE0_ROUTE_CONSOLIDATE.md`](docs/GATE0_ROUTE_CONSOLIDATE.md).

### Gate 1 — ROUTE -> GROW

Gate 1 asks whether persistent branch growth buys anything beyond one moving receiver.

The regime sequence is:

```text
A -> B -> A -> B
```

There is no regime/context label. Existing branches are sampled directly. If none sees enough evidence, the system pays for a global ROUTE. After three similar far-away successful routes, one dormant branch may crystallize there.

Across 20 deterministic seeds:

```text
route_only     accuracy 1.000   total work 18060
single_anchor  accuracy 1.000   total work  3095
grow           accuracy 1.000   total work  1074   growths 1.00
```

After the B branch had grown:

```text
late B       ~2 observations
return A     ~1 observation
second B     ~2 observations
```

Rather than choosing a convenient branch price, the experiment reports the price at which the extra branch would stop paying for itself relative to the single moving anchor:

```text
break-even branch cost ~= 2021 observation units
```

Again: favorable synthetic world, hand-designed growth rule, exhaustive fallback search. This demonstrates the **mechanism**, not superiority to existing ML systems.

See [`docs/GATE1_ROUTE_GROW.md`](docs/GATE1_ROUTE_GROW.md).

## The object under test

The current minimal concept is:

```text
shared complex field X
        |
        v
receiver geometry q(t)
        |
        v
local observation r(t) = <G(q(t)), X(t)>
        |
        +-- WAIT: observe again at q
        +-- ROUTE: change q
        +-- CONSOLIDATE: move persistent q toward repeatedly useful routes
        `-- GROW: preserve a repeatedly useful distant q as another branch
```

Later, local private state and write-back can be added, but they are intentionally absent from Gates 0/1. The first question is whether **changing what can be observed** is a useful computational resource before adding another recurrent network around it.

## Why this is not just Hebbian weights

For emitter `i` and receiver `j`, fixed splat geometry induces an effective interaction roughly through overlap:

```text
A_ji ~ <R_j, E_i>
```

If geometry is fixed, that can collapse into an ordinary factored recurrent operator.

The stronger object is:

```text
A_ji(t) ~ <R_j(q_j(t)), E_i(p_i(t))>
```

where receiver geometry is part of the running state. Repeated use can change the future observation map itself.

A useful informal metric is **computational/epistemic distance**:

```text
d_c(A -> B) = minimum observation work required
              before B can recover A's relevant consequence
```

The current Gates 0/1 ask whether repeated useful interaction can make `d_c` fall by compiling search into persistent receiver geometry.

## Prior art / attackers

The ingredients have strong precursors. In particular:

- active visual attention already learns where to sample;
- spatial transformers and deformable convolutions already make sampling geometry input-dependent;
- differentiable plasticity already learns lifetime Hebbian/plastic rules;
- structural synaptic plasticity during learning is established biology;
- reservoir / liquid-state methods already exploit rich recurrent media with learned readouts.

Therefore neither "move a receptive field" nor "plasticity during inference" is a novelty claim here. The narrower question is whether **lifetime plasticity of observation geometry can amortize repeated active sensing into persistent structure under an explicit observation-work budget**.

See [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md).

## Run

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python experiments/gate0_route_consolidate.py
python experiments/gate1_route_grow.py
```

Requires Python 3.10+ and NumPy.

## Next attacker

Do **not** add a big hidden-state RNN yet.

The current receipts are easy because the world is constructed in our favor. The next gate should attack those conveniences:

1. target views are **off-grid / continuous**, not exact members of the receiver bank;
2. ROUTE cannot exhaustively scan 300 receivers; it gets a strict small budget;
3. the useful destination drifts rather than switching between two stationary points;
4. compare against learned active-attention / deformable-sampling baselines;
5. only then transplant the mechanism onto the trained SplatWorld/SplatField basis.

The ambitious claim to earn is not "splats beat GRUs." It is:

> **A system can reorganize its own observation geometry while operating, and repeated use can turn costly active sensing into cheap persistent structure without losing the task-relevant distinction.**

## Status

**v0.1 research prototype. Gate 0 and Gate 1 are mechanism receipts only. No novelty, neuroscience, performance, or hardware claim.**
