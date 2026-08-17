# Prior art / attackers

SplatNeuron currently makes **no novelty claim**. Several nearby lines already own major pieces of the idea, and one of Antti's own earlier repos now supplies a directly relevant negative control.

## Input-dependent sampling geometry

**Dai et al., 2017 — Deformable Convolutional Networks.** Deformable convolution augments fixed convolution sampling locations with learned, input-dependent offsets. This is a direct attacker against any claim as broad as "neural receptive fields can move."

- arXiv:1703.06211

**Jaderberg et al., 2015 — Spatial Transformer Networks.** Spatial transformers learn input-conditioned spatial transformations inside networks. This attacks "a network can actively change its observation geometry."

- arXiv:1506.02025

**Mnih et al., 2014 — Recurrent Models of Visual Attention.** A recurrent agent adaptively selects a sequence of image locations and controls computation independently of total image size. This is a direct attacker against "ROUTE / active sensing saves observation work."

- arXiv:1406.6247

Therefore fast ROUTE alone is occupied territory.

## Plasticity during lifetime

**Miconi, Stanley & Clune, 2018 — Differentiable plasticity.** Hebbian/plastic recurrent connections continue changing during an agent's lifetime, while gradient descent learns how that plasticity should work. This attacks any broad claim that "meta-learning can learn a within-lifetime plasticity rule."

- PMLR 80:3559-3568

Therefore lifetime adaptation alone is occupied territory.

## Internal attacker: WildIdea W3/K2

`anttiluode/WildIdea` records an off-repo W3/K2 boundary in which a preallocated bank of three alternative charts plus disagreement-directed probing matched predictable online chart growth.

Reported switch/re-entry probe counts:

```text
fixed bank + random probes         84.6 / 56.8
fixed bank + disagreement probes    2.6 /  2.5
predictable growth + disagreement   3.3 /  1.9
```

WildIdea's frozen interpretation is that **having alternatives mattered; manufacturing them online did not earn architectural importance in that toy.**

SplatNeuron Smoke 1 independently reproduced the same shape with plastic Gabor receivers: two preallocated plastic anchors beat online branch growth at identical eventual accuracy and steady-state work.

This is now a mandatory attacker against structural-growth claims in this repo.

## Structural plasticity in biology

These are biological motivation, not implementation evidence.

**Xu et al., 2009 — Rapid formation and selective stabilization of synapses for enduring motor memories.** Motor learning rapidly induced new dendritic spines; a subset was preferentially stabilized with subsequent training.

- Nature 462, 915-919. doi:10.1038/nature08389

**Fu et al., 2012 — Repetitive motor learning induces coordinated formation of clustered dendritic spines in vivo.** Repetitive training produced spatial clusters of new spines, and clustered spines were preferentially retained.

- Nature 483, 92-95. doi:10.1038/nature10844

These support the modest biological statement that repeated experience can leave persistent spatial structural traces at synaptic/dendritic scale. They do **not** establish that dendrites move receptive Gabor splats or optimize an observation-work objective.

## Shared dynamical media / reservoirs

Liquid-state / reservoir computing already establishes that rich recurrent dynamics can provide transient state from which learned readouts extract task-relevant consequences. Therefore "a shared dynamical medium with learned readouts" is not the contribution.

SplatNeuron deliberately postpones recurrent write-back until plastic observation geometry has earned itself independently.

## Narrow research question left open

After the fixed-capacity attack, the live object is narrower:

```text
active sensing / input-dependent receiver movement
        +
within-lifetime persistent consolidation of useful receiver geometry
        +
explicit accounting of observation/search work
```

Structural growth is **not** currently supported. It may return only in tasks where useful recurring views exceed matched fixed capacity.

The claim to test is whether persistent plasticity of the **observation map itself** can amortize repeated active sensing in a useful and scalable way.

Serious future baselines must include at least:

- fixed receiver + larger recurrent memory;
- recurrent visual attention / glimpse policy;
- spatial transformer style learned sampling;
- deformable-convolution style dynamic offsets;
- learned routing / sparse retrieval;
- differentiable plasticity / fast-weight recurrence;
- **fixed-capacity plastic receiver banks**;
- simple cache/table of previously useful observation destinations;
- oracle receiver placement.

If a lookup table over contexts or previously seen routes matches the effect at lower cost, SplatNeuron has learned a fancy address book and the stronger story dies.
