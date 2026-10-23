"""Day 1: working memory -> conscious bandit -> questionnaires (about the bandit).

Run:  python run_day_1.py   (a dialog asks for the subject ID)
Add --bot for a simulated participant (see README).
"""
from common.day import run_day
from tasks.bandit import run as bandit
from tasks.wm import run as wm
from tasks.questionnaires import run as questionnaires

DAY = 1
TASKS = [
    wm.run,                   # working memory (change detection)
    bandit.run_day1,          # conscious casino game
    questionnaires.run_day1,  # open questions + IMI motivation (about the casino game)
]

if __name__ == '__main__':
    run_day(DAY, TASKS)
