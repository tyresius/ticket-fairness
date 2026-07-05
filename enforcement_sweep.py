"""
Enforcement Sensitivity Sweep
==============================

Compares bounded market performance across three enforcement regimes:

  1. Full enforcement  — identity registry + non-transferable barcodes
                         (current baseline: SCALPER_DARK_COST=0.45,
                          DARK_FRAUD_PENALTY=0.25)

  2. Partial enforcement — name-on-ticket law, spot checks, but no technical
                           transfer controls or systematic barcode invalidation
                           (SCALPER_DARK_COST=0.20, DARK_FRAUD_PENALTY=0.15)

  3. No enforcement    — cap on paper only; transfers unimpeded; dark market
                         buyer risk ≈ uncapped secondary market
                         (SCALPER_DARK_COST=0.05, DARK_FRAUD_PENALTY=0.07)

For each enforcement level, runs the core policy set:
  Status Quo, Dynamic Pricing, UK Face Value, Bounded 10%, 20%, 25%, 30%

This answers the question: does the bounded market advantage require the full
enforcement package, or does it survive under weaker real-world compliance?

Key mechanism:
  - Without SCALPER_DARK_COST friction, dark-market expected net revenue rises
    → scalpers stay in the market longer (exit sigmoid stays high)
    → more tickets are routed to the dark channel
    → leakage rises, fan access falls, dark fraud costs rise
  - DARK_FRAUD_PENALTY governs the buyer-side cost of a dark-market purchase;
    without non-transferable barcodes, a dark ticket is just a normal ticket
    so buyer risk reverts to uncapped-market levels (0.07, matching
    BASELINE_SECONDARY_FRAUD_PENALTY)

Outputs:
  enforcement-sweep-summary.csv  — GR scores per (enforcement, series, demand)
  enforcement-sweep-dark.csv     — dark market metrics per (enforcement, series, demand)
  console tables comparing PopWt GR across enforcement scenarios
"""

import csv
import random
import sys

from gre_sim import simulate, Rule, DEFS, DARK_LEAKAGE_BASE, DARK_LEAKAGE_GAMMA

random.seed(42)

# ── Enforcement scenarios ─────────────────────────────────────────────────────
ENFORCEMENT_SCENARIOS = [
    dict(
        id    = "full",
        label = "Full Enforcement",
        note  = "ID registry + non-transferable barcodes",
        kwargs = dict(scalper_dark_cost=0.45, dark_fraud_penalty=0.25),
    ),
    dict(
        id    = "partial",
        label = "Partial Enforcement",
        note  = "Name-on-ticket law; no technical transfer controls",
        kwargs = dict(scalper_dark_cost=0.20, dark_fraud_penalty=0.15),
    ),
    dict(
        id    = "none",
        label = "No Enforcement",
        note  = "Cap on paper only; dark market = uncapped secondary",
        kwargs = dict(scalper_dark_cost=0.05, dark_fraud_penalty=0.07),
    ),
]

# ── Policy series to compare ──────────────────────────────────────────────────
POLICY_SERIES = [
    dict(id="status_quo", label="Status Quo",
         rule=Rule("Status Quo",      cap=None, plimit=8, dyn_mul=None)),
    dict(id="dynamic",    label="Dynamic Pricing",
         rule=Rule("Dynamic Pricing", cap=None, plimit=6, dyn_mul=2.2)),
    dict(id="uk_face",    label="UK Face Value",
         rule=Rule("UK Face Value",   cap=0.0,  plimit=2, dyn_mul=None)),
    dict(id="bounded_10", label="Bounded 10%",
         rule=Rule("Bounded 10%",     cap=0.10, plimit=4, dyn_mul=None)),
    dict(id="bounded_20", label="Bounded 20%",
         rule=Rule("Bounded 20%",     cap=0.20, plimit=4, dyn_mul=None)),
    dict(id="bounded_25", label="Bounded 25%",
         rule=Rule("Bounded 25%",     cap=0.25, plimit=4, dyn_mul=None)),
    dict(id="bounded_30", label="Bounded 30%",
         rule=Rule("Bounded 30%",     cap=0.30, plimit=4, dyn_mul=None)),
]

DEMAND_LEVELS  = [1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10]
RUNS_PER_POINT = 100

