#!/usr/bin/env python3
"""Chart 9 — UK 2026 policy comparison (TF4, 2026-07-05).

The UK's confirmed policy (face-value cap + platform fee cap, Nov 2025
response / May 2026 draft Bill) vs the constructive alternative: the same
fee cap with a ~20% ceiling. Reads cap-sweep-summary.csv; house dark style.
"""

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sweep_config import DEMAND_LEVELS

rows = list(csv.DictReader(open("cap-sweep-summary.csv")))
DEMANDS = [float(m) for m in DEMAND_LEVELS]

SERIES = [
    ("Status Quo",                    "#E05C5C", "--"),
    ("Bounded 0%",                    "#5BA4CF", "--"),
    ("UK 2026 (0% + fee cap)",        "#9B59B6", "-"),
    ("Bounded 10% + fee cap",         "#3D9B70", "-"),
    ("Bounded 20% + fee cap",         "#F4D03F", "-"),
]

plt.rcParams.update({
    "figure.facecolor": "#0F1923", "axes.facecolor": "#0F1923",
    "axes.edgecolor": "#3A4A5A", "axes.labelcolor": "#C8D8E8",
    "text.color": "#C8D8E8", "xtick.color": "#8AA0B0",
    "ytick.color": "#8AA0B0", "grid.color": "#1E2E3E",
})

fig, ax = plt.subplots(figsize=(10, 5.6))
for label, color, ls in SERIES:
    ys = [next((float(r["gr_popwt"]) for r in rows
                if r["series"] == label and float(r["demand"]) == d), None)
          for d in DEMANDS]
    lw = 3.0 if "20% + fee cap" in label else 2.0
    ax.plot(DEMANDS, ys, ls, color=color, linewidth=lw, marker="o",
            markersize=4, label=label)

ax.set_xlabel("Demand multiplier (× venue capacity)")
ax.set_ylabel("Population-weighted GR score")
ax.set_title("The UK's ban vs the constructive alternative\n"
             "(fee cap kept in both — only the resale ceiling differs)",
             color="#E8F0F8", fontsize=13)
ax.grid(alpha=0.4)
leg = ax.legend(facecolor="#1A2A3A", edgecolor="#3A4A5A", labelcolor="#C8D8E8",
                fontsize=9, loc="upper right")
ax.annotate("UK 2026 policy:\nfee cap helps, ceiling still binds",
            xy=(8, 0.304), xytext=(5.6, 0.20), color="#9B59B6", fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#9B59B6"))
ax.annotate("Same fee cap, 20% ceiling:\n2–3× the welfare gain",
            xy=(8, 0.408), xytext=(4.2, 0.50), color="#F4D03F", fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#F4D03F"))
fig.tight_layout()
fig.savefig("chart9_uk2026.png", dpi=150)
print("Wrote chart9_uk2026.png")
