"""
Global Sensitivity Analysis — Latin Hypercube + PRCC
=====================================================

Supplements the one-at-a-time (OAT) sweep in sensitivity_sweep.py with a
*global* sensitivity analysis that perturbs ALL parameters simultaneously.

Why this matters
----------------
OAT varies one knob while holding the rest at baseline, so it cannot detect
interaction effects — cases where two parameters jointly move the optimum even
though neither does alone. A reviewer can reasonably argue an OAT-robust result
is still overfit to the *joint* baseline configuration. Global sensitivity
answers the stronger question: across the full joint uncertainty space, does
the bounded-market conclusion survive, and which parameters actually drive it?

Method
------
1. Latin Hypercube Sampling (LHS) draws N configurations across all 31
   parameters at once, using the same low/high ranges as the OAT sweep
   (imported from sensitivity_sweep.PARAM_SPECS).
2. For each configuration, run the simulation for Status Quo and a set of
   bounded caps across representative high-demand levels.
3. Outcome metric Y = (best bounded cap's GR) − (Status Quo GR), averaged over
   demand levels — the policy-relevant *relative advantage*.
4. PRCC (Partial Rank Correlation Coefficient): for each parameter, the rank
   correlation between that parameter and Y after partialling out all other
   parameters. PRCC is the standard global-sensitivity index for monotonic
   nonlinear models (Saltelli; Marino et al. 2008). Sign = direction of effect;
   magnitude = independent influence; |PRCC| near 1 = strong driver.

Robustness outputs
------------------
  - Fraction of joint draws where the bounded market still beats Status Quo
    (the core claim's survival rate under full joint uncertainty)
  - Distribution of the optimal cap across joint draws (is 10-25% stable?)

Outputs:
  global-sensitivity-prcc.csv     — PRCC, t-stat, significance per parameter/lens
  global-sensitivity-samples.csv  — raw LHS draws + outcomes (for reuse)
  chart7_global_prcc.png          — tornado of PRCC drivers
  chart8_optimal_cap_dist.png     — optimal-cap histogram under joint uncertainty
  console summary
"""

import sys
import csv
import copy
import random

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from gre_sim import (
    Rule, simulate, DEFS as BASELINE_DEFS,
    DEFAULT_UTILITY_W, DEFAULT_GR_W,
    DARK_LEAKAGE_BASE, DARK_LEAKAGE_GAMMA,
    SCALPER_DARK_COST, DARK_FRAUD_PENALTY,
    SCALPER_EXIT_FLOOR, SCALPER_EXIT_MIDPOINT, SCALPER_EXIT_STEEPNESS,
    SATURATION_DEMAND,
)
from sensitivity_sweep import PARAM_SPECS

# ── Reproducibility ───────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ── Configuration (override via argv: N, RUNS) ────────────────────────────────
N_SAMPLES = int(sys.argv[1]) if len(sys.argv) > 1 else 400
RUNS      = int(sys.argv[2]) if len(sys.argv) > 2 else 6
DEMANDS   = [2, 5, 10]          # representative high-demand regime
CAPS      = [0.10, 0.20, 0.30]  # bounded caps compared against Status Quo
LENSES    = {"fan_only": "Fan", "pop_wt": "PopWt", "system": "System"}

# Parameter ordering (the PRCC input matrix columns)
PARAM_NAMES = [s["name"] for s in PARAM_SPECS]
RANGES      = [(s["low"], s["high"]) for s in PARAM_SPECS]
GROUP_OF    = {s["name"]: (s.get("group") or "agent") for s in PARAM_SPECS}

UTIL_KEYS = {"w_access": "access", "w_price": "price",
             "w_attend": "attend", "w_resale_opt": "resale_opt"}
GR_KEYS   = {"gr_floor": "floor", "gr_equality": "equality",
             "gr_average": "average", "gr_baseline": "baseline"}


