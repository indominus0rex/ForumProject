# Slide review: docs/ถุงมือกันสั่น.pdf (2026-09-10)

Reviewer: Hermes Agent. Method: every claim below was checked against the cited
`path:line` in this repo. Deck-side citations (`docs/ถุงมือกันสั่น.pdf:<line>`)
refer to the PDF text-layer line numbers as extracted by the file reader
(118 lines total). Verdicts: accurate / overclaim / wrong-term / typo /
unsourced / missing. Apply the paste-ready blocks in the slide source
(Canva/PowerPoint), then re-export the PDF to `docs/`.

## 1. Slide inventory (15 slides, from PDF text layer)

1. Title + "Presented by Project Advisor" + 5 names
2. Introduction — normal person / sufficient dopamine
3. Introduction — Parkinson's / insufficient dopamine
4. Problem — essential tremor 4–12 Hz (active), resting tremor 3–6 Hz
5. Problem — "Over 70% of patients experience challenges living independently"
6. Objectives (3 bullets)
7. Literature review — Ibrahim et al. 2021 DNN paper
8. System Architecture — MPU6050 → Butterworth bandpass → STFT (x2) → DNN
   features (6 items) → DRV2605L control layer
9. Prototype — fitness-glove design, 320 g, neoprene + silicone, 6–8 h battery
10. Current stage — "Architecture design"
11. Plans (no text content)
12–14. Bibliography (12 refs)
15. Thank you

## 2. Findings

| # | Slide | Claim | Verdict | Evidence | Paste-ready fix |
|---|-------|-------|---------|----------|-----------------|
| F1 | 1 Title | "…Utilizing Deep Neural Network…" as the system as-built | overclaim | `host_scripts/train_classifier.py:193` (`main(paths, use_dnn=False)`); `:227` default is multinomial LogisticRegression; MLP/DNN only behind `--dnn` (`:284`, `:218-226`). DNN-in-firmware exists (`firmware/common/model_dnn.py`, `HIDDEN = 16`, `train_classifier.py:89`) but is NOT the default path | Option A (accurate today): "Real-Time Hand Tremor Suppression System Utilizing Machine Learning on Edge Computing". Option B (keeps DNN): add subtitle "Deep-neural-gated actuation (MLP branch, bake-gated on cross-validation) — baseline: multinomial logistic regression" |
| F2 | 1 Title | "Presented by Project Advisor" over all 5 names | wrong-term | Deck text lines 5–7; advisor vs student roles conflated | "Presented by: Mr. Takorn Wisetrith, Mr. Lertpisit Puengwongsanurak, T. Nongnud Paiboon, Mr. Waritnan Waewbunditwittaya. Project Advisor: Prof. Aphilak Lonklang" (confirm split with team — see §4 Q1) |
| F3 | 8 Arch | "Short-Time Fourier Transform (STFT)" bullet, listed TWICE | wrong-term + duplicate | Zero hits: `grep -rn "STFT\|stft" firmware/ host_scripts/` returns nothing. Actual: in-place Cooley–Tukey FFT, `firmware/common/fft.py:11` (`class FFTProcessor`); 128-sample windows @ 100 Hz = 1.28 s, `firmware/common/config.py:4-7` | Delete one bullet; rewrite the other: "Spectral analysis: in-place Cooley–Tukey FFT on 128-sample windows @ 100 Hz (1.28 s)" |
| F4 | 8 Arch | DNN inputs listed as: RMS, Actuator Motor Speed, Peak Frequency, Suppression Frequency, Spectral Power, Spectral Entropy | overclaim (2 of 6 are outputs, 9 real inputs omitted) | Real 15-element vector `host_scripts/train_classifier.py:146-186`: rms_all, std_all, mcr, dom_freq, bp_3_6, bp_6_9, bp_9_12, bp_12_25, ent, dom_axis, rms_x, rms_y, rms_z, xy_ratio, prominence. "Motor speed"/"suppression frequency" live only on the actuation path (`firmware/embedded_main_hsp.py:32`, `firmware/plan_b/combo_b1_heuristic_haptic.py:38` `frame["suppress_duty"]`) | Inputs (15): "rms_all, std_all, mean-crossing rate, dominant freq, band powers 3–6 / 6–9 / 9–12 / 12–25 Hz, spectral entropy, dominant axis, rms_x/y/z, xy_ratio, peak prominence". Separate line: "Outputs (actuation, not features): suppression frequency + duty from PLL anti-phase chain" |
| F5 | 8 Arch | "Control Layer: DRV2605L Haptic Driver Module" as implemented | overclaim | `docs/embed_readme.md:89` "DRV2605 LRA driver (raw PWM for now)"; `:39` "or use DRV2605 driver for clean drive later". LRAs DEFERRED for 4-IMU build: `docs/pin_assignments.md:57` (`USE_LRA_ARRAY=False`, GPIO25/18/19/20 unpopulated), `:77` | "Control Layer: LRA haptic output — raw PWM @ 200 Hz on GPIO25 today (`firmware/common/config.py:12`); dedicated DRV2605L driver planned. Actuation: PLL anti-phase chain (`firmware/stages/suppress.py`, per `docs/goal.md:24`), per-sample path supervised by per-window classification" |
| F6 | 8 Arch | "Butterworth Bandpass Filter" | accurate (keep) | `firmware/common/bandpass.py:1` "2nd-order IIR bandpass filter for 3-12 Hz tremor band", biquad cascade, "Butterworth-like" (`:94`) | Keep; optionally append "(3–12 Hz IIR biquad cascade)" |
| F7 | 8 Arch | "Sensing Layer: MPU6050 (GY-521)" | accurate (keep) | 4-IMU harness via TCA9548A, `docs/pin_assignments.md:47-54` | Keep; optionally append "(x4 via TCA9548A mux: dorsal wrist, thenar, thumb + index phalanx)" |
| F8 | 4 Problem | Essential 4–12 Hz / resting 3–6 Hz | accurate-as-textbook but inconsistent with design bands | Design bands: pill-rolling 4–6 Hz, ET postural 6–8 Hz, coherence 0.6 — `docs/pin_assignments.md:54,82`, `firmware/common/config.py:64` | Keep the textbook ranges; add footnote: "Design bands: pill-rolling 4–6 Hz; essential/postural 6–8 Hz (thumb–index coherence > 0.6)" |
| F9 | 9 Prototype | "Total weight: 320 grams. Materials: Neoprene fabric and silicone. Battery life: 6–8 hours per charge" | unsourced | `grep -rni "320\|neoprene\|6–8 hours\|6-8 hours" docs/ --include=*.md` returns NOTHING. No weighing/battery measurement in repo. 320 g is heavy for a glove — invites questions | Soften to targets until measured: "Weight ~320 g (target) · Neoprene + silicone · 6–8 h per charge (target)". If measured, add the measurement note to `docs/` and cite it here |
| F10 | 9 Prototype | "Tecnical information" | typo | Deck text line 87 | "Technical information" |
| F11 | 12 Biblio | "Cooley … IEEE Transactions on Education 2522, 12(1), 27-34" | typo (year) | 2522 = Thai Buddhist year. The paper is Cooley–Lewis–Welch, "The Fast Fourier Transform and Its Applications", IEEE Trans. Education, vol. 12, no. 1, pp. 27–34, March 1969 | "Cooley, J. W., Lewis, P. A. W., Welch, P. D. The Fast Fourier Transform and Its Applications. IEEE Transactions on Education, 12(1), 27–34, 1969." |
| F12 | 7 + 14 | Ibrahim et al. 2021 cited on lit-review slide AND as ref 12 (identical paper) | duplicate | Deck text lines 49 and 116 | Delete ref 12, keep the lit-review citation |
| F13 | 14 Biblio | "Parkinso Tremor Reduction" (ref 12) | typo | Deck text line 116 | "Parkinson's" (moot if F12 applied) |
| F14 | 5 Problem | "Over 70% of patients…" | unsourced | No repo source; candidate citations on file are Shanker 2019 (ref 2) / Elias 2014 (ref 3) | Add citation or soften: "A majority of patients report challenges living independently [Shanker 2019]" — verify the number in the cited paper before keeping "70%" |
| F15 | 10–11 | "Current stage: Architecture design" + empty "Plans" | missing | Repo is well past pure architecture: HSP pipeline wired (`docs/goal.md:22-25`), 4-IMU harness locked (`docs/pin_assignments.md:47-57`), pilot protocol exists (`docs/pilot_collection_protocol.md`), but `sessions/*.csv` is EMPTY (no pilot data yet) | See §3 proposals (b) + (c) |
| F16 | whole deck | No mention of actual differentiators: edge-only closed loop, two-tremors-two-problems, PLL supervision, latency | missing | `docs/goal.md:9-18` (constraints), `:22-25` (pipeline) | See §3 proposal (a) |

