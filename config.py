"""
config.py - every tunable constant ("macro") of the experiment lives here.

Rules:
  * Code never hard-codes a number that appears here.
  * Values marked PLACEHOLDER must be replaced once the lab PC is known
    (run print_machine_info.py on it and copy the numbers in).
  * Values marked DEBUG must be restored before any real data collection.
  * A copy of this file is saved next to every participant's data.
"""
import os

# ─── Paths ─────────────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STIMULI_DIR = os.path.join(ROOT_DIR, 'stimuli')
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# ─── Experiment identity ───────────────────────────────────────────────────────
EXPERIMENT_NAME = 'subliminal_rl'

# ─── Monitor / window ──────────────────────────────────────────────────────────
MONITOR_NAME = 'subliminal_rl_monitor'
SCREEN_RESOLUTION = (1536, 960)    # PLACEHOLDER = Alon's ThinkPad L16 Gen 2 (1920x1200 panel shown at 125% scaling)
SCREEN_WIDTH_CM = 34.5             # PLACEHOLDER = 16" 16:10 laptop panel; measure the lab monitor
VIEWING_DISTANCE_CM = 60.0         # standard (STEP paper: 60 cm with chin rest); fix with a chin rest in the lab
EXPECTED_REFRESH_HZ = 60.0         # laptop measured 60.03 Hz; checked (warning only) at startup
REFRESH_TOLERANCE_HZ = 2.0         # warn if measured rate differs by more than this
SCREEN_INDEX = 0                   # which physical screen to use
FULLSCREEN = True
WINDOWED_SCALE = 0.8               # window size (fraction of SCREEN_RESOLUTION) when not full screen
# 'degFlatPos': positions are exact visual angle on a flat screen,
# sizes use the same deg->cm factor everywhere (shapes are not distorted).
UNITS = 'degFlatPos'
BACKGROUND_COLOR = 'black'
HIDE_MOUSE = True

# ─── Keys ──────────────────────────────────────────────────────────────────────
ABORT_KEY = 'escape'                       # quits the current day; data so far is saved
ARM_KEYS = ['s', 'f', 'h', 'k']            # left -> right, one per arm
CONTINUE_KEY = 'space'
INSTR_NEXT_KEY = 'left'                    # Hebrew reads right-to-left: "next" is to the left
INSTR_PREV_KEY = 'right'
# number keys accepted for quiz / Likert answers (main row and numpad)
NUMBER_KEYS = {str(i): i for i in range(10)}
NUMBER_KEYS.update({f'num_{i}': i for i in range(10)})

# ─── Text ──────────────────────────────────────────────────────────────────────
FONT = 'Arial'
LANGUAGE_STYLE = 'RTL'           # Hebrew
TEXT_COLOR = 'white'
TEXT_HEIGHT = 0.8                # deg
TEXT_WRAP_WIDTH = 26.0           # deg
TITLE_HEIGHT = 1.1               # deg
FOOTER_HEIGHT = 0.6              # deg
FOOTER_POS = (0.0, -8.6)         # deg (screen half-height is ~10 deg on the laptop)
HIGHLIGHT_COLOR = 'gold'
TITLE_Y = 8.8                    # deg (top edge of the title)
BODY_TOP_Y = 7.0                 # deg (top edge of the page text)
QUIZ_OPTIONS_TOP_Y = 2.5         # deg - first answer row
QUIZ_OPTION_SPACING = 1.5        # deg between answer rows
QUIZ_NUMBER_COLUMN_WIDTH = 1.5   # deg between the answer number and its text
LIKERT_WIDTH = 16.0              # deg from point 1 to the last point
LIKERT_Y = -1.0                  # deg
TEXT_ENTRY_Y = -3.0              # deg - centre of the typed-answer box
TEXT_ENTRY_HEIGHT = 6.0          # deg
LIKERT_LOW_ON_RIGHT = False      # False: 1 on the left ... 7 on the right, as on the keyboard

