"""
GRE Ticket Market Simulation — Canonical Core
=============================================

Single source of truth for the Golden Rule Equilibrium market simulation.
Imported by cap_sweep.py and weight_discovery.py. All simulation logic changes
should happen here.

History:
  - 2026-04-21: Consolidated from cap_sweep.py, weight_discovery.py, and
    gre-scarcity-curves.jsx (JSX deprecated, no longer synced).
  - Bugfix: dark market phase now checks buyer affordability.
  - Bugfix: unmatched dark-supply tickets now tracked via dark_unmatched and
    counted in `wasted`.
  - Sync: weight_discovery's internal simulate() removed — calls this now.
  - Option A (unified scalper branches): sub-5% dump/waste branch deleted.
    All capped regimes use the same demand-sensitive ask + dark routing.
  - Enforcement & nonlinear leakage (combined pass):
      * SCALPER_DARK_COST now applied to realized dark revenue, not just the
        routing decision (previously the scalper received the full dark_price
        and the enforcement friction only nudged the routing probability).
      * DARK_LEAKAGE scales nonlinearly with the incentive gap
        (gap ** DARK_LEAKAGE_GAMMA) to match the empirical observation that
        black-market share rises sharply as caps tighten — a linear formula
        produced too-flat a leakage curve across the cap spectrum.
    Source calibration: the 0.35 base / 1.5 gamma / 0.45 enforced-cost values
    are placeholders directionally consistent with Ireland / Victoria / UK
    contrasts, but the specific fraud-rate figures circulating in secondary
    reporting need verifiable primary sources before publication use.
  - 2026-04-27: Phase 1 audit fixes (A2, A4, A6):
      * A2: expected_dark in expected_scalper_margin() corrected from
        FACE×(1+0.5×mul) to FACE×(1+0.65×mul) to match mean of realized dark
        price formula. Previous value caused ~30% underestimation of dark
        revenue, artificially suppressing scalper participation and over-stating
        cap advantage at tight caps.
      * A4: resale_opt replaced from a three-step function with a continuous
        linear function: min(0.70, 0.20 + cap×2.0). Eliminates the arbitrary
        0.4→0.6 jump at cap=15% that structurally favored caps ≥ 15% by ~0.06
        utility units. New formula is monotone, continuously differentiable,
        and grounded in expected resale economics (each 1% cap ≈ $1 upside on
        a $100 face-value ticket; saturates at 0.70 = uncapped value at cap≥25%).
      * A6: binary listing probability at cap==0 replaced with a continuous
        function: p_list = min(1.0, 0.5 + cap×5.0). Eliminates the sharp
        behavioral discontinuity between cap=0% and cap=5% that made Bounded 0%
        look artificially worse than Bounded 5%.
"""

import math
import random
from dataclasses import dataclass
from typing import Optional

# ── Market constants ──────────────────────────────────────────────────────────
VENUE = 500
FACE  = 100

BASE_POP = dict(mega_fan=80, committed_casual=150, average_buyer=200, scalper=30)

# Dark market leakage
# leakage probability = DARK_LEAKAGE_BASE * incentive_gap ** DARK_LEAKAGE_GAMMA
# Nonlinear (gamma > 1) so extreme cap tightness produces disproportionately
# more leakage — matches directional empirical evidence that black-market share
# rises sharply as the legal-vs-clearing gap widens rather than linearly.
DARK_LEAKAGE_BASE  = 0.35
DARK_LEAKAGE_GAMMA = 1.5

# B1 fix (2026-04-28): baseline secondary-market fraud penalty for uncapped regimes.
# Status Quo and Dynamic Pricing gave fans a free pass on fraud — zero modeled.
# Empirical anchor: UK uncapped market shows 3.8% fraud rate (Bradshaw Advisory,
# June 2025). Applied as a utility deduction to secondary buyers in uncapped
# regimes, proportional to their secondary purchase fraction. Uses a penalty
# of 0.07 (≈ 28% of DARK_FRAUD_PENALTY, matching the 3.8%/13.6% fraud ratio
# between uncapped and capped markets).
BASELINE_SECONDARY_FRAUD_PENALTY = 0.07

# Enforcement mechanism (added 2026-04-21): capped regimes require an identity
# registry and non-transferable barcodes to be credible. Enforcement imposes
# real costs on both sides of a dark-market transaction:
#   - scalper: chargebacks, meetup walkaway, time cost, and the risk that a
#     non-transferable ticket won't scan at the gate (no payment recourse)
#   - buyer:   same non-scan risk on top of baseline fraud risk
#
# Applied whenever rule.cap is not None (our capped rulesets — Bounded and
# UK Face Value — all assume the enforcement package). Uncapped rulesets
# (Status Quo, Dynamic Pricing) don't activate the dark market at all.
SCALPER_DARK_COST  = 0.45   # fraction of nominal dark revenue lost to enforcement friction
DARK_FRAUD_PENALTY = 0.25   # buyer utility deduction under enforcement (was 0.15 pre-enforcement)

