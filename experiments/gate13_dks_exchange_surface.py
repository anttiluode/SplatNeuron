"""Gate 13 full runner — D x K x task/spatial-alignment exchange surface.

Preregistered before implementation in:
    docs/GATE13_PREREG_DKS_EXCHANGE_SURFACE.md

Run the cheap preflight first. `--smoke` is implementation-only and must not
be interpreted scientifically; `--full` runs the frozen grid for one world
seed and writes JSON suitable for later cross-seed aggregation.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

import gate13_dks_preflight as g

M_VALUES = (8, 16, 24, 32, 48, 64)
BITS = (2, 3, 4, 6, 8, 12, 16)
WORLD_SEEDS = (13100, 13101, 13102)
TARGET_FRACS = (0.95, 0.90)
GEOM_RESTARTS = 3
GEOM_STEPS = 220
GEOM_BATCH = 1024
GEOM_LR = 0.03
RANDOM_SEED_BASE = 73_000


@dataclass
class Candidate:
    d: int
    k: int
    structure: str
    family: str
    m: int
    bits: str
    map_bytes: int
    head_bytes: int
    repr_bytes_fp32: int
    val_accuracy: float
    test_accuracy: float
    test_task_std: float
    test_task_p10: float
    map_trials: int
    optimizer_steps: int
    map_fit_seconds: float
    decoder_fit_seconds: float
    selected_id: int

    @property
    def total_state_bytes(self) -> int:
        return self.map_bytes + self.head_bytes


def task_stats(z: torch.Tensor, y: torch.Tensor, h: torch.Tensor):
    x = torch.cat([z, torch.ones((len(z), 1))], dim=1)
    per = (((x @ h) >= 0.0) == (y >= 0.0)).float().mean(dim=0).numpy()
    return float(per.mean()), float(per.std()), float(np.quantile(per, 0.10))


def fit_candidate(d, k, structure, family, m, bits, map_bytes, b, data,
                  map_trials=0, optimizer_steps=0, map_fit_seconds=0.0,
                  selected_id=-1, frozen_head=None):
    (z, y), (zv, yv), (zt, yt) = data
    start = time.perf_counter()
    h = g.ridge_head(z @ b.T, y) if frozen_head is None else frozen_head
    dec_sec = time.perf_counter() - start if frozen_head is None else 0.0
    va, _, _ = task_stats(zv @ b.T, yv, h)
    te, sd, p10 = task_stats(zt @ b.T, yt, h)
    c = Candidate(
        d=d, k=k, structure=structure, family=family, m=m, bits=bits,
        map_bytes=map_bytes,
        head_bytes=(g.TASKS * m + g.TASKS) * 4,
        repr_bytes_fp32=4 * m,
        val_accuracy=va, test_accuracy=te, test_task_std=sd, test_task_p10=p10,
        map_trials=map_trials, optimizer_steps=optimizer_steps,
        map_fit_seconds=map_fit_seconds, decoder_fit_seconds=dec_sec,
        selected_id=selected_id,
    )
    return c, h


def grid_torch(n):
    yy, xx = torch.meshgrid(torch.linspace(0.0, 1.0, n), torch.linspace(0.0, 1.0, n), indexing="ij")
    return xx, yy


def derivative_rows(n: int, s: torch.Tensor) -> torch.Tensor:
    xx, yy = grid_torch(n)
    cx, cy = 0.03 + 0.94 * s[:, 0], 0.03 + 0.94 * s[:, 1]
    sigma, theta = 0.035 + 0.30 * s[:, 2], math.pi * s[:, 3]
    dx, dy = xx[None] - cx[:, None, None], yy[None] - cy[:, None, None]
    co, si = torch.cos(theta)[:, None, None], torch.sin(theta)[:, None, None]
    xr = co * dx + si * dy
    yr = -si * dx + co * dy
    sg = sigma[:, None, None]
    env = torch.exp(-0.5 * (xr * xr + yr * yr) / (sg * sg))
    odd = (xr / sg) * env
    even = ((xr * xr) / (sg * sg) - 1.0) * env
    odd = odd / (odd.flatten(1).norm(dim=1)[:, None, None] + 1e-8)
    even = even / (even.flatten(1).norm(dim=1)[:, None, None] + 1e-8)
    return torch.cat([odd.flatten(1), even.flatten(1)], dim=0)


def train_geometry(n, a, data, m, seed):
    (z, y), (zv, yv), _ = data
    torch.manual_seed(seed)
    raw = nn.Parameter(torch.randn(m // 2, 4) * 0.7)
    transient = nn.Linear(m, g.TASKS)
    opt = torch.optim.Adam([raw, *transient.parameters()], lr=GEOM_LR)
    gen = torch.Generator().manual_seed(seed + 77)
    start = time.perf_counter()
    for _ in range(GEOM_STEPS):
        ii = torch.randint(0, len(z), (GEOM_BATCH,), generator=gen)
        s = torch.sigmoid(raw)
        b = derivative_rows(n, s) @ a
        logits = transient(z[ii] @ b.T)
        loss = F.binary_cross_entropy_with_logits(logits, (y[ii] + 1.0) * 0.5)
        opt.zero_grad()
        loss.backward()
        opt.step()
    sec = time.perf_counter() - start
    s = torch.sigmoid(raw.detach())
    b = derivative_rows(n, s) @ a
    h = g.ridge_head(z @ b.T, y)
    va = g.accuracy(zv @ b.T, yv, h)
    return s, va, sec


def quant_unit(s, bits):
    levels = (1 << bits) - 1
    q = torch.round(torch.clamp(s, 0.0, 1.0) * levels) / levels
    return q, (s.numel() * bits + 7) // 8


def quant_rows(w, bits):
    levels = (1 << (bits - 1)) - 1
    scale = np.maximum(np.max(np.abs(w), axis=1, keepdims=True), 1e-12)
    q = np.clip(np.round(w / scale * levels), -levels, levels)
    wq = (q / levels * scale).astype(np.float32)
    payload = w.shape[0] * 4 + (w.size * bits + 7) // 8
    return wq, payload


def structured_family(n, k, structure, a_np, data, m, world_seed):
    a = torch.tensor(a_np)
    trials = []
    map_sec = 0.0
    for r in range(GEOM_RESTARTS):
        seed = world_seed * 100_000 + n * 100 + k * 10 + m + r
        s, va, sec = train_geometry(n, a, data, m, seed)
        map_sec += sec
        trials.append((va, r, s))
    vals = [x[0] for x in trials]
    print(f"GEOM_RESTARTS D={n*n} K={k} S={structure} M={m} vals={[round(v,4) for v in vals]} mean={np.mean(vals):.4f} std={np.std(vals):.4f}")
    _, chosen, s = max(trials, key=lambda x: x[0])
    b = derivative_rows(n, s) @ a
    full, h = fit_candidate(n*n, k, structure, "structured", m, "fp32", s.numel()*4, b, data,
                            GEOM_RESTARTS, GEOM_RESTARTS*GEOM_STEPS, map_sec, chosen)
    out = [full]
    for bits in BITS:
        sq, payload = quant_unit(s, bits)
        bq = derivative_rows(n, sq) @ a
        q, _ = fit_candidate(n*n, k, structure, "structured", m, f"{bits}b", payload, bq, data,
                             GEOM_RESTARTS, GEOM_RESTARTS*GEOM_STEPS, map_sec, chosen, h)
        q.decoder_fit_seconds = full.decoder_fit_seconds
        out.append(q)
    return out


def random_b(a, m, seed):
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0, 1.0 / math.sqrt(m), size=(m, a.shape[0])).astype(np.float32)
    return torch.tensor(r @ a)


def random_family(n, k, structure, a, data, m, world_seed, searched):
    trials = 3 if searched else 1
    vals = []
    for j in range(trials):
        seed = RANDOM_SEED_BASE + (1_000_000 if searched else 0) + world_seed + 17*m + 100_003*j
        c, _ = fit_candidate(n*n, k, structure, "random_search3" if searched else "random_fixed",
                             m, "seed32", 4, random_b(a, m, seed), data,
                             trials, 0, 0.0, seed)
        vals.append(c)
    if searched:
        vas = [c.val_accuracy for c in vals]
        print(f"RANDOM_SEARCH3 D={n*n} K={k} S={structure} M={m} vals={[round(v,4) for v in vas]} mean={np.mean(vas):.4f} std={np.std(vas):.4f}")
    best = max(vals, key=lambda c: c.val_accuracy)
    best.decoder_fit_seconds = sum(c.decoder_fit_seconds for c in vals)
    return [best]


def dct_basis(n, m):
    one = np.empty((n, n), dtype=np.float32)
    coords = np.arange(n, dtype=np.float32)
    for u in range(n):
        alpha = math.sqrt(1.0/n) if u == 0 else math.sqrt(2.0/n)
        one[u] = alpha * np.cos(math.pi * (2.0*coords + 1.0) * u / (2.0*n))
    order = []
    for s in range(2*n - 1):
        diag = [(u, s-u) for u in range(n) if 0 <= s-u < n]
        if s % 2 == 0:
            diag.reverse()
        order.extend(diag)
    return np.stack([np.outer(one[u], one[v]).reshape(-1) for u, v in order[:m]]).astype(np.float32)


def dct_family(n, k, structure, a, data, m):
    start = time.perf_counter()
    rows = dct_basis(n, m)
    sec = time.perf_counter() - start
    c, _ = fit_candidate(n*n, k, structure, "dct", m, "algorithmic", 0,
                         torch.tensor(rows @ a), data, 0, 0, sec, -1)
    return [c]


def pca_rows(z_train, a, m):
    if m > a.shape[1]:
        return None, 0.0
    start = time.perf_counter()
    z = z_train.numpy().astype(np.float64)
    z -= z.mean(0, keepdims=True)
    vals, vecs = np.linalg.eigh(z.T @ z / (len(z)-1))
    latent = vecs[:, np.argsort(vals)[::-1][:m]].T.astype(np.float32)
    rows = (latent @ a.T).astype(np.float32)
    return rows, time.perf_counter() - start


def pca_family(n, k, structure, a, data, m):
    rows, sec = pca_rows(data[0][0], a, m)
    if rows is None:
        return []
    full, h = fit_candidate(n*n, k, structure, "pca", m, "fp32", rows.size*4,
                            torch.tensor(rows @ a), data, 1, 0, sec, -1)
    out = [full]
    for bits in BITS:
        rq, payload = quant_rows(rows, bits)
        q, _ = fit_candidate(n*n, k, structure, "pca", m, f"{bits}b", payload,
                             torch.tensor(rq @ a), data, 1, 0, sec, -1, h)
        q.decoder_fit_seconds = full.decoder_fit_seconds
        out.append(q)
    return out


def oracle(n, k, structure, data):
    b = torch.zeros((k, k + g.NUISANCE))
    b[:, :k] = torch.eye(k)
    c, _ = fit_candidate(n*n, k, structure, "oracle_signal_dense", k, "fp32", 4*k*n*n,
                         b, data, 0, 0, 0.0, -1)
    return c


def target(ref, frac):
    return 0.5 + frac * (ref - 0.5)


def pick(cs, t, mode):
    ok = [c for c in cs if c.val_accuracy >= t]
    if not ok:
        return None
    if mode == "map":
        return min(ok, key=lambda c:(c.map_bytes,c.m,c.total_state_bytes,-c.val_accuracy))
    if mode == "width":
        return min(ok, key=lambda c:(c.m,c.map_bytes,c.total_state_bytes,-c.val_accuracy))
    return min(ok, key=lambda c:(c.total_state_bytes,c.m,c.map_bytes,-c.val_accuracy))


def pareto(cs, t):
    ok = [c for c in cs if c.val_accuracy >= t and not c.family.startswith("oracle")]
    out = []
    for c in ok:
        if not any(q.map_bytes <= c.map_bytes and q.m <= c.m and (q.map_bytes < c.map_bytes or q.m < c.m) for q in ok if q is not c):
            out.append(c)
    return sorted(out, key=lambda c:(c.map_bytes,c.m,c.family,c.bits))


def run(world_seed, smoke=False):
    sides = (32,) if smoke else g.D_SIDES
    ks = (8,) if smoke else g.K_VALUES
    structures = ("local","dense") if smoke else g.STRUCTURES
    ms = (16,32) if smoke else M_VALUES
    candidates = []
    refs = []
    checks = []
    for k in ks:
        data = g.data(k, world_seed)
        href = g.ridge_head(data[0][0][:,:k], data[0][1])
        rv = g.accuracy(data[1][0][:,:k], data[1][1], href)
        rt = g.accuracy(data[2][0][:,:k], data[2][1], href)
        refs.append({"k":k,"val":rv,"test":rt})
        print(f"REFERENCE K={k} val={rv:.4f} test={rt:.4f} T95={target(rv,.95):.4f} T90={target(rv,.90):.4f}")
        for n in sides:
            for structure in structures:
                a = g.build_world(n,k,structure,world_seed)
                orth = float(np.max(np.abs(a.T@a - np.eye(a.shape[1],dtype=np.float32))))
                support = g.support_fraction(a[:,:k])
                checks.append({"d":n*n,"k":k,"structure":structure,"orth":orth,"signal_support":support})
                if orth >= 2e-5:
                    raise RuntimeError("world orthonormality failed")
                print(f"CELL D={n*n} K={k} S={structure} support={support:.4f}")
                candidates.append(oracle(n,k,structure,data))
                for m in ms:
                    candidates += random_family(n,k,structure,a,data,m,world_seed,False)
                    candidates += random_family(n,k,structure,a,data,m,world_seed,True)
                    candidates += dct_family(n,k,structure,a,data,m)
                    candidates += pca_family(n,k,structure,a,data,m)
                    candidates += structured_family(n,k,structure,a,data,m,world_seed)
    summaries=[]
    for r in refs:
        k=r["k"]
        for n in sides:
            for structure in structures:
                cell=[c for c in candidates if c.k==k and c.d==n*n and c.structure==structure]
                for frac in TARGET_FRACS:
                    t=target(r["val"],frac)
                    fr=pareto(cell,t)
                    print(f"FRONT D={n*n} K={k} S={structure} T={frac:.2f} target={t:.4f}")
                    for c in fr:
                        print(f"  {c.family:15s} M={c.m:2d} map={c.map_bytes:7d}B bits={c.bits:9s} val={c.val_accuracy:.4f} test={c.test_accuracy:.4f} trials={c.map_trials}")
                    for fam in ("structured","random_fixed","random_search3","dct","pca"):
                        fcs=[c for c in cell if c.family==fam]
                        summaries.append({"d":n*n,"k":k,"structure":structure,"target_frac":frac,"target":t,"family":fam,
                            "min_map":None if pick(fcs,t,"map") is None else asdict(pick(fcs,t,"map")),
                            "min_width":None if pick(fcs,t,"width") is None else asdict(pick(fcs,t,"width")),
                            "min_state":None if pick(fcs,t,"state") is None else asdict(pick(fcs,t,"state"))})
    return {"world_seed":world_seed,"smoke":smoke,"references":refs,"checks":checks,
            "candidates":[asdict(c)|{"total_state_bytes":c.total_state_bytes} for c in candidates],"summaries":summaries}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--world-seed",type=int,default=13100)
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke",action="store_true")
    mode.add_argument("--full",action="store_true")
    ap.add_argument("--output",default="")
    args=ap.parse_args()
    if args.world_seed not in WORLD_SEEDS:
        raise SystemExit(f"world seed must be one of {WORLD_SEEDS}")
    result=run(args.world_seed,args.smoke)
    if args.output:
        p=Path(args.output)
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(result,indent=2))
        print(f"WROTE {p}")


if __name__ == "__main__":
    main()
