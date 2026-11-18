"""
Role-proof test — design and criteria in ROLE_PROOF_TEST.md (fixed before any run;
decisions approved 5 Nov 2026).

A rule is role-proof if the groups it creates still accept it after tickets are
allocated, not only from behind the veil. For each demand level and each rule
R in the menu:

  * Ex ante (veil): the whole market runs under one rule; roles = fan types.
  * Ex post: the primary sale runs under R; then, with tickets where they
    landed, the rest of the market runs under every rule X in the menu (same
    seed, so the allocation is identical). Roles = holders and have-nots of
    each fan type.

Each fan is scored individually with the model's own utility formula. A role's
regret = its utility under its favourite rule minus its utility under R. A
rule's role-proofness gap = the largest regret any role has; smaller is more
role-proof. Holders' weight on the resale option is scaled by (1 + kappa) and
the weights renormalised, so kappa = 0 is pure positional interest. The
"proceeds" variant scores fans who resold on their realized net upside instead
of the option value.

Usage:
    python3 role_proof.py                 # full run
    python3 role_proof.py --smoke         # 1 demand level, 2 seeds: mechanics only
Writes role-proof-summary.csv and role-proof-roles.csv (full run only).
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import sys
import time
from collections import defaultdict

from gre_sim import (BASELINE_SECONDARY_FRAUD_PENALTY, DEFAULT_UTILITY_W, FACE,
                     FAN_TYPES, simulate)
from sweep_config import BOUNDED_LABELS, DEMAND_LEVELS, RUNS_PER_POINT, build_series

MENU_LABELS = ["Status Quo", "UK Face Value"] + BOUNDED_LABELS
KAPPAS = (0.0, 0.5, 1.0)
VARIANTS = [(k, False) for k in KAPPAS] + [(k, True) for k in KAPPAS]   # (kappa, proceeds)
MAIN = (0.0, False)                   # the variant the pre-stated verdict applies to
TOLERANCE = 0.01                      # the sweep's stated margin of error
PASS_CAPS = ("Bounded 10%", "Bounded 15%", "Bounded 20%")
OVERSUBSCRIBED = [d for d in DEMAND_LEVELS if d > 1]
MISSED_UTILITY = 0.02                 # the model's floor for a fan with no ticket
ROLES = [(t, h) for t in FAN_TYPES for h in (True, False)]   # (type, holder?)


def menu_rules():
    by_label = {s["label"]: s for s in build_series()}
    out = []
    for lab in MENU_LABELS:
        s = by_label[lab]
        assert not s.get("sim_kwargs"), f"{lab}: fee-cap regimes are out of v1"
        assert not s["rule"].dyn_mul, f"{lab}: dynamic pricing is out of v1"
        out.append(s["rule"])
    return out


def run_seed(d_idx: int, r_idx: int, s: int) -> int:
    """One fixed seed per (demand, primary rule, run): every continuation of
    that run starts from the identical primary allocation."""
    return 1_000_003 * s + 1_009 * d_idx + 17 * r_idx + 7


def upside_value(net_upside: float) -> float:
    """gre_sim's mapping from net resale upside (fraction of face) to the
    resale term's value (lines ~769-790)."""
    return max(0.05, 0.20 + net_upside) if net_upside <= 0 else min(0.70, 0.20 + net_upside * 2.0)


def resale_option(crule, fee_seller: float) -> float:
    """Option value of being able to resell under the rule in force."""
    if crule.cap is None:
        return 0.70
    return upside_value(crule.cap - fee_seller)


def realized_proceeds(res: dict) -> dict:
    """Seller id -> (tickets sold, total net proceeds), from the sold listings.
    Cached on the result."""
    if "_proceeds" not in res:
        fee = res["secondary_fee_seller"]
        out = defaultdict(lambda: [0, 0.0])
        for li in res["listings"]:
            if li.sold:
                rec = out[li.seller.id]
                rec[0] += 1
                rec[1] += li.final_price * (1 - fee)
        res["_proceeds"] = dict(out)
    return res["_proceeds"]


