"""Keyboard input with timestamps, and the abort key.

RTs come from PsychoPy's Keyboard timestamps (measured from the clock reset,
which is scheduled on the flip that shows the stimulus), not from the polling loop.
Pressing config.ABORT_KEY anywhere raises AbortExperiment; the task wrapper
saves the data collected so far and the day ends.
"""
from psychopy import core
from psychopy.hardware import keyboard

import config


class AbortExperiment(Exception):
    """Raised when the experimenter presses the abort key."""


class Keys:
    def __init__(self):
        self.kb = keyboard.Keyboard()

    def clear(self):
        self.kb.clearEvents()

    def reset_clock_on_flip(self, win):
        """Call before win.flip(): RTs will be measured from that flip."""
        win.callOnFlip(self.kb.clock.reset)

    def check_abort(self):
        """Non-blocking check for the abort key (call inside long waits/loops)."""
        if self.kb.getKeys([config.ABORT_KEY], waitRelease=False, clear=True):
            raise AbortExperiment()

    def wait(self, key_list, max_wait=None):
        """Wait for one of key_list (or the abort key).

        Returns (key_name, rt) - rt relative to the last clock reset - or
        (None, None) if max_wait seconds passed without a valid key.
        """
        allowed = list(key_list) + [config.ABORT_KEY]
        timer = core.Clock()
        while True:
            keys = self.kb.getKeys(allowed, waitRelease=False, clear=True)
            for k in keys:
                if k.name == config.ABORT_KEY:
                    raise AbortExperiment()
                return k.name, k.rt
            if max_wait is not None and timer.getTime() >= max_wait:
                return None, None
            core.wait(config.KEY_POLL_INTERVAL, hogCPUperiod=config.KEY_POLL_INTERVAL)


def number_key_value(key_name):
    """'3' or 'num_3' -> 3; anything else -> None."""
    return config.NUMBER_KEYS.get(key_name)


def number_keys_for(n_options, start=1):
    """Key names (main row + numpad) for answers start..start+n_options-1."""
    names = []
    for i in range(start, start + n_options):
        names += [str(i), f'num_{i}']
    return names
