# Plan: Review presentation slide deck in docs/

## Goal
Produce a slide-by-slide review report that fact-checks every claim in the deck against the repo and gives paste-ready corrected text.

## Current context / assumptions
- The "presentation slide" is the only slide-like file under docs/: `docs/ถุงมือกันสั่น.pdf` (6.5 MB, 118 lines of extractable text, ~15 slides). No `.pptx` or other slide source exists in the repo (verified: no `*.pptx`, one `*.pdf` at repo depth ≤ 2).
- Deck text was extracted with the file reader (text layer reads fine). Slide inventory from extraction:
  1. Title: "Real-Time Hand Tremor Suppression System Utilizing Deep Neural Network on Edge Computing" + "Presented by Project Advisor" + 5 names (Mr. Takorn Wisetrith, Prof. Aphilak Lonklang, Mr. Lertpisit Puengwongsanurak, T. Nongnud Paiboon, Mr. Waritnan Waewbunditwittaya)
  2. Introduction — normal person / sufficient dopamine
  3. Introduction — Parkinson / insufficient dopamine
  4. Problem — essential tremor 4–12 Hz (active), resting tremor 3–6 Hz
  5. Problem — "Over 70% of patients experience challenges living independently"
  6. Objectives (3 bullets: quality of life, daily living, evaluate efficacy + ergonomics)
  7. Literature review (Ibrahim et al. 2021 DNN tremor reduction)
  8. System Architecture: MPU6050 sensing → Butterworth bandpass → STFT (listed TWICE) → DNN features (RMS, Actuator Motor Speed, Peak Frequency, Suppression Frequency, Spectral Power, Spectral Entropy) → DRV2605L control layer
  9. Prototype: fitness-glove design, 320 g, neoprene + silicone, 6–8 h battery
  10. Current stage: "Architecture design"
  11. Plans (no content in text layer)
  12–14. Bibliography (12 refs over 3 slides)
  15. Thank-you slide