# ── Helpers ───────────────────────────────────────────────────────────────────
def avg_f(runs, fn):
    return round(sum(fn(r) for r in runs) / len(runs), 4)

def avg_i(runs, fn):
    return round(sum(fn(r) for r in runs) / len(runs))


total_sims = len(ENFORCEMENT_SCENARIOS) * len(POLICY_SERIES) * len(DEMAND_LEVELS) * RUNS_PER_POINT
print(f"Enforcement sweep: {len(ENFORCEMENT_SCENARIOS)} scenarios × {len(POLICY_SERIES)} policies × "
      f"{len(DEMAND_LEVELS)} demand levels × {RUNS_PER_POINT} runs = {total_sims:,} simulations\n")

summary_rows = []
dark_rows    = []

for enf in ENFORCEMENT_SCENARIOS:
    print(f"  [{enf['label']}]  ({enf['note']})")
    for series in POLICY_SERIES:
        sys.stdout.write(f"    {series['label']:<20}")
        sys.stdout.flush()
        for mul in DEMAND_LEVELS:
            runs = [
                simulate(series["rule"], mul, **enf["kwargs"])
                for _ in range(RUNS_PER_POINT)
            ]

            summary_rows.append(dict(
                enforcement   = enf["label"],
                enforcement_id= enf["id"],
                series        = series["label"],
                series_id     = series["id"],
                demand        = mul,
                gr_system     = avg_f(runs, lambda r: r["system"]),
                gr_fan        = avg_f(runs, lambda r: r["fan_only"]),
                gr_popwt      = avg_f(runs, lambda r: r["pop_wt"]),
                gr_ex_ante_fan= avg_f(runs, lambda r: r["ex_ante_fan"]),
                gr_ex_ante_pw = avg_f(runs, lambda r: r["ex_ante_popwt"]),
                attend        = avg_i(runs, lambda r: r["attend"]),
                wasted        = avg_i(runs, lambda r: r["wasted"]),
                dark_sold     = avg_i(runs, lambda r: r["dark_sold"]),
                dark_unmatched= avg_i(runs, lambda r: r["dark_unmatched"]),
            ))

            dark_rows.append(dict(
                enforcement   = enf["label"],
                series        = series["label"],
                demand        = mul,
                dark_sold     = avg_i(runs, lambda r: r["dark_sold"]),
                dark_unmatched= avg_i(runs, lambda r: r["dark_unmatched"]),
                dark_total    = avg_i(runs, lambda r: r["dark_sold"] + r["dark_unmatched"]),
                attend        = avg_i(runs, lambda r: r["attend"]),
                wasted        = avg_i(runs, lambda r: r["wasted"]),
            ))

            sys.stdout.write(".")
            sys.stdout.flush()
        print()
    print()


# ── Write CSVs ────────────────────────────────────────────────────────────────
def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

write_csv("enforcement-sweep-summary.csv", summary_rows)
write_csv("enforcement-sweep-dark.csv",    dark_rows)
print("Wrote enforcement-sweep-summary.csv  and  enforcement-sweep-dark.csv\n")


# ── Console: PopWt GR — Bounded 25% across enforcement × demand ───────────────
def get(enf_id, series_label, demand, field):
    return next(r[field] for r in summary_rows
                if r["enforcement_id"] == enf_id
                and r["series"] == series_label
                and r["demand"] == demand)


print("── PopWt GR: Bounded 25% vs Status Quo — by enforcement level ──")
print(f"{'Demand':>7} | {'SQ':>8} | {'B25 Full':>8} | {'B25 Part':>8} | {'B25 None':>8} "
      f"| {'Δ Full':>8} | {'Δ Part':>8} | {'Δ None':>8}")
print("-" * 82)
for mul in DEMAND_LEVELS:
    sq_full = get("full", "Status Quo",   mul, "gr_popwt")
    b25_f   = get("full", "Bounded 25%",  mul, "gr_popwt")
    b25_p   = get("partial", "Bounded 25%", mul, "gr_popwt")
    b25_n   = get("none",    "Bounded 25%", mul, "gr_popwt")
    print(f"  {mul:>5} | {sq_full:>8.4f} | {b25_f:>8.4f} | {b25_p:>8.4f} | {b25_n:>8.4f} "
          f"| {b25_f-sq_full:>+8.4f} | {b25_p-sq_full:>+8.4f} | {b25_n-sq_full:>+8.4f}")


