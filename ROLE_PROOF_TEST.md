# Role-proof test: design for sign-off

*Drafted 3 Nov 2026. **Nothing has been run.** The criteria below are fixed before any result exists. Any change after the run goes in a dated amendment at the bottom; the text above it is never edited.*

**What it tests.** A rule is role-proof if the groups it creates still accept it after tickets are allocated, not just from behind the veil. The model already scores the veil half (`ex_ante` lenses). This adds the after-allocation half, which is the part the essay's name now claims.

## How it works

1. **Roles.** After the primary sale, each fan is either a holder or a have-not. With three fan types that makes six roles. Scalpers stay outside the fan contract, as in the existing Fan lens; their numbers are reported separately.
2. **The after-allocation counterfactual.** Run the primary sale under rule R. Then, with tickets where they landed, run the rest of the market (plan changes, resale, the dark market) under each rule in the menu.
   - The seed is the same, so the allocation is identical; only the rule for the rest of the market changes.
   - Scalpers keep the numbers and effort they chose under R: they entered expecting R.
   - This is the moment the brief describes: once tickets are allocated, which rule does each group want governing the rest of the market?
3. **Scoring.** Each fan is scored individually with the model's own formula: access, price paid, attendance, the resale option, and fraud penalties.
   - The current veil lens multiplies a type's group score, which already contains the access rate, by the hit rate again (`gre_sim.py:771` and `803`). Per-agent scoring avoids that double count.
   - The baseline lenses themselves are left unchanged.
4. **What "accept" means.** For each role, *regret* = its utility under its favourite rule in the menu, minus its utility under R. A rule's *role-proofness gap* is the largest regret any role has. A gap of 0 means R is every role's favourite; the most role-proof rule has the smallest gap. It is computed twice:
   - **Ex ante:** the roles are the three fan types, with the whole market under one rule.
   - **Ex post:** the six roles, after allocation.
5. **Preference shift.** Holders weight the resale option by (1+κ).
   - κ = 0 is pure positional interest, which is what Fernandez–Rodrik's account would predict.
   - κ = 0.5 and 1.0 add the role-shifted valuation that the concept claims.
6. **Menu.** Status quo, UK face value, and bounded caps at 0, 5, 10, 15, 20, 25, 30, 40 and 50%. The fee-cap regimes are left out of v1.
7. **Size.** 11 × 11 rule pairs × 10 demand levels × 100 seeds ≈ 121,000 simulations, about 20–30 minutes.

## Why not a simpler definition

