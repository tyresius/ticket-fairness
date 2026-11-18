# Role-proof essay: claims register

*Built 2 Nov 2026 from `POLICY_BRIEF.md` (current version), the stored result files and `gre_sim.py`. Every check was read-only. The reproduction script lives outside the repo and can be added to the release package. "GRE" is now **role-proof** (a role-proof rule; role-proofness).*

**Bottom line: most model numbers reproduce, but the essay cannot quote the brief as it stands.**

1. **The central claim is not computed.** The model never tests whether a cap is role-proof, meaning whether holders and have-nots each still accept it after allocation. It scores welfare, plus an expected-utility "veil" lens.
2. **Two numbers carry the wrong label.** The "margin" figure is a utility index, and the fee-cap figure is a package total, not the ceiling's own effect.
3. **Two results come from an older model.** The 96–99% robustness result was generated before the fraud externality was retired.
4. **Two results rest on runs that were never saved:** "beats face value at every demand level" and the 2% fee condition.
5. **One fact is wrong.** Ontario's cap took effect in April 2026, not on 31 July.

## 1. The central claim

| Claim | Status | Evidence | Fix |
| --- | --- | --- | --- |
| A 10–20% cap is role-proof: accepted from behind the veil, and still accepted by holders and have-nots after allocation | **Not computed by the model** | The "harder test" lens is expected utility before anyone knows their position (`gre_sim.py:794–803`, `870–876`): the veil half only. Nothing compares rules from each role after allocation. Every fan who misses out gets a fixed 0.02 whatever the rule (`gre_sim.py:714`, `720`, `801`), so the model cannot express a have-not's view of a rule. | Patrick's decision: **(a)** add a minimal role-proofness test, or **(b)** present role-proofness as the concept, the model as welfare evidence for the band, and the ownership-versus-information experiment as the test. Recommend (a): the essay's name is now the claim. |

**What (a) needs:**

- For each rule, compare each role's utility after allocation with what it gets under the status quo.
- Make have-nots' utility depend on the rule, through their secondary-market access and the price they would pay.
- Give holders a preference shift. The resale-option term (`gre_sim.py:749–774`) is already the natural place for it.

**Update, 5 Nov 2026: the role-proof test ran and the claim failed its pre-stated criteria.** A 10–20% cap is role-proof at 0 of 9 oversubscribed levels; the status quo is the most role-proof rule from 4× demand up (`ROLE_PROOF_TEST.md`, Results).

The diagnostics found a deeper issue that reaches the brief's welfare numbers too:

- The type-level utility formula (`gre_sim.py:771–795`) applies a type's price score to every member, including the large majority who got no ticket. Access and attendance in the same formula are scaled by the hit rate.
- Scored individually, the status quo gets more fans into seats at high demand, which the stored attendance figures confirm. Depending on how fans are weighed, the best rule is the status quo or a 30–50% cap, not 10–20%.

**Every welfare claim in section 2 needs re-checking under individual scoring before the essay or any brief goes out.**

## 2. Model numbers in the brief