# ── Console: dark market leakage — Bounded 25% ───────────────────────────────
print("\n── Dark market tickets — Bounded 25% by enforcement × demand ──")
print(f"{'Demand':>7} | {'Full Enf':>8} | {'Partial':>8} | {'No Enf':>8} | {'B25 Full Attend':>15} | {'B25 None Attend':>15}")
print("-" * 75)
for mul in DEMAND_LEVELS:
    dk_f = get("full",    "Bounded 25%", mul, "dark_sold") + get("full",    "Bounded 25%", mul, "dark_unmatched")
    dk_p = get("partial", "Bounded 25%", mul, "dark_sold") + get("partial", "Bounded 25%", mul, "dark_unmatched")
    dk_n = get("none",    "Bounded 25%", mul, "dark_sold") + get("none",    "Bounded 25%", mul, "dark_unmatched")
    at_f = get("full",    "Bounded 25%", mul, "attend")
    at_n = get("none",    "Bounded 25%", mul, "attend")
    print(f"  {mul:>5} | {dk_f:>8} | {dk_p:>8} | {dk_n:>8} | {at_f:>15} | {at_n:>15}")


# ── Console: does B25 still beat SQ with no enforcement? ─────────────────────
print("\n── Does Bounded 25% (no enforcement) still outperform Status Quo? ──")
print(f"{'Demand':>7} | {'Fan GR Δ':>10} | {'PopWt GR Δ':>11} | {'System GR Δ':>12} | {'Verdict':>10}")
print("-" * 60)
beats = 0
for mul in DEMAND_LEVELS:
    sq_fan  = get("full", "Status Quo", mul, "gr_fan")
    sq_pw   = get("full", "Status Quo", mul, "gr_popwt")
    sq_sys  = get("full", "Status Quo", mul, "gr_system")
    b25_fan = get("none",    "Bounded 25%", mul, "gr_fan")
    b25_pw  = get("none",    "Bounded 25%", mul, "gr_popwt")
    b25_sys = get("none",    "Bounded 25%", mul, "gr_system")
    d_fan   = b25_fan - sq_fan
    d_pw    = b25_pw  - sq_pw
    d_sys   = b25_sys - sq_sys
    n_beat  = sum(1 for d in [d_fan, d_pw, d_sys] if d > 0)
    verdict = "✓ beats SQ" if n_beat >= 2 else ("≈ mixed" if n_beat == 1 else "✗ loses")
    if n_beat >= 2:
        beats += 1
    print(f"  {mul:>5} | {d_fan:>+10.4f} | {d_pw:>+11.4f} | {d_sys:>+12.4f} | {verdict:>10}")
print(f"\n  Bounded 25% (no enforcement) beats SQ on majority of lenses: "
      f"{beats}/{len(DEMAND_LEVELS)} demand levels")


# ── Console: optimal cap per enforcement level (PopWt) ───────────────────────
print("\n── Optimal bounded cap by demand × enforcement level (PopWt lens) ──")
print(f"{'Demand':>7} | {'Full Enf Opt':>12} | {'Partial Opt':>11} | {'No Enf Opt':>10}")
print("-" * 50)
BOUNDED_IDS = ["bounded_10", "bounded_20", "bounded_25", "bounded_30"]
BOUNDED_LABELS = {bid: next(s["label"] for s in POLICY_SERIES if s["id"] == bid) for bid in BOUNDED_IDS}
for mul in DEMAND_LEVELS:
    opt_f = max(BOUNDED_IDS, key=lambda bid: get("full",    BOUNDED_LABELS[bid], mul, "gr_popwt"))
    opt_p = max(BOUNDED_IDS, key=lambda bid: get("partial", BOUNDED_LABELS[bid], mul, "gr_popwt"))
    opt_n = max(BOUNDED_IDS, key=lambda bid: get("none",    BOUNDED_LABELS[bid], mul, "gr_popwt"))
    print(f"  {mul:>5} | {BOUNDED_LABELS[opt_f]:>12} | {BOUNDED_LABELS[opt_p]:>11} | {BOUNDED_LABELS[opt_n]:>10}")
