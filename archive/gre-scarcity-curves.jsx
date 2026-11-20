// ─────────────────────────────────────────────────────────────────────────────
// DEPRECATED as of 2026-04-21.
//
// The simulation logic in this file is NO LONGER the source of truth and is
// not kept in sync with the Python stack. The canonical simulation lives in
// `gre_sim.py`, driven by `cap_sweep.py` (batch sweep) and `weight_discovery.py`
// (co-evolutionary tuning). This JSX retains a stale copy of simulate() that
// predates:
//   - the dark market affordability fix
//   - the UK Face Value / Bounded 0% cap series
//   - the sub-5% scalper RNG bug (two-independent-draws form — never fixed here)
//
// If you need an interactive visualizer, build a Python one against the CSVs
// emitted by cap_sweep.py (cap-sweep-summary.csv, cap-sweep-agents.csv) rather
// than reviving this file.
// ─────────────────────────────────────────────────────────────────────────────
import { useState, useCallback, useRef } from "react";

const VENUE = 500;
const FACE = 100;
const BASE_POP = { mega_fan: 80, committed_casual: 150, average_buyer: 200, scalper: 30 };

const DEFS = {
  // flipMarginThreshold: minimum expected achievable margin before an agent will opportunistically
  // flip extra tickets. Distinct from resaleEffortThreshold (which governs necessity resale when
  // plans change). Higher threshold = less willing to speculate. Calibrated as starting points
  // for eventual agent-specific simulation tuning.
  // Empirically calibrated from NITO/CMA/Stanford research:
  // - mega_fan WTP raised to 4x (superfan empirical 4-6x; abandonment spikes above 6x)
  // - flipMarginThreshold raised across all fan types (endowment buffer ~40%; 2.5x step-function)
  // - resaleEffortThreshold raised (fans prefer giving to friend vs listing below 30-40% premium)
  // - planChangeRate reduced to align with 8% empirical no-show baseline
  mega_fan:         { speed: 0.85, maxPayMul: 4.0, attendBase: 0.95, wanted: 2, flipChance: 0.02, planChangeRate: 0.08, resaleEffortThreshold: 0.0,  flipMarginThreshold: 0.75 },
  committed_casual: { speed: 0.35, maxPayMul: 1.8, attendBase: 0.78, wanted: 2, flipChance: 0.08, planChangeRate: 0.10, resaleEffortThreshold: 0.30, flipMarginThreshold: 0.40 },
  average_buyer:    { speed: 0.3,  maxPayMul: 1.6, attendBase: 0.55, wanted: 3, flipChance: 0.2,  planChangeRate: 0.12, resaleEffortThreshold: 0.25, flipMarginThreshold: 0.35 },
  scalper:          { speed: 0.95, maxPayMul: 3.0, attendBase: 0.01, wanted: 8, flipChance: 1.0,  planChangeRate: 0.0,  resaleEffortThreshold: 0.0,  flipMarginThreshold: 0.0  },
};

const RULES = {
  status_quo: { name: "Status Quo", cap: null, plimit: 8, col: "#ef4444" },
  bounded: { name: "Bounded Market", cap: 0.2, plimit: 4, col: "#a78bfa" },
  uk_face: { name: "UK Face Value", cap: 0, plimit: 2, col: "#38bdf8" },
  dynamic: { name: "Dynamic Pricing", cap: null, plimit: 6, col: "#fbbf24", dynMul: 2.2 },
};

