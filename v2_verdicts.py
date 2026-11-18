"""Verdicts for the model v2 experiment -- criteria and decision rules exactly as in
V2_PREREGISTRATION.md (written before any v2 number was computed).

Reads v2-runs-*.csv.gz (from v2_experiment.py). Usage: python3 v2_verdicts.py
"""
from __future__ import annotations

import csv
import glob
import gzip
import math
import statistics as st
from collections import defaultdict

LEVELS = [1.5, 2, 3, 4, 5, 6, 7, 8, 10]
HIGH = [4, 5, 6, 7, 8, 10]                     # scalper-fairness levels (4x and up)
CAPS = (10, 20, 30, 40)
FAN_TYPES = ["mega_fan", "committed_casual", "average_buyer"]
ROLES = [(t, h) for t in FAN_TYPES for h in ("holder", "havenot")]
SCEN = {"S1": ("model", "B"), "S2": ("always", "B"), "S3": ("model", "Z"), "S4": ("always", "Z")}
CODES = ("P0", "P1", "P2")
ROI_MAX, DARK_SHARE_MAX = 0.30, 0.20


def load():
    data = defaultdict(list)
    for path in sorted(glob.glob("v2-runs-*.csv.gz")):
        with gzip.open(path, "rt") as f:
            for r in csv.DictReader(f):
                data[(r["mechanics"], r["listing"], r["arm"], float(r["demand"]))].append(r)
    for k in data:
        data[k].sort(key=lambda r: int(r["seed"]))
    return data


def num(x):
    return float(x) if x not in ("", None) else None


def ci(xs):
    m = st.mean(xs)
    h = 1.96 * st.stdev(xs) / math.sqrt(len(xs))
    return m, m - h, m + h


def paired(data, mech, listing, arm_a, arm_b, d, col):
    a, b = data[(mech, listing, arm_a, d)], data[(mech, listing, arm_b, d)]
    assert [r["seed"] for r in a] == [r["seed"] for r in b], "seeds misaligned"
    xs = [(num(x[col]), num(y[col])) for x, y in zip(a, b)]
    xs = [p - q for p, q in xs if p is not None and q is not None]
    return ci(xs) if len(xs) > 1 else (float("nan"),) * 3, len(xs), len(a)


def roi(u):
    return (u - 0.3) / 0.65 if u >= 0.3 else u - 0.3


def fmt(m, lo, hi):
    flag = "*" if lo > 0 else ("!" if hi < 0 else " ")
    return f"{m:+.4f}{flag}"


