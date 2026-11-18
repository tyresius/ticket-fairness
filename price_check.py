"""
Price-score check — design, predictions and criteria in PRICE_SCORE_CHECK.md
(written 9 Nov 2026 before any P1/P2 number was computed).

Three price scores, only the price term changes (role_proof.price_score):
  P0 saturating  the model's own: 1 at face, 0 at 2x face and above (reference)
  P1 linear      the same slope, no floor
  P2 surplus     share of the fan's own value kept: 1 at face, 0 at the fan's max price

Runs, in order:
  1. main grid (cap sweep as stored, seed 42): C1, C6, C7.
     Harness: P0 must equal the 9 Nov S2 rows of rescore-grid.csv (all series but
     Dynamic Pricing, whose surcharge term is now applied).
  2. role-proof (same 121,000 sims and seeds as 5 Nov): R1.
     Harness: P0 at kappa 0 must equal role-proof-summary.csv exactly.
Verdicts are printed only if both harness checks pass.

Usage:
    python3 price_check.py            # full run (~35-45 min)
    python3 price_check.py --smoke    # mechanics + first grid cell harness only; no results
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
import time

from gre_sim import DEFAULT_GR_W, DEFAULT_UTILITY_W, FACE, FAN_TYPES, simulate
import role_proof as rp
from rescore_check import OVERSUBSCRIBED, calc_gr, write_csv
from sweep_config import BOUNDED_LABELS, DEMAND_LEVELS, RUNS_PER_POINT, build_series

FORMS = rp.PRICE_FORMS                                  # saturating, linear, surplus
CODE = {"saturating": "P0", "linear": "P1", "surplus": "P2"}
JUDGED = ("linear", "surplus")                          # P0 is reference only
LENSES = ("system", "fan_only", "pop_wt")
RP_VARIANTS = [(0.0, False, "saturating")] + [(k, False, f) for f in JUDGED for k in rp.KAPPAS]
LOW_CAPS = ("Bounded 10%", "Bounded 15%", "Bounded 20%")


def resent_for(rule, res) -> float:
    """Dynamic pricing's resented surcharge, as gre_sim.py:745-748."""
    if rule.dyn_mul and rule.dyn_mul > 1:
        return (res["sale_price"] - FACE) / FACE * 0.3
    return 0.0


def score_run(res, rule, uw=DEFAULT_UTILITY_W, gw=DEFAULT_GR_W):
    """{form: {lens: value, fan_mean: mean individual fan utility}} for one run.
    Fan types = mean of individual scores (as 9 Nov S2); scalper utility as the model."""
    agents = res["agents"]
    types = list(res["outcomes"].keys())
    groups = {t: [a for a in agents if a.type == t] for t in types}
    resent = resent_for(rule, res)
    out = {}
    for f in FORMS:
        per = {t: [rp.agent_utility(a, res, 0.0, False, uw, price_form=f, resent=resent)
                   for a in groups[t]] for t in FAN_TYPES}
        u = {t: (res["outcomes"][t]["utility"] if t not in FAN_TYPES
                 else round(sum(per[t]) / len(per[t]), 4)) for t in types}
        fans = [x for t in FAN_TYPES for x in per[t]]
        out[f] = dict(system=calc_gr([u[t] for t in types], gw),
                      fan_only=calc_gr([u[t] for t in FAN_TYPES], gw),
                      pop_wt=calc_gr([u[t] for t in types for _ in range(len(groups[t]))], gw),
                      fan_mean=sum(fans) / len(fans))
    return out


def main_grid(series_list=None, demands=DEMAND_LEVELS, runs=RUNS_PER_POINT, verbose=True):
    random.seed(42)                                       # as cap_sweep.py / rescore_check.py
    rows = []
    for series in (series_list or build_series()):
        skw = series.get("sim_kwargs", {})
        for mul in demands:
            vals = {f: {k: [] for k in LENSES + ("fan_mean",)} for f in FORMS}
            for _ in range(runs):
                res = simulate(series["rule"], mul, return_agents=True, **skw)
                for f, v in score_run(res, series["rule"]).items():
                    for k in v:
                        vals[f][k].append(v[k])
            for f in FORMS:
                rows.append(dict(series=series["label"], demand=mul, price=CODE[f],
                                 **{k: round(sum(vals[f][k]) / runs, 4) for k in LENSES},
                                 fan_mean=round(sum(vals[f]["fan_mean"]) / runs, 5)))
        if verbose:
            sys.stdout.write(f"\r  grid: {series['label']:<32}")
            sys.stdout.flush()
    if verbose:
        print()
    return rows


