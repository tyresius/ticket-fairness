# Model v2: pre-registration of the final experiment

*Written 15 Nov 2026, before any v2 code existed and before any v2 number was computed. Agreed with Patrick on 15 Nov.*

- **The scope is final.** No new mechanisms or scoring variants after this document.
- **The brief will say what the results support,** per the decision rules in §5, even if that is not 20–30%.
- **Changes are made only by dated amendment.**
- **Patrick's choices, 15 Nov:**
  - role-proof means "no fan role worse off" against the alternative, plus scalpers fairly governed;
  - "fairly governed" means a return of 0–30% with at least 80% of stock sold lawfully, at 4× demand and above.

**Why v2.** The external audit (12 Nov; triage in `CLAIMS_REGISTER.md`) confirmed four mechanical errors. The most serious was that dark-market tickets were priced above every buyer's limit, so at high demand they never sold.

## 1. v2 mechanics

These are selected by `simulate(..., mechanics="v2")`. The default stays `"v1"`, so every earlier result still reproduces.

| # | Fix | v1 (`gre_sim.py`) | v2 |
| --- | --- | --- | --- |
| M1 | **Dark market clears** | Random dark prices of face × (1 + 0.5·demand + U·0.3·demand), above every buyer's WTP from about 6× demand. Unmatched tickets wasted. | Each dark ticket has a **seller reservation** r = cost basis ÷ (1 − 0.45 enforcement loss), the price at which the scalper recovers their cost. Eligible buyers are, as in v1, missed buyers whose WTP is above 1.1 × the cap ceiling. They are taken in descending WTP. A ticket trades with the first remaining buyer whose limit (WTP × face; no platform fee off-platform) is ≥ r, at the **midpoint (r + limit) ÷ 2** (equal-split bargaining). Tickets with no such buyer are wasted, as in v1. |
| M1b | **Scalpers expect the dark price they can actually get** | Entry (`expected_scalper_margin`) and routing expect face × (1 + 0.65·demand) | Both use the expected v2 dark price (r + top fan WTP × face) ÷ 2, with r at the scalper's primary cost |
| M2 | **Net vs net in routing** | Net dark revenue compared with the *gross* platform ask (`:493–500`) | Compared with platform ask × (1 − seller fee), in both the routing condition and the leakage gap. This matches the entry calculation. |
| M3 | **Buyers can afford the all-in price** | Matched if list price ≤ WTP × face (`:628`) | Matched only if list price × (1 + buyer fee) ≤ WTP × face |
| M4 | **Fans may resell below face** | Fan markdown floored at face (`:618–619`) | No face floor. The markdown is still ×1.00, ×0.95, ×0.88, and the cap still binds. |

**Unchanged and disclosed:**

- the fan listing frictions (tested as scenario S2 instead);
- the on-platform scalper markdown tiers, which distort *today's market* at 2–3× demand (`PRICE_SCORE_CHECK.md` follow-up);
- oracle enforcement against a known price of record;
- the utility weights and the P0 price-score saturation;
- the type definitions and the 500-seat scale.

## 2. Experiment

- **Arms:**
  - **today's market:** no cap, 8-ticket limit, 15%/side fees;
  - **fixed ceilings of 0%, 10%, 20%, 30% and 40%,** each with a 4-ticket limit and **5%/side fee cap.** That fee level is our assumption, not the Bill's. The 0% arm is the draft Bill's face-value rule.
- **Demand:** 1.5, 2, 3, 4, 5, 6, 7, 8 and 10×.
- **Seeds:** **300 paired seeds per level** (seed = 70,000,000 + 10,000 × level index + s). Every arm uses the same seed.
- **Ex post switches:** each positive ceiling c is also run with the primary sale under c and everything after under 0%, on the same seed (`continuation_rule`).
- **v1 comparison, reported only:** the 0%, 20% and 30% arms under `mechanics="v1"`, same seeds, model listing rule.

**Scenarios.** S1 and S2 are the realistic scenarios and decide the verdicts. S3 and S4 are reported as stated bounds.

