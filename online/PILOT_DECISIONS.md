# Online pilot - decisions taken during the port (to verify)

Written by Claude on 2026-11-01, during the port of the PsychoPy experiment to jsPsych. Alon asked
for every open question to be decided reasonably and reported. Each item below gives what was chosen,
the other options, and where to change it. Nothing in the lab (PsychoPy) code was changed.

**Alon's answers (2026-11-01), now implemented:** English yes (8); coin 33 ms yes (13); calibration cap
stops the session with an error message and the normal completion code (18); counterbalancing from the first
character of the ID (19, 20); quizzes 3 attempts then out (17); money bonus ±£0.05, floor 0, shown only at the
end (7); sizes in degrees at an assumed 60 cm (15). Still open: one vs two Pavlovia projects (2). 2026-11-03: last ID character for counterbalancing (20b).

## Platform and setup

| # | Decision | Other options | Where |
|---|---|---|---|
| 1 | **Pavlovia repository not created.** The cloud session that did the port could not reach gitlab.pavlovia.org (blocked by its network policy). The experiment lives in `online/` of the GitHub repo, ready to push. | Create it from a session that can reach Pavlovia; or push it yourself with the commands in README "Put it on Pavlovia". | `online/README.md` |
| 2 | **One Pavlovia project for both days**, chosen with `?day=1` / `?day=2`; days linked by `PROLIFIC_PID`. | Two separate projects. | `main.js` |
| 3 | **jsPsych 7.3.1 and jQuery are inside the project** (copied from ioc-wm's `jspsych/dist`). They are not loaded from Pavlovia's `lib/vendors/jspsych-7.1.2` the way ioc-wm/ioc-all do, so local runs and Pavlovia runs use identical code. The Pavlovia plugin is ioc-wm's `jspsych-7-pavlovia-2021.12.js`. | Use `lib/vendors` as in ioc (needs commenting/uncommenting script tags for local runs). | `index.html` |
| 4 | **Same scaffolding as ioc-wm:** desktop-only gate, preload, reCAPTCHA (lab key, only on pavlovia.org), fullscreen, pause + alert on blur, `blur_count` / `fullscreen_exit_count` on every row, Pavlovia finish, then Prolific redirect. | Drop CAPTCHA / blur pause for the pilot. | `config.js` (`ENABLE_CAPTCHA`, `PAUSE_ON_BLUR`, `BLOCK_MOBILE`) |
| 5 | **Prolific completion codes are placeholders** (`XXXX_...`). While they start with XXXX, there is no redirect. | | `config.js` `COMPLETION_CODE` |
| 6 | **No consent screen.** ioc-wm also has none (Prolific handles consent). | Add ioc-all's `consent.js` with the IRB text. | |
| 7 | **DONE - money bonus:** gold coin +£0.05, black coin −£0.05, never below £0; practice not counted. Not shown during the game; shown on the end screen of each day's game. Saved as `bonus_change` / `bonus_total` (per trial) and `bandit_bonus` (every row). Mentioned in the instructions, plus a new quiz question about the black coin. *Choice made:* "presented at the end" = the end of each day's game, because each day is a separate Prolific study and paid separately. | Show only once, at the end of Day 2: the two sessions do not share data, so Day 2 would have to look up Day 1's bonus. | `config.js` `BONUS_*`, `SHOW_TOTAL_DAY` |

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
| 15 | **DONE - sizes in degrees** (the same values as `config.py`), converted assuming 60 cm viewing distance and the CSS standard of 96 px per inch (1° ≈ 39.6 px). Positions use exact visual angle, as `degFlatPos` does. WM stays in pixels, as in ioc-wm and the lab. | Virtual chinrest. | `config.js` `VIEWING_DISTANCE_CM` and the `*_DEG` values |
| 16 | **WM uses normal jsPsych timing**, as in ioc-wm (200 ms array via `trial_duration`). | Frame-count it too. | `wm.js` |

## Task logic

| # | Decision | Other options | Where |
|---|---|---|---|
| 17 | **DONE - quizzes: 3 attempts, then out** (as ioc-all), for every quiz (WM, calibration, casino). After the 3rd failure the participant sees a "we have to end the experiment" screen, the data are saved, and they are sent back with `SCREENED_OUT_CODE`. All questions are on one page, answered with the mouse. | | `config.js` `QUIZ_MAX_ATTEMPTS` |
| 18 | **DONE - calibration cap stops the session:** the participant sees "An error has occurred ... you will be paid for your participation nevertheless", the data are saved (`stopped = calibration_cap`), and they are sent back with the normal `COMPLETION_CODE`. No casino game and no questionnaires. | `'continue'` is still available. | `config.js` `CALIB_CAP_ACTION` |
| 19 | **DONE - gold-coin side** = parity of the character code of the first character of the Prolific ID (even → gold left), as the lab's ID parity. Saved as `gold_side` and `id_code`. | | `main.js`, `config.js` `GOLD_LEFT_FOR_EVEN_IDS` |
| 20 | **DONE - WM same key** = `WM_KEYS[(code // 2) % 2]`, using the same character code, as the lab's ID // 2 (so it is independent of the gold side). Saved as `wm_same_key`. | | `wm.js` |
| 20b | **DONE - last character of the ID.** Prolific IDs are MongoDB ObjectIds. Their first characters are a timestamp of the account creation, so almost all IDs start with `5` or `6` (see the ioc-wm data file names). With the first character, gold side and WM keys follow account age, and they are fully confounded with each other (`5` → gold right + `s` = same; `6` → gold left + `k` = same). The last character is a counter, uniform over 0-9/a-f: balanced and independent. **Decided by Alon (2026-11-03): last character, `ID_CHAR_INDEX: -1`.** | `ID_CHAR_INDEX: -1` | `config.js` `ID_CHAR_INDEX` |
| 21 | **Bandit random numbers:** a seeded mulberry32 generator, with the seed saved as `bandit_seed`. Within the online version a seed regenerates the session exactly, but it does not reproduce the PsychoPy sequence for the same seed. The walk rule (Gaussian SD 0.05, start 0.5, clipped to 0-1) is unchanged. | Pre-generated walk files shared by both versions (`REWARD_WALK = 'file'` in the lab). | `schedule.js` |
| 22 | **WM practice: 5 trials** (lab `WM_N_PRACTICE`), repeated until all set-size-1 trials are correct. ioc-wm uses 15. | 15 as ioc-wm. | `config.js` `WM_N_PRACTICE` |
| 23 | **In-task awareness probe off** (`AWARENESS_PROBE_RATE` 0), as in the lab config. When it is on, the PAS and coin-choice questions are already implemented inside the trial. | Turn it on for Day 2, e.g. 0.1. | `config.js` |
| 24 | **No end-of-day awareness questions** beyond the two open questions: still an open item in the lab version. ioc-all has a "felt win rates" slider survey that could be adapted. | | |
| 25 | **Missing values are written as `null`** in the CSV (jsPsych default); the lab writes empty cells. | Post-process, or add a data filter before upload. | |

## What was tested (in this session)

- `node tests/test_step.js`: the JS STEP staircase is identical to `tasks/calibration/step.py`, trial by trial and in the
  threshold, on 12 simulated runs (732 trials).
- `node tests/e2e_bot.js`: both days, in English and Hebrew, run start to end with the automatic participant in
  headless Chromium (60 Hz). It checks trial counts, rewards against the schedule, the bonus arithmetic, the coin
  duration in frames, that Day 2 uses the calibrated opacity, the WM K row, the IMI summary and the completion code.
  It also runs three stop scenarios: the quiz failed 3 times on Day 1 and on Day 2 (gives the screened-out code),
  and a calibration that cannot converge (gives the error screen and the normal completion code).
- Screenshots of instructions, quiz, casino trial and coin choice (English and Hebrew) were checked by eye.
- **Not tested:** the real Pavlovia upload (no access from the session), reCAPTCHA, real monitors, Firefox and Safari.
  Before collecting data, do one pilot run on Pavlovia (PILOTING mode) and check the CSV in the project's `data/` folder.
