# Development notes

Context for anyone (or any AI assistant) changing this code. Read this before editing; update the
**Decision log** and **Changelog** at the bottom when you change behaviour.
User-facing instructions (setup, running a session, data files) are in `README.md`.

## 1. Principles the code relies on

1. **One casino scene for everything.** `common/scene.py::CasinoScene.feedback_sequence()` draws
   forward mask → coin → backward mask for BOTH the bandit and the STEP calibration. The calibration must
   be shown in exactly the same setting as the experiment; only the opacity differs. Never give the
   calibration its own drawing code.
2. **All numbers live in `config.py`** ("macros"). Code never hard-codes a duration, size, count or key.
   `PLACEHOLDER` = must be set for the lab PC; `DEBUG` = must be restored before real data.
3. **All participant text lives in `texts/`** (Hebrew). Code only lays it out. Placeholders like
   `{time_limit}` are filled from `config.py`, so texts stay in sync with the settings.
4. **Data are saved only with PsychoPy's `ExperimentHandler`** (`common/io.py::TaskData`): one file per
   task per day, date-stamped (never overwritten), saved on normal end, Escape and crash. Empty cells
   mean "not applicable" (None is written as empty, not the text "None").
   The only extra file is `data/calibration_summary.csv` (in addition, not instead).
5. **Logic is separated from drawing where it matters**, so it can be unit-tested without a screen:
   `tasks/calibration/step.py` (STEP), `tasks/bandit/schedule.py`, the pure functions in `tasks/wm/run.py`.
6. **Timing policy (until decided):** durations are produced with `core.wait()` after `win.flip()`, as in the
   original prototype. Every flip time is logged (`t_*` columns), and measured durations are saved
   (`coin_duration_measured` etc.). Changing to frame-counted timing is an open decision - do it in
   `common/display.py::show()` so every task changes at once.
   *Why it matters:* a screen can only change at a monitor refresh (16.7 ms at 60 Hz). `core.wait(0.033)`
   ends just before the 2nd refresh, so any small delay makes the coin last 3 refreshes (50 ms) instead of 2.
   Frame-counted timing ("draw + flip N times") shows exactly N refreshes, but every duration must then be a
   whole number of refreshes (33.3 ms works at 60/120 Hz, not at 144 Hz). Coin duration is part of the
   subliminal manipulation, so it must be identical in calibration and task. Lab-PC checks: README,
   "Lab PC checklist".
7. **Each day is a list of task functions** (`run_day_1.py`, `run_day_2.py`). A task is `task(ctx)`;
   `ctx` carries `win`, `keys`, `screens`, `participant`, `runtime`. To stop the day from inside a task
   raise `common.day.StopDay("reason")` (participant sees "call the experimenter").

## 2. How to change common things

| I want to… | Where |
|---|---|
| change a duration, size, trial count, key, colour | `config.py` |
| change a sentence the participant sees | `texts/<task>.py` |
| add/remove a quiz question | `QUIZ` list in `texts/<task>.py` (`correct` = 0-based index); bot mode answers automatically |
| change instruction pages | `PAGES` in `texts/<task>.py`; picture keys (`offer`, `coins`, `mask`, …) are drawn by `build_pages()` in the task |
| change task order or add a task | the `TASKS` list in `run_day_1.py` / `run_day_2.py` |
| add a data column | add it to the row dict in the task's `run_trial()`; keep the key present (value None) on trials where it doesn't apply |
| change the coin pair | `COIN_REWARD_IMAGE`, `COIN_NO_REWARD_IMAGE` in `config.py` (open decision: luminance-matched pair) |
| turn on the in-task awareness probe | `AWARENESS_PROBE_RATE` in `config.py` (adds a sentence to the Day-2 instructions automatically) |

After any change: `python -m pytest tests` and `python run_day_1.py --bot` / `run_day_2.py --bot`.

## 3. Gotchas found during development (don't re-learn these)

- **OneDrive:** a Python environment (or the repo) inside OneDrive makes the first `import psychopy.visual`
  take minutes and can lock data files. Keep both outside OneDrive on the experiment PC.
- **Windows display scaling** must be 100% (laptop was 125% → PsychoPy saw 1536×960 instead of 1920×1200).
  `open_window()` warns.
- **Hebrew text wrapping:** PsychoPy's own wrapping reverses the line order of right-to-left paragraphs.
  `common/ui.py::Screens.wrap()` wraps lines itself; stimuli get a wrap width they never reach.
  Lines that START with a digit get the digit moved to the end - start list lines with a word,
  and draw numbers (quiz options, Likert points) as separate stimuli (already done).
- **Typed Hebrew answers:** PsychoPy's editable `TextBox2` stores Hebrew reversed. `Screens.text_entry()`
  reads characters from the window's text events and draws them with TextStim instead.
