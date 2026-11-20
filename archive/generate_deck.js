"use strict";
const pptxgen = require("pptxgenjs");

// ─── DESIGN CONSTANTS ───────────────────────────────────────────────────────
const BG       = "0F1923";  // dark navy
const TEXT     = "E8F0F8";  // primary text
const GREEN    = "7ECBA1";  // accent green
const BLUE     = "5BA4CF";  // accent blue
const RED      = "E05C5C";  // accent red
const AMBER    = "F4D03F";  // accent amber
const MUTED    = "8AA0B0";  // muted text
const CARD     = "1A2A3A";  // card bg
const FONT     = "Calibri";

const W = 13.33;  // slide width
const H = 7.5;    // slide height

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";  // 13.3" × 7.5"
pres.title  = "The Bounded Market";
pres.author = "GRE Simulation";

// ─── SLIDE 1 ── TITLE ────────────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  // Large subtle geometric shapes for visual interest
  slide.addShape(pres.shapes.OVAL, {
    x: -1.5, y: -1.5, w: 7, h: 7,
    fill: { color: "1A2A3A", transparency: 40 },
    line: { color: "1A2A3A", width: 0 }
  });
  slide.addShape(pres.shapes.OVAL, {
    x: 8.5, y: 2.5, w: 6, h: 6,
    fill: { color: "5BA4CF", transparency: 88 },
    line: { color: "5BA4CF", width: 0 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.5, w: 12.33, h: 0.03,
    fill: { color: GREEN, transparency: 60 },
    line: { color: GREEN, width: 0 }
  });

  // Main title
  slide.addText("The Bounded Market", {
    x: 1, y: 1.8, w: 11.33, h: 1.2,
    fontSize: 44, bold: true, color: TEXT, fontFace: FONT,
    align: "center", valign: "middle", margin: 0
  });

  // Subtitle
  slide.addText("A Fair Systems Approach to Ticket Resale Reform", {
    x: 1, y: 3.2, w: 11.33, h: 0.7,
    fontSize: 22, color: GREEN, fontFace: FONT,
    align: "center", valign: "middle", margin: 0
  });

  // Footer tag
  slide.addText("Golden Rule Equilibrium Framework  |  April 2026", {
    x: 1, y: 6.7, w: 11.33, h: 0.4,
    fontSize: 12, color: MUTED, fontFace: FONT,
    align: "center", valign: "middle", margin: 0
  });
}