# ─── Casino scene layout (deg) ─────────────────────────────────────────────────
# Initial values = the original pixel layout (arms 100 px, circles r=30 px,
# coin 80 px, x = +-100/+-300 px, feedback y = 200 px) converted with the
# PLACEHOLDER monitor above (1 px ~= 0.0264 deg). Re-check on the lab monitor.
ARM_X_POSITIONS = [-7.9, -2.6, 2.6, 7.9]   # left -> right
ARM_Y = 0.0
ARM_SIZE = (2.6, 2.6)
ARM_COLOR = 'darkgray'
CIRCLE_RADIUS = 0.8
CIRCLE_INACTIVE_COLOR = 'gray'
CIRCLE_ACTIVE_COLORS = ['red', 'blue', 'green', 'yellow']
N_ACTIVE_ARMS = 2

FEEDBACK_POS = (0.0, 5.3)          # the box the coin / masks appear in
FEEDBACK_BOX_SIZE = (2.6, 2.6)
FEEDBACK_BOX_COLOR = 'darkgray'
COIN_SIZE = (2.1, 2.1)
MASK_SIZE = (2.1, 2.1)

# ─── Stimulus files (relative to STIMULI_DIR) ──────────────────────────────────
# Which coin pair to use is an open decision (status report) - switch here.
COIN_REWARD_IMAGE = os.path.join('rewards', 'coin_reward.png')
COIN_NO_REWARD_IMAGE = os.path.join('rewards', 'coin_no_reward.png')
MASK_IMAGES = [os.path.join('masks', 'mask.png')]   # one or more; one is drawn per mask screen

# ─── Bandit trial timing (seconds) ─────────────────────────────────────────────
CHOICE_TIME_LIMIT = 6.0
WAIT_INITIAL = 1.0               # empty arms before circles appear (acts as ITI)
WAIT_POST_CHOICE = 1.0           # empty arms after the choice, before the first mask
FEEDBACK_FWD_MASK_DURATION = 1.0
FEEDBACK_COIN_DURATION = 3.0     # DEBUG - design value is 0.033; kept long so the coin can be inspected
FEEDBACK_BWD_MASK_DURATION = 0.033
INVALID_MSG_DURATION = 1.0       # 'too late' message after a miss
UNAVAILABLE_CHOICE_DURATION = 3.0   # penalty screen after choosing a grey (unavailable) arm
KEY_POLL_INTERVAL = 0.001        # sleep between keyboard polls (RT comes from key timestamps)

# ─── Feedback opacity ──────────────────────────────────────────────────────────
DAY1_COIN_OPACITY = 1.0
# Day 2 always uses the final threshold of the calibration run earlier in the same session.

# ─── Data ──────────────────────────────────────────────────────────────────────
SUBJECT_ID_DIGITS = 3            # sub-007
SAVE_PICKLE = True               # PsychoPy .psydat next to the .csv
SAVE_LOG_FILE = True             # PsychoPy .log file (written continuously, crash backup)

# ─── Awareness questions (PAS + coin choice) ───────────────────────────────────
GOLD_LEFT_FOR_EVEN_IDS = True    # 2AFC side of the gold coin: even IDs left, odd IDs right
CHOICE_COIN_X = 4.0              # deg - the two coins shown on the coin-choice screen
CHOICE_COIN_Y = 0.0
CHOICE_COIN_SIZE = (2.6, 2.6)

# ─── STEP calibration (Day 2) ──────────────────────────────────────────────────
# Trial = empty arms (WAIT_POST_CHOICE) -> the bandit's feedback sequence
# (FEEDBACK_* durations above) at the staircase opacity -> PAS -> coin choice.
CALIB_N_BLOCKS = 2
CALIB_START_OPACITY = 1.0
CALIB_MAX_OPACITY = 1.0          # initial upper boundary
CALIB_MIN_OPACITY = 0.1
CALIB_INITIAL_STEP = 0.2
CALIB_STEP_DECREASE = 0.05       # per trial
CALIB_MIN_STEP = 0.05
CALIB_CWIR_STOP = 50
CALIB_MIN_TRIALS = 50            # per block
CALIB_MAX_TRIALS = 300           # per block; reaching it stops the day (experimenter is called)
CALIB_GOLD_PROBABILITY = 0.5     # chance that the shown coin is gold
CALIB_PRACTICE_OPACITIES = [1.0, 0.9, 0.8, 1.0, 0.7, 0.6, 0.9, 0.5, 0.4, 0.3]   # shuffled per participant
CALIB_SUMMARY_FILE = 'calibration_summary.csv'   # in DATA_DIR, one row per calibration run
INSTR_SCENE_SHIFT_Y = -6.0       # deg - the casino-scene example on instruction pages is drawn this much lower

