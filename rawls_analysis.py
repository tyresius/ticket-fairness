"""
Alternative Welfare Criteria Analysis
======================================

Supplements GRE scores with three established welfare frameworks:

  1. Rawlsian Maximin (Veil of Ignorance)
     ----------------------------------------
     Behind the veil you do not know which agent type you will be.
     Rational risk-averse actors choose the ruleset that maximises
     the MINIMUM utility across all positions (maximin).

     Key design choice: are scalpers inside or outside the social contract?
       - rawls_all:  all four types — pure veil (you might be a scalper)
       - rawls_fan:  fan types only — scalpers are exogenous market actors,
                     not parties deliberating over the rules of the venue economy

     We report both and flag where they diverge.

  2. Harsanyi Utilitarianism (Expected Utility Behind the Veil)
     -------------------------------------------------------------
     Harsanyi (1953, 1975) argued that behind the veil, a rational agent
     maximises EXPECTED utility, not the minimum. This produces a weighted-
     average welfare criterion — the veil of ignorance collapses to classical
     utilitarianism under the equal-probability assumption.

       - harsanyi_equal: arithmetic mean across all types (equal probability)
       - harsanyi_pop:   population-weighted mean (probability ∝ group size)

     Note: harsanyi_pop is closely related to the existing GRE PopWt lens but
     uses raw utility averages rather than the GRE scoring formula.

  3. Pareto Dominance
     -------------------
     Ruleset A Pareto-dominates ruleset B if every agent type is at least
     as well off under A, and at least one type is strictly better off.
     A Pareto-dominated ruleset should not be chosen regardless of
     distributional preferences — this claim requires no welfare weights.

Reads from:
  cap-sweep-agents.csv   — per-agent-type utility/ex_ante per (series, demand)
  cap-sweep-summary.csv  — GRE lens scores per (series, demand)

Outputs:
  rawls-summary.csv       — all welfare scores per (series, demand)
  console tables and chart6_welfare_criteria.png
"""

import csv
import math
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Load data ─────────────────────────────────────────────────────────────────
agent_rows   = list(csv.DictReader(open("cap-sweep-agents.csv")))
summary_rows = list(csv.DictReader(open("cap-sweep-summary.csv")))

FAN_TYPES = ["mega_fan", "committed_casual", "average_buyer"]
ALL_TYPES = ["mega_fan", "committed_casual", "average_buyer", "scalper"]

# Grid imported from the shared config (2026-07-04) — previously duplicated
# here, so a change to the swept caps silently desynced this analysis.
from sweep_config import SERIES_ORDER, DEMAND_LEVELS

DEMANDS = [float(m) for m in DEMAND_LEVELS]

# ── Index agent data: (series, demand, agent_type) → row ─────────────────────
agent_idx = {}
for r in agent_rows:
    key = (r["series"], float(r["demand"]), r["agent"])
    agent_idx[key] = r

def util(series, demand, agent):
    row = agent_idx.get((series, float(demand), agent))
    return float(row["utility"]) if row else None

def ex_ante(series, demand, agent):
    row = agent_idx.get((series, float(demand), agent))
    return float(row["ex_ante"]) if row else None

def pop_total(series, demand, agent):
    row = agent_idx.get((series, float(demand), agent))
    return int(row["total"]) if row else 1

# ── Index GRE summary: (series, demand) → row ────────────────────────────────
summary_idx = {}
for r in summary_rows:
    summary_idx[(r["series"], float(r["demand"]))] = r

def gre(series, demand, field):
    row = summary_idx.get((series, float(demand)))
    return float(row[field]) if row else None


# ── Compute alternative welfare scores ───────────────────────────────────────
welfare_rows = []