| Claim (brief line) | Reproduces? | Problem | Fix |
| --- | --- | --- | --- |
| Optimal ceiling 10–30% depending on demand: about 10% for a moderately hot event, 20% at 5×, 30% at the extreme (210–213) | **Yes.** `cap-sweep-summary.csv`, PopWt maximum: 20% at 2×, 10% at 3–4×, 20% at 5×, 25–30% at 6–10×; 40–50% below 2× | It isn't monotone in demand (2× → 20%, 3–4× → 10%) | Say "roughly 10–30%, not rising smoothly with demand" |
| Fee cap alone +0.06 to +0.27 against the current market; "adding a 20% ceiling… improves it by +0.08 to +0.25"; median 2.13× (123–128) | **Numbers yes.** Both figures are against the status quo (PopWt, demand 1.5–10); 2.13 is the median of the two packages' ratio | +0.08 to +0.25 is the ceiling-plus-fee-cap package against the status quo, not what the ceiling adds. The ceiling's own increment runs from −0.017 to +0.111: +0.005 at 3×, **−0.017 at 4×**, +0.036 at 5×. "Roughly parity at one demand level" understates it: the package ratio is 1.06 at 3×, 0.94 at 4× and 1.23 at 5×. | Report the increment, and say plainly that the ceiling adds little or nothing at 3–5× demand |
| A 20% ceiling cuts professional reseller margin by 71–89% at 5–10× (19, 137) | **No, a different quantity.** The scalper *utility index* falls 71–88% (`cap-sweep-agents.csv`) | Utility = 0.3 + 0.65 × ROI, capped at 0.95 (`gre_sim.py:706`). Converted back, status-quo ROI is ≥100% (the index saturates) and becomes −2% at 5× through −19% at 10× under a 20% ceiling. | "In the model, a 20% ceiling turns professional resale from a 100%-plus return into a loss (−2% to −19%) at 5–10× demand." Stronger and accurate; note that the status-quo figure is a floor. |
| Bounded ceiling beats the current market in 96–99% of 400 joint perturbations (239–240) | **From the file, yes:** PopWt 99.0%, System 96.5% (Fan 94.0%) | Generated 3 Jun 2026 with the systemic-fraud externality on in every draw (weight sampled 0.5–1.5). It was retired on 5 Jul; the baseline is now 0.0. Probably conservative, since the externality penalizes capped regimes, but it is not the current model. | Re-run `global_sensitivity.py` on the current model |
| A 10% ceiling beats a face-value ceiling on PopWt at every oversubscribed demand level (paired, N=250–300, all significant) (190–193) | **Not from the repo.** The 3 Oct paired runs were never saved; commit 25df598 touched only the brief and deck. | The stored grid (5% fees, unpaired) shows 10% + fee cap beating 0% + fee cap at 8 of 9 levels, and losing at 4× by 0.002. The 9 of 9 relies on DC's 10% fees in the unsaved runs. | Rebuild the paired script, save it, re-run at 10% fees |
| A 2% fee cap narrows the advantage and reverses it at moderate demand (203–205) | **Consistent with the stored grid**, where UK strict beats 10% + fee cap at 3× and 4× | Same unsaved paired runs | Same script |

**Update, 9 Nov 2026: re-checked with fans scored individually (`RESCORE_CHECK.md`; criteria fixed before the run).** The model's own scoring (S0) reproduces the stored results exactly. The verdicts below are under the two corrected scorings, S1 (minimal fix) and S2 (individual).

| Brief claim | Verdict | Under corrected scoring |
| --- | --- | --- |
| Optimal ceiling 10–30% (210–213) | **Fails** | Best cap is 50%, the top of the sweep, at 1.5–5× demand; 15–25% at 6–10×, where every cap from 15% to 40% is within 0.01 of the best. Even under S0 it was 40% at 1.5×. |
| Ceiling + fee cap = median 2.13× the fee cap alone (122–134) | **Fails** | Median 1.06–1.10. The brief's "fee cap alone" arm also has a face-value (0%) ceiling (`sweep_config.py:49–51`); the model has no fee-cap-only arm, so "the ceiling is the stronger lever" is unsupported under any scoring. |
| Beats the current market in 96–99% of 400 perturbations (239–240) | **Survives**, re-run with the externality off | PopWt 100%, System 99.2–100%. Fan-only drops to 81–86% (S0: 95.5%). |
| 10% beats face value at every level, paired (190–193) | **Survives** at both 5% and 10% fees, 300 seeds, CI > 0 | Small margin: +0.003 to +0.028 on the index. S0 fails at 5% fees (4×). |
| Same vs a 2-ticket face-value arm with dark cost 0.65 (194–196) | **Survives** | +0.011 to +0.035 |
| Bounded beats status quo, dynamic pricing, face value (audit brief claim 1) | **Survives under S1 only** | Under S2 the status quo wins at 3× (PopWt 0.252 vs 0.250) |

**What the brief can still say:**

- A cap beats the current market by a wide margin on the model's welfare composite at high demand: 0.22–0.33 against 0.08–0.13 on PopWt at 4–10×.
- A positive ceiling beats face value, consistently but narrowly.

**Qualifier from the exploratory follow-up (`RESCORE_CHECK.md`):**

- The win comes almost entirely from the composite's equality term: scalpers' returns fall, and the gap between mega and casual fans narrows. Total fan welfare is roughly unchanged, because a cap moves seats from mega fans to casual fans.
- The 4-ticket limit plays no part in the win.
- Caps above 50% lose ground fast, so a high cap does not reproduce the status quo.

**What it can't say:** that 10–20% is the optimal band, that the ceiling outweighs the fee cap, or (from 5 Nov) that 10–20% is role-proof.

**Not yet re-checked:**

- The 2% fee claim (203–205).
- The enforcement sweep.

**Update, 9 Nov 2026 (later): price-score check (`PRICE_SCORE_CHECK.md`, pre-registered, with amendment 1 made before any output was read).** Price harm above 2× face was re-scored two ways: P1 keeps counting harm at the same rate; P2 measures price against each fan's own valuation.

