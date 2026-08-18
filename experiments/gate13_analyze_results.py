"""Aggregate the three frozen Gate-13 JSON artifacts.

Implements docs/GATE13_ANALYSIS_PLAN.md.  This script was added after the
full jobs completed, but the classification rules it implements were frozen
before the result artifacts were inspected.

Usage:
    python experiments/gate13_analyze_results.py \
        gate13_seed_13100.json gate13_seed_13101.json gate13_seed_13102.json
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

LOW_FAMILIES = ("dct", "random_fixed", "random_search3")
TARGETS = (0.95, 0.90)
STRUCTURES = ("local", "mixed", "dense")


def load(path: str):
    return json.loads(Path(path).read_text())


def index_summaries(data):
    return {
        (s["d"], s["k"], s["structure"], s["target_frac"], s["family"]): s
        for s in data["summaries"]
    }


def total_state(x):
    return x["map_bytes"] + x["head_bytes"]


def best_low(by, d, k, structure, target):
    found = []
    for family in LOW_FAMILIES:
        x = by[(d, k, structure, target, family)]["min_width"]
        if x is not None:
            found.append((family, x))
    if not found:
        return None, None
    return min(
        found,
        key=lambda q: (q[1]["m"], q[1]["map_bytes"], total_state(q[1]), -q[1]["val_accuracy"]),
    )


def classify(structured, low):
    if structured is not None and low is not None:
        return "WIDTH_TRADE" if structured["m"] < low["m"] else "DOMINATED_OR_TIED"
    if structured is not None:
        return "UNIQUE_REACH"
    if low is not None:
        return "STRUCTURED_FAIL_LOW_REACH"
    return "NONE_REACH"


def chance_target(reference, frac):
    return 0.5 + frac * (reference - 0.5)


def median(xs):
    return statistics.median(xs) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsons", nargs=3)
    args = ap.parse_args()
    runs = [load(p) for p in args.jsons]
    seeds = sorted(d["world_seed"] for d in runs)
    if seeds != [13100, 13101, 13102]:
        raise SystemExit(f"expected seeds 13100/13101/13102, got {seeds}")

    rows = []
    for data in runs:
        seed = data["world_seed"]
        by = index_summaries(data)
        ref_test = {r["k"]: r["test"] for r in data["references"]}
        cells = sorted({(s["d"], s["k"], s["structure"], s["target_frac"])
                        for s in data["summaries"]})
        for d, k, structure, target in cells:
            s = by[(d, k, structure, target, "structured")]["min_width"]
            low_family, low = best_low(by, d, k, structure, target)
            category = classify(s, low)
            test_target = chance_target(ref_test[k], target)
            rows.append({
                "seed": seed, "d": d, "k": k, "structure": structure,
                "target": target, "category": category,
                "structured": s, "low_family": low_family, "low": low,
                "test_target": test_target,
            })

    print("Gate 13 frozen-analysis aggregation")
    print("seeds:", seeds)
    print()

    print("WIDTH-TRADE COUNTS (out of 36 seed-cells per structure/target)")
    for structure in STRUCTURES:
        for target in TARGETS:
            rr = [r for r in rows if r["structure"] == structure and r["target"] == target]
            c = Counter(r["category"] for r in rr)
            print(f"  {structure:5s} T{int(target*100):02d}: {dict(c)}")
    print()

    print("T95 WIDTH_TRADE REPLICATION COUNTS (out of 3 world seeds)")
    for structure in STRUCTURES:
        print(f"  {structure}")
        for k in (2, 4, 8, 16):
            vals = []
            for d in (1024, 2304, 4096):
                n = sum(r["category"] == "WIDTH_TRADE" for r in rows
                        if r["structure"] == structure and r["target"] == 0.95
                        and r["k"] == k and r["d"] == d)
                vals.append(f"D{d}:{n}/3")
            print(f"    K={k:2d}  " + "  ".join(vals))
    print()

    print("T95 MEDIAN MINIMUM-WIDTH FRONTIER ACROSS 3 D x 3 SEED CELLS")
    for structure in STRUCTURES:
        print(f"  {structure}")
        for k in (2, 4, 8, 16):
            rr = [r for r in rows if r["structure"] == structure and r["target"] == 0.95 and r["k"] == k]
            ms = [r["structured"]["m"] for r in rr if r["structured"]]
            bs = [r["structured"]["map_bytes"] for r in rr if r["structured"]]
            ml = [r["low"]["m"] for r in rr if r["low"]]
            print(f"    K={k:2d}: structured M={median(ms):g}, map={median(bs):g} B; low-map M={median(ml):g}")
    print()

    local95_trade = [r for r in rows if r["structure"] == "local" and r["target"] == 0.95
                     and r["category"] == "WIDTH_TRADE"]
    struct_hits = sum(r["structured"]["test_accuracy"] >= r["test_target"] for r in local95_trade)
    low_hits = sum(r["low"]["test_accuracy"] >= r["test_target"] for r in local95_trade)
    misses = [r["structured"]["test_accuracy"] - r["test_target"] for r in local95_trade
              if r["structured"]["test_accuracy"] < r["test_target"]]
    print("LOCAL T95 HELD-OUT GUARD")
    print(f"  WIDTH_TRADE selections: {len(local95_trade)}")
    print(f"  structured held-out target hits: {struct_hits}/{len(local95_trade)}")
    print(f"  low-map held-out target hits:    {low_hits}/{len(local95_trade)}")
    if misses:
        print(f"  worst structured shortfall: {-min(misses)*100:.4f} percentage points")
    print()

    print("LOCAL T95 D-vs-K sanity")
    for d in (1024, 2304, 4096):
        rr = [r for r in rows if r["structure"] == "local" and r["target"] == 0.95 and r["d"] == d]
        print(f"  D={d}: median structured M across K = {median([r['structured']['m'] for r in rr]):g}")
    for k in (2, 4, 8, 16):
        rr = [r for r in rows if r["structure"] == "local" and r["target"] == 0.95 and r["k"] == k]
        print(f"  K={k:2d}: median structured M across D/seeds = {median([r['structured']['m'] for r in rr]):g}")


if __name__ == "__main__":
    main()
