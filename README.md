# Role-proof ticket resale

**An agent-based model of ticket-resale price ceilings, and a test of whether a rule stays acceptable after people's positions change.**

Governments are capping ticket resale. The UK's announced plan is a face-value ceiling plus a cap on platform fees. Ontario capped resale at the original price in April 2026; Washington, D.C. allows up to 10% above it from January 2027. This project asks what level of ceiling actually serves fans, once you model:

- **who the fans are**, since they are not one group with one interest;
- **how professional resellers adapt**, including moving trade off-platform;
- **how preferences change** once some fans hold tickets and others don't.

**Read the policy brief: [`POLICY_BRIEF.md`](POLICY_BRIEF.md).** It recommends keeping the fee cap but setting a fixed resale ceiling of 20–30% above the original price, not face value. That recommendation is a conditional, simulation-based policy argument, with the conditions stated.

## What the model does

- **Three groups of fans:** committed fans who will pay several times face value, regular attendees, and occasional buyers. They differ in willingness to pay, attendance, and how they behave when their plans change.
- **Professional resellers modelled as adaptive predators ("wolves").** They enter and leave the market on expected margin, compete for primary inventory, mark down unsold stock, and route tickets to an off-platform market when it pays. That market clears at negotiated prices.
- **Platform fees, fraud risk and enforcement costs.** The model assumes caps are enforced on-platform against a known original price, a "price of record" for each ticket. It states this as an assumption.
- **Every fan scored individually,** before and after the primary sale, under three different judgements of how much a high price harms a fan.

## Role-proofness

A rule is **role-proof** against an alternative if:

1. **no group of fans is detectably worse off on average,** judged both before allocation and after it, when fans know whether they hold a ticket;
2. **professional resellers are fairly governed:** their business is neither destroyed nor driven off-platform (defined here as returns of 0–30% with at least 80% of stock sold lawfully).

The closest established concept is role-reversal consistency (Costa-Gomes, Ju and Li, *Economic Inquiry*, 2019). This project applies the idea to the design of a market rule.

## Main results

These are from the final experiment (`V2_PREREGISTRATION.md`, results in `v2_verdicts.txt`): fixed ceilings of 0–40% with a 5%-per-side fee cap, 9 demand levels, and 300 paired runs per level.

| Question | Result |
| --- | --- |
| Do positive ceilings beat face value for fans? | **Yes.** 10%, 20%, 30% and 40% each beat face value at every demand level, under both fan-listing assumptions and all three price scorings. |
| How large is the gain? | About 4–11% (20%) and 7–24% (30%) on the fans' welfare index. At 5× demand, occasional fans' chance of a ticket rises from 4% to 7–8%. |
| What happens to resellers? | Model-implied returns are about 16–17% at a 20% ceiling and 25% at 30%, against 85–100%+ in the uncapped model. At 40% they reach 34%, above the fair-governance limit. **That limit, not fan welfare, sets the top of the band.** |
| Is the band role-proof against face value? | **No.** The most committed fans do slightly worse at moderate demand. Only a 10% ceiling showed no detected group-average loss, and only under baseline assumptions. |
| Where does it fail? | Only if fans list unwanted tickets at face value as readily as at higher ceilings *and* place no value on being able to resell. The upper end of the band also moves with the fee level and with off-platform costs; see the brief's stress-test table. |

## How the results were checked

The project's main contribution may be its correction trail as much as its answer.

1. **The claims were audited, and a role-proof test was added** (`CLAIMS_REGISTER.md`, `ROLE_PROOF_TEST.md`). The test failed the original 10–20% claim, and the diagnosis found a scoring error.
2. **Every welfare claim was re-checked** against criteria written in advance (`RESCORE_CHECK.md`, `PRICE_SCORE_CHECK.md`, `LISTING_CHECK.md`).
3. **First independent adversarial review** (`audit results/roleproof_audit_report_2026-11-12.md`). It found four mechanical errors, including off-platform tickets priced beyond every buyer's limit.
4. **Model v2 fixed them** (the earlier version still reproduces exactly). **One final experiment** was run under a dated internal protocol that fixed its criteria and decision rules beforehand (`V2_PREREGISTRATION.md`).
5. **Second independent review** (`audit results/roleproof_v2_audit_report_2026-11-17.md`). It regenerated runs and results exactly, stress-tested the assumptions, and called for wording fixes, which were made.

Withdrawn claims and corrected facts are listed in [`CORRECTION_LOG.md`](CORRECTION_LOG.md).

## Repository guide

| Path | What it is |
| --- | --- |
| `POLICY_BRIEF.md` | The policy brief (final) |
| `V2_PREREGISTRATION.md`, `v2_verdicts.txt` | Final experiment: protocol, criteria, decision rules, results |
| `CORRECTION_LOG.md`, `CLAIMS_REGISTER.md` | What changed and why |
| `audit results/` | Both independent review reports and the reviewer's reproduction files |
| `gre_sim.py` | The simulation. `mechanics="v2"` is the final model; the default `"v1"` reproduces earlier results. |
| `role_proof.py` | Individual fan scoring and the role-proof test |
| `v2_experiment.py`, `v2_verdicts.py`, `v2-runs-*.csv.gz` | Final experiment code and one row per simulated run (62,100 runs) |
| `test_*.py` | 20 tests, including one per v2 fix |
| `*_CHECK.md`, `ROLE_PROOF_TEST.md`, the other scripts, CSVs and logs | The earlier checks, kept for the record |
| `SOURCES.md` | Graded source ledger for every external fact |
| `archive/` | Superseded material (old deck, v1 charts, prototypes). Not current. |

## Reproduce

Requires Python 3.12+. The simulation uses the standard library only; `numpy` is needed only for the older robustness scripts.

```bash
python3 -m unittest test_invariants test_role_proof test_v2   # 20 tests
python3 v2_verdicts.py                                         # all verdicts from the stored runs (seconds)
for i in 0 1 2 3 4 5 6 7 8; do python3 v2_experiment.py --levels $i & done; wait   # re-run the final experiment (~5 min on 10 cores)
python3 cap_sweep.py                                           # v1 sweep; reproduces cap-sweep-*.csv byte for byte
```

## Limitations

- **It is a simulation, not a field study.** A single 500-seat event, calibrated to published evidence. It shows mechanisms and directions, not precise magnitudes.
- **Several behaviours are stylised rather than calibrated:** fan listing behaviour, reseller markdowns, and off-platform costs and bargaining.
- **The 5%-per-side fee cap is an assumption,** and the band's upper end depends on it.
- **The fans' welfare index is constructed,** and the role-proof test uses group averages, not individual preferences.

The brief states all of these in full.

## Author

Patrick Tyler, independent researcher. The code and analysis were developed with AI assistance (Anthropic's Claude), and both adversarial reviews were run independently using a separate AI model. All design choices, definitions and claims are the author's.