- **Fail under both:**
  - 10–20% is role-proof (0 of 9 levels under every scoring);
  - the 10–30% band;
  - "beats every alternative everywhere";
  - "fans are better off on average under 10–20%".
- **Survives under P1 only:** a single fixed cap of 40% is role-proof at 6 of 9 levels. Under P2 the status quo is role-proof from 4× up.
- **The verdict turns on a normative choice:** whether a mega fan paying 2.65× face for a ticket worth 4× to them counts as harmed.
- **Correction to the 9 Nov row on "the ceiling is the stronger lever".** The model has no fee-cap-only arm, but it can isolate the fee cap at a fixed ceiling (0% vs 0% + fee cap; 20% vs 20% + fee cap). So the lever comparison is testable. See `lever_check.py`. The brief's 2.13× ratio is still mislabelled and fails.
- **The composite can reward levelling down.** Under P1, dynamic pricing's composite beats the best cap at 3×, 4× and 6× while its mean fan utility is the lowest of any rule. Composite-only claims are unreliable.
- **The status quo's strength at 3× is a model artefact** (exploratory diagnosis, same day). It comes from the scalper markdown rule jumping from a 25% to a 55% final markdown just above 2× demand (`gre_sim.py:602–604`), which briefly puts dumped scalper tickets within casual fans' reach.
  - Caps are unaffected by the markdown rule.
  - Under the project's one documented markdown anchor (about 33% decay), the status quo loses to a fixed 40% cap at every level tested.
  - Neither fixed schedule clears the market as a real reseller would. That fix would be a pre-registered model change.

## 3. Facts and sources in the brief