# ── Latin Hypercube Sampler ───────────────────────────────────────────────────
def latin_hypercube(n, ranges):
    """Stratified LHS draw. Returns (n × k) array."""
    k = len(ranges)
    out = np.zeros((n, k))
    for j, (lo, hi) in enumerate(ranges):
        perm = np.random.permutation(n)
        u    = (perm + np.random.uniform(0, 1, n)) / n   # one sample per stratum
        out[:, j] = lo + u * (hi - lo)
    return out


# ── Build full simulate() kwargs from a complete parameter assignment ──────────
def build_kwargs(assignment: dict) -> dict:
    """
    assignment: {param_name: value} for ALL params simultaneously.
    Returns kwargs for simulate() with every knob set. Weight groups
    (util_w, gr_w) are normalised to sum to 1 after sampling.
    """
    defs = copy.deepcopy(BASELINE_DEFS)
    kwargs = dict(
        defs                   = defs,
        scalper_demand_scaling = 0.1,
        sat_demand             = SATURATION_DEMAND,
        scalper_decay          = None,
        dark_leakage_base      = DARK_LEAKAGE_BASE,
        dark_leakage_gamma     = DARK_LEAKAGE_GAMMA,
        scalper_dark_cost      = SCALPER_DARK_COST,
        dark_fraud_penalty     = DARK_FRAUD_PENALTY,
        scalper_exit_floor     = SCALPER_EXIT_FLOOR,
        scalper_exit_midpoint  = SCALPER_EXIT_MIDPOINT,
        scalper_exit_steepness = SCALPER_EXIT_STEEPNESS,
        utility_w              = dict(DEFAULT_UTILITY_W),
        gr_w                   = dict(DEFAULT_GR_W),
    )

    decay_r1 = decay_r2 = None
    util_raw = {}
    gr_raw   = {}

    for name, val in assignment.items():
        group = GROUP_OF[name]
        if group == "agent":
            agent_type, key = name.split(".")
            defs[agent_type][key] = val
        elif group == "structural":
            if name == "scalper_demand_scaling":
                kwargs["scalper_demand_scaling"] = val
            elif name == "sat_demand":
                kwargs["sat_demand"] = val
            elif name == "scalper_decay_r1":
                decay_r1 = val
            elif name == "scalper_decay_r2":
                decay_r2 = val
        elif group in ("dark", "exit"):
            kwargs[name] = val
        elif group == "util_w":
            util_raw[UTIL_KEYS[name]] = val
        elif group == "gr_w":
            gr_raw[GR_KEYS[name]] = val

    # scalper_decay tuple (only override if either sampled)
    if decay_r1 is not None or decay_r2 is not None:
        r1 = decay_r1 if decay_r1 is not None else 0.70
        r2 = decay_r2 if decay_r2 is not None else 0.50
        kwargs["scalper_decay"] = (r1, r2)

    # Normalise weight groups to sum to 1 (so they remain valid weightings)
    if util_raw:
        s = sum(util_raw.values())
        kwargs["utility_w"] = {k: v / s for k, v in util_raw.items()}
    if gr_raw:
        s = sum(gr_raw.values())
        kwargs["gr_w"] = {k: v / s for k, v in gr_raw.items()}

    return kwargs


def normalised_inputs(assignment: dict) -> dict:
    """
    Return the assignment with weight-group members replaced by their
    normalised values — these are what actually enter the model, so PRCC
    should correlate against the normalised inputs, not the raw draws.
    """
    out = dict(assignment)
    util_raw = {n: assignment[n] for n in PARAM_NAMES if GROUP_OF[n] == "util_w"}
    gr_raw   = {n: assignment[n] for n in PARAM_NAMES if GROUP_OF[n] == "gr_w"}
    if util_raw:
        s = sum(util_raw.values())
        for n in util_raw:
            out[n] = util_raw[n] / s
    if gr_raw:
        s = sum(gr_raw.values())
        for n in gr_raw:
            out[n] = gr_raw[n] / s
    return out


