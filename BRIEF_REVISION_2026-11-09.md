# Policy brief revision, 9 Nov 2026: change log for Patrick's approval

*Drafted by Claude for Patrick to approve, per `CLAIMS_REGISTER.md` next action 4. The edits are in the working copy of `POLICY_BRIEF.md` and are not committed.*

- **To see the redline:** `git diff POLICY_BRIEF.md`.
- **To reject everything:** `git checkout -- POLICY_BRIEF.md`.
- **To reject one edit:** say which, and I'll restore the original text.

## Decisions for Patrick

1. **The band.** *(Reframed 9 Nov: Patrick wants a defensible band, not one number.)*
   - The draft recommends a fixed 20–30% band (the consultation's top option), not indexed to demand. It explains why the band sits where it does: 10% gives up fan gains; 40% leaves touting profitable and loses on the index at extreme demand. It also names the trade-off inside the band:
     - 30% does more for fans on average at moderate demand;
     - 20% is the more robust result (it survives every kill test below), squeezes touting harder, and scores slightly better on the welfare index at extreme demand.
   - **20% is the end that survives every check; 30% is the end that does most for fans.** The band also assumes the fee cap. Under today's fees, the best fixed ceiling is about 40%.
   - **Alternatives:** name one figure (30% or 20%), or go above the consulted range.
     - 40% is the best single figure in runs *without* a fee cap.
     - *With* the fee cap, 40% does about as well for fans as 30% but leaves touting returning 7–17% at 6–10× demand.
2. **The role-proof paragraph** ("What we did differently"). It reports honestly that the test's verdict turns on how a high-value fan's high payment counts.
   - **Keep it** if the brief advertises the test, which it does in the paragraph above.
   - **Or cut both** and let the brief rest on the welfare evidence.
3. **The withdrawal sentence on 2.13×** (in "Both levers help fans"). Keep it if the August version was circulated; drop it if it never left your hands.
4. **Facts to confirm:**
   - **Ontario's bill number and title.** Source 7 now carries a placeholder: "[bill number and title to be confirmed on ola.org]".
   - **"Failed in three jurisdictions"** (summary). This was never in the claims register, and the brief's own source 6 gives Victoria's cap as 10%, not face value.

## Edits and their evidence

The basis column marks how each figure was produced:

- **Pre-registered:** criteria were fixed before the run (`RESCORE_CHECK.md`, `PRICE_SCORE_CHECK.md`).
- **Exploratory:** run afterwards to size the new sentences, with paired seeds and 95% confidence intervals.
- **Fact:** a verified source.

P0, P1 and P2 are the three price scores in `PRICE_SCORE_CHECK.md`. Every sentence below holds under all three unless it says otherwise.

| # | Section | Was | Now | Evidence | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Header | August 2026 | "August 2026, revised November 2026" | — | — |
| 2 | Summary | The fee cap paired with face value "throws away most of the benefit" | "gives up a second gain for fans, one that is the larger of the two at moderately oversubscribed events" | `lever_check.log` plus kill test K1: the ceiling alone beats the fee cap alone up to 4–5× under every check; at higher demand the result depends on the resale term | Exploratory |
| 3 | Summary | "10–20% … roughly doubles the fan-welfare gain … cutting the touting margin by 71–89%" | 20–30% band; fans better off on average than with the draft Bill's face-value ceiling: at 20% at every level under every check, at 30% except under the most demanding check at the extremes; resellers' returns cut from ≥100% to about a quarter or less at 4× and above, and to break-even or a loss at the extremes | `brief_claims_check.log`, `kill_test_h1h2.log` | Exploratory |
| 4 | Ontario | In force 31 July 2026 | In force April 2026 | Pollstar, 27 Apr 2026; royal assent 24 Apr 2026 (`CLAIMS_REGISTER.md` §3) | Fact |
| 5 | What we did differently | No result given for the test it describes | New paragraph: the verdict turns on whether a high payment by a high-value fan counts as harm. If not (P1), a fixed ~40% cap passes at most levels (6 of 9). Judged against each fan's valuation (P2), the status quo passes at high demand. | `PRICE_SCORE_CHECK.md` R2: survives under P1 only | Pre-registered (amendment 1) |
| 6 | Two levers | "The ceiling is the stronger of the two levers … median 2.13×" | Both levers help fans at every level; each does more with the other; taken one at a time the ceiling is stronger; 2.13× withdrawn | `lever_check.log`, mean fan utility, all scorings, CI > 0, **but it fails kill test K1** (below). The text now limits it to moderate demand. | Exploratory; 2.13× failed as pre-registered C2 |
| 7 | Touting | "Cuts margin by 71–89%" | Returns ≥100% (the index ceiling) under today's market at 4× and above. 20% + fee cap: about 8% at 5×, a loss from 6×. 30% + fee cap: about 18% at 5×, single figures at 6–8×, about break-even at 10×. Roughly 15–25% at 1.5–4×. | `brief_claims_check.log`: ROI inverted from scalper utility (`gre_sim.py:706`) | Exploratory |
| 8 | Recommendation | "10–20% band" | "the 20–30% band, fixed rather than indexed to demand" | As rows 3 and 13 | Decision 1 |
| 9 | Consultation | "the middle of the range" | "the top of the range" | Follows row 8 | — |
| 10 | Paired runs | 10% beats face value on PopWt everywhere, N=250–300, holding with the resale term removed | 10%, 20% and 30% with the fee cap beat face value on fans' average at every level (300 paired, CI > 0). 10% also beats it on the index, including with DC's 10% fees and against the tougher face-value arm. The "resale term removed" clause is dropped, since it was never re-checked. | `brief_claims_check.log`; `RESCORE_CHECK.md` C4 and C5 survive | Exploratory, plus pre-registered C4/C5 |
| 11 | 2% fee caveat | "Narrows sharply and reverses at moderate demand" | "the advantage of a 10% ceiling becomes small at every level" | Stored grid: 10% + 5% fees beats 0% + 2% fees by +0.001 to +0.016 on the index at every level, all scorings. No reversal under corrected scoring. | Grid read, unpaired, not CI-tested |
| 12 | Band paragraph | "A band … rises steadily with scarcity … a finding, not a hedge" | "A fixed band, chosen for a reason", stating Patrick's rationale: a defensible, auditable band, not indexed to demand. Explains why 10% and 40% fall outside it, and notes the band assumes the fee cap. The best ceiling does not rise with demand. With the fee cap, 30% beats 20%, 10% and face value for fans at every level. Names the 30%-vs-20% trade-off. | `brief_claims_check.log` (30% vs 20% on fans' average, CI > 0 at all levels; 20% ahead on the index at 6–10×); `explore_fee_packages.log` for 40% | Exploratory |
| 13 | Closing | "leaves professional touting without a business model" | "turns professional touting from a highly profitable business into a marginal one"; the face-value squeeze "does not reliably happen in practice" | Row 7 | Exploratory |
| 14 | About the evidence | 96–99% robustness; "no single parameter can be tuned to reverse it" | 99–100% on the index, 81–86% fans alone. The scoring correction is disclosed, and which comparisons were pre-registered vs added afterwards. The parameter-tuning clause is dropped (not re-checked). | `RESCORE_CHECK.md` C3 survives | Pre-registered |
| 15 | Limitations | Two limitations, ending "across every weighting we tested … outperforms both the current market and a face-value cap" | Three limitations: no precise elasticity or best figure; equality weighting and the price judgement are explicit; the scalper markdown rule is stylised. Ends: "a positive ceiling outperforms a face-value ceiling" under every scoring tested. The current-market half is dropped: on fans' average it depends on the price score (P2: the status quo is slightly ahead at 6–10×). | `PRICE_SCORE_CHECK.md`; `brief_claims_check.log` | Both |
| 16 | Source 7 | "Bill 94 … in force 31 July 2026" | Budget bill, royal assent 24 April 2026, with a placeholder for the bill number; adds Pollstar | Row 4 | Fact |