// ─── SLIDE 2 ── TWO COLUMN: Problem ──────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  // Title
  slide.addText("Primary Market Reform Has Reached Its Limits", {
    x: 0.5, y: 0.25, w: 12.33, h: 0.8,
    fontSize: 34, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  // Left column header
  slide.addText("What's been tried", {
    x: 0.5, y: 1.2, w: 5.8, h: 0.4,
    fontSize: 16, bold: true, color: BLUE, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  // Left bullets
  slide.addText([
    { text: "Verified Fan & behavioral screening", options: { bullet: true, breakLine: true } },
    { text: "Purchase limits (2–8 tickets)", options: { bullet: true, breakLine: true } },
    { text: "Bot legislation (BOTS Act)", options: { bullet: true, breakLine: true } },
    { text: "Dynamic pricing", options: { bullet: true, breakLine: true } },
    { text: "DOJ settlement with Live Nation (March 2026)", options: { bullet: true } },
  ], {
    x: 0.5, y: 1.65, w: 5.8, h: 2.0,
    fontSize: 13, color: TEXT, fontFace: FONT,
    align: "left", valign: "top"
  });

  // Right column header
  slide.addText("Why it keeps failing", {
    x: 6.9, y: 1.2, w: 5.9, h: 0.4,
    fontSize: 16, bold: true, color: RED, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  // Right bullets
  slide.addText([
    { text: "Identity verification gamed through account farms and proxy buyers", options: { bullet: true, breakLine: true } },
    { text: "Dynamic pricing transfers scalper margin to Ticketmaster, not fans", options: { bullet: true, breakLine: true } },
    { text: "DOJ settlement: $280M = 4 days of Live Nation revenue. No resale cap.", options: { bullet: true, breakLine: true } },
    { text: "36 states + DC rejected the settlement. Trial continues.", options: { bullet: true } },
  ], {
    x: 6.9, y: 1.65, w: 5.9, h: 2.1,
    fontSize: 13, color: TEXT, fontFace: FONT,
    align: "left", valign: "top"
  });

  // Divider line between columns
  slide.addShape(pres.shapes.LINE, {
    x: 6.7, y: 1.2, w: 0, h: 2.6,
    line: { color: "1A2A3A", width: 2 }
  });

  // Bottom callout box — card bg with green left border
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.0, w: 12.33, h: 1.05,
    fill: { color: CARD }, line: { color: CARD, width: 0 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.0, w: 0.07, h: 1.05,
    fill: { color: GREEN }, line: { color: GREEN, width: 0 }
  });
  slide.addText("The primary market is not the failure point. Secondary market conditions determine whether primary-side measures succeed or fail.", {
    x: 0.72, y: 4.08, w: 11.9, h: 0.9,
    fontSize: 13, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle"
  });
}

// ─── SLIDE 3 ── FLOW DIAGRAM: Endowment Effect ───────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("Why Resale Reform Keeps Collapsing: The Endowment Effect", {
    x: 0.5, y: 0.25, w: 12.33, h: 0.7,
    fontSize: 30, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  // Three flow boxes
  const boxes = [
    { x: 0.5,  color: BLUE,  header: "PRE-SALE",  body: "Unified Coalition — All buyers are have-nots. Fairness consensus is strong." },
    { x: 4.67, color: AMBER, header: "PURCHASE",   body: "The Split — Winners gain a property interest. Losers intensify advocacy but lose leverage." },
    { x: 8.83, color: RED,   header: "POST-SALE",  body: "Coalition Fracture — Winners resist restrictions. The Committed Casual becomes the strongest defector." },
  ];

  boxes.forEach(b => {
    // Card bg
    slide.addShape(pres.shapes.RECTANGLE, {
      x: b.x, y: 1.1, w: 3.9, h: 2.5,
      fill: { color: CARD }, line: { color: CARD, width: 0 }
    });
    // Top color border
    slide.addShape(pres.shapes.RECTANGLE, {
      x: b.x, y: 1.1, w: 3.9, h: 0.1,
      fill: { color: b.color }, line: { color: b.color, width: 0 }
    });
    // Header
    slide.addText(b.header, {
      x: b.x + 0.15, y: 1.25, w: 3.6, h: 0.4,
      fontSize: 15, bold: true, color: b.color, fontFace: FONT,
      align: "left", valign: "middle", margin: 0
    });
    // Body
    slide.addText(b.body, {
      x: b.x + 0.15, y: 1.7, w: 3.6, h: 1.7,
      fontSize: 13, color: TEXT, fontFace: FONT,
      align: "left", valign: "top"
    });
  });

  // Arrows between boxes
  [4.4, 8.56].forEach(ax => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: ax, y: 2.25, w: 0.27, h: 0.06,
      fill: { color: TEXT }, line: { color: TEXT, width: 0 }
    });
    // Arrowhead triangle approximation via text
    slide.addText("▶", {
      x: ax + 0.2, y: 2.15, w: 0.3, h: 0.26,
      fontSize: 16, color: TEXT, fontFace: FONT, align: "left", margin: 0
    });
  });

  // Below diagram caption
  slide.addText([
    { text: "Standard Rawlsian analysis misses this. Nash equilibrium assumes fixed preferences — but preferences shift the moment a ticket changes hands.", options: { breakLine: true } },
    { text: "The Golden Rule Equilibrium asks: would you accept these rules not knowing which role you'd occupy — AND after you know?", options: {} },
  ], {
    x: 0.5, y: 4.0, w: 12.33, h: 0.9,
    fontSize: 12, color: MUTED, fontFace: FONT,
    align: "left", valign: "top", italic: false
  });
}