for series in SERIES_ORDER:
    for demand in DEMANDS:
        utils_fan = [util(series, demand, t) for t in FAN_TYPES]
        utils_all = [util(series, demand, t) for t in ALL_TYPES]
        ea_fan    = [ex_ante(series, demand, t) for t in FAN_TYPES]

        if any(u is None for u in utils_all):
            continue

        # ── 1. Rawlsian maximin ───────────────────────────────────────────────
        rawls_fan     = min(utils_fan)        # min utility across fan types
        rawls_all     = min(utils_all)        # min utility across all types
        rawls_ea_fan  = min(ea_fan)           # min ex-ante utility, fan types

        # ── 2. Harsanyi expected utility ─────────────────────────────────────
        # Equal weight: each agent type has probability 1/N
        harsanyi_equal_fan = sum(utils_fan) / len(utils_fan)
        harsanyi_equal_all = sum(utils_all) / len(utils_all)

        # Population weight: probability ∝ group size in this simulation
        pops_all   = [pop_total(series, demand, t) for t in ALL_TYPES]
        total_pop  = sum(pops_all)
        harsanyi_pop_all = sum(u * p for u, p in zip(utils_all, pops_all)) / total_pop

        pops_fan   = [pop_total(series, demand, t) for t in FAN_TYPES]
        total_fan  = sum(pops_fan)
        harsanyi_pop_fan = sum(u * p for u, p in zip(utils_fan, pops_fan)) / total_fan

        # ── 3. Retrieve GRE lenses ────────────────────────────────────────────
        gr_fan    = gre(series, demand, "gr_fan")
        gr_popwt  = gre(series, demand, "gr_popwt")
        gr_system = gre(series, demand, "gr_system")

        welfare_rows.append(dict(
            series             = series,
            demand             = demand,
            # Rawlsian
            rawls_fan          = round(rawls_fan,          4),
            rawls_all          = round(rawls_all,          4),
            rawls_exante_fan   = round(rawls_ea_fan,       4),
            # Harsanyi equal-weight
            harsanyi_eq_fan    = round(harsanyi_equal_fan, 4),
            harsanyi_eq_all    = round(harsanyi_equal_all, 4),
            # Harsanyi population-weight
            harsanyi_pop_all   = round(harsanyi_pop_all,   4),
            harsanyi_pop_fan   = round(harsanyi_pop_fan,   4),
            # GRE lenses (for comparison)
            gr_fan             = round(gr_fan,    4) if gr_fan    is not None else None,
            gr_popwt           = round(gr_popwt,  4) if gr_popwt  is not None else None,
            gr_system          = round(gr_system, 4) if gr_system is not None else None,
            # Per-agent utilities for Pareto checks
            u_mega_fan         = round(utils_all[0], 4),
            u_committed_casual = round(utils_all[1], 4),
            u_average_buyer    = round(utils_all[2], 4),
            u_scalper          = round(utils_all[3], 4),
        ))

