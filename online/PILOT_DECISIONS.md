# Online pilot - decisions taken during the port (to verify)

Written by Claude on 2026-11-01, during the port of the PsychoPy experiment to jsPsych. Alon asked
for every open question to be decided reasonably and reported. Each item below gives what was chosen,
the other options, and where to change it. Nothing in the lab (PsychoPy) code was changed.

## Platform and setup

| # | Decision | Other options | Where |
|---|---|---|---|
| 1 | **Pavlovia repository not created.** The cloud session that did the port could not reach gitlab.pavlovia.org (blocked by its network policy). The experiment lives in `online/` of the GitHub repo, ready to push. | Create it from a session that can reach Pavlovia; or push it yourself with the commands in README "Put it on Pavlovia". | `online/README.md` |
| 2 | **One Pavlovia project for both days**, chosen with `?day=1` / `?day=2`; days linked by `PROLIFIC_PID`. | Two separate projects. | `main.js` |
| 3 | **jsPsych 7.3.1 and jQuery are inside the project** (copied from ioc-wm's `jspsych/dist`). They are not loaded from Pavlovia's `lib/vendors/jspsych-7.1.2` the way ioc-wm/ioc-all do, so local runs and Pavlovia runs use identical code. The Pavlovia plugin is ioc-wm's `jspsych-7-pavlovia-2021.12.js`. | Use `lib/vendors` as in ioc (needs commenting/uncommenting script tags for local runs). | `index.html` |
| 4 | **Same scaffolding as ioc-wm:** desktop-only gate, preload, reCAPTCHA (lab key, only on pavlovia.org), fullscreen, pause + alert on blur, `blur_count` / `fullscreen_exit_count` on every row, Pavlovia finish, then Prolific redirect. | Drop CAPTCHA / blur pause for the pilot. | `config.js` (`ENABLE_CAPTCHA`, `PAUSE_ON_BLUR`, `BLOCK_MOBILE`) |
| 5 | **Prolific completion codes are placeholders** (`XXXX_...`). While they start with XXXX, there is no redirect. | | `config.js` `COMPLETION_CODE` |
| 6 | **No consent screen.** ioc-wm also has none (Prolific handles consent). | Add ioc-all's `consent.js` with the IRB text. | |
| 7 | **No monetary bonus**, as in the lab decision: the coins collected are shown at the end. ioc-all pays a £ bonus. | Pay a bonus per coin (needs text and quiz changes). | `texts_*.js` |

## Language and texts

| # | Decision | Other options | Where |
|---|---|---|---|
| 8 | **English by default** (Prolific), Hebrew with `&lang=he`. The English is Claude's translation of the Hebrew lab texts. WM, IMI and the final questions use ioc-wm's English originals. **Please review the English.** | Hebrew only (Israeli sample, e.g. SONA). | `texts_en.js`; `config.js` `DEFAULT_LANGUAGE` |
| 9 | **Hebrew is generated from the lab texts** (`texts/*.py`), so it stays identical to the lab version. Online-only strings (fullscreen, Prolific, ...) were translated to Hebrew by Claude. | | `tools/export_hebrew_texts.py` (`ONLINE_ONLY`) |
| 10 | **Welcome screens for each day** (new; ioc-wm has one). They say it is a two-day study. | | `texts_*.js` `WELCOME_DAY1/2` |
| 11 | The final open question also asks about **strategy in the casino game** (as in ioc-all). The lab version has only the ioc-wm wording. | Keep the ioc-wm wording exactly. | `texts_en.js` `FINAL_QUESTIONS` |

## Timing and display

| # | Decision | Other options | Where |
|---|---|---|---|
| 12 | **Frame-counted timing on a canvas** for the whole casino trial (a custom jsPsych plugin), not `trial_duration`. The refresh rate is measured at the start, and every screen lasts round(duration / frame) frames, at least 1. The coin and masks are drawn in `requestAnimationFrame`. Measured durations and dropped-frame counts are saved for every trial. | Plain jsPsych `html-keyboard-response` with `trial_duration: 33`. That is much less reliable: often 1-3 frames. | `plugin-casino-trial.js`, `display.js` |
| 13 | **Coin 33 ms on both days** (the design value; the lab `config.py` still has the 3 s DEBUG value). On Day 1 the coin is at full opacity but still masked (33 ms backward mask), exactly as the lab code does. **Please confirm Day 1 should be masked.** | Day 1 coin unmasked / longer. | `config.js` `FEEDBACK_COIN_DURATION` (per day) |
| 14 | **No exclusion by refresh rate.** 144 Hz screens give 5 frames = 34.7 ms. `refresh_hz` and `low_refresh_flag` are saved. | Block participants who are not at 60/120 Hz. | `config.js` |
| 15 | **Sizes in CSS pixels**: the original pixel layout (arms 100 px, coin 80 px, ...). There is no chin rest or screen measurement online, so visual angle varies between participants. | Add a virtual-chinrest (credit card) step to scale to degrees. | `config.js` layout block |
| 16 | **WM uses normal jsPsych timing**, as in ioc-wm (200 ms array via `trial_duration`). | Frame-count it too. | `wm.js` |

## Task logic

| # | Decision | Other options | Where |
|---|---|---|---|
| 17 | **Quizzes: all questions on one page, mouse answers, unlimited retries** (as in the lab and ioc-wm). Every attempt is saved (`quiz_attempt`, `quiz_wrong`). The lab shows one question per screen and answers with number keys. | Limit to 3 attempts and screen out, as in ioc-all. | `common.js` `instructionsWithQuiz` |
| 18 | **Calibration cap: `continue`.** If a block reaches 300 trials without converging, the participant goes on with the threshold computed so far. This is flagged in `calibration_status`. The lab stops the day. With no incorrect answers at all, a fallback opacity of 0.1 is used. | `'stop'`: end the session and send the participant back with `SCREENED_OUT_CODE`. | `config.js` `CALIB_CAP_ACTION`, `CALIB_FALLBACK_OPACITY` |
| 19 | **Gold-coin side in the coin choice: random per participant** (saved as `gold_side`). The lab uses subject-ID parity, but Prolific IDs are not numbers. | Derive it from a hash of the ID. | `main.js` |
| 20 | **WM same/different keys: random per participant** (as ioc-wm; saved as `wm_same_key`). The lab uses ID // 2. | | `wm.js` |
| 21 | **Bandit random numbers:** a seeded mulberry32 generator, with the seed saved as `bandit_seed`. Within the online version a seed regenerates the session exactly, but it does not reproduce the PsychoPy sequence for the same seed. The walk rule (Gaussian SD 0.05, start 0.5, clipped to 0-1) is unchanged. | Pre-generated walk files shared by both versions (`REWARD_WALK = 'file'` in the lab). | `schedule.js` |
| 22 | **WM practice: 5 trials** (lab `WM_N_PRACTICE`), repeated until all set-size-1 trials are correct. ioc-wm uses 15. | 15 as ioc-wm. | `config.js` `WM_N_PRACTICE` |
| 23 | **In-task awareness probe off** (`AWARENESS_PROBE_RATE` 0), as in the lab config. When it is on, the PAS and coin-choice questions are already implemented inside the trial. | Turn it on for Day 2, e.g. 0.1. | `config.js` |
| 24 | **No end-of-day awareness questions** beyond the two open questions: still an open item in the lab version. ioc-all has a "felt win rates" slider survey that could be adapted. | | |
| 25 | **Missing values are written as `null`** in the CSV (jsPsych default); the lab writes empty cells. | Post-process, or add a data filter before upload. | |

## What was tested (in this session)

- `node tests/test_step.js`: the JS STEP staircase is identical to `tasks/calibration/step.py`, trial by trial and in the
  threshold, on 12 simulated runs (732 trials).
- `node tests/e2e_bot.js`: both days, in English and Hebrew, run start to end with the automatic participant in
  headless Chromium (60 Hz). It checks trial counts, rewards against the schedule, the coin duration in frames,
  that Day 2 uses the calibrated opacity, the WM K row, and the IMI summary.
- Screenshots of instructions, quiz, casino trial and coin choice (English and Hebrew) were checked by eye.
- **Not tested:** the real Pavlovia upload (no access from the session), reCAPTCHA, real monitors, Firefox and Safari.
  Before collecting data, do one pilot run on Pavlovia (PILOTING mode) and check the CSV in the project's `data/` folder.
