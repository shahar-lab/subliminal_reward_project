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
6. **Timing: frame-counted** (`config.TIMING_METHOD = 'frames'`, decided 1 Nov 2026). Every timed screen goes
   through `common/display.py::show()`, which draws + flips the screen N = round(duration × refresh rate)
   times (refresh rate measured by `open_window()`, cached per computer). Every flip time is logged
   (`t_*` columns), and measured durations are saved (`coin_duration_measured` etc.); the window info in
   every CSV has `timing_method`, `frame_hz_used`, `coin_frames`. `TIMING_METHOD = 'core.wait'` restores the
   prototype's flip + `core.wait()`.
   *Why it matters:* a screen can only change at a monitor refresh (16.7 ms at 60 Hz). `core.wait(0.033)`
   ends 0.3 ms before the 2nd refresh, so if drawing the next screen takes longer, the coin lasts 3 refreshes
   (50 ms) instead of 2. With frame counting every flip waits for the refresh, so N flips = exactly N refreshes,
   but every duration must be a whole number of refreshes (33.3 ms works at 60/120 Hz, not at 144 Hz;
   `open_window()` warns), and the screen's flips must be vsync-locked (check with `demo_scene.py`). Coin duration is part of the
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
| try the task yourself, short | `python run_day_1.py --manual-demo` (trial counts: `BOT_SHORT` in `common/bot.py`) |
| add/remove a quiz question | `QUIZ` list in `texts/<task>.py` (`correct` = 0-based index); bot mode answers automatically |
| change instruction pages | `PAGES` in `texts/<task>.py`; picture keys (`offer`, `coins`, `mask`, …) are drawn by `build_pages()` in the task |
| change task order or add a task | the `TASKS` list in `run_day_1.py` / `run_day_2.py` |
| add a data column | add it to the row dict in the task's `run_trial()`; keep the key present (value None) on trials where it doesn't apply |
| change the coin pair / scene greys | `STIMULUS_VERSION` in `config.py` (and in `online/js/config.js`); rationale and how to make a matched coin: `stimuli/COIN_PAIR.md`, `stimuli/make_silver_coin.py` |
| pilot the calibration alone (calibration + trials at the threshold) | `calibration_check_main.py` (settings at its top; see README) |
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
- **Refresh-rate measurement** (~10–20 s) runs only once per computer + screen setup; the result is cached in
  `display_cache.json` (keyed by Windows MachineGuid, screen size, full-screen/window and the refresh rate
  Windows reports, so a new monitor or setting triggers a new measurement). `--remeasure` forces it.
- **Pilot script:** `calibration_check_main.py` changes only `config.DATA_DIR`, in memory, before `run_day`
  (so its data and calibration summary never mix with real data). Everything else is the real code.
- **Testing headless:** the code was developed and tested with PsychoPy 2024.2.4 and 2026.2.4 under a
  virtual display (xvfb). Real timing can only be checked on the real screen (`demo_scene.py`, photodiode).
  Under Xvfb the refresh rate measures ~160 Hz and flips do not wait for a refresh, so
  `coin_duration_measured` is meaningless there (frame-counted coin measured ~17 ms). Check timing on a real screen only.
  On Python 3.13 `pip install psychopy` fails; use Python 3.10/3.11 (PsychoPy 2026.2.4 installs on 3.11;
  Xvfb also needs the system packages libglu1-mesa and libegl1).

## 4. Decision log (what was decided, and why)

Decided by Alon during code finalization, 22–23 Oct 2026:

**General**
- Code drawn by PsychoPy (no slide images); Hebrew everywhere; keyboard only (no mouse).
- Units: degrees of visual angle (`degFlatPos`) from the monitor profile; WM task in pixels (see below).
- One participant dialog per day; Escape aborts (data kept); `ExperimentHandler` only for data.
- Quizzes: one question per screen, checked after ALL answers; any mistake → message → back to instructions.
- Likert 1–7 left → right, as on the keyboard.

**Display timing** (1 Nov 2026)
- Coin 33 ms (`FEEDBACK_COIN_DURATION = 0.033`; the 3 s debug value is gone) and frame-counted timing for
  every screen of every task (`TIMING_METHOD = 'frames'`), so the coin cannot slip to 50 ms when drawing the
  backward mask takes longer than the 0.3 ms `core.wait()` left.

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
- Trial = "feedback only": empty arms → the bandit's own mask–coin–mask sequence → PAS (0–3) → gold/silver
  2AFC (arrows; gold side by subject-ID parity). No arm choice in calibration. No UI taken from Eden's code.
- No practice trials (removed 24 Oct 2026: the quiz is enough); 6-question quiz (wording still to be
  reviewed), break between the 2 blocks.
- Threshold saved in the calibration CSV + `calibration_summary.csv`. Day-2 bandit uses ONLY the value from
  the calibration run in the same session (never an older file, never another ID).

**Bandit** (`tasks/bandit/`)
- 4 practice trials (Day 1 full opacity, Day 2 calibrated), 4 blocks × 50, breaks, coins collected shown at the end. No monetary bonus (no money mentioned anywhere).
- Miss (6 s) → "לא נבחר מיקום בזמן", counts as a trial. Grey-arm key → "בחירה לא זמינה!" for 3 s penalty,
  trial ends with no outcome, counts as a trial. Both messages appear between the reward box and the arms
  (`MESSAGE_POS`).
- One random seed per session (saved) generates offers, colours, reward walk and outcomes.
- Logged per trial includes `reward_oneback` and `pas` / `twoafc_*` (empty unless probed).
- 8-question quiz (5 from the design + colour, changing odds, time limit).

