"""
Re-check of POLICY_BRIEF.md's welfare claims under corrected fan scoring.
Method and survival criteria are fixed in RESCORE_CHECK.md (written before any run).

Three scorings on the same runs:
  S0  the model's own type formula, re-implemented from agent records; must
      reproduce the model's per-run outcomes exactly (harness check)
  S1  S0 with the price score multiplied by the type's access rate (the one
      flagged inconsistency; nothing else changes)
  S2  each type's utility = mean of its members' individual scores
      (role_proof.agent_utility, kappa 0, no proceeds)
Scalper utility, the GR composite and every simulation are identical across them.

Usage:  python3 rescore_check.py           (writes rescore-*.csv; log to stdout)
"""
from __future__ import annotations

import csv
import math
import random
import statistics as st
import sys
import time

import numpy as np

from gre_sim import (BASELINE_SECONDARY_FRAUD_PENALTY, DEFAULT_GR_W, DEFAULT_UTILITY_W,
                     FACE, FAN_TYPES, Rule, simulate)
from role_proof import agent_utility, upside_value
from sweep_config import BOUNDED_LABELS, DEMAND_LEVELS, RUNS_PER_POINT, build_series

SCORINGS = ("S0", "S1", "S2")
LENSES = ("system", "fan_only", "pop_wt")
OVERSUBSCRIBED = [d for d in DEMAND_LEVELS if d > 1]


# ── Scoring ──────────────────────────────────────────────────────────────────
def fan_type_utility(grp, res, rule, uw, scoring):
    """Fan-type utility under S0 / S1 / S2 (see module docstring)."""
    if scoring == "S2":
        return round(sum(agent_utility(a, res, 0.0, False, uw) for a in grp) / len(grp), 4)

    total = len(grp)
    got = [a for a in grp if a.tickets > 0 or a.phase in ("bought_secondary", "bought_dark")]
    att = [a for a in grp if a.attending]
    if not got:
        return 0.02

    def paid(a):
        if a.phase == "bought_secondary":
            return a.secondary_price * (1 + res["secondary_fee_buyer"])
        return a.secondary_price or a.cost_basis or 0
    avg_paid = sum(paid(a) for a in got) / len(got)
    access_rate = len(got) / total
    price_ratio = (avg_paid - FACE) / FACE if avg_paid > 0 else 0
    price_score = max(0.0, 1 - price_ratio) if avg_paid > 0 else 0.0
    if rule.dyn_mul and rule.dyn_mul > 1:
        price_score = max(0.0, price_score - (res["sale_price"] - FACE) / FACE * 0.3)
    if scoring == "S1":
        price_score *= access_rate
    attend_rate = len(att) / total
    crule = res["continuation_rule"]
    resale_opt = 0.70 if crule.cap is None else upside_value(crule.cap - res["secondary_fee_seller"])
    resale_opt *= min(1.0, access_rate * 3)
    u = (access_rate * uw["access"] + price_score * uw["price"]
         + attend_rate * uw["attend"] + resale_opt * uw["resale_opt"])
    dark_frac = sum(1 for a in got if a.dark_market) / len(got)
    u = max(0.0, u - dark_frac * res["dark_fraud_penalty"])
    if crule.cap is None:
        sec_frac = sum(1 for a in got if a.phase == "bought_secondary") / len(got)
        u = max(0.0, u - sec_frac * BASELINE_SECONDARY_FRAUD_PENALTY)
    u = max(0.0, u - res["systemic_penalty"])
    return round(u, 4)


def calc_gr(vals, gw):
    mn, mx, av = min(vals), max(vals), sum(vals) / len(vals)
    return round(mn * gw["floor"] + (1 - (mx - mn)) * gw["equality"]
                 + av * gw["average"] + 0.5 * gw["baseline"], 4)


