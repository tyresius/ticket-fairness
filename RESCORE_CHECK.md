# Re-check of the brief's welfare claims under corrected fan scoring

*Written 9 Nov 2026, before any re-check number was computed. Approved by Patrick on 9 Nov ("re-check them"). Results go at the bottom; the method and criteria above them are not edited after the run.*

**Why.** The role-proof test found that the model's type-level utility (`gre_sim.py:771–795`) applies a fan type's price score to every member of the type, including those who got no ticket. Access and attendance in the same formula are scaled by the share who got tickets. Every welfare number in `POLICY_BRIEF.md` uses this formula.

## Three scorings, computed on the same runs

| Scoring | What it is |
| --- | --- |
| **S0, baseline** | The model's own type formula, re-implemented from the agent records. It must reproduce the stored results exactly; otherwise the harness is wrong and nothing below is read. |
| **S1, minimal fix** | S0, with the price score multiplied by the type's access rate, as access and attendance already are. Nothing else changes. This isolates the one flagged inconsistency. |
| **S2, individual** | Each type's utility is the mean of its members' individual scores (`role_proof.agent_utility`, κ = 0, no proceeds). This is the scoring the role-proof test used. |

- **What doesn't change.** Scalper utility, the welfare composite (the model's floor/equality/average weighting), the lenses (Fan, PopWt, System) and every simulation are identical across the three. Only fan-type utility changes.
- **Current model.** The fraud externality retired on 5 Jul is off (weight 0) everywhere, including the robustness re-run, which originally sampled it from 0.5 to 1.5.

## Claims and survival criteria, fixed now

A claim **survives** if its wording in the brief is true under both S1 and S2. It **survives under one** if true under one of them, and **fails** if true under neither. The numbers are reported in every case.

| # | Brief claim (line) | True if |
| --- | --- | --- |
| C1 | The welfare-optimal ceiling for oversubscribed events lies between 10% and 30% (210–213) | The PopWt-best bounded cap (0–50%) lies in 10–30% at all 9 oversubscribed demand levels (1.5–10×) |
| C2 | "The ceiling is the stronger of the two levers": ceiling plus fee cap gives a median of 2.13× the fee cap's gain (122–134) | The median over the 9 levels of (Bounded 20% + fee cap − status quo) ÷ (UK 2026 fee cap − status quo) on PopWt is above 2 |
| C3 | A bounded ceiling beats the current market in 96–99% of 400 joint perturbations (239–240) | On the original 400 draws with the externality off, the best of 10/20/30% beats the status quo on PopWt and on System in at least 95% of draws |
| C4 | A 10% ceiling beats a face-value ceiling on PopWt at every oversubscribed level, in paired runs (190–193) | Paired, 300 seeds per level, same fees on both arms: 10% beats 0% at all 9 levels, with the 95% interval of the difference above 0. Run at 5%/side fees (the stored assumption) and 10%/side (the 3 Oct "DC actual" reading); it must hold at both. |
| C5 | The same holds when the face-value arm gets a 2-ticket limit and stronger enforcement (dark cost 0.65) (194–196) | As C4, against that tougher face-value arm, at 10%/side fees |
| C6 | Bounded caps beat the status quo, dynamic pricing and face value on PopWt and System across oversubscribed demand (audit brief claim 1) | The best bounded cap beats each of the three on both lenses at all 9 levels |

Not re-checked, because fan scoring doesn't touch them:

- **The margin claim.** It is scalper utility; its wording fix already stands.
- **Dark-market volumes.**

## Runs

- **Main grid.** The cap sweep exactly as stored: 16 series × 10 levels × 100 runs, seed 42. S0 must match `cap-sweep-summary.csv`. This feeds C1, C2 and C6.
- **Paired runs** for C4 and C5.
- **Robustness:** the original 400 draws. First, S0 with the original externality settings on the first 20 draws must match `global-sensitivity-samples.csv`, as a harness check. Then all three scorings run with the externality off. This feeds C3.

Code: `rescore_check.py`. Output: `rescore-*.csv` and `rescore_run.log`.

## Results

*Run 9 Nov 2026 (64 min; `rescore_run.log`, `rescore-grid.csv`, `rescore-paired.csv`, `rescore-lhs.csv`).*

**Harness checks: both pass.** S0 reproduces every value in `cap-sweep-summary.csv` and the first 20 stored robustness draws exactly.

The first attempt failed check 1 on 3 grid values, and the script stopped before printing any S1/S2 result:

- **Cause.** The averages were accumulated with `+=`, while `cap_sweep.py` uses Python's compensated `sum()`. Per-run S0 already matched.
- **Fix.** The averaging was changed to match `cap_sweep.py`, then the whole re-check was re-run.

