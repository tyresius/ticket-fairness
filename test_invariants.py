#!/usr/bin/env python3
"""
Invariant test suite for the GRE simulation core.
==================================================
Run BEFORE trusting any sweep:  /usr/local/bin/python3 test_invariants.py

Rationale: the gre_sim.py changelog documents six-plus bugs (A1-A6, B1)
found by laborious manual audit that mechanical invariants would have
caught for free. This suite encodes the properties every simulate() call
must satisfy, plus regression tests for specific audited fixes. Stdlib
only — no third-party dependencies.
"""

import copy
import random
import unittest

from gre_sim import simulate, Rule, DEFS, VENUE, FACE, FAN_TYPES

RULES = {
    "status_quo": Rule("Status Quo",      cap=None, plimit=8, dyn_mul=None),
    "dynamic":    Rule("Dynamic Pricing", cap=None, plimit=6, dyn_mul=2.2),
    "uk_face":    Rule("UK Face Value",   cap=0.0,  plimit=2, dyn_mul=None),
    "bounded0":   Rule("Bounded 0%",      cap=0.0,  plimit=4, dyn_mul=None),
    "bounded20":  Rule("Bounded 20%",     cap=0.20, plimit=4, dyn_mul=None),
    "bounded50":  Rule("Bounded 50%",     cap=0.50, plimit=4, dyn_mul=None),
}
MULS = [1, 1.5, 3, 10]

LENS_KEYS = ["system", "fan_only", "pop_wt", "ex_ante_fan", "ex_ante_popwt",
             "rawls_fan", "rawls_all", "rawls_ea_fan",
             "harsanyi_eq_fan", "harsanyi_eq_all",
             "harsanyi_pop_all", "harsanyi_pop_fan"]


class GridInvariants(unittest.TestCase):
    """Properties that must hold for every (rule, demand) cell."""

    @classmethod
    def setUpClass(cls):
        random.seed(1234)
        cls.grid = {}
        for rid, rule in RULES.items():
            for mul in MULS:
                cls.grid[(rid, mul)] = simulate(rule, mul)

    def test_lens_scores_in_unit_interval(self):
        for key, r in self.grid.items():
            for lens in LENS_KEYS:
                self.assertGreaterEqual(r[lens], 0.0, f"{key} {lens}")
                self.assertLessEqual(r[lens], 1.0, f"{key} {lens}")

    def test_agent_outcomes_bounded_and_consistent(self):
        for key, r in self.grid.items():
            for tid, o in r["outcomes"].items():
                self.assertGreaterEqual(o["utility"], 0.0, f"{key} {tid}")
                self.assertLessEqual(o["utility"], 1.0, f"{key} {tid}")
                self.assertGreaterEqual(o["ex_ante"], 0.0, f"{key} {tid}")
                self.assertLessEqual(o["ex_ante"], 1.0, f"{key} {tid}")
                self.assertLessEqual(o["got"], o["total"], f"{key} {tid}")
                self.assertLessEqual(o["att"], o["total"], f"{key} {tid}")
                self.assertGreaterEqual(o["avg_price"], 0, f"{key} {tid}")

    def test_ticket_conservation(self):
        for key, r in self.grid.items():
            self.assertLessEqual(r["primary_sold"], VENUE, key)
            self.assertLessEqual(r["attend"], VENUE, key)
            self.assertGreaterEqual(r["wasted"], 0, key)
            # Every secondary/dark sale consumes a distinct primary ticket.
            self.assertLessEqual(r["secondary_sold"] + r["dark_sold"],
                                 r["primary_sold"], key)

    def test_uncapped_rules_have_no_dark_market(self):
        for (rid, mul), r in self.grid.items():
            if RULES[rid].cap is None:
                self.assertEqual(r["dark_sold"], 0, (rid, mul))
                self.assertEqual(r["dark_unmatched"], 0, (rid, mul))
                self.assertEqual(r["dark_prevalence"], 0.0, (rid, mul))

    def test_high_demand_sells_out_primary(self):
        for (rid, mul), r in self.grid.items():
            if mul >= 3:
                self.assertEqual(r["primary_sold"], VENUE, (rid, mul))


class Determinism(unittest.TestCase):
    def test_same_seed_bitwise_identical(self):
        random.seed(777)
        a = simulate(RULES["bounded20"], 3)
        random.seed(777)
        b = simulate(RULES["bounded20"], 3)
        self.assertEqual(a, b)

    def test_different_seed_differs(self):
        random.seed(1)
        a = simulate(RULES["bounded20"], 3)
        random.seed(2)
        b = simulate(RULES["bounded20"], 3)
        self.assertNotEqual(a, b)


class ExAnteZeroAccessFloor(unittest.TestCase):
    """E1-followup: a fan type with ZERO access must have ex-ante utility
    equal to the missed-utility floor (0.02) — the expected utility of a
    position that never gets a ticket — not the 0.0 initializer.

    Construction: average_buyer with max_pay_mul=0.01 can afford nothing
    (primary at FACE, secondary floored at FACE, dark requires WTP above
    the cap ceiling), guaranteeing got == 0."""

    def test_ex_ante_equals_missed_floor_when_no_access(self):
        defs = copy.deepcopy(DEFS)
        defs["average_buyer"]["max_pay_mul"] = 0.01
        random.seed(42)
        r = simulate(RULES["bounded20"], 3, defs)
        o = r["outcomes"]["average_buyer"]
        self.assertEqual(o["got"], 0)
        self.assertEqual(o["utility"], 0.02)
        self.assertEqual(o["ex_ante"], 0.02,
                         "zero-access ex-ante must equal the 0.02 missed floor")


if __name__ == "__main__":
    unittest.main(verbosity=2)
