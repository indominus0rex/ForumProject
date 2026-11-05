"""Build docs/slides/plan_b_slide_simple.pptx — Plan B in plain words (16:9)."""
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
slide = prs.slides.add_slide(prs.slide_layouts[5])  # title only

title = slide.shapes.title
title.text = "Plan B: a glove that steadies shaking hands"
title.text_frame.paragraphs[0].runs[0].font.size = Pt(32)

bullets = [
    "The idea is like noise-cancelling headphones, but for hand shaking: feel the shake, then push back at exactly the opposite moment.",
    "Four small motion sensors on the hand and wrist listen to the shaking 100 times per second; one tiny chip does all the thinking, no phone or internet needed.",
    "The chip learns each person's shake rhythm in about half a second and keeps following it even when the shaking gets stronger or weaker.",
    "Two extra sensors on the thumb and finger help tell resting shakes apart from movement shakes, so help only comes when it is really shaking.",
    "What works today: the thinking part passes all 8 computer tests. What is next: sew it into the glove and try wearing it for one minute, still versus shaking.",
]
box = slide.shapes.add_textbox(Inches(0.7), Inches(1.4), Inches(11.9), Inches(5.4))
tf = box.text_frame
tf.word_wrap = True
for i, b in enumerate(bullets):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = b
    p.level = 0
    p.space_after = Pt(10)
    p.runs[0].font.size = Pt(20)

prs.save("docs/slides/plan_b_slide_simple.pptx")
print("saved docs/slides/plan_b_slide_simple.pptx")