def check_grid(rows):
    """Harness 2: P0 == 9 Nov S2 (rescore-grid.csv), every series but Dynamic Pricing."""
    stored = {(r["series"], float(r["demand"])): r for r in csv.DictReader(open("rescore-grid.csv"))
              if r["scoring"] == "S2"}
    bad = checked = 0
    for r in rows:
        if r["price"] != "P0" or r["series"] == "Dynamic Pricing":
            continue
        s = stored.get((r["series"], float(r["demand"])))
        if s is None:
            continue
        for lk in LENSES:
            checked += 1
            if abs(r[lk] - float(s[lk])) > 1e-9:
                bad += 1
                print(f"  mismatch {r['series']} @ {r['demand']} {lk}: {r[lk]} vs stored {s[lk]}")
    return bad, checked


def check_role_proof(rows):
    """Harness 1: P0 kappa 0 gaps == role-proof-summary.csv (kappa 0, no proceeds)."""
    stored = {(float(r["demand"]), r["rule"]): r for r in csv.DictReader(open("role-proof-summary.csv"))
              if float(r["kappa"]) == 0.0 and r["proceeds"] == "False"}
    bad = checked = 0
    for r in rows:
        if r.get("price_form") != "saturating":
            continue
        s = stored[(float(r["demand"]), r["rule"])]
        for col in ("ex_ante_gap", "ex_post_gap"):
            checked += 1
            if abs(r[col] - float(s[col])) > 1e-9:
                bad += 1
                print(f"  mismatch {r['rule']} @ {r['demand']} {col}: {r[col]} vs stored {s[col]}")
        if str(r["role_proof"]) != s["role_proof"]:
            bad += 1
            print(f"  mismatch {r['rule']} @ {r['demand']} role_proof: {r['role_proof']} vs {s['role_proof']}")
    return bad, checked


def verdicts(grid, rp_rows):
    G = {(r["series"], r["demand"], r["price"]): r for r in grid}
    out, holds = [], {}
    for f in FORMS:
        p = CODE[f]

        def g(series, d, k="pop_wt"):
            return G[(series, d, p)][k]
        # R1: pre-stated role-proof criterion, kappa 0
        passed, n, lines = rp.role_proof_levels(rp_rows, (0.0, False, f))
        holds[("R1", f)] = passed >= 6
        out.append(f"R1 [{p}] 10-20% cap role-proof at {passed} of {n} levels")
        out.extend(lines)
        # C1
        best = {d: max(BOUNDED_LABELS, key=lambda lab: g(lab, d)) for d in OVERSUBSCRIBED}
        caps = {d: int(best[d].split()[1].rstrip("%")) for d in OVERSUBSCRIBED}
        holds[("C1", f)] = all(10 <= c <= 30 for c in caps.values())
        out.append(f"C1 [{p}] PopWt-best cap by demand: " + ", ".join(f"{d}x {caps[d]}%" for d in OVERSUBSCRIBED))
        # C6
        fails = []
        for d in OVERSUBSCRIBED:
            for lk in ("pop_wt", "system"):
                b = max(g(lab, d, lk) for lab in BOUNDED_LABELS)
                for other in ("Status Quo", "Dynamic Pricing", "UK Face Value"):
                    if b <= g(other, d, lk):
                        fails.append(f"{d}x {lk} vs {other}")
        holds[("C6", f)] = not fails
        out.append(f"C6 [{p}] best bounded loses at: {fails if fails else 'none'}")
        # C7
        diffs = {d: max(g(lab, d, "fan_mean") for lab in LOW_CAPS) - g("Status Quo", d, "fan_mean")
                 for d in OVERSUBSCRIBED}
        holds[("C7", f)] = all(x > 0 for x in diffs.values())
        out.append(f"C7 [{p}] best 10-20% minus status quo, mean fan utility: "
                   + ", ".join(f"{d}x {x:+.4f}" for d, x in diffs.items()))
        out.append("")
    for c in ("R1", "C1", "C6", "C7"):
        a, b = holds[(c, "linear")], holds[(c, "surplus")]
        v = "SURVIVES" if a and b else ("SURVIVES UNDER ONE (" + ("P1" if a else "P2") + ")" if a or b else "FAILS")
        ref = "" if c == "C7" else f"   (P0 reference: {'true' if holds[(c, 'saturating')] else 'false'})"
        out.append(f"{c}: {v}{ref}")
    out.append("\nSensitivity (no verdict): R1 at kappa 0.5 and 1")
    for f in JUDGED:
        for k in rp.KAPPAS[1:]:
            passed, n, _ = rp.role_proof_levels(rp_rows, (k, False, f))
            out.append(f"  [{CODE[f]}] kappa {k}: 10-20% cap role-proof at {passed} of {n} levels")
    return "\n".join(out)



