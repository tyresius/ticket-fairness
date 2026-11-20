"""Listing check -- design and criteria in LISTING_CHECK.md (written 11 Nov 2026
before any number under fan_listing="always" was computed).

Arms, seeds, scorings and the realized resale channel (B) are as proceeds_check.py.
Runs:
  * fan_listing="always": all 4 arms, 9 oversubscribed levels, 300 paired seeds.
  * fan_listing="model" at 1.5x and 10x only: harness check 2 (must reproduce
    proceeds_check.log) and the listing-share comparison.
Run from the Ticket Fairness repo:  /usr/local/bin/python3 listing_check.py
"""
import math
import random
import re
import statistics as st

from gre_sim import DEFAULT_UTILITY_W, FACE, FAN_TYPES, Rule, simulate
from role_proof import agent_utility, realized_proceeds, upside_value

FEE = dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)
ARMS = {
    "0%+fee":  (Rule("Bounded 0% + fee cap", 0.0, 4, None), FEE),
    "20%":     (Rule("Bounded 20%", 0.20, 4, None), {}),
    "20%+fee": (Rule("Bounded 20% + fee cap", 0.20, 4, None), FEE),
    "30%+fee": (Rule("Bounded 30% + fee cap", 0.30, 4, None), FEE),
}
LEVELS = [1.5, 2, 3, 4, 5, 6, 7, 8, 10]
HARNESS_LEVELS = [1.5, 10]
FORMS = (("P0", "saturating"), ("P1", "linear"), ("P2", "surplus"))
N = 300


def roi(u):
    return (u - 0.3) / 0.65 if u >= 0.3 else u - 0.3


def channel_value(res):            # identical to proceeds_check.channel_value
    proc = realized_proceeds(res)
    vals = []
    for a in res["agents"]:
        if a.type in FAN_TYPES and a.phase == "reselling" and a.tickets > 0:
            net_received = proc.get(a.id, (0, 0.0))[1]
            vals.append(upside_value((net_received / a.tickets - a.cost_basis) / FACE))
    return (sum(vals) / len(vals)) if vals else None


def fan_mean(res, variant, form):  # identical to proceeds_check.fan_mean ("default" and "B")
    kw = dict(proceeds=False) if variant == "default" else dict(proceeds=True, resale_override=res["_channel"])
    us = [agent_utility(a, res, 0.0, uw=DEFAULT_UTILITY_W, price_form=form, **kw)
          for t in FAN_TYPES for a in res["agents"] if a.type == t]
    return sum(us) / len(us)


def listing_share(res):
    ch = [a for a in res["agents"] if a.type in FAN_TYPES and a.phase == "reselling"]
    return (sum(1 for a in ch if a.resale_tickets > 0) / len(ch)) if ch else None


vals, share, scal = {}, {}, {}
for listing, levels in (("always", LEVELS), ("model", HARNESS_LEVELS)):
    for d in levels:
        i = LEVELS.index(d)
        for s in range(N):
            seed = 77_700_000 + 10_000 * i + s
            for arm, (rule, kw) in ARMS.items():
                random.seed(seed)
                r = simulate(rule, d, return_agents=True, fan_listing=listing, **kw)
                r["_channel"] = channel_value(r)
                share.setdefault((listing, arm, d), []).append(listing_share(r))
                scal.setdefault((listing, arm, d), []).append(r["outcomes"]["scalper"]["utility"])
                for v in ("default", "B"):
                    for code, form in FORMS:
                        vals.setdefault((listing, arm, d, v, code), []).append(fan_mean(r, v, form))

TESTS = [("L1", "20%+fee", "0%+fee", LEVELS), ("L2", "30%+fee", "0%+fee", LEVELS),
         ("L3", "30%+fee", "20%+fee", LEVELS), ("L4", "20%", "0%+fee", [1.5, 2, 3, 4, 5, 6])]
PROCEEDS_LABEL = {"L1": "H1: 20%+fee minus 0%+fee", "L2": "H1: 30%+fee minus 0%+fee",
                  "L3": "Band: 30%+fee minus 20%+fee", "L4": "H2: 20% (today's fees) minus 0%+fee"}


def diff_stats(listing, a, b, d, v, code):
    x = [p - q for p, q in zip(vals[(listing, a, d, v, code)], vals[(listing, b, d, v, code)])]
    m, sd = st.mean(x), st.stdev(x)
    h = 1.96 * sd / math.sqrt(len(x))
    return m, m - h, m + h


# Harness check 2: model-listing rows must reproduce proceeds_check.log (default and B blocks).
log = open("proceeds_check.log").read()
blocks = re.split(r"\n(?=\[)", log)
bad = checked = 0
for name, a, b, _ in TESTS:
    for v in ("default", "B"):
        blk = next(x for x in blocks if x.startswith(f"[{v}] {PROCEEDS_LABEL[name]}"))
        for code, _ in FORMS:
            line = next(l for l in blk.splitlines() if l.strip().startswith(code + ":"))
            stored = dict(re.findall(r"([\d.]+)x ([+-]\d\.\d{4})\[", line))
            for d in HARNESS_LEVELS:
                m, _, _ = diff_stats("model", a, b, d, v, code)
                checked += 1
                if f"{m:+.4f}" != stored[f"{d:g}"]:
                    bad += 1
                    print(f"  mismatch {name} [{v}] {code} {d}x: {m:+.4f} vs stored {stored[f'{d:g}']}")
print(f"Harness check 2: model-listing rows vs proceeds_check.log -> {bad} mismatches of {checked}")
if bad:
    raise SystemExit("Harness failed; nothing below is valid.")

print("\nShare of plan-changed fans who list (model -> always)")
for arm in ARMS:
    print(f"  {arm:8s} " + "  ".join(
        f"{d:g}x {st.mean([x for x in share[('model', arm, d)] if x is not None]):.0%}"
        f" -> {st.mean([x for x in share[('always', arm, d)] if x is not None]):.0%}" for d in HARNESS_LEVELS))

print("\nReseller ROI under fan_listing='always' (from mean scalper utility)")
for arm in ("20%+fee", "30%+fee"):
    print(f"  {arm:8s} " + " ".join(f"{d:g}x {roi(st.mean(scal[('always', arm, d)])):+.0%}" for d in LEVELS))

verdict = {}
for v in ("B", "default"):
    for name, a, b, levels in TESTS:
        print(f"\n[always, {v}] {name}: {a} minus {b} -- mean fan utility: mean [95% CI]  '*' > 0, '!' < 0")
        ok = True
        for code, _ in FORMS:
            cells = []
            for d in levels:
                m, lo, hi = diff_stats("always", a, b, d, v, code)
                flag = "*" if lo > 0 else ("!" if hi < 0 else " ")
                ok &= lo > 0
                cells.append(f"{d:g}x {m:+.4f}[{lo:+.4f},{hi:+.4f}]{flag}")
            print(f"  {code}: " + "  ".join(cells))
        verdict[(name, v)] = ok

print("\nVerdicts (criteria in LISTING_CHECK.md; judged on B, default reported):")
for name, *_ in TESTS:
    print(f"  {name}: {'HOLDS' if verdict[(name, 'B')] else 'FAILS'}   (default scoring: {'holds' if verdict[(name, 'default')] else 'fails'})")