# ─── Bandit task (Days 1 and 2) ────────────────────────────────────────────────
BANDIT_N_BLOCKS = 4
BANDIT_TRIALS_PER_BLOCK = 50     # a missed trial (no choice in time) still counts as a trial
BANDIT_N_PRACTICE = 4            # practice trials (own random walk; Day 1 full opacity, Day 2 calibrated)
BANDIT_SEED = None               # None = new random seed each session (saved in the data); int = fixed
# Reward probabilities: 'live' = Gaussian random walk generated from the seed (original rule),
# 'file' = read per-trial probabilities from BANDIT_WALK_FILES (CSV with columns p0,p1,p2,p3).
REWARD_WALK = 'live'
WALK_INITIAL_PROB = 0.5
WALK_STEP_SD = 0.05
WALK_MIN_PROB = 0.0
WALK_MAX_PROB = 1.0
BANDIT_WALK_FILES = {1: os.path.join('schedules', 'walk_day1.csv'),
                     2: os.path.join('schedules', 'walk_day2.csv')}
# Hebrew keyboard layout: the same physical keys can arrive as Hebrew letters
ARM_KEY_ALIASES = {'ד': 's', 'כ': 'f', 'י': 'h', 'ל': 'k'}
# Payment
COIN_VALUE_SHEKEL = 0.05         # per gold coin (5 agorot)
SHOW_TOTAL_DAY = {1: True, 2: True}   # show coins/payment at the end of the task (open decision for Day 2)
# In-task awareness probe (open decision): fraction of trials followed by PAS + coin choice
AWARENESS_PROBE_RATE = {1: 0.0, 2: 0.0}

# ─── Working memory: change detection (Day 1) ──────────────────────────────────
# Ground truth: github.com/shahar-lab/working_memory_capacity_change_detection_task (index.html, my_exp.css).
# Geometry is in the original's CSS pixels and drawn in screen pixels (WM_UNITS = 'pix'),
# so on a 100%-scaled screen it is identical to the web task.
WM_UNITS = 'pix'
WM_SQUARE_SIZE = 51.4            # px
WM_STEP = 105                    # px between positions along each diagonal ("vis_angle_px")
WM_FIXATION_HEIGHT = 15.8        # px (font size of the '+')
WM_BACKGROUND = '#f0f0f0'        # as in ioc-wm (light grey; one of the colours is black)
WM_TEXT_COLOR = '#333333'
# The 9 colours (RGB 0-255, read from the original square images)
WM_COLORS = {'black': (0, 0, 0), 'blue': (68, 114, 196), 'brown': (128, 64, 0), 'cyan': (0, 255, 255),
             'green': (0, 176, 80), 'magenta': (255, 0, 254), 'orange': (255, 128, 65), 'red': (254, 0, 0),
             'yellow': (255, 255, 0)}
WM_SET_SIZES = [4, 8]
WM_N_TRIALS = 120
WM_N_PRACTICE = 5                # first practice trial is set size 1; repeated until all set-size-1 trials correct
# How the 4 conditions (set size 4/8 x same/different colour) are assigned to the WM_N_TRIALS trials:
#   False = as in the ground-truth task: each trial's condition is drawn at random (with replacement),
#           so counts vary between participants (~30 +- 5 each of 120). Keeps K comparable to the
#           lab's earlier data (369 participants), which were collected this way.
#   True  = exactly equal counts (30 of each for 120 trials), shuffled. Slightly more precise K
#           per set size, but differs from how the reference data were collected.
WM_BALANCED_CONDITIONS = False
WM_FIXATION_DURATION = 1.0       # before the array
WM_MEMORY_DURATION = 0.2
WM_RETENTION_DURATION = 0.9
WM_RESPONSE_LIMIT = 6.0
WM_FEEDBACK_DURATION = 0.5
WM_KEYS = ('s', 'k')
WM_KEY_ALIASES = {'ד': 's', 'ל': 'k'}   # Hebrew keyboard layout

# ─── End-of-day questionnaires ─────────────────────────────────────────────────
QUESTIONNAIRE_FINAL_QUESTIONS = True   # the two open questions from ioc-wm (typed answers)
QUESTIONNAIRE_IMI = True               # 36-item Intrinsic Motivation Inventory (incl. 6 attention checks)
TEXT_MIN_CHARS = 1                     # an open answer cannot be empty