## Not changed and not re-checked

These are unchanged in the brief. They were not part of the fan-scoring re-checks:

- **"Leakage responds to the price gap, not the fee rules."** Dark-market volumes don't depend on fan scoring.
- **The Government analytical-note paragraph.**
- **The Leslie & Sorensen, Ireland, Victoria and GAO passages, and sources 1–6 and 8–11.** These were verified in Aug–Oct (`SOURCES.md`) and not re-opened today.

## Other documents still carrying the old claims

- **`README.md:13–15`:** "10–30% band", "a fixed 20% cap", "10–20%" under capped fees.
- **`GRE-pitch-deck.pptx` / `.pdf`:** last updated with the brief in commit 25df598.
- **`gre-audit-package/`** (`AUDIT_BRIEF.md`, a copy of the brief and deck) and **`gre-audit-package.zip`**.

None of these is edited yet. They should follow the brief once you approve it.

## Scripts behind the new figures

These are exploratory and in the repo, uncommitted:

- `explore_fee_packages.py` / `.log`: 100 paired seeds, 0–40% ceilings with the fee cap.
- `brief_claims_check.py` / `.log`: 300 paired seeds with CIs, for rows 3, 7, 10 and 12.
- `lever_check.py` / `.log`: 300 paired seeds, the fee cap × ceiling 2×2, for rows 2 and 6.

