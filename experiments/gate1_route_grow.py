from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from splatneuron import (
    BranchingReceiver,
    ReceiverAnchor,
    SplatWorld,
    classify_response,
    geometry_distance,
    interpolate_geometry,
    make_default_bank,
    nearest_geometry_index,
    route_receiver,
)


def choose_targets(geoms):
    a = min(
        range(len(geoms)),
        key=lambda i: abs(geoms[i].x - 0.14)
        + abs(geoms[i].y - 0.14)
        + abs(geoms[i].freq - 2.0)
        + abs(geoms[i].theta - 0.0),
    )
    b = min(
        range(len(geoms)),
        key=lambda i: abs(geoms[i].x - 0.86)
        + abs(geoms[i].y - 0.86)
        + abs(geoms[i].freq - 8.0)
        + abs(geoms[i].theta - np.pi / 2.0),
    )
    return a, b


@dataclass
class PolicyTrace:
    correct: list[bool]
    work: list[int]
    grows: int = 0


class FixedCapacityReceiver:
    """Two plastic receiver anchors allocated from the start; growth disabled.

    The extra anchor starts at a random bank geometry. Existing anchors are checked
    first. If neither admits the episode, the same exhaustive fallback ROUTE used by
    the growth arm is paid, and the nearest existing anchor consolidates toward the
    successful destination.

    This is the missing boring attacker: if it matches or beats GROW, the result is
    capacity/plasticity, not structural growth.
    """

    def __init__(self, home, extra, *, plasticity_rate: float = 0.28, threshold: float = 0.72):
        self.branches = [home, extra]
        self.plasticity_rate = float(plasticity_rate)
        self.threshold = float(threshold)

    def observe(self, episode, geoms):
        probed: set[int] = set()
        work = 0

        for branch in self.branches:
            i = nearest_geometry_index(geoms, branch)
            if i in probed:
                continue
            probed.add(i)
            work += 1
            z = episode.sample(i)
            if abs(z) >= self.threshold:
                return classify_response(z), work

        remaining = [i for i in range(len(geoms)) if i not in probed]
        remaining.sort(
            key=lambda i: min(geometry_distance(branch, geoms[i]) for branch in self.branches)
        )

        last_z = 0j
        for i in remaining:
            work += 1
            z = episode.sample(i)
            last_z = z
            if abs(z) >= self.threshold:
                k = min(
                    range(len(self.branches)),
                    key=lambda j: geometry_distance(self.branches[j], geoms[i]),
                )
                self.branches[k] = interpolate_geometry(
                    self.branches[k], geoms[i], self.plasticity_rate
                )
                return classify_response(z), work

        return classify_response(last_z), work


def run_seed(seed: int, block_len: int = 30):
    geoms, _, gram = make_default_bank()
    a, b = choose_targets(geoms)
    home = geoms[a]
    regimes = [a] * block_len + [b] * block_len + [a] * block_len + [b] * block_len

    rng = np.random.default_rng(seed)
    labels = rng.choice([-1, 1], size=len(regimes))
    random_extra = geoms[int(rng.integers(len(geoms)))]

    traces = {
        "route_only": PolicyTrace([], []),
        "single_anchor": PolicyTrace([], []),
        "grow": PolicyTrace([], []),
        "fixedcap": PolicyTrace([], []),
    }

    moving = ReceiverAnchor(home, plasticity_rate=0.28)
    growing = BranchingReceiver(home, max_branches=2, growth_patience=3, far_threshold=2.0)
    fixedcap = FixedCapacityReceiver(home, random_extra)

    for t, (target, label) in enumerate(zip(regimes, labels)):
        for si, name in enumerate(traces):
            srng = np.random.default_rng(seed * 2000003 + t * 131 + si * 2029)
            ep = SplatWorld(gram, target, srng).episode(int(label))

            if name == "route_only":
                res = route_receiver(ep, geoms, home)
                pred, work = res.prediction, res.work
            elif name == "single_anchor":
                res = route_receiver(ep, geoms, moving.geometry)
                moving.consolidate(geoms[res.receiver_index], abs(res.response))
                pred, work = res.prediction, res.work
            elif name == "grow":
                res, grew = growing.observe(ep, geoms)
                if grew:
                    traces[name].grows += 1
                pred, work = res.prediction, res.work
            else:
                pred, work = fixedcap.observe(ep, geoms)

            traces[name].correct.append(pred == int(label))
            traces[name].work.append(int(work))

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
            out[name]["blocks"].append(
                {
                    "accuracy": float(cb.mean()),
                    "mean_work": float(wb.mean()),
                    "first5_work": float(wb[:, :5].mean()),
                    "last10_work": float(wb[:, -10:].mean()),
                }
            )

    growths = max(out["grow"]["growths"], 1e-9)
    out["break_even_vs_single_anchor"] = float(
        (out["single_anchor"]["total_work"] - out["grow"]["total_work"]) / growths
    )
    out["break_even_vs_fixedcap"] = float(
        (out["fixedcap"]["total_work"] - out["grow"]["total_work"]) / growths
    )
    return out


def scientific_checks(out):
    g = out["grow"]
    f = out["fixedcap"]
    return {
        "matched_accuracy": min(g["accuracy"], f["accuracy"]) >= 0.95,
        "growth_occurs_once": 0.8 <= g["growths"] <= 1.2,
        "same_late_B_work": abs(g["blocks"][1]["last10_work"] - f["blocks"][1]["last10_work"]) <= 0.25,
        "same_return_A_work": abs(g["blocks"][2]["last10_work"] - f["blocks"][2]["last10_work"]) <= 0.25,
        "same_second_B_work": abs(g["blocks"][3]["last10_work"] - f["blocks"][3]["last10_work"]) <= 0.25,
        "fixed_capacity_beats_growth_total_work": f["total_work"] < g["total_work"],
        "growth_break_even_vs_fixedcap_is_negative": out["break_even_vs_fixedcap"] < 0.0,
    }


def main():
    out = aggregate()
    checks = scientific_checks(out)

    print("Smoke 1 / growth attacker — ROUTE -> GROW")
    print("A -> B -> A -> B; 20 deterministic seeds; capacity=2")
    print("FIXEDCAP starts with a random second anchor and never grows.")
    print()

    for name in ("route_only", "single_anchor", "grow", "fixedcap"):
        x = out[name]
        print(
            f"{name:<14} acc={x['accuracy']:.3f}  "
            f"totalW={x['total_work']:.1f}  growths={x['growths']:.2f}"
        )
        for i, b in enumerate(x["blocks"], start=1):
            print(
                f"  block{i}: meanW={b['mean_work']:.2f} "
                f"first5={b['first5_work']:.2f} last10={b['last10_work']:.2f} "
                f"acc={b['accuracy']:.3f}"
            )

    print(
        f"\nbreak_even_branch_cost_vs_single_anchor = "
        f"{out['break_even_vs_single_anchor']:.1f} observation units"
    )
    print(
        f"break_even_branch_cost_vs_fixedcap      = "
        f"{out['break_even_vs_fixedcap']:.1f} observation units"
    )
    print()

    for key, ok in checks.items():
        print(f"{key:<48} {'PASS' if ok else 'FAIL'}")

    reproduced = all(checks.values())
    print(f"\nSMOKE1_REPRODUCED = {reproduced}")
    print("GROWTH_EARNS_KEEP = False")
    print("Interpretation: fixed plastic capacity explains the two-view result more cheaply.")

    if not reproduced:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
