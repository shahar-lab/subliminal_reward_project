# Subliminal reward learning - ONLINE PILOT (jsPsych / Pavlovia)

A jsPsych port of the two-day PsychoPy lab experiment in the parent folder, for an online pilot
(Prolific + Pavlovia), built the same way as the lab's ioc-wm and ioc-all experiments.
Timing in a browser is less reliable than in the lab; the pilot only checks for general effects.

| Day | URL | Tasks, in order |
|---|---|---|
| 1 | `index.html?day=1` | Working memory (change detection), then the casino game with a fully visible coin, then questionnaires |
| 2 | `index.html?day=2` | STEP calibration of the coin opacity, then the casino game at the calibrated opacity, then questionnaires |

Locally, choose the day with `?day=`. On Pavlovia each day is its own project, built from this folder with the
day fixed (see "Put it on Pavlovia"). The two sessions are linked by `PROLIFIC_PID`.

## Run it locally (no Pavlovia needed)

```
cd online
python -m http.server 8000
```
Then open in Chrome:

| URL | What it does |
|---|---|
| `http://localhost:8000/index.html?day=1` | the real Day 1 (CSV downloaded at the end) |
| `...?day=2&short=1` | short session (few trials per task), **you** play (= `--manual-demo`) |
| `...?day=2&bot=1` | short session, answered automatically (= `--bot`) |
| `...?day=1&bot=full` | full session, answered automatically (= `--bot-real`) |
| add `&lang=he` | Hebrew instead of English |

Checks: `node tests/test_step.js` checks that the STEP staircase gives the same result as the Python version, trial by trial.
`node tests/e2e_bot.js` runs both days, in English and Hebrew, with the bot in headless Chromium and checks the data
(needs Playwright). `node tests/test_build.js` checks the Pavlovia build: the day is fixed, and `.git/` and `data/` are kept.

## Put it on Pavlovia: two projects, built from this one folder

Each day is its own Pavlovia project, so participants cannot switch days by editing the URL:
`Shahar_Lab/subliminal-reward-pilot-day1` and `Shahar_Lab/subliminal-reward-pilot-day2`.
Both are **generated** from this folder (the single source). Always edit here, never in the built folders.

1. Build the two projects:
   ```
   python online/tools/build_pavlovia.py            (from the repository root)
   ```
   This writes `online/build/subliminal-reward-pilot-day1` and `-day2` (git-ignored). Each is a complete
   experiment with the day fixed in `js/day.js`, so `?day=` is ignored there.
   Use `--out <folder>` to build somewhere else, e.g. next to your Pavlovia clones.
2. **First time:** on https://gitlab.pavlovia.org create the two projects in the `Shahar_Lab` group (names
   above). Then push each built folder; the build script prints the exact commands:
   ```
   cd online/build/subliminal-reward-pilot-day1
   git init -b master && git add -A && git commit -m "Online pilot"
   git remote add origin https://gitlab.pavlovia.org/Shahar_Lab/subliminal-reward-pilot-day1.git
   git push -u origin master
   ```
   and the same for `-day2`.
3. **Later updates:** change the code in `online/`, then run the build again with `--out` pointing at the folder
   that holds your two clones. A folder that is already a clone is updated in place: everything is replaced
   except `.git/` and `data/`, so participants' results are never touched. Then `git add -A`, commit and push in each.
4. On pavlovia.org, for **each** project: set it to **PILOTING** (pilot runs get a token in the URL). Under
   *Saving results*, choose CSV and turn on *save incomplete results* (recommended).
5. Set it to **RUNNING**. The Prolific study URLs:
   - Day 1: `https://run.pavlovia.org/Shahar_Lab/subliminal-reward-pilot-day1/?PROLIFIC_PID={{%PROLIFIC_PID%}}&STUDY_ID={{%STUDY_ID%}}&SESSION_ID={{%SESSION_ID%}}`
   - Day 2: the same with `-day2`. Make the Day-2 Prolific study available only to Day-1 completers
     (custom allowlist).
6. Put the Prolific completion codes in `js/config.js` **before building**:
   - `COMPLETION_CODE`, for each day: finished, or calibration error (the participant is paid);
   - `SCREENED_OUT_CODE`: quiz failed 3 times.
   While a code starts with `XXXX`, participants are not redirected.