- **Unanimity against the status quo** ("every role prefers R"): in this model, holders' only cap-sensitive stake is the resale option, which rises steadily as the cap loosens (`gre_sim.py:748–769`). So holders reject every cap by construction, and one formula would decide the test, not the market.
- **Majority vote** (Fernandez–Rodrik's test) measures whether the reform coalition survives politically, not whether every role can accept the rule. It is reported alongside, as a secondary output.

## Criteria, fixed before the run

- **Pass:** with κ = 0, at 6 or more of the 9 oversubscribed demand levels (1.5× to 10×), a 10%, 15% or 20% cap is role-proof: its gap is within 0.01 of the menu's smallest, both ex ante and ex post.
- **Kill, for the essay's claim:** at 4 or more of those levels, no 10–20% cap is role-proof. The essay then reports where the role-proof band actually is. If there is none, it falls back to the concept plus the ownership-versus-information experiment.
- **Reported either way:**
  - the role-proof band at κ = 0, 0.5 and 1.0;
  - whether the ex-ante and ex-post winners differ, which is the coalition split itself;
  - the majority view.
- **The 0.01 threshold** is the sweep's stated margin of error at 100 runs (`sweep_config.py`, `RUNS_PER_POINT`).

## Checks that must pass before any result is read

Otherwise any difference is a bug, not a finding.

1. **Baseline unchanged:** the full cap sweep, re-run with the new code, matches the stored CSVs exactly.
2. **Same-rule switch:** switching to the same rule reproduces the no-switch run exactly.
3. **Fixed allocation:** for a given seed and primary rule, the primary allocation is identical under every continuation rule.
4. **Bounded scores:** every per-agent score lies in [0, 1].

## Limits the essay should state

- **Resale proceeds are missing.** Holders' realized resale proceeds aren't in the fan utility index, only the option value. That understates the stake in a loose cap for holders who actually resell. A variant that adds proceeds can be run.
- **The counterfactual is myopic.** Roles judge the rest of this market, not future events where their role may change.
- **Fairness is a weight.** "What a role thinks is fair" is represented as a utility weight (κ), not modelled separately.

## Decisions, approved by Patrick on 5 Nov 2026, before any run

1. **"Accept" = minimax regret across roles.**
2. **The ex-post counterfactual = switch the rule after the primary sale.**
3. **κ = 0, 0.5 and 1.0.**
4. **Realized resale proceeds are added as a sensitivity**, scored alongside the main run. Nothing else changes.
   - For a fan who sold at least one ticket, the resale term uses the *realized* net upside instead of the option value: (average net proceeds per ticket sold − price paid) ÷ face value.
   - That figure goes through the same mapping as the option value (`gre_sim.py:769–790`), so the score stays in [0, 1].
   - Fans who sold nothing keep the option value.
5. **The criteria as stated above.** The pass/kill verdict applies to the main run only: κ = 0, no proceeds. The variants are reported alongside it.

## Results (run 5 Nov 2026; 121,000 simulations, 28 minutes)

**Pre-registered verdict: KILL.** On the main run (κ = 0, no proceeds), a 10–20% cap is role-proof at **0 of 9** oversubscribed demand levels. Output is in `role-proof-summary.csv`, `role-proof-roles.csv` and `role_proof_run.log`.

| Demand | Role-proof rule | Best ex ante | Best ex post |
| --- | --- | --- | --- |
| 1.5× | none | Status quo | Bounded 30% (winners differ) |
| 2× | Bounded 40% | Bounded 40% | Bounded 40% |
| 3× | none | Bounded 40% | Status quo (winners differ) |
| 4× to 10× | Status quo | Status quo | Status quo |

All five variants (κ = 0.5 and 1; proceeds on, at κ = 0, 0.5 and 1) give the same picture. The ex-ante and ex-post winners differ at 1.5× and 3×, which is the coalition split itself, at moderate demand.

### Why: diagnostics, all exploratory, none part of the verdict

1. **Two scorings disagree.** Per-agent and per-type scoring disagree on the *same* runs. The model's type formula (`gre_sim.py:771–795`) scales access and attendance by each type's hit rate, but applies the price score to the whole type. At 5× demand only 7% of committed casuals get a ticket under a 20% cap, yet the type scores 0.24, almost all from the price that 7% paid. Scored individually, the same type averages 0.07.
2. **Under individual scoring, the status quo serves mega fans much better.** At 5× demand (40 seeds):
   - Mega fans get tickets 93% of the time under the status quo, against 55% under a 20% cap and 61% under face value.
   - Casual and average fans get tickets 2% of the time under the status quo, 7% under the cap and 4% under face value.
3. **The stored baseline agrees, with no new scoring.** At 5× and 8× demand the status quo fills 476–477 of 500 seats with no waste; every cap fills 428–454. At 2× it is the reverse: 369 under the status quo against 431–451 under caps. Caps lose seats to the dark market and to unsold tickets.
4. **The aggregation rule decides the winner.** Re-aggregating individual scores (ex ante, 40 seeds):

   | Aggregation | Winner at 4× and above |
   | --- | --- |
   | Minimax regret (the approved rule) | Status quo |
   | Floor for the weakest fan type | 30–50% caps |
   | Population-weighted total | 40–50% caps |

   In none of them does a 10–20% cap come first.
5. **Minimax regret protects the group with the most to lose.** That is the mega fans, whose access falls most under a cap, not the weakest group. This property was not flagged when the definition was recommended.

**What this means.**

- **What fails is the brief's band, not the concept.** In this model, which rule is role-proof, and whether a cap beats the status quo at all, depends on how individual fans are scored and whose loss counts.
- **The brief's 10–20% band and its cap-beats-status-quo result rest on the type-level formula.** Applying a type's price score to fans who got nothing looks unintended, since access and attendance in the same formula are scaled by the hit rate.

**Correction, 9 Nov 2026.** The cap-beats-status-quo half of the bullet above was too strong. In the 9 Nov re-check (`RESCORE_CHECK.md`), caps still beat the status quo on the welfare composite under individual scoring. The win comes almost entirely from the equality term, not from higher total fan welfare.

## Amendments

*(none)*
