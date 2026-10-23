"""Day 2: STEP calibration -> subliminal bandit -> questionnaires.

Run:  python run_day_2.py   (a dialog asks for the subject ID)
Add --bot for a simulated participant (see README).
"""
from common.day import run_day
from tasks.bandit import run as bandit
from tasks.calibration import run as calibration
from tasks.questionnaires import run as questionnaires

DAY = 2
TASKS = [
    calibration.run,          # STEP calibration of the coin opacity
    bandit.run_day2,          # subliminal casino game (calibrated opacity)
    questionnaires.run_day2,  # open questions + IMI motivation (about the casino game)
]

if __name__ == '__main__':
    run_day(DAY, TASKS)
