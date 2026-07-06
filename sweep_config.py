"""
Shared sweep configuration — single source of truth for the experiment grid.
=============================================================================
Extracted 2026-07-04. Previously the series list, cap levels, and demand
levels were defined independently in cap_sweep.py, rawls_analysis.py, and
generate_charts.py: adding a cap level to the sweep silently desynced the
two downstream consumers. Import from here instead.

generate_deck.js still duplicates PALETTE in JS (documented in README).
"""

from gre_sim import Rule

# ── Experiment grid ───────────────────────────────────────────────────────────
DEMAND_LEVELS  = [1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10]
CAP_LEVELS     = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
RUNS_PER_POINT = 100  # C2: 100 runs -> MOE ~±0.010 on GR lenses

# ── Series (reference rulesets + bounded continuum) ───────────────────────────
def build_series():
    """Series dicts for cap_sweep: reference rulesets then the bounded caps."""
    return [
        dict(id="status_quo", label="Status Quo",
             rule=Rule("Status Quo",      cap=None, plimit=8, dyn_mul=None)),
        dict(id="dynamic",    label="Dynamic Pricing",
             rule=Rule("Dynamic Pricing", cap=None, plimit=6, dyn_mul=2.2)),
        dict(id="uk_face",    label="UK Face Value",
             rule=Rule("UK Face Value",   cap=0.0,  plimit=2, dyn_mul=None)),
        *[
            dict(
                id    = f"bounded_{round(c * 100)}",
                label = f"Bounded {round(c * 100)}%",
                rule  = Rule(f"Bounded {round(c * 100)}%",
                             cap=c, plimit=4, dyn_mul=None),
            )
            for c in CAP_LEVELS
        ],
        # ── UK 2026 regime (added 2026-07-05) ─────────────────────────────────
        # Modeled on the Nov 2025 UK government consultation response / May
        # 2026 King's Speech draft Ticket Tout Ban Bill: resale capped at face
        # value + unavoidable fees, AND platform service fees capped so fees
        # can't undermine the price limit. We model the fee cap at 5% per side
        # ("fee-capped") and 2% per side ("strict"); baseline platforms charge
        # 15%/15% (GAO ~30% combined). The constructive comparator — keep the
        # fee cap, raise the price cap — is Bounded 20% under the same 5% fees.
        # NOTE: appended AFTER the existing grid so the seeded RNG stream for
        # all pre-existing series is untouched (their CSV rows stay
        # bit-for-bit identical).
        dict(id="uk2026", label="UK 2026 (0% + fee cap)",
             rule=Rule("UK 2026 (0% + fee cap)", cap=0.0, plimit=4, dyn_mul=None),
             sim_kwargs=dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)),
        dict(id="uk2026_strict", label="UK 2026 strict (0% + 2% fees)",
             rule=Rule("UK 2026 strict (0% + 2% fees)", cap=0.0, plimit=4, dyn_mul=None),
             sim_kwargs=dict(secondary_fee_seller=0.02, secondary_fee_buyer=0.02)),
        dict(id="bounded20_feecap", label="Bounded 20% + fee cap",
             rule=Rule("Bounded 20% + fee cap", cap=0.20, plimit=4, dyn_mul=None),
             sim_kwargs=dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)),
        dict(id="bounded10_feecap", label="Bounded 10% + fee cap",
             rule=Rule("Bounded 10% + fee cap", cap=0.10, plimit=4, dyn_mul=None),
             sim_kwargs=dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)),
    ]

REFERENCE_LABELS = ["Status Quo", "Dynamic Pricing", "UK Face Value"]
BOUNDED_LABELS   = [f"Bounded {round(c * 100)}%" for c in CAP_LEVELS]
UK2026_LABELS    = ["UK 2026 (0% + fee cap)", "UK 2026 strict (0% + 2% fees)",
                    "Bounded 20% + fee cap", "Bounded 10% + fee cap"]
SERIES_ORDER     = REFERENCE_LABELS + BOUNDED_LABELS + UK2026_LABELS

# ── Chart palette (mirrored in generate_deck.js — keep in sync manually) ─────
PALETTE = {
    "Status Quo":      "#E05C5C",
    "Dynamic Pricing": "#E08B3A",
    "UK Face Value":   "#9B59B6",
    "Bounded 0%":      "#5BA4CF",
    "Bounded 10%":     "#3D9B70",
    "Bounded 20%":     "#2E7D52",
    "Bounded 25%":     "#1A5C3A",
    "highlight":       "#F4D03F",
}
