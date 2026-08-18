# Gate 13 accounting correction — seeded random operator payload

Date: 2026-08-18

Status: **identified while the frozen full jobs were running, before their result JSONs were inspected. No performance result is changed.**

## The issue

The Gate-13 runner charges both seeded-random arms a literal 32-bit deployed seed:

```text
L_map = 4 bytes
```

That is a valid self-contained serialization if the exact PRNG seed is stored with each deployed observer.

However, Gate 13 already uses a shared-family/schema convention for algorithmic transforms. Under that convention DCT pays zero **learned/task-specific** operator bytes because the DCT algorithm is assumed shared.

The same logic gives a stronger accounting for the preregistered random attackers.

## Stronger shared-codebook interpretation

### random_fixed

`random_fixed` uses one preregistered universal seed and performs no task/data-dependent map selection.

If that seed is considered part of the shared algorithm/schema, the per-deployment task-specific map payload is

```text
0 bits
```

rather than 32 bits.

### random_search3

`random_search3` searches exactly three preregistered seeds and selects one using validation.

If the three candidate seeds are part of the shared schema/codebook, only the chosen index must be stored task-specifically:

```text
ceil(log2(3)) = 2 bits
```

A deliberately simple byte-aligned serialization would charge 1 byte.

The three tried maps remain fully charged as **discovery/search debt** even though only the selected index is deployed.

## Reporting rule

Do not rerun or reselect any Gate-13 model because of this correction.

For every seeded-random selected result report both:

```text
literal runner serialization:
    4 B seed

strong shared-schema accounting:
    random_fixed   0 bits task-specific payload
    random_search3 2 bits ideal index / 1 B byte-aligned index
```

Use the stronger accounting when testing whether the structured family is Pareto-nondominated in operator payload versus logical width.

## Effect on the main question

This correction cannot manufacture or erase a logical-width trade because it does not alter `M` or task accuracy.

If, for example, random reaches a target at `M=48` and structured reaches it at `M=32`, the resource exchange remains:

```text
near-zero task-specific random-map payload, M=48
versus
nonzero learned structured payload, M=32
```

The correction simply makes the low-map edge more honestly hostile to the learned observer.

## Why this is not applied to learned structured coordinates

The derivative-rendering algorithm, parameter semantics and codec are likewise shared schema and are not charged. What remains task-specific are the learned coordinate values themselves; those must still be serialized.

Thus the same convention is being applied symmetrically:

```text
shared family algorithm        free / schema
shared fixed constants         free / schema
task-selected learned values   charged
task-selected codebook index   charged
```

## Publication caution

If literal end-to-end self-contained artifact size is ever the objective, then **every** family must include its decoder implementation, family code, PRNG specification, fixed constants and metadata. Gate 13 does not measure that quantity.

It measures task-specific operator payload conditional on shared family implementations.
