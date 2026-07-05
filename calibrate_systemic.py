"""
Two-Point Systemic-Fraud Calibration with Event-Demand Distribution
===================================================================

Problem
-------
Real-world fraud rates (Ireland 13.6% @ 0% cap; Victoria 13.7% @ 10% cap;
UK 3.8% uncapped) are BLENDED AVERAGES across an entire portfolio of events
spanning many demand levels — not measurements at a single scarcity point.
Calibrating DARK_SYSTEMIC_K to "0% cap at demand 8x" was arbitrary on the
demand axis. This script instead:

  1. Defines a realistic event-demand distribution (most events near face-value
     clearing, a long tail of high-demand events).
  2. Computes the model's DEMAND-WEIGHTED fraud rate at each cap regime.
  3. Solves for DARK_SYSTEMIC_K so the demand-weighted fraud at the tight-cap
     regimes matches the Ireland/Victoria anchors (~13.6-13.7%).
  4. Checks the uncapped baseline against the UK anchor (3.8%).

Event-demand distribution
-------------------------
Empirical anchor: 62% of events see resale BELOW face value (scalpers absorb
demand risk) — i.e. most events are NOT oversold. Only a minority are scarcity
events. We model demand as a discrete distribution with most mass at/below 2x
and a declining tail to 10x. This is the portfolio a national fraud statistic
actually averages over.

Outputs:
  systemic-calibration.csv  — per-cap demand-weighted fraud at candidate K values
  console: solved K, fit quality vs all three anchors
"""

import random
import csv
import sys

from gre_sim import simulate, Rule, VENUE, BASELINE_SECONDARY_FRAUD_PENALTY

random.seed(42)

# ── Empirical anchors (cap regime → observed blended fraud rate) ──────────────
ANCHORS = {
    "ireland_0":   dict(cap=0.0,  fraud=0.136, label="Ireland 0% cap"),
    "victoria_10": dict(cap=0.10, fraud=0.137, label="Victoria 10% cap"),
    "uk_uncapped": dict(cap=None, fraud=0.038, label="UK uncapped"),
}

# ── Event-demand distribution ────────────────────────────────────────────────
# Probability mass over demand multipliers. Anchored to "62% of events resell
# below face value" — most events cluster near/below clearing, with a scarcity
# tail. Weights sum to 1.0. We treat demand <=1 as "not oversold" (no dark
# market pressure) and place the majority of mass there.
#
# Interpretation: a national fraud statistic is dominated by the many low-demand
# events (little fraud) diluted with the few high-demand events (much fraud).
DEMAND_DISTRIBUTION = {
    1.0: 0.45,   # not oversold — clears at/below face (the 62%-below-face mass)
    1.5: 0.20,
    2.0: 0.13,
    3.0: 0.09,
    5.0: 0.07,
    8.0: 0.04,
    10.0: 0.02,
}
assert abs(sum(DEMAND_DISTRIBUTION.values()) - 1.0) < 1e-9, "demand dist must sum to 1"

RUNS = 200


def weighted_fraud(cap, k, runs=RUNS):
    """
    Demand-weighted modeled fraud rate for a cap regime at systemic coefficient k.
    For capped regimes: systemic dark fraud (market-wide), demand-weighted.
    For uncapped regime (cap=None): baseline secondary fraud proxy.
    """
    total = 0.0
    for mul, w in DEMAND_DISTRIBUTION.items():
        if cap is None:
            rule = Rule("Status Quo", cap=None, plimit=8, dyn_mul=None)
        else:
            rule = Rule(f"B{int(cap*100)}", cap=cap, plimit=4, dyn_mul=None)
        random.seed(42)
        fr = 0.0
        for _ in range(runs):
            r = simulate(rule, mul, dark_systemic_k=k)
            if cap is None:
                # uncapped: fraud is the baseline secondary fraud realized.
                # Proxy: fraction of attendees who bought secondary × baseline rate.
                sec = r["secondary_sold"]
                att = max(1, r["attend"])
                fr += min(1.0, (sec / att)) * BASELINE_SECONDARY_FRAUD_PENALTY
            else:
                fr += r["systemic_fraud"]
        total += w * (fr / runs)
    return total