function simulate(rid, mul) {
  const R = RULES[rid];
  const POP = {
    mega_fan: Math.round(BASE_POP.mega_fan * mul),
    committed_casual: Math.round(BASE_POP.committed_casual * mul),
    average_buyer: Math.round(BASE_POP.average_buyer * mul),
    // Scalpers don't scale linearly with demand — there's a relatively fixed number
    // of professional operations that increase volume, not headcount
    // CMA finding: operators don't increase headcount at high scarcity — they increase inventory depth via bots
    scalper: Math.round(BASE_POP.scalper * (1 + (mul - 1) * 0.1)),
  };
  const salePrice = R.dynMul ? FACE * R.dynMul : FACE;
  const margin = R.cap !== null ? R.cap : 1.0;
  let remain = VENUE;

  // Expected achievable flip margin given current scarcity and ruleset.
  // Bounded market: scales linearly from 0 up to the cap, reaching full cap at 2x demand
  // (the saturation point where secondary prices reliably hit the ceiling).
  // Uncapped (status quo, dynamic): grows with demand, no ceiling — captures escalating
  // speculative opportunity at high scarcity without an artificial floor.
  const SATURATION_DEMAND = 2.0;
  const expMargin = R.cap !== null
    ? R.cap * Math.min(1, Math.max(0, (mul - 1) / (SATURATION_DEMAND - 1)))
    : Math.max(0, (mul - 1) * 0.5);

  // Scalpers increase inventory depth (not headcount) with demand — each operation acquires more
  // tickets per event at high scarcity via automated purchasing
  const scalerWanted = Math.round(8 * (1 + (mul - 1) * 0.25));

  const agents = [];
  for (const [tid, def] of Object.entries(DEFS)) {
    for (let i = 0; i < POP[tid]; i++) {
      const agentDef = tid === "scalper" ? { ...def, wanted: scalerWanted } : def;
      agents.push({ type: tid, def: agentDef, tickets: 0, costBasis: 0, phase: "waiting", resaleTickets: 0, wastedTickets: 0, attending: false, secondaryPrice: 0, darkMarket: false, id: `${tid}_${i}` });
    }
  }

  // Phase 1: Primary
  const queue = agents.map(a => ({ a, pos: 1 - Math.min(1, Math.max(0, a.def.speed + (Math.random() - 0.5) * 0.3)) })).sort((x, y) => x.pos - y.pos);
  for (const { a } of queue) {
    if (remain <= 0) break;
    const lim = Math.min(a.def.wanted, R.plimit);
    if (salePrice <= a.def.maxPayMul * FACE) {
      const n = Math.min(lim, remain);
      a.tickets = n; a.costBasis = salePrice; a.phase = "got_primary"; remain -= n;
    }
  }
  agents.filter(a => a.phase === "waiting").forEach(a => { a.phase = "missed"; });

  // Dark market constants (Ireland/Australia 2025 empirical data)
  const DARK_LEAKAGE_BASE  = 0.35;  // ~35% of cap-incentive gap captured off-platform
  const DARK_FRAUD_PENALTY = 0.15;  // utility deduction for dark market buyers
  let darkSupply = 0;

  // Phase 2: Life happens
  const listings = [];
  for (const a of agents.filter(x => x.phase === "got_primary")) {
    if (a.type === "scalper") {
      a.phase = "flipping";
      if (R.cap !== null && R.cap < 0.05) {
        for (let t = 0; t < a.tickets; t++) {
          if (Math.random() < 0.3) { listings.push({ seller: a, ask: Math.round(FACE * (1.1 + Math.random() * 0.15)), isScalper: true, sold: false, finalPrice: 0 }); a.resaleTickets++; }
          else if (Math.random() < 0.4) { listings.push({ seller: a, ask: FACE, isScalper: true, sold: false, finalPrice: 0 }); a.resaleTickets++; }
          else { a.wastedTickets++; }
        }
      } else {
        for (let t = 0; t < a.tickets; t++) {
          // Demand-sensitive ask: scalpers price to market, not a fixed markup
          // mul=1: ~$150-180 (50-80%); mul=3: ~$250-340; mul=5: ~$350-500; mul=10: ~$650-950
          const platformAsk = R.cap !== null ? Math.round(salePrice * (1 + R.cap)) : Math.round(FACE * (1 + 0.5 * mul + Math.random() * mul * 0.3));
          // Dark market routing: scalpers divert tickets when cap creates a large profit gap
          if (R.cap !== null) {
            const expectedDark = FACE * (1 + 0.5 * mul);
            const incentiveGap = Math.max(0, (expectedDark - platformAsk) / expectedDark);
            if (Math.random() < DARK_LEAKAGE_BASE * incentiveGap) { darkSupply++; continue; }
          }
          listings.push({ seller: a, ask: platformAsk, isScalper: true, sold: false, finalPrice: 0 });
          a.resaleTickets++;
        }
      }
      continue;
    }
    const plansChanged = Math.random() < a.def.planChangeRate;
    const tempted = Math.random() < a.def.flipChance;
    if (plansChanged) {
      a.phase = "reselling";
      const worthIt = margin >= a.def.resaleEffortThreshold;
      const lists = worthIt ? (R.cap === 0 ? Math.random() < 0.5 : true) : Math.random() < 0.15;
      if (lists) {
        const ask = R.cap !== null ? Math.round(salePrice * (1 + R.cap * 0.9)) : a.type === "average_buyer" ? Math.round(FACE * (1.3 + Math.random() * 0.5)) : Math.round(FACE * (1.0 + Math.random() * 0.2));
        for (let t = 0; t < a.tickets; t++) listings.push({ seller: a, ask, isScalper: false, sold: false, finalPrice: 0 });
        a.resaleTickets = a.tickets;
      } else { a.wastedTickets = a.tickets; }
    } else if (tempted && a.tickets > 1 && expMargin >= a.def.flipMarginThreshold) {
      a.attending = true; a.phase = "flipping";
      const ask = R.cap !== null ? Math.round(salePrice * (1 + R.cap)) : Math.round(FACE * (1.5 + Math.random() * 1.0));
      for (let t = 0; t < a.tickets - 1; t++) listings.push({ seller: a, ask, isScalper: false, sold: false, finalPrice: 0 });
      a.resaleTickets = a.tickets - 1;
    } else {
      a.attending = true; a.phase = "attending";
      if (a.tickets > 1 && a.type === "mega_fan" && Math.random() < 0.15) {
        listings.push({ seller: a, ask: R.cap !== null ? Math.round(salePrice * (1 + (R.cap || 0) * 0.5)) : Math.round(FACE * (1.0 + Math.random() * 0.1)), isScalper: false, sold: false, finalPrice: 0 });
        a.resaleTickets = 1;
      }
      if (!tempted && a.tickets > 1 && expMargin < a.def.resaleEffortThreshold && Math.random() < 0.4) { a.wastedTickets = a.tickets - 1; }
    }
  }

  // Phase 3: Secondary - 3 rounds, all missed buyers attempt each round
  const missed = agents.filter(a => a.phase === "missed" && a.type !== "scalper");
  for (let i = missed.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [missed[i], missed[j]] = [missed[j], missed[i]]; }

  const sellerRev = { mega_fan: 0, committed_casual: 0, average_buyer: 0, scalper: 0 };
  const buyerSpent = { mega_fan: 0, committed_casual: 0, average_buyer: 0, scalper: 0 };
  const buyerGot = { mega_fan: 0, committed_casual: 0, average_buyer: 0, scalper: 0 };
  const bought = new Set();

  for (let round = 0; round < 3; round++) {
    for (const li of listings) {
      if (li.sold) continue;
      if (li.isScalper) {
        // Demand-sensitive markdown: low scarcity = gradual (CMA: 20-30% final markdown);
        // high scarcity = aggressive anchor-then-liquidate (CMA: 50-70% final markdown)
        const decays = mul <= 2 ? [1.0, 0.85, 0.75] : mul <= 5 ? [1.0, 0.65, 0.45] : [1.0, 0.50, 0.30];
        const floors = [li.seller.costBasis * 1.05, li.seller.costBasis * 1.05, li.seller.costBasis * 0.95];
        li.finalPrice = Math.max(Math.round(floors[round]), Math.round(li.ask * decays[round]));
      } else {
        const decays = [1.0, 0.95, 0.88];
        li.finalPrice = Math.max(FACE, Math.round(li.ask * decays[round]));
      }
      if (R.cap !== null) li.finalPrice = Math.min(li.finalPrice, Math.round(FACE * (1 + R.cap)));
    }
    const avail = listings.filter(x => !x.sold).sort((a, b) => a.finalPrice - b.finalPrice);
    const seekers = missed.filter(b => !bought.has(b.id));
    for (let i = seekers.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [seekers[i], seekers[j]] = [seekers[j], seekers[i]]; }
    for (const buyer of seekers) {
      const ticket = avail.find(x => !x.sold && x.finalPrice <= buyer.def.maxPayMul * FACE);
      if (ticket) {
        ticket.sold = true; buyer.phase = "bought_secondary"; buyer.secondaryPrice = ticket.finalPrice;
        buyer.attending = Math.random() < buyer.def.attendBase; bought.add(buyer.id);
        sellerRev[ticket.seller.type] += ticket.finalPrice;
        buyerSpent[buyer.type] += ticket.finalPrice; buyerGot[buyer.type]++;
      }
    }
  }

  // Phase 3.5: Dark Market
  // Scalper tickets routed off-platform match with high-WTP buyers who missed everything.
  // Transactions happen above the cap ceiling; buyers face elevated fraud risk with no recourse.
  if (darkSupply > 0 && R.cap !== null) {
    const capCeiling = FACE * (1 + R.cap);
    const frustrated = agents.filter(a => !bought.has(a.id) && a.phase === "missed" && a.def.maxPayMul * FACE > capCeiling * 1.1);
    for (let i = 0; i < Math.min(darkSupply, frustrated.length); i++) {
      const buyer = frustrated[i];
      const darkPrice = Math.round(FACE * (1 + 0.5 * mul + Math.random() * mul * 0.3));
      buyer.phase = "bought_dark"; buyer.secondaryPrice = darkPrice; buyer.darkMarket = true;
      buyer.attending = Math.random() < buyer.def.attendBase; bought.add(buyer.id);
      sellerRev.scalper += darkPrice;
    }
  }

  // Scoring
  const outcomes = {};
  for (const [tid, def] of Object.entries(DEFS)) {
    const grp = agents.filter(a => a.type === tid);
    const total = grp.length;
    const got = grp.filter(a => a.tickets > 0 || a.phase === "bought_secondary" || a.phase === "bought_dark");
    const att = grp.filter(a => a.attending);
    const avgPaid = got.length > 0 ? got.reduce((s, a) => s + (a.secondaryPrice || a.costBasis || 0), 0) / got.length : 0;

    let utility;
    if (tid === "scalper") {
      const inv = grp.reduce((s, a) => s + a.tickets * salePrice, 0);
      const ret = sellerRev.scalper;
      if (inv === 0) utility = 0;
      else { const roi = (ret - inv) / inv; utility = roi >= 0 ? 0.3 + Math.min(0.65, roi * 0.65) : Math.max(0, 0.3 * (1 + roi / 0.3)); }
    } else {
      const accessRate = got.length / total;
      if (got.length === 0) {
        utility = 0.02;
      } else {
        const priceRatio = avgPaid > 0 ? (avgPaid - FACE) / FACE : 0;
        // Steeper penalty for dynamic pricing surcharges: paying $220 for a $100 ticket
        // feels worse than paying $120 on resale because the inflated price is institutional
        // rather than market-driven. Apply a "surcharge resentment" factor when the
        // primary sale price itself exceeds face value
        let priceScore = avgPaid > 0 ? Math.max(0, 1 - priceRatio) : 0;
        if (R.dynMul && R.dynMul > 1) {
          // Additional penalty: the system itself is overcharging, not just the resale market
          // This captures the real-world resentment toward dynamic pricing (World Cup, Oasis)
          const surchargeRatio = (salePrice - FACE) / FACE; // how much above face the system charges
          const surchargeResent = surchargeRatio * 0.3; // 30% penalty weight on the surcharge
          priceScore = Math.max(0, priceScore - surchargeResent);
        }
        const attendRate = att.length / total;
        let resaleOpt = R.cap === null ? 0.7 : R.cap >= 0.15 ? 0.6 : R.cap > 0 ? 0.4 : 0.2;
        // Scale resale option by access rate: if you didn't get a ticket, the option is worthless
        resaleOpt = resaleOpt * Math.min(1, accessRate * 3); // scales to full value when 33%+ get tickets
        utility = accessRate * 0.35 + priceScore * 0.30 + attendRate * 0.20 + resaleOpt * 0.15;
        const darkFrac = got.filter(a => a.darkMarket).length / got.length;
        utility = Math.max(0, utility - darkFrac * DARK_FRAUD_PENALTY);
      }
    }
    outcomes[tid] = { utility: Math.round(utility * 100) / 100, got: got.length, att: att.length, total, avgPrice: Math.round(avgPaid) };
  }

  function calcGR(list) { const mn = Math.min(...list), mx = Math.max(...list), av = list.reduce((s,u) => s+u, 0)/list.length; return Math.round((mn*0.4 + (1-(mx-mn))*0.3 + av*0.2 + 0.5*0.1)*100)/100; }

  const fanTypes = ["mega_fan", "committed_casual", "average_buyer"];
  const primarySold = VENUE - remain;
  const secondarySold = listings.filter(l => l.sold).length;
  return {
    system: calcGR(Object.values(outcomes).map(o => o.utility)),
    fanOnly: calcGR(fanTypes.map(t => outcomes[t].utility)),
    popWt: calcGR((() => { const w = []; for (const [t,o] of Object.entries(outcomes)) for (let i = 0; i < POP[t]; i++) w.push(o.utility); return w; })()),
    outcomes,
    // Attendance = seats filled, not unique agents
    // Attending primary holders fill (tickets - resold - wasted) seats each
    // Attending secondary buyers fill 1 seat each
    attend: agents.reduce((seats, a) => {
      if (!a.attending) return seats;
      if (a.phase === "bought_secondary" || a.phase === "bought_dark") return seats + 1;
      return seats + Math.max(0, a.tickets - a.resaleTickets - a.wastedTickets);
    }, 0),
    wasted: agents.reduce((s,a) => s + a.wastedTickets, 0),
    primarySold,
    secondarySold,
    darkMarket: agents.filter(a => a.darkMarket).length,
  };
}

