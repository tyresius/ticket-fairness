# GRE Empirical Sources & Citation Ledger

Provenance-graded sources anchoring model parameters and policy claims.
Grades: **A** = official/peer-reviewed, cite freely · **B** = industry-funded
or advocacy, cite only with disclosure · **C** = secondary reporting, verify
before citing. Last updated **2026-08-03** (full primary-source verification pass).

> **Verification status:** every claim below was re-checked against primary
> sources on 2026-08-03. Items previously flagged "unverifiable" have been
> resolved — see the Leslie & Sorensen entry, which is real and whose *actual*
> findings support the thesis better than the misremembered version did.

## UK 2026 policy — grade A (VERIFIED)

- **"Putting Fans First" consultation** ran 10 Jan – 4 Apr 2025; government
  response published 19 Nov 2025. Chosen policy: resale above face value +
  unavoidable fees made unlawful; platform fees capped; quantity limits;
  CMA enforcement powers.
  https://www.gov.uk/government/consultations/putting-fans-first-consultation-on-the-resale-of-live-events-tickets/outcome/government-response-to-the-consultation-on-the-resale-of-live-events-tickets
- **The consultation's own cap menu (KEY):** five options were offered —
  (1) no uplift/face value, (2) ≤10%, (3) 10–20%, (4) 20–30%, (5) other.
  Government stated it had **"no favoured approach at this stage."** It then
  selected the strictest. *Our 10–30% recommendation sits inside options 2–4
  that the government itself consulted on — this is not an exotic ask.*
  https://gov.uk/government/consultations/putting-fans-first-consultation-on-the-resale-of-live-events-tickets/putting-fans-first-consultation-on-the-resale-of-live-events-tickets-html
- **Government analytical note (THE GAP WE FILL):** projects £112M/yr reduced
  fan spend (£6,405M → £6,293M), average resale price −£37 (£269 → £233).
  Critically, it assumes a **"20% displacement effect"** (touts continuing to
  sell above cap off-platform) and concedes this assumption **"lacks strong
  evidence."** Their impact case counts the savings and does not model the
  behavioural response. That is precisely what the GRE simulation quantifies.
  https://www.gov.uk/government/publications/government-response-to-resale-of-live-events-tickets-consultation-analytical-note/analytical-note-on-government-response-to-resale-of-live-events-tickets-consultation
- **Draft Ticket Tout Ban Bill** announced King's Speech 14 May 2026; **draft
  only**, subject to pre-legislative scrutiny + further consultation. Full
  legislation potentially years away.
- **Commons Library briefing SN04715** (Lorraine Conway) — real; the direct
  PDF host 403s automated fetch, cite the landing page.
  https://commonslibrary.parliament.uk/research-briefings/sn04715/

**Submission status (as of 2026-08-03):** pre-legislative scrutiny committee
NOT yet named (candidates: DCMS Select, Business & Trade, or a joint
committee). Call for evidence NOT yet open — draft Bill text unpublished
(expected ~Q3 2026). No second consultation open. **There is currently no
official channel to submit into; the window is imminent, not open.**

## Fees — grade A (VERIFIED, with caveat)

- **GAO-18-347** (published 12 Apr 2018, released 14 May 2018): primary-market
  fees averaged **27%** of ticket price; secondary-market fees averaged **31%**.
  ⚠️ **Caveat to disclose:** GAO describes this as a *"nongeneralizable sample"*
  of events — directional, not a population estimate.
  Anchors `SECONDARY_FEE_SELLER/BUYER = 0.15/0.15` (≈30% combined).
  https://www.gao.gov/products/gao-18-347

## Rent-seeking & resale welfare — grade A (VERIFIED; RESOLVED from "do not cite")

