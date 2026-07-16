# Golden Rule Equilibrium (GRE) — Ticket Market Simulation

Agent-based simulation of ticket-resale policy. Core question: what resale
price cap (if any) maximizes fan welfare once scalpers, dark markets,
platform fees, and enforcement are modeled honestly? The GRE framing scores
rulesets by a "would you accept these rules not knowing your position?"
composite (floor / equality / average weighted), alongside standard welfare
criteria (Rawlsian maximin, Harsanyi utilitarian, Pareto screening).

**Headline finding to date:** a bounded resale cap beats Status Quo,
Dynamic Pricing, and UK-style face-value-only resale on the
population-weighted and system welfare lenses across demand levels. The
optimal cap is demand-dependent within a **10–30% band** (a fixed 20% cap
is never far from the per-demand optimum once markets are oversubscribed);
under a UK-2026-style capped-fee regime the defensible band is **10–20%**.
The band falls out of the secondary-platform fee structure (seller-side
fee makes sub-~17.6% caps loss-making for legal resale) rather than being
tuned to a target. The fan-price lens alone prefers the tightest cap —
an accepted divergence (buyers prefer cheaper); the policy case rests on
system function, not on out-cheapening face value.
See `gre_sim.py`'s embedded changelog for the full audit history (A1–A6,
B1, C1–C2, E1 fixes).

## Running

```bash
# IMPORTANT: use /usr/local/bin/python3 (see requirements.txt note —
# plain python3 resolves to a Homebrew build without numpy/matplotlib).

/usr/local/bin/python3 cap_sweep.py            # main cap × demand sweep -> 2 CSVs
/usr/local/bin/python3 rawls_analysis.py       # welfare criteria (reads cap-sweep CSVs)
/usr/local/bin/python3 generate_charts.py      # charts 1-5 (reads cap-sweep CSVs)
/usr/local/bin/python3 sensitivity_sweep.py    # OAT sensitivity -> rankings CSV
/usr/local/bin/python3 global_sensitivity.py   # LHS + PRCC global sensitivity
/usr/local/bin/python3 enforcement_sweep.py    # enforcement-regime comparison
/usr/local/bin/python3 weight_discovery.py     # co-evolutionary agent tournament
/usr/local/bin/python3 test_invariants.py      # invariant test suite (run before trusting any sweep)
node generate_deck.js                          # pitch deck (pptxgenjs)
```

Run order matters: `rawls_analysis.py` and `generate_charts.py` read the
CSVs written by `cap_sweep.py`. All sweeps are seeded (`random.seed(42)`)
and bit-for-bit reproducible; see the C1 notes in the source.

## File map

- `gre_sim.py` — canonical simulation core (single source of truth; all
  model changes happen here; runners import `simulate()`/`Rule`)
- `cap_sweep.py` — primary experiment: 13 rulesets × 10 demand levels × 100 runs
- `sensitivity_sweep.py` / `global_sensitivity.py` — OAT and LHS+PRCC
  robustness (PARAM_SPECS in the former is imported by the latter)
- `enforcement_sweep.py`, `rawls_analysis.py`, `weight_discovery.py`,
  `calibrate_systemic.py`, `calibrate_tw.py` — secondary analyses
- `generate_charts.py`, `generate_deck.js`, `add_limitations_slide.py` —
  presentation pipeline
- `test_invariants.py` — conservation/bounds/determinism/regression tests
- CSVs and `chart*.png` at root — current results of record (regenerate via
  the commands above)
- **Deprecated:** `cap-sweep.js`, `gre-scarcity-curves.jsx` — pre-2026-04-21
  JS implementations, unsynced since the Python consolidation; kept for
  provenance only

## Open items / decision log

1. **Systemic dark-market externality: DISABLED in baseline**
   (`SYSTEMIC_FRAUD_WEIGHT = 0.0`). Calibration against the Ireland (13.6%) /
   Victoria (13.7%) / UK (3.8%) fraud anchors failed on a units mismatch
   (fraud-per-secondary-transaction vs dark-tickets-per-seat). The headline
   results no longer depend on it; the fee mechanism carries the economic
   argument instead. Re-enabling requires redefining `dark_prevalence` with
   the transaction denominator and recalibrating — decision owner: Patrick.
   Full status note at the `DARK_SYSTEMIC_K` block in `gre_sim.py`.
2. Placeholder parameters flagged in-source (`DARK_LEAKAGE_*`,
   `SCALPER_DARK_COST`) are directionally consistent with the
   Ireland/Victoria/UK contrasts but need primary sources before
   publication use.
3. Chart/deck palette and series lists are defined in `sweep_config.py`
   (shared by cap_sweep, rawls_analysis, generate_charts); `generate_deck.js`
   still duplicates the palette in JS.