| Claim (brief line) | Status | Source |
| --- | --- | --- |
| Ontario's face-value cap came into force on 31 July 2026, via Bill 94 (70, 276) | **Wrong date.** The cap came through the budget bill, with royal assent on 24 April 2026. The bill number is unconfirmed; check ola.org. | [Pollstar, 27 Apr 2026](https://news.pollstar.com/2026/04/27/ontario-resale-cap-goes-into-effect-ticketmaster-delists-tickets-to-comply/), opened 2 Nov |
| DC RESALE Act: 10% ceiling plus a 10% fee cap; the Mayor may reset the ceiling to 0–20% after a year (177–180, 284) | Verified | [DC Council](https://dccouncil.gov/council-gives-final-approval-to-resale-act-regulating-ticket-sales-and-capping-ticket-resale-prices/), opened 28 Oct |
| UK consultation's four capped options; £112M saving; 20% displacement assumption "lacks strong evidence" (154–172, 259–263) | Verified Aug 2026 | `SOURCES.md` |
| Leslie & Sorensen: resale adds about 5% efficiency, with a third lost to rent-seeking (63) | Verified Aug 2026 | `SOURCES.md` |
| Platform fees about 30% combined (116, 268) | Verified, with a caveat: GAO calls its sample nongeneralizable | `SOURCES.md` |
| Fraud incidence of 3.8% (UK), 13.6% (Ireland), 13.7% (Victoria) (280) | Exact figures, carrying three disclosed caveats (commissioned by StubHub; no causal claim; different panels) | `SOURCES.md` |
| Ireland: no prosecutions in five years (77–81) | Corroborated in the Oireachtas, May 2026 | `SOURCES.md` |

Everything except the DC and Ontario rows is carried over from `SOURCES.md` and was not re-opened today.

## 4. Positioning claims

| Claim | Status |
| --- | --- |
| No named concept covers role-proofness | Holds after the October concept search (web only) and Xie (2026), read in full on 28 Oct. **Still to read:** Babcock et al. 1995 (needs the PDF) and "Role-Reversal Consistency: An Experimental Study of the Golden Rule" (*Economic Inquiry*, 2019). |
| "Role-proof" is free as a name | No collision found (web search, 1 Nov 2026) |

## Next actions, in order

1. **Done 3 Nov 2026:** Patrick chose (a). The design and pre-stated criteria are in `ROLE_PROOF_TEST.md`; the code (`role_proof.py`, `test_role_proof.py`) is built, and the full run waits on his sign-off.
2. **Done 9 Nov 2026 for the robustness sweep** (`rescore-lhs.csv`, externality off). The enforcement sweep is still to do, if the essay uses it.
3. **Done 9 Nov 2026:** the paired runs were rebuilt and saved (`rescore_check.py`, `rescore-paired.csv`) at 5% and 10% fees. The 2% fee claim is not yet re-run.
4. **Claude drafts, Patrick approves:** brief corrections. These now cover:
   - the margin wording;
   - the Ontario date;
   - replacing the optimal-band and "stronger lever" paragraphs with what survives the 9 Nov re-check;
   - relabelling "fee cap alone" as the face-value-plus-fee-cap regime;
   - stating the band's actual rationale (Patrick, 9 Nov). 10–20% was never a target; it was a rough average of the cap optima. The point is a defensible, fixed band (Patrick, 9 Nov: "never assumed a single number but a defensible band"), chosen over a demand-indexed cap that would copy the scalper market's prices rising steeply with demand. The brief's "a finding, not a hedge" and "the hottest events need a slightly higher ceiling" framing contradicts this. Whether a single fixed cap holds up is tested as R2 and C8 in `PRICE_SCORE_CHECK.md`.
5. **Claude:** run the six-point `/validate-claim` on each headline once the re-runs are in. Running it on stale outputs would waste the check.

**Update, 9 Nov 2026:** item 4 is drafted in the working copy of `POLICY_BRIEF.md`. The change log, decisions and evidence are in `BRIEF_REVISION_2026-11-09.md`; this awaits Patrick's approval. Item 5 is done for the brief's three new headlines; the results are in the same file.

- **H1 holds at a 20% ceiling under every check.** At 30% it fails one check.
- **H2 holds only at moderate demand.** It depends on the formula resale-option term.
- **H3 holds,** with caveats.
- **Proceeds-scored check, done 9 Nov** (`proceeds_check.py`). Scoring resale by what fans actually recovered restores both ends of the band. 20–30% with the fee cap beats face value at every level, and the ceiling is the stronger lever up to 6×.
- **Exploratory finding, 11 Nov: against face value, the band passes the role-proof test for ticket holders.**
  - **Source:** the role-proof runs (`role-proof-roles.csv`, `price-check-roleproof-roles.csv`), at today's 15% fees, with no fee cap.
  - **Holders always prefer the band.** After allocation under any of the 11 menu rules, continuing under a 20% or 30% ceiling beats face value in every case at every oversubscribed level, under P0, P1 and P2, at every κ: 0 of the holder cases.
  - **Their preference grows with the endowment shift.** Median holder gain over face value at κ = 0 / 0.5 / 1:
    - 20%: +0.037 / +0.052 / +0.065;
    - 30%: +0.068 / +0.094 / +0.117.
  - **Have-nots mostly prefer the band too.** Exceptions out of 414 cases (demand × primary rule × role), all have-nots: P0 13, P1 2, P2 23 for 20% and 54 for 30%. Most are mega-fan have-nots at 2–4×, who can buy on the dark market under face value, plus average-buyer have-nots under P2 at 30%.
  - **Caveats:** not pre-registered; no fee cap in these runs; resale valued by formula. The 9 Nov proceeds check found the realized 0%-vs-20% gap close to the formula's.
- **Listing check, done 11 Nov** (`LISTING_CHECK.md`, pre-registered). With frictionless fan listing, the band still beats face value at every level, and 30% still beats 20%. "The ceiling is the stronger lever on its own" fails: the fee cap wins at 1.5–6×. The brief no longer ranks the levers.

## External audit, 12 Nov 2026: triage (15 Nov)

**Source.** The report is in `audit results/roleproof_audit_report_2026-11-12.md`. Its verdict: **do not publish the brief as written.** The within-model baseline (a 20–30% ceiling beats fee-capped face value) reproduces, but several claims fail. Each finding was checked by Claude on 15 Nov.

| ID | Finding | Checked | Status |
| --- | --- | --- | --- |
| F01 | Dark asks exceed every buyer's WTP at high demand. Zero dark sales; routed tickets destroyed; touting "losses" are an artefact. | Code plus runs. 0% of dark tickets sell at ≥6× under every cap. Replication of the audit's repricing: 10× at 30% + fee, ROI −1% → **+42.4%**; the band still beats face value for fans. | **Confirmed. The brief's touting claim (C3) must be withdrawn pending repair.** |
| F02 | Frictionless listing plus zero resale-option weight together reverse 20% and 30% vs face value | Clean replication, 250 paired seeds: e.g. 7× P0 at 20%, −0.0022, CI < 0 (audit −0.0023) | **Confirmed.** Nuance: frictionless listing with *realized* resale scoring (`LISTING_CHECK.md` L1–L2, B) still holds. The reversal needs resale valued at zero. |
| F03 | The LHS robustness figure is the best of 10/20/30% per draw and lens, not a fixed ceiling | Code: `rescore_check.py`, `one_draw` takes the `max` over caps | **Confirmed.** C6 wording oversells it. |
| F04 | "Role-proof" is minimax regret within 0.01, not acceptance by all; scalpers and the fee-capped arms are outside the menu | Matches the design docs | **Confirmed** (and previously noted) |
| F05 | Dark routing compares net dark revenue with the gross platform ask | `gre_sim.py:493–497` vs `:283` | **Confirmed** (modest numeric effect per the audit) |
| F06 | Ontario: Bill 97 Sch. 16, not Bill 94; the cap's base is the original *total* price paid; 24 Apr 2026 | The Ontario explainer confirms the base is "original total price paid to the primary seller". The bill number could not be checked (the pages need JavaScript). | **Base and date confirmed; bill number per the audit's official-statute citation** |
| F07 | DC: the resale base is the total initial price incl. fees and taxes, +10%; a single marketplace fee ≤10% of that total (not 10% per side); second reading 14 Jul, effective 25 Sep 2026, applies 1 Jan 2027; Mayor may adjust (0–20%, fee 5–20%) from 2028 | Official text, D.C. Law 26-181 | **Confirmed.** C5's "DC's actual fees" is wrong; it is a hypothetical 10%-per-side run. |
| F08 | "A positive ceiling is the minimum condition for lawful resale" rests on uncalibrated listing behaviour and a formula option value | Consistent with `LISTING_CHECK.md` L4 | **Accepted** |
| F09 | Buyer affordability ignores the buyer fee | `gre_sim.py:628` | **Confirmed** |
| F10 | Fan resale has a face-value price floor (`max(FACE, …)`) | `gre_sim.py:618–619` | **Confirmed** |
| F11 | Forking paths: the band and the mean-fan lens were chosen after pre-registered failures; `--verdicts` reads stored P1/P2 rather than re-simulating | Accurate | **Accepted** |
| F12 | Endowment = resale-weight shift only; WTP fixed per type | Accurate (in the ledger) | **Accepted** |
| F13 | Oracle enforcement favours caps against today's market; the disclosure is narrow | Accurate (in the ledger) | **Accepted** |
| F14 | Prior art: Costa-Gomes, Ju & Li (2019) "Role-Reversal Consistency", *Econ Inquiry* 57(1); Kydland–Prescott (1977); Kőszegi–Rabin (2006) | The Costa-Gomes paper was already on our unread list | **Accepted.** Qualify novelty as a synthesis or extension. |
| F15 | Leslie–Sorensen's one-third offset is rent-seeking *plus* transaction costs; several broad narrative assertions | `SOURCES.md:57–62` already says "plus resale transaction costs"; the brief dropped it | **Confirmed** |

Replication scripts are in the session scratchpad (exploratory). No repo code was changed.

## Model v2 final experiment (15 Nov 2026; `V2_PREREGISTRATION.md`)

The four audit mechanics were fixed; v1 is reproducible byte for byte; 62,100 runs. The pre-registered decision is **D1: a fixed 20–30% band.**

- **Every positive ceiling beats face value for fans** at all levels in both realistic scenarios, under all price scores.
- **Scalpers are fairly governed at 0–30%** (returns 0–25%, ≥90% lawful); **not at 40%** (34%).
- **30% beats 20% for fans.**
- **Role-proof against face value: only 10%, under the model's listing rule.** Mega fans are worse off under 20–40% at 3–4×.
- **The fail bound:** frictionless listing plus resale valued at zero.

The touting claim is now: 16–17% returns at 20% and 25% at 30%, against 100%+ today. The old "loss at extreme demand" claim is withdrawn.

## Final external audit, 17 Nov 2026: triage

Report: `audit results/roleproof_v2_audit_report_2026-11-17.md`.

**Call: publish after wording and evidence fixes.** All 13 findings were checked by Claude on 17 Nov:

- **Verified from data:** N01, N02, N05 (re-analysis of the auditor's stress CSVs), and N06 and N09 (from `v2_verdicts.txt`).
- **Verified from official sources in the browser:** N04 (Bill 97, Sch. 16, s. 2(3)) and N12 (UK written answer of 18 Sept; Commons debate of 4 Nov).
- **Verified in code:** N11 (`gre_sim.py:493`: tickets are never decremented on resale).
- **Accepted as stated:** N03, N07, N08, N10, N13.

**All are fixed as wording or evidence; none reverses B1.** No model or analysis change was made, per the agreed scope.
