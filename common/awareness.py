"""Awareness questions about the coin, shared by the calibration and (if decided) the Day-2 bandit.

  pas()          - Perceptual Awareness Scale, keys 0-3 (0 = saw nothing).
  coin_choice()  - objective 2AFC: which coin was shown? Both coins at full opacity,
                   left/right arrows; which side gold is on is fixed per participant
                   (counterbalanced by subject ID, see gold_side()).
"""
import os

from psychopy import visual

import config
from common.display import show
from common.scene import REWARD, NO_REWARD
from texts import awareness as T


def gold_side(subject_id):
    """'left' or 'right' - counterbalanced by subject ID parity."""
    even = int(subject_id) % 2 == 0
    return 'left' if even == config.GOLD_LEFT_FOR_EVEN_IDS else 'right'


class AwarenessQuestions:
    def __init__(self, win, keys, screens, subject_id):
        self.win, self.keys, self.screens = win, keys, screens
        self.gold_side = gold_side(subject_id)
        x = config.CHOICE_COIN_X
        gold_x, black_x = (-x, x) if self.gold_side == 'left' else (x, -x)
        self.choice_coins = [
            visual.ImageStim(win, image=os.path.join(config.STIMULI_DIR, config.COIN_REWARD_IMAGE),
                             pos=(gold_x, config.CHOICE_COIN_Y), size=config.CHOICE_COIN_SIZE),
            visual.ImageStim(win, image=os.path.join(config.STIMULI_DIR, config.COIN_NO_REWARD_IMAGE),
                             pos=(black_x, config.CHOICE_COIN_Y), size=config.CHOICE_COIN_SIZE),
        ]
        self.side_to_coin = {'left': REWARD if self.gold_side == 'left' else NO_REWARD,
                             'right': NO_REWARD if self.gold_side == 'left' else REWARD}

    def pas(self):
        """Returns (rating 0-3, rt)."""
        return self.screens.choice(T.PAS_QUESTION, T.PAS_OPTIONS, start=0, footer=T.PAS_FOOTER)

    def coin_choice(self):
        """Returns (REWARD or NO_REWARD, rt)."""
        page = {'text': T.CHOICE_QUESTION,
                'draw': lambda: [c.draw() for c in self.choice_coins]}
        self.keys.clear()
        self.keys.reset_clock_on_flip(self.win)
        show(self.win, lambda: self.screens._draw_page(page, T.CHOICE_FOOTER))
        key, rt = self.keys.wait(['left', 'right'])
        return self.side_to_coin[key], rt
