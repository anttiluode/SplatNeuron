# Gate 7 — matched ~200 parameter allocation

Date: 2026-08-17

Status: **no interior optimum; receiver-heavy endpoint wins.**

Gate 6 showed that learning eight receiver geometries with a linear decoder was dramatically more parameter-efficient than freezing those receivers and spending the same trainable budget on a small nonlinear decoder.

The obvious next question was whether a mixed allocation could beat both endpoints at the same tiny total budget.

## Configurations

All models transmit the same 16 real receiver channels.

```text
fixed_H7          0/8 receiver geometries learn + H=7 MLP   199 params
interior_m7_H6    7/8 receiver geometries learn + H=6 MLP   200 params
learned_linear    8/8 receiver geometries learn + linear    202 params
```

Additional nearby points (`m1_H7`, `m4_H7`, `m8_H7`) were included as development diagnostics.

## Four development splits

```text
fixed_H7          ~89.9%
interior_m7_H6    ~93.1%
learned_linear    ~95.5%
```

The interior allocation is real: moving almost all of the tiny budget toward receiver learning recovers several points over the downstream-heavy endpoint.

But it **does not beat** learning all receiver geometries with the simpler linear decoder.

## Interpretation

At this budget the receiver side can spend only 32 geometry scalars (`8 receivers x 4 parameters`). The endpoint is reached quickly; there is not enough receiver-side capacity to create a meaningful continuous allocation frontier.

Therefore Gate 7 does **not** produce the hoped-for interior `Y` block.

It motivates the stronger pre-collapse experiment in Gate 8: allow more private receiver branches than transmitted channels, then collapse locally back to the same 16-wide carrier.