# ── PRCC ──────────────────────────────────────────────────────────────────────
def rankdata(a):
    """Average ranks (1..n). Continuous draws rarely tie."""
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    ranks[order] = np.arange(1, len(a) + 1)
    return ranks


def prcc(X, y):
    """
    Partial Rank Correlation Coefficient of each column of X with y.
    Returns (prcc_vec, t_vec, df).
    """
    n, k = X.shape
    Rx = np.column_stack([rankdata(X[:, j]) for j in range(k)])
    ry = rankdata(y)
    coeffs = np.zeros(k)
    tvals  = np.zeros(k)
    df = n - 2 - (k - 1)
    for i in range(k):
        others = [j for j in range(k) if j != i]
        Z = np.column_stack([np.ones(n), Rx[:, others]])
        bi, *_ = np.linalg.lstsq(Z, Rx[:, i], rcond=None)
        res_i  = Rx[:, i] - Z @ bi
        by, *_ = np.linalg.lstsq(Z, ry, rcond=None)
        res_y  = ry - Z @ by
        denom  = (np.std(res_i) * np.std(res_y))
        rho    = float(np.mean((res_i - res_i.mean()) * (res_y - res_y.mean())) / denom) if denom > 0 else 0.0
        coeffs[i] = rho
        tvals[i]  = rho * np.sqrt(df / max(1e-12, 1 - rho ** 2))
    return coeffs, tvals, df


