"""Runs one experiment day: dialog -> log/config copy -> window -> tasks in order -> end screen.

Each task is a function task(ctx) where ctx carries win, keys, screens,
participant and runtime info.
Add --bot (fast) or --bot-real to the command line for a simulated participant (common/bot.py).
"""
import sys
from types import SimpleNamespace

from psychopy import core, logging

import config

from common.display import open_window
from common import io as data_io
from common.io import start_day_files, runtime_info
from common.keyboard import Keys, AbortExperiment
from common.ui import Screens
from texts import common as T


class StopDay(Exception):
    """A task decided the day cannot continue (e.g. calibration hit its trial cap).

    The message is printed for the experimenter; the participant sees DAY_STOPPED.
    """


def run_day(day, tasks):
    if '--bot' in sys.argv or '--bot-real' in sys.argv:
        from common import bot
        bot.enable(fast='--bot' in sys.argv)
    participant = data_io.get_participant_info(day)   # replaced by a fixed bot ID in bot mode
    start_day_files(participant)
    win, window_info = open_window()
    keys = Keys()
    ctx = SimpleNamespace(win=win, keys=keys, screens=Screens(win, keys),
                          participant=participant, runtime=runtime_info(window_info))
    logging.exp(f'Day {day} start: {participant}')
    try:
        for task in tasks:
            task(ctx)
        ctx.screens.message(T.DAY_END)
    except StopDay as stop:
        logging.warning(f'Day {day} stopped by task: {stop}')
        print(f'\nDAY STOPPED: {stop}\n')
        try:
            ctx.screens.message(T.DAY_STOPPED, keys=[config.CONTINUE_KEY, config.ABORT_KEY], footer='')
        except AbortExperiment:
            pass
    except AbortExperiment:
        logging.warning(f'Day {day} aborted by experimenter (abort key).')
        print('Aborted by experimenter - data collected so far was saved.')
    finally:
        logging.flush()
        win.close()
        core.quit()
