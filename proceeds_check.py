"""Proceeds-scored check of the brief's band (9 Nov 2026). Exploratory.

Why: /validate-claim found that the resale-option term, assigned by formula from
the cap level (role_proof.resale_option), carries the band's high-demand results:
the 30% end and the "ceiling is the stronger lever" claim. This replaces the
formula with what actually happens in each run. Definitions, fixed before running:

  default  The formula option value for every ticket holder (as the brief's runs).
  A        Fans who actually resold are scored on their realized net upside
           (role_proof's proceeds variant, approved 5 Nov). Everyone else keeps the
           formula value.
  B        As A, but every other ticket holder's resale term is the resale channel's
           realized value in that run: the mean, over fans whose plans changed
           (phase "reselling"), of upside_value(net upside per ticket), where net
           upside = (net proceeds actually received / tickets held - cost basis) / face.
           Tickets never listed or listed but unsold recover nothing. If no fan's
           plans changed in a run, the formula value is used.

Arms (300 paired seeds per demand level; same seeds as kill_test_h1h2.py, so the
default rows must reproduce its "ref" rows): face value, 20% and 30% ceilings, each
with the 5%/side fee cap; and a 20% ceiling at today's 15%/side fees (for the lever claim).
Outcome: mean individual fan utility under P0/P1/P2, with 95% CIs on paired differences.
Run from the Ticket Fairness repo:  /usr/local/bin/python3 proceeds_check.py
"""
import math
import random
import statistics as st

from gre_sim import DEFAULT_UTILITY_W, FACE, FAN_TYPES, Rule, simulate
from role_proof import agent_utility, realized_proceeds, resale_option, upside_value

FEE = dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)
ARMS = {
    "0%+fee":  (Rule("Bounded 0% + fee cap", 0.0, 4, None), FEE),
    "20%":     (Rule("Bounded 20%", 0.20, 4, None), {}),
    "20%+fee": (Rule("Bounded 20% + fee cap", 0.20, 4, None), FEE),
    "30%+fee": (Rule("Bounded 30% + fee cap", 0.30, 4, None), FEE),
}
LEVELS = [1.5, 2, 3, 4, 5, 6, 7, 8, 10]
FORMS = (("P0", "saturating"), ("P1", "linear"), ("P2", "surplus"))
VARIANTS = ("default", "A", "B")
N = 300


def channel_value(res):
    """Realized value of the resale channel for fans whose plans changed (B)."""
    proc = realized_proceeds(res)
    vals = []
    for a in res["agents"]:
        if a.type in FAN_TYPES and a.phase == "reselling" and a.tickets > 0:
            net_received = proc.get(a.id, (0, 0.0))[1]
            vals.append(upside_value((net_received / a.tickets - a.cost_basis) / FACE))
    return (sum(vals) / len(vals)) if vals else None


def fan_mean(res, variant, form):
    if variant == "default":
        kw = dict(proceeds=False)
    elif variant == "A":
        kw = dict(proceeds=True)
    else:
        kw = dict(proceeds=True, resale_override=res["_channel"])
    us = [agent_utility(a, res, 0.0, uw=DEFAULT_UTILITY_W, price_form=form, **kw)
          for t in FAN_TYPES for a in res["agents"] if a.type == t]
    return sum(us) / len(us)


vals, chan, formula = {}, {}, {}
for i, d in enumerate(LEVELS):
    for s in range(N):
        seed = 77_700_000 + 10_000 * i + s
        for arm, (rule, kw) in ARMS.items():
            random.seed(seed)
            r = simulate(rule, d, return_agents=True, **kw)
            r["_channel"] = channel_value(r)
            chan.setdefault((arm, d), []).append(r["_channel"])
            formula[(arm, d)] = resale_option(r["continuation_rule"], r["secondary_fee_seller"])
            for v in VARIANTS:
                for code, form in FORMS:
                    vals.setdefault((arm, d, v, code), []).append(fan_mean(r, v, form))

print("Resale channel: formula value vs realized value (B), mean over runs")
for arm in ARMS:
    print(f"  {arm:8s} formula {formula[(arm, 2)]:.3f} | realized " + " ".join(
        f"{d:g}x {st.mean([c for c in chan[(arm, d)] if c is not None]):.3f}" for d in LEVELS))

TESTS = [("H1: 20%+fee minus 0%+fee", "20%+fee", "0%+fee"),
         ("H1: 30%+fee minus 0%+fee", "30%+fee", "0%+fee"),
         ("Band: 30%+fee minus 20%+fee", "30%+fee", "20%+fee"),
         ("H2: 20% (today's fees) minus 0%+fee", "20%", "0%+fee")]
for v in VARIANTS:
    for label, a, b in TESTS:
        print(f"\n[{v}] {label} -- mean fan utility: mean [95% CI]  '*' > 0, '!' < 0")
        for code, _ in FORMS:
            cells = []
            for d in LEVELS:
                x = [p - q for p, q in zip(vals[(a, d, v, code)], vals[(b, d, v, code)])]
                m, sd = st.mean(x), st.stdev(x)
                h = 1.96 * sd / math.sqrt(len(x))
                flag = "*" if m - h > 0 else ("!" if m + h < 0 else " ")
                cells.append(f"{d:g}x {m:+.4f}[{m - h:+.4f},{m + h:+.4f}]{flag}")
            print(f"  {code}: " + "  ".join(cells))