- **Window colour** changes show only after the next flip (`tasks/wm/run.py` flips once after switching).
- **Text anchoring:** right-aligned body text is anchored at the right edge (`anchorHoriz='right'`);
  with the huge internal wrap width, centre anchoring pushes it off screen.
- **Hebrew keyboard layout:** s/f/h/k may arrive as ד/כ/י/ל (and s/k in WM as ד/ל) - accepted via
  `ARM_KEY_ALIASES` / `WM_KEY_ALIASES`.
- **Measured timing on the laptop (60 Hz):** the 33 ms backward mask measured 34.8–36.5 ms with
  `core.wait()` timing (demo_timing.txt, 23 Oct 2026) - evidence for the timing decision.
- **Testing headless:** the code was developed and tested with PsychoPy 2024.2.4 and 2026.2.4 under a
  virtual display (xvfb). Real timing can only be checked on the real screen (`demo_scene.py`, photodiode).

## 4. Decision log (what was decided, and why)

Decided by Alon during code finalization, 22–23 Oct 2026:

**General**
- Code drawn by PsychoPy (no slide images); Hebrew everywhere; keyboard only (no mouse).
- Units: degrees of visual angle (`degFlatPos`) from the monitor profile; WM task in pixels (see below).
- One participant dialog per day; Escape aborts (data kept); `ExperimentHandler` only for data.
- Quizzes: one question per screen, checked after ALL answers; any mistake → message → back to instructions.
- Likert 1–7 left → right, as on the keyboard.

**STEP calibration** (`tasks/calibration/`)
- Ported from Eden Elbaz's `ISI_calcu.py` (paper's Experiment 3: contrast 1 → step 0.2, −0.05/trial,
  min step 0.05, floor 0.1). Verified identical trial-by-trial in `tests/test_step.py`.
- Two deliberate deviations, both following the paper's text (Elbaz et al., 2025, BRM 58:13):
  (1) each run of incorrect answers enters the threshold once (Eq. 5; the original double-counted when
  CWIR reached 50 before trial 50); (2) "seen & incorrect → no change" stops at the minimal step
  (the original's float comparison kept it one trial longer). Her always-true boundary check matches the
  paper ("in each trial") and was simply not ported.
- Stop: CWIR ≥ 50 AND ≥ 50 trials (from her code; not stated in the paper). Cap 300 trials → the day stops,
  the casino game does not run.
- Trial = "feedback only": empty arms → the bandit's own mask–coin–mask sequence → PAS (0–3) → gold/black
  2AFC (arrows; gold side by subject-ID parity). No arm choice in calibration. No UI taken from Eden's code.
- 10 practice trials, 6-question quiz (wording still to be reviewed), break between the 2 blocks.
- Threshold saved in the calibration CSV + `calibration_summary.csv`. Day-2 bandit uses ONLY the value from
  the calibration run in the same session (never an older file, never another ID).

**Bandit** (`tasks/bandit/`)
- 4 practice trials (Day 1 full opacity, Day 2 calibrated), 4 blocks × 50, breaks, coins + payment at the end.
- Miss (6 s) → "לא נבחר מיקום בזמן", counts as a trial. Grey-arm key → "בחירה לא זמינה!" for 3 s penalty,
  trial ends with no outcome, counts as a trial.
- One random seed per session (saved) generates offers, colours, reward walk and outcomes.
- Logged per trial includes `reward_oneback` and `pas` / `twoafc_*` (empty unless probed).
- 9-question quiz (5 from the design + colour, changing odds, time limit, payment).

**Working memory** (`tasks/wm/`)
- Ground truth: github.com/shahar-lab/working_memory_capacity_change_detection_task (not ioc-wm).
  Same CSS geometry (pixels), colours, timings, 5-question quiz, 5 practice trials (set size 1 must be all
  correct), 120 trials, conditions drawn at random (`WM_BALANCED_CONDITIONS = False`, keeps K comparable to
  the lab's 369-participant data). Background #f0f0f0 as in ioc-wm. s/k mapping by ID // 2 (independent of
  the gold side). Live-drawn instruction examples. First task of Day 1.

**Questionnaires** (`tasks/questionnaires/`)
- End of each day, about the casino game: ioc-wm's 2 open questions (typed) then the 36-item IMI with 6
  attention checks. Hebrew translation by Claude, corrected by Alon (items 28, open question 2).

## 5. Open items (code-related)

See the status report ("Points to address and open decisions" and the to-do list) for the full list.
In short: restore the 3 s debug coin; lab-PC monitor values; timing method; awareness probe; reward walk
source; coin pair luminance; Day-2 total display; end-of-day strategy/awareness questions; review of the
calibration quiz wording; move `rl_task/`, `step_calibration/`, `config.json` to `legacy/`.

## 6. Changelog

Add a line for every behaviour change (date – what – why).

- 2026-10-23 – Rewrite of the prototype into the current structure (phases 0–7 of the code-finalization
  plan: shared infrastructure, STEP, bandit, WM, questionnaires, day runners, bot mode, README).
