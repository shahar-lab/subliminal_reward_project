# Subliminal reward learning – PsychoPy experiment

Two-day lab experiment (Shahar lab, TAU). Does reward-driven learning happen when the reward is
presented below awareness?

| Day | Script | Tasks, in order |
|---|---|---|
| 1 | `python run_day_1.py` | Working memory (change detection) → casino game, conscious coin → questionnaires |
| 2 | `python run_day_2.py` | STEP calibration of the coin opacity → casino game at the calibrated opacity → questionnaires |

Each script opens a dialog (subject ID, experimenter; on Day 1 also age, gender, hand) and runs all tasks.

**Changing the code?** Read `DEVELOPMENT.md` first: design principles, where to change what, known gotchas,
the decision log, and a changelog to update.

## Setup (once per computer)

1. **Keep the Python environment outside OneDrive** (OneDrive syncing makes PsychoPy imports take minutes).
   On the experiment PC, keep this repository outside OneDrive too.
   ```
   py -3.11 -m venv C:\envs\psychopy-env
   C:\envs\psychopy-env\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Windows display scaling must be 100%** (Settings → Display → Scale). The experiment warns at start if not.
3. Run `python print_machine_info.py` and copy its values into the `Monitor / window` block of `config.py`
   (resolution, refresh rate). Measure the screen width and the viewing distance in cm.
4. Check everything: `python -m pytest tests` (all tests must pass) and one bot run of each day (below).

## Before collecting real data

- `config.py`: `FEEDBACK_COIN_DURATION` is **3.0 s for debugging** – restore it to `0.033`.
- `config.py`: replace every value marked `PLACEHOLDER` with the experiment PC's values.
- Open decisions that are config switches are listed in the status report (e.g. `REWARD_WALK`,
  `AWARENESS_PROBE_RATE`, `SHOW_TOTAL_DAY`, `WM_BALANCED_CONDITIONS`).

## Lab PC checklist (display and timing)

The coin must be shown for exactly 33 ms in calibration and task alike. On a 60 Hz screen that is
2 refreshes; a missed refresh makes it 50 ms. Check before the first participant:

1. One monitor, native resolution, **Windows scaling 100%**. Turn off adaptive sync (G-Sync/FreeSync),
   HDR, Night light, eye-care / dynamic-contrast modes.
2. Refresh rate **60 or 120 Hz** (33.3 ms = 2 or 4 refreshes). Not 144 Hz (4.75 refreshes).
3. Code and Python environment outside OneDrive; pause sync, notifications and updates; close other programs.
4. Same PC and monitor for both days (opacity looks different on different screens).
5. `python print_machine_info.py` → copy resolution and refresh rate into `config.py`; measure screen width
   and viewing distance (cm), use a chin rest.
6. Restore `FEEDBACK_COIN_DURATION = 0.033` (debug value is 3 s).
7. `python demo_scene.py` (full screen) → `demo_timing.txt`: coin and backward mask should read ~33.3 ms on
   every trial. 50 ms values = dropped refreshes; odd in-between values = timestamps not locked to the
   refresh (seen on the development laptop: 34.8–36.5 ms).
8. If available, verify the 33 ms coin with a photodiode.
9. `python run_day_1.py --bot-real` once, to check session length and smoothness.
10. After the pilot: check `coin_duration_measured` in the bandit and calibration files.

## Running a session

- Keyboard layout: the task keys (s/f/h/k, numbers, arrows, space) also work on the Hebrew layout.
  The participant needs the Hebrew layout (Alt+Shift) only for the two typed questions at the end.
- **Escape** stops the day at any point; everything collected so far is saved.
- **Day 2 calibration stop:** if a calibration block reaches 300 trials without converging, the participant
  sees "please call the experimenter", the console explains why, and the casino game does not start.
- **Crash or stop on Day 2:** run Day 2 again from the start. The casino game only uses the calibration
  value from the same run; it never reads an older file.
- Payment: the end of the casino game shows the coins collected and the amount (also printed in the console
  and saved in the data).

## Data

```
data/
  calibration_summary.csv                         one row per calibration run (all participants)
  sub-007/
    sub-007_day1_<date>.log                       PsychoPy log of the whole day
    sub-007_day1_<date>_config.py                 the config.py used
    sub-007_day1_wm_<date>.csv / .psydat          one file per task (PsychoPy ExperimentHandler)
    sub-007_day1_bandit_<date>.csv / .psydat
    sub-007_day1_questionnaires_<date>.csv / .psydat
    sub-007_day2_calibration_<date>.csv / ...
```
Nothing is ever overwritten (every name carries a date-time stamp). `data/` is not committed to git.
Main columns: see the docstring at the top of each task file in `tasks/`. Columns starting with `t_` are
flip times – the moment a screen appeared, in seconds – so differences give real on-screen durations.

## Checking without a participant

```
python run_day_1.py --bot        simulated participant, short durations (~1 minute)
python run_day_1.py --bot-real   simulated participant, real durations
python demo_scene.py --window    the casino screen and coin sequence + measured timing
```
Bot data go to `data/bot/` with subject ID 999.

## Code layout

```
config.py              every tunable value, with comments
run_day_1.py, run_day_2.py
common/                shared building blocks
  display.py           window, monitor profile, flip timestamps
  scene.py             THE casino screen and the mask–coin–mask sequence (used by bandit and calibration)
  awareness.py         PAS and gold/black choice screens
  ui.py                Hebrew text pages, instructions, quiz, Likert, typed answers
  keyboard.py, io.py   keys / abort, participant dialog and PsychoPy data saving
  day.py, bot.py       day runner, bot mode
tasks/
  calibration/         STEP staircase (step.py, pure logic) + task
  bandit/              schedule (seeded) + casino game
  wm/                  change-detection task (port of shahar-lab/working_memory_capacity_change_detection_task)
  questionnaires/      open questions + IMI
texts/                 all participant-facing Hebrew text
tests/                 python -m pytest tests
legacy/                the original prototype scripts (not used)
```
