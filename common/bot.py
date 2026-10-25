"""Bot mode: a simulated participant answers every screen, for checking a whole day quickly.

    python run_day_1.py --bot          real durations, but only a few trials per task (BOT_SHORT below)
    python run_day_1.py --bot-real     the full session: real durations and trial counts

    python run_day_1.py --manual-demo  same short session as --bot, but YOU answer every screen
                                       (to learn the task and try all the options; data in data/demo/)

Data go to data/bot/ (never mixed with real participants), subject ID 999, no dialog.
The bot answers quizzes correctly, says it saw nothing (PAS 0), guesses the coin,
chooses random arms (sometimes a grey arm, sometimes no answer), and answers the WM task correctly
with probability BOT_WM_ACCURACY. It pauses BOT_RESPONSE_DELAY s before each answer so you can follow it.
"""
import random
import os

import config

BOT_SUBJECT = 999
BOT_RESPONSE_DELAY = 0.4   # s the bot "thinks" before each answer
BOT_WM_ACCURACY = 0.8      # chance of a correct WM answer (keeps practice from looping)
# --bot: config values replaced to make each task short (durations stay real)
BOT_SHORT = {
    'BANDIT_N_BLOCKS': 2, 'BANDIT_TRIALS_PER_BLOCK': 3, 'BANDIT_N_PRACTICE': 2,
    'WM_N_TRIALS': 6, 'WM_N_PRACTICE': 3,
    'CALIB_MIN_TRIALS': 3, 'CALIB_CWIR_STOP': 1, 'CALIB_MAX_TRIALS': 100,
}


def _setup_session(folder, experimenter, fast):
    """What bot and manual-demo modes share: separate data folder, fixed ID, no dialog, window, few trials."""
    from psychopy import data
    from common import io

    config.DATA_DIR = os.path.join(config.DATA_DIR, folder)
    config.FULLSCREEN = False
    if fast:
        for name, value in BOT_SHORT.items():
            setattr(config, name, value)
    io.get_participant_info = lambda d: {'subject': BOT_SUBJECT, 'day': d, 'experimenter': experimenter,
                                          'date': data.getDateStr()}


def enable_manual_demo():
    """--manual-demo: the short bot session, but every answer comes from the keyboard (nothing automatic)."""
    _setup_session('demo', 'demo', fast=True)
    print(f'MANUAL DEMO: you play; few trials per task; subject {BOT_SUBJECT}, data in {config.DATA_DIR}')


def enable(fast=True, seed=None):
    from psychopy import core
    from common import ui, keyboard
    from tasks.wm import run as wm
    from texts import calibration as TC, wm as TW, common as T_COMMON
    from tasks.bandit.run import build_quiz

    _setup_session('bot', 'bot', fast)

    rng = random.Random(seed)
    correct = {q['prompt']: q['correct'] for q in TC.QUIZ + build_quiz() + TW.QUIZ}

    def show_and_wait(self, page, footer=''):
        from common.display import show
        show(self.win, lambda: self._draw_page(page, footer))
        core.wait(BOT_RESPONSE_DELAY)

    def choice(self, prompt, options, title='', start=1, footer=None):
        show_and_wait(self, {'title': title, 'text': prompt, 'draw': lambda: self._draw_options(options, start)})
        return correct.get(prompt, 0), 0.5               # quizzes correct; PAS = 0 (saw nothing)

    def text_entry(self, prompt, title='', **kwargs):
        show_and_wait(self, {'title': title, 'text': prompt})
        return 'bot answer', 2.0

    def likert(self, prompt, n_points=7, low_label='', high_label='', title=''):
        # same screen as the real Likert item: all points 1..n with the anchor texts under 1 and n
        show_and_wait(self, {'title': title, 'text': prompt,
                             'draw': lambda: self._draw_scale(n_points, low_label, high_label)},
                      footer=T_COMMON.LIKERT_FOOTER.format(n=n_points))
        return rng.randint(1, n_points), 0.8

    wm_correct = {}                                      # correct key of the current WM trial
    original_wm_trial = wm.run_trial

    def wm_trial(ctx, display, trial, same_key, diff_key, key_list):
        wm_correct['key'] = same_key if trial['condition'] == 'same' else diff_key
        return original_wm_trial(ctx, display, trial, same_key, diff_key, key_list)

    def wait(self, key_list, max_wait=None):
        core.wait(min(BOT_RESPONSE_DELAY, max_wait) if max_wait else BOT_RESPONSE_DELAY)
        if 'f' in key_list:                              # bandit arm choice
            if rng.random() < 0.03:
                return None, None                        # miss
            return rng.choice(config.ARM_KEYS), round(rng.uniform(0.3, 1.5), 3)
        if 's' in key_list:                              # WM same/different
            other = [k for k in config.WM_KEYS if k != wm_correct.get('key')][0]
            return (wm_correct.get('key') if rng.random() < BOT_WM_ACCURACY else other), 0.6
        if key_list[:2] == ['left', 'right'] and len(key_list) <= 3:
            return rng.choice(['left', 'right']) if config.INSTR_PREV_KEY in key_list else 'left', 0.4
        return key_list[0], 0.2                          # continue / next page

    ui.Screens.choice = choice
    ui.Screens.text_entry = text_entry
    ui.Screens.likert = likert
    keyboard.Keys.wait = wait
    wm.run_trial = wm_trial
    print(f'BOT MODE ({"short" if fast else "full session"}): subject {BOT_SUBJECT}, data in {config.DATA_DIR}')
