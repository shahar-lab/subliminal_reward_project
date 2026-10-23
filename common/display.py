"""Window creation, monitor profile and flip helpers.

Timing policy (until decided - see status report "Display timing method"):
durations are produced with core.wait() after win.flip(), exactly as before.
The only addition is that every flip's timestamp is returned so it can be logged.
"""
import sys

from psychopy import visual, monitors, core, logging

import config


def windows_display_scaling():
    """Windows 'Scale' setting in percent (100 = no scaling), or None elsewhere/unknown."""
    if sys.platform != 'win32':
        return None
    try:
        import ctypes
        return int(ctypes.windll.shcore.GetScaleFactorForDevice(0))
    except Exception:  # noqa: BLE001 - informational only
        return None


def make_monitor(scale=1.0):
    """Monitor profile built from config (not saved to PsychoPy's Monitor Center).

    scale < 1 (windowed mode): fewer pixels for the same physical width, so the
    window shows the whole full-screen layout, only smaller, instead of cutting it off.
    """
    mon = monitors.Monitor(config.MONITOR_NAME,
                           width=config.SCREEN_WIDTH_CM,
                           distance=config.VIEWING_DISTANCE_CM)
    mon.setSizePix([int(v * scale) for v in config.SCREEN_RESOLUTION])
    return mon


def open_window(fullscreen=None):
    """Open the experiment window and measure the refresh rate.

    Returns (win, info) where info holds the measured refresh values for logging.
    """
    fullscreen = config.FULLSCREEN if fullscreen is None else fullscreen
    size = list(config.SCREEN_RESOLUTION) if fullscreen else \
        [int(v * config.WINDOWED_SCALE) for v in config.SCREEN_RESOLUTION]
    win = visual.Window(size=size,
                        fullscr=fullscreen,
                        screen=config.SCREEN_INDEX,
                        monitor=make_monitor(1.0 if fullscreen else config.WINDOWED_SCALE),
                        units=config.UNITS,
                        color=config.BACKGROUND_COLOR,
                        allowGUI=not fullscreen,
                        checkTiming=False)
    win.mouseVisible = not config.HIDE_MOUSE

    measured = win.getActualFrameRate(nIdentical=20, nMaxFrames=200, nWarmUpFrames=20)
    info = {'refresh_expected_hz': config.EXPECTED_REFRESH_HZ,
            'refresh_measured_hz': round(measured, 3) if measured else None,
            'window_size_pix': tuple(int(v) for v in win.size),
            'fullscreen': fullscreen,
            'windows_display_scaling_pct': windows_display_scaling()}
    scaling = info['windows_display_scaling_pct']
    if scaling not in (None, 100):
        msg = (f'Windows display scaling is {scaling}% - set it to 100% on the experiment PC '
               f'(Settings > Display > Scale) so stimuli are drawn 1:1 on screen pixels.')
        logging.warning(msg)
        print('WARNING: ' + msg)
    if measured is None:
        logging.warning('Could not measure the refresh rate.')
        print('WARNING: could not measure the refresh rate.')
    elif abs(measured - config.EXPECTED_REFRESH_HZ) > config.REFRESH_TOLERANCE_HZ:
        msg = (f'Measured refresh rate {measured:.2f} Hz differs from '
               f'EXPECTED_REFRESH_HZ = {config.EXPECTED_REFRESH_HZ} Hz (see config.py).')
        logging.warning(msg)
        print('WARNING: ' + msg)
    return win, info


def show(win, draw, duration=None):
    """Draw a screen, flip, optionally wait, and return the flip timestamp.

    draw: a function that draws everything for this screen (no flip).
    duration: seconds to wait after the flip (core.wait), or None to return at once.
    """
    draw()
    t_flip = win.flip()
    if duration:
        core.wait(duration)
    return t_flip