def lenses(res, rule, uw=DEFAULT_UTILITY_W, gw=DEFAULT_GR_W, check=True):
    """{scoring: {lens: value}} for one run. With check=True, S0 must equal the
    model's own per-type outcomes and lenses, or the harness is wrong."""
    agents = res["agents"]
    types = list(res["outcomes"].keys())                 # model's defs order
    groups = {t: [a for a in agents if a.type == t] for t in types}
    out = {}
    for sc in SCORINGS:
        u = {t: (res["outcomes"][t]["utility"] if t not in FAN_TYPES
                 else fan_type_utility(groups[t], res, rule, uw, sc)) for t in types}
        if check and sc == "S0":
            for t in FAN_TYPES:
                if u[t] != res["outcomes"][t]["utility"]:
                    raise AssertionError(f"S0 mismatch {rule.name} {t}: {u[t]} vs {res['outcomes'][t]['utility']}")
        out[sc] = dict(
            system=calc_gr([u[t] for t in types], gw),
            fan_only=calc_gr([u[t] for t in FAN_TYPES], gw),
            pop_wt=calc_gr([u[t] for t in types for _ in range(len(groups[t]))], gw),
        )
        if check and sc == "S0":
            for lk in LENSES:
                if out[sc][lk] != res[lk]:
                    raise AssertionError(f"S0 lens mismatch {rule.name} {lk}: {out[sc][lk]} vs {res[lk]}")
    return out


# ── Run 1: main grid (cap sweep exactly as stored) ───────────────────────────
def main_grid():
    random.seed(42)                                       # as cap_sweep.py
    rows = []
    for series in build_series():
        skw = series.get("sim_kwargs", {})
        for mul in DEMAND_LEVELS:
            # Collect then sum(), exactly as cap_sweep.avg_f does: Python's
            # sum() of floats is compensated (3.12+), so += accumulation can
            # differ in the last bit and flip a 4-dp rounding.
            vals_by = {sc: {lk: [] for lk in LENSES} for sc in SCORINGS}
            for _ in range(RUNS_PER_POINT):
                res = simulate(series["rule"], mul, return_agents=True, **skw)
                for sc, vals in lenses(res, series["rule"]).items():
                    for lk in LENSES:
                        vals_by[sc][lk].append(vals[lk])
            for sc in SCORINGS:
                rows.append(dict(series=series["label"], demand=mul, scoring=sc,
                                 **{lk: round(sum(vals_by[sc][lk]) / RUNS_PER_POINT, 4) for lk in LENSES}))
        sys.stdout.write(f"\r  grid: {series['label']:<32}")
        sys.stdout.flush()
    print()
    return rows


def check_grid_against_stored(rows):
    stored = {(r["series"], float(r["demand"])): r for r in csv.DictReader(open("cap-sweep-summary.csv"))}
    bad = 0
    for r in rows:
        if r["scoring"] != "S0":
            continue
        s = stored[(r["series"], float(r["demand"]))]
        for lk, col in (("system", "gr_system"), ("fan_only", "gr_fan"), ("pop_wt", "gr_popwt")):
            if abs(r[lk] - float(s[col])) > 1e-9:
                bad += 1
                print(f"  mismatch {r['series']} @ {r['demand']} {lk}: {r[lk]} vs stored {s[col]}")
    return bad


# ── Run 2: paired 10% vs face value (C4, C5) ─────────────────────────────────
def paired(n=300):
    b10 = Rule("Bounded 10%", cap=0.10, plimit=4, dyn_mul=None)
    b0 = Rule("Bounded 0%", cap=0.0, plimit=4, dyn_mul=None)
    fv_tough = Rule("Face value, 2-ticket limit", cap=0.0, plimit=2, dyn_mul=None)
    arms = [("C4 fees 5%/side", 0.05, b0, {}),
            ("C4 fees 10%/side", 0.10, b0, {}),
            ("C5 tough face value, fees 10%/side", 0.10, fv_tough, dict(scalper_dark_cost=0.65))]
    rows = []
    for name, fee, other, other_kw in arms:
        fees = dict(secondary_fee_seller=fee, secondary_fee_buyer=fee)
        for d_idx, d in enumerate(OVERSUBSCRIBED):
            diffs = {sc: [] for sc in SCORINGS}
            for s in range(n):
                seed = 77_000_000 + 10_000 * d_idx + s
                random.seed(seed)
                r10 = simulate(b10, d, return_agents=True, **fees)
                random.seed(seed)
                ro = simulate(other, d, return_agents=True, **fees, **other_kw)
                l10, lo = lenses(r10, b10), lenses(ro, other)
                for sc in SCORINGS:
                    diffs[sc].append(l10[sc]["pop_wt"] - lo[sc]["pop_wt"])
            for sc in SCORINGS:
                m, sd = st.mean(diffs[sc]), st.stdev(diffs[sc])
                half = 1.96 * sd / math.sqrt(n)
                rows.append(dict(arm=name, demand=d, scoring=sc, mean_diff=round(m, 5),
                                 ci_low=round(m - half, 5), ci_high=round(m + half, 5), n=n))
        sys.stdout.write(f"\r  paired: {name:<40}")
        sys.stdout.flush()
    print()
    return rows