// ─── SLIDE 4 ── TWO COLUMN: GRE Explained ────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("The Golden Rule Equilibrium: A Harder Test", {
    x: 0.5, y: 0.25, w: 12.33, h: 0.7,
    fontSize: 34, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  // Intro text
  slide.addText("The GRE scores each ruleset on whether participants would accept it regardless of role. Three lenses:", {
    x: 0.5, y: 1.1, w: 7.7, h: 0.6,
    fontSize: 13, color: TEXT, fontFace: FONT,
    align: "left", valign: "top"
  });

  // Three items with colored labels
  const lenses = [
    { label: "Fan Fairness:", labelColor: GREEN, desc: "Measures access, price equity, and attendance outcomes for fans only" },
    { label: "Population-Weighted:", labelColor: BLUE, desc: "Weights all market participants by population share" },
    { label: "System (Equal Weight):", labelColor: AMBER, desc: "Equal weight to all roles including scalpers" },
  ];
  lenses.forEach((l, i) => {
    slide.addText([
      { text: l.label + " ", options: { bold: true, color: l.labelColor } },
      { text: l.desc, options: { color: TEXT } },
    ], {
      x: 0.5, y: 1.85 + i * 0.62, w: 7.7, h: 0.5,
      fontSize: 13, fontFace: FONT, align: "left", valign: "top"
    });
  });

  // Right card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.7, y: 1.05, w: 4.1, h: 3.2,
    fill: { color: CARD }, line: { color: CARD, width: 0 }
  });
  slide.addText("GR Score Formula", {
    x: 8.9, y: 1.2, w: 3.7, h: 0.35,
    fontSize: 11, color: MUTED, fontFace: FONT, align: "left", valign: "middle", margin: 0
  });
  slide.addText([
    { text: "GR Score =", options: { breakLine: true } },
    { text: "Floor × 0.4", options: { breakLine: true } },
    { text: "+ Equality × 0.3", options: { breakLine: true } },
    { text: "+ Average × 0.2", options: { breakLine: true } },
    { text: "+ Baseline × 0.1", options: {} },
  ], {
    x: 8.9, y: 1.65, w: 3.7, h: 2.3,
    fontSize: 13, color: GREEN, fontFace: "Courier New",
    align: "left", valign: "top"
  });

  // Bottom note
  slide.addText("Validation precedent: Milgrom & Wilson (2020 Nobel) used simulation → theory → deployment for spectrum auction design. Same methodology.", {
    x: 0.5, y: 4.55, w: 12.33, h: 0.55,
    fontSize: 11, color: MUTED, fontFace: FONT, align: "left", valign: "top"
  });
}

