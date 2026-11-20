# Keep the Fee Cap. Fix the Ceiling.

**Why a face-value resale cap is the wrong ceiling, and what to set instead**
Patrick Tyler · independent researcher · [LinkedIn](https://www.linkedin.com/in/bytelawyer/) · August 2026, revised November 2026

## Summary for policymakers

The Government has got the hard half of this policy right and the easy half
wrong.

Capping platform service fees is good policy. In our model, the
Government's announced package, a face-value resale ceiling plus a cap on
platform fees, already leaves fans better off on average than today's
unregulated market at most levels of demand. But pairing the fee cap with a
**face-value resale ceiling** gives up a second, separate gain for fans.
Whether face-value ceilings can be enforced is also uncertain. Ireland
reports no prosecutions in five years, and early reports from Ontario
describe sellers moving to informal channels, but neither has yet been
measured.

Our recommendation is to set the ceiling in a fixed **20–30% band above the
original price instead of at zero, and keep every other element of the
Government's announced package.** In our simulation that leaves fans better
off on average than the same package with a face-value ceiling. It does so at
both ends of the band, at every level of demand we tested, and under each of
the three ways we scored the cost of high prices. Under our baseline
assumptions it also holds professional resellers to modest model-implied
returns on their stock (before bot, labour and holding costs, which the
model omits). Those returns are roughly 16–25% against 85% to over 100% in
the model's uncapped market at heavily oversubscribed events, with about 95%
of their resale stock staying on lawful platforms. Touting is governed, not
destroyed.

The band is a policy judgement, not a proof:

- **It is not role-proof against face value.** It accepts a small loss for
  the most committed fans at moderately oversubscribed events in exchange
  for larger average gains for fans.
- **Its upper end depends on assumptions.** It rests on a limit on reseller
  returns that we chose, on the fee cap the Government has yet to set, and
  on uncalibrated off-platform costs.

These are results from a simulation, with its assumptions stated below.
They show mechanisms and directions, not precise magnitudes.

## Why resale reform is hard to hold together

Our starting hypothesis is that ticket resale reform has an unusual
political property: **its coalition changes shape at the moment it
succeeds.**

Before tickets go on sale, most fans want broadly the same thing: a fair
chance at a ticket at a fair price. Once tickets are allocated, that public
splits. Fans who got tickets now hold something of value, and their interest
shifts toward the freedom to pass it on if their plans change. Fans who
missed out want access, and a route to it. Reform is designed for people
standing in the queue, then enforced on a population where many have
already sat down.

That is why we model fans as distinct groups with interests that can
diverge. These are committed fans who will pay several times face value,
regular attendees, and occasional buyers. Treating fans as one group who
simply want cheap tickets points toward the cheapest possible ceiling.
Treating them as groups shows what that ceiling costs: the lawful route by
which tickets reach fans who missed the on-sale.

## Touts are better governed than banned

The instinct behind a face-value cap is that touts are parasites and the
right number of them is zero. The evidence is more mixed than that.

Peer-reviewed work on this market (Leslie and Sorensen, *Review of Economic
Studies*, 2014) finds that resale improves allocation by around 5%: tickets
move from people who value them less to people who value them more. Roughly
a third of that gain is offset by **rent-seeking and the transaction costs
of resale**: brokers spending real resources to reach inventory first, and
the costs of reselling itself. Resale is neither costless nor worthless.
That is an argument for *bounding* the resale margin, not for abolishing it.

A ceiling that is too tight may not stop resale; it may move it.

- **Ontario** now caps resale at the total price paid to the primary seller,
  plus the fees, service charges and taxes applicable to the resale, in force
  from 24 April 2026. Its law also requires that total price to be printed on
  the ticket and proven to resale platforms. A major platform delisted its
  Ontario resale inventory.
  Contemporaneous reporting described sellers moving to general classified
  sites, listing at a nominal one dollar and negotiating the real price
  privately. That evidence is anecdotal. No one has yet measured how much
  resale moved, or what happened to fraud.
- **Ireland's** face-value cap has been law since July 2021, and has
  produced no prosecutions in five years, a point raised in the Oireachtas in
  May 2026. A prosecution count alone cannot show whether the rule is being
  complied with, is poorly enforced, or is displacing trade.
- **Survey evidence from Ireland and Victoria** reports higher ticket-fraud
  rates than the pre-ban UK market. We treat it cautiously. It was
  commissioned by a secondary-market operator, its authors state that causal
  inference is not possible from the data, and different panels were used in
  each country. We cite it as consistent with displacement, not as proof of
  it.

## What we did

We built an agent-based simulation of the primary sale, the lawful resale
market, and the unlawful off-platform channel:

- **Three groups of fans** with different willingness to pay, attendance
  and resale behaviour.
- **Professional resellers who adapt like predators.** They enter and leave
  the market depending on whether the margin is worth their costs. They
  compete harder for primary inventory when resale pays more. They mark down
  unsold stock, and they move tickets off-platform when that pays better than
  the lawful channel.
- **Platform fees, fraud risk and enforcement costs** off-platform.

The model's off-platform market clears at negotiated prices between what the
reseller needs and what the buyer can pay.

**The test.** We asked whether a rule is **role-proof** against the
alternative on the table. Role-proof means:

1. no group of fans is detectably worse off on average under it (no
   statistically significant loss in the group's average), judged before
   tickets are allocated, and again after, when fans know whether they hold
   a ticket;
2. it governs professional resellers fairly, neither destroying their
   lawful business nor driving it underground. We define fair governance as
   returns of 0–30% on their stock at heavily oversubscribed events, with at
   least 80% of it sold on lawful platforms.

This is an operational test, not proof that every individual would accept
the rule. It detects losses in group averages; it cannot show that no fan
loses. The 30% limit on reseller returns is our normative choice.

The closest established concept we know of is role-reversal consistency, an
experimental test of the Golden Rule (Costa-Gomes, Ju and Li, 2019). Our
contribution is to apply acceptability from every position, before and after
allocation, to the design of a market rule.

**How the final results were produced.** An independent adversarial review of an
earlier version, run with a separate AI model, found four mechanical errors
in the simulation, which we fixed. We
then fixed the experiment, the criteria for each conclusion, and what this
brief would recommend under each possible outcome, in a dated internal
protocol, *before* running it once. The protocol was not registered with an
outside body. The design compares fixed ceilings of 0%, 10%, 20%, 30% and 40%, each
with a 5%-per-side fee cap, against each other and against an uncapped market like today's.
It runs at nine levels of demand, from one-and-a-half to ten times
oversubscribed, with 300 paired runs per level.

## What the evidence says

**Every positive ceiling we tested leaves fans better off than face value.**
Ceilings of 10%, 20%, 30% and 40% each beat face value for fans on average
at every level of demand. That holds under each of three ways of counting the
harm of a high price, and whether or not fans who cannot use a ticket are
reluctant to resell it at a loss. On our index (a constructed score, not
money), fans' average outcome is roughly 4–11% higher at a 20% ceiling and
7–24% higher at 30%, depending on demand and listing behaviour. The gain comes through access:

| At five times oversubscribed | Face value | 20% ceiling | 30% ceiling |
| --- | --- | --- | --- |
| Occasional and regular fans' chance of a ticket | 4% | 7% | 8% |
| Lawful resales per 500-seat event | 86 | 135 | 156 |

**Under our baseline assumptions, professional resellers are governed, not
destroyed, up to 30%.** In the model's uncapped market, resellers' returns on
their stock are about 85% at four times oversubscribed and 100% or more
beyond that. The measure tops out there, and it is before the bot, labour
and holding costs the model omits. With the fee cap:

- **20% ceiling:** returns hold at about 16–17%.
- **30% ceiling:** about 25%.
- **Off-platform share:** 4–6% of their resale stock goes off-platform,
  against 9–10% under face value.
- **40% ceiling:** returns rise to about 34%, above the 30% limit we chose.
  **That limit, not fan welfare, is what sets the top of the band.** Fans'
  average outcome keeps rising to 40%.

**That upper end is sensitive to assumptions.** The second independent review re-ran
the model under alternatives, with 45 paired runs per point. Under every one,
the 20% and 30% ceilings still left fans better off than face value.
Resellers' returns, at five times oversubscribed, moved as follows:

| Assumption | 20% ceiling | 30% ceiling | 40% ceiling |
| --- | --- | --- | --- |
| Our baseline (45% of off-platform revenue lost to enforcement; 5% fees per side) | 16% | 25% | 34% |
| Cheaper off-platform trading (20% lost) | 24% | 31% | 39% |
| Resellers take 75% of each off-platform bargain | 20% | 28% | 36% |
| More tickets routed off-platform | 20% | 27% | 34% |
| Fee cap of 2% per side | 19% | 28% | 38% |
| Fee cap of 10% per side | 11% | 19% | 27% |

So the 30% ceiling meets our limit only under some of these assumptions,
and with a 10% fee cap even 40% would. The band's upper end is therefore a
normative choice that depends on the fee level the Government sets and on
how costly off-platform trading really is. A 20% ceiling stays within the
limit in every case tested.

**Within the band the choice is a real trade-off.** We would rather name it
than hide it.

- **30%** does more for fans on average at every level of demand.
- **20%** holds resellers to lower returns.

**The band is not role-proof against face value, and we say so plainly.** At
20–30%, the most committed fans, those willing to pay several times face
value, do slightly worse than under face value at moderately oversubscribed
events (around three to four times demand). That holds both as a group and
among those who miss the on-sale.

- **10% is the only ceiling for which no group-average loss relative to
  face value was detected,** under our baseline assumptions. With frictionless
  listing, small losses appeared there too.
- **The trade-off for legislators** is between a ceiling with no detected
  group-average loss (about 10%) and larger average gains for fans with
  resellers still fairly governed under baseline assumptions (20–30%). Our
  recommendation takes the second, and in doing so gives up the role-proof
  condition.

**The condition.** The band's advantage is not robust in one combination of
assumptions: that fans who cannot use a ticket list it at face value just as
readily as they would at a higher ceiling, *and* that fans place no value at
all on being able to resell. Under that combination, on one way of scoring
price, the gain stays positive at moderate demand but shrinks to roughly
nothing at high demand. On another, it reverses from about two times
oversubscribed. We consider that combination unlikely, but it is the
condition under which this recommendation no longer holds across all levels
of demand.

**Displacement can be modelled, not just assumed.** The analytical note
accompanying the consultation response assumes a **20% displacement
effect**: touts continuing to sell above the cap outside regulated platforms.
It states that this assumption "lacks strong evidence." The £112 million
annual saving is calculated carefully on the price side; the behavioural
response that decides whether it materialises is assumed. Our model makes
that response explicit. In it, a positive ceiling keeps more professional
resale on lawful platforms than face value does. Those figures depend on our
assumed enforcement costs, which are not calibrated.

## The recommendation

Keep every enforcement element of the Government's announced proposals: the
platform fee cap, the platform duty to monitor, the resale quantity limit,
and the CMA's new powers. (The draft Bill had not been published when this
brief was revised; the Government has said it will publish one this
session.) Change one thing: set the resale ceiling in a **fixed 20–30% band
above the original price**, instead of at face value.

This is not an exotic request. The *Putting Fans First* consultation put four
capped options to respondents: no uplift, 10% or less, 10–20%, and 20–30%. It
stated that the Government had "no favoured approach at this stage." The
evidence here supports the top of the range the Government itself consulted
on, rather than its strictest end.

It is also no longer hypothetical. The District of Columbia's RESALE law
(D.C. Law 26-181, in effect from 25 September 2026 and applying from
1 January 2027) has two parts:

- **The ceiling:** resale is capped at the total original price, including
  fees and taxes, plus up to 10%.
- **The fee cap:** the resale marketplace's own fee is capped at 10% of that
  total.

It is the same two-lever design as the Government's proposals, with the
ceiling above zero. DC chose the low end of the range. In our model, under
baseline assumptions, that is the ceiling with no detected group-average loss
for any fan group. We recommend accepting the trade-off described above in
exchange for larger gains for fans. Our model does not reproduce DC's
exact price base or fee structure.

**A fixed band, for a reason.** We recommend a fixed ceiling rather than one
that rises with demand. A ceiling indexed to scarcity would reproduce the
market it replaces, with prices climbing steeply as demand climbs. It would
also be harder for buyers to understand and for regulators to audit. A fixed
band costs little: in our primary scenarios the ranking of ceilings does not
change with demand. (In the adverse combination described above, it can.)

**Two qualifications.**

- **This is a controlled comparison of ceiling levels,** not a head-to-head
  of legislative packages. Several provisions on each side are outside the
  model: DC's speculative-sale ban and reseller registration, and the
  proposed monitoring duty and CMA powers.
- **The band assumes a fee cap of the order we modelled,** 5% per side. That
  is our assumption, not a figure the Government has set. As the table above
  shows, the fee level moves the band's upper end. With higher platform fees,
  a fan reselling at a given ceiling recovers less, and the ceiling needs
  more headroom.

A ceiling in this band:

- keeps fan-to-fan resale lawful and worthwhile;
- keeps it on platforms where the new monitoring duty can operate;
- holds professional resellers to a modest, governed margin under our
  baseline assumptions.

## About the evidence

**The final runs.** The simulation covers six rules (an uncapped market like today's, and five
fixed ceilings) at nine demand levels,
with 300 paired runs per level, in a 500-seat venue. Each run models the
primary sale, three rounds of lawful resale, and the off-platform channel.
The final experiment, its pass criteria, and the brief's decision rules were
fixed in a dated internal protocol before it was run
(`V2_PREREGISTRATION.md`). The code and every run's results are published.
The previous version of the model still reproduces exactly from the same
code. A second independent review, also run with a separate AI model,
regenerated a sample of runs and the results
exactly from the published code and data, and ran the stress tests reported
above.

**Corrections.** This brief corrects earlier versions. An internal check
found an error in how fan welfare was scored. The first independent review found four
mechanical errors:

- off-platform tickets priced beyond any buyer;
- inconsistent fee accounting;
- buyer fees ignored when matching buyers to tickets;
- a price floor on fans' resale.

Claims that rested on those errors have been withdrawn. They include an
earlier statement that the ceiling's gain was 2.13 times the fee cap's, and
that touting becomes loss-making at extreme demand. A correction log is
published with the code.

**Six limitations deserve stating here rather than in an appendix.**

1. **This is a simulation calibrated to published evidence, not a field
   experiment,** at the scale of a single 500-seat event. It establishes
   mechanisms and directions, not precise magnitudes, and cannot pin the
   best ceiling down to within a few percentage points.
2. **Several behaviours are stylised rather than calibrated.** These include
   how readily fans list tickets they cannot use, how resellers mark down
   unsold stock, and the costs of trading off-platform. The reseller
   markdown rule affects our comparison with the uncapped market at moderate
   demand, not the comparison between ceilings.
3. **Fans' welfare is a constructed index.** How much a high price harms a
   fan is a value judgement. We report three versions, and our conclusions
   hold under each. Our role-proofness test uses group averages: individuals
   within a group may disagree.
4. **The model assumes any ceiling is enforced on lawful platforms against a
   known original price,** a price of record tied to each ticket. That
   applies equally to face value and to the band, so it does not tilt the
   comparison between them. But it flatters every capped rule against
   the uncapped market, and it means a ceiling at any level depends on someone
   keeping that record. Ontario's new law shows one way to do it: the total
   price must be printed on the ticket and proven to resale platforms.
5. **The fee cap's level is our assumption,** and the band's upper end
   depends on it.
6. **Fans who resell a ticket are still credited with having obtained one,**
   as is their buyer. In a check by the second review, scoring only final
   holders narrowed the band's advantage but did not reverse it.

## Sources

1. *Putting fans first: consultation on the resale of live events tickets*,
   10 January – 4 April 2025. Maximum-uplift options put to respondents: no
   uplift, 10% or less, 10–20%, 20–30%, other. Government response,
   19 November 2025.
2. *Analytical note on the government response to the resale of live events
   tickets consultation*, GOV.UK. £112m estimated annual reduction in fan
   spend; 20% displacement assumption stated to lack strong evidence.
3. P. Leslie and A. Sorensen, "Resale and Rent-Seeking: An Application to
   Ticket Markets," *Review of Economic Studies* 81(1) (2014), 266–300,
   doi:10.1093/restud/rdt033. The roughly one-third offset combines
   rent-seeking and resale transaction costs.
4. U.S. Government Accountability Office, *Event Ticket Sales: Market
   Characteristics and Consumer Protection Issues*, GAO-18-347 (2018).
   Primary-market fees averaging 27% and secondary-market fees 31% of ticket
   price, in a sample GAO describes as nongeneralizable.
5. Sale of Tickets (Cultural, Entertainment, Recreational and Sporting
   Events) Act 2021 (Ireland), commenced 31 July 2021. Absence of
   prosecutions raised in the Oireachtas, May 2026.
6. Major Events Act 2009 (Victoria, Australia): 10% resale ceiling for
   declared events.
7. *Plan to Protect Ontario Act (Budget Measures), 2026* (Bill 97),
   S.O. 2026, c. 2, Schedule 16, amending the Ticket Sales Act, 2017.
   - **The cap (s. 2(3)):** resale may not exceed the total price paid to the
     primary seller, plus applicable fees, service charges and taxes charged
     by the secondary seller or platform.
   - **The price of record (s. 6):** the total price must be printed on the
     ticket and proven to platforms.
   - Royal Assent and in force 24 April 2026.
   - Also: Government of Ontario, "Buying tickets for events in Ontario";
     *Pollstar*, 27 April 2026; contemporaneous reporting on seller migration
     to unregulated listing channels (anecdotal).
8. Bradshaw Advisory, *Ticket fraud: its impact and the cost of market
   regulation* (2025), commissioned by StubHub International. Self-reported
   two-year fraud incidence of 3.8% (UK), 13.6% (Ireland), 13.7% (Victoria).
   Cited with the limitations noted in the text.
9. House of Commons Library, *Ticket resales*, briefing SN04715.
10. D.C. Law 26-181, *Restricting Egregious Scalping Against Live
    Entertainment (RESALE) Amendment Act of 2026* (Bill 26-224; second
    reading 14 July 2026; effective 25 September 2026; applies from
    1 January 2027). Resale capped at the total initial price including fees
    and taxes plus up to 10%; marketplace service fee capped at 10% of the
    total initial price; Mayor may adjust within set limits from 2028.
11. M. A. Costa-Gomes, Y. Ju and J. Li, "Role-Reversal Consistency: An
    Experimental Study of the Golden Rule," *Economic Inquiry* 57(1) (2019),
    685–704, doi:10.1111/ecin.12708.
12. UK Parliament, written answer UIN 28945 (18 September 2026): the
    Government "will publish the draft bill in this session of parliament for
    pre-legislative scrutiny"; House of Commons, Sporting Events Bill [Lords]
    debate, 4 November 2026 (the ticket touting Bill still to come forward).

*The author is a US-based independent researcher with no financial interest
in any primary or secondary ticketing business, and no relationship with
any party cited above.*

*The code and analysis were developed with AI assistance (Anthropic's
Claude), and both adversarial reviews were run independently using a separate
AI model. All design choices, definitions and claims are the author's.*
