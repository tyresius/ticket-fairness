// Cap Optimization Sweep
// Runs bounded market at cap levels [0.05..0.50] × demand levels [1..10]
// plus status_quo and dynamic_pricing as reference columns.
// Outputs two CSV files: cap-sweep-summary.csv and cap-sweep-agents.csv

const fs = require("fs");

// ── Simulation constants (mirrored from gre-scarcity-curves.jsx) ──
const VENUE = 500;
const FACE = 100;
const BASE_POP = { mega_fan: 80, committed_casual: 150, average_buyer: 200, scalper: 30 };

const DEFS = {
  mega_fan:         { speed: 0.85, maxPayMul: 2.5, attendBase: 0.95, wanted: 2, flipChance: 0.02, planChangeRate: 0.08, resaleEffortThreshold: 0.0 },
  committed_casual: { speed: 0.35, maxPayMul: 1.8, attendBase: 0.78, wanted: 2, flipChance: 0.08, planChangeRate: 0.2,  resaleEffortThreshold: 0.05 },
  average_buyer:    { speed: 0.3,  maxPayMul: 1.4, attendBase: 0.55, wanted: 3, flipChance: 0.2,  planChangeRate: 0.25, resaleEffortThreshold: 0.1 },
  scalper:          { speed: 0.95, maxPayMul: 3.0, attendBase: 0.01, wanted: 8, flipChance: 1.0,  planChangeRate: 0.0,  resaleEffortThreshold: 0.0 },
};

// Base rulesets — bounded variants are generated dynamically below
const BASE_RULES = {
  status_quo: { name: "Status Quo",      cap: null, plimit: 8, dynMul: null },
  dynamic:    { name: "Dynamic Pricing", cap: null, plimit: 6, dynMul: 2.2  },
};

function makeRule(cap) {
  return { name: `Bounded ${Math.round(cap * 100)}%`, cap, plimit: 4, dynMul: null };
}

