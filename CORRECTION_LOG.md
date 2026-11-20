# Correction log

*How the policy brief's claims changed between the August 2026 version and the final November 2026 version, and why. The details are in the documents named in each entry.*

| Date (2026) | What was found | Consequence | Document |
| --- | --- | --- | --- |
| 2 Nov | Audit of the brief against the model. Problems found: the role-proofness claim had never been tested; the "71–89% margin cut" was a utility index, not a margin; the robustness figure came from an older model version; two results rested on unsaved runs; Ontario's in-force date was wrong. | Claims register created; a role-proof test added | `CLAIMS_REGISTER.md` |
| 5 Nov | Pre-registered role-proof test: "a 10–20% cap is role-proof" **failed** (0 of 9 demand levels). Diagnosis: a **scoring error**. Fan-group utility applied the price paid by fans who got tickets to every fan in the group, including those who got none. | All fan welfare was rescored fan by fan | `ROLE_PROOF_TEST.md` |
| 9 Nov | Pre-registered re-check of the brief's welfare claims under corrected scoring. | **Withdrawn:** "the optimal ceiling is 10–30%" and "the ceiling's gain is 2.13× the fee cap's". | `RESCORE_CHECK.md` |
| 9 Nov | Pre-registered price-score check (P0/P1/P2). | Every 10–20% claim failed. Today's market's strength at about 3× demand was diagnosed as a reseller-markdown artefact. | `PRICE_SCORE_CHECK.md` |
| 9–11 Nov | Exploratory and pre-registered checks of the redrafted brief: resale valued by realized proceeds; frictionless fan listing. | **Withdrawn:** "the ceiling is the stronger lever on its own" | `BRIEF_REVISION_2026-11-09.md`, `LISTING_CHECK.md` |
| 12 Nov | **First independent adversarial review** (run with a separate AI model). It found four mechanical errors: off-platform tickets priced above every buyer's limit, so they never sold at high demand; dark routing comparing net with gross; buyer fees ignored when matching buyers; a face-value floor on fans' resale. It also found legal and citation errors and method problems. | All accepted; triage in the claims register | `audit results/roleproof_audit_report_2026-11-12.md`, `CLAIMS_REGISTER.md` |
| 15 Nov | **Model v2** fixes the four errors (the old version still reproduces exactly). One pre-registered experiment was run. | Decision D1: a fixed 20–30% band. The brief was rewritten to the result. | `V2_PREREGISTRATION.md`, `v2_verdicts.txt` |

## Claims withdrawn from the brief

- **"Touting becomes loss-making at extreme demand" / "breaks the economics of industrial touting".** These rested on off-platform tickets that could never sell. Under v2, resellers keep about 16–25% at a 20–30% ceiling.
- **"The ceiling's gain is 2.13× the fee cap's"** and **"the ceiling is the stronger lever".** The first came from a mislabelled comparison plus the scoring error. The second depends on uncalibrated listing behaviour.
- **"The optimal ceiling is 10–30%, rising with demand"** and **"a 10–20% cap is role-proof".** The band is not role-proof against face value under the final definition.
- **"Beats the current market in 96–99% / 99–100% of 400 perturbations".** This came from an older model, and it picked the best of three ceilings in each scenario rather than testing a fixed one.
- **"10% beats face value under DC's actual fee structure".** The modelled fees were not DC's structure.
- **"A 2% fee cap narrows and reverses the advantage".** It was an unpaired grid read.
- **"Leakage responds to the price gap, not the fee rules".**
- **"A positive ceiling is the minimum condition for lawful resale to exist".**
- **"Face-value caps have failed in three jurisdictions"** and **"every analysis, including the Government's, models a single representative consumer".** Both were unsupported.

## Facts corrected

- **Ontario.** The cap is set on the original total price paid, not face value. It took effect in April 2026, not 31 July. The bill number is to be confirmed: "Bill 94" in our earlier ledger was wrong.
- **DC Law 26-181.** The cap is set on the total initial price including fees and taxes, plus up to 10%. There is a single marketplace fee of up to 10% of that total. It took effect on 25 September 2026 and applies from 1 January 2027.
- **Leslie & Sorensen (2014).** The one-third offset is rent-seeking **plus** resale transaction costs.

## Final independent review, 17 Nov 2026 (run with a separate AI model)

- **Source:** `audit results/roleproof_v2_audit_report_2026-11-17.md`, plus a reproduction zip.
- **Verdict:** "publish with listed wording and evidence fixes, not as written". There were no new code errors comparable to the first review's. Results reproduced exactly: 138 runs regenerated, 10,626 fields compared; verdicts byte-identical.
- **Wording changes in the brief:**
  - "The draft Bill" → **the Government's announced proposals.** No draft text has been published; this was verified against Parliament's written answer of 18 Sept and the 4 Nov debate.
  - **Reseller returns** are now "model-implied returns before omitted costs" in "the model's uncapped market", not claims about today's real market.
  - **The upper end of the band** is described as a normative choice that depends on assumptions. A stress-test table was added: at a 30% ceiling, returns reach 31% with cheaper off-platform trading. At a 10% fee cap, even 40% stays within the limit.
  - **Role-proof wording:** "no group of fans worse off" → "no detected group-average loss". The brief states that the recommendation gives up the role-proof condition for larger average gains.
  - **The failure condition** is described precisely: positive at moderate demand, near zero at high demand on one scoring, reversed on another. "Disappears" was dropped. The claim that "the ranking doesn't change with demand" is limited to the primary scenarios.
  - **Ireland:** the causal enforcement claim is removed.
  - **Ontario:** Bill 97, Schedule 16 (confirmed from the statute text). The cap is the total primary price **plus permitted secondary fees and taxes**. The statute's price-of-record requirements are noted.
  - **Pre-registration** is described as a dated internal protocol, not externally registered.
  - **New limitation:** fans who resell are still credited with obtaining a ticket.
