# Listing check: does the brief's band rest on how readily fans list for resale?

*Written 11 Nov 2026, before any number under the new listing rule was computed. Patrick approved the check on 11 Nov ("Test listing first"). Results go at the bottom. The method and criteria above them are not edited after the run; any change is made by dated amendment.*

**Why.** `/validate-claim` (9 Nov, `BRIEF_REVISION_2026-11-09.md`) named this as the most dangerous open item for the revised brief. In the model, a fan whose plans change does not always list their tickets. Two frictions decide it (`gre_sim.py:452`, `505–535`):

1. **An effort threshold.** A fan lists only if the ceiling, gross of fees, is at least their threshold. Mega fans' threshold is 0%, committed casuals' 30%, average buyers' 25%. Below it they list with probability 0.15.
2. **A listing probability under any cap:** 0.5 + 5 × ceiling, so 0.5 at face value and 1.0 from 10% up.

Neither is calibrated. Both favour higher ceilings. For fans whose plans change, they imply these listing rates:

| | Face value | 10–20% | 30% | No cap |
| --- | --- | --- | --- | --- |
| Mega fans | 50% | 100% | 100% | 100% |
| Committed casuals, average buyers | 15% | 15% | 100% | 100% |

**The test.** A variant in which every fan whose plans change lists all their tickets, in every arm (`simulate(..., fan_listing="always")`).

- **Why this extreme.** It is the best case for low ceilings: listing is frictionless, and fans resell at face value as readily as at 30%. If the brief's claims survive it, the listing assumption is not carrying them.
- **Random-number stream.** The variant draws the same random numbers as the model, so runs differ only in the listing decision.
- **The default is unchanged.**

## Arms and scoring

- **Arms:** the same as `proceeds_check.py`: face value, 20% and 30% ceilings, each with the 5%/side fee cap; and a 20% ceiling at today's 15%/side fees.
- **Seeds:** 300 paired seeds per oversubscribed level, the same seeds as `proceeds_check.py`.
- **Outcome:** mean individual fan utility under P0, P1 and P2.
- **Resale scoring:** both ways from `proceeds_check.py`: the formula ("default") and the realized channel value ("B").
- **Judged scoring:** B, the realistic one the brief's robustness statements now rest on. The default is reported alongside.

## Claims and criteria, fixed now

Each is checked under `fan_listing="always"`. A claim **holds** if the 95% interval of the paired difference is above 0 at every listed level, under all three price scores, with B scoring.

| # | Brief claim | Levels |
| --- | --- | --- |
| L1 | A 20% ceiling with the fee cap leaves fans better off on average than face value with the fee cap | All 9 (1.5–10×) |
| L2 | The same for a 30% ceiling | All 9 |
| L3 | Within the band, 30% does more for fans on average than 20% | All 9 |
| L4 | Taken one at a time, the ceiling is the stronger lever: 20% at today's fees beats face value with the fee cap | 1.5–6× (as the brief now claims) |

**Reported, no criterion:**

- the share of plan-changed fans who list, by arm, under each listing rule;
- resellers' return (ROI) for 20% and 30% with the fee cap, since frictionless fan listing adds lawful supply that competes with scalpers.

**Prediction, written before the run.** L3 is the most at risk. The step from 20% to 30% is where casual and average fans switch from 15% to 100% listing. With that step removed, 30%'s edge over 20% may shrink or vanish at some levels.

## Harness checks

All must pass, or nothing below is read.

1. With the default listing rule, the new option leaves `simulate` unchanged. The unit tests pass, and `price_check.py --smoke` still reproduces its stored first cell.
2. The default-listing rows of this run reproduce `proceeds_check.log` exactly (same seeds).

Code: `listing_check.py`, plus a `fan_listing` option in `gre_sim.simulate` (default `"model"`, unchanged). Output: `listing_check.log`.

## Results

*Run 11 Nov 2026 (`listing_check.py`, `listing_check.log`).*

**Harness checks: both pass.**

1. With the default listing rule, `simulate` is identical to the pre-edit model on 192 runs (all 16 series × 4 demand levels × 3 seeds). The 14 unit tests pass, and `price_check.py --smoke` reproduces its stored cell.
2. The model-listing rows at 1.5× and 10× reproduce `proceeds_check.log` (48 of 48 values).

**How big the friction is.** Share of plan-changed fans who list, under the model's rule and then with every fan listing:

| Arm | 1.5× | 10× |
| --- | --- | --- |
| Face value + fee cap | 31% → 100% | 50% → 100% |
| 20% at today's fees | 55% → 100% | 100% → 100% |
| 20% + fee cap | 58% → 100% | 100% → 100% |
| 30% + fee cap | 100% → 100% | 100% → 100% |

At high demand, most plan-changed holders are mega fans, who list readily under any positive cap.

### Verdicts

Judged with B scoring, under P0, P1 and P2, with every fan listing:

| # | Claim | Result | Verdict |
| --- | --- | --- | --- |
| L1 | 20% + fee cap beats face value + fee cap, all 9 levels | +0.0011 to +0.0274, every CI > 0 | **Holds** |
| L2 | 30% + fee cap beats face value + fee cap, all 9 levels | +0.0020 to +0.0491, every CI > 0 | **Holds** |
| L3 | 30% beats 20% (both with fee cap), all 9 levels | +0.0009 to +0.0217, every CI > 0 | **Holds** |
| L4 | 20% at today's fees beats face value + fee cap, 1.5–6× | −0.0027 to −0.0120, every CI < 0: the fee cap alone wins at every level | **Fails** |

Default scoring agrees on L1–L3. For L4 it is mixed:

- under P0 and P1, the ceiling leads at 1.5–2×, the two are level at 3–5×, and the fee cap leads at 6×;
- under P2, the fee cap leads throughout.

The prediction was wrong. L3 held; L4 was the claim that rested on the listing assumption.

**Margins narrow but keep their sign.** The band's lead over face value with frictionless listing, compared with the model's listing rule (B scoring, P0):

| Ceiling | 1.5× | 10× |
| --- | --- | --- |
| 20% | +0.036 → +0.027 | +0.0050 → +0.0018 |
| 30% | +0.091 → +0.049 | +0.0062 → +0.0030 |

**Reseller returns are unchanged** (20% and 30% with the fee cap, every level), so the brief's touting figures stand.

**What it means.**

- **Not carried by the listing assumption:** the case for the band against face value, and 30% beating 20%.
- **Carried by it:** the claim that the ceiling is the stronger lever on its own. If fans list unwanted tickets at face value as readily as at 20–30%, the fee cap is the stronger single lever.
- **The brief now makes no claim about which lever matters more.** It names the listing assumption as the deciding factor and lists it among the limitations.
