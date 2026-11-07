"""Pilot: is the STEP calibration reliable?  Calibration -> N_CHECK_TRIALS at the calibrated opacity.

    python calibration_check_main.py                 full pilot (dialog asks for the subject ID)
    python calibration_check_main.py --manual-demo   short version, you play (few trials)
    python calibration_check_main.py --bot           short version, simulated participant

Flow:
  1. The unchanged Day-2 calibration (tasks/calibration/run.py: instructions, quiz, 2 STEP blocks).
  2. N_CHECK_TRIALS trials at the final threshold, fixed opacity, no staircase, no arm choice.
     Each trial is calibration.run_trial(): empty arms -> mask / coin / mask -> PAS -> gold/black 2AFC,
     so it looks exactly like a calibration trial.
  3. A summary is printed in the console and saved as the last rows of the check CSV.

Coin duration and timing method are the experiment's own (config.py: FEEDBACK_COIN_DURATION,
TIMING_METHOD), so the pilot shows the coin exactly as the real Day 2 does.
The only pilot-only setting: data go to data/pilot_calib_check/ (its own calibration_summary.csv;
never mixed with real data).
"""
import math
import os
import sys

import config

# ─── Pilot settings ────────────────────────────────────────────────────────────
N_CHECK_TRIALS = 200
CHECK_BREAK_EVERY = 50            # break screen after every this many check trials
PILOT_DATA_DIR = os.path.join(config.DATA_DIR, 'pilot_calib_check')
CHECK_TASK = 'calibration_check'
SHORT_RUN = {'N_CHECK_TRIALS': 6, 'CHECK_BREAK_EVERY': 3}   # --bot / --manual-demo

# Applied before anything reads it (bot / manual-demo then add their own subfolder to DATA_DIR)
config.DATA_DIR = PILOT_DATA_DIR
if '--bot' in sys.argv or '--manual-demo' in sys.argv:
    N_CHECK_TRIALS, CHECK_BREAK_EVERY = SHORT_RUN['N_CHECK_TRIALS'], SHORT_RUN['CHECK_BREAK_EVERY']

from scipy.stats import binomtest, norm    # noqa: E402

from common.awareness import AwarenessQuestions   # noqa: E402
from common.day import run_day             # noqa: E402
from common.io import TaskData             # noqa: E402
from common.scene import CasinoScene, REWARD   # noqa: E402
from tasks.calibration import run as calibration   # noqa: E402

DAY = 2   # same dialog and file naming as the real Day-2 calibration

# Hebrew messages of the check phase (pilot only, so kept here instead of texts/)
CHECK_START = ('כעת יופיעו עוד {n} צעדים, בדיוק כמו בשלב הכיול.\n'
               'בכל צעד ענו על אותן שתי שאלות: כמה טוב ראיתם את המטבע, ואיזה מטבע ראיתם.\n\n'
               'כשתהיו מוכנים, לחצו על מקש הרווח.')
CHECK_BREAK = 'הפסקה ({done} מתוך {n} צעדים).\nנצלו אותה כמה שאתם צריכים.\n\nכשתהיו מוכנים, לחצו על מקש הרווח.'
CHECK_END = 'סיימתם. תודה!'


# ─── Task 0: record the pilot settings ────────────────────────────────────────
def setup_pilot(ctx):
    ctx.runtime['pilot_n_check_trials'] = N_CHECK_TRIALS   # saved in both CSVs (calibration and check)
    print(f'PILOT: coin {config.FEEDBACK_COIN_DURATION * 1000:.1f} ms, timing {ctx.runtime["timing_method"]}'
          + (f' ({ctx.runtime["coin_frames"]} refreshes at {ctx.runtime["frame_hz_used"]:.2f} Hz)'
             if ctx.runtime['timing_method'] == 'frames' else '')
          + f', {N_CHECK_TRIALS} check trials, data in {config.DATA_DIR}')


# ─── Task 2: the check phase ───────────────────────────────────────────────────
def check(ctx):
    opacity = ctx.calibration_threshold      # set by calibration.run (it stops the day if there is none)
    scene = CasinoScene(ctx.win)
    awareness = AwarenessQuestions(ctx.win, ctx.keys, ctx.screens, ctx.participant['subject'])
    extra = {**ctx.runtime, 'gold_side': awareness.gold_side, 'check_opacity': opacity}
    print(f'Check phase: {N_CHECK_TRIALS} trials at opacity {opacity:.4f}')

    rows = []
    with TaskData(ctx.participant, CHECK_TASK, extra) as td:
        ctx.screens.message(CHECK_START.format(n=N_CHECK_TRIALS))
        for i in range(1, N_CHECK_TRIALS + 1):
            row = calibration.run_trial(ctx, scene, awareness, opacity)
            row = {'phase': 'check', 'check_trial': i, **row}
            rows.append(row)
            td.add_row(row)
            if i % CHECK_BREAK_EVERY == 0 and i < N_CHECK_TRIALS:
                ctx.screens.break_screen(CHECK_BREAK.format(done=i, n=N_CHECK_TRIALS))
        summary = summarize(rows)
        for key, value in summary.items():
            td.add_row({'phase': 'check', 'event': 'check_summary', 'measure': key, 'value': value})
    print_summary(summary, opacity)
    ctx.screens.message(CHECK_END)