// ─── SLIDE 5 ── TABLE: Four Regimes ──────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("Four Regimes Tested Across 10 Demand Levels, 30 Runs Each", {
    x: 0.5, y: 0.25, w: 12.33, h: 0.7,
    fontSize: 32, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  const headerOpts = { fill: { color: "1E3A52" }, color: TEXT, bold: true, fontFace: FONT, fontSize: 13, align: "center", valign: "middle" };
  const row1Opts   = { fill: { color: "131F2B" }, color: TEXT, fontFace: FONT, fontSize: 13, align: "left", valign: "middle" };
  const row2Opts   = { fill: { color: "0F1923" }, color: TEXT, fontFace: FONT, fontSize: 13, align: "left", valign: "middle" };
  const row3Opts   = { fill: { color: "131F2B" }, color: TEXT, fontFace: FONT, fontSize: 13, align: "left", valign: "middle" };
  const row4Opts   = { fill: { color: "1A3A2A" }, color: GREEN, bold: true, fontFace: FONT, fontSize: 13, align: "left", valign: "middle" };

  const tableData = [
    [
      { text: "Regime",         options: { ...headerOpts, align: "left" } },
      { text: "Cap",            options: headerOpts },
      { text: "Purchase Limit", options: headerOpts },
      { text: "Enforcement",    options: headerOpts },
    ],
    [
      { text: "Status Quo",     options: { ...row1Opts, align: "left" } },
      { text: "None",           options: row1Opts },
      { text: "8 tickets",      options: row1Opts },
      { text: "None",           options: row1Opts },
    ],
    [
      { text: "Dynamic Pricing",options: { ...row2Opts, align: "left" } },
      { text: "None (2.2× primary price)", options: row2Opts },
      { text: "6 tickets",      options: row2Opts },
      { text: "None",           options: row2Opts },
    ],
    [
      { text: "UK Face Value",  options: { ...row3Opts, align: "left" } },
      { text: "0%",             options: row3Opts },
      { text: "2 tickets",      options: row3Opts },
      { text: "Identity registry", options: row3Opts },
    ],
    [
      { text: "Bounded Market", options: { ...row4Opts, align: "left" } },
      { text: "5–50% tested (20–25% optimal)", options: row4Opts },
      { text: "4 tickets",      options: row4Opts },
      { text: "Identity registry + non-transferable barcodes", options: row4Opts },
    ],
  ];

  slide.addTable(tableData, {
    x: 0.5, y: 1.1, w: 12.33, h: 3.5,
    rowH: [0.55, 0.65, 0.65, 0.65, 0.7],
    border: { pt: 1, color: "1A2A3A" },
    colW: [2.8, 2.8, 2.0, 4.73],
  });

  slide.addText("Demand multiplier: 1× = venue sells out at face value. 10× = demand is 10× supply. Real-world hot events: 3–8×.", {
    x: 0.5, y: 4.85, w: 12.33, h: 0.4,
    fontSize: 12, color: MUTED, fontFace: FONT, align: "left", valign: "middle"
  });
}

// ─── SLIDE 6 ── CHART: Ruleset Comparison ────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("Bounded Market Outperforms Every Alternative at High Demand", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.75,
    fontSize: 30, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  slide.addImage({
    path: "/Users/patricktyler/PycharmProjects/Ticket Fairness/chart1_ruleset_comparison.png",
    x: 1.16, y: 1.3, w: 11, h: 5
  });

  slide.addText("Population-Weighted GR Score across demand levels. Bounded 20–25% consistently outperforms Status Quo, Dynamic Pricing, and UK Face Value at demand ≥ 1.5×. Source: GRE simulation, 30 runs per data point.", {
    x: 0.5, y: 6.5, w: 12.33, h: 0.6,
    fontSize: 10, color: MUTED, fontFace: FONT, align: "left", valign: "top"
  });
}

// ─── SLIDE 7 ── CHART: Cap Heatmap ───────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("The 20–25% Band Is Robust Across All Demand Conditions", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.75,
    fontSize: 30, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  slide.addImage({
    path: "/Users/patricktyler/PycharmProjects/Ticket Fairness/chart2_cap_heatmap.png",
    x: 1.16, y: 1.3, w: 11, h: 4.8
  });

  slide.addText("GR Score by cap level and demand multiplier. Stars mark the optimal cap at each demand level. The 20–25% band is within 0.01–0.02 GR of optimal at every demand level — the right shape for a policy rule.", {
    x: 0.5, y: 6.35, w: 12.33, h: 0.7,
    fontSize: 10, color: MUTED, fontFace: FONT, align: "left", valign: "top"
  });
}

// ─── SLIDE 8 ── CHART: Dark Market ───────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("Why 0% and 10% Caps Fail: They Create Dark Markets", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.75,
    fontSize: 30, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  slide.addImage({
    path: "/Users/patricktyler/PycharmProjects/Ticket Fairness/chart3_dark_market.png",
    x: 1.16, y: 1.3, w: 11, h: 5
  });

  slide.addText("Dark market tickets by cap level. Tight caps (0–10%) create strong dark market incentive. At 20–25%, leakage collapses. Confirmed: Ireland (0%) and Victoria AU (10%) show 3.6× higher fraud rates than uncapped UK. Source: GRE simulation + Bradshaw Advisory (June 2025, commissioned by StubHub).", {
    x: 0.5, y: 6.5, w: 12.33, h: 0.6,
    fontSize: 10, color: MUTED, fontFace: FONT, align: "left", valign: "top"
  });
}

