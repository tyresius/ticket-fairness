"""
Emergent Weight Discovery — Co-evolutionary Tournament
======================================================

Three fan agent populations (mega_fan, committed_casual, average_buyer) evolve
simultaneously. Each agent type optimizes its own behavioral parameters to
maximize its own utility under a bounded ruleset. Scalper parameters are fixed
(definitional, not behavioral choices).

Co-evolution mechanism:
  - Each individual is evaluated against the current generation's MEAN
    parameters of all other agent types (cooperative co-evolution)
  - All three populations evolve in parallel each generation
  - Scalper parameters fixed throughout

Sim logic is imported from gre_sim.py — no duplicated simulate() here.
As of 2026-04-21 this uses the canonical simulation (dark market leakage,
0.1x scalper pop scaling, demand-sensitive scalper ask/decay, static `margin`
in necessity resale). Previous results from the pre-sync version diverge
meaningfully and should be rerun.

Outputs:
  weight_discovery_generations_b{cap}.csv  — fitness per population per generation
  weight_discovery_results_b{cap}.csv      — hand-tuned vs emerged parameters + GR impact
  console summary
"""

import csv
import copy
import math
import random

# C1 fix (2026-04-27): fixed seed for reproducibility.
random.seed(42)

from gre_sim import simulate, Rule, DEFS as BASELINE_DEFS


# ── Evolution configuration ───────────────────────────────────────────────────
EVOLVE_AGENTS = ["mega_fan", "committed_casual", "average_buyer"]

# Parameters allowed to evolve and their (min, max) bounds
PARAM_BOUNDS = {
    "flip_chance":             (0.001, 0.50),
    "plan_change_rate":        (0.02,  0.55),
    "resale_effort_threshold": (0.0,   0.30),
    "flip_margin_threshold":   (0.0,   1.00),
}

# Fixed-identity parameters: not evolved
FIXED_PARAMS = ["speed", "max_pay_mul", "attend_base", "wanted"]

# Hyperparameters
POP_SIZE       = 30    # individuals per agent type
N_GENERATIONS  = 40
N_EVAL_MARKETS = 15    # markets per individual evaluation
SURVIVAL_RATE  = 0.30  # top 30% survive unchanged
MUTATION_RATE  = 0.40  # probability each param is mutated per offspring
MUTATION_SCALE = 0.12  # std dev of mutation as fraction of param range
DEMAND_POOL    = [1, 2, 3, 5, 8, 10]


# ── Individual / population helpers ───────────────────────────────────────────
def init_individual(agent_type: str) -> dict:
    """Start near the baseline with uniform random variation."""
    base   = BASELINE_DEFS[agent_type]
    result = {}
    for key, (lo, hi) in PARAM_BOUNDS.items():
        spread = (hi - lo) * 0.25
        result[key] = min(hi, max(lo, base[key] + random.uniform(-spread, spread)))
    result["fitness"] = 0.0
    return result

def pop_mean(population: list) -> dict:
    """Mean parameter values across a population."""
    return {key: sum(ind[key] for ind in population) / len(population)
            for key in PARAM_BOUNDS}

def make_def(agent_type: str, params: dict) -> dict:
    """Merge evolved params with fixed-identity params from baseline."""
    d = copy.copy(BASELINE_DEFS[agent_type])
    for key in PARAM_BOUNDS:
        d[key] = params[key]
    return d

def crossover(p1: dict, p2: dict) -> dict:
    """Uniform crossover: each gene comes from a random parent."""
    child = {}
    for key in PARAM_BOUNDS:
        child[key] = p1[key] if random.random() < 0.5 else p2[key]
    child["fitness"] = 0.0
    return child

def mutate(individual: dict) -> dict:
    """Gaussian mutation, clamped to bounds."""
    result = copy.copy(individual)
    for key, (lo, hi) in PARAM_BOUNDS.items():
        if random.random() < MUTATION_RATE:
            scale = (hi - lo) * MUTATION_SCALE
            result[key] = min(hi, max(lo, result[key] + random.gauss(0, scale)))
    result["fitness"] = 0.0
    return result