# Secondary-market platform fees (added 2026-06-03).
# Real regulated resale platforms charge fees on BOTH sides of a transaction.
# Empirical anchor: GAO-18-347 and follow-on reporting put combined primary+
# secondary fees around 27–31% of face; the secondary leg alone is ~25–30%
# split roughly evenly between a buyer service fee and a seller listing/payout
# fee. We model ~15% per side (≈30% combined), applied ONLY to legal on-platform
# resale (capped regimes' platform listings + uncapped secondary listings).
#
# Why this matters for the cap question:
#   - SELLER fee reduces a reseller's NET proceeds. At a 0% cap a seller lists at
#     face ($100) and nets ~$85 — a guaranteed loss on a $100 ticket. No rational
#     fan lists, so the "cheap legal secondary market" a face-value cap is
#     supposed to create cannot actually exist; supply wastes or routes dark.
#     A POSITIVE cap is therefore the minimum for a functional legal resale
#     market: the ceiling must clear the fee load before resale breaks even.
#     With ~15% seller fee, break-even is at cap ≈ 0.15/0.85 ≈ 17.6%, which is
#     why the defensible cap band (≈15–25%) falls out of the fee structure
#     rather than being tuned to a target.
#   - BUYER fee raises the price a secondary buyer actually pays above the
#     listed/ticket price, worsening their price_score. This is real money fans
#     lose that the face-value-only framing ignores.
#
# The dark market dodges BOTH fees (cash, off-platform) — which is part of why a
# punitively tight cap pushes volume dark: the legal channel is not just capped,
# it is fee-laden and loss-making, while the dark channel is fee-free.
SECONDARY_FEE_SELLER = 0.15  # seller-side fee: fraction of sale price withheld from net proceeds
SECONDARY_FEE_BUYER  = 0.15  # buyer-side fee: fraction added on top of price the buyer pays

# Systemic dark-market harm (added 2026-05-30 audit).
# DARK_FRAUD_PENALTY above is a PRIVATE cost: it hits only the buyer who
# knowingly transacts in the dark market. But a prevalent dark market imposes a
# NEGATIVE EXTERNALITY on the whole fan population — counterfeit tickets
# circulate, gate-scan failures and chargeback disputes rise, and trust in the
# resale channel erodes for everyone, including fans who bought through
# nominally legitimate channels. This is why a 0% cap (which maximizes dark-
# market prevalence) is socially worse than its private dark-buyer harm alone
# suggests.
#
# Mechanism: every fan (legit or dark) takes a utility deduction proportional
# to the realized dark-market prevalence in their market:
#     systemic_fraud = min(SYSTEMIC_FRAUD_CAP, DARK_SYSTEMIC_K * dark_prevalence)
#     dark_prevalence = dark_sold / VENUE   ← NOTE: this denominator is the
#       source of the calibration failure documented below; see status note.
# where the deduction is systemic_fraud * SYSTEMIC_FRAUD_WEIGHT.
#
# CALIBRATION STATUS (2026-05-31): UNRESOLVED — DO NOT CITE A FIT.
# An attempt to calibrate DARK_SYSTEMIC_K against the Ireland (13.6%), Victoria
# (13.7%), and UK (3.8%) fraud anchors FAILED: with dark_prevalence defined as
# dark_sold/VENUE, the model's dark channel is too small (≈1–2% of capacity) to
# generate market-wide fraud anywhere near 13.6% at any K — it tops out near
# ~0.8% under transaction weighting. The mismatch is a UNITS problem: Ireland's
# 13.6% is fraud PER SECONDARY TRANSACTION, whereas dark_sold/VENUE is dark
# tickets per total seats. These are not the same denominator. Matching the
# anchor requires either (a) redefining prevalence as dark_sold/(secondary_sold
# + dark_sold), or (b) revisiting whether DARK_LEAKAGE_BASE understates the dark
# channel's size. Until that is resolved, the value below is a PLACEHOLDER and
# its effect on the optimum has not been validated against data.
DARK_SYSTEMIC_K      = 1.75  # PLACEHOLDER — not calibrated; see status note above
SYSTEMIC_FRAUD_CAP   = 0.20  # ceiling on modeled market-wide fraud rate
# DISABLED IN BASELINE (2026-06-03): the systemic-harm externality never
# calibrated (units mismatch documented above) and the audit flagged it as a
# broken component. Rather than let an unvalidated term contaminate the headline
# results, its baseline weight is set to 0.0 — the externality is OFF by default.
# The kwarg remains live so sensitivity_sweep.py can still probe "what if it were
# active," but the cap-sweep / rawls / enforcement / global headline numbers no
# longer depend on it. The real fee mechanism (SECONDARY_FEE_*) now carries the
# economic argument that the systemic-harm hack was reaching for. Re-enable only
# after resolving the dark_prevalence denominator and recalibrating to data.
SYSTEMIC_FRAUD_WEIGHT= 0.0   # 0.0 = externality disabled in baseline (was 1.0, uncalibrated)

# Saturation point where exp_margin hits full cap value
SATURATION_DEMAND = 2.0

# Endogenous scalper exit (added 2026-04-22)
# Professional scalpers carry operational overhead (bots, proxies, labor,
# chargeback risk) that requires a nontrivial expected margin to break even.
# At zero on-platform margin with no viable dark routing (e.g. cap=0 at low
# demand), participation is not economic and the population contracts.
#
# Mechanism: compute an ex-ante expected per-ticket margin given (rule, mul),
# then scale pop["scalper"] by a sigmoid on that margin. A floor keeps a
# residual scalper population to model those who mis-estimate or accept
# sub-break-even margins for other reasons (access, bundling, arbitrage on
# the long tail of events).
SCALPER_EXIT_FLOOR       = 0.20  # minimum fraction of baseline scalper pop
SCALPER_EXIT_MIDPOINT    = 0.20  # margin at which pop_mul = floor + 0.4
SCALPER_EXIT_STEEPNESS   = 0.08  # sigmoid scale; smaller = sharper transition