PRICE_FORMS = ("saturating", "linear", "surplus")   # PRICE_SCORE_CHECK.md: P0, P1, P2


def price_score(paid: float, wtp_mul: float, form: str = "saturating", resent: float = 0.0) -> float:
    """Price term for one fan who paid `paid` (PRICE_SCORE_CHECK.md).
    saturating (P0) = the model's own: 1 at face, 0 at 2x face and above.
    linear (P1)     = the same slope with no floor.
    surplus (P2)    = share of the fan's value kept: 1 at face, 0 at wtp_mul x face.
    `resent` = dynamic pricing's resented surcharge (gre_sim.py:745-748), subtracted
    under every form; 0 for every rule in the role-proof menu."""
    if paid <= 0:
        return 0.0
    if form == "saturating":
        ps = max(0.0, 1 - (paid - FACE) / FACE)
        return max(0.0, ps - resent) if resent else ps
    if form == "linear":
        return 1 - (paid - FACE) / FACE - resent
    if form == "surplus":
        wtp = wtp_mul * FACE
        return (wtp - paid) / (wtp - FACE) - resent
    raise ValueError(f"unknown price form {form!r}")


def agent_utility(a, res: dict, kappa: float = 0.0, proceeds: bool = False,
                  uw: dict = DEFAULT_UTILITY_W, price_form: str = "saturating",
                  resent: float = 0.0, resale_override=None) -> float:
    """One fan's utility, using the model's components at the individual level:
    access, price paid, attendance, the resale term (only if holding a ticket),
    and the dark-market / secondary fraud penalties."""
    has_ticket = a.tickets > 0 or a.phase in ("bought_secondary", "bought_dark")
    if not has_ticket:
        return MISSED_UTILITY
    if a.phase == "bought_secondary":
        paid = a.secondary_price * (1 + res["secondary_fee_buyer"])
    else:
        paid = a.secondary_price or a.cost_basis or 0
    ps = price_score(paid, a.def_["max_pay_mul"], price_form, resent)
    attend = 1.0 if a.attending else 0.0
    crule = res["continuation_rule"]

    sold = realized_proceeds(res).get(a.id) if proceeds else None
    if sold and sold[0] > 0:
        resale = upside_value((sold[1] / sold[0] - a.cost_basis) / FACE)
    else:
        # resale_override (proceeds_check.py): an empirical value for the resale
        # channel in place of the formula option; None = the formula, as before.
        resale = resale_option(crule, res["secondary_fee_seller"]) if resale_override is None else resale_override

    w = dict(uw)
    if a.primary_holder and kappa:
        w["resale_opt"] *= (1 + kappa)
    total_w = sum(w.values())
    w = {k: v / total_w for k, v in w.items()}

    u = w["access"] + ps * w["price"] + attend * w["attend"] + resale * w["resale_opt"]
    if a.dark_market:
        u -= res["dark_fraud_penalty"]
    if crule.cap is None and a.phase == "bought_secondary":
        u -= BASELINE_SECONDARY_FRAUD_PENALTY
    u -= res["systemic_penalty"]
    return max(0.0, u)


def price_form_of(v) -> str:
    """Variants are (kappa, proceeds) or (kappa, proceeds, price_form)."""
    return v[2] if len(v) > 2 else "saturating"


