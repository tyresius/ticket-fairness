# Price-score check: does counting price harm above 2× face change the verdicts?

*Written 9 Nov 2026, before any number under the new price scores was computed. Patrick approved the check in principle on 9 Nov ("Yes, pre-register it") and signed off both ★ choices as recommended the same day, before the full run: a claim must hold under both P1 and P2, and C7 is included. Results go at the bottom. The method and criteria above them are not edited after the run; any change is made by dated amendment.*

**Why.** The model scores a fan's price as `max(0, 1 − (paid − face) / face)` (`gre_sim.py:744`; `role_proof.py:110`): 1 at face value, 0 at 2× face, and still 0 above that.

- So a mega fan paying 2.65× face scores the same on price as one paying 2×.
- The 9 Nov follow-up (`RESCORE_CHECK.md`) flagged this as the modeling choice now carrying much of the result.

This check comes after two failures: the role-proof test (5 Nov) and the 10–30% band in the welfare re-check (9 Nov). The risk is picking whichever scoring rescues the claim. To guard against that:

- both alternatives are fixed now;
- a claim survives only if it holds under both;
- the expected direction of each is written down before the run.

## Three price scores

Only the price term changes.

| Code | Name | Price score for a fan who paid *p*, where *r* = (*p* − face) ÷ face |
| --- | --- | --- |
| **P0** | Current | max(0, 1 − *r*): 1 at face, 0 at 2× face and above |
| **P1** | Keep counting | 1 − *r* with no floor: the same slope continues above 2× face, so 3× face scores −1 |
| **P2** | Share of value kept | (WTP − *p*) ÷ (WTP − face): 1 at face, 0 at the fan's own maximum price |

WTP is the fan type's maximum price in the model (`gre_sim.py:201–207`): mega fans 4.0× face, committed casuals 1.8×, average buyers 1.6×.

Everything else is unchanged from individual scoring (`role_proof.agent_utility`, κ = 0, no proceeds):

- the weights, access, attendance and the resale term;
- the fraud penalties;
- 0.02 for a fan with no ticket;
- the floor of 0 on a fan's total.

Dynamic pricing's resented surcharge (`gre_sim.py:745–748`) is subtracted from the price score under all three; see the disclosure below.

**What the two alternatives assume.**

- **P1** treats money the same for every fan: each extra 1× face costs 0.30 of utility. A fan is indifferent between buying and missing out at about 4.1× face, whatever their type.
- **P2** measures price against each fan's own valuation. An extra 1× face costs a mega fan 0.10 and a committed casual 0.375.

**Predictions, written before the run.**

- **P1 should move results toward caps.** It newly penalises the high prices mega fans pay under the status quo: 2.65× face on average at 5× demand.
- **P2 should move results toward the status quo.** A mega fan paying 2.65× face keeps 45% of their value, so their price score rises from 0 to about 0.45. Casual fans' scores fall slightly, since they reach 0 at 1.8× instead of 2×.
- **They may therefore disagree**, which is why a claim must hold under both.

## Claims and criteria, fixed now

| # | Claim | True if |
| --- | --- | --- |
| R1 | A 10–20% cap is role-proof | The pre-stated PASS criterion in `ROLE_PROOF_TEST.md`, unchanged: a 10–20% cap is within 0.01 of the minimum role-proofness gap, ex ante and ex post, at 6 or more of the 9 oversubscribed levels (κ = 0, no proceeds) |
| C1 | The optimal ceiling lies in 10–30% | As in `RESCORE_CHECK.md`: the PopWt-best bounded cap (0–50%) is in 10–30% at all 9 levels |
| C6 | Bounded caps beat the status quo, dynamic pricing and face value | As in `RESCORE_CHECK.md`: the best bounded cap beats each on PopWt and System at all 9 levels |
| C7 ★ | Fans are better off on average under a 10–20% cap than under the status quo (new) | The best of 10/15/20% has a higher mean individual fan utility (every fan weighted equally) than the status quo at all 9 levels |

**Verdict per claim** ★:

- **Survives:** true under P1 and P2.
- **Survives under one:** true under one of them.
- **Fails:** true under neither.