# ── Empirical agent calibration (NITO / CMA / Stanford) ──────────────────────
# - mega_fan WTP at 4x (superfan empirical 4–6x; abandonment above 6x)
# - flip_margin_threshold raised across all fans (endowment buffer ~40%; 2.5x step)
# - resale_effort_threshold raised (fans prefer gifting below 30–40% premium)
# - plan_change_rate aligned with 8% empirical no-show baseline
DEFS = {
    "mega_fan":         dict(speed=0.85, max_pay_mul=4.0, attend_base=0.95, wanted=2,
                             flip_chance=0.02, plan_change_rate=0.08,
                             resale_effort_threshold=0.0,  flip_margin_threshold=0.75),
    "committed_casual": dict(speed=0.35, max_pay_mul=1.8, attend_base=0.78, wanted=2,
                             flip_chance=0.08, plan_change_rate=0.10,
                             resale_effort_threshold=0.30, flip_margin_threshold=0.40),
    "average_buyer":    dict(speed=0.30, max_pay_mul=1.6, attend_base=0.55, wanted=3,
                             flip_chance=0.20, plan_change_rate=0.12,
                             resale_effort_threshold=0.25, flip_margin_threshold=0.35),
    "scalper":          dict(speed=0.95, max_pay_mul=3.0, attend_base=0.01, wanted=8,
                             flip_chance=1.0,  plan_change_rate=0.00,
                             resale_effort_threshold=0.0,  flip_margin_threshold=0.0),
}

FAN_TYPES = ["mega_fan", "committed_casual", "average_buyer"]


# ── Dataclasses ──────────────────────────────────────────────────────────────
@dataclass
class Rule:
    name:    str
    cap:     Optional[float]   # None = no cap; 0.0 = face value only
    plimit:  int
    dyn_mul: Optional[float]   # None = face value primary; 2.2 = dynamic pricing


@dataclass
class Agent:
    type:             str
    def_:             dict
    tickets:          int   = 0
    cost_basis:       float = 0.0
    phase:            str   = "waiting"
    resale_tickets:   int   = 0
    wasted_tickets:   int   = 0
    attending:        bool  = False
    secondary_price:  float = 0.0
    dark_market:      bool  = False
    id:               str   = ""


@dataclass
class Listing:
    seller:      Agent
    ask:         float
    is_scalper:  bool
    sold:        bool  = False
    final_price: float = 0.0


# ── Scalper entry/exit helpers ───────────────────────────────────────────────
def expected_scalper_margin(rule: "Rule", mul: float,
                             dark_leakage_base:  float = DARK_LEAKAGE_BASE,
                             dark_leakage_gamma: float = DARK_LEAKAGE_GAMMA,
                             scalper_dark_cost:  float = SCALPER_DARK_COST,
                             secondary_fee_seller: float = SECONDARY_FEE_SELLER) -> float:
    """
    Ex-ante expected margin per ticket for a scalper given ruleset and demand.
    Mirrors the pricing + leakage logic inside simulate() without sampling.
    Returns a fraction (e.g. 0.25 = 25% margin over FACE).

    Fees (2026-06-03): legal on-platform resale nets the seller fee
    (platform_net = ask × (1 − fee_seller)); the dark channel dodges the platform
    fee but pays enforcement friction (scalper_dark_cost). So the fee both thins
    legal scalping margins at every cap AND makes the dark channel relatively more
    attractive — a second reason tight caps push volume off-platform.
    """
    if rule.cap is None:
        # Uncapped legal resale also pays the platform seller fee.
        expected_ask = FACE * (1 + 0.65 * mul)
        blended = expected_ask * (1 - secondary_fee_seller)
    else:
        # A2 fix (2026-04-27): align with the mean of the realized dark price
        # formula (FACE × (1 + 0.5×mul + rand×mul×0.3)); mean random term = 0.15×mul
        # so mean realized = FACE × (1 + 0.65×mul). Previous 0.5×mul caused scalpers
        # to systematically underestimate dark revenue by ~30%, over-exiting and
        # under-routing — which overstated the cap advantage at tight caps.
        platform_net      = FACE * (1 + rule.cap) * (1 - secondary_fee_seller)
        expected_dark     = FACE * (1 + 0.65 * mul)
        expected_dark_net = expected_dark * (1 - scalper_dark_cost)

        if expected_dark_net > platform_net:
            gap       = (expected_dark_net - platform_net) / expected_dark_net
            leakage_p = dark_leakage_base * (gap ** dark_leakage_gamma)
            blended   = (1 - leakage_p) * platform_net + leakage_p * expected_dark_net
        else:
            blended = platform_net

    sell_through = max(0.1, min(1.0, (mul - 0.8) / 0.7))
    nominal_margin = (blended - FACE) / FACE
    return nominal_margin * sell_through


def scalper_pop_multiplier(expected_margin: float,
                            floor:    float = SCALPER_EXIT_FLOOR,
                            midpoint: float = SCALPER_EXIT_MIDPOINT,
                            steepness:float = SCALPER_EXIT_STEEPNESS) -> float:
    """Sigmoid in [floor, 1.0] on expected margin."""
    z   = (expected_margin - midpoint) / steepness
    sig = 1.0 / (1.0 + math.exp(-max(-50, min(50, z))))
    return floor + (1.0 - floor) * sig


# ── Core simulation ──────────────────────────────────────────────────────────
# Default weight dicts (match the hardcoded values the sim used prior to
# making them overridable). Exposed so sensitivity sweeps can perturb them.
DEFAULT_UTILITY_W = dict(access=0.35, price=0.30, attend=0.20, resale_opt=0.15)
DEFAULT_GR_W      = dict(floor=0.40,  equality=0.30, average=0.20, baseline=0.10)