// ─── SLIDE 9 ── CHART: Lens Convergence ──────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("All Three Fairness Lenses Agree: 20–25% Is the Sweet Spot", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.75,
    fontSize: 30, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  slide.addImage({
    path: "/Users/patricktyler/PycharmProjects/Ticket Fairness/chart4_lens_convergence.png",
    x: 1.16, y: 1.3, w: 11, h: 5
  });

  slide.addText("At demand 5×, Population-Weighted and System lenses converge on 20–25%. Fan lens 0% result is a documented scope artifact — noted as a limitation, not a finding.", {
    x: 0.5, y: 6.5, w: 12.33, h: 0.6,
    fontSize: 10, color: MUTED, fontFace: FONT, align: "left", valign: "top"
  });
}

// ─── SLIDE 10 ── CHART: Sensitivity ──────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("The Policy Recommendation Is Robust", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.75,
    fontSize: 34, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  slide.addImage({
    path: "/Users/patricktyler/PycharmProjects/Ticket Fairness/chart5_sensitivity.png",
    x: 1.16, y: 1.3, w: 11, h: 5
  });

  slide.addText("29 parameters × ±40% perturbation × 4 rulesets × 4 demand levels × 20 runs. No parameter variation moves the optimum out of the Bounded regime. Dark market parameters rank LOW — policy does not depend on precise fraud-rate estimates.", {
    x: 0.5, y: 6.5, w: 12.33, h: 0.6,
    fontSize: 10, color: MUTED, fontFace: FONT, align: "left", valign: "top"
  });
}

// ─── SLIDE 11 ── THREE COLUMN: Empirical Validation ──────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("Empirical Anchors: What the Real World Confirms", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.7,
    fontSize: 30, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  const cols = [
    {
      x: 0.5, color: RED,
      header: "0% & 10% Caps — The Evidence",
      bullets: [
        "Ireland (0% cap, 2021): 13.6% fraud rate. Zero prosecutions.",
        "Victoria AU (10% cap): 13.7% fraud rate. Circumvented via bundling.",
        "EU DSA 2025: 275 illegal listings flagged. Platform takedown compliance: 0%.",
        "3.6× higher fraud in capped vs uncapped markets (Bradshaw/StubHub, 2025)",
      ]
    },
    {
      x: 4.5, color: BLUE,
      header: "Market Structure",
      bullets: [
        "Top 10% of resellers = 70% of volume (UK Gov)",
        "80% of platform volume = professional touts (UK Gov)",
        "62% of events: resale below face value — scalpers absorb demand risk",
        "~33% secondary price decay confirms our 3-round markdown model",
      ]
    },
    {
      x: 8.5, color: GREEN,
      header: "The Bounded Market Logic",
      bullets: [
        "Enforcement (ID registry + non-transferable barcodes) is load-bearing",
        "Cap must be high enough to keep scalpers on regulated platform",
        "Scalpers provide real liquidity: risk absorption, price discovery",
        "20–25% = profitable for individual resale, unprofitable for bulk speculation",
      ]
    },
  ];

  cols.forEach(c => {
    // Card bg
    slide.addShape(pres.shapes.RECTANGLE, {
      x: c.x, y: 1.0, w: 3.8, h: 5.3,
      fill: { color: CARD }, line: { color: CARD, width: 0 }
    });
    // Top border
    slide.addShape(pres.shapes.RECTANGLE, {
      x: c.x, y: 1.0, w: 3.8, h: 0.1,
      fill: { color: c.color }, line: { color: c.color, width: 0 }
    });
    // Header
    slide.addText(c.header, {
      x: c.x + 0.15, y: 1.15, w: 3.5, h: 0.55,
      fontSize: 13, bold: true, color: c.color, fontFace: FONT,
      align: "left", valign: "top"
    });
    // Bullets
    slide.addText(c.bullets.map((b, i) => ({
      text: b,
      options: { bullet: true, breakLine: i < c.bullets.length - 1 }
    })), {
      x: c.x + 0.1, y: 1.8, w: 3.6, h: 4.2,
      fontSize: 12, color: TEXT, fontFace: FONT,
      align: "left", valign: "top"
    });
  });
}

