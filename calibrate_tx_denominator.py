#!/usr/bin/env python3
"""
TF2 — Systemic-fraud calibration with the TRANSACTION denominator
==================================================================
Decision support for the one open model question (tabled 2026-05-31).

History: the systemic dark-market externality (DARK_SYSTEMIC_K etc.) failed
calibration against the Ireland 13.6% / Victoria 13.7% / UK 3.8% anchors and
was disabled in baseline (SYSTEMIC_FRAUD_WEIGHT=0). Root cause was UNITS:
the anchors measure fraud PER SECONDARY-MARKET TRANSACTION, while the model
computed prevalence as dark_sold/VENUE (per seat). This script tests whether
the proposed fix — prevalence = dark_sold/(secondary_sold + dark_sold) —
can actually hit the anchors, WITHOUT touching gre_sim.py: it recomputes the
externality from simulate()'s existing outputs (dark_sold, secondary_sold
are both returned), demand-weighted over the same event portfolio as
calibrate_tw.py.

Anchor targets (provenance: Bradshaw Advisory June 2025, StubHub-funded —
cite with disclosure):
    face-value cap regime (Ireland):   13.6% of secondary transactions
    10% cap regime (Victoria):         13.7%
    uncapped regime (UK, pre-ban):      3.8%

Output: transaction-weighted dark share by cap regime, the implied K that
maps dark share -> fraud rate, and a fit verdict. If the dark share itself
is in the right band, the externality can be re-enabled with the new
denominator; if not, recommend formal retirement (the fee mechanism already
carries the economic argument).
"""

import random

from gre_sim import simulate, Rule

# Event-demand portfolio (same as calibrate_tw.py): most events not oversold.
DIST = {1.0: 0.45, 1.5: 0.20, 2.0: 0.13, 3.0: 0.09, 5.0: 0.07, 8.0: 0.04, 10.0: 0.02}
RUNS = 200

REGIMES = {
    "Ireland (0% cap)":   Rule("Ireland", cap=0.0,  plimit=4, dyn_mul=None),
    "Victoria (10% cap)": Rule("Victoria", cap=0.10, plimit=4, dyn_mul=None),
    "UK pre-ban (uncap)": Rule("UK",      cap=None, plimit=8, dyn_mul=None),
}
ANCHORS = {"Ireland (0% cap)": 0.136, "Victoria (10% cap)": 0.137,
           "UK pre-ban (uncap)": 0.038}


def tx_weighted_dark_share(rule):
    """Demand-weighted dark share of secondary transactions:
    sum over portfolio of w * dark / (secondary + dark), weighted by that
    event's secondary-transaction volume (fraud stats are per-transaction,
    and transactions concentrate on high-demand events)."""
    num = den = 0.0
    for mul, w in DIST.items():
        random.seed(42)
        for _ in range(RUNS):
            r = simulate(rule, mul)
            tx = r["secondary_sold"] + r["dark_sold"]
            if tx > 0:
                num += w * r["dark_sold"]
                den += w * tx
    return num / den if den > 0 else 0.0


def main():
    print("TF2 — transaction-denominator systemic-fraud calibration")
    print(f"Portfolio: {DIST}; {RUNS} runs/point; seed 42\n")
    print(f"{'Regime':<22} | {'tx dark share':>13} | {'anchor fraud':>12} | "
          f"{'implied fraud/dark':>18}")
    print("-" * 76)
    shares = {}
    for name, rule in REGIMES.items():
        s = tx_weighted_dark_share(rule)
        shares[name] = s
        anchor = ANCHORS[name]
        implied = anchor / s if s > 0 else float('inf')
        print(f"{name:<22} | {s:>12.1%} | {anchor:>11.1%} | "
              f"{implied:>17.2f}x" if s > 0 else
              f"{name:<22} | {s:>12.1%} | {anchor:>11.1%} | {'n/a':>18}")

    print("\nInterpretation guide:")
    print("  The anchors say ~13.6% of secondary TRANSACTIONS are fraudulent in")
    print("  capped regimes. If the model's transaction-weighted dark share is in")
    print("  the ~10-30% band for capped regimes, then 'fraud rate = K_tx x dark")
    print("  share' needs a plausible K_tx (0.5-1.5): dark transactions carry the")
    print("  fraud, and the externality can be re-enabled with the transaction")
    print("  denominator. If dark share is far below the anchors (<5%), no honest")
    print("  K exists (K >> 1 would mean more fraud than dark transactions) and")
    print("  the externality should be formally RETIRED: the model's dark channel")
    print("  is too thin to carry a market-wide fraud story, and the fee")
    print("  mechanism already carries the welfare argument.")
    print("\n  Also note UK anchor (3.8%) is fraud in an UNCAPPED market — the")
    print("  model produces ZERO dark transactions there by construction, so that")
    print("  anchor is carried by BASELINE_SECONDARY_FRAUD_PENALTY, not by the")
    print("  dark channel. Only the capped-regime anchors bear on this decision.")


if __name__ == "__main__":
    main()