def simulate(rule: Rule, mul: float,
             defs:                 Optional[dict]  = None,
             *,
             # Structural knobs
             scalper_demand_scaling: float = 0.1,
             sat_demand:            float = SATURATION_DEMAND,
             scalper_decay:         Optional[tuple] = None,
             # Dark market knobs
             dark_leakage_base:     float = DARK_LEAKAGE_BASE,
             dark_leakage_gamma:    float = DARK_LEAKAGE_GAMMA,
             scalper_dark_cost:     float = SCALPER_DARK_COST,
             dark_fraud_penalty:    float = DARK_FRAUD_PENALTY,
             # Secondary-market platform fees (legal resale only; dark dodges them)
             secondary_fee_seller:  float = SECONDARY_FEE_SELLER,
             secondary_fee_buyer:   float = SECONDARY_FEE_BUYER,
             # Systemic dark-market harm (externality on all fans)
             dark_systemic_k:       float = DARK_SYSTEMIC_K,
             systemic_fraud_cap:    float = SYSTEMIC_FRAUD_CAP,
             systemic_fraud_weight: float = SYSTEMIC_FRAUD_WEIGHT,
             # Scalper exit sigmoid
             scalper_exit_floor:    float = SCALPER_EXIT_FLOOR,
             scalper_exit_midpoint: float = SCALPER_EXIT_MIDPOINT,
             scalper_exit_steepness:float = SCALPER_EXIT_STEEPNESS,
             # Scoring weights
             utility_w:             Optional[dict] = None,
             gr_w:                  Optional[dict] = None,
             ) -> dict:
    """
    Canonical market simulation.

    Default values reproduce the baseline model exactly. All kwargs exist so
    sensitivity analysis can perturb one knob at a time while holding the rest
    at baseline. `scalper_decay` as a 2-tuple overrides the default 3-tier
    mul-dependent scalper markdown schedule uniformly across demand levels.
    """
    if defs is None:
        defs = DEFS
    uw = utility_w if utility_w is not None else DEFAULT_UTILITY_W
    gw = gr_w      if gr_w      is not None else DEFAULT_GR_W

    # Endogenous scalper exit
    scalper_margin = expected_scalper_margin(
        rule, mul,
        dark_leakage_base    = dark_leakage_base,
        dark_leakage_gamma   = dark_leakage_gamma,
        scalper_dark_cost    = scalper_dark_cost,
        secondary_fee_seller = secondary_fee_seller,
    )
    scalper_pop_factor = scalper_pop_multiplier(
        scalper_margin,
        floor    = scalper_exit_floor,
        midpoint = scalper_exit_midpoint,
        steepness= scalper_exit_steepness,
    )

    pop = {
        "mega_fan":         round(BASE_POP["mega_fan"]         * mul),
        "committed_casual": round(BASE_POP["committed_casual"] * mul),
        "average_buyer":    round(BASE_POP["average_buyer"]    * mul),
        "scalper":          max(1, round(BASE_POP["scalper"]
                                          * (1 + (mul - 1) * scalper_demand_scaling)
                                          * scalper_pop_factor)),
    }

    sale_price = FACE * rule.dyn_mul if rule.dyn_mul else FACE
    margin     = rule.cap if rule.cap is not None else 1.0
    remain     = VENUE

    if rule.cap is not None:
        exp_margin = rule.cap * min(1.0, max(0.0, (mul - 1) / (sat_demand - 1)))
    else:
        exp_margin = max(0.0, (mul - 1) * 0.5)

    # Scalpers scale inventory depth with demand (bots buying more tickets per operation)
    # ── Channel 1 (demand): more bot capacity deployed when an event is hot.
    base_wanted = 8 * (1 + (mul - 1) * 0.25)
    #
    # ── Channel 2 (resale ceiling) — primary-participation feedback (2026-06-03).
    # Patrick's bidirectional mechanism: the resale ceiling doesn't only set how
    # much a scalper makes per ticket, it sets how hard they fight to CAPTURE the
    # primary in the first place. An uncapped (or high-cap) resale market turns
    # each primary ticket into a lottery ticket on a large payout, so scalpers
    # pour capacity into dominating the on-sale. Cap the resale upside and the
    # primary-capture arms race loses its prize.
    #
    # Previously scalper_wanted scaled with demand ONLY — blind to the resale
    # ceiling — so a scalper tried to grab just as many tickets at a 0% cap as in
    # an uncapped jackpot. That understated uncapped on-sale domination and missed
    # the core real-world dynamic. Here per-capita intensity scales with expected
    # margin (which itself rises with the cap and with demand, net of fees).
    #
    # Normalisation: a reference margin of REF_MARGIN maps to intensity 1.0 (so
    # the bounded regimes — whose margins cluster near this reference — keep their
    # previously-calibrated behaviour). Margin above the reference (the uncapped
    # jackpot: margins of 1–5×) drives intensity up toward a saturating ceiling;
    # margin below it (loss-making tight-cap scalping) pulls intensity down toward
    # a floor. Bounded between [0.5, 2.0] so the effect is meaningful but not
    # explosive, then capped inventory depth follows.
    REF_MARGIN = 0.25
    intensity  = 1.0 + 0.6 * math.tanh((scalper_margin - REF_MARGIN) / 0.6)
    intensity  = max(0.5, min(2.0, intensity))
    scalper_wanted = max(1, round(base_wanted * intensity))

    agents: list[Agent] = []
    for tid, def_ in defs.items():
        agent_def = {**def_, "wanted": scalper_wanted} if tid == "scalper" else def_
        for i in range(pop[tid]):
            agents.append(Agent(type=tid, def_=agent_def, id=f"{tid}_{i}"))

    # ── Phase 1: Primary Sale ────────────────────────────────────────────────
    queue = sorted(agents,
                   key=lambda a: 1 - min(1, max(0, a.def_["speed"] + (random.random() - 0.5) * 0.3)))
    for a in queue:
        if remain <= 0:
            break
        lim = min(a.def_["wanted"], rule.plimit)
        if sale_price <= a.def_["max_pay_mul"] * FACE:
            n            = min(lim, remain)
            a.tickets    = n
            a.cost_basis = sale_price
            a.phase      = "got_primary"
            remain       -= n

    for a in agents:
        if a.phase == "waiting":
            a.phase = "missed"

    # ── Phase 2: Life Happens ────────────────────────────────────────────────
    dark_supply = 0  # scalper tickets routed off-platform
    listings: list[Listing] = []

    for a in [x for x in agents if x.phase == "got_primary"]:
        if a.type == "scalper":
            a.phase = "flipping"
            # Unified scalper listing (2026-04-21): previously a sub-5% branch
            # dumped/wasted tickets without ever routing dark. That was backwards —
            # a tight cap is exactly where dark routing should be most intense
            # because the incentive gap between face value and off-platform price
            # is largest. Now all capped regimes use the same demand-sensitive
            # ask + dark routing logic.
            for _ in range(a.tickets):
                # Demand-sensitive ask: mul=1 ~$150-180; mul=5 ~$350-500; mul=10 ~$650-950
                platform_ask = round(sale_price * (1 + rule.cap)) if rule.cap is not None \
                               else round(FACE * (1 + 0.5 * mul + random.random() * mul * 0.3))
                # Dark market routing: scalpers compare NET dark revenue (after
                # enforcement friction) against platform ask. Route only when net
                # dark exceeds platform AND the gap is large enough to be worth
                # the risk. Under enforcement, scalper_dark_cost=0.45 shrinks the
                # effective dark payoff, tightening the binding region of the cap.
                if rule.cap is not None:
                    # A2 completion (2026-05-30 audit): align the in-loop routing
                    # decision with the realized dark-price mean and the ex-ante
                    # exit math. The realized dark price (line ~503 and the ask
                    # formula above) has mean FACE×(1+0.65×mul); expected_scalper_margin()
                    # was corrected to 0.65×mul by the original A2 fix, but THIS
                    # routing test was left at 0.5×mul — so scalpers under-routed to
                    # the dark channel relative to their own realized payoff and exit
                    # decision. Now consistent at 0.65×mul across all three sites.
                    expected_dark     = FACE * (1 + 0.65 * mul)
                    expected_dark_net = expected_dark * (1 - scalper_dark_cost)
                    if expected_dark_net > platform_ask:
                        incentive_gap = (expected_dark_net - platform_ask) / expected_dark_net
                        leakage_p = dark_leakage_base * (incentive_gap ** dark_leakage_gamma)
                        if random.random() < leakage_p:
                            dark_supply += 1
                            continue  # skip platform listing for this ticket
                listings.append(Listing(seller=a, ask=platform_ask, is_scalper=True))
                a.resale_tickets += 1
            continue

        plans_changed = random.random() < a.def_["plan_change_rate"]
        tempted       = random.random() < a.def_["flip_chance"]

        if plans_changed:
            a.phase  = "reselling"
            # Necessity resale decision keys on static cap level, not demand —
            # a fan whose plans changed won't wait for demand to rise.
            worth_it = margin >= a.def_["resale_effort_threshold"]
            if worth_it:
                # A6 fix (2026-04-27): replace binary cap==0 discontinuity with a
                # continuous listing probability. At cap=0, effort exceeds return for
                # ~half of fans (p=0.5). Probability rises linearly to 1.0 at cap=10%,
                # reflecting that even modest margin makes the effort worthwhile.
                # Uncapped regimes (cap=None) always list (margin can be substantial).
                if rule.cap is not None:
                    p_list = min(1.0, 0.5 + rule.cap * 5.0)
                    lists  = random.random() < p_list
                else:
                    lists  = True
            else:
                lists = random.random() < 0.15

            if lists:
                if rule.cap is not None:
                    ask = round(sale_price * (1 + rule.cap * 0.9))
                elif a.type == "average_buyer":
                    ask = round(FACE * (1.3 + random.random() * 0.5))
                else:
                    ask = round(FACE * (1.0 + random.random() * 0.2))
                for _ in range(a.tickets):
                    listings.append(Listing(seller=a, ask=ask, is_scalper=False))
                a.resale_tickets = a.tickets
            else:
                a.wasted_tickets = a.tickets

        elif tempted and a.tickets > 1 and (
            # A1 fix (2026-04-28): decouple flip threshold from exp_margin saturation.
            # Previously, exp_margin for capped regimes was capped at rule.cap, making
            # it structurally impossible for any fan to speculatively flip under the
            # 20–25% range the model recommends — suppressing the endowment-effect
            # coalition-splitting dynamic that is the GRE thesis's central claim.
            #
            # Fix: introduce demand-driven sell_confidence that reduces the effective
            # flip threshold for capped regimes. At high demand, fans face near-certain
            # sell-through at the cap ceiling, making even modest absolute profits
            # compelling — the same behavioral dynamic the endowment-effect literature
            # documents. At full confidence (mul ≥ 1+sat_demand), threshold drops to
            # 55% of baseline, allowing average_buyers to flip at cap ≥ 20% and
            # committed_casuals at cap ≥ 22–25%. Mega fans (threshold=0.75) still
            # won't flip below cap=41% — they value attending too highly.
            #
            # sell_confidence: 0 at mul=1 (no scarcity), 1.0 at mul ≥ 1+sat_demand.
            (lambda sc=min(1.0, max(0.0, (mul - 1.0) / sat_demand)):
             exp_margin >= a.def_["flip_margin_threshold"] * (1.0 - 0.45 * sc)
             if rule.cap is not None
             else exp_margin >= a.def_["flip_margin_threshold"])()
        ):
            a.attending = True
            a.phase     = "flipping"
            ask = round(sale_price * (1 + rule.cap)) if rule.cap is not None \
                  else round(FACE * (1.5 + random.random() * 1.0))
            for _ in range(a.tickets - 1):
                listings.append(Listing(seller=a, ask=ask, is_scalper=False))
            a.resale_tickets = a.tickets - 1

        else:
            a.attending = True
            a.phase     = "attending"
            if a.tickets > 1 and a.type == "mega_fan" and random.random() < 0.15:
                cap_val = rule.cap or 0
                if rule.cap is not None:
                    ask = round(sale_price * (1 + cap_val * 0.5))
                else:
                    ask = round(FACE * (1.0 + random.random() * 0.1))
                listings.append(Listing(seller=a, ask=ask, is_scalper=False))
                a.resale_tickets = 1
            if (not tempted
                    and a.tickets > 1
                    and exp_margin < a.def_["resale_effort_threshold"]
                    and random.random() < 0.4):
                a.wasted_tickets = a.tickets - 1

    # ── Phase 3: Secondary Market (3 rounds) ─────────────────────────────────
    missed = [a for a in agents if a.phase == "missed" and a.type != "scalper"]
    random.shuffle(missed)

    seller_rev = {t: 0.0 for t in defs}
    bought_ids = set()

    for rnd in range(3):
        for li in listings:
            if li.sold:
                continue
            if li.is_scalper:
                if scalper_decay is not None:
                    # Override: uniform 2-round decay (R1, R2) + carry-through for R3
                    r1, r2 = scalper_decay
                    decays = [1.0, r1, r2]
                else:
                    # Demand-sensitive markdown: low scarcity gradual; extreme aggressive
                    decays = [1.0, 0.85, 0.75] if mul <= 2 else \
                             [1.0, 0.65, 0.45] if mul <= 5 else \
                             [1.0, 0.50, 0.30]
                floors = [li.seller.cost_basis * 1.05,
                          li.seller.cost_basis * 1.05,
                          li.seller.cost_basis * 0.95]
                li.final_price = max(round(floors[rnd]), round(li.ask * decays[rnd]))
            else:
                decays = [1.0, 0.95, 0.88]
                li.final_price = max(FACE, round(li.ask * decays[rnd]))
            if rule.cap is not None:
                li.final_price = min(li.final_price, round(FACE * (1 + rule.cap)))

        avail   = sorted([x for x in listings if not x.sold], key=lambda x: x.final_price)
        seekers = [b for b in missed if b.id not in bought_ids]
        random.shuffle(seekers)

        for buyer in seekers:
            ticket = next((x for x in avail
                           if not x.sold and x.final_price <= buyer.def_["max_pay_mul"] * FACE),
                          None)
            if ticket:
                ticket.sold           = True
                buyer.phase           = "bought_secondary"
                buyer.secondary_price = ticket.final_price
                buyer.attending       = random.random() < buyer.def_["attend_base"]
                bought_ids.add(buyer.id)
                # Seller nets the listed price MINUS the platform seller fee
                # (2026-06-03). This is what makes face-value resale loss-making and
                # is the supply-side half of the break-even-cap mechanism. Applies
                # to all legal on-platform listings (fan and scalper alike).
                seller_rev[ticket.seller.type] += ticket.final_price * (1 - secondary_fee_seller)

    # ── Phase 3.5: Dark Market ───────────────────────────────────────────────
    # Scalper tickets routed off-platform match with high-WTP frustrated buyers.
    # Transactions happen above the cap ceiling at elevated fraud risk.
    #
    # FIX (2026-04-21): affordability check. Previously any buyer with
    # max_pay_mul * FACE > cap_ceiling * 1.1 would be assigned a ticket
    # regardless of the sampled dark_price — this over-counted dark matches
    # at high scarcity and inflated the dark fraud penalty for
    # committed_casual and average_buyer. Unmatched tickets are now tracked
    # via dark_unmatched and rolled into `wasted`.
    dark_sold      = 0
    dark_unmatched = 0
    if dark_supply > 0 and rule.cap is not None:
        cap_ceiling = FACE * (1 + rule.cap)
        # Candidates: missed buyers with WTP meaningfully above the cap ceiling
        # (those who would actually consider off-platform transactions).
        # Sort by descending WTP so high-WTP buyers absorb high-priced tickets first.
        candidates = [b for b in agents
                      if b.id not in bought_ids
                      and b.phase == "missed"
                      and b.def_["max_pay_mul"] * FACE > cap_ceiling * 1.1]
        candidates.sort(key=lambda b: -b.def_["max_pay_mul"])

        # A3 fix (2026-04-28): generate all dark prices upfront and sort descending,
        # then match each ticket (highest price first) to the highest-WTP buyer who
        # can afford it. Previous approach drew a random price per iteration and
        # matched the first affordable buyer — causing high-WTP buyers to consume
        # cheap tickets first, leaving expensive tickets unmatched and inflating
        # dark_unmatched. Efficient top-down matching is the standard mechanism
        # design approach and removes the algorithmic bias.
        dark_prices = sorted(
            [round(FACE * (1 + 0.5 * mul + random.random() * mul * 0.3))
             for _ in range(dark_supply)],
            reverse=True
        )
        available = list(candidates)  # matched buyers removed as we go

        for dark_price in dark_prices:
            buyer = next((b for b in available
                          if b.def_["max_pay_mul"] * FACE >= dark_price),
                         None)
            if buyer is None:
                dark_unmatched += 1
                continue
            available.remove(buyer)
            buyer.phase           = "bought_dark"
            buyer.secondary_price = dark_price
            buyer.dark_market     = True
            buyer.attending       = random.random() < buyer.def_["attend_base"]
            bought_ids.add(buyer.id)
            # Scalper realized revenue is NET of enforcement friction.
            seller_rev["scalper"] += dark_price * (1 - scalper_dark_cost)
            dark_sold += 1

    # ── Systemic dark-market fraud externality ───────────────────────────────
    # Realized dark-market prevalence imposes a market-wide fraud/trust cost on
    # EVERY fan, not just those who knowingly bought dark (that private cost is
    # dark_fraud_penalty, applied per-buyer below). Calibrated so the worst case
    # (0% cap, high demand) reproduces ~Ireland's 13.6% market-wide fraud rate.
    # Uncapped regimes don't activate the dark channel, so prevalence = 0 there
    # (their baseline secondary fraud is handled separately by B1).
    dark_prevalence = dark_sold / VENUE
    systemic_fraud  = min(systemic_fraud_cap, dark_systemic_k * dark_prevalence)
    systemic_penalty = systemic_fraud * systemic_fraud_weight

    # ── Scoring ──────────────────────────────────────────────────────────────
    outcomes = {}
    for tid in defs:
        grp      = [a for a in agents if a.type == tid]
        total    = len(grp)
        got      = [a for a in grp if a.tickets > 0 or a.phase in ("bought_secondary", "bought_dark")]
        att      = [a for a in grp if a.attending]

        # Effective price paid (2026-06-03): legal secondary buyers pay the
        # platform BUYER fee on top of the listed price — real money the
        # face-value-only framing ignores. Dark-market buyers dodge the fee
        # (cash, off-platform) but bear fraud risk instead (handled below).
        # Primary holders pay only their cost_basis (no secondary fee).
        def _effective_paid(a):
            if a.phase == "bought_secondary":
                return a.secondary_price * (1 + secondary_fee_buyer)
            return a.secondary_price or a.cost_basis or 0
        avg_paid = (sum(_effective_paid(a) for a in got) / len(got)) if got else 0

        ex_ante_utility = 0.0  # default; overwritten for fan types below
        if tid == "scalper":
            inv = sum(a.tickets * sale_price for a in grp)
            ret = seller_rev["scalper"]
            if inv == 0:
                utility = 0.0
            else:
                roi     = (ret - inv) / inv
                utility = (0.3 + min(0.65, roi * 0.65)) if roi >= 0 \
                          else max(0.0, 0.3 * (1 + roi / 0.3))
            ex_ante_utility = utility  # scalper ex-ante = utility (no positional split)
        else:
            access_rate = len(got) / total
            if not got:
                utility = 0.02
                # E1 completion (2026-07-04): with zero access, the ex-ante
                # expectation IS the missed-utility floor — hit_rate is 0, so
                # ex_ante = 0*got_utility + 1*0.02. Previously the 0.0
                # initializer leaked through because the E1 computation lives
                # in the else-branch, understating rawls_ea_fan / ex_ante
                # lenses at total-shutout corners (tight cap × extreme
                # demand). Caught by test_invariants.py::ExAnteZeroAccessFloor.
                ex_ante_utility = 0.02
            else:
                price_ratio = (avg_paid - FACE) / FACE if avg_paid > 0 else 0
                price_score = max(0.0, 1 - price_ratio) if avg_paid > 0 else 0.0
                if rule.dyn_mul and rule.dyn_mul > 1:
                    surcharge_ratio  = (sale_price - FACE) / FACE
                    surcharge_resent = surcharge_ratio * 0.3
                    price_score      = max(0.0, price_score - surcharge_resent)
                attend_rate = len(att) / total
                # A4 fix (2026-04-27), fee revision (2026-06-03): resale option
                # value as a continuous function of cap grounded in NET resale
                # economics — the cap ceiling minus the seller-side platform fee.
                #
                # A reseller listing at the cap ceiling grosses FACE×(1+cap) and
                # nets FACE×(1+cap)×(1−fee_seller). Net upside over face is thus
                # roughly (cap − fee_seller) once the small cross term is ignored.
                # Below the break-even cap (≈ fee_seller/(1−fee_seller) ≈ 17.6% at
                # a 15% fee) resale LOSES money, so the option to resell is close to
                # worthless — a fan would gift or eat the ticket rather than pay to
                # offload it. Above break-even the option value climbs and
                # saturates at 0.70 (the uncapped reference) by the time net upside
                # reaches ~25 points.
                #
                # This is the mechanism that makes a 0% cap socially poor on the
                # fan side without any hand-tuned penalty: face-value-only resale is
                # fee-dominated and non-functional, exactly as in the UK/Ireland
                # experience. Uncapped regimes keep full option value (0.70) since
                # the gross markup swamps the fee.
                if rule.cap is None:
                    resale_opt = 0.70
                else:
                    net_upside = rule.cap - secondary_fee_seller   # may be negative
                    # Map net upside in [0, 0.25] → option value in [0.20, 0.70];
                    # below break-even (net_upside ≤ 0) it declines linearly to a
                    # 0.05 floor.
                    #
                    # UK-2026 generalization (2026-07-05): the sub-break-even
                    # branch was previously 0.05 + 0.15·cap/fee_seller — which at
                    # the baseline fee (0.15) is algebraically IDENTICAL to
                    # 0.20 + net_upside (0.05 + cap = 0.20 + cap − 0.15), but
                    # fails to respond when the FEE side moves: under a platform
                    # fee cap (UK 2026 regime: face-value resale + capped service
                    # fees), a reseller recouping 95/100 has real option value a
                    # 85/100 reseller lacks. The continuous form responds to both
                    # sides of net_upside and reproduces baseline bit-for-bit at
                    # fee=0.15 (verified against the committed cap-sweep CSVs).
                    if net_upside <= 0:
                        resale_opt = max(0.05, 0.20 + net_upside)
                    else:
                        resale_opt = min(0.70, 0.20 + net_upside * 2.0)
                resale_opt *= min(1.0, access_rate * 3)
                utility     = (access_rate * uw["access"]
                               + price_score * uw["price"]
                               + attend_rate * uw["attend"]
                               + resale_opt  * uw["resale_opt"])
                dark_frac = sum(1 for a in got if a.dark_market) / len(got)
                utility   = max(0.0, utility - dark_frac * dark_fraud_penalty)

                # B1 fix (2026-04-28): apply baseline fraud penalty to secondary
                # buyers in uncapped regimes. Status Quo and DP previously had zero
                # modeled fraud, giving them a free pass vs the 3.8% UK empirical
                # rate. Only applied to secondary (not primary or dark) buyers.
                if rule.cap is None:
                    sec_frac = sum(1 for a in got if a.phase == "bought_secondary") / len(got)
                    utility  = max(0.0, utility - sec_frac * BASELINE_SECONDARY_FRAUD_PENALTY)

                # Systemic dark-market externality (2026-05-30): every fan who
                # holds a ticket bears the market-wide fraud/trust cost of dark
                # prevalence, regardless of how they acquired their ticket. This
                # is what makes a 0%-cap regime socially worse than its private
                # dark-buyer harm alone implies — and is the mechanism that
                # reconciles the model with Ireland's observed 13.6% fraud rate.
                utility = max(0.0, utility - systemic_penalty)

                # E1 fix (2026-04-28): compute ex-ante acceptance utility — the
                # expected utility before knowing whether you'll get a ticket.
                # This operationalizes the GRE "harder test": would you accept
                # these rules not knowing your position? Weighted by actual hit rate.
                # got_utility (above) and missed_utility (access=0, floor=0.02).
                # Stored per-type for the ex-ante lens; scored separately below.
                got_utility    = utility  # utility of those who got access
                missed_utility = 0.02     # utility of those who missed (access=0)
                hit_rate       = len(got) / total
                ex_ante_utility = hit_rate * got_utility + (1 - hit_rate) * missed_utility

        outcomes[tid] = dict(
            utility        = round(utility, 4),
            ex_ante        = round(ex_ante_utility if tid != "scalper" else utility, 4),
            got            = len(got),
            att            = len(att),
            total          = total,
            avg_price      = round(avg_paid),
        )

    # ── GR composite ─────────────────────────────────────────────────────────
    def calc_gr(vals):
        mn = min(vals); mx = max(vals); av = sum(vals) / len(vals)
        return round((mn * gw["floor"]
                      + (1 - (mx - mn)) * gw["equality"]
                      + av * gw["average"]
                      + 0.5 * gw["baseline"]), 4)

    # Attendance = seats filled (not unique attending agents)
    attend = sum(
        (1 if a.phase in ("bought_secondary", "bought_dark")
         else max(0, a.tickets - a.resale_tickets - a.wasted_tickets))
        for a in agents if a.attending
    )
    # Total waste: fan wastage + unmatched dark-supply tickets (routed but unsold).
    wasted = sum(a.wasted_tickets for a in agents) + dark_unmatched

    # ── Alternative welfare criteria ─────────────────────────────────────────
    # Computed alongside GRE lenses so every sweep automatically carries them.
    #
    # Rawlsian maximin (Veil of Ignorance, Rawls 1971):
    #   Choose the ruleset that maximises the MINIMUM utility across positions.
    #   Two variants — whether scalpers are inside the social contract or not:
    #     rawls_fan: min utility across the three fan types only (scalpers are
    #       exogenous market actors, not parties deliberating over venue rules)
    #     rawls_all: min across all four types (pure veil — you might be a scalper)
    #
    # Harsanyi utilitarianism (Harsanyi 1953, 1975):
    #   Behind the veil, rational agents maximise EXPECTED utility (not the min),
    #   collapsing to a weighted-average criterion.
    #     harsanyi_equal: arithmetic mean across fan types (equal probability)
    #     harsanyi_pop:   population-weighted mean across all types (prob ∝ size)
    #
    # Pareto dominance is computed in post-processing (rawls_analysis.py) because
    # it requires pairwise comparison across ruleset runs, not within a single run.
    fan_utils = [outcomes[t]["utility"] for t in FAN_TYPES]
    all_utils = [outcomes[t]["utility"] for t in defs]

    rawls_fan     = round(min(fan_utils), 4)
    rawls_all     = round(min(all_utils), 4)
    rawls_ea_fan  = round(min(outcomes[t]["ex_ante"] for t in FAN_TYPES), 4)

    harsanyi_eq_fan = round(sum(fan_utils) / len(fan_utils), 4)
    harsanyi_eq_all = round(sum(all_utils) / len(all_utils), 4)

    total_pop_all = sum(pop[t] for t in defs)
    harsanyi_pop_all = round(
        sum(outcomes[t]["utility"] * pop[t] for t in defs) / total_pop_all, 4)
    total_pop_fan = sum(pop[t] for t in FAN_TYPES)
    harsanyi_pop_fan = round(
        sum(outcomes[t]["utility"] * pop[t] for t in FAN_TYPES) / total_pop_fan, 4)

    return dict(
        system         = calc_gr([o["utility"]  for o in outcomes.values()]),
        fan_only       = calc_gr([outcomes[t]["utility"]  for t in FAN_TYPES]),
        pop_wt         = calc_gr([outcomes[t]["utility"]  for t in defs for _ in range(pop[t])]),
        # E1 fix (2026-04-28): ex-ante acceptance lens — GRE's "harder test."
        # Scores each ruleset on expected utility before knowing your position
        # (got vs missed). Directly operationalizes "would you accept these rules
        # not knowing which role you'd occupy?" as weighted average of got/missed
        # utilities at the actual hit rate. Fan-only and pop-weighted variants.
        ex_ante_fan    = calc_gr([outcomes[t]["ex_ante"]  for t in FAN_TYPES]),
        ex_ante_popwt  = calc_gr([outcomes[t]["ex_ante"]  for t in defs for _ in range(pop[t])]),
        # Alternative welfare criteria (added 2026-04-28):
        rawls_fan      = rawls_fan,
        rawls_all      = rawls_all,
        rawls_ea_fan   = rawls_ea_fan,
        harsanyi_eq_fan= harsanyi_eq_fan,
        harsanyi_eq_all= harsanyi_eq_all,
        harsanyi_pop_all= harsanyi_pop_all,
        harsanyi_pop_fan= harsanyi_pop_fan,
        outcomes       = outcomes,
        attend         = attend,
        wasted         = wasted,
        primary_sold   = VENUE - remain,
        secondary_sold = sum(1 for l in listings if l.sold),
        dark_sold      = dark_sold,
        dark_unmatched = dark_unmatched,
        dark_prevalence = round(dark_prevalence, 4),
        systemic_fraud  = round(systemic_fraud, 4),
    )
