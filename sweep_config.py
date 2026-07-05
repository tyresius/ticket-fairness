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
    ]

REFERENCE_LABELS = ["Status Quo", "Dynamic Pricing", "UK Face Value"]
BOUNDED_LABELS   = [f"Bounded {round(c * 100)}%" for c in CAP_LEVELS]
SERIES_ORDER     = REFERENCE_LABELS + BOUNDED_LABELS

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