P0 is reported for reference only. It must reproduce the stored results (see the harness checks).

C7 is new. The brief implies it, and the 9 Nov follow-up raised it by finding that the cap's welfare win comes from the equality term. Its P0 value was glimpsed in that exploratory run (about level at 5×). It is not judged under P0.

**Sensitivity, reported with no verdict:** R1 at κ = 0.5 and 1, under P1 and P2.

The proceeds variants are not re-run. They change only resellers' resale term, not the price term.

## Design choices for Patrick ★

1. **Verdict rule.**
   - **Recommended: a claim must hold under both P1 and P2.** It matches the 9 Nov rule (S1 and S2), and it stops the result from resting on the one scoring that helps.
   - **Alternative: P1 alone decides, with P2 reported.** P1 is the direct fix for the flagged saturation, whereas P2 changes what the price term measures.
2. **Include C7.** Recommended: it asks directly whether fans are better off, which the composite can't answer.

## Runs

- **Role-proof:** the same 121,000 simulations and seeds as on 5 Nov. Scorings: P0 at κ = 0 (as the harness check), and P1 and P2 at κ = 0, 0.5 and 1.
- **Main grid:** the cap sweep as stored, 16 series × 10 levels × 100 runs, seed 42. Scorings: P0, P1 and P2.
- **Not re-run:** C2–C5 (the fee-cap package, the robustness draws, the paired runs). They are out of scope.

## Harness checks

All of these must pass, or nothing below is read.

1. P0 role-proof gaps (κ = 0, no proceeds) reproduce `role-proof-summary.csv` exactly.
2. P0 grid values reproduce the 9 Nov S2 rows of `rescore-grid.csv` exactly, for every series except Dynamic Pricing. Dynamic Pricing's values change by design (see the disclosure).
3. Unit tests (`test_role_proof.py`):
   - P0 equals the old scoring on every agent;
   - P1 equals P0 at or below 2× face;
   - P2 is 1 at face and 0 at the fan's limit;
   - every per-agent score stays in [0, 1].

## Disclosure: the 9 Nov S2 scoring omitted dynamic pricing's surcharge penalty

`rescore_check.py`'s S2 scored Dynamic Pricing fans without the model's resented-surcharge term (`gre_sim.py:745–748`). This flatters dynamic pricing.

- **9 Nov verdicts are unaffected.** Dynamic pricing lost to the best bounded cap at every level under S2 even so.
- **This check applies the term** under P0, P1 and P2.

Code: `price_check.py`, plus a `price_form` option in `role_proof.agent_utility` (default unchanged). Output: `price-check-*.csv` and `price_check_run.log`.

## Amendments

**Amendment 1, 9 Nov 2026, about 21:10 EST.** Approved by Patrick the same day.

- **Timing.** Made during the full run, which started at about 21:00. The grid output (`price-check-grid.csv`) had been written at 21:07; neither it nor the log had been opened. The role-proof phase was still running.
- **Why.** Patrick clarified that the 10–20% band was never a target. It was a rough average of the cap optima, chosen because one fixed, understandable, auditable number is better than a demand-indexed cap, which would copy the scalper market's mechanics of prices rising steeply with demand.
- **What changes.** R1 and C1 test the brief's wording and stay as registered. Two claims are added to test Patrick's actual position:

| # | Claim | True if |
| --- | --- | --- |
| R2 | A single fixed cap is role-proof | One bounded cap in the menu (any level, 0–50%) is role-proof under R1's definition (within 0.01 of the minimum gap, ex ante and ex post) at 6 or more of the 9 oversubscribed levels; κ = 0, no proceeds |
| C8 | One fixed cap is close to the best everywhere and beats the market alternatives | One bounded cap *c* (0–50%) is within 0.01 of the PopWt-best bounded cap at all 9 oversubscribed levels, **and** beats the status quo and dynamic pricing on PopWt and System at all 9 |

The tolerance of 0.01 is the model's stated margin of error, the same one R1 uses (`role_proof.TOLERANCE`).

