# Online pilot vs lab version: what is the same and what differs

Last updated 7 Nov 2026. "Lab" = the PsychoPy experiment in the repository root (`run_day_1.py`, `run_day_2.py`,
`config.py`); "online" = the jsPsych port in `online/` (Prolific + Pavlovia). The reason for each online decision is in
`PILOT_DECISIONS.md` (numbers in brackets).

## The same in both

- **Tasks and order.** Day 1: working memory, then the casino game with a visible coin, then questionnaires. Day 2:
  STEP calibration, then the casino game at the calibrated opacity, then questionnaires.
- **Casino trial.** Empty arms 1 s, two coloured + two grey circles, choice within 6 s (s/f/h/k), empty arms 1 s,
  forward mask 1 s, coin 33 ms, backward mask 33 ms. Miss: "too late" message 1 s. Grey arm: "unavailable" message,
  3 s penalty. Both count as trials.
- **Casino structure.** 4 practice trials, then 4 blocks × 50 trials with breaks.
- **Reward probabilities.** A Gaussian random walk per arm (start 0.5, SD 0.05, clipped 0–1), generated from a
  per-session seed (decision on a pre-chosen walk pending).
- **Calibration.** Same STEP staircase and parameters (start 1.0, step 0.2 → 0.05, floor 0.1, stop at CWIR ≥ 50 and
  ≥ 50 trials, cap 300), 2 blocks with a break. Same trial: empty arms → mask–coin–mask → PAS (0–3) → gold/silver
  choice (arrows). The JS staircase is verified trial by trial against `tasks/calibration/step.py`
  (`node online/tests/test_step.js`).
- **Calibration that does not converge** (300 trials in a block): the day stops and there is no casino game.
- **Coin pair and greys** (stimulus version v2, `stimuli/COIN_PAIR.md`): gold vs luminance-matched silver coin,
  reward box and arms #7c7c7c, unavailable circles 'darkgray'.
- **Layout** in degrees of visual angle, with the same values in both.
- **Timing method.** Frame-counted: every screen is a whole number of refreshes, from the measured refresh rate.
- **WM task.** Same geometry, colours, timings (fixation 1000, array 200, retention 900, response ≤ 6000,
  feedback 500 ms), 120 trials, set size 4/8 × same/different drawn at random, K per set size.
- **Questionnaires.** The two open questions, then the 36-item IMI with 6 attention checks.
- **Hebrew texts.** The online Hebrew is generated from the lab texts (`online/tools/export_hebrew_texts.py`), so shared
  sentences are identical.

## Differences

| Topic | Lab (PsychoPy) | Online (jsPsych) | Why / where |
|---|---|---|---|
| Participants, platform | in the lab, experimenter present | Prolific, Pavlovia; two Pavlovia projects (day 1 / day 2) built from one source | [2], `online/README.md` |
| Participant ID | numeric subject ID typed in a dialog | `PROLIFIC_PID` from the URL | |
| Language | Hebrew | English by default (translated by Claude); Hebrew with `&lang=he` | [8] |
| Viewing distance, screen size | measured monitor profile, chin rest at 60 cm | assumed 60 cm and 96 CSS px per inch; real screens vary | [15] |
| Refresh rate | measured once per PC and cached; PsychoPy flips | measured at the start of every session (requestAnimationFrame); dropped frames logged per trial (`feedback_long_frames`) | [12], [14] |
| WM timing | frame-counted, like everything else | normal jsPsych timing (as ioc-wm) | [16] |
| Before the tasks | dialog, then the tasks | desktop-only gate, CAPTCHA, fullscreen, refresh measurement, welcome screen with a warning that not completing both days, leaving fullscreen or switching windows means the participation is not approved | [4], [27] |
| Attention tracking | none needed (experimenter present) | `blur_count`, `fullscreen_exit_count` on every row; the experiment pauses with an alert when the window loses focus | [4] |
| Quizzes | one question per screen, number keys, unlimited retries | all questions on one page, mouse; **3 failed attempts end the session** (screened-out code) | [17] |
| Calibration that does not converge | "call the experimenter" screen | "an error occurred, you will be paid nevertheless" screen, normal completion code | [18] |
| Gold side in the coin choice | parity of the subject ID | parity of the character code of the **last** character of the Prolific ID | [19], [20b] |
| WM same/different keys | subject ID // 2 | (that character code // 2) % 2 | [20] |
| WM practice | 5 trials, only the first surely single-square | 8 trials, **4 single-square** (the first one always), the rest set size 4/8 | [28] |
| WM instructions | live-drawn examples | ioc-wm's example pictures | |
| Casino instructions, Day 1 | no page about the masks | extra page: the coin appears very briefly between two "screen" pictures (mask shown), so stay focused on the upper square; Day 2's mask page ends with the same reminder | [29] |
| Money | none; coins collected shown at the end | **bonus**: gold +£0.05, silver −£0.05, never below £0; not shown during the game, shown at its end; saved as `bandit_bonus`; extra quiz question about the silver coin | [7] |
| Open questions | typed in a custom text box (Hebrew input handled) | browser text areas, pasting disabled; the second question also asks about a strategy in the casino game | [11] |
| Random-number generator | Python `random` (Mersenne Twister) | mulberry32; the same seed gives a different session than in the lab | [21] |
| Data files | one PsychoPy ExperimentHandler file per task, empty cells = not applicable | one CSV per session on Pavlovia; missing values written as `null` | [25] |
| End of the day | "call the experimenter" | Pavlovia saves the data, then redirect to Prolific with the completion code | [5] |
| Testing modes | `--bot`, `--bot-real`, `--manual-demo` | `&bot=1`, `&bot=full`, `&short=1` (WM 5 trials; casino and calibration 2 blocks × 5) | `online/README.md` |
| Calibration-only pilot | `calibration_check_main.py` | not available | |

## Keeping the two in sync

- Hebrew texts: edit `texts/*.py`, then run `python online/tools/export_hebrew_texts.py`.
- STEP: if `tasks/calibration/step.py` changes, regenerate `online/tests/step_reference.json`
  (`python online/tests/step_reference.py > online/tests/step_reference.json`) and run `node online/tests/test_step.js`.
- Stimuli and greys: `STIMULUS_VERSION` exists in both `config.py` and `online/js/config.js`; change both.
- Shared numbers (durations, trial counts, STEP parameters, layout degrees) are duplicated in `config.py` and
  `online/js/config.js` with the same names. Change both.