function simulate(R, mul) {
  const POP = {
    mega_fan:         Math.round(BASE_POP.mega_fan * mul),
    committed_casual: Math.round(BASE_POP.committed_casual * mul),
    average_buyer:    Math.round(BASE_POP.average_buyer * mul),
    scalper:          Math.round(BASE_POP.scalper * (1 + (mul - 1) * 0.3)),
  };
  const salePrice = R.dynMul ? FACE * R.dynMul : FACE;
  const margin = R.cap !== null ? R.cap : 1.0;
  let remain = VENUE;

  const agents = [];
  for (const [tid, def] of Object.entries(DEFS)) {
    for (let i = 0; i < POP[tid]; i++) {
      agents.push({ type: tid, def, tickets: 0, costBasis: 0, phase: "waiting",
                    resaleTickets: 0, wastedTickets: 0, attending: false,
                    secondaryPrice: 0, id: `${tid}_${i}` });
    }
  }

  // Phase 1: Primary
  const queue = agents
    .map(a => ({ a, pos: 1 - Math.min(1, Math.max(0, a.def.speed + (Math.random() - 0.5) * 0.3)) }))
    .sort((x, y) => x.pos - y.pos);
  for (const { a } of queue) {
    if (remain <= 0) break;
    const lim = Math.min(a.def.wanted, R.plimit);
    if (salePrice <= a.def.maxPayMul * FACE) {
      const n = Math.min(lim, remain);
      a.tickets = n; a.costBasis = salePrice; a.phase = "got_primary"; remain -= n;
    }
  }
  agents.filter(a => a.phase === "waiting").forEach(a => { a.phase = "missed"; });

  // Phase 2: Life happens
  const listings = [];
  for (const a of agents.filter(x => x.phase === "got_primary")) {
    if (a.type === "scalper") {
      a.phase = "flipping";
      if (R.cap !== null && R.cap < 0.05) {
        for (let t = 0; t < a.tickets; t++) {
          if (Math.random() < 0.3) {
            listings.push({ seller: a, ask: Math.round(FACE * (1.1 + Math.random() * 0.15)), isScalper: true, sold: false, finalPrice: 0 });
            a.resaleTickets++;
          } else if (Math.random() < 0.4) {
            listings.push({ seller: a, ask: FACE, isScalper: true, sold: false, finalPrice: 0 });
            a.resaleTickets++;
          } else {
            a.wastedTickets++;
          }
        }
      } else {
        for (let t = 0; t < a.tickets; t++) {
          const ask = R.cap !== null
            ? Math.round(salePrice * (1 + R.cap))
            : Math.round(FACE * (1.5 + Math.random() * 1.0));
          listings.push({ seller: a, ask, isScalper: true, sold: false, finalPrice: 0 });
        }
        a.resaleTickets = a.tickets;
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
        const ask = R.cap !== null
          ? Math.round(salePrice * (1 + R.cap * 0.9))
          : a.type === "average_buyer"
            ? Math.round(FACE * (1.3 + Math.random() * 0.5))
            : Math.round(FACE * (1.0 + Math.random() * 0.2));
        for (let t = 0; t < a.tickets; t++)
          listings.push({ seller: a, ask, isScalper: false, sold: false, finalPrice: 0 });
        a.resaleTickets = a.tickets;
      } else {
        a.wastedTickets = a.tickets;
      }
    } else if (tempted && a.tickets > 1 && margin >= 0.15) {
      a.attending = true; a.phase = "flipping";
      const ask = R.cap !== null
        ? Math.round(salePrice * (1 + R.cap))
        : Math.round(FACE * (1.5 + Math.random() * 1.0));
      for (let t = 0; t < a.tickets - 1; t++)
        listings.push({ seller: a, ask, isScalper: false, sold: false, finalPrice: 0 });
      a.resaleTickets = a.tickets - 1;
    } else {
      a.attending = true; a.phase = "attending";
      if (a.tickets > 1 && a.type === "mega_fan" && Math.random() < 0.15) {
        listings.push({ seller: a, ask: R.cap !== null ? Math.round(salePrice * (1 + (R.cap || 0) * 0.5)) : Math.round(FACE * (1.0 + Math.random() * 0.1)), isScalper: false, sold: false, finalPrice: 0 });
        a.resaleTickets = 1;
      }
      if (!tempted && a.tickets > 1 && margin < 0.15 && Math.random() < 0.4) {
        a.wastedTickets = a.tickets - 1;
      }
    }
  }

  // Phase 3: Secondary — 3 rounds
  const missed = agents.filter(a => a.phase === "missed" && a.type !== "scalper");
  for (let i = missed.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [missed[i], missed[j]] = [missed[j], missed[i]];
  }

  const sellerRev  = { mega_fan: 0, committed_casual: 0, average_buyer: 0, scalper: 0 };
  const buyerSpent = { mega_fan: 0, committed_casual: 0, average_buyer: 0, scalper: 0 };
  const buyerGot   = { mega_fan: 0, committed_casual: 0, average_buyer: 0, scalper: 0 };
  const bought = new Set();

  for (let round = 0; round < 3; round++) {
    for (const li of listings) {
      if (li.sold) continue;
      if (li.isScalper) {
        const decays  = [1.0, 0.70, 0.50];
        const floors  = [li.seller.costBasis * 1.05, li.seller.costBasis * 1.05, li.seller.costBasis * 0.95];
        li.finalPrice = Math.max(Math.round(floors[round]), Math.round(li.ask * decays[round]));
      } else {
        const decays  = [1.0, 0.95, 0.88];
        li.finalPrice = Math.max(FACE, Math.round(li.ask * decays[round]));
      }
      if (R.cap !== null) li.finalPrice = Math.min(li.finalPrice, Math.round(FACE * (1 + R.cap)));
    }
    const avail   = listings.filter(x => !x.sold).sort((a, b) => a.finalPrice - b.finalPrice);
    const seekers = missed.filter(b => !bought.has(b.id));
    for (let i = seekers.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [seekers[i], seekers[j]] = [seekers[j], seekers[i]];
    }
    for (const buyer of seekers) {
      const ticket = avail.find(x => !x.sold && x.finalPrice <= buyer.def.maxPayMul * FACE);
      if (ticket) {
        ticket.sold = true; buyer.phase = "bought_secondary"; buyer.secondaryPrice = ticket.finalPrice;
        buyer.attending = Math.random() < buyer.def.attendBase; bought.add(buyer.id);
        sellerRev[ticket.seller.type]  += ticket.finalPrice;
        buyerSpent[buyer.type]         += ticket.finalPrice;
        buyerGot[buyer.type]++;
      }
    }
  }

  // Scoring
  const outcomes = {};
  for (const [tid] of Object.entries(DEFS)) {
    const grp    = agents.filter(a => a.type === tid);
    const total  = grp.length;
    const got    = grp.filter(a => a.tickets > 0 || a.phase === "bought_secondary");
    const att    = grp.filter(a => a.attending);
    const avgPaid = got.length > 0
      ? got.reduce((s, a) => s + (a.secondaryPrice || a.costBasis || 0), 0) / got.length
      : 0;

    let utility;
    if (tid === "scalper") {
      const inv = grp.reduce((s, a) => s + a.tickets * salePrice, 0);
      const ret = sellerRev.scalper;
      if (inv === 0) utility = 0;
      else {
        const roi = (ret - inv) / inv;
        utility = roi >= 0
          ? 0.3 + Math.min(0.65, roi * 0.65)
          : Math.max(0, 0.3 * (1 + roi / 0.3));
      }
    } else {
      const accessRate = got.length / total;
      if (got.length === 0) {
        utility = 0.02;
      } else {
        const priceRatio = avgPaid > 0 ? (avgPaid - FACE) / FACE : 0;
        let priceScore   = avgPaid > 0 ? Math.max(0, 1 - priceRatio) : 0;
        if (R.dynMul && R.dynMul > 1) {
          const surchargeRatio = (salePrice - FACE) / FACE;
          const surchargeResent = surchargeRatio * 0.3;
          priceScore = Math.max(0, priceScore - surchargeResent);
        }
        const attendRate = att.length / total;
        let resaleOpt = R.cap === null ? 0.7 : R.cap >= 0.15 ? 0.6 : R.cap > 0 ? 0.4 : 0.2;
        resaleOpt = resaleOpt * Math.min(1, accessRate * 3);
        utility = accessRate * 0.35 + priceScore * 0.30 + attendRate * 0.20 + resaleOpt * 0.15;
      }
    }
    outcomes[tid] = {
      utility:  Math.round(utility * 100) / 100,
      got:      got.length,
      att:      att.length,
      total,
      avgPrice: Math.round(avgPaid),
    };
  }

  function calcGR(list) {
    const mn = Math.min(...list), mx = Math.max(...list);
    const av = list.reduce((s, u) => s + u, 0) / list.length;
    return Math.round((mn * 0.4 + (1 - (mx - mn)) * 0.3 + av * 0.2 + 0.5 * 0.1) * 100) / 100;
  }

  const fanTypes   = ["mega_fan", "committed_casual", "average_buyer"];
  const primarySold   = VENUE - remain;
  const secondarySold = listings.filter(l => l.sold).length;

  return {
    system:  calcGR(Object.values(outcomes).map(o => o.utility)),
    fanOnly: calcGR(fanTypes.map(t => outcomes[t].utility)),
    popWt:   calcGR((() => {
      const w = [];
      for (const [t, o] of Object.entries(outcomes))
        for (let i = 0; i < POP[t]; i++) w.push(o.utility);
      return w;
    })()),
    outcomes,
    attend:       agents.reduce((seats, a) => {
      if (!a.attending) return seats;
      if (a.phase === "bought_secondary") return seats + 1;
      return seats + Math.max(0, a.tickets - a.resaleTickets - a.wastedTickets);
    }, 0),
    wasted:       agents.reduce((s, a) => s + a.wastedTickets, 0),
    primarySold,
    secondarySold,
  };
}