// ─── SLIDE 12 ── TWO COLUMN: Scalper as Ecological Actor ─────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("Scalpers Are Ecological Actors — Not the Problem", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.7,
    fontSize: 32, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  // Left column body text
  slide.addText("Professional resellers fulfill a legitimate market function:", {
    x: 0.5, y: 1.1, w: 7.7, h: 0.4,
    fontSize: 13, color: TEXT, fontFace: FONT, align: "left", valign: "top"
  });

  slide.addText([
    { text: "Risk absorption: 62% of events, scalpers buy at face value and sell at a loss", options: { bullet: true, breakLine: true } },
    { text: "Liquidity: fans who can't attend can exit; fans who decide late can enter", options: { bullet: true, breakLine: true } },
    { text: "Price discovery: secondary prices signal true demand to artists and venues", options: { bullet: true } },
  ], {
    x: 0.5, y: 1.6, w: 7.7, h: 1.3,
    fontSize: 13, color: TEXT, fontFace: FONT, align: "left", valign: "top"
  });

  slide.addText("The question is optimal predator-to-prey ratio, not elimination.", {
    x: 0.5, y: 3.05, w: 7.7, h: 0.4,
    fontSize: 13, color: TEXT, fontFace: FONT, align: "left", valign: "top", italic: true
  });

  slide.addText("This is why the NATB (National Association of Ticket Brokers) is a natural coalition partner. A transparent, capped, legal secondary market benefits legitimate resellers over the current environment where bots, dark markets, and Ticketmaster's own resale platform crowd them out.", {
    x: 0.5, y: 3.55, w: 7.7, h: 1.3,
    fontSize: 13, color: TEXT, fontFace: FONT, align: "left", valign: "top"
  });

  // Right card with green left border
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.7, y: 1.0, w: 4.1, h: 4.0,
    fill: { color: CARD }, line: { color: CARD, width: 0 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 8.7, y: 1.0, w: 0.07, h: 4.0,
    fill: { color: GREEN }, line: { color: GREEN, width: 0 }
  });
  slide.addText("The Bounded Market offers:", {
    x: 8.85, y: 1.15, w: 3.7, h: 0.45,
    fontSize: 14, bold: true, color: GREEN, fontFace: FONT, align: "left", valign: "middle", margin: 0
  });
  slide.addText([
    { text: "✓ Legal certainty for resellers", options: { breakLine: true } },
    { text: "✓ A level playing field vs. bots", options: { breakLine: true } },
    { text: "✓ 20–25% margin = viable business", options: { breakLine: true } },
    { text: "✓ Regulated platform preferred over dark market risk", options: {} },
  ], {
    x: 8.85, y: 1.7, w: 3.7, h: 2.5,
    fontSize: 13, color: TEXT, fontFace: FONT, align: "left", valign: "top"
  });
}

