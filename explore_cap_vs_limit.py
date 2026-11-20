"""Exploratory, 9 Nov 2026 (not pre-registered; informs, decides nothing).

Q1: Is the bounded rule's win over the status quo the cap or the 4-ticket limit?
Q2: Do caps above 50% (the sweep's top) slide back toward the status quo?
Q3: Under the composite, where does the win come from (floor / equality / average),
    and is scalper utility setting the max?

Paired seeds across arms. Scorings S0 (model) and S2 (individual), via rescore_check.
Run from the Ticket Fairness repo:  /usr/local/bin/python3 <this file>
"""
import random
import statistics as st
import sys

sys.path.insert(0, ".")
from gre_sim import DEFAULT_GR_W, DEFAULT_UTILITY_W, FAN_TYPES, Rule, simulate  # noqa: E402
from rescore_check import fan_type_utility, lenses  # noqa: E402

ARMS = [
    Rule("Status quo (no cap, limit 8)", None, 8, None),
    Rule("No cap, limit 4", None, 4, None),
    Rule("Cap 50%, limit 8", 0.50, 8, None),
    Rule("Cap 20%, limit 4", 0.20, 4, None),
    Rule("Cap 50%, limit 4", 0.50, 4, None),
    Rule("Cap 100%, limit 4", 1.00, 4, None),
    Rule("Cap 200%, limit 4", 2.00, 4, None),
]
DEMANDS = [1.5, 2, 3, 5, 8]
N = 60
gw = DEFAULT_GR_W

print(f"N={N} paired seeds per cell\n")
for d in DEMANDS:
    print(f"=== demand {d}x ===")
    print(f"{'arm':30s} {'S0 pop':>7s} {'S2 pop':>7s} {'S2 sys':>7s} {'S2 fan':>7s} | "
          f"{'floor':>6s} {'equal':>6s} {'avg':>6s} {'max type':>9s} | "
          f"{'mega acc':>8s} {'cas+avg acc':>11s} {'mega u':>6s} {'cas u':>6s} {'scalp u':>7s} {'seats':>5s}")
    for rule in ARMS:
        acc = {k: [] for k in ("s0p", "s2p", "s2s", "s2f", "fl", "eq", "av", "mega_acc", "low_acc",
                               "mega_u", "cas_u", "sc_u", "seats")}
        maxtypes = []
        for s in range(N):
            seed = 91_000_000 + int(d * 1000) * 1000 + s
            random.seed(seed)
            res = simulate(rule, d, return_agents=True)
            L = lenses(res, rule, check=True)
            acc["s0p"].append(L["S0"]["pop_wt"]); acc["s2p"].append(L["S2"]["pop_wt"])
            acc["s2s"].append(L["S2"]["system"]); acc["s2f"].append(L["S2"]["fan_only"])
            agents = res["agents"]
            types = list(res["outcomes"].keys())
            groups = {t: [a for a in agents if a.type == t] for t in types}
            u = {t: (res["outcomes"][t]["utility"] if t not in FAN_TYPES
                     else fan_type_utility(groups[t], res, rule, DEFAULT_UTILITY_W, "S2")) for t in types}
            vals = [u[t] for t in types for _ in range(len(groups[t]))]
            mn, mx, av = min(vals), max(vals), sum(vals) / len(vals)
            acc["fl"].append(mn * gw["floor"]); acc["eq"].append((1 - (mx - mn)) * gw["equality"])
            acc["av"].append(av * gw["average"])
            maxtypes.append(max(types, key=lambda t: u[t]))
            o = res["outcomes"]
            acc["mega_acc"].append(o["mega_fan"]["got"] / o["mega_fan"]["total"])
            acc["low_acc"].append((o["committed_casual"]["got"] + o["average_buyer"]["got"])
                                  / (o["committed_casual"]["total"] + o["average_buyer"]["total"]))
            acc["mega_u"].append(u["mega_fan"]); acc["cas_u"].append(u["committed_casual"])
            acc["sc_u"].append(u["scalper"])
            acc["seats"].append(res.get("attend", float("nan")))
        m = {k: st.mean(v) for k, v in acc.items()}
        top = max(set(maxtypes), key=maxtypes.count)
        print(f"{rule.name:30s} {m['s0p']:7.3f} {m['s2p']:7.3f} {m['s2s']:7.3f} {m['s2f']:7.3f} | "
              f"{m['fl']:6.3f} {m['eq']:6.3f} {m['av']:6.3f} {top:>9.9s} | "
              f"{m['mega_acc']:8.0%} {m['low_acc']:11.1%} {m['mega_u']:6.3f} {m['cas_u']:6.3f} "
              f"{m['sc_u']:7.3f} {m['seats']:5.0f}")
    print()
    sys.stdout.flush()