function avg(runs, fn) {
  return Math.round(runs.reduce((s, r) => s + fn(r), 0) / runs.length * 100) / 100;
}
function avgI(runs, fn) {
  return Math.round(runs.reduce((s, r) => s + fn(r), 0) / runs.length);
}

// ── Sweep configuration ──
const DEMAND_LEVELS = [1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10];
const CAP_LEVELS    = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50];
const RUNS_PER_POINT = 30;

// Build the full set of series: reference rulesets + bounded cap variants
const SERIES = [
  { id: "status_quo", label: "Status Quo",       rule: BASE_RULES.status_quo },
  { id: "dynamic",    label: "Dynamic Pricing",  rule: BASE_RULES.dynamic    },
  ...CAP_LEVELS.map(c => ({
    id:    `bounded_${Math.round(c * 100)}`,
    label: `Bounded ${Math.round(c * 100)}%`,
    rule:  makeRule(c),
  })),
];

console.log(`Running sweep: ${SERIES.length} series × ${DEMAND_LEVELS.length} demand levels × ${RUNS_PER_POINT} runs`);
console.log(`Total simulations: ${SERIES.length * DEMAND_LEVELS.length * RUNS_PER_POINT}`);

const summaryRows = [];   // one row per (series × demand)
const agentRows   = [];   // one row per (series × demand × agent_type)