def reproduce(population: list) -> list:
    """Select survivors, generate offspring to refill population."""
    population.sort(key=lambda x: -x["fitness"])
    n_survive  = max(2, round(len(population) * SURVIVAL_RATE))
    survivors  = population[:n_survive]
    offspring  = []
    while len(offspring) < len(population) - n_survive:
        p1, p2 = random.choices(survivors, k=2)
        child  = mutate(crossover(p1, p2))
        offspring.append(child)
    return survivors + offspring


# ── Fitness evaluation ────────────────────────────────────────────────────────
def evaluate_individual(individual: dict, agent_type: str,
                        gen_means: dict, rule: Rule) -> float:
    """
    Run N_EVAL_MARKETS markets at random demand levels.
    Focal agent uses individual's params; others use generation mean.
    Returns mean utility for the focal agent type.
    """
    defs = {}
    for agent in EVOLVE_AGENTS:
        params = individual if agent == agent_type else gen_means[agent]
        defs[agent] = make_def(agent, params)
    defs["scalper"] = copy.copy(BASELINE_DEFS["scalper"])

    utilities = []
    for _ in range(N_EVAL_MARKETS):
        mul    = random.choice(DEMAND_POOL)
        result = simulate(rule, mul, defs)
        utilities.append(result["outcomes"][agent_type]["utility"])
    return sum(utilities) / len(utilities)


