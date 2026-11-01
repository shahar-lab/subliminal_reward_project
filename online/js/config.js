// ─── config.js ────────────────────────────────────────────────────────────────
// Every tunable value of the ONLINE pilot. Mirrors ../config.py (the PsychoPy lab
// version); names are kept the same where possible so the two can be compared.
//
// Differences from the lab version are marked  ONLINE:  in the comments.
// All durations are in milliseconds (the lab config uses seconds).
// All sizes/positions are in CSS pixels (the lab config uses degrees; the pixel
// values below are the original pixel layout the degrees were converted from).
//
// URL parameters (read in main.js) override a few values:
//   ?day=1|2            which day to run (default 1)
//   &lang=en|he         participant language (default CONFIG.DEFAULT_LANGUAGE)
//   &PROLIFIC_PID=...   participant ID (Prolific adds it automatically)
//   &short=1            few trials per task, you play (= --manual-demo)
//   &bot=1              few trials per task, everything answered automatically (= --bot)
//   &bot=full           full session answered automatically (= --bot-real)

const CONFIG = {
    EXPERIMENT_NAME: 'subliminal_rl_online_pilot',

    // ─── Language ─────────────────────────────────────────────────────────────
    // ONLINE: English by default (Prolific). Hebrew texts (from ../texts/) are kept in
    // js/texts_he.js; run with &lang=he.
    DEFAULT_LANGUAGE: 'en',

    // ─── Study / platform ─────────────────────────────────────────────────────
    // PLACEHOLDER: Prolific completion codes. While they start with 'XXXX' the
    // participant is NOT redirected at the end (they see a thank-you page).
    COMPLETION_CODE: { 1: 'XXXX_DAY1', 2: 'XXXX_DAY2' },
    SCREENED_OUT_CODE: 'XXXX_SCREENED',   // calibration failure (if CALIB_CAP_ACTION = 'stop')
    ENABLE_CAPTCHA: true,                 // reCAPTCHA, only when running on pavlovia.org (as in ioc-wm)
    RECAPTCHA_SITE_KEY: '6Lfy684qAAAAAEScfxhF2CxfoYJFfhKcQmxe-FuV',   // the lab key used by ioc-wm / ioc-all
    BLOCK_MOBILE: true,                   // desktop-only gate, as in ioc-wm
    PAUSE_ON_BLUR: true,                  // pause + alert when the window loses focus, as in ioc-wm

    // ─── Display ──────────────────────────────────────────────────────────────
    BACKGROUND_COLOR: '#000000',
    TEXT_COLOR: '#ffffff',
    FONT: 'Arial, Helvetica, sans-serif',
    // ONLINE: refresh rate is measured at the start of every session (requestAnimationFrame);
    // every screen of the casino trial lasts a whole number of refreshes:
    // frames = max(1, round(duration_ms / frame_ms)).
    REFRESH_MEASURE_FRAMES: 120,
    MIN_REFRESH_HZ_WARNING: 50,           // logged as a flag only (no exclusion)

    // ─── Keys (KeyboardEvent.code = physical key, so Hebrew layout also works) ─
    ARM_KEYS: ['KeyS', 'KeyF', 'KeyH', 'KeyK'],   // left -> right
    ARM_KEY_NAMES: ['s', 'f', 'h', 'k'],

    // ─── Casino scene layout (px, origin = screen centre, y up) ───────────────
    // Original pixel layout: arms 100 px, circles r = 30 px, x = +-100/+-300 px,
    // feedback box 100 px at y = 200 px, coin/mask 80 px.
    ARM_X_POSITIONS: [-300, -100, 100, 300],
    ARM_Y: 0,
    ARM_SIZE: 100,
    ARM_COLOR: '#a9a9a9',                 // PsychoPy 'darkgray'
    CIRCLE_RADIUS: 30,
    CIRCLE_INACTIVE_COLOR: '#808080',     // 'gray'
    CIRCLE_ACTIVE_COLORS: ['#ff0000', '#0000ff', '#008000', '#ffff00'],   // red, blue, green, yellow (PsychoPy names)
    CIRCLE_COLOR_NAMES: ['red', 'blue', 'green', 'yellow'],
    N_ACTIVE_ARMS: 2,
    FEEDBACK_POS: [0, 200],
    FEEDBACK_BOX_SIZE: 100,
    FEEDBACK_BOX_COLOR: '#a9a9a9',
    COIN_SIZE: 80,
    MASK_SIZE: 80,
    MESSAGE_COLOR: '#ff0000',
    MESSAGE_FONT_PX: 30,
    // message between the reward box and the arms (as MESSAGE_POS in config.py)
    get MESSAGE_POS() {
        return [0, ((this.FEEDBACK_POS[1] - this.FEEDBACK_BOX_SIZE / 2) + (this.ARM_Y + this.ARM_SIZE / 2)) / 2];
    },

    // ─── Stimulus files ───────────────────────────────────────────────────────
    COIN_REWARD_IMAGE: 'stimuli/coin_reward.png',
    COIN_NO_REWARD_IMAGE: 'stimuli/coin_no_reward.png',
    MASK_IMAGES: ['stimuli/mask.png'],

    // ─── Bandit trial timing (ms) ─────────────────────────────────────────────
    CHOICE_TIME_LIMIT: 6000,
    WAIT_INITIAL: 1000,                   // empty arms before the circles appear (ITI)
    WAIT_POST_CHOICE: 1000,               // empty arms after the choice, before the first mask
    FEEDBACK_FWD_MASK_DURATION: 1000,
    // ONLINE: design value 33 ms on both days (the lab config.py still has the 3 s DEBUG value).
    FEEDBACK_COIN_DURATION: { 1: 33, 2: 33 },
    FEEDBACK_BWD_MASK_DURATION: 33,
    INVALID_MSG_DURATION: 1000,           // 'too late' message after a miss
    UNAVAILABLE_CHOICE_DURATION: 3000,    // penalty after choosing a grey arm

    // ─── Feedback opacity ─────────────────────────────────────────────────────
    DAY1_COIN_OPACITY: 1.0,
    // Day 2 uses the final threshold of the calibration run earlier in the same session.

    // ─── Awareness questions (PAS + coin choice) ──────────────────────────────
    // ONLINE: gold side is random per participant (lab: subject-ID parity). Saved as gold_side.
    CHOICE_COIN_X: 150,                   // px
    CHOICE_COIN_SIZE: 100,                // px

    // ─── STEP calibration (Day 2) ─────────────────────────────────────────────
    CALIB_N_BLOCKS: 2,
    CALIB_START_OPACITY: 1.0,
    CALIB_MAX_OPACITY: 1.0,
    CALIB_MIN_OPACITY: 0.1,
    CALIB_INITIAL_STEP: 0.2,
    CALIB_STEP_DECREASE: 0.05,
    CALIB_MIN_STEP: 0.05,
    CALIB_CWIR_STOP: 50,
    CALIB_MIN_TRIALS: 50,
    CALIB_MAX_TRIALS: 300,
    CALIB_GOLD_PROBABILITY: 0.5,
    // ONLINE: what happens if a block reaches CALIB_MAX_TRIALS without converging.
    //   'continue' - use the threshold computed so far (flagged calibration_status = cap_reached_blockN)
    //                and run the casino game anyway (pilot: keep the participant, exclude later if needed)
    //   'stop'     - as in the lab: end the session (participant sent back with SCREENED_OUT_CODE)
    CALIB_CAP_ACTION: 'continue',
    // used only if 'continue' and the staircase has no incorrect answer at all (threshold undefined)
    CALIB_FALLBACK_OPACITY: 0.1,

    // ─── Bandit task (Days 1 and 2) ───────────────────────────────────────────
    BANDIT_N_BLOCKS: 4,
    BANDIT_TRIALS_PER_BLOCK: 50,
    BANDIT_N_PRACTICE: 4,
    BANDIT_SEED: null,                    // null = new random seed each session (saved); integer = fixed
    WALK_INITIAL_PROB: 0.5,
    WALK_STEP_SD: 0.05,
    WALK_MIN_PROB: 0.0,
    WALK_MAX_PROB: 1.0,
    SHOW_TOTAL_DAY: { 1: true, 2: true },
    AWARENESS_PROBE_RATE: { 1: 0.0, 2: 0.0 },   // fraction of trials followed by PAS + coin choice

    // ─── Working memory: change detection (Day 1) ─────────────────────────────
    // Same geometry, colours and timing as ioc-wm / the lab's ground-truth task.
    WM_SQUARE_SIZE: 51.4,
    WM_STEP: 105,
    WM_BACKGROUND: '#f0f0f0',
    WM_TEXT_COLOR: '#333333',
    WM_COLORS: ['black', 'blue', 'brown', 'cyan', 'green', 'magenta', 'orange', 'red', 'yellow'],
    WM_SET_SIZES: [4, 8],
    WM_N_TRIALS: 120,
    WM_N_PRACTICE: 5,                     // first practice trial is set size 1; repeated until all set-size-1 correct
    WM_BALANCED_CONDITIONS: false,
    WM_FIXATION_DURATION: 1000,
    WM_MEMORY_DURATION: 200,
    WM_RETENTION_DURATION: 900,
    WM_RESPONSE_LIMIT: 6000,
    WM_FEEDBACK_DURATION: 500,
    WM_KEYS: ['s', 'k'],                  // ONLINE: same/different mapping random per participant (as ioc-wm)

    // ─── Questionnaires (end of each day) ─────────────────────────────────────
    QUESTIONNAIRE_FINAL_QUESTIONS: true,
    QUESTIONNAIRE_IMI: true,

    // ─── Short / bot sessions (as BOT_SHORT in common/bot.py) ─────────────────
    SHORT: {
        BANDIT_N_BLOCKS: 2, BANDIT_TRIALS_PER_BLOCK: 3, BANDIT_N_PRACTICE: 2,
        WM_N_TRIALS: 6, WM_N_PRACTICE: 3,
        CALIB_MIN_TRIALS: 3, CALIB_CWIR_STOP: 1, CALIB_MAX_TRIALS: 100,
    },
    BOT_RESPONSE_DELAY: 150,              // ms the bot waits before answering
    BOT_WM_ACCURACY: 0.85,
};
