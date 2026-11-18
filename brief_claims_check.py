"""Exploratory, 9 Nov 2026 (not pre-registered). Paired confidence intervals for the
quantitative claims in the revised POLICY_BRIEF.md draft. Decides nothing; it sizes
and checks the sentences before /validate-claim.

Arms (300 paired seeds per demand level): status quo; 0%, 10%, 20%, 30% ceilings, each
with the draft Bill's fee cap (5%/side, as sweep_config's UK 2026 arms).
Differences reported with 95% CIs, on mean individual fan utility and PopWt, under the
three price scores (P0 model, P1 keep counting, P2 share of own value kept).
Also: scalper ROI from mean scalper utility (gre_sim.py:706 inverted; 0.95 = 100% or more).
Run from the Ticket Fairness repo:  /usr/local/bin/python3 brief_claims_check.py
"""
import math
import random
import statistics as st

from gre_sim import Rule, simulate
from price_check import score_run

FEE = dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)
ARMS = {"SQ": (Rule("Status Quo", None, 8, None), {})}
ARMS.update({f"{c}%+fee": (Rule(f"Bounded {c}% + fee cap", c / 100, 4, None), FEE) for c in (0, 10, 20, 30)})
LEVELS = [1.5, 2, 3, 4, 5, 6, 7, 8, 10]
FORMS = (("P0", "saturating"), ("P1", "linear"), ("P2", "surplus"))
N = 300
COMPARISONS = [("30%+fee", "0%+fee"), ("20%+fee", "0%+fee"), ("10%+fee", "0%+fee"),
               ("30%+fee", "SQ"), ("20%+fee", "SQ"), ("30%+fee", "20%+fee")]


def roi(u):
    return (u - 0.3) / 0.65 if u >= 0.3 else u - 0.3


def ci(xs):
    m, sd = st.mean(xs), st.stdev(xs)
    h = 1.96 * sd / math.sqrt(len(xs))
    return m, m - h, m + h


vals = {}      # (arm, d, metric, code) -> list over seeds
scal = {}      # (arm, d) -> list of scalper utility
for i, d in enumerate(LEVELS):
    for s in range(N):
        seed = 88_000_000 + 10_000 * i + s
        for arm, (rule, kw) in ARMS.items():
            random.seed(seed)
            r = simulate(rule, d, return_agents=True, **kw)
            sc = score_run(r, rule)
            for code, form in FORMS:
                vals.setdefault((arm, d, "fan", code), []).append(sc[form]["fan_mean"])
                vals.setdefault((arm, d, "pop", code), []).append(sc[form]["pop_wt"])
            scal.setdefault((arm, d), []).append(r["outcomes"]["scalper"]["utility"])

for a, b in COMPARISONS:
    for metric, label in (("fan", "mean fan utility"), ("pop", "PopWt")):
        print(f"\n{a} minus {b}, {label}: mean [95% CI]; '*' = CI excludes 0 in a's favour, '!' = in b's favour")
        for code, _ in FORMS:
            cells = []
            for d in LEVELS:
                diff = [x - y for x, y in zip(vals[(a, d, metric, code)], vals[(b, d, metric, code)])]
                m, lo, hi = ci(diff)
                flag = "*" if lo > 0 else ("!" if hi < 0 else " ")
                cells.append(f"{d:g}x {m:+.4f}[{lo:+.4f},{hi:+.4f}]{flag}")
            print(f"  {code}: " + "  ".join(cells))

print("\nScalper ROI from mean scalper utility")
for arm in ARMS:
    print(f"  {arm:8s} " + " ".join(f"{d:g}x {roi(st.mean(scal[(arm, d)])):+.0%}" for d in LEVELS))
