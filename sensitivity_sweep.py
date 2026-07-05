"""
Sensitivity Analysis — Golden Rule Equilibrium Simulation
=========================================================
One-at-a-time (OAT): vary each parameter while holding all others at baseline.

For each parameter:
  - Test at baseline, low, and high values
  - Run bounded_10/20/30 and status_quo at demand levels [1, 2, 5, 10]
  - Compute Advantage Range (AR) of (bounded_20 − status_quo) across low/high

Sensitivity metric: Advantage Range (AR) — how much does the bounded_20 vs
status_quo delta fluctuate across the low/high range? Computed on the
differential so it only moves when relative performance changes.

2026-04-22: Refactored to import from canonical `gre_sim`. Adds sensitivity
specs for the new enforcement + nonlinear leakage + scalper exit knobs.
"""

import random
import csv
import sys
import copy

# C1 fix (2026-04-27): fixed seed for reproducibility.
random.seed(42)

from gre_sim import (
    Rule, simulate, DEFS as BASELINE_DEFS,
    DEFAULT_UTILITY_W, DEFAULT_GR_W,
    DARK_LEAKAGE_BASE, DARK_LEAKAGE_GAMMA,
    SCALPER_DARK_COST, DARK_FRAUD_PENALTY,
    SCALPER_EXIT_FLOOR, SCALPER_EXIT_MIDPOINT, SCALPER_EXIT_STEEPNESS,
    SATURATION_DEMAND,
)


# ── Weight renormalization ─────────────────────────────────────────────────────
def renorm(weights: dict, varied_key: str, new_val: float) -> dict:
    """Set weights[varied_key]=new_val, renormalize others proportionally."""
    remaining = 1.0 - new_val
    others    = {k: v for k, v in weights.items() if k != varied_key}
    other_sum = sum(others.values())
    result    = {varied_key: new_val}
    if other_sum == 0 or remaining == 0:
        eq = remaining / max(len(others), 1)
        result.update({k: eq for k in others})
    else:
        result.update({k: v * (remaining / other_sum) for k, v in others.items()})
    return result


# ── Parameter test specifications ─────────────────────────────────────────────
# group=None           → patch DEFS[agent][key]
# group="structural"   → structural sim parameter
# group="dark"         → dark-market / enforcement parameter
# group="exit"         → scalper exit sigmoid parameter
# group="util_w"       → renormalize utility_w
# group="gr_w"         → renormalize gr_w
PARAM_SPECS = [
    # ── Tier 1: Agent behavioral ──────────────────────────────────────────────
    dict(name="mega_fan.flip_chance",                    tier=1, group=None, low=0.005, high=0.06),
    dict(name="mega_fan.plan_change_rate",               tier=1, group=None, low=0.03,  high=0.18),
    dict(name="mega_fan.flip_margin_threshold",          tier=1, group=None, low=0.40,  high=0.95),
    dict(name="mega_fan.resale_effort_threshold",        tier=1, group=None, low=0.0,   high=0.10),
    dict(name="committed_casual.flip_chance",            tier=1, group=None, low=0.03,  high=0.20),
    dict(name="committed_casual.plan_change_rate",       tier=1, group=None, low=0.05,  high=0.25),
    dict(name="committed_casual.flip_margin_threshold",  tier=1, group=None, low=0.20,  high=0.60),
    dict(name="committed_casual.resale_effort_threshold",tier=1, group=None, low=0.10,  high=0.50),
    dict(name="average_buyer.flip_chance",               tier=1, group=None, low=0.08,  high=0.40),
    dict(name="average_buyer.plan_change_rate",          tier=1, group=None, low=0.06,  high=0.25),
    dict(name="average_buyer.flip_margin_threshold",     tier=1, group=None, low=0.15,  high=0.55),
    dict(name="average_buyer.resale_effort_threshold",   tier=1, group=None, low=0.10,  high=0.45),

    # ── Tier 2: Structural ────────────────────────────────────────────────────
    dict(name="scalper_demand_scaling", tier=2, group="structural", low=0.05, high=0.25),
    dict(name="sat_demand",             tier=2, group="structural", low=1.5,  high=3.0),
    dict(name="scalper_decay_r1",       tier=2, group="structural", low=0.50, high=0.90),
    dict(name="scalper_decay_r2",       tier=2, group="structural", low=0.30, high=0.70),

    # ── Tier 2.5: Dark market / enforcement ───────────────────────────────────
    dict(name="dark_leakage_base",  tier=2, group="dark", low=0.20, high=0.50),
    dict(name="dark_leakage_gamma", tier=2, group="dark", low=1.0,  high=2.0),
    dict(name="scalper_dark_cost",  tier=2, group="dark", low=0.25, high=0.65),
    dict(name="dark_fraud_penalty", tier=2, group="dark", low=0.10, high=0.40),
    # Systemic dark-market externality (added 2026-05-30)
    dict(name="dark_systemic_k",       tier=2, group="dark", low=1.5,  high=3.5),
    dict(name="systemic_fraud_weight", tier=2, group="dark", low=0.5,  high=1.5),

    # ── Tier 2.5: Scalper endogenous exit ─────────────────────────────────────
    dict(name="scalper_exit_floor",     tier=2, group="exit", low=0.05, high=0.40),
    dict(name="scalper_exit_midpoint",  tier=2, group="exit", low=0.10, high=0.30),
    dict(name="scalper_exit_steepness", tier=2, group="exit", low=0.04, high=0.15),

    # ── Tier 3: Scoring methodology ───────────────────────────────────────────
    dict(name="w_access",     tier=3, group="util_w", low=0.20, high=0.50),
    dict(name="w_price",      tier=3, group="util_w", low=0.15, high=0.45),
    dict(name="w_attend",     tier=3, group="util_w", low=0.08, high=0.35),
    dict(name="w_resale_opt", tier=3, group="util_w", low=0.05, high=0.28),

    dict(name="gr_floor",    tier=3, group="gr_w", low=0.20, high=0.60),
    dict(name="gr_equality", tier=3, group="gr_w", low=0.15, high=0.50),
    dict(name="gr_average",  tier=3, group="gr_w", low=0.08, high=0.35),
    dict(name="gr_baseline", tier=3, group="gr_w", low=0.03, high=0.22),
]

