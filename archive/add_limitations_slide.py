"""
Add limitations slide (B2) to GRE-pitch-deck.pptx.

Inserts after slide 11 (Empirical Anchors), before slide 12 (Scalpers).
Three-column layout matching slide 11 styling.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import copy
from lxml import etree

BG       = RGBColor(0x0F, 0x19, 0x23)
TITLE_C  = RGBColor(0xE8, 0xF0, 0xF8)
BODY_C   = RGBColor(0xE8, 0xF0, 0xF8)
FOOT_C   = RGBColor(0x8A, 0xA0, 0xB0)
CARD_BG  = RGBColor(0x16, 0x26, 0x33)

COL1_HDR = RGBColor(0xE0, 0x5C, 0x5C)   # red  — structural scope
COL2_HDR = RGBColor(0x5B, 0xA4, 0xCF)   # blue — enforcement
COL3_HDR = RGBColor(0x7E, 0xCB, 0xA1)   # green — framework divergence


def add_textbox(slide, left, top, width, height, paras,
                default_size=12, default_color=BODY_C, default_bold=False,
                word_wrap=True, v_anchor=None):
    """
    Add a textbox. `paras` is a list of dicts:
      text, size, color, bold, align, space_before
    """
    from pptx.util import Pt
    from pptx.enum.text import PP_ALIGN
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = word_wrap
    if v_anchor:
        tf.vertical_anchor = v_anchor

    for idx, p in enumerate(paras):
        para = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        para.alignment = p.get("align", PP_ALIGN.LEFT)
        if "space_before" in p:
            para.space_before = Pt(p["space_before"])
        run = para.add_run()
        run.text = p["text"]
        run.font.size  = Pt(p.get("size",  default_size))
        run.font.bold  = p.get("bold",  default_bold)
        run.font.color.rgb = p.get("color", default_color)
    return txb


def add_filled_rect(slide, left, top, width, height, fill_color):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape


prs = Presentation("GRE-pitch-deck.pptx")
W = prs.slide_width
H = prs.slide_height

# ── Add blank slide after slide 11 (index 11) ────────────────────────────────
blank_layout = prs.slide_layouts[0]  # only layout available
new_slide    = prs.slides.add_slide(blank_layout)

# Move it to position 12 (0-indexed: 11) — after "Empirical Anchors"
xml_slides = prs.slides._sldIdLst
# The newly added slide is last; move it to index 11 (after slide 11)
last = xml_slides[-1]
xml_slides.remove(last)
xml_slides.insert(11, last)

slide = prs.slides[11]  # now the new slide

# ── Background ────────────────────────────────────────────────────────────────
bg = slide.background
bg.fill.solid()
bg.fill.fore_color.rgb = BG

# ── Title ─────────────────────────────────────────────────────────────────────
add_textbox(slide,
    left=Inches(0.50), top=Inches(0.18), width=Inches(12.33), height=Inches(0.72),
    paras=[dict(text="Model Scope & Limitations", size=30, bold=True, color=TITLE_C)],
)

# ── Column layout constants ───────────────────────────────────────────────────
COL_W    = Inches(3.80)
COL_TOP  = Inches(1.00)
COL_H    = Inches(5.40)
BAR_H    = Inches(0.10)
HDR_H    = Inches(0.52)
BODY_TOP = Inches(1.75)
BODY_H   = Inches(4.55)
COLS     = [Inches(0.50), Inches(4.50), Inches(8.50)]

# ── Column 1: Structural Scope ────────────────────────────────────────────────
add_filled_rect(slide, COLS[0], COL_TOP, COL_W, COL_H, CARD_BG)
add_filled_rect(slide, COLS[0], COL_TOP, COL_W, BAR_H, COL1_HDR)

add_textbox(slide,
    left=COLS[0]+Inches(0.15), top=COL_TOP+Inches(0.13),
    width=COL_W-Inches(0.15), height=HDR_H,
    paras=[dict(text="Structural Scope", size=13, bold=True, color=COL1_HDR)],
)

col1_body = [
    dict(text="Single-queue primary sale — real markets run Verified Fan, artist and fan-club presales, and venue holds that place 54%+ of inventory before the public on-sale. Effective primary supply and scalper competition are both underestimated.", size=11),
    dict(text="", size=6),
    dict(text="No fee modeling — Ticketmaster buyer fees (20–30%) and secondary platform fees (10–15%) affect true access cost, price gaps, and dark-market economics. Modeled prices are face-value net.", size=11),
    dict(text="", size=6),
    dict(text="Synthetic population — 80 mega-fans / 150 committed casuals / 200 average buyers / 30 scalpers per 500-seat venue. Calibrated from CMA/PTR data but not event-specific.", size=11),
    dict(text="", size=6),
    dict(text="Single event, single period — no repeat play, reputation effects, or cross-event learning by scalpers or fans.", size=11),
]
add_textbox(slide,
    left=COLS[0]+Inches(0.12), top=BODY_TOP, width=COL_W-Inches(0.15), height=BODY_H,
    paras=col1_body, default_size=11, default_color=BODY_C,
)

# ── Column 2: Enforcement Dependency ─────────────────────────────────────────
add_filled_rect(slide, COLS[1], COL_TOP, COL_W, COL_H, CARD_BG)
add_filled_rect(slide, COLS[1], COL_TOP, COL_W, BAR_H, COL2_HDR)

add_textbox(slide,
    left=COLS[1]+Inches(0.15), top=COL_TOP+Inches(0.13),
    width=COL_W-Inches(0.15), height=HDR_H,
    paras=[dict(text="Enforcement Dependency", size=13, bold=True, color=COL2_HDR)],
)

col2_body = [
    dict(text="Baseline assumes full enforcement — identity registry + non-transferable barcodes. Real-world FEAT data shows ~0% compliance with existing resale laws.", size=11),
    dict(text="", size=6),
    dict(text="Enforcement sweep finding — Bounded 25% beats Status Quo on 9 of 10 demand levels even with no enforcement. The advantage is structural, not enforcement-dependent.", size=11, color=RGBColor(0x7E, 0xCB, 0xA1)),
    dict(text="", size=6),
    dict(text="Fan GR lens flips negative at extreme demand (10×) without enforcement — scalper dark-market routing takes enough tickets that fans net worse than Status Quo on the fan-only measure.", size=11),
    dict(text="", size=6),
    dict(text="Practical implication — enforcement tightens the optimal cap (20% vs 25–30%) and is necessary to sustain the fan-only advantage at extreme scarcity.", size=11),
]
add_textbox(slide,
    left=COLS[1]+Inches(0.12), top=BODY_TOP, width=COL_W-Inches(0.15), height=BODY_H,
    paras=col2_body, default_size=11, default_color=BODY_C,
)

# ── Column 3: Welfare Framework Divergence ───────────────────────────────────
add_filled_rect(slide, COLS[2], COL_TOP, COL_W, COL_H, CARD_BG)
add_filled_rect(slide, COLS[2], COL_TOP, COL_W, BAR_H, COL3_HDR)

add_textbox(slide,
    left=COLS[2]+Inches(0.15), top=COL_TOP+Inches(0.13),
    width=COL_W-Inches(0.15), height=HDR_H,
    paras=[dict(text="When Frameworks Disagree", size=13, bold=True, color=COL3_HDR)],
)

col3_body = [
    dict(text="Harsanyi utilitarianism agrees with GRE ordinal rankings at every demand level — both prefer the same bounded cap. Strong convergent validity for the scoring formula.", size=11, color=RGBColor(0x7E, 0xCB, 0xA1)),
    dict(text="", size=6),
    dict(text="Rawlsian maximin diverges at demand ≥ 4× — the maximin criterion (maximize the worst-off position) prefers face-value caps (0%) because scalper exit raises average buyer hit rates in the primary queue.", size=11),
    dict(text="", size=6),
    dict(text="The divergence maps a real policy choice:", size=11),
    dict(text="  Rawls → prioritize worst-off fan → 0% cap (UK model)", size=11),
    dict(text="  GRE / Harsanyi → system-wide fairness → 10–20% cap", size=11),
    dict(text="", size=6),
    dict(text="Both agree the bounded market beats Status Quo and Dynamic Pricing — the disagreement is only about how tight the cap should be.", size=11, color=RGBColor(0xF4, 0xD0, 0x3F)),
]
add_textbox(slide,
    left=COLS[2]+Inches(0.12), top=BODY_TOP, width=COL_W-Inches(0.15), height=BODY_H,
    paras=col3_body, default_size=11, default_color=BODY_C,
)

# ── Footer ────────────────────────────────────────────────────────────────────
add_textbox(slide,
    left=Inches(0.50), top=Inches(6.55), width=Inches(12.33), height=Inches(0.55),
    paras=[dict(
        text="These limitations are inputs to a research agenda, not objections to the core finding. "
             "Pareto dominance of bounded caps over Dynamic Pricing holds across all agent types and demand "
             "levels — a claim that requires no welfare weights and survives all scope conditions above.",
        size=10, color=FOOT_C,
    )],
)

# ── Save ──────────────────────────────────────────────────────────────────────
prs.save("GRE-pitch-deck.pptx")
print("Saved. Slide count:", len(prs.slides))
print("Slide 12 title check:")
slide_check = prs.slides[11]
for shape in slide_check.shapes:
    if shape.has_text_frame and shape.text.strip():
        print(" ", shape.text.strip()[:80])
        break
