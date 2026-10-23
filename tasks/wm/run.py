"""Visual working-memory capacity: change-detection task (Day 1).

Port of the lab's ground-truth jsPsych task
(github.com/shahar-lab/working_memory_capacity_change_detection_task, index.html + css/my_exp.css):

  instructions -> quiz (5 questions; any mistake -> back to instructions)
  -> practice (WM_N_PRACTICE trials; the first has set size 1; repeated until every
     set-size-1 trial is correct) -> WM_N_TRIALS test trials -> K per set size.
  Trial: fixation 1000 ms -> memory array 200 ms -> fixation 900 ms
         -> one test square (same / different colour) until key or 6 s -> feedback 500 ms.

Geometry: 12 locations, 3 per quadrant along the diagonals (one or two per quadrant
for set size 4 / 8); 6 locations on the vertical midline for set size 1. A "different"
test square takes a colour that was not in the array. Same/different keys (s/k) are
counterbalanced by subject ID (independently of the gold-coin side).
"""
import random

import config
from common.display import show
from common.io import TaskData
from texts import wm as T
from psychopy import visual

TASK = 'wm'
QUADRANT_LETTERS = ['abc', 'def', 'ghi', 'jkl']           # top-left, top-right, bottom-right, bottom-left
QUADRANT_SIGNS = [(-1, 1), (1, 1), (1, -1), (-1, -1)]
MIDLINE = ['upper1', 'upper2', 'upper3', 'lower1', 'lower2', 'lower3']


# ── geometry (pure) ──────────────────────────────────────────────────────────
def _offset(k):
    """Centre offset (px) of the k-th position along a diagonal, from the original CSS corners."""
    return config.WM_STEP * k - config.WM_SQUARE_SIZE / 2


def location_positions():
    """{location name: (x, y)} in px, origin at the screen centre, y up."""
    pos = {}
    for letters, (sx, sy) in zip(QUADRANT_LETTERS, QUADRANT_SIGNS):
        for k, letter in enumerate(letters, start=1):
            pos[letter] = (sx * _offset(k), sy * _offset(k))
    for i, k in enumerate([3, 2, 1]):
        pos[f'upper{i + 1}'] = (0.0, _offset(k))
        pos[f'lower{i + 1}'] = (0.0, -_offset(k))
    return pos