# ── Run the LHS experiment ────────────────────────────────────────────────────
def main():
    print(f"Global sensitivity: LHS N={N_SAMPLES} samples × {len(CAPS)+1} rulesets "
          f"× {len(DEMANDS)} demands × {RUNS} runs "
          f"= {N_SAMPLES*(len(CAPS)+1)*len(DEMANDS)*RUNS:,} simulations")
    print(f"Parameters perturbed simultaneously: {len(PARAM_NAMES)}\n")

    samples = latin_hypercube(N_SAMPLES, RANGES)

    # Per-lens outcome arrays
    adv = {lk: np.zeros(N_SAMPLES) for lk in LENSES}        # best-bounded − SQ advantage
    opt_cap = {lk: np.zeros(N_SAMPLES) for lk in LENSES}    # argmax cap (%)
    beats = {lk: np.zeros(N_SAMPLES, dtype=bool) for lk in LENSES}

    norm_matrix = np.zeros((N_SAMPLES, len(PARAM_NAMES)))   # normalised inputs for PRCC

    sq_rule = Rule("Status Quo", cap=None, plimit=8, dyn_mul=None)
    cap_rules = {c: Rule(f"Bounded {round(c*100)}%", cap=c, plimit=4, dyn_mul=None) for c in CAPS}

    for s in range(N_SAMPLES):
        assignment = {PARAM_NAMES[j]: samples[s, j] for j in range(len(PARAM_NAMES))}
        kwargs = build_kwargs(assignment)

        norm = normalised_inputs(assignment)
        norm_matrix[s, :] = [norm[n] for n in PARAM_NAMES]

        # Mean GR per lens for SQ and each cap, averaged over demands & runs
        def mean_gr(rule):
            acc = {lk: 0.0 for lk in LENSES}
            cnt = 0
            for mul in DEMANDS:
                for _ in range(RUNS):
                    r = simulate(rule, mul, **kwargs)
                    for lk in LENSES:
                        acc[lk] += r[lk]
                    cnt += 1
            return {lk: acc[lk] / cnt for lk in LENSES}

        sq = mean_gr(sq_rule)
        cap_scores = {c: mean_gr(cap_rules[c]) for c in CAPS}

        for lk in LENSES:
            best_c = max(CAPS, key=lambda c: cap_scores[c][lk])
            best_v = cap_scores[best_c][lk]
            adv[lk][s]     = best_v - sq[lk]
            opt_cap[lk][s] = round(best_c * 100)
            beats[lk][s]   = best_v > sq[lk]

        if (s + 1) % max(1, N_SAMPLES // 20) == 0:
            sys.stdout.write(f"\r  {s+1}/{N_SAMPLES} samples")
            sys.stdout.flush()
    print("\n")

    # ── PRCC per lens ─────────────────────────────────────────────────────────
    prcc_rows = []
    crit_t = 2.58  # ~p<0.01 for large df
    for lk, lname in LENSES.items():
        coeffs, tvals, df = prcc(norm_matrix, adv[lk])
        for j, name in enumerate(PARAM_NAMES):
            prcc_rows.append(dict(
                lens        = lname,
                param       = name,
                group       = GROUP_OF[name],
                prcc        = round(float(coeffs[j]), 4),
                t_stat      = round(float(tvals[j]), 3),
                significant = abs(tvals[j]) > crit_t,
                abs_prcc    = round(abs(float(coeffs[j])), 4),
            ))

    with open("global-sensitivity-prcc.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(prcc_rows[0].keys()))
        w.writeheader(); w.writerows(prcc_rows)
    print("Wrote global-sensitivity-prcc.csv")

    # ── Raw samples CSV ───────────────────────────────────────────────────────
    with open("global-sensitivity-samples.csv", "w", newline="") as f:
        fieldnames = PARAM_NAMES + [f"adv_{LENSES[lk]}" for lk in LENSES] \
                                 + [f"optcap_{LENSES[lk]}" for lk in LENSES]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for s in range(N_SAMPLES):
            row = {PARAM_NAMES[j]: round(float(norm_matrix[s, j]), 5) for j in range(len(PARAM_NAMES))}
            for lk in LENSES:
                row[f"adv_{LENSES[lk]}"]    = round(float(adv[lk][s]), 4)
                row[f"optcap_{LENSES[lk]}"] = int(opt_cap[lk][s])
            w.writerow(row)
    print("Wrote global-sensitivity-samples.csv\n")

    # ── Console: robustness of the core claim ─────────────────────────────────
    print("── Core-claim survival under FULL joint parameter uncertainty ──")
    print(f"   (best bounded cap vs Status Quo, averaged over demand {DEMANDS})\n")
    print(f"{'Lens':>8} | {'% draws bounded beats SQ':>26} | {'mean advantage':>15} | {'5th pct':>9} | {'min':>8}")
    print("-" * 78)
    for lk, lname in LENSES.items():
        pct  = 100.0 * beats[lk].mean()
        mean = adv[lk].mean()
        p5   = np.percentile(adv[lk], 5)
        mn   = adv[lk].min()
        print(f"{lname:>8} | {pct:>25.1f}% | {mean:>+15.4f} | {p5:>+9.4f} | {mn:>+8.4f}")

    # ── Console: optimal-cap distribution ─────────────────────────────────────
    print("\n── Optimal cap distribution across joint draws (among 10/20/30%) ──")
    print(f"{'Lens':>8} | " + " | ".join(f"{c}%:>6" for c in [10, 20, 30]))
    print("-" * 40)
    for lk, lname in LENSES.items():
        counts = {c: int(np.sum(opt_cap[lk] == c)) for c in [10, 20, 30]}
        frac   = {c: 100.0 * counts[c] / N_SAMPLES for c in [10, 20, 30]}
        print(f"{lname:>8} | " + " | ".join(f"{frac[c]:>5.1f}%" for c in [10, 20, 30]))

    # ── Console: top PRCC drivers per lens ────────────────────────────────────
    for lk, lname in LENSES.items():
        rows = sorted([r for r in prcc_rows if r["lens"] == lname],
                      key=lambda r: -r["abs_prcc"])[:12]
        print(f"\n── Top global drivers of bounded-vs-SQ advantage ({lname} lens, PRCC) ──")
        print(f"{'Parameter':<40} {'Group':>10} {'PRCC':>8} {'t':>8} {'sig':>4}")
        print("-" * 74)
        for r in rows:
            sig = "***" if r["significant"] else ""
            print(f"{r['param']:<40} {r['group']:>10} {r['prcc']:>+8.3f} {r['t_stat']:>+8.2f} {sig:>4}")

    # ── Chart 7: PRCC tornado (PopWt lens) ────────────────────────────────────
    plt.rcParams.update({
        "figure.facecolor": "#0F1923", "axes.facecolor": "#0F1923",
        "axes.edgecolor": "#3A4A5A", "axes.labelcolor": "#C8D8E8",
        "text.color": "#C8D8E8", "xtick.color": "#8AA0B0", "ytick.color": "#8AA0B0",
        "grid.color": "#1E2E3E", "grid.linestyle": "--", "grid.alpha": 0.6,
        "font.family": "sans-serif", "font.size": 10,
    })
    group_colors = {
        "gr_w": "#F4D03F", "structural": "#5BA4CF", "dark": "#E05C5C",
        "util_w": "#3D9B70", "agent": "#E08B3A", "exit": "#9B59B6",
    }
    pw = sorted([r for r in prcc_rows if r["lens"] == "PopWt"],
                key=lambda r: r["abs_prcc"], reverse=True)[:15]
    pw = pw[::-1]
    names  = [r["param"] for r in pw]
    vals   = [r["prcc"] for r in pw]
    colors = [group_colors.get(r["group"], "#888") for r in pw]

    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.barh(names, vals, color=colors, edgecolor="#0F1923", linewidth=0.5)
    ax.axvline(0, color="#8AA0B0", linewidth=0.8)
    ax.set_xlabel("Partial Rank Correlation Coefficient (PRCC) with bounded-vs-SQ advantage")
    ax.set_title("Global Sensitivity (PRCC): What Actually Drives the Bounded-Market Advantage\n"
                 f"All {len(PARAM_NAMES)} parameters perturbed simultaneously (LHS, N={N_SAMPLES})",
                 fontsize=12, color="#E8F0F8", pad=12)
    legend_patches = [mpatches.Patch(color=v, label=k.replace("_", " ").title())
                      for k, v in group_colors.items()]
    ax.legend(handles=legend_patches, loc="lower right", framealpha=0.15, fontsize=8)
    ax.grid(True, axis="x")
    fig.tight_layout()
    fig.savefig("chart7_global_prcc.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("\nSaved chart7_global_prcc.png")

    # ── Chart 8: optimal-cap distribution + advantage histogram ───────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    caps_list = [10, 20, 30]
    width = 0.25
    x = np.arange(len(caps_list))
    for i, (lk, lname) in enumerate(LENSES.items()):
        fracs = [100.0 * np.sum(opt_cap[lk] == c) / N_SAMPLES for c in caps_list]
        ax.bar(x + (i - 1) * width, fracs, width,
               label=lname, color=list(group_colors.values())[i])
    ax.set_xticks(x); ax.set_xticklabels([f"{c}%" for c in caps_list])
    ax.set_xlabel("Optimal cap"); ax.set_ylabel("% of joint draws")
    ax.set_title("Optimal Cap Under Joint Uncertainty", fontsize=12, color="#E8F0F8")
    ax.legend(framealpha=0.15, fontsize=9); ax.grid(True, axis="y")

    ax = axes[1]
    for i, (lk, lname) in enumerate(LENSES.items()):
        ax.hist(adv[lk], bins=30, alpha=0.5, label=lname,
                color=list(group_colors.values())[i])
    ax.axvline(0, color="#E05C5C", linewidth=1.5, linestyle="--", label="SQ parity")
    ax.set_xlabel("Bounded-market advantage over Status Quo")
    ax.set_ylabel("Count of joint draws")
    ax.set_title("Advantage Distribution (mass right of 0 = robust)", fontsize=12, color="#E8F0F8")
    ax.legend(framealpha=0.15, fontsize=9); ax.grid(True, axis="y")

    fig.tight_layout()
    fig.savefig("chart8_optimal_cap_dist.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved chart8_optimal_cap_dist.png")
    print("\nDone.")


if __name__ == "__main__":
    main()
