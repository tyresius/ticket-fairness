#!/usr/bin/env python3
"""
TF4 (2026-07-05): append two slides to GRE-pitch-deck.pptx —
  A) "The UK Is About to Test This" — chart9 UK-2026 comparison + takeaways
  B) "Robust Under Joint Uncertainty" — chart7 (global PRCC) + chart8
     (optimal-cap distribution), the June leftover.
Appended at the end; no existing slide is modified.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

BG      = RGBColor(0x0F, 0x19, 0x23)
TITLE_C = RGBColor(0xE8, 0xF0, 0xF8)
BODY_C  = RGBColor(0xC8, 0xD8, 0xE8)
FOOT_C  = RGBColor(0x8A, 0xA0, 0xB0)
AMBER   = RGBColor(0xF4, 0xD0, 0x3F)
PURPLE  = RGBColor(0x9B, 0x59, 0xB6)
GREEN   = RGBColor(0x7E, 0xCB, 0xA1)

W, H = Inches(13.333), Inches(7.5)


def blank_slide(pres):
    # pptxgenjs decks ship a minimal layout set — use the last available
    # (full-bleed BG rect below covers whatever the layout contains).
    slide = pres.slides.add_slide(pres.slide_layouts[len(pres.slide_layouts) - 1])
    bg = slide.shapes.add_shape(1, 0, 0, W, H)
    bg.fill.solid(); bg.fill.fore_color.rgb = BG
    bg.line.fill.background()
    bg.shadow.inherit = False
    return slide


def text(slide, left, top, width, height, paras):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = True
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = p.get("align", PP_ALIGN.LEFT)
        if "space_before" in p:
            para.space_before = Pt(p["space_before"])
        run = para.add_run()
        run.text = p["text"]
        run.font.size = Pt(p.get("size", 12))
        run.font.bold = p.get("bold", False)
        run.font.color.rgb = p.get("color", BODY_C)
    return txb


pres = Presentation("GRE-pitch-deck.pptx")

# ── Slide A: the UK policy hook ──────────────────────────────────────────────
s = blank_slide(pres)
text(s, Inches(0.6), Inches(0.35), Inches(12.1), Inches(0.9), [
    dict(text="The UK Is About to Test This — With the Ceiling Set Wrong",
         size=28, bold=True, color=TITLE_C),
    dict(text="Draft Ticket Tout Ban Bill (King's Speech, May 2026): resale capped at face value, platform fees capped — in pre-legislative scrutiny now",
         size=13, color=FOOT_C, space_before=4),
])
s.shapes.add_picture("chart9_uk2026.png", Inches(0.6), Inches(1.55),
                     width=Inches(7.9))
text(s, Inches(8.8), Inches(1.75), Inches(4.0), Inches(4.8), [
    dict(text="What the simulation says:", size=15, bold=True, color=TITLE_C),
    dict(text="✓  The fee cap is good policy — worth ~+0.04 welfare on its own",
         size=13, color=GREEN, space_before=10),
    dict(text="✗  But at a 0% ceiling, legal resale stays throttled and dark-market "
              "routing is untouched (it's driven by the price gap, not fees)",
         size=13, color=PURPLE, space_before=10),
    dict(text="→  The same fee cap with a ~20% ceiling delivers two to three "
              "times the welfare gain — the levers are super-additive",
         size=13, bold=True, color=AMBER, space_before=10),
    dict(text="Under capped fees the defensible ceiling band shifts to 10–20%, "
              "exactly as the break-even mechanism predicts.",
         size=12, color=BODY_C, space_before=14),
    dict(text="Keep the fee cap. Fix the ceiling.", size=16, bold=True,
         color=TITLE_C, space_before=18),
])
text(s, Inches(0.6), Inches(7.05), Inches(12.1), Inches(0.35), [
    dict(text="Sources: UK Gov consultation response (Nov 2025); Commons Library SN04715 (Jan 2026); GRE cap sweep, 16 rulesets × 10 demand levels × 100 seeded runs",
         size=9, color=FOOT_C),
])

# ── Slide B: joint-uncertainty robustness (June leftover) ────────────────────
s = blank_slide(pres)
text(s, Inches(0.6), Inches(0.35), Inches(12.1), Inches(0.9), [
    dict(text="Robust Under Joint Uncertainty", size=28, bold=True, color=TITLE_C),
    dict(text="Latin-hypercube sampling: all 33 parameters perturbed simultaneously across their full ranges (N=400 joint draws)",
         size=13, color=FOOT_C, space_before=4),
])
s.shapes.add_picture("chart7_global_prcc.png", Inches(0.55), Inches(1.6),
                     width=Inches(6.2))
s.shapes.add_picture("chart8_optimal_cap_dist.png", Inches(6.95), Inches(2.35),
                     width=Inches(6.2))
text(s, Inches(0.6), Inches(6.35), Inches(12.1), Inches(0.9), [
    dict(text="Bounded market beats Status Quo in 99.0% (PopWt) / 96.5% (System) of joint draws; "
              "the optimal cap stays in the 20–30% band in ~99% of PopWt/System draws.",
         size=14, bold=True, color=AMBER),
    dict(text="Fan lens prefers 10% — the accepted price-minimizer divergence (see limitations slide). "
              "No single parameter, including every unsourced dark-market placeholder, can be tuned to reverse the conclusion.",
         size=12, color=BODY_C, space_before=6),
])

pres.save("GRE-pitch-deck.pptx")
print(f"Deck now has {len(pres.slides.slides._sldIdLst)} slides"
      if hasattr(pres.slides, 'slides') else
      f"Deck saved with {len(pres.slides._sldIdLst)} slides")