**Working memory** (`tasks/wm/`)
- Ground truth: github.com/shahar-lab/working_memory_capacity_change_detection_task (not ioc-wm).
  Same CSS geometry (pixels), colours, timings, 5-question quiz, 5 practice trials (set size 1 must be all
  correct), 120 trials, conditions drawn at random (`WM_BALANCED_CONDITIONS = False`, keeps K comparable to
  the lab's 369-participant data). Background #f0f0f0 as in ioc-wm. s/k mapping by ID // 2 (independent of
  the gold side). Live-drawn instruction examples. First task of Day 1.

**Coin pair and scene greys** (decided 7 Nov 2026, full rationale in `stimuli/COIN_PAIR.md`)
- Problem: on the grey reward box ('darkgray', 169) the gold coin had ~4% contrast and the black coin ~86%, so the
  no-reward coin was far more noticeable (a conscious "dark flicker = loss" route; threshold driven by the black coin).
- Stimulus version v2: silver no-reward coin with the same mean and SD of luminance as gold
  (`stimuli/make_silver_coin.py`); reward box AND arm boxes medium grey #7c7c7c (124: Day-1 coin clearly visible,
  ~7% contrast at the STEP floor of opacity 0.1); unavailable circles 'darkgray' (169) so they stay visible on the
  arms. Colour difference gold/silver is intended (the signal). Texts: black → silver / שחור → כסוף.
- Old version kept: `STIMULUS_VERSION = 'v1_gold_black'`; old coin files untouched.

**Questionnaires** (`tasks/questionnaires/`)
- End of each day, about the casino game: ioc-wm's 2 open questions (typed) then the 36-item IMI with 6
  attention checks. Hebrew translation by Claude, corrected by Alon (items 28, open question 2).

## 5. Open items (code-related)

See the status report ("Points to address and open decisions" and the to-do list) for the full list.
In short: lab-PC monitor values; verify vsync-locked 33 ms on the lab screen (demo_scene.py, photodiode); awareness probe; reward walk
source; Day-2 total display; end-of-day strategy/awareness questions; review of the
calibration quiz wording; move `rl_task/`, `step_calibration/`, `config.json` to `legacy/`.

## 6. Changelog

Add a line for every behaviour change (date – what – why).

- 2026-10-23 – Rewrite of the prototype into the current structure (phases 0–7 of the code-finalization
  plan: shared infrastructure, STEP, bandit, WM, questionnaires, day runners, bot mode, README).
- 2026-10-24 – Bot mode: real durations with few trials (`BOT_SHORT`), shows the real Likert screen.
- 2026-10-24 – 'בחירה לא זמינה!' / 'too late' messages moved between the reward box and the arms.
- 2026-10-24 – Refresh rate measured once per computer/screen setup and cached (`display_cache.json`).
- 2026-10-24 – Calibration practice trials removed.
- 2026-10-24 – `--manual-demo`: the short bot session played by a human (data in `data/demo/`).
- 2026-10-24 – No monetary bonus: money removed from the casino instructions, quiz (payment question deleted), end screen and data (`payment_shekel`, `COIN_VALUE_SHEKEL`); colour sentence shortened.
- 2026-11-01 – `calibration_check_main.py` (new file, no existing code changed): pilot = Day-2 calibration
  → 200 trials at the calibrated opacity → summary (2AFC accuracy vs chance, accuracy at PAS 0, d′, PAS
  distribution, measured coin duration). Pilot-only, in memory: 33 ms coin, frame-counted mask/coin/mask
  timing, data in `data/pilot_calib_check/`. Purpose: check that the threshold is subliminal, and test
  frame-counted timing on a real screen (open timing decision, principle 6).
- 2026-11-01 – Coin duration set to 33 ms (debug 3 s removed) and frame-counted timing for every screen
  (`TIMING_METHOD = 'frames'`, `common/display.py::show()`); startup warning if 33 ms is not a whole number
  of refreshes; `timing_method`, `frame_hz_used`, `coin_frames` saved with every task. The pilot no longer
  needs its own coin / timing overrides. Why: a 33 ms coin produced with `core.wait()` can last 50 ms.
- 2026-11-01 – `online/`: jsPsych port of both days for an online pilot (Pavlovia + Prolific); see
  `online/README.md` and `online/PILOT_DECISIONS.md`. The lab code is unchanged. If you change `texts/`, run
  `python online/tools/export_hebrew_texts.py`; if you change `tasks/calibration/step.py`, regenerate
  `online/tests/step_reference.json` and run `node online/tests/test_step.js`.
- 2026-11-07 – Coin pair v2 (lab and online): silver no-reward coin luminance-matched to gold, reward box and arm
  boxes #7c7c7c, unavailable circles 'darkgray', texts black → silver. Switch: `STIMULUS_VERSION`; rationale and
  measurements: `stimuli/COIN_PAIR.md`. Why: the black coin was much more noticeable than gold on the old box.
- 2026-11-07 – Online pilot: two Pavlovia projects (day1 / day2) generated from `online/` by
  `online/tools/build_pavlovia.py` (day fixed in `js/day.js`; `?day=` ignored there). Edit only `online/`, then rebuild.
- 2026-11-07 – Online pilot only: welcome-screen approval warning; WM practice with 4 single-square trials (8 in total);
  Day-1 casino instruction page about the brief coin between the masks (`online/PILOT_DECISIONS.md` 27–29).