## /validate-claim results (9 Nov 2026)

**Claims checked:**

- **H1:** with the fee cap, a 20–30% ceiling beats face value on fans' average at every level.
- **H2:** taken one at a time, the ceiling is the stronger lever at every level.
- **H3:** resellers' returns of 100% or more under today's market fall to about a quarter or less, and to break-even or a loss at the extremes.

**Kill-test runs:**

- `kill_test_h1h2.py` / `.log`: 300 paired seeds per demand level.
- An ROI-inversion and markdown check, done inline: 60 seeds, plus `explore_3x.log`.

### Verdicts

1. **Real alternative.**
   - **H1: CAVEAT.** The comparator is the draft Bill as modeled (`sweep_config.py:49–51`: face value, 4-ticket limit, fees 5%/side). The 5% fee-cap level is the model's assumption (`sweep_config.py:42–43`), not the Bill's figure.
   - **H2: CAVEAT.** It is a decomposition of the levers, not a real policy choice, and it depends on the step sizes chosen (fees from 15% to 5%; ceiling from 0% to 20%).
   - **H3: SATISFIED.** Today's market is the comparator (`sweep_config.py:24`). Resellers' alternatives are modeled: the dark market (`gre_sim.py:636–688`) and exit.
2. **Independent observer.**
   - **H1 and H2: FAILS for H2, CAVEAT for H1.** Fan utility is the model's own index (`gre_sim.py:308`; `role_proof.py` `agent_utility`). Its resale-option term is assigned by formula from the cap level (`role_proof.resale_option` → `upside_value`), so part of the outcome is defined to rise with the ceiling. K1 shows that term carries about three-quarters of H1's margin at high demand and flips H2 there.
   - **H3: CAVEAT.** The return is separate revenue-over-cost accounting (`gre_sim.py:633`, `686`, `720–726`), but:
     - it excludes bot, labour and holding costs;
     - the index tops out at 100% (`gre_sim.py:722–727`);
     - today's-market asks at 4× demand and above (mean face × (1 + 0.65 × demand), `gre_sim.py:475`) are well above the anchored average markup of more than 50% (`project_gre_empirical_anchors`: "~75% modeled").
3. **Symmetric scrutiny: CAVEAT.** Every arm in H1 and H2 carries the same enforcement package (`gre_sim.py:76–87`). The face-value arm, though, carries two unaudited handicaps:
   - fans list for resale with probability 0.5 at face value, rising to 1.0 at 10% (`gre_sim.py:517`, uncalibrated);
   - the formula resale option.
   A tougher face-value arm was tested (K2), but the best-case one, where fans list as readily as under a positive ceiling, was not. For H3, caps get perfect on-platform enforcement against face value (`gre_sim.py:613`), which flatters the capped arms against today's market.
4. **Information leak: CAVEAT.**
   - **Resellers know the true demand multiplier** (`expected_scalper_margin`, `gre_sim.py:253–290`; the ask formula at `gre_sim.py:475`).
   - **The dark market matches tickets to buyers by true willingness to pay,** a hidden type (`gre_sim.py:650–675`). This helps the face-value arm, so it is conservative for H1.
   - **Caps are enforced against a perfectly known face value,** with an identity registry and non-transferable barcodes assumed (`gre_sim.py:76–85`, `613`). This is the price-of-record problem the registrar idea addresses. It applies to both arms of H1 and H2, but flatters caps against today's market.
