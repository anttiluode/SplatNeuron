# Gate 1 — ROUTE -> GROW

Date: 2026-08-17

Status: **PASS as a controlled recurring-regime capability test.**

## Question

Does persistent branch growth buy anything beyond one receiver whose home geometry can move?

Gate 0's single anchor can learn the current regime but forgets the old one. Gate 1 makes the structural prediction sharper:

> If a useful distant route recurs, preserving it as another receiver branch should convert repeated global search into a small local branch check, and the old route should remain available when the world returns.

## Regime sequence

```text
A -> B -> A -> B
```

30 episodes per block. There is **no context/regime label** supplied to the receiver.

## Policies

`ROUTE ONLY` always searches from the original A home. `SINGLE ANCHOR` uses Gate 0 consolidation: successful routes continuously move one home receiver. `GROW` starts with one A branch and one dormant branch slot. At each episode it samples existing branches directly; if one crosses the evidence threshold it uses it, otherwise it pays for global ROUTE. If three similar successful routed destinations lie far from every existing branch, it crystallizes one new branch there.

The branch rule receives no hidden regime identifier.

## Result

20 deterministic seeds:

```text
route_only     acc=1.000  totalW=18060.0  growths=0.00
single_anchor  acc=1.000  totalW= 3095.0  growths=0.00
grow           acc=1.000  totalW= 1074.0  growths=1.00
```

GROW block behavior:

```text
block A1   meanW  1.00   first5 1.00    last10 1.00
block B    meanW 31.80   first5 180.80  last10 2.00
block A2   meanW  1.00   first5 1.00    last10 1.00
block B2   meanW  2.00   first5 2.00    last10 2.00
```

So after structural growth, the system retained both useful observation locations. Returning to A no longer caused the search spike seen in the single-anchor policy, and returning to B likewise remained local.

## Charged morphology

A new branch is not free.

Rather than choose a branch cost and tune toward a win, the experiment computes the branch cost at which GROW would stop beating SINGLE ANCHOR over the tested horizon:

```text
(single-anchor observation work - grow observation work)
--------------------------------------------------------
                    number of grown branches

= (3095 - 1074) / 1
= 2021 observation units
```

So this particular recurring workload has positive structural value for any branch cost below about 2021 units in the same logical accounting.

That is not a hardware cost estimate. It is a break-even boundary for the synthetic experiment.

## Supported statement

> In a recurring two-regime Gabor observation world with no explicit context label, a hand-designed use-dependent branch-growth rule can preserve two previously expensive receiver routes and substantially reduce future observation/search work at unchanged task accuracy; the experiment exposes the break-even cost of the extra branch rather than treating morphology as free.

## What this does not support

Do not claim that biological dendrites implement this rule; the growth policy is learned; branch checks stay cheap at large branch counts; exhaustive fallback routing is scalable; useful views are discovered in a continuous space; the result beats active attention, spatial transformers, deformable convolution, memory systems, or learned routers; or one branch's logical cost corresponds to a real neuron, cache line, GPU kernel, or joule.

The world remains favorable: A/B are stationary, exact bank members, and recur for long blocks.

## Next attacker

The next gate should remove the two biggest conveniences at once:

```text
no exact target in the bank
no exhaustive 300-view search
```

Use continuous receiver geometry and a strict route budget. A learned/local route policy must then decide where to move next from the observations it already has. That is the point at which deformable sampling and active-attention baselines become mandatory.
