"""Exploratory, 9 Nov 2026 (not pre-registered; measures the packages the revised
brief recommends, decides nothing).

The draft Bill keeps a platform fee cap; the stored grid has the fee cap only with
0%, 10% and 20% ceilings. This runs the status quo and 0/10/20/30/40% ceilings,
all but the status quo with the 5%/side fee cap (as sweep_config's UK 2026 arms),
on paired seeds, scored P0/P1/P2 (price_check.score_run). Also reports scalper
return on investment, inverted from the model's scalper utility (gre_sim.py:706;
utility 0.95 = ROI of 100% or more).
Run from the Ticket Fairness repo:  /usr/local/bin/python3 explore_fee_packages.py
"""
import random
import statistics as st

from gre_sim import Rule, simulate
from price_check import score_run

FEE = dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)
ARMS = [("Status quo", Rule("Status Quo", None, 8, None), {})] + [
    (f"{c}% + fee cap", Rule(f"Bounded {c}% + fee cap", c / 100, 4, None), FEE) for c in (0, 10, 20, 30, 40)]
LEVELS = [1.5, 2, 3, 4, 5, 6, 7, 8, 10]
N = 100


def roi(u):
    return (u - 0.3) / 0.65 if u >= 0.3 else u - 0.3


res_tab = {}
for i, d in enumerate(LEVELS):
    for name, rule, kw in ARMS:
        acc = {k: [] for k in ("P0", "P1", "P2", "f0", "f1", "f2", "sc")}
        for s in range(N):
            random.seed(66_000_000 + 1_000 * i + s)
            r = simulate(rule, d, return_agents=True, **kw)
            sc = score_run(r, rule)
            for code, form in (("0", "saturating"), ("1", "linear"), ("2", "surplus")):
                acc["P" + code].append(sc[form]["pop_wt"]); acc["f" + code].append(sc[form]["fan_mean"])
            acc["sc"].append(r["outcomes"]["scalper"]["utility"])
        res_tab[(name, d)] = {k: st.mean(v) for k, v in acc.items()}

for metric, label in (("P0", "PopWt P0"), ("P1", "PopWt P1"), ("P2", "PopWt P2"),
                      ("f0", "mean fan utility P0"), ("f1", "mean fan utility P1"), ("f2", "mean fan utility P2")):
    print(f"\n{label}")
    print(f"{'arm':16s}" + "".join(f"{d:>8g}x" for d in LEVELS))
    for name, _, _ in ARMS:
        print(f"{name:16s}" + "".join(f"{res_tab[(name, d)][metric]:9.3f}" for d in LEVELS))
print("\nScalper ROI (from mean scalper utility; status quo 0.95 = 100% or more)")
print(f"{'arm':16s}" + "".join(f"{d:>8g}x" for d in LEVELS))
for name, _, _ in ARMS:
    print(f"{name:16s}" + "".join(f"{roi(res_tab[(name, d)]['sc']):+9.0%}" for d in LEVELS))