- **Leslie & Sorensen (2014), "Resale and Rent-Seeking: An Application to
  Ticket Markets," *Review of Economic Studies* 81(1): 266–300.** Real,
  peer-reviewed, and directly supportive. Actual findings: resale raises
  allocative efficiency by **~5% on average**, but **roughly one third of that
  gain is offset** by costly rent-seeking in the *primary* market plus resale
  transaction costs. Rent-seeking takes the form of brokers investing in
  strategies to buy up tickets fast at on-sale.
  **Why this matters:** it is peer-reviewed empirical support for the
  cap→primary-participation feedback mechanism we model (Channel 2 of
  `scalper_wanted`) — resale profitability drives contested primary
  acquisition. It also supports the bounded (not zero, not unlimited) framing:
  resale creates real efficiency gains worth preserving, *and* real rent-seeking
  costs worth bounding.
  https://academic.oup.com/restud/article-abstract/81/1/266/1730966
  (open PDF: https://users.ssc.wisc.edu/~atsorensen/papers/leslie_sorensen_2014.pdf)
  ⚠️ The previously circulated **"75th-percentile threshold"** claim is **not**
  among the paper's findings as verified — **do not cite it.**

## Fraud by regime — grade B (industry-funded; ALWAYS disclose)

- **Bradshaw Advisory, "Ticket fraud: its impact and the cost of market
  regulation"** — commissioned by **StubHub International**. Verified exact
  figures: **UK 3.8%**, **Ireland 13.6%**, **Victoria 13.7%** of respondents
  reporting ticket fraud within the past two years.
  ⚠️ **Methodological caveats (disclose all three):**
  1. The report itself states causal inference is **"impossible"** without
     historical data — it does not claim the caps caused the fraud.
  2. **Different pollsters and different panels** were used for the Irish and
     Australian samples vs the UK — cross-jurisdiction comparability is weak.
  3. Commissioned by a party with a direct commercial interest in the outcome.
  **Model status:** cited as *motivation only, never as a fitted target.* The
  simulation's dark channel cannot reproduce these levels under either
  denominator (see `calibrate_tx_denominator.py`, 20–25× gap) — this is
  documented as a failed calibration, not papered over.
  https://bradshawadvisory.com/insights/ticket-fraud-its-impact-and-the-cost-of-market-regulationnbsp

## Comparator regimes — grade A (VERIFIED)

- **Ireland:** Sale of Tickets (Cultural, Entertainment, Recreational and
  Sporting Events) Act 2021, commenced **31 July 2021**; bans resale above
  original price. Penalties up to €100,000 / 2 years on indictment.
  **Zero prosecutions** as of May 2026 — independently corroborated (Dep. John
  Clendennen, Fine Gael, May 2026), not merely an industry claim.
  https://www.irishstatutebook.ie/eli/2021/act/21/enacted/en/html
- **Victoria, Australia:** Major Events Act 2009 — resale above **10%** over
  face value unlawful for declared events.
- **Ontario, Canada (LIVE NATURAL EXPERIMENT — NEW):** Bill 94, *Putting Fans
  First Act (No Ticket Resales Above Face Value), 2026*, passed via budget bill,
  Royal Assent **April 2026**, in force. Caps resale at face value **including
  fees**. Penalties to CA$50,000 individual / CA$250,000 corporate.
  Ticketmaster **delisted** Ontario resale inventory in response.
  **Observed displacement:** reporting documents sellers migrating to Facebook
  Marketplace using **$1 "ask-first" listings** with prices negotiated by DM to
  evade the cap (Global News, sellers switching after 31 July 2026 in-force
  date). ⚠️ Currently **anecdotal only — no quantitative volume/fraud data
  published.** This is the single best available real-world test of the
  displacement mechanism and is *currently unmeasured*.
  https://www.ola.org/en/legislative-business/bills/parliament-44/session-1/bill-94

## Market structure — grade A

- **CMA Viagogo/StubHub merger report + UK Gov analytical note:** top 10% of
  resellers >70% of volume; ~80% of uncapped platform volume professional;
  £404M resale on 1.5M tickets. Anchors scalper concentration.

## US legal and legislative developments — grade A (VERIFIED 2026-09-29)

- **United States v. Live Nation Entertainment (SDNY).** DOJ **settled
  mid-trial on 9 March 2026** (trial began 2 March). Settlement is
  **behavioural only — no divestiture**: multi-vendor ticketing at venues,
  outside promoters admitted to up to 50% of amphitheatre inventory, and
  certain fees capped at **15%**. There is **no financial component to the
  DOJ settlement itself**; the **$280M** figure is a settlement *fund* for
  plaintiff states' damages and civil-penalty claims, of which six "Settling
  States" took ~$18.6M.
  A coalition of states refused to settle and continued. On **15 April 2026**
  a **jury** returned a verdict for the states on all federal and state
  claims: unlawful monopolisation of primary ticketing and amphitheatres, and
  unlawful tying of amphitheatres to promotion services. The jury found an
  overcharge of **$1.72 per ticket** across 21 states and DC.
  ⚠️ **Three corrections to how this is commonly stated, including in our own
  earlier deck and in the Sept 2026 external audit:** (1) this is a **civil**
  case — the correct term is *found liable* / *found to have monopolised*,
  **not "guilty"**; (2) the April verdict was won by **the states**, not the
  DOJ, which had already withdrawn; (3) sources differ on the state count
  (33 states, or 36 states + DC) — prefer "a coalition of states" unless
  citing one source precisely.
  https://en.wikipedia.org/wiki/United_States_v._Live_Nation_Entertainment
  https://ag.ny.gov/press-release/2026/attorney-general-james-and-coalition-states-win-trial-against-live-nation-and

- **Washington DC — RESALE Act** ("Restricting Egregious Scalping Against
  Live Entertainment"). Passed **unanimously** by the DC Council on final
  reading **15 July 2026**; takes effect **1 January** subject to the 30-day
  congressional review period. Caps resale at **10% above face value** *plus*
  a **10% cap on fees** (so a consumer pays at most 120% of face, all-in).
  Also bans speculative ticket sales, requires registration for anyone
  advertising 50+ tickets a year, and prohibits surveillance pricing.
  **Why this matters to us:** it is the first US jurisdiction to legislate a
  **bounded non-zero ceiling**, and it uses the *same two-lever structure*
  (price ceiling + fee cap) as the UK draft Bill while setting the ceiling
  above zero. It corresponds closely to our modelled `Bounded 10% + fee cap`
  series. On PopWt GR that configuration beats the UK's `0% + fee cap`
  configuration at **8 of 9** oversubscribed demand levels (mean +0.044).
  https://dccouncil.gov/council-gives-final-approval-to-resale-act-regulating-ticket-sales-and-capping-ticket-resale-prices/

## Behavior — grade B (industry-derived; disclose)

- **Protect Ticket Rights / Automatiq** (July 2025): 62% of events resale below
  face; ~33% price decay to event day. Anchors demand-distribution portfolio
  and the 3-round markdown decay.
- **American Consumer Institute** (June 2025): 62% of events with below-face
  resale; **$414M** in consumer savings in 2024; average secondary price falls
  $29 between on-sale and the final month.
  ⚠️ **Not independent corroboration.** The ACI analysis is built on
  **186,113 transactions supplied by Automatiq** — the same resale-industry
  data provider behind the PTR figure above. A Sept 2026 external audit
  presented ACI as a separate source confirming the 62% number; it is the
  same dataset with a second analyst. ACI is a market-oriented think tank and
  the finding was republished by IPI. Cite as grade B with the data
  provenance stated, never as independent confirmation.

## Enforcement — grade B/C (advocacy source; verify before load-bearing use)

- **FEAT (Face-value European Alliance for Ticketing):** open letter **Jan 2026**
  signed by **130+** European live-industry figures (incl. Rammstein, management
  of Ed Sheeran and Radiohead, FC Barcelona, festivals) urging Brussels to
  address unauthorised resale via the **Digital Fairness Act**. Verified.
  The specific "275 DSA-flagged listings, zero takedowns" figure originates
  with FEAT advocacy materials — **treat as grade C until traced to a primary
  DSA enforcement record.**
  `SCALPER_DARK_COST = 0.45` assumes an enforcement regime that does not
  currently exist — stated as an assumption, and the enforcement sweep shows
  the bounded-cap result does **not** depend on it.

## Open global venues — see `reference_uk_2026_policy_verified` memory

- **EU Digital Fairness Act:** consultation closed 24 Oct 2025; legislative
  proposal expected **Q4 2026**. Ticket resale not yet in core scope — FEAT
  campaigning to add it. A live, addressable window.
- **US:** Executive Order on ticket resale (**31 Mar 2025**) directs FTC to
  enforce the BOTS Act, address deceptive secondary-market conduct, and
  *consider rulemaking* on price transparency; joint Treasury/AG/FTC report due
  27 Sep 2025. Active BOTS Act litigation (FTC v. Key Investment Group allowed
  to proceed, Apr 2026). **No open comment docket identified as of Aug 2026.**

## Do not cite

- "Leslie & Sorensen 75th-percentile threshold" — not a finding of the paper.
- Any figure traceable only to secondary AI-generated reporting.
- FEAT "275 listings / 0 takedowns" as grade A — it is advocacy-sourced.