# ── Write CSV ─────────────────────────────────────────────────────────────────
with open("rawls-summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(welfare_rows[0].keys()))
    w.writeheader()
    w.writerows(welfare_rows)
print("Wrote rawls-summary.csv\n")


# ── Helper: get a welfare score for (series, demand, field) ──────────────────
def w_get(series, demand, field):
    return next((r[field] for r in welfare_rows
                 if r["series"] == series and r["demand"] == demand), None)


# ── Console: Rawlsian optimal ruleset by demand ───────────────────────────────
BOUNDED = [s for s in SERIES_ORDER if s.startswith("Bounded")]

print("── Rawlsian Maximin: optimal bounded cap vs comparators (fan types only) ──")
print(f"{'Demand':>7} | {'Opt Cap':>12} | {'RawlsFan':>9} | {'vs SQ':>7} | "
      f"{'vs Dyn':>7} | {'vs UK':>7} | {'GRE opt?':>9}")
print("-" * 72)
for demand in DEMANDS:
    sq_r  = w_get("Status Quo",      demand, "rawls_fan")
    dyn_r = w_get("Dynamic Pricing", demand, "rawls_fan")
    uk_r  = w_get("UK Face Value",   demand, "rawls_fan")
    bounded_scores = [(s, w_get(s, demand, "rawls_fan")) for s in BOUNDED
                      if w_get(s, demand, "rawls_fan") is not None]
    best_s, best_r = max(bounded_scores, key=lambda x: x[1])

    # Check if Rawlsian opt matches GRE (PopWt) opt
    gr_scores = [(s, w_get(s, demand, "gr_popwt")) for s in BOUNDED
                 if w_get(s, demand, "gr_popwt") is not None]
    gre_best_s = max(gr_scores, key=lambda x: x[1])[0]
    agrees = "✓ agree" if best_s == gre_best_s else f"≠ {gre_best_s}"

    print(f"  {demand:>5} | {best_s:>12} | {best_r:>9.4f} | {best_r-sq_r:>+7.4f} | "
          f"{best_r-dyn_r:>+7.4f} | {best_r-uk_r:>+7.4f} | {agrees:>9}")


# ── Console: Harsanyi vs GRE PopWt comparison ────────────────────────────────
KEY_SERIES = ["Status Quo", "Dynamic Pricing", "Bounded 10%",
              "Bounded 20%", "Bounded 25%", "Bounded 30%"]

print("\n── Harsanyi (pop-weighted) vs GRE PopWt at demand 5× ──")
print("(Higher = better; both use population-weighted average but different scoring formulas)")
print(f"{'Series':<20} | {'Harsanyi PopWt':>14} | {'GRE PopWt':>10} | {'Δ':>8} | {'Rank Hars':>10} | {'Rank GRE':>9}")
print("-" * 80)

h_scores  = [(s, w_get(s, 5.0, "harsanyi_pop_all")) for s in KEY_SERIES]
gr_scores = [(s, w_get(s, 5.0, "gr_popwt"))         for s in KEY_SERIES]
h_ranked  = sorted(h_scores,  key=lambda x: -x[1])
gr_ranked = sorted(gr_scores, key=lambda x: -x[1])
h_rank    = {s: i+1 for i, (s, _) in enumerate(h_ranked)}
gr_rank   = {s: i+1 for i, (s, _) in enumerate(gr_ranked)}

for s in KEY_SERIES:
    h  = w_get(s, 5.0, "harsanyi_pop_all")
    gr = w_get(s, 5.0, "gr_popwt")
    print(f"  {s:<18} | {h:>14.4f} | {gr:>10.4f} | {h-gr:>+8.4f} | "
          f"{'#'+str(h_rank[s]):>10} | {'#'+str(gr_rank[s]):>9}")


# ── Console: Pareto dominance at each demand level ───────────────────────────
AGENT_UTIL_FIELDS = ["u_mega_fan", "u_committed_casual", "u_average_buyer", "u_scalper"]
FAN_UTIL_FIELDS   = ["u_mega_fan", "u_committed_casual", "u_average_buyer"]

def pareto_dominates(row_a, row_b, fields):
    """True if A Pareto-dominates B: all fields ≥, at least one >."""
    vals_a = [row_a[f] for f in fields]
    vals_b = [row_b[f] for f in fields]
    return all(a >= b for a, b in zip(vals_a, vals_b)) and any(a > b for a, b in zip(vals_a, vals_b))

print("\n── Pareto Dominance (fan types only, across all demand levels) ──")
print("Pair A → B means A Pareto-dominates B at ALL demand levels surveyed\n")

# For each ordered pair of series, check dominance at all demand levels
dominated_by = defaultdict(set)
for sa in SERIES_ORDER:
    for sb in SERIES_ORDER:
        if sa == sb:
            continue
        rows_a = [r for r in welfare_rows if r["series"] == sa]
        rows_b = [r for r in welfare_rows if r["series"] == sb]
        if not rows_a or not rows_b:
            continue
        # dominates at ALL demand levels
        all_dom = all(
            pareto_dominates(ra, rb, FAN_UTIL_FIELDS)
            for ra, rb in zip(
                sorted(rows_a, key=lambda r: r["demand"]),
                sorted(rows_b, key=lambda r: r["demand"]),
            )
        )
        if all_dom:
            dominated_by[sb].add(sa)

if dominated_by:
    for loser, winners in sorted(dominated_by.items()):
        for w in sorted(winners):
            print(f"  {w}  →  Pareto-dominates  {loser}")
else:
    # Partial dominance: count demand levels
    print("  No strict universal Pareto dominance across ALL demand levels.")
    print("  Checking partial dominance (majority of demand levels):\n")
    for sa in SERIES_ORDER:
        for sb in SERIES_ORDER:
            if sa == sb:
                continue
            rows_a = sorted([r for r in welfare_rows if r["series"] == sa], key=lambda r: r["demand"])
            rows_b = sorted([r for r in welfare_rows if r["series"] == sb], key=lambda r: r["demand"])
            if not rows_a or not rows_b:
                continue
            count = sum(
                pareto_dominates(ra, rb, FAN_UTIL_FIELDS)
                for ra, rb in zip(rows_a, rows_b)
            )
            if count >= 7:  # majority (7+/10)
                print(f"  {sa:<22} →  dominates  {sb:<22}  ({count}/{len(DEMANDS)} demand levels)")


# ── Console: GRE vs Rawls convergence summary ────────────────────────────────
print("\n── Convergence: does Rawlsian agree with GRE PopWt on optimal bounded cap? ──")
agree_count = 0
for demand in DEMANDS:
    bounded_gre  = [(s, w_get(s, demand, "gr_popwt"))  for s in BOUNDED if w_get(s, demand, "gr_popwt")]
    bounded_rawl = [(s, w_get(s, demand, "rawls_fan")) for s in BOUNDED if w_get(s, demand, "rawls_fan")]
    gre_opt  = max(bounded_gre,  key=lambda x: x[1])[0]
    rawl_opt = max(bounded_rawl, key=lambda x: x[1])[0]
    agrees   = gre_opt == rawl_opt
    if agrees:
        agree_count += 1
    print(f"  Demand {demand:>4}× | GRE best: {gre_opt:<12} | Rawls best: {rawl_opt:<12} "
          f"| {'✓ agree' if agrees else '≠ diverge'}")
print(f"\n  Agreement rate: {agree_count}/{len(DEMANDS)} demand levels")


# ── Chart 6: GRE vs Rawlsian vs Harsanyi for key rulesets ───────────────────
plt.rcParams.update({
    "figure.facecolor": "#0F1923",
    "axes.facecolor":   "#0F1923",
    "axes.edgecolor":   "#3A4A5A",
    "axes.labelcolor":  "#C8D8E8",
    "text.color":       "#C8D8E8",
    "xtick.color":      "#8AA0B0",
    "ytick.color":      "#8AA0B0",
    "grid.color":       "#1E2E3E",
    "grid.linestyle":   "--",
    "grid.alpha":       0.6,
    "font.family":      "sans-serif",
    "font.size":        11,
})

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
fig.suptitle("GRE vs Rawlsian vs Harsanyi: Do Alternative Frameworks Agree?",
             fontsize=13, color="#E8F0F8", y=1.01)

PLOT_SERIES = [
    ("Status Quo",    "#E05C5C", "--", 1.8),
    ("Dynamic Pricing","#E08B3A","--", 1.8),
    ("Bounded 20%",   "#2E7D52", "-",  2.4),
    ("Bounded 25%",   "#1A5C3A", "-",  2.4),
]

# Left: Rawlsian (fan maximin) vs GRE Fan lens
ax = axes[0]
for s, color, ls, lw in PLOT_SERIES:
    rawls_vals = [w_get(s, d, "rawls_fan") for d in DEMANDS]
    gre_vals   = [w_get(s, d, "gr_fan")    for d in DEMANDS]
    ax.plot(DEMANDS, rawls_vals, color=color, linestyle=ls,  linewidth=lw,
            marker="o", markersize=4, label=f"{s} (Rawls)")
    ax.plot(DEMANDS, gre_vals,   color=color, linestyle=":", linewidth=lw * 0.7,
            marker="s", markersize=3, label=f"{s} (GRE)")

ax.set_xlabel("Demand Multiplier", fontsize=10)
ax.set_ylabel("Score", fontsize=10)
ax.set_title("Rawlsian Maximin (fan floor)\nvs GRE Fan Lens", fontsize=11, color="#E8F0F8")
ax.grid(True)
ax.set_xlim(0.8, 10.2)

# Custom legend: just series colors, not every line
legend_patches = [mpatches.Patch(color=c, label=s) for s, c, _, _ in PLOT_SERIES]
solid_line = plt.Line2D([0], [0], color="#8AA0B0", linestyle="-",  lw=1.5, label="Rawlsian")
dot_line   = plt.Line2D([0], [0], color="#8AA0B0", linestyle=":", lw=1.5, label="GRE")
ax.legend(handles=legend_patches + [solid_line, dot_line],
          loc="upper right", framealpha=0.15, fontsize=8)

# Right: Harsanyi (pop-weighted) vs GRE PopWt lens
ax = axes[1]
for s, color, ls, lw in PLOT_SERIES:
    hars_vals = [w_get(s, d, "harsanyi_pop_all") for d in DEMANDS]
    gre_vals  = [w_get(s, d, "gr_popwt")         for d in DEMANDS]
    ax.plot(DEMANDS, hars_vals, color=color, linestyle=ls,  linewidth=lw,
            marker="o", markersize=4, label=f"{s} (Harsanyi)")
    ax.plot(DEMANDS, gre_vals,  color=color, linestyle=":", linewidth=lw * 0.7,
            marker="s", markersize=3, label=f"{s} (GRE)")

ax.set_xlabel("Demand Multiplier", fontsize=10)
ax.set_title("Harsanyi Expected Utility (pop-weighted)\nvs GRE PopWt Lens", fontsize=11, color="#E8F0F8")
ax.grid(True)
ax.set_xlim(0.8, 10.2)
ax.legend(handles=legend_patches + [solid_line, dot_line],
          loc="upper right", framealpha=0.15, fontsize=8)

fig.tight_layout()
fig.savefig("chart6_welfare_criteria.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nSaved chart6_welfare_criteria.png")
print("\nAll done.")
