# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

PsychoPy experiment (Shahar lab, TAU) testing whether reward-driven learning happens when the reward coin
is shown below awareness. Two lab days, all participant text in Hebrew, keyboard only.

**Read `DEVELOPMENT.md` before changing behaviour.** It holds the design principles, a "where to change
what" table, gotchas already solved (Hebrew RTL wrapping, typed Hebrew, display scaling, OneDrive), the
decision log, and a changelog. When you change behaviour, add a changelog line (date – what – why) and,
if relevant, a decision-log entry there. `README.md` is the user-facing doc (setup, lab-PC checklist, data files).

## STATUS.md: keep it current

Work here often stops partway through a chat, so `STATUS.md` records where things stand. A new chat should
be able to answer "what are all the open strands?" from that file alone.

- **Read `STATUS.md` at the start of a session.** When asked about open strands, answer from it, check each
  item against the code and git log, and say which ones look stale.
- **Update it after each major step, not only at the end of the session:** a feature or fix finished, a
  decision made, a plan set, or work left half done. Write as you go, since a chat can stop at any point.
- For each open strand, write what it is, its state (not started / in progress / blocked / waiting on a
  decision), the files or branch involved, and the concrete next step. Write half-done work so that
  someone else can pick it up.
- When a strand is finished, remove it and add one line under "Recently done" with the date. Record the
  lasting decisions and behaviour changes in `DEVELOPMENT.md` (decision log and changelog) as well.
  `STATUS.md` holds only what is current and is not a history.

## Commands

```bash
python -m pytest tests                          # all tests (logic only, no screen needed)
python -m pytest tests/test_step.py::test_trial_cap   # single test
python run_day_1.py --bot                       # simulated participant, few trials, real durations
python run_day_2.py --bot-real                  # simulated participant, full session
python run_day_1.py --manual-demo               # play the short bot session yourself
python demo_scene.py --window                   # casino scene + coin timing -> demo_timing.txt
python run_day_1.py --remeasure                 # force refresh-rate re-measurement (cache: display_cache.json)
```

After any change: run the tests and a `--bot` run of both days. Headless runs need a virtual display (xvfb).
Bot data go to `data/bot/`, manual-demo data to `data/demo/` (subject 999). `data/` is never committed.

## Architecture

- **Day = list of task functions.** `run_day_1.py` / `run_day_2.py` define `TASKS`; `common/day.py::run_day`
  handles the dialog, log/config copy, window, bot flags, and runs each `task(ctx)`. `ctx` carries `win`,
  `keys`, `screens`, `participant`, `runtime`. A task stops the day by raising `common.day.StopDay`;
  Escape raises `AbortExperiment` (data so far are kept).
  - Day 1: WM change detection → bandit with fully visible coin → questionnaires.
  - Day 2: STEP calibration of coin opacity → bandit at the calibrated opacity → questionnaires.
    The Day-2 bandit uses only the threshold from the calibration run in the same session.
- **One casino scene.** `common/scene.py::CasinoScene.feedback_sequence()` (forward mask → coin → backward
  mask) is shared by the bandit and the calibration; only opacity differs. Never give calibration its own drawing code.
- **All numbers in `config.py`** (durations, sizes, counts, keys, colours). `PLACEHOLDER` values must be set
  for the lab PC; `DEBUG` values must be restored before real data (notably `FEEDBACK_COIN_DURATION`, 3.0 → 0.033).
- **All participant text in `texts/<task>.py`** (`PAGES`, `QUIZ`, messages); `{placeholders}` are filled from
  `config.py`. Code only lays text out (`common/ui.py::Screens`).
- **Data only via PsychoPy `ExperimentHandler`** (`common/io.py::TaskData`): one date-stamped file per task per
  day, saved on normal end, Escape and crash; `None` written as empty. Extra: `data/calibration_summary.csv`.
  Every row dict keeps the same keys on every trial (None where not applicable); `t_*` columns are flip times.
- **Pure logic separated for tests:** `tasks/calibration/step.py` (STEP staircase, verified trial-by-trial
  against Eden Elbaz's original in `tests/test_step.py`, with two documented deliberate deviations),
  `tasks/bandit/schedule.py` (seeded schedule: offers, colours, reward walk, outcomes), pure functions in `tasks/wm/run.py`.
- **Timing:** durations use `core.wait()` after `win.flip()`; measured durations are logged. Any switch to
  frame-counted timing belongs in `common/display.py::show()` so all tasks change together.
- `common/bot.py` implements `--bot` / `--manual-demo` (short trial counts in `BOT_SHORT`).
- `legacy/` is the original prototype, not used.
