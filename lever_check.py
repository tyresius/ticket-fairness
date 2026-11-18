"""Exploratory, 9 Nov 2026 (not pre-registered). Which lever does more for fans:
the draft Bill's fee cap or a positive ceiling? A 2x2 on paired seeds:

    ceiling 0% or 20%   x   resale fees 15%/side (model default) or 5%/side (fee cap)

All four arms have the bounded rule's 4-ticket limit, as in sweep_config. Reports, with
95% CIs over 300 paired seeds per demand level, under P0/P1/P2, on mean individual fan
utility and PopWt:
    fee-cap effect at each ceiling, ceiling effect at each fee level, and
    (ceiling effect) minus (fee-cap effect) at the other lever's two settings.
Run from the Ticket Fairness repo:  /usr/local/bin/python3 lever_check.py
"""
import math
import random
import statistics as st

from gre_sim import Rule, simulate
from price_check import score_run

FEE = dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)
ARMS = {
    "0%":      (Rule("Bounded 0%", 0.0, 4, None), {}),
    "0%+fee":  (Rule("Bounded 0% + fee cap", 0.0, 4, None), FEE),
    "20%":     (Rule("Bounded 20%", 0.20, 4, None), {}),
    "20%+fee": (Rule("Bounded 20% + fee cap", 0.20, 4, None), FEE),
}
LEVELS = [1.5, 2, 3, 4, 5, 6, 7, 8, 10]
FORMS = (("P0", "saturating"), ("P1", "linear"), ("P2", "surplus"))
N = 300

vals = {}
for i, d in enumerate(LEVELS):
    for s in range(N):
        seed = 99_000_000 + 10_000 * i + s
        for arm, (rule, kw) in ARMS.items():
            random.seed(seed)
            r = simulate(rule, d, return_agents=True, **kw)
            sc = score_run(r, rule)
            for code, form in FORMS:
                vals.setdefault((arm, d, "fan", code), []).append(sc[form]["fan_mean"])
                vals.setdefault((arm, d, "pop", code), []).append(sc[form]["pop_wt"])


def series(arm, d, m, c):
    return vals[(arm, d, m, c)]


def show(label, fn):
    for metric, mlab in (("fan", "mean fan utility"), ("pop", "PopWt")):
        print(f"\n{label} -- {mlab}: mean [95% CI]  '*' > 0, '!' < 0")
        for code, _ in FORMS:
            cells = []
            for d in LEVELS:
                x = fn(d, metric, code)
                m, sd = st.mean(x), st.stdev(x)
                h = 1.96 * sd / math.sqrt(len(x))
                flag = "*" if m - h > 0 else ("!" if m + h < 0 else " ")
                cells.append(f"{d:g}x {m:+.4f}[{m - h:+.4f},{m + h:+.4f}]{flag}")
            print(f"  {code}: " + "  ".join(cells))


def diff(a, b):
    return lambda d, m, c: [x - y for x, y in zip(series(a, d, m, c), series(b, d, m, c))]


def ceiling_minus_fee(cei_hi, cei_lo, fee_hi, fee_lo):
    return lambda d, m, c: [(a - b) - (e - f) for a, b, e, f in zip(
        series(cei_hi, d, m, c), series(cei_lo, d, m, c), series(fee_hi, d, m, c), series(fee_lo, d, m, c))]


show("Fee-cap effect at a 0% ceiling (0%+fee minus 0%)", diff("0%+fee", "0%"))
show("Fee-cap effect at a 20% ceiling (20%+fee minus 20%)", diff("20%+fee", "20%"))
show("Ceiling effect without fee cap (20% minus 0%)", diff("20%", "0%"))
show("Ceiling effect with fee cap (20%+fee minus 0%+fee)", diff("20%+fee", "0%+fee"))
show("Ceiling step minus fee-cap step, each alone (20%-0%) - (0%+fee - 0%)",
     ceiling_minus_fee("20%", "0%", "0%+fee", "0%"))
show("Ceiling step minus fee-cap step, each added to the other (20%+fee - 0%+fee) - (20%+fee - 20%)",
     ceiling_minus_fee("20%+fee", "0%+fee", "20%+fee", "20%"))
