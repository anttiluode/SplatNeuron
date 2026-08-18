"""Gate 13c analyzer — generic Givens circuit vs frozen Gate-13 geometry.

Categories and kill rules are frozen in:
    docs/GATE13C_PREREG_GIVENS_ATTACK.md

Usage:
    python experiments/gate13c_analyze_attack.py \
      gate13_seed_13100.json gate13_seed_13101.json gate13_seed_13102.json \
      gate13c_seed_13100.json gate13c_seed_13101.json gate13c_seed_13102.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load(p):
    return json.loads(Path(p).read_text())


def old_struct(run):
    return {
        (s["d"], s["k"], s["structure"]): s["min_width"]
        for s in run["summaries"]
        if s["target_frac"] == 0.95 and s["family"] == "structured"
    }


def dominates(a_m, a_l, b_m, b_l):
    return a_m <= b_m and a_l <= b_l and (a_m < b_m or a_l < b_l)


def pareto(points):
    return sorted(
        [p for p in points if not any(
            dominates(q["m"], q["map_bytes"], p["m"], p["map_bytes"])
            for q in points if q is not p
        )],
        key=lambda p: (p["map_bytes"], p["m"], p["angle_count"], p["bits"]),
    )


def classify(s, points):
    if s is None:
        return "NO_STRUCTURED_REFERENCE"
    reaching = [p for p in points if p["reaches"]]
    if not reaching:
        return "ATTACKER_FAIL"
    front = pareto(reaching)
    if any(dominates(p["m"], p["map_bytes"], s["m"], s["map_bytes"]) for p in front):
        return "ATTACKER_DOMINATES"
    if all(dominates(s["m"], s["map_bytes"], p["m"], p["map_bytes"]) for p in front):
        return "STRUCTURED_DOMINATES"
    return "TRADEOFF"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gate13", nargs=3)
    ap.add_argument("gate13c", nargs=3)
    args = ap.parse_args()

    old = {r["world_seed"]: r for r in map(load, args.gate13)}
    new = {r["world_seed"]: r for r in map(load, args.gate13c)}
    expected = [13100, 13101, 13102]
    if sorted(old) != expected or sorted(new) != expected:
        raise SystemExit("expected both artifact sets for seeds 13100/13101/13102")

    rows = []
    for seed in expected:
        oi = old_struct(old[seed])
        by_d = defaultdict(list)
        for r in new[seed]["results"]:
            by_d[r["d"]].append(r)
        for d in (1024, 2304, 4096):
            s = oi[(d, 8, "local")]
            points = by_d[d]
            reaching = [p for p in points if p["reaches"]]
            rows.append({
                "seed": seed,
                "d": d,
                "structured": s,
                "attacker_front": pareto(reaching),
                "category": classify(s, points),
            })

    c = Counter(r["category"] for r in rows)
    print("GATE 13C PRIMARY K=8 LOCAL T95 (9 cells)")
    print(dict(c))
    for r in rows:
        s = r["structured"]
        front = [
            (p["m"], p["map_bytes"], p["rounds"], p["angle_count"], p["bits"], round(p["val_accuracy"],4), round(p["test_accuracy"],4))
            for p in r["attacker_front"]
        ]
        print(
            f"  seed={r['seed']} D={r['d']} {r['category']:20s} "
            f"structured=(M{s['m']},{s['map_bytes']}B) attacker_front={front}"
        )

    n_dom = c["ATTACKER_DOMINATES"]
    n_nondom = c["STRUCTURED_DOMINATES"] + c["TRADEOFF"]
    if n_dom >= 5:
        verdict = "GEOMETRY_SPECIFIC_KEEP = False"
    elif n_nondom >= 8:
        verdict = "GEOMETRY_SPECIFIC_KEEP = survives_givens_attack"
    else:
        verdict = "GEOMETRY_SPECIFIC_KEEP = inconclusive"
    print(verdict)

    print("\nMINIMUM GENERIC CIRCUIT COMPLEXITY THAT REACHES T95")
    for r in rows:
        front = r["attacker_front"]
        if not front:
            print(f"  seed={r['seed']} D={r['d']}: none")
            continue
        # report minimum learned angle count among any reaching candidate, then its cheapest bits
        all_reach = [p for p in new[r['seed']]["results"] if p["d"] == r["d"] and p["reaches"]]
        min_r = min(p["angle_count"] for p in all_reach)
        rr = [p for p in all_reach if p["angle_count"] == min_r]
        best = min(rr, key=lambda p: (p["map_bytes"], p["m"], -p["val_accuracy"]))
        print(
            f"  seed={r['seed']} D={r['d']}: R={min_r}, rounds={best['rounds']}, "
            f"M={best['m']}, map={best['map_bytes']}B, bits={best['bits']}, val={best['val_accuracy']:.4f}"
        )


if __name__ == "__main__":
    main()