# ─── Summary ───────────────────────────────────────────────────────────────────
def summarize(rows):
    """Objective (2AFC) and subjective (PAS) awareness at the calibrated opacity, plus coin timing."""
    n = len(rows)
    n_correct = sum(r['correct'] for r in rows)
    pas0 = [r for r in rows if r['pas'] == 0]
    gold = [r for r in rows if r['coin_shown'] == REWARD]
    black = [r for r in rows if r['coin_shown'] != REWARD]
    # d' / criterion with 'gold' as the signal; log-linear correction (+0.5 / +1) avoids infinite z
    hit = (sum(r['coin_chosen'] == REWARD for r in gold) + 0.5) / (len(gold) + 1)
    fa = (sum(r['coin_chosen'] == REWARD for r in black) + 0.5) / (len(black) + 1)
    durations = [r['coin_duration_measured'] for r in rows if r.get('coin_duration_measured') is not None]
    nominal = config.FEEDBACK_COIN_DURATION
    s = {
        'n_trials': n,
        'accuracy': n_correct / n,
        'binom_p_above_chance': binomtest(n_correct, n, 0.5, alternative='greater').pvalue,
        'n_pas0': len(pas0),
        'accuracy_pas0': (sum(r['correct'] for r in pas0) / len(pas0)) if pas0 else None,
        'binom_p_above_chance_pas0': (binomtest(sum(r['correct'] for r in pas0), len(pas0), 0.5,
                                                alternative='greater').pvalue if pas0 else None),
        'd_prime': norm.ppf(hit) - norm.ppf(fa),
        'criterion': -0.5 * (norm.ppf(hit) + norm.ppf(fa)),
        'p_choose_gold': sum(r['coin_chosen'] == REWARD for r in rows) / n,
    }
    for level in range(4):
        s[f'pas{level}_proportion'] = sum(r['pas'] == level for r in rows) / n
    if durations:
        ms = [d * 1000 for d in durations]
        s.update({'coin_ms_mean': sum(ms) / len(ms), 'coin_ms_min': min(ms), 'coin_ms_max': max(ms),
                  # longer than nominal by more than a quarter refresh-ish -> most likely a dropped frame
                  'coin_n_too_long': sum(d > nominal + 0.008 for d in durations)})
    return s


def print_summary(s, opacity):
    fmt = lambda v: '-' if v is None else (f'{v:.3f}' if isinstance(v, float) and not math.isnan(v) else v)  # noqa: E731
    print('\n' + '=' * 60)
    print(f'CALIBRATION CHECK  (opacity {opacity:.4f}, {s["n_trials"]} trials)')
    print(f'  2AFC accuracy          {fmt(s["accuracy"])}   (binomial p > chance = {fmt(s["binom_p_above_chance"])})')
    print(f'  accuracy when PAS = 0  {fmt(s["accuracy_pas0"])}   (n = {s["n_pas0"]}, '
          f'p = {fmt(s["binom_p_above_chance_pas0"])})')
    print(f"  d'                     {fmt(s['d_prime'])}   criterion {fmt(s['criterion'])}, "
          f"P(choose gold) {fmt(s['p_choose_gold'])}")
    print('  PAS 0/1/2/3            ' + ' / '.join(fmt(s[f'pas{k}_proportion']) for k in range(4)))
    if 'coin_ms_mean' in s:
        print(f'  coin duration (ms)     mean {fmt(s["coin_ms_mean"])}, min {fmt(s["coin_ms_min"])}, '
              f'max {fmt(s["coin_ms_max"])}, too long on {s["coin_n_too_long"]} trials')
    print('=' * 60 + '\n')


TASKS = [
    setup_pilot,          # prints and records the pilot settings
    calibration.run,      # unchanged Day-2 STEP calibration -> ctx.calibration_threshold
    check,                # N_CHECK_TRIALS at the calibrated opacity
]

if __name__ == '__main__':
    run_day(DAY, TASKS)