- **Verdict rule:** unchanged, so a claim must hold under both P1 and P2.
- **P0:** reported for reference only. Its inputs were already seen in the 5 Nov and 9 Nov results.
- **Also reported for C8,** under each scoring: the fixed cap with the smallest worst-level shortfall, and that shortfall.

These claims are computed from the outputs the run already writes; no re-run is needed. Code: `price_check.py --verdicts` (added after this amendment). It re-reads the CSVs and prints every verdict, R1, C1, C6, C7, R2 and C8.

## Results

*Run 9 Nov 2026 (47 min). Output: `price_check_run.log`, `price-check-grid.csv`, `price-check-roleproof-summary.csv`, `price-check-roleproof-roles.csv`. The amendment-1 verdicts are from `python3 price_check.py --verdicts`.*

**Harness checks: both pass.** P0 reproduces all 450 checked grid values from 9 Nov and all 220 role-proof values from 5 Nov exactly.

### Verdicts

| # | Claim | P0 (reference) | P1 (keep counting) | P2 (share of value kept) | Verdict |
| --- | --- | --- | --- | --- | --- |
| R1 | A 10–20% cap is role-proof | 0 of 9 levels | 0 of 9 | 0 of 9 | **Fails** |
| C1 | Optimal ceiling in 10–30% | 50% at 1.5–5× | Same as P0 | 40%, 30%, then 50% at 1.5–5× | **Fails** |
| C6 | Best cap beats status quo, dynamic pricing and face value everywhere | Loses to SQ at 3× | Loses to SQ at 3×, and to DP at 3×, 4× and 6× (PopWt) | Loses to SQ at 3× (System) | **Fails** |
| C7 | Fans better off on average under 10–20% | Worse at 7 of 9 levels | Better at 8 of 9; worse at 1.5× (−0.052) | Worse at 7 of 9 | **Fails** |
| R2 | One fixed cap is role-proof (amendment 1) | 40% at 1 of 9 | **40% at 6 of 9** (2, 4, 5, 7, 8, 10×) | 40% at 1 of 9 (2×) | **Survives under one (P1)** |
| C8 | One fixed cap within 0.01 of the best everywhere, and beats SQ and DP (amendment 1) | None. Closest is 40%, 0.017 short at 3× | None. 40% is 0.017 short; loses to SQ at 3× and DP at 3×, 4×, 6× | None. 40% is 0.012 short at 3×; loses to SQ at 3× | **Fails** |

**κ sensitivity** (κ = 0.5 and 1):

- R1: 0 of 9 everywhere.
- R2: the same as at κ = 0, i.e. 6 of 9 under P1 and 1 of 9 under P2.

The endowment shift changes nothing.

### What the results say

1. **The role-proof verdict turns on one value judgement: how a high-value fan's high payment counts.**
   - **Under P1**, every extra 1× face costs every fan the same. A fixed 40% cap is then role-proof at 6 of 9 levels. Mega fans who lose access under the cap no longer regret it much, because the status quo makes them pay about 2.65× face.
   - **Under P2 and P0**, the status quo is role-proof from 4× up. Under P2 a mega fan paying 2.65× for a ticket worth 4× to them is still well off; under P0 price harm stops at 2×.
   - Both readings are defensible. The model can't choose between them; it is a normative choice.
2. **The fixed cap that holds up is about 40%, not 10–20%.**
   - Under every scoring, 40% is the single cap that is most often role-proof and closest to the best everywhere.
   - A 10–20% cap is never role-proof, and it falls 0.03–0.05 short of the best somewhere under every scoring.
3. **A fixed 40% cap is close to the best everywhere, but not within 0.01.** Its worst shortfall is 0.012–0.017, at 3× in each case.
4. **Fans on average with a fixed 40% cap** (exploratory: 40% was not a pre-registered C7 arm). Mean fan utility, 40% cap minus status quo:
   - **P0:** ahead at all 9 levels, but by less than 0.005 at 5–10×.
   - **P1:** ahead at all 9 levels, by +0.006 to +0.076.
   - **P2:** ahead at 1.5×, 2× and 4×; behind at 3× and 5–10×, by at most 0.011.
