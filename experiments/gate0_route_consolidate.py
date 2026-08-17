from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np

from splatneuron import ReceiverAnchor, SplatWorld, make_default_bank, route_receiver, wait_same_receiver


@dataclass
class BlockScore:
    accuracy: float
    mean_work: float
    first5_work: float
    last10_work: float


def summarize(correct: list[bool], work: list[int]) -> BlockScore:
    a = np.asarray(correct, dtype=float)
    w = np.asarray(work, dtype=float)
    return BlockScore(
        accuracy=float(a.mean()),
        mean_work=float(w.mean()),
        first5_work=float(w[:5].mean()),
        last10_work=float(w[-10:].mean()),
    )


def choose_targets(geoms):
    a = min(range(len(geoms)), key=lambda i: abs(geoms[i].x - 0.14) + abs(geoms[i].y - 0.14) + abs(geoms[i].freq - 2.0) + abs(geoms[i].theta - 0.0))
    b = min(range(len(geoms)), key=lambda i: abs(geoms[i].x - 0.86) + abs(geoms[i].y - 0.86) + abs(geoms[i].freq - 8.0) + abs(geoms[i].theta - np.pi / 2.0))
    return a, b


def run_seed(seed: int, block_len: int = 50, wait_repeats: int = 300):
    geoms, _, gram = make_default_bank()
    target_a, target_b = choose_targets(geoms)
    home = geoms[target_a]

    rng = np.random.default_rng(seed)
    anchor = ReceiverAnchor(home, plasticity_rate=0.28)
    labels = rng.choice([-1, 1], size=block_len * 3)
    regimes = [target_a] * block_len + [target_b] * block_len + [target_a] * block_len

    traces = {
        "fixed": {"correct": [], "work": []},
        "wait": {"correct": [], "work": []},
        "route": {"correct": [], "work": []},
        "consolidate": {"correct": [], "work": []},
    }

    for t, (target, label) in enumerate(zip(regimes, labels)):
        for si, name in enumerate(("fixed", "wait", "route", "consolidate")):
            srng = np.random.default_rng(seed * 1000003 + t * 97 + si * 1009)
            world = SplatWorld(gram, target, srng)
            ep = world.episode(int(label))

            if name == "fixed":
                z = ep.sample(target_a)
                pred = 1 if np.real(z) >= 0 else -1
                result_work = 1
            elif name == "wait":
                res = wait_same_receiver(ep, target_a, wait_repeats)
                pred, result_work = res.prediction, res.work
            elif name == "route":
                res = route_receiver(ep, geoms, home)
                pred, result_work = res.prediction, res.work
            else:
                res = route_receiver(ep, geoms, anchor.geometry)
                pred, result_work = res.prediction, res.work
                anchor.consolidate(geoms[res.receiver_index], abs(res.response))

            traces[name]["correct"].append(pred == int(label))
            traces[name]["work"].append(int(result_work))

    out = {}
    for name, tr in traces.items():
        out[name] = {
            "A1": summarize(tr["correct"][:block_len], tr["work"][:block_len]),
            "B": summarize(tr["correct"][block_len:2*block_len], tr["work"][block_len:2*block_len]),
            "A2": summarize(tr["correct"][2*block_len:], tr["work"][2*block_len:]),
        }
    return out


def aggregate(seeds=range(20)):
    runs = [run_seed(int(s)) for s in seeds]
    names = runs[0].keys()
    blocks = ("A1", "B", "A2")
    agg = {}
    for name in names:
        agg[name] = {}
        for block in blocks:
            scores = [r[name][block] for r in runs]
            agg[name][block] = BlockScore(
                accuracy=float(np.mean([s.accuracy for s in scores])),
                mean_work=float(np.mean([s.mean_work for s in scores])),
                first5_work=float(np.mean([s.first5_work for s in scores])),
                last10_work=float(np.mean([s.last10_work for s in scores])),
            )
    return agg


def gate_verdict(agg):
    fixed_b = agg["fixed"]["B"]
    wait_b = agg["wait"]["B"]
    route_b = agg["route"]["B"]
    con_b = agg["consolidate"]["B"]
    con_a1 = agg["consolidate"]["A1"]
    con_a2 = agg["consolidate"]["A2"]

    return {
        "fixed_offsupport_near_chance": fixed_b.accuracy <= 0.65,
        "wait_cannot_restore_missing_view": wait_b.accuracy <= 0.65,
        "route_recovers_distinction": route_b.accuracy >= 0.95,
        "consolidate_preserves_accuracy": con_b.accuracy >= 0.95,
        "shift_causes_search_spike": con_b.first5_work >= max(5.0, 5.0 * con_a1.last10_work),
        "repeated_use_shortens_route": con_b.last10_work <= 0.35 * con_b.first5_work,
        "consolidation_beats_route_only_late": con_b.last10_work <= 0.35 * route_b.last10_work,
        "return_shift_spikes_again": con_a2.first5_work >= max(5.0, 5.0 * con_b.last10_work),
        "return_relearns": con_a2.last10_work <= 0.35 * con_a2.first5_work,
    }


def print_report(agg, checks):
    print("Gate 0 — ROUTE -> CONSOLIDATE")
    print("real complex Gabor bank; 20 deterministic seeds")
    print()
    print(f"{'policy':<14} {'block':<4} {'acc':>7} {'meanW':>9} {'first5W':>9} {'last10W':>9}")
    print("-" * 58)
    for name in ("fixed", "wait", "route", "consolidate"):
        for block in ("A1", "B", "A2"):
            s = agg[name][block]
            print(f"{name:<14} {block:<4} {s.accuracy:7.3f} {s.mean_work:9.2f} {s.first5_work:9.2f} {s.last10_work:9.2f}")
    print()
    for key, ok in checks.items():
        print(f"{key:<42} {'PASS' if ok else 'FAIL'}")
    print(f"\nGATE0_PASS = {all(checks.values())}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=20)
    args = parser.parse_args()
    agg = aggregate(range(args.seeds))
    checks = gate_verdict(agg)
    print_report(agg, checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
