# Keep the Fee Cap. Fix the Ceiling.

**Simulation evidence on the draft Ticket Tout Ban Bill's resale price cap**
Patrick Tyler · independent researcher · [LinkedIn](https://www.linkedin.com/in/bytelawyer/) · July 2026

## Summary for policymakers

The Government's decision to cap resale platform service fees is good
policy — our modeling confirms it produces a real consumer welfare gain on
its own. But pairing it with a **face-value (0%) resale ceiling** forfeits
most of the available benefit. In an agent-based simulation of ticket
markets calibrated to UK and international evidence, a resale ceiling of
**10–20% above face value, combined with the same fee cap**, delivers
**two to three times the fan-welfare improvement** of the face-value
version of the policy — while avoiding the enforcement pathologies observed
in the two jurisdictions that have tried strict face-value regimes.

## The three findings that matter

**1. The fee cap and the price ceiling are separate levers, and the
ceiling is the stronger one.** Modeling the draft Bill's design (face-value
ceiling + capped fees) against alternatives across demand conditions from
undersubscribed to 10× oversubscribed: the fee cap alone improves
population-weighted fan welfare by roughly a third of what a 20% ceiling
adds under identical fee rules. The two measures reinforce each other —
but only if the ceiling is set above the level at which lawful resale is
economically viable.

**2. A face-value ceiling suppresses the lawful resale market the policy
depends on.** A fan reselling at face value recovers less than they paid
once any fee or friction applies. When lawful resale is loss-making,
supply routes around the regulated channel. This is not hypothetical:
Ireland (face-value cap, 2021) and Victoria, Australia (10% cap, 2009)
both report substantially higher ticket-fraud rates than the pre-ban UK
market (industry-commissioned data; enforcement capacity differs across
jurisdictions and the comparison should be read with that caveat — but the
directional mechanism is exactly what the simulation reproduces).

**3. Unlawful-channel leakage responds to the price gap, not the fee
rules.** In simulation, capping platform fees leaves off-platform routing
essentially unchanged, because the incentive to transact outside the
regulated channel is the gap between the ceiling and willingness-to-pay.
A modest positive ceiling narrows that gap; a fee cap does not.

## The recommendation

Retain every enforcement element of the current draft — capped platform
fees, the platform duty to monitor, the resale-quantity limit — and set
the resale ceiling in the **10–20% band above face value** rather than at
face value. This preserves the anti-touting intent (a 10–20% ceiling
eliminates the professional touting margin as effectively as 0% in our
runs, because tout economics require much larger markups), while keeping
fan-to-fan resale lawful, viable, and on regulated platforms where the
monitoring duty can actually operate.

## About the evidence

Agent-based simulation of primary + secondary + unlawful ticket channels:
four buyer/reseller types with empirically anchored behavior, platform
fees on both sides of resale transactions, enforcement frictions, and
professional-reseller entry/exit responding to expected margin. 16
rulesets × 10 demand levels × 100 seeded runs per point; results are
bit-for-bit reproducible from the published code and seed. Robustness:
all 33 model parameters perturbed jointly (Latin-hypercube, N=400); the
bounded-ceiling advantage over the status quo survives in 96–99% of
draws, and no single parameter can be tuned to reverse it. Full source
code, data, sensitivity analyses, and a documented limitations ledger
(including scope exclusions: presale allocations, multi-event dynamics)
are available for scrutiny.

*The author is a US-based independent researcher with no financial
interest in any primary or secondary ticketing business.*