def main():
    data = load()
    n_runs = sum(len(v) for v in data.values())
    print(f"Loaded {n_runs} runs from {len(glob.glob('v2-runs-*.csv.gz'))} shard(s).")
    print("Legend: '*' 95% CI above 0, '!' below 0.\n")

    # ── Q1: positive ceilings vs face value, fans' mean ──────────────────────
    q1 = {}
    print("Q1  Fans' mean utility, ceiling minus face value (both with fee cap)")
    for sname, (listing, v) in SCEN.items():
        for c in CAPS:
            for code in CODES:
                cells, ok = [], True
                for d in LEVELS:
                    (m, lo, hi), _, _ = paired(data, "v2", listing, f"cap{c}", "cap0", d, f"fan_{v}_{code}")
                    ok &= lo > 0
                    cells.append(f"{d:g}x {fmt(m, lo, hi)}")
                q1[(sname, c, code)] = ok
                if code == "P0" or not ok:
                    print(f"  {sname} {c:>2}% {code}: {'PASS' if ok else 'fail'}  " + " ".join(cells))
    print()

    # ── Q2: 30% vs 20% ────────────────────────────────────────────────────────
    print("Q2  Fans' mean utility, 30% minus 20% (P0)")
    for sname, (listing, v) in SCEN.items():
        cells = []
        for d in LEVELS:
            (m, lo, hi), _, _ = paired(data, "v2", listing, "cap30", "cap20", d, f"fan_{v}_P0")
            cells.append(f"{d:g}x {fmt(m, lo, hi)}")
        print(f"  {sname}: " + " ".join(cells))
    print()

    # ── Q3: scalpers fairly governed ─────────────────────────────────────────
    fair = {}
    print(f"Q3  Scalpers fairly governed (at every level 4-10x: ROI in [0, {ROI_MAX:.0%}], dark-routed share <= {DARK_SHARE_MAX:.0%})")
    for listing in ("model", "always"):
        rows = []
        for c in (0, 10, 20, 30, 40):
            ok, cells = True, []
            for d in HIGH:
                rs = data[("v2", listing, f"cap{c}", d)]
                r_ = roi(st.mean(num(r["scalper_util"]) for r in rs))
                routed = st.mean(num(r["dark_routed"]) for r in rs)
                listed = st.mean(num(r["scalper_listed"]) for r in rs)
                share = routed / (routed + listed) if routed + listed else 0.0
                ok &= (0 <= r_ <= ROI_MAX) and share <= DARK_SHARE_MAX
                cells.append(f"{d:g}x {r_:+.0%}/{share:.0%}")
            fair[(listing, c)] = ok
            rows.append(f"    {c:>2}%: {'FAIR' if ok else 'not fair'}  (ROI/dark share) " + " ".join(cells))
        sq = " ".join(f"{d:g}x {roi(st.mean(num(r['scalper_util']) for r in data[('v2', listing, 'SQ', d)])):+.0%}" for d in HIGH)
        print(f"  listing={listing}:")
        print("\n".join(rows))
        print(f"    today's market ROI: {sq}  (index tops out at 100%)")
    print()

    # ── Q4: role-proof against face value ────────────────────────────────────
    q4 = {}
    print("Q4  Role-proof against face value (P0): no fan type lower ex ante, no role lower ex post, scalpers fairly governed")
    for sname, (listing, v) in SCEN.items():
        for c in CAPS:
            fails = []
            for d in LEVELS:
                for t in FAN_TYPES:
                    (m, lo, hi), _, _ = paired(data, "v2", listing, f"cap{c}", "cap0", d, f"type_{t}_{v}_P0")
                    if hi < 0:
                        fails.append(f"ex ante {t} @{d:g}x {m:+.4f}")
                for t, h in ROLES:
                    col = f"role_{t}_{h}_{v}_P0"
                    (m, lo, hi), n_ok, n_all = paired(data, "v2", listing, f"cap{c}", f"cap{c}->cap0", d, col)
                    if n_ok < 0.9 * n_all:
                        continue                                  # role present in <90% of runs
                    if hi < 0:
                        fails.append(f"ex post {t}/{h} @{d:g}x {m:+.4f}")
            if not fair[(listing, c)]:
                fails.append("scalpers not fairly governed")
            q4[(sname, c)] = not fails
            print(f"  {sname} {c:>2}%: {'ROLE-PROOF' if not fails else 'not role-proof'}"
                  + ("" if not fails else f"  ({len(fails)} failures; first: {'; '.join(fails[:3])})"))
    print()

    # ── Q5: against today's market (reported) ────────────────────────────────
    print("Q5  Fans' mean utility, ceiling minus today's market (P0), reported")
    for sname, (listing, v) in SCEN.items():
        for c in (0, 20, 30):
            cells = []
            for d in LEVELS:
                (m, lo, hi), _, _ = paired(data, "v2", listing, f"cap{c}", "SQ", d, f"fan_{v}_P0")
                cells.append(f"{d:g}x {fmt(m, lo, hi)}")
            print(f"  {sname} {c:>2}%: " + " ".join(cells))
    print()

    # ── Reported metrics ─────────────────────────────────────────────────────
    print("Reported (S1 sims, model listing): access mega/casual/average, lawful resale sold, dark sold, seats")
    for d in (2, 5, 10):
        for arm in ("SQ", "cap0", "cap20", "cap30"):
            rs = data[("v2", "model", arm, d)]
            acc = "/".join(f"{st.mean(num(r[f'access_{t}']) for r in rs):.0%}" for t in FAN_TYPES)
            print(f"  {d:>3}x {arm:5s} access {acc}  lawful {st.mean(num(r['secondary_sold']) for r in rs):5.1f}"
                  f"  dark {st.mean(num(r['dark_sold']) for r in rs):5.1f}  seats {st.mean(num(r['seats']) for r in rs):5.1f}")
    print()

    print("v1 vs v2 (model listing, B scoring, P0): dark sold, reseller ROI, seats, fans' mean vs face value")
    for d in (2, 5, 10):
        for c in (0, 20, 30):
            cells = []
            for mech in ("v1", "v2"):
                rs = data[(mech, "model", f"cap{c}", d)]
                ds = st.mean(num(r["dark_sold"]) for r in rs)
                r_ = roi(st.mean(num(r["scalper_util"]) for r in rs))
                se = st.mean(num(r["seats"]) for r in rs)
                diff = "" if c == 0 else fmt(*paired(data, mech, "model", f"cap{c}", "cap0", d, "fan_B_P0")[0])
                cells.append(f"{mech}: dark {ds:5.1f} ROI {r_:+.0%} seats {se:5.1f} fan {diff or '   n/a  '}")
            print(f"  {d:>3}x {c:>2}%  " + " | ".join(cells))
    print()

    # ── Decision rule (V2_PREREGISTRATION.md §5) ─────────────────────────────
    passing = [c for c in CAPS if q1[("S1", c, "P0")] and q1[("S2", c, "P0")]]
    if 20 in passing and 30 in passing:
        rule = "D1: the brief recommends a fixed 20-30% band"
    elif passing:
        rule = f"D2: the brief recommends a modest fixed positive ceiling; passing ceilings: {passing}"
    else:
        rule = "D3: the brief withdraws the positive-ceiling recommendation"
    print("DECISION (pre-registered rule):", rule)
    for c in passing:
        conds = [f"{s} {code}" for s in ("S1", "S2") for code in ("P1", "P2") if not q1[(s, c, code)]]
        bounds = [s for s in ("S3", "S4") if not q1[(s, c, "P0")]]
        print(f"  {c}%: conditions -- fails under {conds or 'none'} (P1/P2); fails in bounds {bounds or 'none'};"
              f" scalpers fair: model={fair[('model', c)]}, always={fair[('always', c)]};"
              f" role-proof vs face: S1={q4[('S1', c)]}, S2={q4[('S2', c)]}")


if __name__ == "__main__":
    main()