# ── Sweep configuration ────────────────────────────────────────────────────────
DEMAND_LEVELS  = [1, 2, 5, 10]
RUNS_PER_POINT = 20
LENSES         = ["fan_only", "pop_wt", "system"]
LENS_LABELS    = {"fan_only": "Fan", "pop_wt": "PopWt", "system": "System"}

TEST_RULES = {
    "status_quo":  Rule("Status Quo",  cap=None, plimit=8, dyn_mul=None),
    "bounded_10":  Rule("Bounded 10%", cap=0.10, plimit=4, dyn_mul=None),
    "bounded_20":  Rule("Bounded 20%", cap=0.20, plimit=4, dyn_mul=None),
    "bounded_30":  Rule("Bounded 30%", cap=0.30, plimit=4, dyn_mul=None),
}


def build_sim_kwargs(spec, test_label):
    """
    Returns a kwargs dict for simulate() given a param spec and test_label
    ('baseline', 'low', 'high'). Defaults mirror gre_sim's baseline so that
    test_label='baseline' reproduces the canonical simulation exactly.
    """
    val = {"baseline": None, "low": spec["low"], "high": spec["high"]}[test_label]

    kwargs = dict(
        defs                   = copy.deepcopy(BASELINE_DEFS),
        scalper_demand_scaling = 0.1,
        sat_demand             = SATURATION_DEMAND,
        scalper_decay          = None,  # None = use default 3-tier schedule
        dark_leakage_base      = DARK_LEAKAGE_BASE,
        dark_leakage_gamma     = DARK_LEAKAGE_GAMMA,
        scalper_dark_cost      = SCALPER_DARK_COST,
        dark_fraud_penalty     = DARK_FRAUD_PENALTY,
        scalper_exit_floor     = SCALPER_EXIT_FLOOR,
        scalper_exit_midpoint  = SCALPER_EXIT_MIDPOINT,
        scalper_exit_steepness = SCALPER_EXIT_STEEPNESS,
        utility_w              = copy.deepcopy(DEFAULT_UTILITY_W),
        gr_w                   = copy.deepcopy(DEFAULT_GR_W),
    )

    if test_label == "baseline" or val is None:
        return kwargs

    group = spec.get("group")
    name  = spec["name"]

    if group is None:
        # agent behavioral: name = "agent_type.key"
        agent_type, key = name.split(".")
        kwargs["defs"][agent_type][key] = val

    elif group == "structural":
        if name == "scalper_demand_scaling":
            kwargs["scalper_demand_scaling"] = val
        elif name == "sat_demand":
            kwargs["sat_demand"] = val
        elif name == "scalper_decay_r1":
            # Baseline for override: (0.70, 0.50) matches the pre-refactor default.
            kwargs["scalper_decay"] = (val, 0.50)
        elif name == "scalper_decay_r2":
            kwargs["scalper_decay"] = (0.70, val)

    elif group == "dark":
        kwargs[name] = val

    elif group == "exit":
        kwargs[name] = val

    elif group == "util_w":
        key_map = {"w_access": "access", "w_price": "price",
                   "w_attend": "attend", "w_resale_opt": "resale_opt"}
        kwargs["utility_w"] = renorm(DEFAULT_UTILITY_W, key_map[name], val)

    elif group == "gr_w":
        key_map = {"gr_floor": "floor", "gr_equality": "equality",
                   "gr_average": "average", "gr_baseline": "baseline"}
        kwargs["gr_w"] = renorm(DEFAULT_GR_W, key_map[name], val)

    return kwargs