# ── Main evolution loop ───────────────────────────────────────────────────────
def run_discovery(cap: float = 0.25):
    eval_rule = Rule(f"Bounded {round(cap*100)}%", cap=cap, plimit=4, dyn_mul=None)
    print(f"Initializing {POP_SIZE} individuals × {len(EVOLVE_AGENTS)} populations")
    print(f"Running {N_GENERATIONS} generations × {N_EVAL_MARKETS} eval markets")
    total = N_GENERATIONS * POP_SIZE * len(EVOLVE_AGENTS) * N_EVAL_MARKETS
    print(f"Total simulations: ~{total:,}\n")

    # Initialize populations
    populations = {agent: [init_individual(agent) for _ in range(POP_SIZE)]
                   for agent in EVOLVE_AGENTS}

    gen_log = []

    for gen in range(N_GENERATIONS):
        gen_means = {agent: pop_mean(populations[agent]) for agent in EVOLVE_AGENTS}

        for agent in EVOLVE_AGENTS:
            for ind in populations[agent]:
                ind["fitness"] = evaluate_individual(ind, agent, gen_means, eval_rule)

        stats = {}
        for agent in EVOLVE_AGENTS:
            fits = [ind["fitness"] for ind in populations[agent]]
            mean = sum(fits) / len(fits)
            stats[agent] = dict(
                mean = mean,
                best = max(fits),
                std  = math.sqrt(sum((f - mean) ** 2 for f in fits) / len(fits)),
            )

        gen_log.append(dict(
            generation = gen,
            **{f"{a}_mean_fitness": round(stats[a]["mean"], 4) for a in EVOLVE_AGENTS},
            **{f"{a}_best_fitness": round(stats[a]["best"], 4) for a in EVOLVE_AGENTS},
            **{f"{a}_fitness_std":  round(stats[a]["std"],  4) for a in EVOLVE_AGENTS},
        ))

        if gen % 5 == 0 or gen == N_GENERATIONS - 1:
            parts = [f"{a[:2].upper()}:{stats[a]['mean']:.3f}(+{stats[a]['best']:.3f})"
                     for a in EVOLVE_AGENTS]
            print(f"  Gen {gen+1:>3}/{N_GENERATIONS}  " + "  ".join(parts))

        if gen < N_GENERATIONS - 1:
            for agent in EVOLVE_AGENTS:
                populations[agent] = reproduce(populations[agent])

    print()

    # ── Extract converged parameters (mean of top 30%) ───────────────────────
    emerged = {}
    for agent in EVOLVE_AGENTS:
        sorted_pop = sorted(populations[agent], key=lambda x: -x["fitness"])
        top_n      = max(3, round(len(sorted_pop) * SURVIVAL_RATE))
        top        = sorted_pop[:top_n]
        emerged[agent] = {key: round(sum(ind[key] for ind in top) / len(top), 4)
                          for key in PARAM_BOUNDS}

    # ── Write generation log ──────────────────────────────────────────────────
    cap_tag = round(cap * 100)
    with open(f"weight_discovery_generations_b{cap_tag}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(gen_log[0].keys()))
        w.writeheader(); w.writerows(gen_log)
    print(f"Wrote weight_discovery_generations_b{cap_tag}.csv")

    # ── Compare emerged vs hand-tuned: parameter table ───────────────────────
    print("\n── Emerged vs Hand-tuned Parameters ──")
    print(f"{'Agent':<20} {'Parameter':<30} {'Hand-tuned':>12} {'Emerged':>10} "
          f"{'Δ%':>9}  {'Direction'}")
    print("─" * 95)

    result_rows = []
    for agent in EVOLVE_AGENTS:
        for param, (lo, hi) in PARAM_BOUNDS.items():
            baseline_val = BASELINE_DEFS[agent][param]
            emerged_val  = emerged[agent][param]
            if baseline_val != 0:
                pct = (emerged_val - baseline_val) / baseline_val * 100
            else:
                pct = float("inf") if emerged_val > 0 else 0
            direction = ("↑ higher" if pct > 10 else
                         "↓ lower"  if pct < -10 else
                         "≈ stable")
            print(f"  {agent:<18} {param:<30} {baseline_val:>12.4f} {emerged_val:>10.4f} "
                  f"{pct:>+8.1f}%  {direction}")
            result_rows.append(dict(
                agent=agent, parameter=param,
                hand_tuned=baseline_val, emerged=emerged_val,
                pct_change=round(pct, 1), direction=direction,
                param_lo=lo, param_hi=hi,
            ))
        print()

    # ── GR score comparison: hand-tuned vs emerged ────────────────────────────
    print(f"── GR Score Comparison: Hand-tuned vs Emerged Weights (eval cap: {cap_tag}%) ──")
    print("(Eval cap and Status Quo, averaged over 30 runs per demand level)\n")

    comparison_rules = {
        f"bounded_{cap_tag}": eval_rule,
        "status_quo":         Rule("Status Quo",  cap=None, plimit=8, dyn_mul=None),
    }
    comparison_demands = [1, 2, 5, 10]
    N_COMP = 30

    def build_defs(weight_set):
        defs = {}
        for agent in EVOLVE_AGENTS:
            if weight_set == "baseline":
                defs[agent] = copy.copy(BASELINE_DEFS[agent])
            else:
                defs[agent] = make_def(agent, weight_set[agent])
        defs["scalper"] = copy.copy(BASELINE_DEFS["scalper"])
        return defs

    gr_rows = []
    for label, weight_set in [("hand_tuned", "baseline"), ("emerged", emerged)]:
        defs = build_defs(weight_set)
        for rid, rule in comparison_rules.items():
            for mul in comparison_demands:
                runs = [simulate(rule, mul, defs) for _ in range(N_COMP)]
                fan  = round(sum(r["fan_only"] for r in runs) / N_COMP, 4)
                pwt  = round(sum(r["pop_wt"]   for r in runs) / N_COMP, 4)
                sys_ = round(sum(r["system"]   for r in runs) / N_COMP, 4)
                gr_rows.append(dict(weights=label, ruleset=rid, demand=mul,
                                    gr_fan=fan, gr_popwt=pwt, gr_system=sys_))

    print(f"{'':30} {'— Fan GR ——————':17} {'— PopWt GR ————':17} {'— System GR ———':17}")
    print(f"{'Demand / Ruleset':<30} {'Hand':>7}  {'Emerged':>7}  {'Δ':>5}  "
          f"{'Hand':>7}  {'Emerged':>7}  {'Δ':>5}  "
          f"{'Hand':>7}  {'Emerged':>7}  {'Δ':>5}")
    print("─" * 100)

    bounded_key = f"bounded_{cap_tag}"
    for mul in comparison_demands:
        for rid in [bounded_key, "status_quo"]:
            ht = next(r for r in gr_rows if r["weights"]=="hand_tuned"
                      and r["ruleset"]==rid and r["demand"]==mul)
            em = next(r for r in gr_rows if r["weights"]=="emerged"
                      and r["ruleset"]==rid and r["demand"]==mul)
            label = f"  {mul}x  {rid.replace('_',' '):<20}"
            print(f"{label:<30} "
                  f"{ht['gr_fan']:>7.4f}  {em['gr_fan']:>7.4f}  "
                  f"{em['gr_fan']-ht['gr_fan']:>+5.3f}  "
                  f"{ht['gr_popwt']:>7.4f}  {em['gr_popwt']:>7.4f}  "
                  f"{em['gr_popwt']-ht['gr_popwt']:>+5.3f}  "
                  f"{ht['gr_system']:>7.4f}  {em['gr_system']:>7.4f}  "
                  f"{em['gr_system']-ht['gr_system']:>+5.3f}")
        print()

    # ── Bounded market advantage under emerged weights ────────────────────────
    print(f"── Bounded {cap_tag}% advantage over Status Quo (Fan GR) ──")
    print(f"{'Demand':>8} {'Hand-tuned Δ':>14} {'Emerged Δ':>12} {'Change':>10}")
    print("─" * 50)
    for mul in comparison_demands:
        ht_b = next(r for r in gr_rows if r["weights"]=="hand_tuned"
                    and r["ruleset"]==bounded_key and r["demand"]==mul)["gr_fan"]
        ht_s = next(r for r in gr_rows if r["weights"]=="hand_tuned"
                    and r["ruleset"]=="status_quo" and r["demand"]==mul)["gr_fan"]
        em_b = next(r for r in gr_rows if r["weights"]=="emerged"
                    and r["ruleset"]==bounded_key and r["demand"]==mul)["gr_fan"]
        em_s = next(r for r in gr_rows if r["weights"]=="emerged"
                    and r["ruleset"]=="status_quo" and r["demand"]==mul)["gr_fan"]
        ht_adv = ht_b - ht_s
        em_adv = em_b - em_s
        print(f"  {mul:>5}x  {ht_adv:>+13.4f}  {em_adv:>+11.4f}  "
              f"{em_adv-ht_adv:>+9.4f}")

    # ── Biggest movers ────────────────────────────────────────────────────────
    print("\n── Largest Parameter Shifts (emerged vs hand-tuned) ──")
    movers = sorted(result_rows, key=lambda r: abs(r["pct_change"]), reverse=True)
    for r in movers[:8]:
        if abs(r["pct_change"]) < 5: break
        print(f"  {r['agent']:<20} {r['parameter']:<30} "
              f"{r['hand_tuned']:.4f} → {r['emerged']:.4f}  ({r['pct_change']:+.1f}%)  "
              f"{r['direction']}")

    # ── Write results CSV ─────────────────────────────────────────────────────
    for row in result_rows:
        ht_b = next(r for r in gr_rows if r["weights"]=="hand_tuned"
                    and r["ruleset"]==bounded_key and r["demand"]==5)["gr_fan"]
        em_b = next(r for r in gr_rows if r["weights"]=="emerged"
                    and r["ruleset"]==bounded_key and r["demand"]==5)["gr_fan"]
        row[f"gr_fan_b{cap_tag}_d5_hand_tuned"] = ht_b
        row[f"gr_fan_b{cap_tag}_d5_emerged"]    = em_b

    with open(f"weight_discovery_results_b{cap_tag}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(result_rows[0].keys()))
        w.writeheader(); w.writerows(result_rows)
    print(f"\nWrote weight_discovery_results_b{cap_tag}.csv")

    return emerged


if __name__ == "__main__":
    import sys as _sys
    _cap = float(_sys.argv[1]) if len(_sys.argv) > 1 else 0.25
    run_discovery(cap=_cap)