# ── Run 3: robustness on the original 400 joint draws (C3) ───────────────────
def lhs(n_check=20):
    import global_sensitivity as gs                    # reproduces the original draws
    np.random.seed(gs.SEED)
    samples = gs.latin_hypercube(gs.N_SAMPLES, gs.RANGES)
    sq = Rule("Status Quo", cap=None, plimit=8, dyn_mul=None)
    caps = {c: Rule(f"Bounded {round(c * 100)}%", cap=c, plimit=4, dyn_mul=None) for c in gs.CAPS}

    def mean_lenses(rule, kwargs):
        acc = {sc: {lk: 0.0 for lk in LENSES} for sc in SCORINGS}
        cnt = 0
        uw = kwargs.get("utility_w", DEFAULT_UTILITY_W)
        gw = kwargs.get("gr_w", DEFAULT_GR_W)
        for mul in gs.DEMANDS:
            for _ in range(gs.RUNS):
                res = simulate(rule, mul, return_agents=True, **kwargs)
                for sc, vals in lenses(res, rule, uw, gw).items():
                    for lk in LENSES:
                        acc[sc][lk] += vals[lk]
                cnt += 1
        return {sc: {lk: acc[sc][lk] / cnt for lk in LENSES} for sc in SCORINGS}

    def one_draw(s, externality_off):
        assignment = {gs.PARAM_NAMES[j]: samples[s, j] for j in range(len(gs.PARAM_NAMES))}
        kwargs = gs.build_kwargs(assignment)
        if externality_off:
            kwargs["systemic_fraud_weight"] = 0.0
        base = mean_lenses(sq, kwargs)
        capv = {c: mean_lenses(caps[c], kwargs) for c in gs.CAPS}
        return {sc: {lk: max(capv[c][sc][lk] for c in gs.CAPS) - base[sc][lk] for lk in LENSES}
                for sc in SCORINGS}

    # Harness check: original settings, first n_check draws, S0 vs the stored file.
    random.seed(gs.SEED)
    stored = list(csv.DictReader(open("global-sensitivity-samples.csv")))
    mism = 0
    for s in range(n_check):
        adv = one_draw(s, externality_off=False)["S0"]
        for lk, col in (("fan_only", "adv_Fan"), ("pop_wt", "adv_PopWt"), ("system", "adv_System")):
            if abs(round(adv[lk], 4) - float(stored[s][col])) > 1e-9:
                mism += 1
    # Re-run: externality off, all draws.
    random.seed(gs.SEED)
    rows = []
    for s in range(gs.N_SAMPLES):
        adv = one_draw(s, externality_off=True)
        for sc in SCORINGS:
            rows.append(dict(draw=s, scoring=sc, **{f"adv_{lk}": round(adv[sc][lk], 5) for lk in LENSES}))
        if (s + 1) % 20 == 0:
            sys.stdout.write(f"\r  robustness: {s + 1}/{gs.N_SAMPLES}")
            sys.stdout.flush()
    print()
    return rows, mism