# ── Amendment 1 (PRICE_SCORE_CHECK.md): a single fixed cap ──────────────────
def amendment_verdicts(grid, rp_rows):
    """R2: one bounded cap is role-proof at >= 6 of 9 levels (kappa 0).
    C8: one bounded cap within rp.TOLERANCE of the PopWt-best bounded cap at all 9
    levels, and beating Status Quo and Dynamic Pricing on PopWt and System at all 9."""
    G = {(r["series"], r["demand"], r["price"]): r for r in grid}
    out, holds = [], {}
    for f in FORMS:
        p = CODE[f]
        # R2
        counts = {}
        for lab in BOUNDED_LABELS:
            counts[lab] = sum(1 for r in rp_rows
                              if r["kappa"] == 0.0 and r["proceeds"] is False
                              and r.get("price_form") == f and r["rule"] == lab
                              and r["demand"] in OVERSUBSCRIBED and r["role_proof"])
        top = max(BOUNDED_LABELS, key=lambda lab: counts[lab])
        holds[("R2", f)] = counts[top] >= 6
        out.append(f"R2 [{p}] most often role-proof single cap: {top} at {counts[top]} of {len(OVERSUBSCRIBED)} levels")
        # C8
        worst, beats = {}, {}
        for lab in BOUNDED_LABELS:
            sf, ok = [], True
            for d in OVERSUBSCRIBED:
                best = max(G[(b, d, p)]["pop_wt"] for b in BOUNDED_LABELS)
                sf.append(round(best - G[(lab, d, p)]["pop_wt"], 4))
                for lk in ("pop_wt", "system"):
                    for other in ("Status Quo", "Dynamic Pricing"):
                        ok &= G[(lab, d, p)][lk] > G[(other, d, p)][lk]
            worst[lab], beats[lab] = max(sf), ok
        qualify = [lab for lab in BOUNDED_LABELS if worst[lab] <= rp.TOLERANCE and beats[lab]]
        holds[("C8", f)] = bool(qualify)
        closest = min(BOUNDED_LABELS, key=lambda lab: worst[lab])
        out.append(f"C8 [{p}] closest single cap: {closest}, worst-level shortfall {worst[closest]:.4f}, "
                   f"beats SQ and DP everywhere: {beats[closest]}; caps meeting C8: {qualify or 'none'}")
        out.append(f"       worst shortfall by cap: "
                   + ", ".join(f"{lab.split()[1]} {worst[lab]:.3f}{'' if beats[lab] else '*'}"
                               for lab in BOUNDED_LABELS) + "   (* = loses to SQ or DP somewhere)")
    out.append("")
    for c in ("R2", "C8"):
        a, b = holds[(c, "linear")], holds[(c, "surplus")]
        v = "SURVIVES" if a and b else ("SURVIVES UNDER ONE (" + ("P1" if a else "P2") + ")" if a or b else "FAILS")
        out.append(f"{c}: {v}   (P0 reference: {'true' if holds[(c, 'saturating')] else 'false'})")
    return "\n".join(out)