// ─── SLIDE 13 ── TWO COLUMN: The Product ─────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("From Simulation to System: The Bounded Market Platform", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.7,
    fontSize: 30, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  // Left column
  slide.addText("What It Does", {
    x: 0.5, y: 1.1, w: 6.3, h: 0.45,
    fontSize: 16, bold: true, color: BLUE, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  slide.addText([
    { text: "Identity-linked ticket issuance and transfer recording", options: { bullet: true, breakLine: true } },
    { text: "Real-time cap enforcement on secondary listings (20–25% above face value)", options: { bullet: true, breakLine: true } },
    { text: "Dark market displacement monitoring and flagging", options: { bullet: true, breakLine: true } },
    { text: "Compliance reporting for venues and regulators", options: { bullet: true, breakLine: true } },
    { text: "Open API: connects to existing primary ticketing infrastructure", options: { bullet: true } },
  ], {
    x: 0.5, y: 1.65, w: 6.3, h: 3.5,
    fontSize: 13, color: TEXT, fontFace: FONT, align: "left", valign: "top"
  });

  // Right column
  slide.addText("Who It Serves", {
    x: 7.3, y: 1.1, w: 5.5, h: 0.45,
    fontSize: 16, bold: true, color: GREEN, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  const serves = [
    { label: "Regulators:", desc: "Enforcement infrastructure + empirical data to justify cap legislation" },
    { label: "Venues/Promoters:", desc: "Compliance SaaS — reduce reputational and legal risk" },
    { label: "NATB/Resellers:", desc: "Legal, transparent platform; level playing field vs. bots" },
    { label: "Fans:", desc: "Higher probability of face-value access; dark market fraud eliminated" },
  ];

  serves.forEach((s, i) => {
    slide.addText([
      { text: s.label + " ", options: { bold: true, color: MUTED } },
      { text: s.desc, options: { color: TEXT } },
    ], {
      x: 7.3, y: 1.65 + i * 0.75, w: 5.5, h: 0.65,
      fontSize: 13, fontFace: FONT, align: "left", valign: "top"
    });
  });
}

// ─── SLIDE 14 ── THREE PHASE: Go-to-Market ───────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("Phased Coalition-Building Strategy", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.7,
    fontSize: 34, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  const phases = [
    {
      x: 0.5, num: "01", numColor: BLUE, borderColor: BLUE,
      header: "Venue Pilots",
      bullets: ["2–3 mid-size venue partners", "Generate real compliance + leakage data", "Validate simulation predictions"]
    },
    {
      x: 4.67, num: "02", numColor: AMBER, borderColor: AMBER,
      header: "NATB Partnership",
      bullets: ["Reseller buy-in and industry legitimacy", "Platform as the legal alternative to dark markets", "NATB members benefit from bot-free, rule-enforced competition"]
    },
    {
      x: 8.83, num: "03", numColor: GREEN, borderColor: GREEN,
      header: "Regulatory Engagement",
      bullets: ["Pilot data + simulation + policy brief", "36-state AG coalition as primary audience", "DOJ consent decree as forcing function"]
    },
  ];

  phases.forEach(p => {
    // Card bg
    slide.addShape(pres.shapes.RECTANGLE, {
      x: p.x, y: 1.05, w: 3.9, h: 4.6,
      fill: { color: CARD }, line: { color: p.borderColor, width: 2 }
    });
    // Phase number
    slide.addText(p.num, {
      x: p.x + 0.2, y: 1.2, w: 1.5, h: 0.75,
      fontSize: 28, bold: true, color: p.numColor, fontFace: FONT,
      align: "left", valign: "middle", margin: 0
    });
    // Phase header
    slide.addText(p.header, {
      x: p.x + 0.2, y: 2.0, w: 3.5, h: 0.45,
      fontSize: 16, bold: true, color: p.numColor, fontFace: FONT,
      align: "left", valign: "middle", margin: 0
    });
    // Bullets
    slide.addText(p.bullets.map((b, i) => ({
      text: b,
      options: { bullet: true, breakLine: i < p.bullets.length - 1 }
    })), {
      x: p.x + 0.15, y: 2.55, w: 3.6, h: 2.8,
      fontSize: 13, color: TEXT, fontFace: FONT, align: "left", valign: "top"
    });
  });

  slide.addText("The DOJ settlement's open-platform requirement creates the infrastructure. Adding a resale price cap closes the loop. We are the cap enforcement layer.", {
    x: 0.5, y: 5.9, w: 12.33, h: 0.6,
    fontSize: 11, color: MUTED, fontFace: FONT, align: "left", valign: "middle"
  });
}

// ─── SLIDE 15 ── WHY NOW ──────────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  slide.addText("The Window Is Open", {
    x: 0.5, y: 0.2, w: 12.33, h: 0.7,
    fontSize: 36, bold: true, color: TEXT, fontFace: FONT,
    align: "left", valign: "middle", margin: 0
  });

  const items = [
    "36 states + DC rejected the DOJ settlement. Trial continues. They need analytical tools.",
    "UK enacted face-value ban (Nov 2025) — but our data shows 0% is the wrong number.",
    "EU Digital Services Act enforcement is failing (0% takedown rate). Credible alternatives needed.",
    "Live Nation DOJ open-platform requirement creates the infrastructure gap we fill.",
    "Post-Eras Tour political will is the highest it has been in 20 years.",
  ];
  const dotColors = [BLUE, GREEN, RED, AMBER, GREEN];

  items.forEach((item, i) => {
    // Colored dot
    slide.addShape(pres.shapes.OVAL, {
      x: 0.5, y: 1.2 + i * 0.72 + 0.13, w: 0.18, h: 0.18,
      fill: { color: dotColors[i] }, line: { color: dotColors[i], width: 0 }
    });
    slide.addText(item, {
      x: 0.85, y: 1.2 + i * 0.72, w: 11.98, h: 0.62,
      fontSize: 14, color: TEXT, fontFace: FONT, align: "left", valign: "middle"
    });
  });

  // Bottom callout box — amber left border
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.9, w: 12.33, h: 1.15,
    fill: { color: CARD }, line: { color: CARD, width: 0 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.9, w: 0.07, h: 1.15,
    fill: { color: AMBER }, line: { color: AMBER, width: 0 }
  });
  slide.addText("The UK chose 0%. Our simulation and the empirical record show 20–25% works better. The data exists. The coalition exists. The enforcement gap exists.", {
    x: 0.72, y: 4.98, w: 11.9, h: 0.99,
    fontSize: 13, color: TEXT, fontFace: FONT, align: "left", valign: "middle"
  });
}