# ── Verdicts (criteria fixed in RESCORE_CHECK.md) ────────────────────────────
def verdicts(grid, pairs, lhs_rows):
    G = {(r["series"], r["demand"], r["scoring"]): r for r in grid}
    out, holds = [], {}

    def pw(series, d, sc, lk="pop_wt"):
        return G[(series, d, sc)][lk]

    for sc in SCORINGS:
        # C1: PopWt-best bounded cap (0-50%) in 10-30% at all oversubscribed levels
        best = {d: max(BOUNDED_LABELS, key=lambda lab: pw(lab, d, sc)) for d in OVERSUBSCRIBED}
        caps = {d: int(best[d].split()[1].rstrip("%")) for d in OVERSUBSCRIBED}
        holds[("C1", sc)] = all(10 <= c <= 30 for c in caps.values())
        out.append(f"C1 [{sc}] PopWt-best cap by demand: " + ", ".join(f"{d}x {caps[d]}%" for d in OVERSUBSCRIBED))
        # C2: median of (B20+fee - SQ) / (UK2026 - SQ) > 2
        ratios = []
        for d in OVERSUBSCRIBED:
            num = pw("Bounded 20% + fee cap", d, sc) - pw("Status Quo", d, sc)
            den = pw("UK 2026 (0% + fee cap)", d, sc) - pw("Status Quo", d, sc)
            ratios.append(num / den if den > 0 else (math.inf if num > 0 else -math.inf))
        med = st.median(ratios)
        holds[("C2", sc)] = med > 2
        out.append(f"C2 [{sc}] package/fee-only ratio by demand: "
                   + ", ".join(f"{d}x {r:.2f}" for d, r in zip(OVERSUBSCRIBED, ratios)) + f"; median {med:.2f}")
        # C6: best bounded beats SQ, DP and UK Face Value on PopWt and System at all levels
        fails = []
        for d in OVERSUBSCRIBED:
            for lk in ("pop_wt", "system"):
                b = max(pw(lab, d, sc, lk) for lab in BOUNDED_LABELS)
                for other in ("Status Quo", "Dynamic Pricing", "UK Face Value"):
                    if b <= pw(other, d, sc, lk):
                        fails.append(f"{d}x {lk} vs {other}")
        holds[("C6", sc)] = not fails
        out.append(f"C6 [{sc}] best bounded loses at: {fails if fails else 'none'}")
        # C3: robustness
        rr = [r for r in lhs_rows if r["scoring"] == sc]
        share = {lk: sum(r[f"adv_{lk}"] > 0 for r in rr) / len(rr) for lk in LENSES}
        holds[("C3", sc)] = share["pop_wt"] >= 0.95 and share["system"] >= 0.95
        out.append(f"C3 [{sc}] share of draws where best of 10/20/30% beats status quo: "
                   + ", ".join(f"{lk} {share[lk]:.1%}" for lk in LENSES))
        # C4 / C5: paired
        for claim, arms in (("C4", ("C4 fees 5%/side", "C4 fees 10%/side")),
                            ("C5", ("C5 tough face value, fees 10%/side",))):
            ok = True
            for arm in arms:
                pr = [p for p in pairs if p["arm"] == arm and p["scoring"] == sc]
                lost = [p["demand"] for p in pr if not p["ci_low"] > 0]
                ok &= not lost
                out.append(f"{claim} [{sc}] {arm}: 10% not clearly ahead at {lost if lost else 'no level'}; "
                           + "mean diffs " + ", ".join(f"{p['demand']}x {p['mean_diff']:+.3f}" for p in pr))
            holds[(claim, sc)] = ok
    out.append("")
    for c in ("C1", "C2", "C3", "C4", "C5", "C6"):
        s1, s2 = holds[(c, "S1")], holds[(c, "S2")]
        v = "SURVIVES" if s1 and s2 else ("SURVIVES UNDER ONE (" + ("S1" if s1 else "S2") + ")" if s1 or s2 else "FAILS")
        out.append(f"{c}: {v}   (S0 baseline: {'true' if holds[(c, 'S0')] else 'false'})")
    return "\n".join(out)


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    t0 = time.time()
    grid = main_grid()
    bad = check_grid_against_stored(grid)
    print(f"Harness check 1: S0 vs stored cap-sweep-summary.csv -> {bad} mismatches")
    if bad:
        sys.exit("S0 does not reproduce the stored grid; stopping (nothing below is valid).")
    write_csv("rescore-grid.csv", grid)
    pairs = paired()
    write_csv("rescore-paired.csv", pairs)
    lhs_rows, mism = lhs()
    print(f"Harness check 2: S0 vs stored global-sensitivity-samples.csv (first 20 draws) -> {mism} mismatches")
    if mism:
        sys.exit("S0 does not reproduce the stored robustness draws; stopping.")
    write_csv("rescore-lhs.csv", lhs_rows)
    print(f"\nVerdicts (criteria in RESCORE_CHECK.md), {time.time() - t0:.0f}s:\n")
    print(verdicts(grid, pairs, lhs_rows))
