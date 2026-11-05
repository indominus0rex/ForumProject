---
date: 2026-09-10T12:00:00+07:00
type: plan
status: draft
topic: plan-B simple-explanation slide version
---

# Plan: Simple-explanation version of the Plan B slide

## Goal

Produce `docs/plan_b_slide_simple.pptx`: the same Plan B slide rewritten so a non-engineer (advisor, first-year student, family member) understands it in 30 seconds.

## Current context / assumptions

- Technical slide exists: `docs/plan_b_slide.pptx`, built by `tools/make_plan_b_slide.py` (33 lines, python-pptx, 16:9 blank layout, title Pt 32 + 6 bullets Pt 18). Regenerate pattern: `uv run python tools/make_plan_b_slide.py` (bare `python` is the hermes venv and lacks `pptx`; the project interpreter is reached via `uv run`).
- Source facts the simple version must not contradict: 4 motion sensors on hand/wrist (`docs/PIN_ASSIGNMENTS.md`), small ESP32 chip, vibration motors as output, everything computed on-device with no phone/cloud (`docs/GOAL.md:15-18`), Plan B = smaller fit of the same math (`firmware/plan_b/README.md`), status = host tests green, wear test still pending.
- Deck context: source lives in Canva, PDF exported to `docs/`; new slide must paste cleanly into either (plain text, no special glyphs beyond UTF-8 already used: arrows and Greek already render in the technical slide, but the simple version avoids them entirely).
- House rule for slides from `docs/slide_review_2026-09-10.md`: every claim must trace to a repo path; no STFT, no DRV2605L-as-built, weights/battery numbers marked target-vs-measured.

## Architecture / proposed approach

Mirror the existing builder as `tools/make_plan_b_slide_simple.py` (same layout constants, same save-and-verify pattern), swapping the 6 engineer bullets for 5 plain-language ones built on one analogy: noise-cancelling headphones, but for hand shaking. A tiny host-side check script acts as the "test": it fails before the pptx exists and passes after, asserting slide count, title text, and that no banned jargon words appear.

## Step-by-step tasks

### Task 1 — Failing check script `tools/check_plan_b_slide_simple.py`

Why: the TDD "red" for a slide artifact — proves what "done" means before writing content.

Create `tools/check_plan_b_slide_simple.py` with this exact content (copy verbatim):

```python
"""Host check for docs/plan_b_slide_simple.pptx. Fails until the slide is built."""
from pptx import Presentation

BANNED = ["PLL", "ISR", "TCA9548A", "PWM", "biquad", "coherence",
          "MicroPython", "SRAM", "DSP", "quarantined"]

prs = Presentation("docs/plan_b_slide_simple.pptx")
assert len(prs.slides) == 1, "want exactly 1 slide, got %d" % len(prs.slides)
title = prs.slides[0].shapes.title.text
assert "Plan B" in title, "title must contain 'Plan B', got %r" % title
full = "\n".join(sh.text for sh in prs.slides[0].shapes if sh.has_text_frame)
for word in BANNED:
    assert word not in full, "jargon leak: %r must be reworded" % word
assert "noise-cancelling" in full, "the headphones analogy sentence is required"
print("simple slide check passed!")
```

Run (from repo root `C:\ForumProject`):

```bash
uv run python tools/check_plan_b_slide_simple.py
# expected (RED): FileNotFoundError ... docs/plan_b_slide_simple.pptx (file does not exist yet)
```

Pass criteria for this task: command fails with FileNotFoundError, nothing else. Commit: `test: add failing simple-slide check`.

### Task 2 — Builder `tools/make_plan_b_slide_simple.py` (green)

Why: same proven pattern as `tools/make_plan_b_slide.py`, new words only.

Create `tools/make_plan_b_slide_simple.py` with this exact content (copy verbatim):

```python
"""Build docs/plan_b_slide_simple.pptx — Plan B in plain words (16:9)."""
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

prs.save("docs/plan_b_slide_simple.pptx")
print("saved docs/plan_b_slide_simple.pptx")
```

Run:

```bash
uv run python tools/make_plan_b_slide_simple.py
# expected (GREEN): saved docs/plan_b_slide_simple.pptx

uv run python tools/check_plan_b_slide_simple.py
# expected (GREEN): simple slide check passed!
```

Pass criteria: both commands green; open `docs/plan_b_slide_simple.pptx` in PowerPoint once and confirm one slide, no text overflow at 16:9. Commit: `feat: add simple-explanation Plan B slide`.

### Task 3 — Cross-check simple vs technical (no-contradiction pass)

Why: plain words must still be true; the slide review rejects unsourced claims.

Read-only comparison, no code. For each simple bullet, write the tracing line as a comment at the top of the commit message (not in the slide):

```bash
uv run python -c "from pptx import Presentation; p=Presentation('docs/plan_b_slide_simple.pptx'); print('\n'.join(sh.text for sh in p.slides[0].shapes if sh.has_text_frame))"
# expected: title + 5 bullets printed; verify by eye:
#  bullet 1 (opposite push) <- firmware/common/anticancel.py phase_offset pi
#  bullet 2 (4 sensors, 100Hz, no phone) <- docs/PIN_ASSIGNMENTS.md + docs/GOAL.md:15-18
#  bullet 3 (half-second learn, follows) <- firmware/common/pll.py lock_threshold 50
#  bullet 4 (thumb/finger tell shakes apart) <- firmware/stages/features.py coh 0.6
#  bullet 5 (8 tests green, wear test next) <- tests/test_b7_fit.py + plan Task 7
```

Pass criteria: every bullet traces; any bullet that does not trace gets reworded (never add numbers like accuracy or battery life — those are targets, see review finding F9). Commit: `docs: trace simple slide claims to repo` (message body holds the 5 trace lines; if a reword was needed, amend the builder and re-run Task 2 greens first).

## Tests / validation

- Per task: red then green with the exact commands above. The "test suite" for this work is:

```bash
uv run python tools/check_plan_b_slide_simple.py
# expected: simple slide check passed!

uv run python tools/make_plan_b_slide.py && uv run python tools/check_plan_b_slide_simple.py
# note: rebuilding the TECHNICAL slide must not affect the simple one; both files coexist
```

- Manual gate (2 min): open `docs/plan_b_slide_simple.pptx` in PowerPoint/Canva import, confirm single 16:9 slide, all text visible, no jargon a first-year student would trip on (test: read it aloud; any word you must explain gets reworded).
- Existing repo tests untouched; if `python tests/test_b7_fit.py` was green before, re-run once at the end to confirm nothing in `firmware/` changed (it must not — this work adds only `tools/` + `docs/` files).

## Risks, tradeoffs, and open questions

- Oversimplification risk: "learns rhythm in half a second" hides lock failures and voluntary-motion false buzzes. Tradeoff accepted for a general audience, but the speaker notes (30 s version below, to be read aloud not printed) must carry the honest caveat. Proposed notes: "This is the small version that fits today's chip. It helps with steady rhythmic shaking; it does not diagnose anything, and the wearing test has not happened yet."
- Thai-audience option: the deck PDF is Thai-titled; if the advisor wants Thai, do NOT machine-translate the pptx in this work — add a follow-up task with a native speaker reviewing, since mistranslated medical claims are worse than English ones.
- Open: does the simple slide replace or accompany the technical one? Recommendation: accompany (technical for methods Q&A, simple for opening) — confirm with team before inserting into the Canva source, since slide count affects talk timing.
- Open: DRV2605L and 320 g / 6-8 h targets are deliberately absent from the simple slide; if the team wants them mentioned, they must be labeled "(target)" per review finding F9.