7. Pay the bonus: the `bandit_bonus` column (in £) of each session's CSV.

Data: one CSV per session in each Pavlovia project's `data/` folder, named
`<experiment>_<PROLIFIC_PID>_day<1|2>_SESSION_<date>.csv`.

## Code layout

```
index.html                 loads everything (jsPsych 7.3.1 + jQuery are in this folder: no CDN, no lib/vendors)
js/config.js               EVERY tunable value (same names as ../config.py; differences marked ONLINE)
js/texts_en.js             all English participant text
js/texts_he.js             all Hebrew text - GENERATED from ../texts/*.py by tools/export_hebrew_texts.py
js/main.js                 session setup + the two day timelines (as run_day_1.py / run_day_2.py)
js/day.js                  FIXED_DAY: null here (day from the URL); 1 or 2 in the built Pavlovia projects
js/plugin-casino-trial.js  jsPsych plugin: one casino trial (bandit or calibration), canvas, frame-counted
js/display.js              THE casino scene drawing, refresh-rate measurement, frame sequences
js/step.js                 STEP staircase (port of ../tasks/calibration/step.py)
js/schedule.js             seeded random numbers + bandit schedule (port of ../tasks/bandit/schedule.py)
js/wm.js, calibration.js, bandit.js, questionnaires.js   the tasks
js/common.js               instructions + quiz loop, message screens, bot helpers
stimuli/                   coins and mask (from ../stimuli), WM squares and examples (from ioc-wm)
jspsych/jspsych-7-pavlovia-2021.12.js   Pavlovia plugin (from ioc-wm)
tests/, tools/             checks, the Hebrew text exporter, and build_pavlovia.py (makes the two Pavlovia projects)
```

## Timing

- The refresh rate is measured at the start (`refresh_hz`, `frame_ms`, saved on every row).
- In the casino trial every screen lasts a whole number of refreshes, counted with
  `requestAnimationFrame`. Number of frames = round(duration / frame duration), and at least 1. The coin is 33 ms:
  2 frames at 60 Hz, 4 at 120 Hz, 5 (34.7 ms) at 144 Hz.
- Saved per trial: `coin_frames`, `coin_duration_measured` and `bwd_mask_duration_measured` (from frame timestamps),
  and `feedback_long_frames` (frames longer than 1.5 refreshes, i.e. probably dropped).
  Exclude trials or participants on these after the pilot.
- WM and questionnaires use normal jsPsych timing, as in ioc-wm.

## Data columns (main ones)

Every row: `subject_id`, `day`, `language`, `run_mode`, `refresh_hz`, `gold_side`, `id_code`, `wm_same_key`,
`bandit_bonus`, `stopped` (empty, `quiz_failed_<task>` or `calibration_cap`), `blur_count`, `fullscreen_exit_count`,
`device_type`, `screen_width/height`.

- **Casino trials** (`trial_type = casino-trial`, `task = bandit | calibration`):
  - which trial: `phase` (practice / main / calibration), `block`, `trial`
  - the offer: `offered_arms`, `colour_arm0-3`, `p_arm0-3`, `outcome_draw`
  - the response: `choice_key`, `choice_arm`, `choice_colour`, `rt`, `missed`, `unavailable_choice`
  - the outcome: `reward`, `reward_oneback`, `coins_total`, `bonus_change`, `bonus_total` (£), `coin_shown`, `coin_opacity`
  - timing: `t_*` (frame timestamps, in ms)
  - awareness answers: `pas`, `seen`, `coin_chosen`, `twoafc_correct`
  - calibration only: all STEP columns (`boundary_*`, `cwir_*`, `step`, `next_intensity`, ...)
- **Calibration summary rows**: `event = block_threshold` and `event = final_threshold` (`final_threshold`, `calibration_status`).
- **WM**: `screen = wm_test` rows (`set_size`, `condition`, `accuracy`, `rt`, ...), and the `event = wm_capacity` row (`K_set4`, `K_set8`, `K_mean`).
- **Quizzes**: `screen = quiz` (`quiz_attempt`, `quiz_passed`, `quiz_wrong`).
- **IMI**: `phase = imi` (`imi_response` 1-7, `attention_failed`), and the `event = imi_summary` row.
