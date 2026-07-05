"""Generate charts for the GRE slide deck."""

import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import defaultdict

# ── Load data ─────────────────────────────────────────────────────────────────
rows = list(csv.DictReader(open("cap-sweep-summary.csv")))

def get(series, demand, field):
    matches = [r for r in rows if r["series"] == series and float(r["demand"]) == demand]
    if not matches:
        return None
    return float(matches[0][field])

# Grid + palette imported from the shared config (2026-07-04) — previously
# duplicated here, so a change to the swept caps silently desynced the charts.
from sweep_config import DEMAND_LEVELS, CAP_LEVELS, BOUNDED_LABELS, PALETTE

DEMANDS  = [float(m) for m in DEMAND_LEVELS]
BOUNDED  = BOUNDED_LABELS
CAP_VALS = [round(c * 100) for c in CAP_LEVELS]

STYLE = dict(figure_facecolor="#0F1923", axes_facecolor="#0F1923")
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


# ── Chart 1: Ruleset comparison — PopWt GR across demand levels ───────────────
fig, ax = plt.subplots(figsize=(10, 5.5))

RULESETS = ["Status Quo", "Dynamic Pricing", "UK Face Value", "Bounded 20%", "Bounded 25%"]
COLORS   = ["#E05C5C",    "#E08B3A",         "#9B59B6",       "#2E7D52",      "#1A5C3A"]
STYLES   = ["--",         "--",               "-.",             "-",            "-"]
WIDTHS   = [1.8,           1.8,               1.8,              2.4,            2.4]

for series, color, ls, lw in zip(RULESETS, COLORS, STYLES, WIDTHS):
    vals = [get(series, d, "gr_popwt") for d in DEMANDS]
    ax.plot(DEMANDS, vals, color=color, linestyle=ls, linewidth=lw,
            label=series, marker="o", markersize=4)