function runCurve(runsPerPoint) {
  const demandLevels = [1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10];
  const results = {};
  for (const rid of Object.keys(RULES)) {
    results[rid] = demandLevels.map(mul => {
      const runs = Array.from({ length: runsPerPoint }, () => simulate(rid, mul));
      const avg = (fn) => Math.round(runs.reduce((s, r) => s + fn(r), 0) / runs.length * 100) / 100;
      const avgI = (fn) => Math.round(runs.reduce((s, r) => s + fn(r), 0) / runs.length);
      const oc = {};
      for (const t of Object.keys(DEFS)) {
        oc[t] = { utility: avg(r => r.outcomes[t].utility), got: avgI(r => r.outcomes[t].got), total: avgI(r => r.outcomes[t].total), avgPrice: avgI(r => r.outcomes[t].avgPrice) };
      }
      return { mul, system: avg(r => r.system), fanOnly: avg(r => r.fanOnly), popWt: avg(r => r.popWt), attend: avgI(r => r.attend), wasted: avgI(r => r.wasted), primarySold: avgI(r => r.primarySold), secondarySold: avgI(r => r.secondarySold), outcomes: oc };
    });
  }
  return { demandLevels, results };
}

// ── Chart Drawing ──
function Chart({ data, metric, title, height = 200 }) {
  if (!data) return null;
  const { demandLevels, results } = data;
  const W = 700, H = height, pad = { t: 20, r: 20, b: 40, l: 45 };
  const cw = W - pad.l - pad.r, ch = H - pad.t - pad.b;

  // Find y range across all series
  let yMin = 1, yMax = 0;
  for (const rid of Object.keys(RULES)) {
    for (const pt of results[rid]) {
      const v = pt[metric];
      if (v < yMin) yMin = v;
      if (v > yMax) yMax = v;
    }
  }
  yMin = Math.max(0, Math.floor(yMin * 10) / 10 - 0.05);
  yMax = Math.min(1, Math.ceil(yMax * 10) / 10 + 0.05);
  const yRange = yMax - yMin || 0.1;

  const xScale = (i) => pad.l + (i / (demandLevels.length - 1)) * cw;
  const yScale = (v) => pad.t + ch - ((v - yMin) / yRange) * ch;

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: "#889", letterSpacing: "0.08em", marginBottom: 6 }}>{title}</div>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: W, background: "#0e0e1a", borderRadius: 8, border: "1px solid #222238" }}>
        {/* Grid */}
        {[0, 0.25, 0.5, 0.75, 1].map(frac => {
          const v = yMin + frac * yRange;
          const y = yScale(v);
          return v >= yMin && v <= yMax ? (
            <g key={frac}>
              <line x1={pad.l} y1={y} x2={W - pad.r} y2={y} stroke="#1a1a2e" strokeWidth={1} />
              <text x={pad.l - 6} y={y + 3} textAnchor="end" fill="#556" fontSize={9} fontFamily="monospace">{v.toFixed(2)}</text>
            </g>
          ) : null;
        })}
        {/* X axis labels */}
        {demandLevels.map((d, i) => (
          <text key={d} x={xScale(i)} y={H - 8} textAnchor="middle" fill="#556" fontSize={9} fontFamily="monospace">{d}x</text>
        ))}
        <text x={W / 2} y={H - 0} textAnchor="middle" fill="#445" fontSize={8} fontFamily="monospace">demand multiplier</text>
        {/* Lines */}
        {Object.entries(RULES).map(([rid, rule]) => {
          const pts = results[rid];
          const d = pts.map((pt, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(pt[metric])}`).join(" ");
          return (
            <g key={rid}>
              <path d={d} fill="none" stroke={rule.col} strokeWidth={2.5} strokeLinejoin="round" opacity={0.9} />
              {pts.map((pt, i) => (
                <circle key={i} cx={xScale(i)} cy={yScale(pt[metric])} r={3} fill={rule.col} />
              ))}
            </g>
          );
        })}
      </svg>
      {/* Legend */}
      <div style={{ display: "flex", gap: 16, marginTop: 6, justifyContent: "center" }}>
        {Object.entries(RULES).map(([rid, rule]) => (
          <div key={rid} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <div style={{ width: 12, height: 3, background: rule.col, borderRadius: 1 }} />
            <span style={{ fontSize: 9, color: "#889" }}>{rule.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AgentChart({ data, agentType, agentName, agentCol }) {
  if (!data) return null;
  const { demandLevels, results } = data;
  const W = 700, H = 160, pad = { t: 16, r: 20, b: 36, l: 45 };
  const cw = W - pad.l - pad.r, ch = H - pad.t - pad.b;

  let yMin = 1, yMax = 0;
  for (const rid of Object.keys(RULES)) {
    for (const pt of results[rid]) {
      const v = pt.outcomes[agentType]?.utility || 0;
      if (v < yMin) yMin = v;
      if (v > yMax) yMax = v;
    }
  }
  yMin = Math.max(0, Math.floor(yMin * 10) / 10 - 0.05);
  yMax = Math.min(1, Math.ceil(yMax * 10) / 10 + 0.05);
  const yRange = yMax - yMin || 0.1;
  const xScale = (i) => pad.l + (i / (demandLevels.length - 1)) * cw;
  const yScale = (v) => pad.t + ch - ((v - yMin) / yRange) * ch;

  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 10, fontWeight: 600, color: agentCol, marginBottom: 4 }}>{agentName}</div>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: W, background: "#0e0e1a", borderRadius: 6, border: "1px solid #1a1a2e" }}>
        {[0, 0.5, 1].map(frac => {
          const v = yMin + frac * yRange, y = yScale(v);
          return v >= yMin && v <= yMax ? (
            <g key={frac}><line x1={pad.l} y1={y} x2={W-pad.r} y2={y} stroke="#1a1a2e" strokeWidth={1} /><text x={pad.l-6} y={y+3} textAnchor="end" fill="#445" fontSize={8} fontFamily="monospace">{v.toFixed(2)}</text></g>
          ) : null;
        })}
        {demandLevels.map((d, i) => <text key={d} x={xScale(i)} y={H-8} textAnchor="middle" fill="#445" fontSize={8} fontFamily="monospace">{d}x</text>)}
        {Object.entries(RULES).map(([rid, rule]) => {
          const pts = results[rid];
          const d = pts.map((pt, i) => `${i===0?"M":"L"} ${xScale(i)} ${yScale(pt.outcomes[agentType]?.utility || 0)}`).join(" ");
          return <path key={rid} d={d} fill="none" stroke={rule.col} strokeWidth={2} strokeLinejoin="round" opacity={0.85} />;
        })}
      </svg>
    </div>
  );
}

export default function App() {
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);
  const [view, setView] = useState("gr");
  const [runs, setRuns] = useState(15);
  const [copied, setCopied] = useState(false);

  const go = useCallback(() => {
    setBusy(true);
    setTimeout(() => { setData(runCurve(runs)); setBusy(false); }, 100);
  }, [runs]);

  return (
    <div style={{ fontFamily: "'SF Mono','Fira Code','JetBrains Mono',monospace", maxWidth: 780, margin: "0 auto", padding: 20, color: "#dde", background: "#0a0a12", minHeight: "100vh", borderRadius: 12 }}>
      <div style={{ marginBottom: 20, borderBottom: "1px solid #222238", paddingBottom: 14 }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: "#a78bfa" }}>GRE <span style={{ color: "#556", fontWeight: 400, fontSize: 12 }}>Scarcity Curve Analysis</span></div>
        <div style={{ fontSize: 10, color: "#445", marginTop: 3 }}>
          Golden Rule scores across demand levels (1x&#x2013;10x) · {VENUE} seats · {runs} runs averaged per point
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16, alignItems: "flex-end", flexWrap: "wrap" }}>
        <div>
          <div style={{ fontSize: 9, color: "#667", fontWeight: 700, letterSpacing: "0.1em", marginBottom: 3 }}>PRECISION</div>
          <select value={runs} onChange={e => { setRuns(parseInt(e.target.value)); setData(null); }} style={{ padding: "6px 8px", borderRadius: 5, fontSize: 11, background: "#111120", color: "#dde", border: "1px solid #222238", fontFamily: "inherit" }}>
            <option value={8}>Fast (8 runs)</option>
            <option value={15}>Normal (15 runs)</option>
            <option value={30}>Precise (30 runs)</option>
          </select>
        </div>
        <button onClick={go} disabled={busy} style={{ padding: "7px 24px", borderRadius: 5, fontSize: 11, fontWeight: 600, background: busy ? "#222" : "linear-gradient(135deg,#6366F1,#8b5cf6)", color: "#fff", border: "none", cursor: busy ? "default" : "pointer", fontFamily: "inherit" }}>
          {busy ? "Running..." : "▶ Generate Curves"}
        </button>
        {data && (
          <div style={{ display: "flex", gap: 4 }}>
            {[["gr", "GR Scores"], ["agents", "Per Agent"], ["export", "📋 Data Export"]].map(([v, l]) => (
              <button key={v} onClick={() => setView(v)} style={{ padding: "6px 14px", borderRadius: 5, fontSize: 10, fontWeight: 600, background: view === v ? "#1a1040" : "#111120", color: view === v ? "#a78bfa" : "#667", border: `1px solid ${view === v ? "#6366F140" : "#222238"}`, cursor: "pointer", fontFamily: "inherit" }}>{l}</button>
            ))}
          </div>
        )}
      </div>

      {data && view === "gr" && (
        <div>
          <Chart data={data} metric="fanOnly" title="FAN FAIRNESS (excluding scalpers)" height={220} />
          <Chart data={data} metric="popWt" title="POPULATION WEIGHTED (by headcount)" height={220} />
          <Chart data={data} metric="system" title="SYSTEM (all agents equal weight)" height={220} />

          <div style={{ background: "#111120", borderRadius: 8, padding: 14, border: "1px solid #222238", marginTop: 8 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: "#889", marginBottom: 8 }}>KEY INSIGHT</div>
            <div style={{ fontSize: 11, color: "#aab", lineHeight: 1.7 }}>
              The bounded market is the only system that maintains high utility across all scarcity levels. At low demand it matches status quo (no reason to change when the market clears easily). At high demand it matches or exceeds dynamic pricing (both compress scalper extraction). Status quo collapses under scarcity. Dynamic pricing underperforms at low scarcity by overcharging for events that don't warrant it. The bounded market's value proposition is <span style={{ color: "#a78bfa", fontWeight: 600 }}>robustness</span> — not optimal at any single point, but consistently good everywhere.
            </div>
          </div>
        </div>
      )}

      {data && view === "agents" && (
        <div>
          <AgentChart data={data} agentType="mega_fan" agentName="🎸 Mega Fan" agentCol="#7C3AED" />
          <AgentChart data={data} agentType="committed_casual" agentName="🎵 Committed Casual" agentCol="#2563EB" />
          <AgentChart data={data} agentType="average_buyer" agentName="🎟️ Average Buyer" agentCol="#059669" />
          <AgentChart data={data} agentType="scalper" agentName="🐺 Scalper" agentCol="#DC2626" />

          <div style={{ display: "flex", gap: 16, marginTop: 8, justifyContent: "center" }}>
            {Object.entries(RULES).map(([rid, rule]) => (
              <div key={rid} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <div style={{ width: 12, height: 3, background: rule.col, borderRadius: 1 }} />
                <span style={{ fontSize: 9, color: "#889" }}>{rule.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {data && view === "export" && (() => {
        const { demandLevels, results } = data;
        const rids = Object.keys(RULES);
        const agentTypes = Object.keys(DEFS);
        const agentNames = { mega_fan: "Mega Fan", committed_casual: "Committed Casual", average_buyer: "Average Buyer", scalper: "Scalper" };

        // Build text tables
        const sep = " | ";
        const lines = [];

        lines.push("=== GOLDEN RULE SCORES BY DEMAND LEVEL ===");
        lines.push("");
        lines.push(["Demand", ...rids.map(r => RULES[r].name + " (Fan)"), ...rids.map(r => RULES[r].name + " (Pop)"), ...rids.map(r => RULES[r].name + " (Sys)")].join(sep));
        lines.push("-".repeat(180));
        for (let i = 0; i < demandLevels.length; i++) {
          const d = demandLevels[i];
          const row = [d + "x"];
          for (const rid of rids) row.push(results[rid][i].fanOnly.toString());
          for (const rid of rids) row.push(results[rid][i].popWt.toString());
          for (const rid of rids) row.push(results[rid][i].system.toString());
          lines.push(row.join(sep));
        }

        lines.push("");
        lines.push("=== PER-AGENT UTILITY BY DEMAND LEVEL ===");
        for (const tid of agentTypes) {
          lines.push("");
          lines.push(`--- ${agentNames[tid]} ---`);
          lines.push(["Demand", ...rids.map(r => RULES[r].name + " (util)"), ...rids.map(r => RULES[r].name + " (got/total)"), ...rids.map(r => RULES[r].name + " (avg$)")].join(sep));
          lines.push("-".repeat(180));
          for (let i = 0; i < demandLevels.length; i++) {
            const d = demandLevels[i];
            const row = [d + "x"];
            for (const rid of rids) row.push((results[rid][i].outcomes[tid]?.utility || 0).toString());
            for (const rid of rids) { const o = results[rid][i].outcomes[tid]; row.push(o ? `${o.got}/${o.total}` : "0/0"); }
            for (const rid of rids) row.push("$" + (results[rid][i].outcomes[tid]?.avgPrice || 0).toString());
            lines.push(row.join(sep));
          }
        }

        lines.push("");
        lines.push("=== ATTENDANCE, WASTAGE & TICKET FLOW ===");
        lines.push(["Demand", ...rids.map(r => RULES[r].name + " (attend)"), ...rids.map(r => RULES[r].name + " (wasted)"), ...rids.map(r => RULES[r].name + " (1°sold)"), ...rids.map(r => RULES[r].name + " (2°sold)")].join(sep));
        lines.push("-".repeat(200));
        for (let i = 0; i < demandLevels.length; i++) {
          const d = demandLevels[i];
          const row = [d + "x"];
          for (const rid of rids) row.push(results[rid][i].attend.toString());
          for (const rid of rids) row.push(results[rid][i].wasted.toString());
          for (const rid of rids) row.push(results[rid][i].primarySold.toString());
          for (const rid of rids) row.push(results[rid][i].secondarySold.toString());
          lines.push(row.join(sep));
        }

        const fullText = lines.join("\n");

        return (
          <div>
            <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
              <button onClick={() => { navigator.clipboard.writeText(fullText).then(() => setCopied(true)).catch(() => {}); setTimeout(() => setCopied(false), 2000); }}
                style={{ padding: "7px 18px", borderRadius: 5, fontSize: 11, fontWeight: 600, background: copied ? "#166534" : "#111120", color: copied ? "#4ade80" : "#a78bfa", border: "1px solid #6366F130", cursor: "pointer", fontFamily: "inherit" }}>
                {copied ? "✓ Copied!" : "📋 Copy All Data"}
              </button>
              <span style={{ fontSize: 10, color: "#556", alignSelf: "center" }}>Copy and paste into our chat for analysis</span>
            </div>
            <pre style={{
              background: "#0e0e1a", border: "1px solid #222238", borderRadius: 8, padding: 14,
              fontSize: 9, color: "#99a", lineHeight: 1.5, overflow: "auto", maxHeight: 500,
              whiteSpace: "pre", fontFamily: "inherit",
            }}>{fullText}</pre>
          </div>
        );
      })()}

      {!data && !busy && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#334" }}>
          <div style={{ fontSize: 28, marginBottom: 10 }}>📈</div>
          <div style={{ fontSize: 11 }}>Generate scarcity curves to see how each ruleset performs from Tuesday comedy shows to Eras Tour</div>
          <div style={{ fontSize: 9, marginTop: 6, color: "#2a2a3a" }}>Tests 10 demand levels × 4 rulesets × {runs} runs each = {10 * 4 * runs} simulations</div>
        </div>
      )}
    </div>
  );
}
