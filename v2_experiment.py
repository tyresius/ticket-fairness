"""Model v2 final experiment -- design, criteria and decision rules fixed in
V2_PREREGISTRATION.md (written 15 Nov 2026 before any v2 number was computed).

Writes one row per simulated run (for auditors) to v2-runs-<shard>.csv.gz:
  * whole-market runs: today's market (no cap, 8-ticket limit, 15%/side fees) and
    fixed 0/10/20/30/40% ceilings (4-ticket limit, 5%/side fee cap), mechanics v2,
    under both listing rules ("model" -> S1/S3, "always" -> S2/S4);
  * ex post switch runs: primary sale under c in {10,20,30,40}%, everything after
    under 0% (same seed, same allocation), both listing rules;
  * v1 comparison: 0/20/30% under mechanics v1, model listing.
Fans are scored individually (role_proof.agent_utility, kappa 0) under
  B = resale term from realized recovery, and Z = resale term weight zero,
each with price scores P0 / P1 / P2.  Verdicts: v2_verdicts.py.

Usage:  python3 v2_experiment.py --levels 0,1,2      (indices into LEVELS; shard)
        python3 v2_experiment.py --smoke              (2 seeds, 1 level; prints no results)
"""
from __future__ import annotations

import argparse
import csv
import gzip
import random
import sys
import time

from gre_sim import DEFAULT_UTILITY_W, FACE, FAN_TYPES, Rule, simulate
from role_proof import agent_utility, realized_proceeds, upside_value

LEVELS = [1.5, 2, 3, 4, 5, 6, 7, 8, 10]
N_SEEDS = 300
FEE = dict(secondary_fee_seller=0.05, secondary_fee_buyer=0.05)
SQ = ("SQ", Rule("Status Quo", None, 8, None), {})
CAP_RULES = {c: Rule(f"Bounded {c}% + fee cap", c / 100, 4, None) for c in (0, 10, 20, 30, 40)}
FACE_RULE = CAP_RULES[0]
FORMS = (("P0", "saturating"), ("P1", "linear"), ("P2", "surplus"))
_w = {k: v for k, v in DEFAULT_UTILITY_W.items() if k != "resale_opt"}
ZERO_RESALE_W = {**{k: v / sum(_w.values()) for k, v in _w.items()}, "resale_opt": 0.0}
ROLES = [(t, h) for t in FAN_TYPES for h in (True, False)]


def seed_for(level_index: int, s: int) -> int:
    return 70_000_000 + 10_000 * level_index + s


def channel_value(res):
    """Realized resale-channel value for plan-changed fans (as proceeds_check.py)."""
    proc = realized_proceeds(res)
    vals = []
    for a in res["agents"]:
        if a.type in FAN_TYPES and a.phase == "reselling" and a.tickets > 0:
            net_received = proc.get(a.id, (0, 0.0))[1]
            vals.append(upside_value((net_received / a.tickets - a.cost_basis) / FACE))
    return (sum(vals) / len(vals)) if vals else None


def scalper_roi(u: float) -> float:
    return (u - 0.3) / 0.65 if u >= 0.3 else u - 0.3


def score(res) -> dict:
    """Fan means (overall, by type, by role) under B/Z x P0/P1/P2, plus market metrics."""
    out = {}
    chan = channel_value(res)
    fans = [a for t in FAN_TYPES for a in res["agents"] if a.type == t]
    for v in ("B", "Z"):
        kw = (dict(proceeds=True, resale_override=chan, uw=DEFAULT_UTILITY_W) if v == "B"
              else dict(proceeds=False, uw=ZERO_RESALE_W))
        for code, form in FORMS:
            us = [agent_utility(a, res, 0.0, price_form=form, **kw) for a in fans]
            tag = f"{v}_{code}"
            out[f"fan_{tag}"] = sum(us) / len(us)
            by_type, by_role = {t: [] for t in FAN_TYPES}, {r: [] for r in ROLES}
            for a, u in zip(fans, us):
                by_type[a.type].append(u)
                by_role[(a.type, a.primary_holder)].append(u)
            for t in FAN_TYPES:
                out[f"type_{t}_{tag}"] = sum(by_type[t]) / len(by_type[t])
            for (t, h) in ROLES:
                xs = by_role[(t, h)]
                out[f"role_{t}_{'holder' if h else 'havenot'}_{tag}"] = (sum(xs) / len(xs)) if xs else ""
    sc = [a for a in res["agents"] if a.type == "scalper"]
    o = res["outcomes"]
    out.update(
        scalper_util=o["scalper"]["utility"],
        scalper_roi=scalper_roi(o["scalper"]["utility"]),
        scalper_listed=sum(a.resale_tickets for a in sc),
        dark_routed=res["dark_sold"] + res["dark_unmatched"],
        dark_sold=res["dark_sold"],
        secondary_sold=res["secondary_sold"],
        seats=res["attend"],
        wasted=res["wasted"],
        channel_value=chan if chan is not None else "",
        **{f"access_{t}": o[t]["got"] / o[t]["total"] for t in FAN_TYPES},
    )
    return {k: (round(v, 6) if isinstance(v, float) else v) for k, v in out.items()}


def jobs():
    """(label, mechanics, listing, primary rule, continuation rule or None, fees)."""
    for listing in ("model", "always"):
        yield ("SQ", "v2", listing, SQ[1], None, SQ[2])
        for c, rule in CAP_RULES.items():
            yield (f"cap{c}", "v2", listing, rule, None, FEE)
        for c in (10, 20, 30, 40):
            yield (f"cap{c}->cap0", "v2", listing, CAP_RULES[c], FACE_RULE, FEE)
    for c in (0, 20, 30):
        yield (f"cap{c}", "v1", "model", CAP_RULES[c], None, FEE)


def run(level_indices, n_seeds, path, verbose=True):
    t0 = time.time()
    writer, fh = None, gzip.open(path, "wt", newline="") if path else None
    n = 0
    for li in level_indices:
        d = LEVELS[li]
        for s in range(n_seeds):
            seed = seed_for(li, s)
            for label, mech, listing, rule, cont, fees in jobs():
                random.seed(seed)
                res = simulate(rule, d, return_agents=True, continuation_rule=cont,
                               fan_listing=listing, mechanics=mech, **fees)
                row = dict(arm=label, mechanics=mech, listing=listing, demand=d, seed=s, **score(res))
                if fh:
                    if writer is None:
                        writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
                        writer.writeheader()
                    writer.writerow(row)
                n += 1
            if verbose and (s + 1) % 25 == 0:
                sys.stdout.write(f"\r  demand {d:>4}: seed {s + 1}/{n_seeds}  ({time.time() - t0:5.0f}s)")
                sys.stdout.flush()
        if verbose:
            print()
    if fh:
        fh.close()
    return n


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default=",".join(str(i) for i in range(len(LEVELS))))
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        t = time.time()
        n = run([4], 2, None, verbose=False)
        print(f"smoke: {n} runs scored in {time.time() - t:.1f}s; no results printed by design")
        sys.exit(0)
    idx = [int(x) for x in a.levels.split(",")]
    path = f"v2-runs-{'-'.join(str(i) for i in idx)}.csv.gz"
    n = run(idx, N_SEEDS, path)
    print(f"wrote {n} runs to {path}")
