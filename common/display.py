"""Window creation, monitor profile and flip helpers.

Timing (config.TIMING_METHOD): every timed screen goes through show().
  'frames'    - the screen is drawn and flipped N times, N = round(duration x refresh rate).
                Each flip waits for the next refresh, so the screen lasts exactly N refreshes.
  'core.wait' - one flip, then core.wait(duration) (the original prototype's method).
The refresh rate is the one measured by open_window() (cached per computer). Every flip's
timestamp is returned so it can be logged.
"""
import json
import os
import platform
import sys
import uuid
from datetime import datetime

from psychopy import visual, monitors, core, logging

import config

DISPLAY_CACHE = os.path.join(config.ROOT_DIR, 'display_cache.json')   # per computer, not in git
_frame_hz = None   # refresh rate used for frame-counted timing; set by open_window()


def windows_display_scaling():
    """Windows 'Scale' setting in percent (100 = no scaling), or None elsewhere/unknown."""
    if sys.platform != 'win32':
        return None
    try:
        import ctypes
        return int(ctypes.windll.shcore.GetScaleFactorForDevice(0))
    except Exception:  # noqa: BLE001 - informational only
        return None


def machine_id():
    """Stable ID of this computer: Windows MachineGuid (set when Windows is installed);
    elsewhere host name + network address."""
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography') as key:
                return winreg.QueryValueEx(key, 'MachineGuid')[0]
        except OSError:
            pass
    return f'{platform.node()}-{uuid.getnode():x}'


def reported_refresh_hz():
    """Refresh rate Windows reports for the main display (changes if the monitor or its setting changes)."""
    if sys.platform != 'win32':
        return None
    try:
        import ctypes
        hdc = ctypes.windll.user32.GetDC(0)
        hz = ctypes.windll.gdi32.GetDeviceCaps(hdc, 116)       # 116 = VREFRESH
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return int(hz)
    except Exception:  # noqa: BLE001 - informational only
        return None


def _cache_key(win, fullscreen):
    w, h = (int(v) for v in win.size)
    return (f'{machine_id()}|screen{config.SCREEN_INDEX}|{w}x{h}|'
            f'{"fullscreen" if fullscreen else "window"}|windows_hz={reported_refresh_hz()}')


def _load_cache():
    try:
        with open(DISPLAY_CACHE, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def measure_refresh(win, fullscreen, remeasure=None):
    """Measured refresh rate, cached per computer + screen setup in display_cache.json.

    Measured once; later runs on the same computer, screen size and Windows refresh setting
    reuse it. Run with --remeasure (or delete display_cache.json) to measure again.
    Returns (hz or None, 'cache' / 'measured').
    """
    remeasure = ('--remeasure' in sys.argv) if remeasure is None else remeasure
    cache, key = _load_cache(), _cache_key(win, fullscreen)
    if not remeasure and key in cache:
        entry = cache[key]
        print(f'Refresh rate {entry["refresh_hz"]} Hz (measured on this computer {entry["measured_at"]}; '
              f'--remeasure to measure again)')
        return entry['refresh_hz'], 'cache'
    print('Measuring the screen refresh rate (once per computer/screen setup)...')
    measured = win.getActualFrameRate(nIdentical=20, nMaxFrames=200, nWarmUpFrames=20)
    if measured:
        cache[key] = {'refresh_hz': round(float(measured), 3), 'measured_at': datetime.now().isoformat(timespec='minutes'),
                      'computer': platform.node()}
        try:
            with open(DISPLAY_CACHE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
        except OSError as e:
            logging.warning(f'Could not save {DISPLAY_CACHE}: {e}')
    return (round(float(measured), 3) if measured else None), 'measured'


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
    """Open the experiment window and get the refresh rate (measured once per setup, then cached).

    Returns (win, info) where info holds the refresh values for logging.
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

    measured, source = measure_refresh(win, fullscreen)
    global _frame_hz
    _frame_hz = measured or config.EXPECTED_REFRESH_HZ
    info = {'refresh_expected_hz': config.EXPECTED_REFRESH_HZ,
            'refresh_measured_hz': measured,
            'refresh_source': source,
            'refresh_windows_reported_hz': reported_refresh_hz(),
            'window_size_pix': tuple(int(v) for v in win.size),
            'fullscreen': fullscreen,
            'windows_display_scaling_pct': windows_display_scaling(),
            'timing_method': config.TIMING_METHOD,
            'frame_hz_used': _frame_hz if config.TIMING_METHOD == 'frames' else None,
            'coin_frames': n_frames(config.FEEDBACK_COIN_DURATION) if config.TIMING_METHOD == 'frames' else None}
    check_frame_durations()
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


def n_frames(duration):
    """Number of refreshes that frame-counted timing shows for a duration (at least 1)."""
    return max(1, round(duration * (_frame_hz or config.EXPECTED_REFRESH_HZ)))


def check_frame_durations():
    """Warn if a feedback duration is not (close to) a whole number of refreshes, e.g. 33 ms at 144 Hz."""
    if config.TIMING_METHOD != 'frames':
        return
    hz = _frame_hz or config.EXPECTED_REFRESH_HZ
    for name in ('FEEDBACK_COIN_DURATION', 'FEEDBACK_BWD_MASK_DURATION'):
        duration = getattr(config, name)
        if abs(duration * hz - round(duration * hz)) > config.FRAME_TOLERANCE:
            msg = (f'{name} = {duration * 1000:.1f} ms is not a whole number of refreshes at {hz:.2f} Hz; '
                   f'it will be shown for {n_frames(duration)} refreshes = {n_frames(duration) / hz * 1000:.1f} ms.')
            logging.warning(msg)
            print('WARNING: ' + msg)


def show(win, draw, duration=None):
    """Draw a screen, flip, keep it for `duration` seconds, and return the timestamp of the first flip.

    draw: a function that draws everything for this screen (no flip).
    duration: seconds the screen stays, or None to return right after the flip (the next show() or a
              key wait follows). With TIMING_METHOD 'frames' the screen is redrawn and flipped until it has
              been up n_frames(duration) refreshes; the next screen then appears on the following refresh.
    """
    draw()
    t_flip = win.flip()
    if duration:
        if config.TIMING_METHOD == 'frames':
            for _ in range(n_frames(duration) - 1):
                draw()
                win.flip()
        else:
            core.wait(duration)
    return t_flip
