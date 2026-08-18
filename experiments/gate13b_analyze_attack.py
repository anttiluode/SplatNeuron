"""Gate 13b analyzer — compare index-only attackers to frozen Gate 13 geometry.

The scientific categories are frozen in:
    docs/GATE13B_PREREG_INDEX_ONLY_ATTACKERS.md

Usage:
    python experiments/gate13b_analyze_attack.py \
        gate13_seed_13100.json gate13_seed_13101.json gate13_seed_13102.json \
        gate13b_seed_13100.json gate13b_seed_13101.json gate13b_seed_13102.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load(p):
    return json.loads(Path(p).read_text())


def struct_index(run):
    return {
        (s["d"], s["k"], s["structure"]): s["min_width"]
        for s in run["summaries"]
        if s["target_frac"] == 0.95 and s["family"] == "structured"
    }


def attack_index(run):
    out = defaultdict(list)
    for r in run["results"]:
        if r["reaches"]:
            out[(r["d"], r["k"], r["structure"])].append(r)
    return out


def dominates(a_m, a_l, b_m, b_l):
    return a_m <= b_m and a_l <= b_l and (a_m < b_m or a_l < b_l)


def pareto(points):
    keep = []
    for p in points:
        if not any(
            dominates(q["m"], q["map_bytes"], p["m"], p["map_bytes"])
            for q in points if q is not p
        ):
            keep.append(p)
    return sorted(keep, key=lambda p: (p["map_bytes"], p["m"], p["family"]))


def classify(structured, attack_points):
    if structured is None:
        return "NO_STRUCTURED_REFERENCE"
    if not attack_points:
        return "ATTACKER_FAIL"
    sm, sl = structured["m"], structured["map_bytes"]
    front = pareto(attack_points)
    if any(dominates(p["m"], p["map_bytes"], sm, sl) for p in front):
        return "ATTACKER_DOMINATES"
    if all(dominates(sm, sl, p["m"], p["map_bytes"]) for p in front):
        return "STRUCTURED_DOMINATES"
    return "TRADEOFF"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gate13", nargs=3)
    ap.add_argument("gate13b", nargs=3)
    args = ap.parse_args()

    old = {r["world_seed"]: r for r in map(load, args.gate13)}
    new = {r["world_seed"]: r for r in map(load, args.gate13b)}
    if sorted(old) != [13100, 13101, 13102] or sorted(new) != [13100, 13101, 13102]:
        raise SystemExit("expected both artifact sets for seeds 13100/13101/13102")

    rows = []
    for seed in sorted(old):
        si = struct_index(old[seed])
        ai = attack_index(new[seed])
        for d in (1024, 2304, 4096):
            for k in (2, 4, 8, 16):
                for structure in ("local", "mixed", "dense"):
                    s = si[(d, k, structure)]
                    pts = ai[(d, k, structure)]
                    rows.append({
                        "seed": seed, "d": d, "k": k, "structure": structure,
                        "structured": s, "attack_front": pareto(pts),
                        "category": classify(s, pts),
                    })

    primary = [r for r in rows if r["k"] == 8 and r["structure"] == "local"]
    c = Counter(r["category"] for r in primary)
    print("PRIMARY K=8 LOCAL T95 (9 cells)")
    print(dict(c))
    for r in primary:
        s = r["structured"]
        front = [(p["family"], p["m"], p["map_bytes"], round(p["val_accuracy"], 4)) for p in r["attack_front"]]
        print(
            f"  seed={r['seed']} D={r['d']} {r['category']:20s} "
            f"structured=(M{s['m']},{s['map_bytes']}B) attacker_front={front}"
        )

    n_dom = c["ATTACKER_DOMINATES"]
    n_nondom = c["STRUCTURED_DOMINATES"] + c["TRADEOFF"]
    if n_dom >= 5:
        verdict = "GEOMETRY_SPECIFIC_KEEP = False"
    elif n_nondom >= 8:
        verdict = "GEOMETRY_SPECIFIC_KEEP = survives_index_attack"
    else:
        verdict = "GEOMETRY_SPECIFIC_KEEP = inconclusive"
    print(verdict)
    print()

    print("FULL T95 CATEGORY COUNTS")
    for structure in ("local", "mixed", "dense"):
        for k in (2, 4, 8, 16):
            rr = [r for r in rows if r["structure"] == structure and r["k"] == k]
            print(f"  {structure:5s} K={k:2d}: {dict(Counter(r['category'] for r in rr))}")


if __name__ == "__main__":
    main()
