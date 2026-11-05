"""Host check for docs/slides/plan_b_slide_simple.pptx. Fails until the slide is built."""
from pptx import Presentation

BANNED = ["PLL", "ISR", "TCA9548A", "PWM", "biquad", "coherence",
          "MicroPython", "SRAM", "DSP", "quarantined"]

prs = Presentation("docs/slides/plan_b_slide_simple.pptx")
assert len(prs.slides) == 1, "want exactly 1 slide, got %d" % len(prs.slides)
title = prs.slides[0].shapes.title.text
assert "Plan B" in title, "title must contain 'Plan B', got %r" % title
full = "\n".join(sh.text for sh in prs.slides[0].shapes if sh.has_text_frame)
for word in BANNED:
    assert word not in full, "jargon leak: %r must be reworded" % word
assert "noise-cancelling" in full, "the headphones analogy sentence is required"
print("simple slide check passed!")
