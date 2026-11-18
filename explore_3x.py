"""Exploratory, 9 Nov 2026 (not pre-registered; diagnoses, decides nothing).

Why does the status quo score unusually well at 3x demand?
Hypothesis: the scalper markdown schedule steps from gentle (x0.85, x0.75) to
aggressive (x0.65, x0.45) just above 2x demand (gre_sim.py:602-604), while the
scalper ask grows with demand (mean FACE x (1 + 0.65 x demand), gre_sim.py:475).
Around 3x the last-round price (~0.45 x 2.95 = 1.33x face) falls within average
buyers' limit (1.6x); by 4x (~1.62x) it no longer does.

Test: status quo on a fine demand grid, as is and with the markdown forced to one
schedule at every demand (simulate's scalper_decay override). Bounded 40% for reference.
Paired seeds across arms. Scored with price_check.score_run (P0/P1/P2).
Run from the Ticket Fairness repo:  /usr/local/bin/python3 explore_3x.py
"""
import random
import statistics as st

from gre_sim import Rule, simulate
from price_check import score_run

SQ = Rule("Status Quo", None, 8, None)
B40 = Rule("Bounded 40%", 0.40, 4, None)
ARMS = [
    ("SQ as is", SQ, {}),
    ("SQ gentle markdown everywhere", SQ, dict(scalper_decay=(0.85, 0.75))),
    ("SQ aggressive markdown everywhere", SQ, dict(scalper_decay=(0.65, 0.45))),
    # ~33% total decay = the one documented anchor (PTR/Automatiq, project_gre_empirical_anchors)
    ("SQ 33% markdown everywhere (empirical anchor)", SQ, dict(scalper_decay=(0.80, 0.67))),
    ("Bounded 40% as is", B40, {}),
    ("Bounded 40% gentle markdown everywhere", B40, dict(scalper_decay=(0.85, 0.75))),
    ("Bounded 40% aggressive markdown everywhere", B40, dict(scalper_decay=(0.65, 0.45))),
]
GRID = [1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0, 4.5, 5.0, 5.5, 6.0]
N = 60

print(f"N={N} paired seeds per cell. PopWt and fan_mean under P0 (model's price score); "
      f"access and price paid by type; scalper utility; seats filled.\n")
hdr = (f"{'demand':>6} {'PopWt':>6} {'P1 Pop':>6} {'P2 Pop':>6} {'fanmean':>7} | "
       f"{'mega acc':>8} {'cas acc':>7} {'avg acc':>7} | {'cas paid':>8} {'avg paid':>8} | {'scalp u':>7} {'seats':>5}")
for name, rule, kw in ARMS:
    print(f"=== {name} ===")
    print(hdr)
    for i, d in enumerate(GRID):
        acc = {k: [] for k in ("p0", "p1", "p2", "fm", "mega", "cas", "avg", "casp", "avgp", "sc", "seats")}
        for s in range(N):
            random.seed(55_000_000 + 1_000 * i + s)
            res = simulate(rule, d, return_agents=True, **kw)
            sc = score_run(res, rule)
            o = res["outcomes"]
            acc["p0"].append(sc["saturating"]["pop_wt"]); acc["p1"].append(sc["linear"]["pop_wt"])
            acc["p2"].append(sc["surplus"]["pop_wt"]); acc["fm"].append(sc["saturating"]["fan_mean"])
            acc["mega"].append(o["mega_fan"]["got"] / o["mega_fan"]["total"])
            acc["cas"].append(o["committed_casual"]["got"] / o["committed_casual"]["total"])
            acc["avg"].append(o["average_buyer"]["got"] / o["average_buyer"]["total"])
            if o["committed_casual"]["got"]:
                acc["casp"].append(o["committed_casual"]["avg_price"])
            if o["average_buyer"]["got"]:
                acc["avgp"].append(o["average_buyer"]["avg_price"])
            acc["sc"].append(o["scalper"]["utility"]); acc["seats"].append(res["attend"])
        m = {k: (st.mean(v) if v else float("nan")) for k, v in acc.items()}
        print(f"{d:>6} {m['p0']:6.3f} {m['p1']:6.3f} {m['p2']:6.3f} {m['fm']:7.3f} | "
              f"{m['mega']:8.0%} {m['cas']:7.1%} {m['avg']:7.1%} | {m['casp']:8.0f} {m['avgp']:8.0f} | "
              f"{m['sc']:7.3f} {m['seats']:5.0f}")
    print()