- Ground truth already spot-checked (implementer re-verifies each in tasks below):
  - `host_scripts/train_classifier.py:main(paths, use_dnn=False)` — DEFAULT is multinomial LogisticRegression (`:227`); MLP/DNN only on the `use_dnn` flag (`:219`). Deck title/arcitecture says "DNN" unconditionally.
  - `docs/PIN_ASSIGNMENTS.md:57` — LRAs are DEFERRED for the 4-IMU build (`USE_LRA_ARRAY=False`, GPIO25/18/19/20 unpopulated); `docs/EMBED_README.md` says "DRV2605 LRA driver (raw PWM for now)". Deck presents DRV2605L as the implemented control layer.
  - `host_scripts/train_classifier.py:146-186` — real feature vector is 15 elements (`rms_all, std_all, mcr, dom_freq, bp_3_6, bp_6_9, bp_9_12, bp_12_25, ent, dom_axis, rms_x, rms_y, rms_z, xy_ratio, prominence`). Deck lists 6 items, two of which ("Actuator Motor Speed", "Suppression Frequency") are actuator outputs, not classifier inputs.
  - No STFT anywhere in `firmware/` or `host_scripts/` (grep, excl. `.venv`, returns nothing); firmware uses in-place Cooley-Tukey FFT on 128-sample windows (`fft.py`, `GY521` + `FFTProcessor`). "STFT" is wrong terminology (and listed twice).
  - `firmware/common/bandpass.py:1` — 2nd-order IIR biquad cascade, "Butterworth-like", 3–12 Hz tremor band. The "Butterworth bandpass" claim is roughly accurate; verify cutoffs match the slide if the slide states any.
  - Repo design bands (`docs/PIN_ASSIGNMENTS.md:54,82`, `firmware/common/config.py:64`): pill-rolling 4–6 Hz, ET postural 6–8 Hz, coherence discriminant 0.6. Deck says essential 4–12 Hz / rest 3–6 Hz (textbook ranges, wider than design bands — flag, don't necessarily "fix").
  - "320 g / neoprene+silicone / 6–8 h" appears NOWHERE else in repo docs (grep over `*.md` returns no hits). Unsourced; 320 g is heavy for a glove — flag to source or soften to "target".
  - Bibliography defects: ref 1 (Cooley) year "2522" (Thai Buddhist year; the paper is Cooley–Lewis–Welch, IEEE Trans. Education 12(1), 27–34, March 1969 — fix to 1969); Ibrahim et al. 2021 appears TWICE (lit-review slide AND ref 12); ref 12 has typo "Parkinso" (missing s).
  - Typo on prototype slide: "Tecnical information".
  - Title slide role label: "Presented by Project Advisor" followed by a mix of advisor + student names — label is wrong.
  - Deck omits the project's actual differentiators (`docs/GOAL.md`): edge-only closed loop (no phone/cloud), two-tremor-types-two-problems, PLL anti-phase actuation supervised by per-window classification, 100 Hz / 128-sample windows. No methods/results data, no evaluation numbers, "Current stage" and "Plans" slides look near-empty.

## Architecture / proposed approach
The PDF is a binary export with no editable source in the repo, so the deliverable is a review REPORT (`docs/slide_review_2026-09-10.md`), not an edited deck: a claim-vs-ground-truth table where every finding cites an exact `path:line`, each with paste-ready replacement text the author applies in their slide tool (Canva/PowerPoint). Verify-first rule: any finding without a `path:line` citation is dropped from the report.

## Step-by-step tasks

### Task 1 — Re-extract deck text and freeze the slide inventory (3 min)
Read the PDF text layer and confirm the 15-slide inventory in Current context above still matches (the file was touched 2026-09-10; it may have changed since).
Exact commands (read-only; quote the Thai filename):
```
python -c "print('skip')"
ls -la "C:/ForumProject/docs/" | grep -i "pdf"
```
Then re-read via the file reader: `docs/ถุงมือกันสั่น.pdf`, lines 1–118.
Expected: single PDF ~6.5 MB; extraction yields the same 15 blocks (title → thank-you). If slides differ, update the inventory list in the report (Task 7) before proceeding — do not review stale text.

### Task 2 — Verify the "DNN" claim (5 min)
Open `host_scripts/train_classifier.py` and confirm: default classifier type, what the flag is called, and what the DNN branch is.
```
grep -n "use_dnn\|MLPClassifier\|LogisticRegression\|HIDDEN" "C:/ForumProject/host_scripts/train_classifier.py"
```
Expected output: `use_dnn=False` default at `main()`; `MLPClassifier` in the `if use_dnn:` branch (~:219), `LogisticRegression` in `else` (~:227).
Also check `docs/GOAL.md:26-27` (research direction: 1D-CNN/LSTM, hybrid DNN-gated PLL) to characterize DNN as direction vs. current default.
Record verdict for the report: title + architecture slide overclaim UNLESS the team has locked the DNN branch — if locked, cite the bake-gate instead (`docs/GOAL.md:32-34`: no weights into `firmware/common/` without beating baseline on CV).
Paste-ready replacement (use if default is still logreg):
```
Title option A (accurate today): "Real-Time Hand Tremor Suppression System Utilizing Machine Learning on Edge Computing"
Title option B (keeps DNN): keep title, add subtitle "Deep-neural-gated actuation (MLP branch, bake-gated on cross-validation) — baseline: multinomial logistic regression"
```

### Task 3 — Verify the DRV2605L / actuation claim (5 min)
```
grep -n "DRV2605\|raw PWM\|USE_LRA_ARRAY\|Deferred\|GPIO25" "C:/ForumProject/docs/PIN_ASSIGNMENTS.md" "C:/ForumProject/docs/EMBED_README.md" | head -15
```
Expected: `PIN_ASSIGNMENTS.md:57` LRAs deferred, `USE_LRA_ARRAY=False`; `EMBED_README.md` "raw PWM for now".
Record verdict: architecture slide presents DRV2605L as implemented — overclaim for the 4-IMU build.
Paste-ready replacement:
```
4. Control Layer: LRA haptic output (raw PWM @ 200 Hz on GPIO25 today; dedicated DRV2605L driver planned) — PLL anti-phase actuation, per-sample path supervised by per-window classification
```
Cross-check the PLL part against `firmware/common/pll.py:31` and `docs/GOAL.md:12-14` before including the second clause; drop the clause if the files don't support it.

### Task 4 — Verify the signal-chain terminology (bandpass / STFT / FFT) (5 min)
```
grep -rn "STFT\|stft\|short-time" --include="*.py" "C:/ForumProject/firmware/" "C:/ForumProject/host_scripts/" | head -5
sed -n '1,20p' "C:/ForumProject/firmware/common/bandpass.py"
grep -n "class FFTProcessor\|class GY521\|128\|SAMPLE_INTERVAL" "C:/ForumProject/firmware/fft.py" 2>/dev/null | head -8 || grep -rln "FFTProcessor" --include="*.py" "C:/ForumProject/firmware/"
```
Expected: STFT grep returns NOTHING (confirms wrong term + duplicate bullet); `bandpass.py:1` confirms 3–12 Hz IIR biquad "Butterworth-like"; FFT class + 128-sample window at 100 Hz confirmed somewhere in `firmware/`.
Paste-ready replacement:
```
2. Signal Processing: IIR bandpass (3–12 Hz, Butterworth-like) → in-place Cooley–Tukey FFT on 128-sample windows @ 100 Hz → 15 spectral/time-domain features
```
(delete the duplicated STFT bullet outright).

### Task 5 — Verify the feature list (5 min)
Re-read `host_scripts/train_classifier.py:146-186` (`extract_features` return array) and confirm the 15 names in Current context. Confirm "motor speed" / "suppression frequency" appear only as actuation-side concepts:
```
grep -rn "motor_speed\|suppress_duty\|LRA_FREQ" --include="*.py" "C:/ForumProject/firmware/" | head -8
```
Expected: those terms live in `firmware/stages/haptic.py` / `suppress.py` / config (actuation path), NOT in `extract_features`.
Paste-ready replacement (feature chips on the architecture slide):
```
Inputs (15): rms_all, std_all, mean-crossing rate, dominant freq, band powers 3–6 / 6–9 / 9–12 / 12–25 Hz, spectral entropy, dominant axis, rms_x/y/z, xy_ratio, peak prominence
Outputs (actuation, not features): suppression frequency + duty from PLL anti-phase chain
```

### Task 6 — Verify prototype specs + frequency bands (5 min)
```
grep -rni "320\|neoprene\|6–8 hours\|6-8 hours\|battery life" --include="*.md" "C:/ForumProject/docs/" "C:/ForumProject/README.md" 2>/dev/null | head -8
grep -n "4–6\|6–8\|4-6\|6-8\|coherence" "C:/ForumProject/docs/PIN_ASSIGNMENTS.md" | head -8
```
Expected: first grep returns NOTHING (specs unsourced — flag as "source or soften"); second confirms pill 4–6 Hz / ET 6–8 Hz design bands vs. deck's textbook 4–12 / 3–6 Hz.
Paste-ready replacements:
```
Technical information (targets — update after weighing): weight ~320 g (target) · neoprene + silicone · 6–8 h per charge (target)
Bands footnote for problem slide: "Design bands: pill-rolling 4–6 Hz; essential/postural 6–8 Hz (thumb–index coherence > 0.6); wider textbook ranges shown."
```
Also fix `Tecnical` → `Technical`.

### Task 7 — Bibliography + title-slide fixes (5 min)
From the extraction (lines 97–116), confirm and fix in the report:
- Ref 1: `2522` → `1969`. Replacement: `Cooley, J. W., Lewis, P. A. W., Welch, P. D. The Fast Fourier Transform and Its Applications. IEEE Transactions on Education, 12(1), 27–34, 1969.`
- Refs 1-vs-12: Ibrahim et al. 2021 duplicated — delete ref 12, keep the lit-review citation.
- Ref 12 (if kept): `Parkinso` → `Parkinson's`.
- Title slide: replace `## Presented by Project Advisor` + name soup with:
```
Presented by: Mr. Takorn Wisetrith, Mr. Lertpisit Puengwongsanurak, T. Nongnud Paiboon, Mr. Waritnan Waewbunditwittaya
Project Advisor: Prof. Aphilak Lonklang
```
(confirm the advisor/student split with the user — see Open questions; if unsure, list as verdict "role labels ambiguous" with this as proposal, not fact.)
- "70% of patients" (slide 5): no repo source — mark "needs citation (papers 2/3/4 are candidates — check Shanker 2019 or Elias 2014 before claiming)".

### Task 8 — Write the review report (5 min)
Create `docs/slide_review_2026-09-10.md` with exactly three sections:
1. `Slide inventory` — numbered slides with one-line content each (from Task 1).
2. `Findings table` — one row per finding: `| Slide | Claim | Verdict (accurate / overclaim / wrong-term / typo / unsourced / missing) | Evidence (path:line) | Paste-ready fix |`. Minimum 12 rows (F1–F12 in Current context). Drop any row lacking a `path:line`.
3. `Missing slides (proposal)` — 3 paste-ready outlines: (a) Methods/pipeline diagram (quality → bandpass → FFT → features → classify → PLL suppress; cite `docs/GOAL.md:20-27`); (b) Results (train accuracy + CV protocol from `train_classifier.py` — run `python host_scripts/train_classifier.py --help` read-only to see if reportable numbers exist; if `sessions/` is empty, write "no pilot data yet — show expected-metrics template instead"); (c) Timeline/next steps (flesh out empty Current-stage/Plans slides).
Verify: `ls docs/slide_review_2026-09-10.md` exists; every Findings row has a non-empty Evidence cell. Then commit: `git add docs/slide_review_2026-09-10.md && git commit -m "docs: review presentation slide deck with paste-ready fixes"`.

## Tests / validation
This is a docs-review task — no code changes, so no TDD cycle. Validation is per-task "verify-first" instead:
- Each task has an Exact command + Expected output above. If actual output contradicts Expected, STOP: update Current context with the real finding and adjust the report — never copy a verdict the grep didn't support.
- Report acceptance gate (all must hold): (i) ≥12 findings rows; (ii) every row has a `path:line` that opens to the cited text; (iii) every overclaim/typo row has a paste-ready fix block; (iv) no firmware/host files modified (`git status --short` shows only the new report file).
- Suggested spot-checks after writing: `grep -c "path:line\|\\.py:\\|\\.md:" docs/slide_review_2026-09-10.md` (expect ≥12); open 3 cited `path:line`s at random and confirm they say what the row claims.

## Risks, tradeoffs, and open questions
- Risk: PDF is an export with no source in repo — the report is advisory; actual slide edits happen in the author's external tool. Mitigation: paste-ready blocks minimize transcription error; ask the author to re-export the PDF to `docs/` after fixing.
- Risk: Thai filename (`ถุงมือกันสั่น.pdf`) breaks naive tooling (glob/encoding). Mitigation: always quote the full path; verified working with `ls`/`grep` above.
- Risk: deck may have been re-exported after this plan (touched 2026-09-10 08:44). Mitigation: Task 1 re-verifies inventory first.
- Tradeoff: "DNN" in the title — fixing to "Machine Learning" is accurate today but weaker positioning; keeping DNN bets on the `use_dnn`/CNN-LSTM direction landing. Flagged as the author's call (options A/B in Task 2), not decided unilaterally.
- Open question 1 (user): title-slide roles — is Prof. Aphilak Lonklang the sole advisor and the other four the student team? Fix in Task 7 assumes yes.
- Open question 2 (user): are 320 g / 6–8 h measured or targets? If measured, point at the measurement note so the report can cite it; else use the "(target)" wording.
- Open question 3 (user): is there a slide source file (`.pptx`, Canva link) that should live alongside the PDF? If yes, Task 8 gains a follow-up: apply fixes at source and re-export.
- Do NOT: edit firmware/host code, translate Thai comments, hand-edit `model.py` weights block, or commit anything except the review report.