def run(demands, n_seeds, variants=VARIANTS, verbose=True):
    rules = menu_rules()
    names = [r.name for r in rules]
    # ex_post[v][d][R][X][role] -> list of per-seed role means
    ex_post = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
    # ex_ante[(proceeds, price_form)][d][R][type] -> per-seed type means (whole market under R, kappa 0)
    ex_ante = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    # keep[v][d][R][X] -> [agents preferring to keep R, agents compared]
    keep = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0, 0]))))

    t0 = time.time()
    for d_idx, d in ((DEMAND_LEVELS.index(d), d) for d in demands):
        for r_idx, R in enumerate(rules):
            for s in range(n_seeds):
                per_x = {}
                for X in rules:
                    random.seed(run_seed(d_idx, r_idx, s))
                    per_x[X.name] = simulate(R, d, continuation_rule=X, return_agents=True)
                fans_keep = [a for a in per_x[R.name]["agents"] if a.type in FAN_TYPES]
                for v in variants:
                    k, pr, pf = v[0], v[1], price_form_of(v)
                    u_keep = {a.id: agent_utility(a, per_x[R.name], k, pr, price_form=pf) for a in fans_keep}
                    for X in rules:
                        res = per_x[X.name]
                        buckets = defaultdict(list)
                        for a in res["agents"]:
                            if a.type not in FAN_TYPES:
                                continue
                            u = agent_utility(a, res, k, pr, price_form=pf)
                            buckets[(a.type, a.primary_holder)].append(u)
                            if X.name != R.name:
                                tally = keep[v][d][R.name][X.name]
                                tally[0] += u_keep[a.id] > u
                                tally[1] += 1
                        for role in ROLES:
                            if buckets[role]:
                                ex_post[v][d][R.name][X.name][role].append(
                                    sum(buckets[role]) / len(buckets[role]))
                # ex ante: whole market under R (the R -> R run), kappa 0
                res = per_x[R.name]
                for pr, pf in sorted({(v[1], price_form_of(v)) for v in variants}):
                    for t in FAN_TYPES:
                        grp = [a for a in res["agents"] if a.type == t]
                        ex_ante[(pr, pf)][d][R.name][t].append(
                            sum(agent_utility(a, res, 0.0, pr, price_form=pf) for a in grp) / len(grp))
            if verbose:
                sys.stdout.write(f"\r  demand {d:>4}  rule {r_idx + 1:>2}/{len(rules)}  "
                                 f"elapsed {time.time() - t0:6.0f}s")
                sys.stdout.flush()
    if verbose:
        print()
    return dict(names=names, ex_post=ex_post, ex_ante=ex_ante, keep=keep, n_seeds=n_seeds)


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def summarise(out, demands, variants=VARIANTS, min_presence=0.9):
    names, n = out["names"], out["n_seeds"]
    rows, role_rows = [], []
    for v in variants:
        k, pr, pf = v[0], v[1], price_form_of(v)
        tag = {"price_form": pf} if len(v) > 2 else {}
        for d in demands:
            # Ex ante: each type's regret against its favourite whole-market rule.
            u_ante = {R: {t: mean(out["ex_ante"][(pr, pf)][d][R][t]) for t in FAN_TYPES} for R in names}
            best_ante = {t: max(u_ante[R][t] for R in names) for t in FAN_TYPES}
            gap_ante = {R: max(best_ante[t] - u_ante[R][t] for t in FAN_TYPES) for R in names}
            # Ex post: each role's regret, after allocation under R, against its
            # favourite continuation. Roles present in < min_presence of runs
            # are skipped (and named in the output).
            gap_post, worst_role, skipped = {}, {}, {}
            for R in names:
                regrets, skip = {}, []
                for role in ROLES:
                    if len(out["ex_post"][v][d][R][R][role]) < min_presence * n:
                        skip.append(f"{role[0]}/{'holder' if role[1] else 'have-not'}")
                        continue
                    u = {X: mean(out["ex_post"][v][d][R][X][role]) for X in names}
                    regrets[role] = max(u.values()) - u[R]
                    for X in names:
                        role_rows.append(dict(kappa=k, proceeds=pr, **tag, demand=d, primary_rule=R,
                                              continuation_rule=X, fan_type=role[0],
                                              role="holder" if role[1] else "have-not",
                                              mean_utility=round(u[X], 5),
                                              seeds=len(out["ex_post"][v][d][R][X][role])))
                gap_post[R] = max(regrets.values()) if regrets else float("nan")
                worst = max(regrets, key=regrets.get) if regrets else None
                worst_role[R] = f"{worst[0]}/{'holder' if worst[1] else 'have-not'}" if worst else ""
                skipped[R] = ";".join(skip)
            min_ante = min(gap_ante.values())
            min_post = min(g for g in gap_post.values() if not math.isnan(g))
            for R in names:
                kv_sq = out["keep"][v][d][R].get("Status Quo", [0, 0])
                kv_fv = out["keep"][v][d][R].get("UK Face Value", [0, 0])
                rows.append(dict(
                    kappa=k, proceeds=pr, **tag, demand=d, rule=R,
                    ex_ante_gap=round(gap_ante[R], 5), ex_post_gap=round(gap_post[R], 5),
                    role_proof=(gap_ante[R] <= min_ante + TOLERANCE
                                and gap_post[R] <= min_post + TOLERANCE),
                    worst_role_ex_post=worst_role[R],
                    keep_vs_status_quo=round(kv_sq[0] / kv_sq[1], 4) if kv_sq[1] else "",
                    keep_vs_face_value=round(kv_fv[0] / kv_fv[1], 4) if kv_fv[1] else "",
                    roles_skipped=skipped[R]))
    return rows, role_rows


