"""Build docs/slides/plan_b_slide.pptx — single Plan B detail slide (16:9)."""
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
slide = prs.slides.add_slide(prs.slide_layouts[5])  # title only

title = slide.shapes.title
title.text = "Plan B: small-fit firmware (fits stock ESP32-DevKitC)"
title.text_frame.paragraphs[0].runs[0].font.size = Pt(32)

bullets = [
    "Why: full 12-stage pipeline needs headroom; Plan B reuses the same common/ DSP math as thin combos fitting 520 KB SRAM / ~100 KB MicroPython heap.",
    "Fit build b7_fit (entry fit_main.py): 100 Hz polling loop, no Timer ISR; 4 IMUs via TCA9548A \u2014 ch0 wrist drives PLL live, ch1\u20133 round-robin (~33 Hz) for coherence logging.",
    "Per sample: gravity-strip \u2192 dominant-axis projection \u2192 IIR bandpass 3\u201312 Hz \u2192 software PLL (lock ~50 samples) \u2192 15 ms LRA-delay prediction \u2192 anti-phase duty |\u00b7sin(\u03c6+\u03c0)|\u00d7amp\u00d7gain.",
    "Pushes: 4-IMU fusion weights \u00b7 vector tracking, no magnitude frequency-doubling \u00b7 amplitude-normalized PLL (survives 4\u00d7 shakes).",
    "Output: GPIO25 primary LRA + array mirror, 200 Hz raw PWM capped 700/1023; silent unless PLL locked + amp above gate; 4-windows-on / 2-off cooldown.",
    "Status: b7 combo + 8 host tests green, pipeline tests unbroken. Next: Thonny flash + 60 s wear smoke (still = silent, 6 Hz shake = buzz, no reset).",
]
box = slide.shapes.add_textbox(Inches(0.7), Inches(1.4), Inches(11.9), Inches(5.4))
tf = box.text_frame
tf.word_wrap = True
for i, b in enumerate(bullets):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = b
    p.level = 0
    p.space_after = Pt(10)
    p.runs[0].font.size = Pt(18)

prs.save("docs/slides/plan_b_slide.pptx")
print("saved docs/slides/plan_b_slide.pptx")
