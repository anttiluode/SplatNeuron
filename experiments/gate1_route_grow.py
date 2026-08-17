from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from splatneuron import BranchingReceiver, ReceiverAnchor, SplatWorld, make_default_bank, route_receiver


def choose_targets(geoms):
    a = min(range(len(geoms)), key=lambda i: abs(geoms[i].x - 0.14) + abs(geoms[i].y - 0.14) + abs(geoms[i].freq - 2.0) + abs(geoms[i].theta - 0.0))
    b = min(range(len(geoms)), key=lambda i: abs(geoms[i].x - 0.86) + abs(geoms[i].y - 0.86) + abs(geoms[i].freq - 8.0) + abs(geoms[i].theta - np.pi / 2.0))
    return a, b


@dataclass
class PolicyTrace:
    correct: list[bool]
    work: list[int]
    grows: int = 0


def run_seed(seed: int, block_len: int = 30):
    geoms, _, gram = make_default_bank()
    a, b = choose_targets(geoms)
    home = geoms[a]
    regimes = [a] * block_len + [b] * block_len + [a] * block_len + [b] * block_len
    rng = np.random.default_rng(seed)
    labels = rng.choice([-1, 1], size=len(regimes))

    traces = {
        "route_only": PolicyTrace([], []),
        "single_anchor": PolicyTrace([], []),
        "grow": PolicyTrace([], []),
    }
    moving = ReceiverAnchor(home, plasticity_rate=0.28)
    growing = BranchingReceiver(home, max_branches=2, growth_patience=3, far_threshold=2.0)

    for t, (target, label) in enumerate(zip(regimes, labels)):
        for si, name in enumerate(traces):
            srng = np.random.default_rng(seed * 2000003 + t * 131 + si * 2029)
            ep = SplatWorld(gram, target, srng).episode(int(label))

            if name == "route_only":
                res = route_receiver(ep, geoms, home)
                grew = False
            elif name == "single_anchor":
                res = route_receiver(ep, geoms, moving.geometry)
                moving.consolidate(geoms[res.receiver_index], abs(res.response))
                grew = False
            else:
                res, grew = growing.observe(ep, geoms)
                if grew:
                    traces[name].grows += 1

            traces[name].correct.append(res.prediction == int(label))
            traces[name].work.append(res.work)

    return traces


def aggregate(seeds=range(20), block_len=30):
    runs = [run_seed(int(seed), block_len=block_len) for seed in seeds]
    out = {}
    for name in runs[0]:
        work = np.asarray([r[name].work for r in runs], dtype=float)
        correct = np.asarray([r[name].correct for r in runs], dtype=float)
        grows = np.asarray([r[name].grows for r in runs], dtype=float)
        out[name] = {
            "accuracy": float(correct.mean()),
            "total_work": float(work.sum(axis=1).mean()),
            "growths": float(grows.mean()),
            "blocks": [],
        }
        for bi in range(4):
            sl = slice(bi * block_len, (bi + 1) * block_len)
            wb = work[:, sl]
            cb = correct[:, sl]
            out[name]["blocks"].append({
                "accuracy": float(cb.mean()),
                "mean_work": float(wb.mean()),
                "first5_work": float(wb[:, :5].mean()),
                "last10_work": float(wb[:, -10:].mean()),
            })
    saved = out["single_anchor"]["total_work"] - out["grow"]["total_work"]
    growths = max(out["grow"]["growths"], 1e-9)
    out["break_even_branch_cost"] = float(saved / growths)
    return out


def verdict(out):
    g = out["grow"]
    s = out["single_anchor"]
    r = out["route_only"]
    return {
        "all_policies_hold_accuracy": min(g["accuracy"], s["accuracy"], r["accuracy"]) >= 0.95,
        "growth_occurs_but_is_bounded": 0.8 <= g["growths"] <= 1.2,
        "grown_view_makes_late_B_local": g["blocks"][1]["last10_work"] <= 3.0,
        "grown_view_survives_return_to_A": g["blocks"][2]["first5_work"] <= 3.0,
        "grown_view_survives_second_B": g["blocks"][3]["first5_work"] <= 3.0,
        "growth_beats_single_anchor_work": g["total_work"] < 0.60 * s["total_work"],
        "growth_beats_route_only_work": g["total_work"] < 0.60 * r["total_work"],
        "branch_has_positive_break_even_value": out["break_even_branch_cost"] > 100.0,
    }


def main():
    out = aggregate()
    checks = verdict(out)
    print("Gate 1 — ROUTE -> GROW")
    print("A -> B -> A -> B recurring regimes; no regime/context label")
    print("20 deterministic seeds; one dormant branch available")
    print()
    for name in ("route_only", "single_anchor", "grow"):
        x = out[name]
        print(f"{name:<14} acc={x['accuracy']:.3f}  totalW={x['total_work']:.1f}  growths={x['growths']:.2f}")
        for i, b in enumerate(x["blocks"], start=1):
            print(f"  block{i}: meanW={b['mean_work']:.2f} first5={b['first5_work']:.2f} last10={b['last10_work']:.2f} acc={b['accuracy']:.3f}")
    print(f"\nbreak_even_branch_cost_vs_single_anchor = {out['break_even_branch_cost']:.1f} observation units")
    print()
    for k, ok in checks.items():
        print(f"{k:<42} {'PASS' if ok else 'FAIL'}")
    print(f"\nGATE1_PASS = {all(checks.values())}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
