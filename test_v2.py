"""Regression tests for model v2 mechanics (V2_PREREGISTRATION.md, M1-M4).

Run:  python3 -m unittest test_v2 -v
These check mechanics only; they print no policy results.
"""
import random
import unittest

from gre_sim import (FACE, FAN_TYPES, SCALPER_DARK_COST, Rule, dark_routing,
                     expected_scalper_margin, simulate, v2_dark_reservation,
                     v2_expected_dark_price)

FEE = dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)
CAPS = (0.0, 0.2, 0.3)
SEEDS = range(6)


def runs(demands, caps=CAPS, **kw):
    for c in caps:
        for d in demands:
            for s in SEEDS:
                random.seed(31_000 + s)
                yield c, d, simulate(Rule("t", c, 4, None), d, return_agents=True, mechanics="v2", **FEE, **kw)


class DarkMarketClears(unittest.TestCase):
    """M1: every dark sale lies between the reservation and the buyer's limit, at the
    midpoint; dark tickets sell at high demand when eligible buyers exist."""

    def test_prices_and_sales(self):
        r = v2_dark_reservation(FACE, SCALPER_DARK_COST)
        sold_high = 0
        for c, d, res in runs((3, 5, 7, 10)):
            for a in res["agents"]:
                if a.dark_market:
                    limit = a.def_["max_pay_mul"] * FACE
                    self.assertGreaterEqual(limit, r)
                    self.assertEqual(a.secondary_price, round((r + limit) / 2))
                    self.assertLessEqual(a.secondary_price, limit)
            if d >= 7:
                sold_high += res["dark_sold"]
        self.assertGreater(sold_high, 0, "v2 dark market should clear at high demand")

    def test_expected_price(self):
        self.assertAlmostEqual(v2_expected_dark_price(100, 0.45, 400), (100 / 0.55 + 400) / 2)
        self.assertAlmostEqual(v2_expected_dark_price(100, 0.45, 150), 100 / 0.55)   # no buyer can pay
        m1 = expected_scalper_margin(Rule("t", 0.2, 4, None), 7, mechanics="v1")
        m2 = expected_scalper_margin(Rule("t", 0.2, 4, None), 7, mechanics="v2", top_wtp=400)
        self.assertNotEqual(m1, m2)


class RoutingUsesNetPlatformPrice(unittest.TestCase):
    """M2: v2 compares net dark revenue with the platform price NET of the seller fee."""

    def test_net_vs_gross(self):
        # Dark net 115 vs ask 120: v1 (gross) does not consider dark; v2 (net 114) does.
        c1, p1 = dark_routing(115, 120, 0.05, 0.5, 1.5, "v1")
        c2, p2 = dark_routing(115, 120, 0.05, 0.5, 1.5, "v2")
        self.assertFalse(c1)
        self.assertTrue(c2)
        self.assertGreater(p2, 0)
        # v2 gap uses the net price
        expected = 0.5 * (((115 - 114) / 115) ** 1.5)
        self.assertAlmostEqual(p2, expected)


class BuyersAffordAllIn(unittest.TestCase):
    """M3: no lawful resale buyer pays more than their limit, including the buyer fee."""

    def test_all_in_within_limit(self):
        for c, d, res in runs((1.5, 3, 5, 10), caps=(0.0, 0.2, 0.3, None)):
            fee = res["secondary_fee_buyer"]
            for a in res["agents"]:
                if a.phase == "bought_secondary":
                    self.assertLessEqual(a.secondary_price * (1 + fee),
                                         a.def_["max_pay_mul"] * FACE + 1e-9)


class FansMayResellBelowFace(unittest.TestCase):
    """M4: under v2 unsold fan listings are marked down below face; under v1 the
    face-value floor stops them. Checked at 0.5x demand (surplus tickets): from 1x
    up, scalpers absorb enough primary stock that fan listings sell at face in
    round 1, so the floor never binds in the policy experiments."""

    def below_face_listings(self, mechanics):
        n = 0
        for s in range(30):
            random.seed(55_000 + s)
            res = simulate(Rule("t", 0.0, 4, None), 0.5, return_agents=True, mechanics=mechanics, **FEE)
            n += sum(1 for li in res["listings"] if not li.is_scalper and li.final_price < FACE)
        return n

    def test_floor_removed(self):
        self.assertEqual(self.below_face_listings("v1"), 0)
        self.assertGreater(self.below_face_listings("v2"), 0)


class MechanicsValidated(unittest.TestCase):
    def test_bad_value(self):
        with self.assertRaises(ValueError):
            simulate(Rule("t", 0.2, 4, None), 2, mechanics="v3")


if __name__ == "__main__":
    unittest.main(verbosity=2)