## 3. Proposed additional slides (paste-ready outlines)

(a) Methods / pipeline (replaces vague arch slide if space is short):
"Pipeline @ 100 Hz, 128-sample (1.28 s) windows: sensor → quality gate → IIR
bandpass 3–12 Hz → FFT → 15 features → classifier → state machine (supervisory)
→ PLL anti-phase LRA drive (per-sample actuation). Training on host; only baked
weights enter firmware. No phone/cloud in the loop."

(b) Results (honest version given empty `sessions/`):
"Status: pilot collection protocol defined; no pilot windows captured yet
(`sessions/` empty). Evaluation protocol (locked): StandardScaler +
classifier bake-gate — weights enter `firmware/common/` only on beating
baseline cross-validation (`train_classifier.py`, StratifiedKFold). Next: capture
rest/postural/kinetic/baseline sessions, report train + CV accuracy per class."

(c) Timeline / next steps (fills slides 10–11):
"Done: HSP stage pipeline, 4-IMU harness lock, bandpass/FFT/feature firmware,
trainer with logreg + MLP branches. Next: (1) pilot capture → (2) bake-gated
weights → (3) LRA procurement + DRV2605L drive → (4) closed-loop latency +
suppression-efficacy measurement → (5) weight/ergonomics validation of the
320 g / 6–8 h targets."

## 4. Open questions for the team

- Q1: Title-slide roles — is Prof. Aphilak Lonklang the sole advisor and the other four the student team? (F2 fix assumes yes.)
- Q2: Are 320 g / 6–8 h measured or targets? (Determines F9 wording.)
- Q3: Is "DNN" the locked claim (i.e. `--dnn` MLP branch is what ships)? If yes, say so explicitly with the bake-gate; if no, take Title option A. (F1.)
- Q4: Where is the slide source (`.pptx`, Canva link)? Consider storing it next to the PDF so fixes don't require re-typing from this report.
