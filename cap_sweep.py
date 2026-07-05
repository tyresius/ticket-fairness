"""
Cap Optimization Sweep
======================

Sweeps bounded-market cap levels against reference rulesets (status quo,
dynamic pricing, UK face value) across demand multipliers. Uses the canonical
simulation in gre_sim.py — no sim logic is defined here.

Outputs:
  cap-sweep-summary.csv  — GR scores + ticket flow per (series, demand)
  cap-sweep-agents.csv   — per-agent-type utility/access/price per (series, demand)
"""

import csv
import random
import sys

from gre_sim import simulate, Rule, DEFS

# C1 fix (2026-04-27): fixed seed for reproducibility. All results from this
# script can be regenerated bit-for-bit with this seed. Change only when
# intentionally altering the sweep configuration, and document the change.
random.seed(42)

# ── Sweep configuration ───────────────────────────────────────────────────────
# Extracted to sweep_config.py (2026-07-04) so rawls_analysis.py and
# generate_charts.py can't silently desync from the grid actually swept.
# Historical notes: Bounded 0% added 2026-04-21 alongside UK Face Value
# (a distinct real-world comparator with a 2-ticket limit); RUNS_PER_POINT
# raised 30 -> 100 by the C2 fix (MOE ~±0.010 vs ±0.018).
from sweep_config import DEMAND_LEVELS, CAP_LEVELS, RUNS_PER_POINT, build_series

SERIES = build_series()


def avg_f(runs, fn):
    return round(sum(fn(r) for r in runs) / len(runs), 4)

def avg_i(runs, fn):
    return round(sum(fn(r) for r in runs) / len(runs))


total_sims = len(SERIES) * len(DEMAND_LEVELS) * RUNS_PER_POINT
print(f"Running sweep: {len(SERIES)} series × {len(DEMAND_LEVELS)} demand levels × "
      f"{RUNS_PER_POINT} runs = {total_sims} simulations")

summary_rows = []
agent_rows   = []

for series in SERIES:
    sys.stdout.write(f"  {series['label']:<20}")
    sys.stdout.flush()
    for mul in DEMAND_LEVELS:
        runs = [simulate(series["rule"], mul) for _ in range(RUNS_PER_POINT)]

        system      = avg_f(runs, lambda r: r["system"])
        fan_only    = avg_f(runs, lambda r: r["fan_only"])
        pop_wt      = avg_f(runs, lambda r: r["pop_wt"])
        ex_ante_fan = avg_f(runs, lambda r: r["ex_ante_fan"])
        ex_ante_pw  = avg_f(runs, lambda r: r["ex_ante_popwt"])
        attend      = avg_i(runs, lambda r: r["attend"])
        wasted      = avg_i(runs, lambda r: r["wasted"])
        dark_s      = avg_i(runs, lambda r: r["dark_sold"])
        dark_u      = avg_i(runs, lambda r: r["dark_unmatched"])
        cap_pct     = round(series["rule"].cap * 100) if series["rule"].cap is not None else "N/A"

        summary_rows.append(dict(
            series              = series["label"],
            cap_pct             = cap_pct,
            demand              = mul,
            gr_system           = system,
            gr_fan              = fan_only,
            gr_popwt            = pop_wt,
            gr_ex_ante_fan      = ex_ante_fan,
            gr_ex_ante_popwt    = ex_ante_pw,
            # Alternative welfare criteria
            rawls_fan           = avg_f(runs, lambda r: r["rawls_fan"]),
            rawls_all           = avg_f(runs, lambda r: r["rawls_all"]),
            rawls_ea_fan        = avg_f(runs, lambda r: r["rawls_ea_fan"]),
            harsanyi_eq_fan     = avg_f(runs, lambda r: r["harsanyi_eq_fan"]),
            harsanyi_eq_all     = avg_f(runs, lambda r: r["harsanyi_eq_all"]),
            harsanyi_pop_all    = avg_f(runs, lambda r: r["harsanyi_pop_all"]),
            harsanyi_pop_fan    = avg_f(runs, lambda r: r["harsanyi_pop_fan"]),
            attend              = attend,
            wasted              = wasted,
            dark_sold           = dark_s,
            dark_unmatched      = dark_u,
        ))

        for tid in DEFS:
            u   = avg_f(runs, lambda r, t=tid: r["outcomes"][t]["utility"])
            ea  = avg_f(runs, lambda r, t=tid: r["outcomes"][t]["ex_ante"])
            got = avg_i(runs, lambda r, t=tid: r["outcomes"][t]["got"])
            tot = avg_i(runs, lambda r, t=tid: r["outcomes"][t]["total"])
            ap  = avg_i(runs, lambda r, t=tid: r["outcomes"][t]["avg_price"])
            agent_rows.append(dict(
                series     = series["label"],
                cap_pct    = cap_pct,
                demand     = mul,
                agent      = tid,
                utility    = u,
                ex_ante    = ea,
                got        = got,
                total      = tot,
                access_pct = round(got / tot * 100) if tot else 0,
                avg_price  = ap,
            ))
        sys.stdout.write(".")
        sys.stdout.flush()
    print()