| | Fan listing | Resale term in fans' scores |
| --- | --- | --- |
| **S1** | Model's rule | Realized recovery (B) |
| **S2** | Every plan-changed fan lists (`fan_listing="always"`) | Realized recovery (B) |
| S3 (bound) | Model's rule | Zero (weights renormalized) |
| S4 (bound) | Every fan lists | Zero |

B scoring is as in `proceeds_check.py`: fans who resold are scored on what they netted, and other holders get that run's realized resale-channel value.

**Primary outcome:** mean individual fan utility (every fan weighted equally), `role_proof.agent_utility`, κ = 0, **price score P0**. **Sensitivities:** P1 and P2.

**Also reported, with no criterion:**

- access by fan type;
- lawful resale volume;
- dark-market volume and the dark-routed share of scalper stock;
- fans exposed to dark-market fraud;
- seats filled;
- reseller ROI, inverted from the scalper utility index (`gre_sim.py:734–737`; 0.95 = 100% or more).

## 3. Definitions

"Lower" means the paired 95% interval of the difference lies entirely below zero.

- **Beats face value for fans (per cap c, per scenario):** the paired difference (c − 0%) in the primary outcome has its 95% interval above zero at all 9 levels.
- **Scalpers fairly governed (per cap, per scenario):** at every level from 4× to 10×, mean reseller ROI is between 0% and 30%, **and** at most 20% of scalper resale stock is routed to the dark market. The routed share is dark-routed ÷ (dark-routed + listed on the platform).
- **Role-proof against face value (per cap c, per scenario), all three of:**
  1. **Ex ante:** no fan type has lower mean utility under c than under 0%, at any level.
  2. **Ex post:** after allocation under c, no role (fan type × holder or have-not; roles present in ≥90% of runs) has lower mean utility continuing under c than switching to 0%, at any level.
  3. **Scalpers fairly governed** under c.

  This uses role *averages*; individuals within a role may disagree. That is a disclosed limitation.
- **Against today's market (reported, no verdict):** the primary outcome and ex ante fan types for each ceiling vs today's market. There is no ex post switch, because the fee regimes differ.

## 4. Claims

| # | Question | Decided on |
| --- | --- | --- |
| Q1 | Which positive ceilings beat face value for fans? | S1 and S2, P0 |
| Q2 | Within the band, 30% vs 20% for fans, per level | S1 and S2, P0; direction reported |
| Q3 | Which ceilings govern scalpers fairly? What is today's-market reseller ROI? | S1 and S2 |
| Q4 | Which ceilings are role-proof against face value? | S1 and S2, P0 |
| Q5 | Each ceiling vs today's market | Reported |

## 5. Decision rules for the brief, fixed now

- **D1.** If **20% and 30% both** beat face value (Q1) in S1 and S2, the brief recommends a **fixed 20–30% band**. It states Q2's trade-off, Q3 and Q4 as found, and S3/S4 as conditions.
- **D2.** Otherwise, if at least one positive ceiling beats face value in S1 and S2, the brief recommends a **modest fixed positive ceiling**. It names the ceilings that pass and says the exact percentage is uncertain.
- **D3.** Otherwise, the brief **withdraws the positive-ceiling recommendation.** It reports where face value does as well or better.

In every case:

- **Touting, scalper and role-proof claims** are stated only as Q3 and Q4 find them. If no ceiling passes Q4, the brief says so plainly.
- **A D1/D2 claim that fails under P1 or P2** in S1 or S2 is stated with that condition.
- **A claim that fails in S3 or S4** is stated as the condition "if fans place no value on being able to resell…".

## 6. Checks before any result is read

1. With `mechanics="v1"` (the default), `simulate` is unchanged: the existing tests pass, and `cap_sweep.py` reproduces the stored CSVs byte for byte.
2. New unit tests for M1–M4 under v2 pass:
   - every dark sale lies between the reservation and the buyer's limit, at the midpoint;
   - no buyer pays more than their limit, all-in;
   - routing uses the net platform price;
   - fan sales below face occur.