// ─── SLIDE 16 ── CLOSING ──────────────────────────────────────────────────────
{
  const slide = pres.addSlide();
  slide.background = { color: BG };

  // Subtle background circles
  slide.addShape(pres.shapes.OVAL, {
    x: -2, y: -2, w: 8, h: 8,
    fill: { color: "1A2A3A", transparency: 50 },
    line: { color: "1A2A3A", width: 0 }
  });
  slide.addShape(pres.shapes.OVAL, {
    x: 9, y: 3, w: 6, h: 6,
    fill: { color: "7ECBA1", transparency: 90 },
    line: { color: "7ECBA1", width: 0 }
  });

  // Quote
  slide.addText('"Would you accept these rules not knowing which role you\'d occupy?"', {
    x: 1, y: 1.6, w: 11.33, h: 1.8,
    fontSize: 28, color: TEXT, fontFace: FONT,
    align: "center", valign: "middle", italic: true
  });

  // Tagline
  slide.addText("The Bounded Market is the only tested regime that passes.", {
    x: 1, y: 3.6, w: 11.33, h: 0.7,
    fontSize: 18, bold: true, color: GREEN, fontFace: FONT,
    align: "center", valign: "middle"
  });

  // Bottom left
  slide.addText("[Contact / Next Steps]", {
    x: 0.5, y: 6.8, w: 5, h: 0.4,
    fontSize: 11, color: MUTED, fontFace: FONT, align: "left", valign: "middle"
  });

  // Bottom right
  slide.addText("GRE Simulation  |  Python  |  30 runs × 10 demand levels × 12 rulesets", {
    x: 6.5, y: 6.8, w: 6.33, h: 0.4,
    fontSize: 11, color: MUTED, fontFace: FONT, align: "right", valign: "middle"
  });
}

// ─── WRITE FILE ───────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "/Users/patricktyler/PycharmProjects/Ticket Fairness/GRE-pitch-deck.pptx" })
  .then(() => console.log("Done: GRE-pitch-deck.pptx"))
  .catch(err => { console.error(err); process.exit(1); });