def avg_f(runs, fn):
    return round(sum(fn(r) for r in runs) / len(runs), 4)


# ── Main sweep ────────────────────────────────────────────────────────────────
def run_sensitivity():
    # ── Compute baseline first ──
    print("Computing baseline...")
    baseline_results = {}  # (rule_id, demand, lens) → mean GR
    base_kwargs = build_sim_kwargs(PARAM_SPECS[0], "baseline")
    for rid, rule in TEST_RULES.items():
        for mul in DEMAND_LEVELS:
            runs = [simulate(rule, mul, **base_kwargs) for _ in range(RUNS_PER_POINT)]
            for lens in LENSES:
                baseline_results[(rid, mul, lens)] = avg_f(runs, lambda r, l=lens: r[l])
    print("  done.\n")

    # ── Parameter sweep ──
    summary_rows = []
    total_params = len(PARAM_SPECS)

    for pi, spec in enumerate(PARAM_SPECS, 1):
        name = spec["name"]
        sys.stdout.write(f"[{pi:2d}/{total_params}] {name:<40}")
        sys.stdout.flush()

        for test_label in ("low", "high"):
            val    = spec[test_label]
            kwargs = build_sim_kwargs(spec, test_label)

            for rid, rule in TEST_RULES.items():
                for mul in DEMAND_LEVELS:
                    runs = [simulate(rule, mul, **kwargs) for _ in range(RUNS_PER_POINT)]
                    for lens in LENSES:
                        mean_gr = avg_f(runs, lambda r, l=lens: r[l])
                        base_gr = baseline_results[(rid, mul, lens)]
                        summary_rows.append(dict(
                            param      = name,
                            tier       = spec["tier"],
                            group      = spec.get("group") or "agent",
                            test_label = test_label,
                            test_value = val,
                            series     = rid,
                            demand     = mul,
                            lens       = LENS_LABELS[lens],
                            gr_mean    = mean_gr,
                            gr_base    = base_gr,
                            delta_vs_base = round(mean_gr - base_gr, 4),
                        ))
        sys.stdout.write(" done\n")
        sys.stdout.flush()

    print()

    # ── Write sensitivity_summary.csv ──
    with open("sensitivity_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        w.writeheader(); w.writerows(summary_rows)
    print("Wrote sensitivity_summary.csv")

    # ── Compute rankings ──
    rankings = []

    for spec in PARAM_SPECS:
        name = spec["name"]

        for lens_label in ("Fan", "PopWt", "System"):
            lens_key = [k for k, v in LENS_LABELS.items() if v == lens_label][0]

            # Advantage Range: bounded_20 − status_quo delta across low/high
            deltas_by_label = {}
            for test_label in ("low", "high"):
                advantage_at_demands = []
                for mul in DEMAND_LEVELS:
                    b20 = next(r["gr_mean"] for r in summary_rows
                               if r["param"] == name and r["test_label"] == test_label
                               and r["series"] == "bounded_20" and r["demand"] == mul
                               and r["lens"] == lens_label)
                    sq  = next(r["gr_mean"] for r in summary_rows
                               if r["param"] == name and r["test_label"] == test_label
                               and r["series"] == "status_quo" and r["demand"] == mul
                               and r["lens"] == lens_label)
                    advantage_at_demands.append(b20 - sq)
                deltas_by_label[test_label] = advantage_at_demands

            base_advantages = [
                baseline_results[("bounded_20", mul, lens_key)]
                - baseline_results[("status_quo", mul, lens_key)]
                for mul in DEMAND_LEVELS
            ]

            all_deltas = (deltas_by_label["low"] + deltas_by_label["high"] + base_advantages)
            AR         = round(max(all_deltas) - min(all_deltas), 4)
            sign_flip  = sum(1 for d in deltas_by_label["low"] + deltas_by_label["high"] if d < 0)

            base_avg = sum(base_advantages) / len(base_advantages)
            high_avg = sum(deltas_by_label["high"]) / len(deltas_by_label["high"])
            low_avg  = sum(deltas_by_label["low"])  / len(deltas_by_label["low"])
            dir_high = ("widens" if high_avg > base_avg + 0.005 else
                        "flips"  if high_avg < 0 else "narrows")
            dir_low  = ("widens" if low_avg  > base_avg + 0.005 else
                        "flips"  if low_avg  < 0 else "narrows")

            def opt_cap(test_label_):
                scores = {}
                for cap_id in ("bounded_10", "bounded_20", "bounded_30"):
                    scores[cap_id] = sum(
                        r["gr_mean"] for r in summary_rows
                        if r["param"] == name and r["test_label"] == test_label_
                        and r["series"] == cap_id and r["lens"] == lens_label
                    )
                return max(scores, key=scores.get)

            base_opt = max(
                {cap_id: sum(baseline_results[(cap_id, mul, lens_key)] for mul in DEMAND_LEVELS)
                 for cap_id in ("bounded_10", "bounded_20", "bounded_30")},
                key=lambda k: sum(baseline_results[(k, m, lens_key)] for m in DEMAND_LEVELS)
            )

            rankings.append(dict(
                param          = name,
                tier           = spec["tier"],
                group          = spec.get("group") or "agent",
                lens           = lens_label,
                AR             = AR,
                sign_flips     = sign_flip,
                dir_low        = dir_low,
                dir_high       = dir_high,
                base_adv_mean  = round(base_avg, 4),
                cap_shift_low  = opt_cap("low")  != base_opt,
                cap_shift_high = opt_cap("high") != base_opt,
                base_opt       = base_opt,
            ))

    for lens_label in ("Fan", "PopWt", "System"):
        subset = [r for r in rankings if r["lens"] == lens_label]
        max_ar = max(r["AR"] for r in subset) or 1
        max_sf = max(r["sign_flips"] for r in subset) or 1
        for r in subset:
            r["sensitivity_score"] = round(
                (r["AR"] / max_ar) * 0.70 + (r["sign_flips"] / max_sf) * 0.30, 4
            )

    for lens_label in ("Fan", "PopWt", "System"):
        subset = sorted([r for r in rankings if r["lens"] == lens_label],
                        key=lambda r: -r["sensitivity_score"])
        for rank, r in enumerate(subset, 1):
            r["rank"] = rank

    rankings.sort(key=lambda r: (r["lens"], r["rank"]))

    with open("sensitivity_rankings.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rankings[0].keys()))
        w.writeheader(); w.writerows(rankings)
    print("Wrote sensitivity_rankings.csv\n")

    # ── Console summary ───────────────────────────────────────────────────────
    for lens_label in ("Fan", "PopWt", "System"):
        print(f"── Top 12 most sensitive parameters ({lens_label} lens) ──")
        subset = sorted([r for r in rankings if r["lens"] == lens_label],
                        key=lambda r: r["rank"])[:12]
        print(f"{'Rank':>4} {'Parameter':<36} {'Grp':>6} {'AR':>7} {'SF':>3} "
              f"{'Score':>6} {'Low':>9} {'High':>9} {'CapShift':>9}")
        print("─" * 100)
        for r in subset:
            cs = ("L" if r["cap_shift_low"] else "-") + ("H" if r["cap_shift_high"] else "-")
            print(f"  {r['rank']:>2}  {r['param']:<36} {r['group']:>6}  "
                  f"{r['AR']:>7.4f}  {r['sign_flips']:>2}  {r['sensitivity_score']:>6.4f}  "
                  f"{r['dir_low']:>9}  {r['dir_high']:>9}  {cs:>9}")
        print()

    # Cap-shift report: params that move the optimal cap
    for lens_label in ("Fan", "PopWt", "System"):
        cap_shifters = [r for r in rankings if r["lens"] == lens_label
                        and (r["cap_shift_low"] or r["cap_shift_high"])]
        if cap_shifters:
            print(f"── Parameters that shift the optimal cap ({lens_label} lens) ──")
            for r in sorted(cap_shifters, key=lambda r: r["rank"]):
                sides = []
                if r["cap_shift_low"]:  sides.append("low→shift")
                if r["cap_shift_high"]: sides.append("high→shift")
                print(f"  {r['param']:<40}  {', '.join(sides)}  (base_opt={r['base_opt']})")
        else:
            print(f"── Optimal cap robust on {lens_label} lens ──")
        print()


if __name__ == "__main__":
    # NOTE (2026-05-30 audit fix): a stray `random.seed()` here previously
    # re-seeded from system entropy on every run, silently defeating the
    # `random.seed(42)` at module top (the C1 reproducibility fix) and making
    # sensitivity rankings non-reproducible. Removed so the module-level seed
    # governs the whole run. Results are now bit-for-bit reproducible.
    run_sensitivity()
