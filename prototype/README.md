# prototype/ — Plan B loop simulator (host only, no hardware)

One command: `python prototype/run.py` (add `--seconds 30 --seed 3` to vary).
Output: 4 metrics on stdout + `prototype/out.csv` (open in Excel: t, raw x,
tremor amplitude, LRA duty, PLL locked?).

What it is: synthetic shaking hand (`sim.py`, tremor drifts 5.5-7.5 Hz) fed
sample-by-sample through the Plan B math (`loop.py`, mirrors
`firmware/plan_b/combo_b7_fit.py` for one channel).

What it is NOT: on-body proof. The residual model assumes an ideal push;
real LRA force, skin, and voluntary motion are unmodeled. Do not quote the
ratio as device efficacy.

## loop_v2.py — improved loop (experimental)

`loop.py` mirrors the device PLL exactly, including its real flaw: the
absolute lock band false-locks on far-off tones (4.2 Hz in, NCO parked at
6.0, duties at wrong phase — confirmed). `loop_v2.py` adds, all validated
in this directory:

- G1 gear-shift bandwidth: 3.0 Hz unlocked, 1.5 Hz locked.
- G2 coarse seeding: hysteresis rate-counter recenters the NCO after 1 s
  unlocked (self-healing; last-crossing differencing was tried and cascaded).
- B1 beat-aware lock: fast/slow phase-error EMAs + slow-EMA'd coarse-vs-NCO
  agreement veto (0.5 Hz, 30-sample persistence).

Results (static tones 4.2-8.5 Hz): lock 0.5-0.9 s, worst freq error 0.34 Hz
(negligible at 15 ms look-ahead). Realistic drift sim: locks 72% vs 96% for
the lenient stock loop — Loop2 stays silent when unsure instead of buzzing
at the wrong phase. Device port pending (see plan).
