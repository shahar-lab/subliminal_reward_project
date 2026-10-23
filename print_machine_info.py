"""Print (and save to machine_info.txt) what config.py needs to know about this PC.

Run it on the machine that will run the experiment, with the real monitor
attached and set to its final resolution:
    python print_machine_info.py
A full-screen window opens for a few seconds to measure the refresh rate.
Physical screen width (cm) and viewing distance (cm) cannot be measured by
software - measure them with a ruler.
"""
import os
import platform
import sys

lines = []


def out(label, value):
    line = f'{label:<32}{value}'
    print(line, flush=True)
    lines.append(line)


out('python', sys.version.split()[0])
out('platform', platform.platform())

try:
    import psychopy
    out('psychopy', psychopy.__version__)
except ImportError:
    out('psychopy', 'NOT INSTALLED')
    sys.exit(1)

try:
    import pyglet
    try:
        screens = pyglet.canvas.get_display().get_screens()
    except AttributeError:   # newer pyglet
        screens = pyglet.display.get_display().get_screens()
    for i, s in enumerate(screens):
        out(f'screen {i} resolution (pix)', f'{s.width} x {s.height}')
except Exception as e:  # noqa: BLE001 - diagnostics only
    out('screens', f'could not read ({e})')

if sys.platform == 'win32':
    try:
        import ctypes
        scale = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        out('windows display scaling (%)', f'{scale}  (should be 100 on the experiment PC)')
    except Exception as e:  # noqa: BLE001
        out('windows display scaling (%)', f'could not read ({e})')

try:
    import psychtoolbox  # noqa: F401
    out('psychtoolbox (precise keys)', 'available')
except ImportError:
    out('psychtoolbox (precise keys)', 'not available')

print('\nLoading psychopy.visual - the FIRST run in a new environment can take minutes '
      '(Python compiles thousands of files). Later runs take seconds.', flush=True)
_t0 = __import__('time').time()
from psychopy import visual, core  # noqa: E402
out('import psychopy.visual took (s)', f'{__import__("time").time() - _t0:.1f}')
print('Opening a full-screen window to measure the refresh rate (~10-20 s)...', flush=True)

win = visual.Window(fullscr=True, screen=0, units='pix', color='black', checkTiming=False)
msg = visual.TextStim(win, text='Measuring refresh rate - please wait', height=30)
msg.draw()
win.flip()
rate = win.getActualFrameRate(nIdentical=40, nMaxFrames=600, nWarmUpFrames=40)
out('window size (pix)', f'{win.size[0]} x {win.size[1]}')
out('measured refresh rate (Hz)', f'{rate:.3f}' if rate else 'could not measure')
out('frame duration (ms)', f'{1000 / rate:.3f}' if rate else '-')
if rate:
    for ms in (16.7, 33.3, 50.0):
        out(f'  {ms} ms = frames', f'{ms / (1000 / rate):.2f}')
try:
    from psychopy import info
    rti = info.RunTimeInfo(win=win, refreshTest=None, verbose=False)
    for key in ('openGLVendor', 'openGLRenderingEngine', 'openGLVersion', 'windowWinType'):
        if key in rti:
            out(key, rti[key])
except Exception as e:  # noqa: BLE001
    out('opengl info', f'could not read ({e})')
win.close()

out('screen width (cm)', 'MEASURE WITH A RULER (visible image only)')
out('viewing distance (cm)', 'MEASURE (eye to screen)')

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'machine_info.txt')
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print(f'\nSaved to {path}')
core.quit()
