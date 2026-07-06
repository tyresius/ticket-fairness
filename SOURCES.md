# GRE Empirical Sources & Citation Ledger

Provenance-graded sources anchoring model parameters and policy claims.
Grades: **A** = official/peer-reviewed, cite freely · **B** = industry-funded
or advocacy, cite only with disclosure · **C** = secondary reporting, verify
before citing. Last updated 2026-07-05.

## UK 2026 policy (the deck's new framing hook) — grade A

- **Government response to the resale consultation** (19 Nov 2025): resale
  above face value + unavoidable fees to be made illegal; platform service
  fees capped; platforms given legal enforcement duty; resale quantity
  limited to original purchase entitlement. Projects £112M/yr fan savings,
  −£37 average resale price, 900k more primary purchases.
  https://www.gov.uk/government/consultations/putting-fans-first-consultation-on-the-resale-of-live-events-tickets/outcome/government-response-to-the-consultation-on-the-resale-of-live-events-tickets
- **Commons Library briefing SN04715** (13 Jan 2026) — consolidated history
  and data. https://commonslibrary.parliament.uk/research-briefings/sn04715/
- **King's Speech (13 May 2026)**: draft Ticket Tout Ban Bill published for
  pre-legislative scrutiny + Sporting Events Bill. Final legislation
  potentially years out — the evidence window for a cap-level argument is
  open now. (Slaughter & May / RPC / Lewis Silkin analyses concur.)
  https://www.slaughterandmay.com/insights/new-insights/at-face-value-the-king-s-speech-and-the-future-of-ticket-reselling-in-uk-sport/

**Model artifact:** `sweep_config.py` UK-2026 series (0% cap + 5%/2% fee
caps); results in commit 8a7e4d7. Headline: fee cap helps (+0.04 PopWt) but
Bounded 20% under the same fee cap gains 2–3× more; levers super-additive;
dark leakage driven by the price gap, untouched by the fee cap.

## Fees — grade A

- **GAO-18-347** (Apr 2018): primary fees ~27% of face; combined secondary
  fees ~30–31%; presale/hold allocations 10–65% + ~16% holds (single-queue
  scope limitation). Anchors `SECONDARY_FEE_SELLER/BUYER = 0.15/0.15`.

## Fraud by regime — grade B (industry-funded; disclose)

- **Bradshaw Advisory** (June 2025, commissioned by StubHub): UK uncapped
  3.8% / Ireland face-value cap 13.6% / Victoria 10% cap 13.7% (2-yr rates).
  Causal caveats: enforcement absence in Ireland (zero prosecutions since
  2021) may explain more than the cap. **Calibration status: the model's
  dark channel cannot reproduce these levels under either denominator
  (see calibrate_tx_denominator.py, 20–25× gap) — cited as motivation only,
  never as a fitted target.** Anchors `BASELINE_SECONDARY_FRAUD_PENALTY`
  ratio (0.07 ≈ 28% of 0.25, matching 3.8/13.6).

## Market structure — grade A

- **CMA Viagogo/StubHub merger report + UK Gov analytical note**: top 10% of
  resellers >70% of volume; ~80% of uncapped platform volume is
  professional; £404M resale on 1.5M tickets. Anchors scalper concentration.
- **UK Gov analytical note**: ~20% displacement to unregulated channels
  projected under a face-value cap. Anchors `DARK_LEAKAGE_*` directionally.

## Behavior — grade B (scalper-lobby data; disclose)

- **Protect Ticket Rights / Automatiq** (July 2025): 62% of events resale
  below face; ~33% price decay to event day. Anchors demand-distribution
  portfolio (calibrate_* scripts) and 3-round markdown decay.

## Enforcement — grade A

- **FEAT AGM Oct 2025 / open letter Jan 2026**: 275+ DSA-flagged illegal
  listings, zero takedowns. `SCALPER_DARK_COST = 0.45` assumes an
  enforcement regime that does not currently exist in the EU — stated as an
  assumption, load-bearing for capped-regime results.

## Known unverifiable / do not cite

- "Leslie & Sorensen 75th-percentile threshold" as circulated — verify
  against the actual REStud paper before any use.
- Any secondary-AI-reported figure not traceable to the sources above.
