"""Bot mode: a simulated participant answers every screen, for checking a whole day quickly.

    python run_day_1.py --bot          answers everything, short durations (a day takes a few minutes)
    python run_day_1.py --bot-real     answers everything, real durations (checks the real session length)

Data go to data/bot/ (never mixed with real participants), subject ID 999, no dialog.
The bot answers quizzes correctly, says it saw nothing (PAS 0), guesses the coin,
chooses random arms (sometimes a grey arm, sometimes no answer) and guesses in the WM task.
"""
import random
import os

import config

BOT_SUBJECT = 999
FAST_DURATION = 0.017   # s, used for every duration in fast mode


def enable(fast=True, seed=None):
    from psychopy import data
    from common import io, ui, keyboard
    from texts import calibration as TC, wm as TW
    from tasks.bandit.run import build_quiz

    config.DATA_DIR = os.path.join(config.DATA_DIR, 'bot')
    config.FULLSCREEN = False
    if fast:
        for name in ('FEEDBACK_COIN_DURATION', 'FEEDBACK_FWD_MASK_DURATION', 'FEEDBACK_BWD_MASK_DURATION',
                     'WAIT_POST_CHOICE', 'WAIT_INITIAL', 'INVALID_MSG_DURATION', 'UNAVAILABLE_CHOICE_DURATION',
                     'WM_FIXATION_DURATION', 'WM_MEMORY_DURATION', 'WM_RETENTION_DURATION',
                     'WM_FEEDBACK_DURATION'):
            setattr(config, name, FAST_DURATION)

    rng = random.Random(seed)
    correct = {q['prompt']: q['correct'] for q in TC.QUIZ + build_quiz() + TW.QUIZ}

    io.get_participant_info = lambda d: {'subject': BOT_SUBJECT, 'day': d, 'experimenter': 'bot',
                                          'date': data.getDateStr()}

    def choice(self, prompt, options, title='', start=1, footer=None):
        return correct.get(prompt, 0), 0.5               # quizzes correct; PAS = 0 (saw nothing)

    def text_entry(self, prompt, **kwargs):
        return 'bot answer', 2.0

    def likert(self, prompt, n_points=7, **kwargs):
        return rng.randint(1, n_points), 0.8

    def wait(self, key_list, max_wait=None):
        if 'f' in key_list:                              # bandit arm choice
            if rng.random() < 0.03:
                return None, None                        # miss
            return rng.choice(config.ARM_KEYS), round(rng.uniform(0.3, 1.5), 3)
        if 's' in key_list:                              # WM same/different
            return rng.choice(list(config.WM_KEYS)), 0.6
        if key_list[:2] == ['left', 'right'] and len(key_list) <= 3:
            return rng.choice(['left', 'right']) if config.INSTR_PREV_KEY in key_list else 'left', 0.4
        return key_list[0], 0.2                          # continue / next page

    ui.Screens.choice = choice
    ui.Screens.text_entry = text_entry
    ui.Screens.likert = likert
    keyboard.Keys.wait = wait
    print(f'BOT MODE ({"fast" if fast else "real durations"}): subject {BOT_SUBJECT}, data in {config.DATA_DIR}')
