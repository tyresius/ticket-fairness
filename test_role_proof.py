"""Checks that must pass before any role-proof result is read (ROLE_PROOF_TEST.md).

Run:  python3 -m unittest test_role_proof -v
The fourth check in the design (the full cap sweep reproduces the stored CSVs)
is a separate run: re-run cap_sweep.py on a copy and compare the files.
"""
import random
import unittest

from gre_sim import FAN_TYPES, simulate
from gre_sim import FACE
from role_proof import KAPPAS, PRICE_FORMS, agent_utility, menu_rules, price_score

DEMANDS = (1, 3, 5, 10)
SEED = 20261103


def strip(res):
    return {k: v for k, v in res.items()
            if k not in ("agents", "listings", "continuation_rule", "sale_price", "secondary_fee_seller",
                         "secondary_fee_buyer", "dark_fraud_penalty", "systemic_penalty")}


class SameRuleSwitchIsANoOp(unittest.TestCase):
    """Switching to the same rule, or asking for agents, changes nothing."""

    def test_identical_results(self):
        for R in menu_rules():
            for d in DEMANDS:
                random.seed(SEED)
                base = simulate(R, d)
                random.seed(SEED)
                same = simulate(R, d, continuation_rule=R)
                random.seed(SEED)
                with_agents = simulate(R, d, return_agents=True)
                self.assertEqual(base, same, f"{R.name} @ {d}: same-rule switch changed results")
                self.assertEqual(base, strip(with_agents), f"{R.name} @ {d}: return_agents changed results")


class PrimaryAllocationIsFixed(unittest.TestCase):
    """For one seed and primary rule, every continuation starts from the same allocation."""

    def test_allocation_identical_across_continuations(self):
        rules = menu_rules()
        for R in rules:
            for d in DEMANDS:
                snapshots = []
                for X in rules:
                    random.seed(SEED)
                    res = simulate(R, d, continuation_rule=X, return_agents=True)
                    snapshots.append(sorted(
                        (a.id, a.primary_holder, a.cost_basis if a.primary_holder else 0.0,
                         a.tickets if a.primary_holder else 0)
                        for a in res["agents"]))
                for snap in snapshots[1:]:
                    self.assertEqual(snapshots[0], snap,
                                     f"{R.name} @ {d}: allocation differs across continuations")


class PerAgentScoresAreBounded(unittest.TestCase):
    """Every per-agent score lies in [0, 1], at every kappa."""

    def test_bounds(self):
        rules = menu_rules()
        for R in rules:
            for X in (rules[0], rules[1], R):
                for d in DEMANDS:
                    random.seed(SEED)
                    res = simulate(R, d, continuation_rule=X, return_agents=True)
                    for a in res["agents"]:
                        if a.type not in FAN_TYPES:
                            continue
                        for k in KAPPAS:
                            for pr in (False, True):
                                u = agent_utility(a, res, k, pr)
                                self.assertGreaterEqual(u, 0.0)
                                self.assertLessEqual(u, 1.0,
                                                     f"{R.name}->{X.name} @ {d}, kappa {k}, proceeds {pr}: {u}")


class ProceedsOnlyChangeSellers(unittest.TestCase):
    """The proceeds variant changes the score only for fans who actually sold."""

    def test_non_sellers_unchanged(self):
        rules = menu_rules()
        for R in rules:
            for d in DEMANDS:
                random.seed(SEED)
                res = simulate(R, d, return_agents=True)
                sellers = {li.seller.id for li in res["listings"] if li.sold}
                for a in res["agents"]:
                    if a.type in FAN_TYPES and a.id not in sellers:
                        self.assertEqual(agent_utility(a, res, 0.0, False),
                                         agent_utility(a, res, 0.0, True),
                                         f"{R.name} @ {d}: {a.id} changed without selling")



class PriceFormsBehaveAsDefined(unittest.TestCase):
    """PRICE_SCORE_CHECK.md harness 3: the price forms do what the design says."""

    def test_formula_points(self):
        for wtp in (1.6, 1.8, 4.0):
            self.assertEqual(price_score(FACE, wtp, "saturating"), 1.0)
            self.assertEqual(price_score(FACE, wtp, "linear"), 1.0)
            self.assertAlmostEqual(price_score(FACE, wtp, "surplus"), 1.0, places=12)
            self.assertAlmostEqual(price_score(wtp * FACE, wtp, "surplus"), 0.0, places=12)
        self.assertEqual(price_score(3 * FACE, 4.0, "saturating"), 0.0)
        self.assertAlmostEqual(price_score(3 * FACE, 4.0, "linear"), -1.0, places=12)
        for paid in (0.0, -1.0):
            for f in PRICE_FORMS:
                self.assertEqual(price_score(paid, 4.0, f), 0.0)
        # resented surcharge under saturating matches gre_sim.py:745-748
        for paid in (100, 130, 190, 250):
            r = (paid - FACE) / FACE
            for resent in (0.05, 0.3, 0.9):
                self.assertEqual(price_score(paid, 4.0, "saturating", resent),
                                 max(0.0, max(0.0, 1 - r) - resent))

    def test_on_simulated_agents(self):
        rules = menu_rules()
        for R in rules:
            for d in DEMANDS:
                random.seed(SEED)
                res = simulate(R, d, return_agents=True)
                for a in res["agents"]:
                    if a.type not in FAN_TYPES:
                        continue
                    base = agent_utility(a, res, 0.0, False)
                    # P0 is the old scoring, bit for bit
                    self.assertEqual(base, agent_utility(a, res, 0.0, False, price_form="saturating"))
                    paid = a.secondary_price * (1 + res["secondary_fee_buyer"]) \
                        if a.phase == "bought_secondary" else (a.secondary_price or a.cost_basis or 0)
                    lin = agent_utility(a, res, 0.0, False, price_form="linear")
                    if paid <= 2 * FACE:
                        self.assertEqual(base, lin, f"{R.name} @ {d}: P1 differs below 2x face")
                    else:
                        self.assertLessEqual(lin, base)
                    for f in PRICE_FORMS:
                        for k in KAPPAS:
                            u = agent_utility(a, res, k, False, price_form=f)
                            self.assertGreaterEqual(u, 0.0)
                            self.assertLessEqual(u, 1.0, f"{R.name} @ {d} {f} kappa {k}: {u}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