Code: `gre_sim.py` (`mechanics`), `v2_experiment.py`, `v2_verdicts.py`, `test_v2.py`. Output: `v2-runs.csv.gz` (one row per run, for auditors), `v2_experiment.log`, `v2_verdicts.txt`.

## Results

*Run 15 Nov 2026: 62,100 runs, 9 parallel shards. Per-run data in `v2-runs-*.csv.gz`; verdicts in `v2_verdicts.txt` (from `v2_verdicts.py`, written before the run).*

**Checks: both pass.**

1. The default `mechanics="v1"` is byte-identical to the pre-v2 model on 480 runs (16 series × 5 demands × 3 seeds × 2 listing rules). `cap_sweep.py` regenerates both stored CSVs byte for byte. The existing 14 tests pass.
2. The 6 new v2 tests pass (M1–M4 and input validation).

**Decision: D1. The brief recommends a fixed 20–30% band.**

| # | Result |
| --- | --- |
| Q1 | **Every positive ceiling (10/20/30/40%) beats face value for fans at all 9 levels in S1 and S2, under P0, P1 and P2.** Also in S3. Gains rise with the ceiling: at 10× in S1, +0.0052, +0.0074, +0.0097 and +0.0106. **S4** (every fan lists *and* resale is valued at zero) is the one bound where no ceiling passes: differences are about 0 at 3–10× under P0, and slightly negative under P2. |
| Q2 | **30% beats 20% for fans at every level in S1 and S2** (+0.0023 at 10× to +0.0513 at 1.5×, S1). In S3 and S4 the gap is not significant from 5× up. |
| Q3 | **Scalpers are fairly governed at 0–30%.** At 4–10× they earn about 0–1% at face value, 8–9% at 10%, 16–17% at 20% and 25% at 30%, with 4–10% of stock routed dark. **At 40% they earn 34%, which exceeds the 30% bound.** Today's market is 85% at 4× and ≥100% from 5×. The same holds under both listing rules. |
| Q4 | **Only 10% is role-proof against face value, and only in S1.** 20%, 30% and 40% fail because mega fans are worse off at 3–4× demand: ex ante as a type (e.g. −0.004 at 3× for 20%), and ex post as have-nots. In S2, 10% fails because committed-casual and average-buyer have-nots are slightly worse off (about −0.0005). No ceiling is role-proof in S3 or S4. |
| Q5 | Against today's market, every ceiling, face value included, beats it for fans at 2–10× in S1 and S2. At 1.5× in S1, face value is slightly below. (Today's market at 2× is depressed by the disclosed markdown-tier artefact.) |

**Reported, with no criterion:**

- **Access at 5×:** today's market gives mega fans 93% and casual/average fans 2%. A 20% ceiling gives 57% and 7%.
- **Lawful resale volume rises with the ceiling:** at 5×, 86 tickets at face value, 135 at 20%, 156 at 30%.
- **Seats filled:** 450–459 under ceilings vs 476 in today's market at 5–10×.
- **Dark sales under v2:** about 3.5–4 per event at 5–10×.

**v1 → v2:**

- Dark tickets now clear: at 10×, 0 → about 3.5 sold, with far less routing.
- Reseller returns under ceilings rise: at 10× and 20%, −10% → +16%.
- Fans' advantage over face value is slightly larger: at 10× and 20%, +0.0050 → +0.0074.
- **M4 (no face floor) has no effect at ≥1×,** because fan listings at face always sell in round 1.

**What the brief will say (per §5, D1):**

- Recommend a fixed 20–30% band with the fee cap.
- Fans gain over face value at every demand level, in both realistic scenarios and under all price scores, and gains rise with the ceiling.
- The band's top is set by fair governance of scalpers: 40% lets returns exceed 30%.
- Within the band, 30% gives fans more than 20%.
- **State plainly that no ceiling in the band is role-proof against face value under our definition.** Mega fans are worse off at moderately oversubscribed events. Only 10% leaves no fan group worse off, and only under the model's listing behaviour.
- State the S4 condition: if fans list unwanted tickets at face value as readily as at a positive ceiling, *and* place no value on being able to resell, the advantage disappears.
