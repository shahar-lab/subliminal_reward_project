"""Tests for file naming and PsychoPy-based saving. No window needed.
Run from the project root:  python -m pytest tests
"""
import csv
import glob
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
from common import io  # noqa: E402
from common.keyboard import AbortExperiment, number_keys_for, number_key_value  # noqa: E402
from common.scene import CasinoScene  # noqa: E402

PARTICIPANT = {'subject': 7, 'day': 2, 'experimenter': 'AK', 'date': '2026-10-22_14h00.00.000'}


def read_csv(path):
    with open(path, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def test_subject_label_padding():
    assert io.subject_label(7) == 'sub-' + '7'.zfill(config.SUBJECT_ID_DIGITS)


def test_file_base_layout(tmp_path):
    base = io.file_base(7, 2, 'bandit', date_str='D', data_dir=tmp_path)
    assert base == os.path.join(tmp_path, io.subject_label(7), f'{io.subject_label(7)}_day2_bandit_D')


def test_completed_task_saves_rows(tmp_path):
    with io.TaskData(PARTICIPANT, 'demo', {'refresh_measured_hz': 60}, data_dir=tmp_path) as td:
        td.add_row({'trial': 1, 'choice': 2})
        td.add_row({'trial': 2, 'choice': 0})
    rows = read_csv(td.base + '.csv')
    assert [r['trial'] for r in rows] == ['1', '2', '']
    assert rows[-1]['event'] == 'task_completed'
    assert rows[0]['subject'] == '7' and rows[0]['refresh_measured_hz'] == '60'
    if config.SAVE_PICKLE:
        assert os.path.exists(td.base + '.psydat')


@pytest.mark.parametrize('exc, status', [(AbortExperiment, 'task_aborted'),
                                         (ZeroDivisionError, 'task_crashed:ZeroDivisionError')])
def test_data_saved_on_abort_and_crash(tmp_path, exc, status):
    with pytest.raises(exc):
        with io.TaskData(PARTICIPANT, 'demo', data_dir=tmp_path) as td:
            td.add_row({'trial': 1})
            raise exc()
    rows = read_csv(td.base + '.csv')
    assert rows[0]['trial'] == '1' and rows[-1]['event'] == status


def test_never_overwrites(tmp_path):
    for _ in range(2):
        with io.TaskData(PARTICIPANT, 'demo', data_dir=tmp_path) as td:
            td.add_row({'trial': 1})
    files = glob.glob(os.path.join(tmp_path, '*', '*demo*.csv'))
    assert len(files) == 2


def test_number_keys():
    assert number_keys_for(3) == ['1', 'num_1', '2', 'num_2', '3', 'num_3']
    assert number_key_value('num_4') == 4 and number_key_value('x') is None


def test_random_offer():
    for _ in range(200):
        arms, colours = CasinoScene.draw_random_offer()
        assert len(set(arms)) == config.N_ACTIVE_ARMS and len(set(colours)) == config.N_ACTIVE_ARMS
        assert all(0 <= a < len(config.ARM_X_POSITIONS) for a in arms)
        assert all(c in config.CIRCLE_ACTIVE_COLORS for c in colours)


def test_calibration_summary(tmp_path):
    for status in ('completed', 'cap_reached_block1'):
        path = io.append_calibration_summary({'subject': 7, 'status': status}, data_dir=tmp_path)
    rows = read_csv(path)
    assert [r['status'] for r in rows] == ['completed', 'cap_reached_block1']