### Verdicts

| # | Claim | S0 (model as is) | S1 (minimal fix) | S2 (individual) | Verdict |
| --- | --- | --- | --- | --- | --- |
| C1 | Optimal ceiling lies in 10–30% | False at 1.5× only (best 40%) | Best is 50% at 1.5–5×; 15–20% at 6–10× | Best is 50% at 1.5–5×; 15–25% at 6–10× | **Fails** |
| C2 | Ceiling + fee cap = median 2.13× the "fee cap alone" gain | Median 2.13 | Median 1.10 | Median 1.06 | **Fails** |
| C3 | Best of 10/20/30% beats status quo in ≥95% of 400 draws (PopWt, System) | 99.5%, 98.0% | 100%, 100% | 100%, 99.2% | **Survives** |
| C4 | 10% beats face value at all 9 levels, paired, CI > 0 | Fails at 5% fees (4×: −0.001, CI low −0.003); holds at 10% fees | Holds at both fee levels; gap +0.003 to +0.028 | Holds at both fee levels; gap +0.008 to +0.022 | **Survives** |
| C5 | Same, against face value with a 2-ticket limit and dark cost 0.65 | Holds | Holds; gap +0.014 to +0.035 | Holds; gap +0.011 to +0.035 | **Survives** |
| C6 | Best bounded cap beats status quo, dynamic pricing and face value, PopWt and System, all 9 levels | Holds | Holds | Loses to status quo at 3×: PopWt 0.250 vs 0.252, System 0.275 vs 0.289 | **Survives under one (S1)** |

C1 under S0 fails only because of the 1.5× level, where the stored grid has always put the best cap at 40%. The brief doesn't mention this. Under S1 and S2 it fails at 5 of 9 levels whatever is done about 1.5×.

In C2, both scorings' ratios at 3× are coded ±∞:

- **Why ±∞.** The "UK 2026" arm scores below the status quo there, so the denominator is negative. The ±∞ code records which arm beat the status quo.
- **Effect on the verdict.** The median of 9 is unaffected. Read with 3× excluded, the median is 1.07 (S1) and 1.08 (S2), still far from 2.

### What the results say

1. **Robust: any cap beats the current market at high demand.** At 4–10× demand, every bounded cap from 0% to 50% scores 0.22–0.33 on PopWt under S1 and S2, against 0.08–0.13 for the status quo. This holds under all three scorings.
2. **Not robust: the level of the cap.**
   - At 6–10×, every cap from 15% to 40% is within 0.01 of the best, so the curve is flat.
   - At 1.5–5×, the score keeps rising up to 50%, the top of the sweep (`CAP_LEVELS`). The optimum there may be higher than any level the model has tried.
   - "10–20%" sits inside the flat region at high demand. It is not the optimum and is not distinguishable from 30–40%.
3. **The model never isolates the fee cap.**
   - The brief's "fee cap alone" arm is the UK 2026 model, which also has a face-value (0%) ceiling (`sweep_config.py:49–51`, `cap=0.0`). So C2 compares a 20% ceiling with a 0% ceiling, both under a 5% fee cap.
   - No arm has a fee cap without a ceiling. "The ceiling is the stronger of the two levers" is therefore unsupported under any scoring, S0 included.
   - Under S1 and S2, raising the ceiling from 0% to 20% adds a median 6–10% to the face-value package's gain over the status quo.
   - *Correction, 9 Nov 2026 (later):* "never isolates the fee cap" overstates it. No arm has a fee cap without a ceiling, but at a fixed ceiling the grid has the same rule with and without the fee cap (Bounded 0% vs UK 2026; Bounded 20% vs Bounded 20% + fee cap). That allows a two-by-two comparison of the levers. It is checked with paired seeds in `lever_check.py`. The brief's specific ratio is still mislabelled.
4. **A positive ceiling beats face value, consistently but by a small margin.** 10% beats 0% at every level, paired, under both corrected scorings and both fee levels; this is cleaner than under S0. The gap is +0.003 to +0.035 on the index, against up to +0.07 under S0.
5. **For fans alone, the robustness result is much weaker.** The fan-only lens is not part of C3's criterion, but the brief quotes it alongside.
   - The cap's median advantage over the status quo falls to +0.017 (S2) and +0.019 (S1), from +0.038 under S0.
   - The cap loses to the status quo in 14–19% of draws, against 4.5% under S0.
   - The PopWt and System advantages stay large.