# ── Write CSVs ────────────────────────────────────────────────────────────────
def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

write_csv("cap-sweep-summary.csv", summary_rows)
write_csv("cap-sweep-agents.csv",  agent_rows)
print("\nWrote cap-sweep-summary.csv  and  cap-sweep-agents.csv")


# ── Console: optimal-cap tables ───────────────────────────────────────────────
def optimal_cap_table(lens_key, lens_name):
    print(f"\n── Optimal bounded cap by demand level ({lens_name} lens) ──")
    print(f"{'Demand':>7} | {'Opt Cap':>7} | {lens_name:>8} | {'vs SQ':>7} | {'vs Dyn':>7} | {'vs UK':>7}")
    print("-" * 62)
    for mul in DEMAND_LEVELS:
        sq  = next(r for r in summary_rows if r["series"] == "Status Quo"      and r["demand"] == mul)
        dyn = next(r for r in summary_rows if r["series"] == "Dynamic Pricing" and r["demand"] == mul)
        uk  = next(r for r in summary_rows if r["series"] == "UK Face Value"   and r["demand"] == mul)
        bounded = [r for r in summary_rows if r["series"].startswith("Bounded") and r["demand"] == mul]
        best = max(bounded, key=lambda r: r[lens_key])
        d_sq  = best[lens_key] - sq[lens_key]
        d_dyn = best[lens_key] - dyn[lens_key]
        d_uk  = best[lens_key] - uk[lens_key]
        print(f"  {mul:>5} | {str(best['cap_pct'])+'%':>7} | {best[lens_key]:>8.4f} | "
              f"{d_sq:>+7.4f} | {d_dyn:>+7.4f} | {d_uk:>+7.4f}")

optimal_cap_table("gr_fan",    "Fan")
optimal_cap_table("gr_popwt",  "PopWt")
optimal_cap_table("gr_system", "System")


# ── Console: full summary table at a glance ───────────────────────────────────
print("\n── Fan GR scores by cap × demand (highlight: best bounded cap per demand) ──")
header_caps = ["SQ", "Dyn", "UK"] + [f"{round(c*100)}%" for c in CAP_LEVELS]
print(f"{'Demand':>7} | " + " | ".join(f"{h:>6}" for h in header_caps))
print("-" * (10 + 10 * len(header_caps)))
for mul in DEMAND_LEVELS:
    sq_val  = next(r["gr_fan"] for r in summary_rows if r["series"] == "Status Quo"      and r["demand"] == mul)
    dyn_val = next(r["gr_fan"] for r in summary_rows if r["series"] == "Dynamic Pricing" and r["demand"] == mul)
    uk_val  = next(r["gr_fan"] for r in summary_rows if r["series"] == "UK Face Value"   and r["demand"] == mul)
    bounded_vals = [
        next(r["gr_fan"] for r in summary_rows if r["series"] == f"Bounded {round(c*100)}%" and r["demand"] == mul)
        for c in CAP_LEVELS
    ]
    best_bounded = max(bounded_vals)
    cells = [f"{sq_val:.4f}", f"{dyn_val:.4f}", f"{uk_val:.4f}"] + [
        f"[{v:.4f}]" if v == best_bounded else f" {v:.4f} " for v in bounded_vals
    ]
    print(f"  {mul:>5} | " + " | ".join(cells))


# ── Console: dark market leakage summary ──────────────────────────────────────
print("\n── Dark market leakage (capped regimes only) ──")
print(f"{'Series':<22} | {'Demand':>7} | {'DarkSold':>8} | {'Unmatched':>9}")
print("-" * 55)
for series in SERIES:
    if series["rule"].cap is None:
        continue
    for mul in DEMAND_LEVELS:
        r = next(x for x in summary_rows if x["series"] == series["label"] and x["demand"] == mul)
        if r["dark_sold"] > 0 or r["dark_unmatched"] > 0:
            print(f"  {series['label']:<20} | {mul:>7} | {r['dark_sold']:>8} | {r['dark_unmatched']:>9}")
