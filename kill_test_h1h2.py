"""Kill tests for the revised brief's H1 and H2 (/validate-claim, 9 Nov 2026). Exploratory.

K1: score with the resale-option term removed (weight 0, other weights renormalised).
    The term is assigned by formula from the cap level (role_proof.resale_option), so it
    could mechanically favour positive ceilings.
K2: 20% and 30% ceilings (with fee cap) against a tougher face-value arm: 2-ticket limit
    and dark cost 0.65, with the same fee cap (as RESCORE_CHECK C5, which only tested 10%).

300 paired seeds per demand level; mean individual fan utility under P0/P1/P2; 95% CIs.
Run from the Ticket Fairness repo:  /usr/local/bin/python3 kill_test_h1h2.py
"""
import math
import random
import statistics as st

from gre_sim import DEFAULT_UTILITY_W, Rule, simulate
from price_check import score_run

FEE = dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)
ARMS = {
    "0%+fee":       (Rule("Bounded 0% + fee cap", 0.0, 4, None), FEE),
    "0%+fee tough": (Rule("Face value + fee cap, tough", 0.0, 2, None), dict(FEE, scalper_dark_cost=0.65)),
    "20%":          (Rule("Bounded 20%", 0.20, 4, None), {}),
    "20%+fee":      (Rule("Bounded 20% + fee cap", 0.20, 4, None), FEE),
    "30%+fee":      (Rule("Bounded 30% + fee cap", 0.30, 4, None), FEE),
}
LEVELS = [1.5, 2, 3, 4, 5, 6, 7, 8, 10]
FORMS = (("P0", "saturating"), ("P1", "linear"), ("P2", "surplus"))
N = 300
w = {k: v for k, v in DEFAULT_UTILITY_W.items() if k != "resale_opt"}
NO_RESALE_W = {k: v / sum(w.values()) for k, v in w.items()}
NO_RESALE_W["resale_opt"] = 0.0

vals = {}
for i, d in enumerate(LEVELS):
    for s in range(N):
        seed = 77_700_000 + 10_000 * i + s
        for arm, (rule, kw) in ARMS.items():
            random.seed(seed)
            r = simulate(rule, d, return_agents=True, **kw)
            for wlab, uw in (("default", DEFAULT_UTILITY_W), ("no resale term", NO_RESALE_W)):
                sc = score_run(r, rule, uw=uw)
                for code, form in FORMS:
                    vals.setdefault((arm, d, wlab, code), []).append(sc[form]["fan_mean"])

TESTS = [
    ("K1  H1: 20%+fee minus 0%+fee", "20%+fee", "0%+fee", "no resale term"),
    ("K1  H1: 30%+fee minus 0%+fee", "30%+fee", "0%+fee", "no resale term"),
    ("K1  H2: 20% (no fee cap) minus 0%+fee", "20%", "0%+fee", "no resale term"),
    ("K2  20%+fee minus tough face value", "20%+fee", "0%+fee tough", "default"),
    ("K2  30%+fee minus tough face value", "30%+fee", "0%+fee tough", "default"),
    ("ref H1: 20%+fee minus 0%+fee (default weights)", "20%+fee", "0%+fee", "default"),
    ("ref H2: 20% minus 0%+fee (default weights)", "20%", "0%+fee", "default"),
]
for label, a, b, wlab in TESTS:
    print(f"\n{label} [{wlab}] -- mean fan utility: mean [95% CI]  '*' > 0, '!' < 0")
    for code, _ in FORMS:
        cells = []
        for d in LEVELS:
            x = [p - q for p, q in zip(vals[(a, d, wlab, code)], vals[(b, d, wlab, code)])]
            m, sd = st.mean(x), st.stdev(x)
            h = 1.96 * sd / math.sqrt(len(x))
            flag = "*" if m - h > 0 else ("!" if m + h < 0 else " ")
            cells.append(f"{d:g}x {m:+.4f}[{m - h:+.4f},{m + h:+.4f}]{flag}")
        print(f"  {code}: " + "  ".join(cells))