def role_proof_levels(rows, variant=MAIN):
    """(levels where a 10-20% cap is role-proof, levels present, report lines)."""
    k, pr, pf = variant[0], variant[1], price_form_of(variant)
    lines, passed = [], 0
    for d in OVERSUBSCRIBED:
        level = [r for r in rows if r["kappa"] == k and r["proceeds"] == pr
                 and r.get("price_form", "saturating") == pf and r["demand"] == d]
        if not level:
            continue
        proof = [r["rule"] for r in level if r["role_proof"]]
        ok = any(c in proof for c in PASS_CAPS)
        passed += ok
        ante_best = min(level, key=lambda r: r["ex_ante_gap"])["rule"]
        post_best = min(level, key=lambda r: r["ex_post_gap"])["rule"]
        lines.append(f"  demand {d:>4}: role-proof {proof or ['none']}  "
                     f"| ex-ante best {ante_best}, ex-post best {post_best}"
                     f"{'  <- winners differ' if ante_best != post_best else ''}")
    return passed, len(lines), lines


def verdict(rows, variant=MAIN):
    """Apply the pre-stated criteria (ROLE_PROOF_TEST.md). The pass/kill
    verdict is defined for MAIN only; other variants are reported the same way."""
    passed, n, lines = role_proof_levels(rows, variant)
    tag = "PASS" if passed >= 6 else "KILL"
    lines.append(f"  10-20% cap role-proof at {passed} of {n} oversubscribed levels"
                 + (f" -> {tag} (pass needs 6 of 9)" if variant == MAIN else " (variant; no verdict)"))
    return "\n".join(lines)


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="mechanics check only: demand 5, 2 seeds, no CSVs, no verdict")
    ap.add_argument("--seeds", type=int, default=RUNS_PER_POINT)
    a = ap.parse_args()
    if a.smoke:
        t = time.time()
        out = run([5], 2, verbose=False)
        rows, role_rows = summarise(out, [5])
        print(f"smoke: {len(rows)} summary rows, {len(role_rows)} role rows, "
              f"{time.time() - t:.1f}s; no results printed by design")
        sys.exit(0)
    print(f"Role-proof test: {len(MENU_LABELS)} rules x {len(MENU_LABELS)} continuations x "
          f"{len(DEMAND_LEVELS)} demand levels x {a.seeds} seeds, {len(VARIANTS)} scorings")
    out = run(DEMAND_LEVELS, a.seeds)
    rows, role_rows = summarise(out, DEMAND_LEVELS)
    write_csv("role-proof-summary.csv", rows)
    write_csv("role-proof-roles.csv", role_rows)
    print("Wrote role-proof-summary.csv and role-proof-roles.csv\n")
    print("Verdict against the pre-stated criteria (main run: kappa = 0, no proceeds):")
    print(verdict(rows))
    for v in VARIANTS:
        if v != MAIN:
            print(f"\nVariant kappa = {v[0]}, proceeds = {v[1]}:")
            print(verdict(rows, v))