def load_outputs():
    """Re-read the run's CSVs with the types the verdict code expects."""
    grid = []
    for r in csv.DictReader(open("price-check-grid.csv")):
        grid.append(dict(series=r["series"], demand=float(r["demand"]), price=r["price"],
                         **{k: float(r[k]) for k in LENSES + ("fan_mean",)}))
    rows = []
    for r in csv.DictReader(open("price-check-roleproof-summary.csv")):
        rows.append(dict(r, kappa=float(r["kappa"]), proceeds=(r["proceeds"] == "True"),
                         demand=float(r["demand"]), ex_ante_gap=float(r["ex_ante_gap"]),
                         ex_post_gap=float(r["ex_post_gap"]), role_proof=(r["role_proof"] == "True")))
    return grid, rows

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="mechanics + first-cell harness only; prints no P1/P2 numbers")
    ap.add_argument("--verdicts", action="store_true",
                    help="re-read the CSVs, re-run both harness checks, print every verdict incl. amendment 1")
    a = ap.parse_args()
    t0 = time.time()
    if a.verdicts:
        grid, rp_rows = load_outputs()
        b2, c2 = check_grid(grid)
        b1, c1 = check_role_proof(rp_rows)
        print(f"Harness check 2 (grid): {b2} mismatches of {c2}; harness check 1 (role-proof): {b1} mismatches of {c1}")
        if b1 or b2:
            print("Harness failed; nothing below is valid.")
            sys.exit(1)
        print("\nPre-registered claims:\n")
        print(verdicts(grid, rp_rows))
        print("\nAmendment 1 claims:\n")
        print(amendment_verdicts(grid, rp_rows))
        sys.exit(0)
    if a.smoke:
        sq = [s for s in build_series() if s["label"] == "Status Quo"]
        rows = main_grid(sq, demands=[DEMAND_LEVELS[0]], verbose=False)   # first cell of the seed-42 stream
        bad, checked = check_grid(rows)
        dp = [s for s in build_series() if s["label"] == "Dynamic Pricing"][0]
        random.seed(1)
        res = simulate(dp["rule"], 5, return_agents=True)
        assert resent_for(dp["rule"], res) > 0
        sr = score_run(res, dp["rule"])
        assert set(sr) == set(FORMS)
        out = rp.run([5], 2, variants=RP_VARIANTS, verbose=False)
        rr, rl = rp.summarise(out, [5], variants=RP_VARIANTS)
        forms_seen = sorted({r["price_form"] for r in rr})
        print(f"smoke: first grid cell P0 vs stored S2 -> {bad} mismatches of {checked}; "
              f"role-proof rows {len(rr)}, forms {forms_seen}; {time.time() - t0:.0f}s. "
              f"No P1/P2 results printed by design.")
        sys.exit(1 if bad else 0)

    print("Price-score check (PRICE_SCORE_CHECK.md)\n1. main grid")
    grid = main_grid()
    write_csv("price-check-grid.csv", grid)
    bad, checked = check_grid(grid)
    print(f"\nHarness check 2: P0 grid vs rescore-grid.csv S2 -> {bad} mismatches of {checked}")
    if bad:
        print("P0 does not reproduce the 9 Nov S2 grid; stopping (nothing below is valid).")
        sys.exit(1)

    print(f"\n2. role-proof ({len(RP_VARIANTS)} scorings)")
    out = rp.run(DEMAND_LEVELS, RUNS_PER_POINT, variants=RP_VARIANTS)
    rp_rows, rp_roles = rp.summarise(out, DEMAND_LEVELS, variants=RP_VARIANTS)
    write_csv("price-check-roleproof-summary.csv", rp_rows)
    write_csv("price-check-roleproof-roles.csv", rp_roles)
    bad, checked = check_role_proof(rp_rows)
    print(f"\nHarness check 1: P0 role-proof vs role-proof-summary.csv -> {bad} mismatches of {checked}")
    if bad:
        print("P0 does not reproduce the 5 Nov role-proof run; stopping (nothing below is valid).")
        sys.exit(1)

    print(f"\nVerdicts (criteria in PRICE_SCORE_CHECK.md), {time.time() - t0:.0f}s:\n")
    print(verdicts(grid, rp_rows))