for (const series of SERIES) {
  process.stdout.write(`  ${series.label.padEnd(20)}`);
  for (const mul of DEMAND_LEVELS) {
    const runs = Array.from({ length: RUNS_PER_POINT }, () => simulate(series.rule, mul));

    const system  = avg(runs, r => r.system);
    const fanOnly = avg(runs, r => r.fanOnly);
    const popWt   = avg(runs, r => r.popWt);
    const attend  = avgI(runs, r => r.attend);
    const wasted  = avgI(runs, r => r.wasted);

    summaryRows.push({
      series:     series.label,
      cap_pct:    series.rule.cap !== null ? Math.round(series.rule.cap * 100) : "N/A",
      demand:     mul,
      gr_system:  system,
      gr_fan:     fanOnly,
      gr_popwt:   popWt,
      attend,
      wasted,
    });

    for (const tid of Object.keys(DEFS)) {
      const u  = avg(runs,  r => r.outcomes[tid].utility);
      const got = avgI(runs, r => r.outcomes[tid].got);
      const tot = avgI(runs, r => r.outcomes[tid].total);
      const ap  = avgI(runs, r => r.outcomes[tid].avgPrice);
      agentRows.push({
        series:     series.label,
        cap_pct:    series.rule.cap !== null ? Math.round(series.rule.cap * 100) : "N/A",
        demand:     mul,
        agent:      tid,
        utility:    u,
        got,
        total:      tot,
        access_pct: Math.round(got / tot * 100),
        avg_price:  ap,
      });
    }
    process.stdout.write(".");
  }
  console.log();
}

// ── Write CSV helper ──
function toCSV(rows) {
  if (rows.length === 0) return "";
  const keys = Object.keys(rows[0]);
  const header = keys.join(",");
  const lines  = rows.map(r => keys.map(k => r[k]).join(","));
  return [header, ...lines].join("\n");
}

fs.writeFileSync("cap-sweep-summary.csv", toCSV(summaryRows));
fs.writeFileSync("cap-sweep-agents.csv",  toCSV(agentRows));

console.log("\nWrote cap-sweep-summary.csv and cap-sweep-agents.csv");

// ── Quick optimal-cap analysis printed to console ──
console.log("\n── Optimal cap by demand level (Fan Fairness lens) ──");
console.log("Demand | Opt Cap | Fan GR | vs Status Quo | vs Dynamic");
console.log("-------|---------|--------|---------------|----------");

for (const mul of DEMAND_LEVELS) {
  const sq  = summaryRows.find(r => r.series === "Status Quo"      && r.demand === mul);
  const dyn = summaryRows.find(r => r.series === "Dynamic Pricing" && r.demand === mul);

  const bounded = summaryRows.filter(r =>
    r.series.startsWith("Bounded") && r.demand === mul
  );
  const best = bounded.reduce((a, b) => b.gr_fan > a.gr_fan ? b : a);

  const dSQ  = (best.gr_fan - sq.gr_fan).toFixed(2);
  const dDyn = (best.gr_fan - dyn.gr_fan).toFixed(2);

  console.log(
    `  ${String(mul).padEnd(5)}  | ${String(best.cap_pct + "%").padEnd(7)} | ` +
    `${best.gr_fan.toFixed(2)}   | ` +
    `${dSQ >= 0 ? "+" : ""}${dSQ}          | ` +
    `${dDyn >= 0 ? "+" : ""}${dDyn}`
  );
}

console.log("\n── Optimal cap by demand level (Population Weighted lens) ──");
console.log("Demand | Opt Cap | PopWt GR | vs Status Quo | vs Dynamic");
console.log("-------|---------|----------|---------------|----------");

for (const mul of DEMAND_LEVELS) {
  const sq  = summaryRows.find(r => r.series === "Status Quo"      && r.demand === mul);
  const dyn = summaryRows.find(r => r.series === "Dynamic Pricing" && r.demand === mul);

  const bounded = summaryRows.filter(r =>
    r.series.startsWith("Bounded") && r.demand === mul
  );
  const best = bounded.reduce((a, b) => b.gr_popwt > a.gr_popwt ? b : a);

  const dSQ  = (best.gr_popwt - sq.gr_popwt).toFixed(2);
  const dDyn = (best.gr_popwt - dyn.gr_popwt).toFixed(2);

  console.log(
    `  ${String(mul).padEnd(5)}  | ${String(best.cap_pct + "%").padEnd(7)} | ` +
    `${best.gr_popwt.toFixed(2)}     | ` +
    `${dSQ >= 0 ? "+" : ""}${dSQ}          | ` +
    `${dDyn >= 0 ? "+" : ""}${dDyn}`
  );
}
