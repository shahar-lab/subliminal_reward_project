"""The casino scene - the ONE place where the task screen and the coin feedback are drawn.

Both the bandit task and the calibration draw through CasinoScene, so the coin
is shown in exactly the same setting (arms, feedback box, masks, size,
position, background). The only thing a caller changes is the opacity.

All stimuli are created once here and re-used; nothing is loaded from disk
during a trial.
"""
import os
import random

from psychopy import visual

import config
from common.display import show

REWARD = 'reward'
NO_REWARD = 'no_reward'


class CasinoScene:
    def __init__(self, win):
        self.win = win
        n_arms = len(config.ARM_X_POSITIONS)
        self.n_arms = n_arms
        self.arm_positions = [(x, config.ARM_Y) for x in config.ARM_X_POSITIONS]

        self.arms = [visual.Rect(win, size=config.ARM_SIZE, pos=pos,
                                 fillColor=config.ARM_COLOR, lineColor=config.ARM_COLOR)
                     for pos in self.arm_positions]
        self.circles = [visual.Circle(win, radius=config.CIRCLE_RADIUS, pos=pos, edges=64,
                                      fillColor=config.CIRCLE_INACTIVE_COLOR,
                                      lineColor=config.CIRCLE_INACTIVE_COLOR)
                        for pos in self.arm_positions]
        self.feedback_box = visual.Rect(win, size=config.FEEDBACK_BOX_SIZE, pos=config.FEEDBACK_POS,
                                        fillColor=config.FEEDBACK_BOX_COLOR,
                                        lineColor=config.FEEDBACK_BOX_COLOR)
        self.coins = {
            REWARD: visual.ImageStim(win, image=os.path.join(config.STIMULI_DIR, config.COIN_REWARD_IMAGE),
                                     pos=config.FEEDBACK_POS, size=config.COIN_SIZE),
            NO_REWARD: visual.ImageStim(win, image=os.path.join(config.STIMULI_DIR, config.COIN_NO_REWARD_IMAGE),
                                        pos=config.FEEDBACK_POS, size=config.COIN_SIZE),
        }
        self.masks = [visual.ImageStim(win, image=os.path.join(config.STIMULI_DIR, path),
                                       pos=config.FEEDBACK_POS, size=config.MASK_SIZE)
                      for path in config.MASK_IMAGES]
        self.message = visual.TextStim(win, text='', pos=config.FEEDBACK_POS, height=config.TEXT_HEIGHT,
                                       color='red', font=config.FONT, languageStyle=config.LANGUAGE_STYLE)

    # ── offer (which arms are available, and their colours) ──────────────────
    def set_offer(self, active_arms, active_colors):
        """Colour the circles: active arms get their colour, the rest are inactive grey."""
        colour_of = dict(zip(active_arms, active_colors))
        for i, circle in enumerate(self.circles):
            colour = colour_of.get(i, config.CIRCLE_INACTIVE_COLOR)
            circle.fillColor = colour
            circle.lineColor = colour

    @staticmethod
    def draw_random_offer():
        """Random offer: N_ACTIVE_ARMS distinct arms, each with a distinct random colour."""
        arms = sorted(random.sample(range(len(config.ARM_X_POSITIONS)), config.N_ACTIVE_ARMS))
        colours = random.sample(config.CIRCLE_ACTIVE_COLORS, config.N_ACTIVE_ARMS)
        return arms, colours

    # ── drawing primitives (no flip) ─────────────────────────────────────────
    def draw_background(self):
        for arm in self.arms:
            arm.draw()
        self.feedback_box.draw()

    def draw_offer(self):
        self.draw_background()
        for circle in self.circles:
            circle.draw()

    def draw_inactive_circles(self):
        """All four circles in inactive grey (e.g. for calibration screens)."""
        self.draw_background()
        for circle in self.circles:
            fill, line = circle.fillColor, circle.lineColor
            circle.fillColor = circle.lineColor = config.CIRCLE_INACTIVE_COLOR
            circle.draw()
            circle.fillColor, circle.lineColor = fill, line

    def draw_message(self, text):
        self.draw_background()
        self.message.text = text
        self.message.draw()

    def pick_mask(self):
        return random.randrange(len(self.masks))

    # ── the feedback sequence ────────────────────────────────────────────────
    def feedback_sequence(self, outcome, opacity,
                          fwd_mask_duration=None, coin_duration=None, bwd_mask_duration=None):
        """forward mask -> coin -> backward mask -> background.

        outcome: REWARD or NO_REWARD.  opacity: coin opacity (0-1).
        Durations default to the bandit values in config.
        Returns a dict of flip timestamps and the mask indices used (for logging).
        """
        fwd = config.FEEDBACK_FWD_MASK_DURATION if fwd_mask_duration is None else fwd_mask_duration
        coin_dur = config.FEEDBACK_COIN_DURATION if coin_duration is None else coin_duration
        bwd = config.FEEDBACK_BWD_MASK_DURATION if bwd_mask_duration is None else bwd_mask_duration

        coin = self.coins[outcome]
        coin.opacity = opacity
        fwd_idx, bwd_idx = self.pick_mask(), self.pick_mask()

        def draw_mask(idx):
            def _draw():
                self.draw_background()
                self.masks[idx].draw()
            return _draw

        def draw_coin():
            self.draw_background()
            coin.draw()

        t = {}
        if fwd and fwd > 0:
            t['t_fwd_mask'] = show(self.win, draw_mask(fwd_idx), fwd)
        else:
            t['t_fwd_mask'] = None
        t['t_coin'] = show(self.win, draw_coin, coin_dur)
        t['t_bwd_mask'] = show(self.win, draw_mask(bwd_idx), bwd)
        t['t_feedback_end'] = show(self.win, self.draw_background)
        return {**t, 'fwd_mask_idx': fwd_idx if fwd else None, 'bwd_mask_idx': bwd_idx,
                'coin_opacity': opacity, 'coin_shown': outcome,
                'coin_duration_measured': t['t_bwd_mask'] - t['t_coin'],
                'bwd_mask_duration_measured': t['t_feedback_end'] - t['t_bwd_mask']}