ax.axvspan(1.5, 10.5, alpha=0.06, color="#2E7D52", label="_nolegend_")
ax.annotate("Bounded market\ndominates at demand ≥ 1.5×",
            xy=(1.5, 0.54), xytext=(2.2, 0.57),
            color="#7ECBA1", fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#7ECBA1", lw=1.2))

ax.set_xlabel("Demand Multiplier (1× = sold out at face value)", fontsize=11)
ax.set_ylabel("Population-Weighted Golden Rule Score", fontsize=11)
ax.set_title("Bounded Market Outperforms All Alternatives at High Demand",
             fontsize=13, color="#E8F0F8", pad=14)
ax.legend(loc="upper right", framealpha=0.15, fontsize=9)
ax.grid(True)
ax.set_xlim(0.8, 10.2)
ax.set_ylim(0.18, 0.72)
fig.tight_layout()
fig.savefig("chart1_ruleset_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart1_ruleset_comparison.png")


# ── Chart 2: Cap sweep heatmap — PopWt GR by cap × demand ─────────────────────
fig, ax = plt.subplots(figsize=(10, 5))

matrix = []
for cap_s in BOUNDED:
    row = [get(cap_s, d, "gr_popwt") or 0 for d in DEMANDS]
    matrix.append(row)

matrix = np.array(matrix)

im = ax.imshow(matrix, aspect="auto", cmap="YlGn",
               vmin=matrix.min(), vmax=matrix.max(),
               origin="upper")

ax.set_xticks(range(len(DEMANDS)))
ax.set_xticklabels([str(d) for d in DEMANDS], fontsize=9)
ax.set_yticks(range(len(CAP_VALS)))
ax.set_yticklabels([f"{c}%" for c in CAP_VALS], fontsize=9)
ax.set_xlabel("Demand Multiplier", fontsize=11)
ax.set_ylabel("Resale Cap", fontsize=11)
ax.set_title("Golden Rule Score by Cap Level × Demand\n(Darker = Higher Fairness)",
             fontsize=13, color="#E8F0F8", pad=10)

# Annotate optima
opt_caps = {1.0: 50, 1.5: 30, 2.0: 20, 3.0: 10, 4.0: 5, 5.0: 10,
            6.0: 15, 7.0: 15, 8.0: 20, 10.0: 20}
for d_idx, d in enumerate(DEMANDS):
    opt = opt_caps.get(d)
    if opt in CAP_VALS:
        c_idx = CAP_VALS.index(opt)
        ax.plot(d_idx, c_idx, marker="*", color="#F4D03F",
                markersize=14, zorder=5)

star_patch = mpatches.Patch(color="#F4D03F", label="Optimal cap at this demand")
ax.legend(handles=[star_patch], loc="upper right", framealpha=0.2, fontsize=9)

cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cbar.ax.yaxis.set_tick_params(color="#8AA0B0")
plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#8AA0B0", fontsize=8)

# Highlight 20-25% band
ax.axhspan(4.5, 5.5, color="#F4D03F", alpha=0.12, zorder=0)
ax.annotate("20–25% band\n(robust range)", xy=(-0.5, 5.0),
            xytext=(-0.45, 6.2), color="#F4D03F", fontsize=8,
            ha="left")

fig.tight_layout()
fig.savefig("chart2_cap_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart2_cap_heatmap.png")


# ── Chart 3: Dark market leakage — driven by demand, flat across the cap ──────
# HONEST REVISION (2026-06-03): the prior version claimed "leakage collapses in
# the 20–25% band." That was false — the corrected model shows dark leakage is
# driven by DEMAND, essentially flat across the 0–30% policy cap range, and small
# in absolute terms (≤ ~5% of a 500-seat house even at 8× demand). The real
# argument is the inverse of the old slide: the resale cap does NOT create the
# dark market, so you cannot "cap your way out of" leakage — but a moderate cap
# also does not WORSEN it. Leakage is a demand/enforcement problem, not a cap
# problem, which is exactly why the policy case rests on the PopWt/System welfare
# gains, not on a (non-existent) leakage cliff.
fig, ax = plt.subplots(figsize=(9, 5))

demand_levels = [3.0, 5.0, 8.0]
d_colors = ["#5BA4CF", "#3D9B70", "#E08B3A"]
d_labels = ["Demand 3×", "Demand 5×", "Demand 8×"]

for d, color, label in zip(demand_levels, d_colors, d_labels):
    dark = []
    for cap_s in BOUNDED:
        ds = get(cap_s, d, "dark_sold") or 0
        du = get(cap_s, d, "dark_unmatched") or 0
        dark.append((ds + du) / 500.0 * 100.0)  # as % of venue capacity
    ax.plot(CAP_VALS, dark, color=color, marker="o", linewidth=2.2,
            markersize=5, label=label)

ax.set_xlabel("Resale Cap (%)", fontsize=11)
ax.set_ylabel("Dark Market Tickets (% of venue capacity)", fontsize=11)
ax.set_title("Dark-Market Leakage Is Driven by Demand, Not the Cap —\n"
             "Flat Across the 0–30% Policy Range, and Small in Absolute Terms",
             fontsize=12.5, color="#E8F0F8", pad=12)
ax.legend(loc="upper left", framealpha=0.15, fontsize=9, title="Demand level")
ax.grid(True)
ax.set_xlim(-1, 52)
ax.set_ylim(0, None)

# Shade the policy-relevant band (no magic threshold — just where the debate lives)
ax.axvspan(10, 30, alpha=0.06, color="#3D9B70")
fig.canvas.draw()
ymax = ax.get_ylim()[1]
ax.annotate("Policy band (10–30%):\nleakage essentially flat —\nthe cap is not the lever",
            xy=(20, ymax * 0.50), xytext=(20, ymax * 0.50),
            color="#7ECBA1", fontsize=8.5, ha="center")
ax.annotate("Higher demand, not tighter caps,\nis what grows the dark market",
            xy=(40, [ (get('Bounded 40%', 8.0,'dark_sold') or 0)+(get('Bounded 40%',8.0,'dark_unmatched') or 0) ][0]/500*100),
            xytext=(26, ymax * 0.86), color="#E08B3A", fontsize=8.5, ha="left",
            arrowprops=dict(arrowstyle="->", color="#E08B3A", lw=1))

fig.tight_layout()
fig.savefig("chart3_dark_market.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart3_dark_market.png")


# ── Chart 4: Three-lens convergence at demand 5× ──────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))

lenses = [("gr_popwt", "#3D9B70", "Population-Weighted"),
          ("gr_system", "#5BA4CF", "System (Equal Weight)"),
          ("gr_fan",    "#9B59B6", "Fan-Only")]

for field, color, label in lenses:
    vals = [get(cap_s, 5.0, field) for cap_s in BOUNDED]
    ax.plot(CAP_VALS, vals, color=color, marker="o", linewidth=2.2,
            markersize=5, label=label)

ax.axvspan(18, 27, alpha=0.12, color="#F4D03F")
ax.annotate("20–25%: PopWt &\nSystem converge",
            xy=(22.5, 0.47), xytext=(28, 0.45),
            color="#F4D03F", fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#F4D03F", lw=1.2))

ax.set_xlabel("Resale Cap (%)", fontsize=11)
ax.set_ylabel("Golden Rule Score", fontsize=11)
ax.set_title("Three-Lens Convergence at Demand 5×\n(Fan Lens Pending Scalper-Exit Modeling)",
             fontsize=13, color="#E8F0F8", pad=12)
ax.legend(loc="upper right", framealpha=0.15, fontsize=9)
ax.grid(True)
ax.set_xlim(-1, 52)
fig.tight_layout()
fig.savefig("chart4_lens_convergence.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart4_lens_convergence.png")


# ── Chart 5: Sensitivity — top parameters ─────────────────────────────────────
sens_rows = list(csv.DictReader(open("sensitivity_rankings.csv")))

# Get top 10 by sensitivity_score across all lenses, unique params
seen = set()
top = []
for r in sorted(sens_rows, key=lambda x: -float(x["sensitivity_score"])):
    if r["param"] not in seen:
        seen.add(r["param"])
        top.append(r)
    if len(top) == 10:
        break

params = [r["param"] for r in top]
scores = [float(r["sensitivity_score"]) for r in top]
groups = [r["group"] for r in top]

group_colors = {
    "gr_w":       "#F4D03F",
    "structural": "#5BA4CF",
    "dark":       "#E05C5C",
    "utility_w":  "#3D9B70",
    "behavioral": "#E08B3A",
}
bar_colors = [group_colors.get(g, "#888") for g in groups]

fig, ax = plt.subplots(figsize=(10, 5.5))
bars = ax.barh(params[::-1], scores[::-1], color=bar_colors[::-1],
               edgecolor="#0F1923", linewidth=0.5)

# Add a "dark market zone" annotation
dark_params = [p for p, g in zip(params, groups) if g == "dark"]
dark_indices = [params[::-1].index(p) for p in dark_params if p in params[::-1]]

ax.axvline(0.3, color="#888", linestyle=":", alpha=0.5, linewidth=1)
ax.annotate("Dark market parameters\nhave LOW sensitivity\n— policy robust to\nunsourced estimates",
            xy=(0.05, 1.5), xytext=(0.32, 3),
            color="#E05C5C", fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color="#E05C5C", lw=1))

legend_patches = [mpatches.Patch(color=v, label=k.replace("_", " ").title())
                  for k, v in group_colors.items()]
ax.legend(handles=legend_patches, loc="lower right", framealpha=0.15, fontsize=9)
ax.set_xlabel("Sensitivity Score", fontsize=11)
ax.set_title("Parameter Sensitivity — Policy Robust Across All Key Knobs\n"
             "Dark Market Parameters Do Not Move the Optimal Cap",
             fontsize=13, color="#E8F0F8", pad=12)
ax.grid(True, axis="x")
fig.tight_layout()
fig.savefig("chart5_sensitivity.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved chart5_sensitivity.png")

print("\nAll charts generated.")
