# Status – open strands

Snapshot of where the work stands, for picking up after an interrupted chat. Update it after every major
step (see `CLAUDE.md`). History belongs in `DEVELOPMENT.md` (decision log and changelog).

_Last updated: 2026-11-01_

## Open strands

### Before real data collection
- **Debug coin duration**: `FEEDBACK_COIN_DURATION` in `config.py` is 3.0 s (DEBUG). Next: restore to `0.033`.
- **Lab-PC monitor values**: every `PLACEHOLDER` in `config.py` (resolution, screen width, refresh rate,
  viewing distance) is still set for Alon's laptop. Next: on the lab PC, run `print_machine_info.py`, measure
  the screen width and viewing distance, then work through the README's "Lab PC checklist".

### Open design decisions (waiting on a decision)
- **Timing method**: `core.wait()` vs frame-counted. If switched, change it in `common/display.py::show()`.
- **In-task awareness probe**: `AWARENESS_PROBE_RATE`.
- **Reward walk source**: `REWARD_WALK`.
- **Coin pair luminance matching**: `COIN_REWARD_IMAGE` / `COIN_NO_REWARD_IMAGE`.
- **Day-2 total display**: `SHOW_TOTAL_DAY`.
- **End-of-day strategy/awareness questions**: not yet designed.
- **Calibration quiz wording**: needs review (`texts/calibration.py`, `QUIZ`).

## Recently done
- 2026-11-01 – Added `CLAUDE.md` and this `STATUS.md`.
- 2026-10-24 – No monetary bonus, `--manual-demo`, calibration practice removed, refresh-rate cache
  (details in the `DEVELOPMENT.md` changelog).
