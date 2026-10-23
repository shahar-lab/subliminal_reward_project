"""Visual + timing check of the shared infrastructure. Saves no participant data.

    python demo_scene.py            full screen (as in the experiment)
    python demo_scene.py --window   windowed, for a quick look on a laptop

What it shows:
  1. A Hebrew text page, including mixed Hebrew/English (key names) - check the word order.
  2. The casino scene: 6 trials = 3 opacities (1.0, 0.5, 0.2) x gold / black coin,
     using the feedback timing from config.py (coin is still the DEBUG 3 s).
  3. A 2-question quiz (checked at the end) and one Likert item.
At the end it prints the measured refresh rate and the measured coin and
backward-mask durations of every trial, and saves them to demo_timing.txt.
Escape quits at any point.
"""
import os
import sys

from psychopy import core

import config
from common.display import open_window, show
from common.keyboard import Keys, AbortExperiment
from common.scene import CasinoScene, REWARD, NO_REWARD
from common.ui import Screens

OPACITIES = [1.0, 0.5, 0.2]

DEMO_PAGES = [
    {'title': 'בדיקת תצוגה',
     'text': 'זהו עמוד הוראות לדוגמה. בדקו שהטקסט מיושר לימין ושסדר המילים תקין.\n'
             "בדיקת מילים באנגלית: לחצו על המקשים s, f, h או k כדי לבחור מיקום."},
    {'title': 'דוגמה עם תמונות',
     'text': 'כך נראה מטבע הזהב (משמאל) והמטבע השחור (מימין):',
     'images': [(config.COIN_REWARD_IMAGE, (-3, 0), config.COIN_SIZE),
                (config.COIN_NO_REWARD_IMAGE, (3, 0), config.COIN_SIZE)]},
]
DEMO_QUIZ = [
    {'name': 'n_locations', 'prompt': 'כמה מיקומים יש במשחק?', 'options': ['2', '4', '6'], 'correct': 1},
    {'name': 'leftmost_key', 'prompt': 'איזה מקש בוחר את המיקום השמאלי ביותר?',
     'options': ['S', 'F', 'H', 'K'], 'correct': 0},
]


def main():
    windowed = '--window' in sys.argv
    win, win_info = open_window(fullscreen=not windowed)
    keys = Keys()
    screens = Screens(win, keys)
    scene = CasinoScene(win)
    rows = []
    try:
        screens.instructions(DEMO_PAGES)
        for opacity in OPACITIES:
            for outcome in (REWARD, NO_REWARD):
                arms, colours = scene.draw_random_offer()
                scene.set_offer(arms, colours)
                show(win, scene.draw_background, config.WAIT_INITIAL)
                show(win, scene.draw_offer, 1.0)
                show(win, scene.draw_background, config.WAIT_POST_CHOICE)
                keys.check_abort()
                t = scene.feedback_sequence(outcome, opacity)
                rows.append(t)
        passed = screens.quiz(DEMO_QUIZ)
        screens.message('תשובות ' + ('נכונות' if passed else 'שגויות - במשימה האמיתית תחזרו להוראות'))
        value, rt = screens.likert('נהניתי מהמשימה.', low_label='בכלל לא נכון', high_label='נכון מאוד')
        rows.append({'likert_value': value, 'likert_rt': rt})
    except AbortExperiment:
        print('Escape pressed - stopping demo.')
    finally:
        win.close()
    report(win_info, rows)
    core.quit()


def report(win_info, rows):
    lines = [f'refresh expected {win_info["refresh_expected_hz"]} Hz, '
             f'measured {win_info["refresh_measured_hz"]} Hz, window {win_info["window_size_pix"]}',
             f'config: coin {config.FEEDBACK_COIN_DURATION * 1000:.1f} ms, '
             f'backward mask {config.FEEDBACK_BWD_MASK_DURATION * 1000:.1f} ms',
             'opacity  coin       coin_ms  bwd_mask_ms']
    for r in rows:
        if 'coin_opacity' in r:
            lines.append(f'{r["coin_opacity"]:<8} {r["coin_shown"]:<10} '
                         f'{r["coin_duration_measured"] * 1000:7.1f}  {r["bwd_mask_duration_measured"] * 1000:7.1f}')
    text = '\n'.join(lines)
    print('\n' + text)
    path = os.path.join(config.ROOT_DIR, 'demo_timing.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text + '\n')
    print(f'Saved to {path}')


if __name__ == '__main__':
    main()