def same_key_for(subject_id):
    """'s' or 'k' = the SAME key; based on ID // 2 so it is independent of the gold-side parity."""
    return config.WM_KEYS[(int(subject_id) // 2) % 2]


# ── trial generation (pure) ──────────────────────────────────────────────────
def pick_locations(rng, set_size):
    if set_size == 1:
        return [rng.choice(MIDLINE)]
    locs = []
    for letters in QUADRANT_LETTERS:
        two = rng.sample(list(letters), 2)
        locs.append(two[0])
        if set_size > 4:
            locs.append(two[1])
    return locs


def make_trial(rng, set_size, condition):
    colours = list(config.WM_COLORS)
    rng.shuffle(colours)
    locs = pick_locations(rng, set_size)
    test_index = rng.randrange(set_size)
    original = colours[test_index]
    test_colour = original if condition == 'same' else rng.choice(colours[set_size:])
    return {'set_size': set_size, 'condition': condition, 'array_colours': colours[:set_size],
            'array_locations': locs, 'test_index': test_index, 'test_location': locs[test_index],
            'original_colour': original, 'test_colour': test_colour}


def condition_sequence(rng, n_trials, set_sizes, balanced):
    conditions = [(s, c) for s in set_sizes for c in ('same', 'diff')]
    if not balanced:                         # ground truth: each trial drawn at random
        return [rng.choice(conditions) for _ in range(n_trials)]
    seq = conditions * (n_trials // len(conditions))
    seq += rng.sample(conditions, n_trials - len(seq))
    rng.shuffle(seq)
    return seq


def practice_sequence(rng, n_trials):
    """Ground truth: first trial set size 1, then any of 1/4/8 x same/diff."""
    first = rng.choice([(1, 'same'), (1, 'diff')])
    rest = [rng.choice([(s, c) for s in (1, 4, 8) for c in ('same', 'diff')]) for _ in range(n_trials - 1)]
    return [first] + rest


def capacity(rows, set_size):
    """K = set size x (2 x accuracy - 1); accuracy over all test trials (no response = incorrect)."""
    acc_values = [r['accuracy'] for r in rows if r['set_size'] == set_size]
    if not acc_values:
        return None, None
    accuracy = sum(a or 0 for a in acc_values) / len(acc_values)
    return accuracy, set_size * (2 * accuracy - 1)


# ── the task ─────────────────────────────────────────────────────────────────
class WMDisplay:
    def __init__(self, win):
        self.win = win
        self.positions = location_positions()
        self.square = visual.Rect(win, units=config.WM_UNITS, width=config.WM_SQUARE_SIZE,
                                  height=config.WM_SQUARE_SIZE, colorSpace='rgb255', lineWidth=0)
        self.fixation = visual.TextStim(win, text='+', units=config.WM_UNITS, height=config.WM_FIXATION_HEIGHT,
                                        color=config.WM_TEXT_COLOR, bold=True)
        self.feedback = visual.TextStim(win, units=config.WM_UNITS, height=config.WM_FIXATION_HEIGHT * 1.6,
                                        color=config.WM_TEXT_COLOR, font=config.FONT,
                                        languageStyle=config.LANGUAGE_STYLE)

    def draw_squares(self, colours, locations, scale=1.0, offset=(0, 0)):
        for colour, loc in zip(colours, locations):
            x, y = self.positions[loc]
            self.square.pos = (x * scale + offset[0], y * scale + offset[1])
            self.square.size = (config.WM_SQUARE_SIZE * scale,) * 2
            self.square.fillColor = config.WM_COLORS[colour]
            self.square.draw()
        self.square.size = (config.WM_SQUARE_SIZE,) * 2

    def draw_fixation(self, scale=1.0, offset=(0, 0)):
        self.fixation.pos = offset
        self.fixation.height = config.WM_FIXATION_HEIGHT * max(scale, 1.0)
        self.fixation.draw()
        self.fixation.pos, self.fixation.height = (0, 0), config.WM_FIXATION_HEIGHT

    def draw_feedback(self, text):
        self.feedback.text = text
        self.feedback.draw()


def run(ctx):
    subject = ctx.participant['subject']
    same_key = same_key_for(subject)
    diff_key = [k for k in config.WM_KEYS if k != same_key][0]
    key_list = list(config.WM_KEYS) + list(config.WM_KEY_ALIASES)
    rng = random.Random()
    display = WMDisplay(ctx.win)
    extra = {**ctx.runtime, 'same_key': same_key, 'diff_key': diff_key}

    previous_bg = ctx.win.color
    ctx.win.color = config.WM_BACKGROUND
    ctx.win.flip()                       # a new window colour shows from the next flip on
    ctx.screens.set_text_color(config.WM_TEXT_COLOR)
    try:
        with TaskData(ctx.participant, TASK, extra) as td:
            fmt = dict(same_key=same_key, diff_key=diff_key)
            quiz = [{**q, 'options': [o.format(**fmt) for o in q['options']]} for q in T.QUIZ]
            ctx.screens.instructions_with_quiz(build_pages(display, fmt), quiz, log=td.add_row,
                                               fail_text=T.QUIZ_FAILED)

            attempt = 1
            while True:                                          # practice until set-size-1 all correct
                ctx.screens.message(T.PRACTICE_START.format(**fmt))
                rows = []
                for i, (size, cond) in enumerate(practice_sequence(rng, config.WM_N_PRACTICE), start=1):
                    row = run_trial(ctx, display, make_trial(rng, size, cond), same_key, diff_key, key_list)
                    rows.append(row)
                    td.add_row({'phase': 'practice', 'practice_attempt': attempt, 'trial': i, **row})
                if all(r['accuracy'] == 1 for r in rows if r['set_size'] == 1):
                    break
                ctx.screens.message(T.PRACTICE_FAILED)
                attempt += 1

            ctx.screens.message(T.EXP_START)
            rows = []
            sequence = condition_sequence(rng, config.WM_N_TRIALS, config.WM_SET_SIZES,
                                          config.WM_BALANCED_CONDITIONS)
            for t, (size, cond) in enumerate(sequence, start=1):
                row = run_trial(ctx, display, make_trial(rng, size, cond), same_key, diff_key, key_list)
                rows.append(row)
                td.add_row({'phase': 'exp', 'trial': t, **row})

            summary = {'phase': 'exp', 'event': 'wm_capacity'}
            ks = []
            for size in config.WM_SET_SIZES:
                acc, k = capacity(rows, size)
                summary[f'accuracy_set{size}'], summary[f'K_set{size}'] = acc, k
                summary[f'n_trials_set{size}'] = sum(r['set_size'] == size for r in rows)
                if k is not None:
                    ks.append(k)
            summary['K_mean'] = sum(ks) / len(ks) if ks else None
            td.add_row(summary)
            print('WM capacity:', {k: v for k, v in summary.items() if k.startswith(('K_', 'accuracy_'))})
            ctx.screens.message(T.EXP_END)
    finally:
        ctx.win.color = previous_bg
        ctx.win.flip()
        ctx.screens.set_text_color(config.TEXT_COLOR)
    return summary


def run_trial(ctx, display, trial, same_key, diff_key, key_list):
    win = ctx.win
    ctx.keys.check_abort()
    t_fix = show(win, display.draw_fixation, config.WM_FIXATION_DURATION)
    t_mem = show(win, lambda: (display.draw_squares(trial['array_colours'], trial['array_locations']),
                               display.draw_fixation()), config.WM_MEMORY_DURATION)
    t_ret = show(win, display.draw_fixation, config.WM_RETENTION_DURATION)
    ctx.keys.clear()
    ctx.keys.reset_clock_on_flip(win)
    t_test = show(win, lambda: (display.draw_squares([trial['test_colour']], [trial['test_location']]),
                                display.draw_fixation()))
    key, rt = ctx.keys.wait(key_list, max_wait=config.WM_RESPONSE_LIMIT)
    response = config.WM_KEY_ALIASES.get(key, key) if key else None
    correct_key = same_key if trial['condition'] == 'same' else diff_key
    accuracy = None if response is None else int(response == correct_key)
    text = T.FEEDBACK_TOO_SLOW if accuracy is None else (T.FEEDBACK_CORRECT if accuracy else T.FEEDBACK_INCORRECT)
    t_fb = show(win, lambda: display.draw_feedback(text), config.WM_FEEDBACK_DURATION)
    return {'set_size': trial['set_size'], 'condition': trial['condition'],
            'array_colours': ';'.join(trial['array_colours']), 'array_locations': ';'.join(trial['array_locations']),
            'test_location': trial['test_location'], 'test_index': trial['test_index'],
            'original_colour': trial['original_colour'], 'test_colour': trial['test_colour'],
            'correct_key': correct_key, 'response_key': key, 'response': response, 'rt': rt,
            'accuracy': accuracy, 't_fixation': t_fix, 't_memory': t_mem, 't_retention': t_ret,
            't_test': t_test, 't_feedback': t_fb, 'memory_duration_measured': t_ret - t_mem}


# ── instruction pages with live examples ─────────────────────────────────────
EXAMPLE_ARRAY = (['red', 'blue', 'green', 'yellow'], ['a', 'e', 'g', 'k'])
EXAMPLE_SCALE = 0.55
EXAMPLE_OFFSET = (0, -110)                 # px - below the page text


def build_pages(display, fmt):
    colours, locs = EXAMPLE_ARRAY
    kw = dict(scale=EXAMPLE_SCALE, offset=EXAMPLE_OFFSET)
    examples = {
        'fixation': lambda: display.draw_fixation(**kw),
        'example_memory': lambda: (display.draw_squares(colours, locs, **kw), display.draw_fixation(**kw)),
        'example_same': lambda: (display.draw_squares([colours[1]], [locs[1]], **kw), display.draw_fixation(**kw)),
        'example_diff': lambda: (display.draw_squares(['orange'], [locs[1]], **kw), display.draw_fixation(**kw)),
    }
    pages = []
    for spec in T.PAGES:
        page = {'title': T.TITLE, 'text': spec['text'].format(**fmt)}
        for key, draw in examples.items():
            if spec.get(key):
                page['draw'] = draw
        pages.append(page)
    return pages