5. **Kill test.**
   - **K1, resale-option term removed** (weights renormalised):
     - H1 at 20% survives at all levels and under all scorings, but the margin at 10× falls from +0.0053 to +0.0012 (P0).
     - **H1 at 30% fails at 7–10× under P2** (−0.0010 to −0.0012, CI < 0).
     - **H2 fails at high demand.** The fee cap alone beats the ceiling alone at 8–10× (P0/P1) and 6–10× (P2). → **FAILS for H2 as originally worded; the text is now limited to moderate demand.**
   - **K2, tougher face value** (2-ticket limit, dark cost 0.65, same fee cap): 20% and 30% both beat it at every level, all scorings. → SATISFIED.
   - **H3:** today's-market saturation at 4× and above holds under all four markdown schedules (`explore_3x.log`). Inverting the mean index matches the run-by-run mean within 0.5 points. → SATISFIED.
   - **Not run:**
     - resale value scored by realized proceeds instead of the formula (`role_proof`'s proceeds variant exists);
     - fans listing as readily under face value (needs a `p_list` option in `gre_sim.py`).
6. **Proxy vs regime: CAVEAT.** Results use 300 paired seeds per level, but at toy scale: a 500-seat venue (`gre_sim.py:54`), a fan base of 430 × demand, one event, and no multi-event dynamics. Nothing has been confirmed at market scale.

### The claims as currently defensible (now in the brief)

- **H1.** With the draft Bill's fee cap, a 20% ceiling leaves fans better off on average than a face-value ceiling at every level of demand tested. That holds under every check run, including with resale-option value removed and against a tougher face-value regime. A 30% ceiling does too, except with resale value removed and price judged against each fan's own valuation, when it falls slightly behind at 7–10×.
- **H2.** Taken one at a time, the ceiling is the stronger lever up to four or five times demand. At the extremes the two are close, and which wins depends on how much fans value being able to resell.
- **H3.** In the model, today's resellers earn at least 100% on stock at four or more times demand (the index tops out there). With the fee cap, a 20% ceiling cuts this to about 18% at 4×, 8% at 5× and a loss from 6×. A 30% ceiling cuts it to about 26%, 18%, single figures, and break-even at 10×. These are revenue-over-cost returns, before bot, labour and holding costs.

### The rest

- **Most dangerous unmet item:** the resale-option value. It is assigned by formula, it carries the high-demand results, and nothing outside the model checks it.
- **Cheapest experiment to close it:** re-run `kill_test_h1h2.py`, scoring resale by realized proceeds (`role_proof.agent_utility(..., proceeds=True)`) instead of the formula option. It needs no model change; about 10 minutes.

## Follow-up: proceeds-scored check (9 Nov 2026, run at Patrick's go-ahead)

`proceeds_check.py` / `.log` used 300 paired seeds per level, with the same seeds as `kill_test_h1h2.py`. Its default rows reproduce the kill test's reference rows exactly.

**Two variants, both defined in the script header before running:**

- **A.** Fans who resold are scored on their realized net upside (the 5 Nov proceeds variant). Everyone else keeps the formula value.
- **B.** As A, but every other ticket holder gets the resale channel's realized value in that run, averaged over fans whose plans changed. Unsold or unlisted tickets recover nothing.

**The resale channel, formula vs realized** (at 3× and above):

| Arm | Formula | Realized |
| --- | --- | --- |
| Face value + fee cap | 0.15 | ~0.10 |
| 20% at today's fees | 0.30 | ~0.21 |
| 20% + fee cap | 0.50 | ~0.44 |
| 30% + fee cap | 0.70 | ~0.61 |

The formula overstates every arm, but the order and the 0%-vs-20% gap are preserved.

**Results under A and B:**

- **H1, both ends of the band:** 20% and 30% with the fee cap beat face value with the fee cap at every level, under all three price scores (CI > 0).
- **Within the band:** 30% beats 20% for fans at every level.
- **H2:** the ceiling alone beats the fee cap alone at every level up to 6×, under all scorings. At 7–10× under B, P0/P1 still favour the ceiling (+0.0009 to +0.0015). Under P2 the fee cap edges ahead by 0.0002–0.0003, effectively level.

**Revised verdicts:**

- **H1: SATISFIED at both ends of the band.** 30% fails only the zero-resale-value bound (K1, P2, 7–10×), which is now disclosed in the brief as the one check 20% survives and 30% doesn't.
- **H2: SATISFIED up to 6× demand; "effectively level" at the extremes.** The brief text was updated to say so.

**Remaining most dangerous item: `p_list`** (`gre_sim.py:517`). The model has fans list resale tickets half as often under face value, which is uncalibrated and favours positive ceilings. Testing it needs a model option, so it would need pre-registering.

## Follow-up: listing check (11 Nov 2026, pre-registered in `LISTING_CHECK.md`)

The test lets every fan whose plans change list their tickets, whatever the ceiling. That is the best case for face value.

- **The band's claims hold:** both ends beat face value at every level, and 30% beats 20%. Margins narrow, by about half at 10×.
- **"The ceiling is the stronger lever on its own" fails.** With frictionless listing, the fee cap alone beats the ceiling alone at every level from 1.5× to 6×.

**Brief changes, 11 Nov:**

- **Summary:** "gives up a second, separate gain for fans" (no ranking of the levers).
- **Lever paragraph:** retitled "Both levers help fans, and the recommendation keeps both". It now says which lever is stronger on its own depends on how readily fans list at face value, and makes no claim either way. The 2.13× withdrawal stays.
- **Robustness sentence:** adds the frictionless-listing check.
- **Limitations:** listing behaviour joins the scalper markdown rule as stylised.

**Remaining validate-claim items:** none are open for the band against face value. The open model questions (resellers' knowledge of demand, perfect price-of-record enforcement, toy scale) are disclosed in the brief's limitations or in this log.

## Additions, 11 Nov 2026 (Patrick: "Yes, add it")

**1. Role-proof paragraph ("What we did differently").** It now opens with the result against face value:

- Once tickets are allocated, every holder prefers a 20–30% ceiling to face value at every level, whichever rule ran the sale and however price is scored, and more so as the endowment effect strengthens.
- Most have-nots agree. The main exceptions are committed fans who missed out at moderate demand, who can buy from touts off-platform under face value.
- It is flagged as runs at today's fees, without the fee cap.

The conditional result against today's market follows, unchanged.

- **Evidence:** `CLAIMS_REGISTER.md`, exploratory finding of 11 Nov (from the role-proof roles CSVs).
- **Basis:** exploratory, not pre-registered.

**2. Limitations.** "Three" became "Four". The fourth: the model assumes ceilings are enforced on-platform against a known face value (a price of record), with an identity registry and non-transferable barcodes (`gre_sim.py:76–85`, `613`).

- It doesn't tilt band vs face value.
- It flatters any cap against today's market.
- It makes a price-of-record keeper a precondition of any ceiling.
- This was offered alongside the holder finding; **drop it if you'd rather not raise the registrar in the brief.**

## Rewrite, 15 Nov 2026: model v2, decision D1

**This supersedes the edit table above.** `POLICY_BRIEF.md` was rewritten from the pre-registered v2 results (`V2_PREREGISTRATION.md`, decision D1) and incorporates the external audit's corrections (`CLAIMS_REGISTER.md`, audit triage). Withdrawn claims and corrected facts are listed in `CORRECTION_LOG.md`, which the brief references.

**Every number in the brief now comes from `v2_verdicts.txt` / `v2-runs-*.csv.gz`:**

- **Fans' gain over face value:** 4–11% at 20% and 7–24% at 30%, on the index. Computed from the v2 runs (S1/S2, B, P0).
- **Access and lawful resale at 5×:** the "reported" block of `v2_verdicts.txt`.
- **Reseller returns and off-platform shares:** Q3.
- **Role-proof and the condition:** Q4 and Q1 S4.

**Still Patrick's decisions:**

1. **The closing disclosure.** The audit (F13) says it is narrower than needed *if* the author has or expects any role in a price-of-record, registrar, implementation or consulting system the recommendation presupposes. Only Patrick can say what is accurate.
2. **Ontario's bill number.** The audit cites Bill 97, Schedule 16, and we could not verify it because the Ontario pages need JavaScript. Source 7 cites S.O. 2026, c. 2, with "[bill number to be confirmed]".
3. **Dropped sources.** The DOJ / Live Nation entry is no longer referenced in the text and was dropped. Restore it if wanted.
4. **Other documents still carrying old claims:** the README, the deck, and the old audit packages.