def solve_k():
    """
    Solve for K so the demand-weighted fraud at the tight-cap anchors
    (Ireland 0%, Victoria 10%) best matches their observed rates.
    Uses the mean of the two tight-cap targets as the joint objective,
    scanning a K grid and minimizing squared error across BOTH points.
    """
    targets = [(ANCHORS["ireland_0"]["cap"],   ANCHORS["ireland_0"]["fraud"]),
               (ANCHORS["victoria_10"]["cap"], ANCHORS["victoria_10"]["fraud"])]
    best = None
    grid = [round(x, 2) for x in [1.0 + 0.25 * i for i in range(21)]]  # 1.0 .. 6.0
    scan = []
    for k in grid:
        sse = 0.0
        modeled = {}
        for cap, tgt in targets:
            m = weighted_fraud(cap, k)
            modeled[cap] = m
            sse += (m - tgt) ** 2
        scan.append((k, sse, modeled))
        if best is None or sse < best[1]:
            best = (k, sse, modeled)
    return best, scan


def main():
    print("Two-point systemic-fraud calibration with event-demand distribution")
    print(f"Demand distribution: {DEMAND_DISTRIBUTION}")
    print(f"Anchors: Ireland 0%→13.6%, Victoria 10%→13.7%, UK uncapped→3.8%\n")
    print("Solving for DARK_SYSTEMIC_K (scanning grid)...\n")

    best, scan = solve_k()
    k_star = best[0]

    # Report fit at solved K
    print(f"{'K':>5} | {'SSE(tight)':>10} | {'mdl 0%':>7} | {'mdl 10%':>7}")
    print("-" * 40)
    for k, sse, modeled in scan:
        mark = "  <- best" if k == k_star else ""
        print(f"{k:>5.2f} | {sse:>10.5f} | {modeled.get(0.0,0):>7.4f} | {modeled.get(0.10,0):>7.4f}{mark}")

    print(f"\n>>> Solved DARK_SYSTEMIC_K = {k_star}\n")

    # Full fit table at K* against ALL three anchors
    print("── Fit vs all empirical anchors at K* ──")
    print(f"{'Regime':<20} | {'cap':>5} | {'observed':>9} | {'modeled':>9} | {'error':>8}")
    print("-" * 62)
    rows = []
    for key, a in ANCHORS.items():
        m = weighted_fraud(a["cap"], k_star)
        err = m - a["fraud"]
        capstr = "uncap" if a["cap"] is None else f"{int(a['cap']*100)}%"
        print(f"{a['label']:<20} | {capstr:>5} | {a['fraud']:>9.4f} | {m:>9.4f} | {err:>+8.4f}")
        rows.append(dict(regime=a["label"], cap=capstr,
                         observed=a["fraud"], modeled=round(m, 4), error=round(err, 4)))

    # Demand-resolved fraud at K* (show where each anchor's blend comes from)
    print(f"\n── Demand-resolved systemic fraud at K*={k_star} (the blend components) ──")
    print(f"{'demand':>7} | {'weight':>7} | {'0% cap':>7} | {'10% cap':>7} | {'20% cap':>7}")
    print("-" * 50)
    for mul, w in DEMAND_DISTRIBUTION.items():
        vals = {}
        for cap in [0.0, 0.10, 0.20]:
            random.seed(42)
            fr = sum(simulate(Rule(f"B{int(cap*100)}", cap=cap, plimit=4, dyn_mul=None),
                              mul, dark_systemic_k=k_star)["systemic_fraud"]
                     for _ in range(RUNS)) / RUNS
            vals[cap] = fr
        print(f"{mul:>7} | {w:>7.2f} | {vals[0.0]:>7.4f} | {vals[0.10]:>7.4f} | {vals[0.20]:>7.4f}")

    with open("systemic-calibration.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["regime", "cap", "observed", "modeled", "error"])
        w.writeheader(); w.writerows(rows)
    print("\nWrote systemic-calibration.csv")
    print(f"\nACTION: set DARK_SYSTEMIC_K = {k_star} in gre_sim.py if fit is acceptable.")


if __name__ == "__main__":
    main()