6. **The status quo is anomalously strong at 3× under every scoring.** Under S2, PopWt is 0.252 at 3×, against 0.196 at 2× and 0.130 at 4×. This is the same 3–4× irregularity the brief mentions. Not diagnosed.
7. **Caveat: the "cap" comparison is a package.** Every bounded arm also halves the per-buyer purchase limit, from the status quo's 8 to 4 (`sweep_config.py:24`, `34`). "A cap beats the market" therefore means cap plus 4-ticket limit.

**Not covered by this re-check:**

- The 2% fee-cap claim (brief 203–205).
- The enforcement sweep.

**Consistency with the role-proof test.** This agrees with that test's exploratory re-aggregation (pop-weighted → 40–50% caps). Taken together:

- What the brief can still say is that a cap (with a purchase limit) beats the current market by a wide margin, and that a positive ceiling beats face value by a small one.
- What it cannot say is that 10–20% is the optimal or role-proof band.

**Disclosure, added 9 Nov 2026 after the run.** S2 scored Dynamic Pricing fans without the model's resented-surcharge term (`gre_sim.py:745–748`). This flatters dynamic pricing. It lost to the best bounded cap at every level under S2 anyway, so no verdict above changes. `PRICE_SCORE_CHECK.md` applies the term.

## Exploratory follow-up (9 Nov 2026, not pre-registered)

*This section informs; it decides nothing. Source: `explore_cap_vs_limit.py`, `explore_cap_vs_limit.log`. 60 paired seeds per cell, scored S2, at 1.5, 2, 3, 5 and 8× demand.*

Three questions, raised by caveat 7 and by Patrick's 9 Nov point that a high cap mirrors the existing system.

**1. The 4-ticket limit is not what beats the status quo.**

- No cap with a 4-ticket limit scores the same as the status quo: PopWt 0.125 vs 0.122 at 5×, and 0.110 vs 0.107 at 8×. The cap does the work, so caveat 7 is resolved.
- Under a cap, the looser 8-ticket limit scores better than 4 at every level tested. For a 50% cap: 0.314 vs 0.288 at 5×, and 0.325 vs 0.249 at 3×.

**2. A high cap does not slide back to the status quo.**

- Resale prices bind a 50% cap at every oversubscribed level. Under the status quo, fans with tickets pay on average 1.9× face including fees at 1.5–2× demand (casual fans) and 2.65× at 5× (mega fans). Those averages include primary buyers at face, so resale prices are higher still (`cap-sweep-agents.csv`). A 50% ceiling is therefore below the market price at every oversubscribed level.
- Welfare falls once the cap goes above 50%. At 5×, PopWt is 0.288 at 50%, 0.179 at 100% and 0.113 at 200%, against 0.122 for the status quo. At 8× the figures are 0.299, 0.193 and 0.102 (status quo 0.107).
- The optimum is interior, roughly 20–50%, not at the edge of the sweep.
- A 200% cap behaves oddly at 1.5–2×: scalpers list at the ceiling and don't sell. Don't read those rows.

**3. At high demand, the cap's win comes almost entirely from the equality term.**

- At 5×, PopWt rises by +0.158 from the status quo to a 20% cap. Of that, the equality term contributes +0.148, the floor +0.014, and the average −0.003. At 8× the split is equality +0.202 out of +0.208.
- Under the status quo, the best-off type is the scalper, at utility 0.95, which is the index ceiling. That maximises the gap the equality term penalises.
- Average welfare barely moves. The population-weighted average is 0.165 under the status quo against 0.150–0.160 for 20–50% caps at 5×. A cap moves seats from mega fans to casual fans:

| At 5× demand | Status quo | 20% cap |
| --- | --- | --- |
| Mega fans with tickets | 92% | 56% |
| Casual and average fans with tickets | 2% | 7% |
| Seats filled | 476 | 448 |

- Scalpers' utility falls from 0.95 to 0.27.
- On the fan-only lens the cap still wins, by +0.04 to +0.08 at 5–8×. That win also runs through equality: the cap narrows the mega/casual gap, partly by lowering mega fans' utility (0.66 to 0.49).

**What this means.** Under corrected scoring, a cap beats the status quo because the composite puts 70% of its weight on the worst-off type and on equality, not because fans are better off in total. Whether moving seats from the fans who want them most to the fans who rarely get in is an improvement is a value judgement. It is the question the role-proof test exists to settle; under minimax regret it sided with the mega fans.

**A modeling choice now carries much of the result.** The price score stops counting harm at 2× face (`max(0, 1 − ratio)`), and money paid is never set against willingness to pay. So a mega fan paying 2.65× face scores the same on price as one paying 2×, and the status quo's transfer to scalpers is invisible in fan utility. Any change to this must be pre-registered before it is run, since it would come after a failed test.
