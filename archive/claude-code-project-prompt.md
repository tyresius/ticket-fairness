# Golden Rule Equilibrium — Claude Code Project Setup

## Project Prompt

You are helping me build and iterate on the Golden Rule Equilibrium (GRE) ticket fairness simulation. This is a game-theoretic model that evaluates different ticket market rulesets (Status Quo, Bounded Market, UK Face Value, Dynamic Pricing) across varying demand/scarcity levels using multi-agent simulation.

### Project Context

The Golden Rule Equilibrium asks: would each participant accept the system rules regardless of which role they occupied? It's a position-invariant fairness metric that must survive the endowment effect (preferences shifting post-purchase).

The simulation models four agent types competing for 500 venue seats at $100 face value:
- **Mega Fan** (80 base pop): Fast buyer (0.85 speed), will pay up to 2.5x face, 95% attendance, rarely resells
- **Committed Casual** (150 base pop): Slower buyer (0.35), pays up to 1.8x, 78% attendance, resells when plans change (20% rate)
- **Average Buyer** (200 base pop): Slowest (0.3), pays up to 1.4x, 55% attendance, most likely non-scalper to flip (20%), highest plan change rate (25%)
- **Scalper** (30 base pop, scales at 0.3x demand multiplier): Fastest (0.95, bots), pays up to 3x, never attends, always resells. Functions like wolves in an ecosystem — serves liquidity/urgency function but extractive if unchecked

Four rulesets compared:
- **Status Quo**: No resale cap, 8-ticket purchase limit, no identity checks
- **Bounded Market**: Resale cap at face + X% (currently 20%), 4-ticket limit, identity registry
- **UK Face Value**: 0% resale cap, 2-ticket limit, identity registry
- **Dynamic Pricing**: 2.2x initial price, 6-ticket limit, no resale cap

The simulation runs four temporal phases:
1. **Primary Sale**: Probabilistic queue based on speed + jitter, tickets sell until gone
2. **Life Happens**: Plan changes, endowment effect, flip temptation, ticket wastage (zero-cap systems see more wastage because resale isn't worth the effort)
3. **Secondary Market**: 3 rounds with scalper repricing (100% → 70% → 50% of ask, floored near cost). All missed buyers attempt each round. Cap enforced as ceiling, not floor.
4. **Showtime**: Unsold tickets = total loss for scalpers

Utility scoring:
- **Scalpers**: ROI-based (breakeven = 0.3, 50% ROI = 0.6, 100% = 0.85)
- **Everyone else**: Access rate (35%) + Price score (30%, steeper penalty for dynamic pricing surcharges) + Attendance rate (20%) + Resale option value (15%, scaled by access rate)
- **Zero-ticket agents**: Utility floors at 0.02

Golden Rule composite: Floor (worst-off) × 0.4 + Equality (1 - spread) × 0.3 + Average × 0.2 + 0.5 baseline × 0.1
Three lenses: Fan Fairness (excl. scalpers), Population Weighted (by headcount), System (equal weight)

### Immediate Task: Cap Optimization Sweep

Run the bounded market simulation across cap levels [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50] at demand levels [1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10], averaging 30 runs per point. Output a table showing:
- Golden Rule scores (all three lenses) for each cap level at each demand level
- Per-agent utility for each cap level at each demand level
- Attendance and wastage
- Identify the optimal cap level at each demand level and overall

The goal is to find whether 20% is actually optimal or whether a different cap level produces better fairness outcomes, and whether the optimal cap varies with scarcity.

### Future Tasks (after cap sweep)
- Emergent weight discovery: Let agent behavioral weights emerge through iterated simulation rather than hand-tuning
- Sensitivity analysis: Which parameters most affect the Golden Rule score
- Stress testing: "Scalper DDoS" scenario where constrained agents collectively attack the mechanism
- Cap-to-demand linking: If optimal cap varies with scarcity, explore whether the cap could be dynamically tied to demand signals

### Key Files
- `gre-scarcity-curves.jsx` — The full simulation with React UI (simulation logic is in the `simulate()` function, pure JS, no React dependencies needed for the sweep)
- `golden-rule-equilibrium-roadmap-v4.docx` — Complete project roadmap with theoretical framework, agent architecture, landscape analysis (UK legislation, DOJ settlement), and all simulation findings to date

### Important Design Principles
- Agents interact through the market mechanism, not with each other directly (intermediated, asynchronous — like real ticket markets)
- Scalpers are ecological actors (wolves), not villains — manage them, don't eliminate them
- The bounded market's value proposition is robustness across scarcity levels, not optimality at any single point
- No agent is demonized; all have legitimate (if sometimes extractive) motivations
- The endowment effect is the central insight: preferences shift post-purchase, making reform coalitions unstable
