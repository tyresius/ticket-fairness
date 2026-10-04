---
description: Run the 6-point model-validation checklist on a claim before it is quoted anywhere
argument-hint: <the claim or result to validate>
---
Run the model-validation checklist on this claim before it is quoted anywhere: $ARGUMENTS

For each item, read the relevant code and data (don't answer from memory),
and give a verdict: SATISFIED / CAVEAT / FAILS, with file:line evidence.

1. Real alternative — Who decides or pays, and what would they do instead?
   Is that alternative modeled, calibrated to real data, and the thing we
   compare against? Or did we pick a comparator that flatters the pitch?
2. Independent observer — Is the outcome measured by something the
   mechanism doesn't itself use to make decisions (separate accounting,
   ground-truth check, empirical anchor)? Or does the model grade its own work?
3. Symmetric scrutiny — Were the baselines and competitors audited as hard
   as our design (calibration, physical/economic validity, best-case
   operation)? Any strawman?
4. Information leak — List what each agent or mechanism knows in the
   model vs what it could know in reality. Flag any oracle access (true
   probabilities, hidden types, future events, perfect enforcement or
   identity). Treat "future improvement" comments about leaks as open flaws.
5. Kill test — What would make this result lose? Name the 2–3 most
   plausible breakers (adversarial adaptation, human behavior, regime
   extremes) and say whether each has been run. If not, propose the
   cheapest run that would decide it.
6. Proxy vs regime — Is the number from a proxy (single seed, single
   contest or event, toy scale) that realistic multi-seed, market-scale
   runs haven't confirmed?

End with: the claim as currently defensible (rewritten with its caveats),
the single most dangerous unmet item, and the cheapest experiment to close it.
Do not soften verdicts. A result that flatters us is the priority to break.

Why this exists: ClaudeStop (Oct 2026) lost its headline claims to exactly
these six gaps — a self-graded safety metric, an unaudited benchmark, a
never-modeled real competitor, an oracle leak documented in code comments,
proxy numbers quoted before the realistic runs, and an unquantified human
factor. Each was cheap to check on day one and expensive to find late.

## GRE-specific starting points (check these first)

1. Real alternative — the decision-maker is the UK government. The
   comparator must be the actual proposed 2026 reform (see
   `POLICY_BRIEF.md`, `chart9_uk2026.py`, `sweep_config.py`), not a generic "no cap" baseline.
2. Independent observer — are fan-access / welfare outcomes computed
   separately from the mechanism's own scoring and tied to the empirical
   anchors (fraud rates, displacement, scalper concentration, fees)?
3. Symmetric scrutiny — are scalper agents, enforcement and dark-market
   assumptions (`enforcement_sweep.py`) equally realistic for our ruleset and
   for the status quo / UK reform?
4. Information leak — look for perfect identity verification, perfect
   enforcement, or agents knowing each other's true valuations or future
   demand.
5. Kill test — scalper adaptation: bots, identity fraud, offshore/dark resale,
   and displacement (the government's own unevidenced "20% displacement" is
   exactly what the model claims to answer — test it adversarially).
6. Proxy vs regime — single-event results vs market-wide; is 30 runs/point in
   `cap_sweep.py` enough for the confidence quoted; are optimal-cap claims
   stable across demand levels (the demand-dependence finding)?