5. **The welfare composite is unreliable on its own.**
   - Under P1, dynamic pricing's mean fan utility is the lowest of any rule. At 4× it is 0.077, against 0.115 for the status quo and 0.190 for a 40% cap.
   - Yet its composite rises past the best cap at 3×, 4× and 6×. P1 pulls every fan type down together under dynamic pricing, which narrows the gaps the equality term rewards.
   - The composite can therefore rank a rule higher for making fans equally worse off. C1, C6 and C8 rest on the composite; any claim built on it needs the mean-fan figure alongside.
6. **3× decides several verdicts and is still undiagnosed.**
   - At 3×, the status quo beats every cap on at least one lens under every scoring. That one level decides C6 and C8 and is where 40% falls short.
   - The scalper markdown tiers change at 2× and 5× (`gre_sim.py:602–604`). 4× sits in the same tier as 3×, so the tiers alone don't explain it. *(Diagnosed later the same day; see the follow-up below.)*

**For the essay.**

- **What survives** is conditional: a single fixed cap, at about 40%, is role-proof at most demand levels if money counts the same for every fan, and is not if price is judged against each fan's own valuation.
- **What fails** is every 10–20% claim and every claim that rests on the composite alone.

## Follow-up: why the status quo is strong at 3× (exploratory, 9 Nov 2026)

*Not pre-registered; it diagnoses and decides nothing. Source: `explore_3x.py`, `explore_3x.log`. 60 paired seeds per cell, demand 1.75–6× in steps of 0.25–0.5.*

**Cause: the scalper markdown rule.** Two demand-dependent mechanisms meet around 3×:

- **Scalper asks grow with demand.** The mean ask is face × (1 + 0.65 × demand), about 2.95× face at 3× (`gre_sim.py:475`).
- **The markdown on unsold scalper tickets jumps at fixed thresholds** (`gre_sim.py:602–604`). The last round sells at 75% of the ask up to 2× demand, 45% from just above 2× up to 5×, and 30% above 5×.
- **Just above 2× to about 3×, the two combine** to put the final price at roughly 1.3–1.6× face. That is within reach of committed casuals (limit 1.8×) and average buyers (limit 1.6×). About 16% of them get in, against about 3% elsewhere.
- **From about 3.25×, the higher asks push those prices back out of reach.**

**It is a step artefact.** The status quo's PopWt jumps from 0.196 at 2.0× to 0.245 at 2.25×, exactly at the threshold. It stays near 0.25 through 3.0×, then falls to 0.151 at 3.5× and 0.129 at 4×.

The status quo with one markdown schedule at every demand level:

| Schedule (status quo) | Effect on the 2.25–3× window | Status quo vs 40% cap, PopWt at 3× |
| --- | --- | --- |
| As in the model | Window present | +0.022 (status quo ahead) |
| Gentle (75% final) everywhere | Window gone | −0.048 |
| Aggressive (45% final) everywhere | Window extends down: the status quo beats 40% at 1.75–3× | +0.022 |
| **33% decay everywhere** (the project's one documented anchor, PTR/Automatiq) | Window gone; the status quo loses to 40% at every level tested (1.75–5×), on PopWt and on mean fan utility | −0.048 |

**Caps are untouched.** A 40% cap gives identical results under all three schedules.

**Caveat: neither fixed schedule behaves like a profit-seeking reseller.** Under the gentle and 33% schedules, 90–130 seats go unsold at 2.5–3.5× while fans who would pay 1.6–1.8× face go without. The aggressive tier is closer to "sell to whoever is left".

- **A principled fix:** a markdown that clears to the remaining buyers' limits. It isn't built. It is a model change, so it would need pre-registering, and it could strengthen the status quo at moderate demand.

**What it means for the verdicts.** No pre-registered verdict changes formally, since this is exploratory.

- **What the diagnosis does change:** the status quo's wins at 3× under P0 and P2 (C6) and its 3× role-proof results come from an uncalibrated threshold, not from the status quo's economics.
- **C8 would still fail.** 40%'s 0.012–0.017 shortfall at 3× is against the 50% cap, and caps don't depend on the markdown. Dynamic pricing's composite win under P1 is also unrelated.
