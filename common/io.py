"""Participant info, file names, and data saving through PsychoPy's ExperimentHandler.

Data layout:
    data/sub-007/sub-007_day1_bandit_2026-10-22_14h30.05.123.csv   (+ .psydat)
    data/sub-007/sub-007_day1_2026-10-22_14h29.50.001.log           (PsychoPy log, whole day)
    data/sub-007/sub-007_day1_2026-10-22_14h29.50.001_config.py     (copy of config.py)

One ExperimentHandler per task per day. The date-time stamp in every name
means a file is never overwritten.
"""
import os
import shutil
import sys

from psychopy import gui, data, logging, core
import psychopy

import config


# ─── names and folders ─────────────────────────────────────────────────────────
def subject_label(subject_id):
    return f'sub-{int(subject_id):0{config.SUBJECT_ID_DIGITS}d}'


def participant_dir(subject_id, data_dir=None):
    path = os.path.join(data_dir or config.DATA_DIR, subject_label(subject_id))
    os.makedirs(path, exist_ok=True)
    return path


def file_base(subject_id, day, task=None, date_str=None, data_dir=None):
    """Full path without extension, e.g. .../sub-007/sub-007_day2_bandit_<date>."""
    date_str = date_str or data.getDateStr()
    parts = [subject_label(subject_id), f'day{day}'] + ([task] if task else []) + [date_str]
    return os.path.join(participant_dir(subject_id, data_dir), '_'.join(parts))


def existing_files(subject_id, day, data_dir=None):
    folder = participant_dir(subject_id, data_dir)
    prefix = f'{subject_label(subject_id)}_day{day}_'
    return sorted(f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith('.csv'))


# ─── participant dialog (one per day) ──────────────────────────────────────────
def get_participant_info(day):
    """Dialog for the day. Day 1 also asks demographics. Returns a dict or quits on Cancel."""
    fields = {'subject': '', 'experimenter': ''}
    order = ['subject', 'experimenter']
    if day == 1:
        fields.update({'age': '', 'gender': ['F', 'M', 'Other'], 'hand': ['R', 'L']})
        order += ['age', 'gender', 'hand']

    while True:
        dlg = gui.DlgFromDict(fields, title=f'{config.EXPERIMENT_NAME} - Day {day}', order=order)
        if not dlg.OK:
            core.quit()
        error = _validate(fields, day)
        if not error:
            break
        err = gui.Dlg(title='Input error')
        err.addText(error)
        err.show()

    info = dict(fields)
    info['subject'] = int(info['subject'])
    info['day'] = day
    info['date'] = data.getDateStr()

    previous = existing_files(info['subject'], day)
    if previous:
        warn = gui.Dlg(title='Data already exist')
        warn.addText(f'{subject_label(info["subject"])} already has Day {day} files:')
        for f in previous[-5:]:
            warn.addText(f)
        warn.addText('Continue anyway? New files will be added; nothing is overwritten.')
        warn.show()
        if not warn.OK:
            core.quit()
    return info


def _validate(fields, day):
    if not str(fields['subject']).strip().isdigit():
        return 'Subject ID must be a whole number.'
    if day == 1 and not str(fields['age']).strip().isdigit():
        return 'Age must be a whole number.'
    return ''


# ─── run-time info saved with the data ─────────────────────────────────────────
def git_commit():
    """Current commit hash of the code (read from .git, no git executable needed)."""
    git_dir = os.path.join(config.ROOT_DIR, '.git')
    try:
        with open(os.path.join(git_dir, 'HEAD')) as f:
            head = f.read().strip()
        if head.startswith('ref:'):
            ref = head.split(' ', 1)[1]
            ref_path = os.path.join(git_dir, *ref.split('/'))
            if os.path.exists(ref_path):
                with open(ref_path) as f:
                    return f.read().strip()[:10]
            with open(os.path.join(git_dir, 'packed-refs')) as f:
                for line in f:
                    if line.strip().endswith(ref):
                        return line.split()[0][:10]
        return head[:10]
    except OSError:
        return 'unknown'


def runtime_info(window_info=None):
    info = {'psychopy_version': psychopy.__version__,
            'python_version': sys.version.split()[0],
            'code_commit': git_commit()}
    info.update(window_info or {})
    return info


def start_day_files(participant):
    """PsychoPy log file for the whole day + a copy of config.py. Returns the base path."""
    base = file_base(participant['subject'], participant['day'], date_str=participant['date'])
    if config.SAVE_LOG_FILE:
        logging.LogFile(base + '.log', level=logging.EXP, filemode='w')
    shutil.copy(os.path.join(config.ROOT_DIR, 'config.py'), base + '_config.py')
    return base


# ─── per-task data ─────────────────────────────────────────────────────────────
class TaskData:
    """Thin wrapper around PsychoPy's ExperimentHandler for one task on one day.

    Use as a context manager: the file is saved when the task ends, when the
    abort key is pressed, or when the code crashes.

        with TaskData(participant, 'bandit', extra) as td:
            td.add_row({'trial': 1, 'choice': 2, ...})
    """

    def __init__(self, participant, task, extra_info=None, data_dir=None):
        self.task = task
        self.base = file_base(participant['subject'], participant['day'], task, data_dir=data_dir)
        info = {**participant, 'task': task, **(extra_info or {})}
        self.exp = data.ExperimentHandler(name=f'{config.EXPERIMENT_NAME}_{task}',
                                          extraInfo=info,
                                          dataFileName=self.base,
                                          savePickle=config.SAVE_PICKLE,
                                          saveWideText=True,
                                          autoLog=False)
        self.n_rows = 0

    def add_row(self, row):
        """Add one finished row (e.g. one trial) and move to the next entry."""
        for key, value in row.items():
            self.exp.addData(key, '' if value is None else value)   # empty cell, not the text 'None'
        self.exp.nextEntry()
        self.n_rows += 1

    def close(self, status='completed'):
        self.add_row({'event': f'task_{status}'})
        self.exp.close()   # PsychoPy saves .csv (+ .psydat) here
        logging.flush()

    def __enter__(self):
        logging.exp(f'START task {self.task} -> {self.base}')
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            status = 'completed'
        elif exc_type.__name__ == 'AbortExperiment':
            status = 'aborted'
        else:
            status = f'crashed:{exc_type.__name__}'
        self.close(status)
        logging.exp(f'END task {self.task} ({status})')
        return False   # never swallow the exception; the day runner decides what to do


# ─── calibration results on disk ───────────────────────────────────────────────
CALIBRATION_TASK = 'calibration'
FINAL_THRESHOLD_EVENT = 'final_threshold'


def append_calibration_summary(row, data_dir=None):
    """Append one row to the lab-wide calibration summary (in addition to the task's own CSV)."""
    import csv
    path = os.path.join(data_dir or config.DATA_DIR, config.CALIB_SUMMARY_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new_file = not os.path.exists(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if new_file:
            writer.writeheader()
        writer.writerow(row)
    return path
