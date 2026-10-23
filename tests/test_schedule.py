"""Bandit schedule and key mapping. Run: python -m pytest tests"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402
from tasks.bandit.schedule import make_schedule, is_rewarded  # noqa: E402
from tasks.bandit.run import key_to_arm  # noqa: E402


def test_same_seed_same_schedule():
    assert make_schedule(200, 123, 1) == make_schedule(200, 123, 1)
    assert make_schedule(200, 123, 1) != make_schedule(200, 124, 1)


def test_offers_and_colours_valid():
    for trial in make_schedule(500, 7, 1):
        arms, colours = trial['offered_arms'], trial['colours']
        assert len(set(arms)) == config.N_ACTIVE_ARMS and arms == sorted(arms)
        assert len(set(colours)) == config.N_ACTIVE_ARMS
        assert set(colours) <= set(config.CIRCLE_ACTIVE_COLORS)
        assert 0 <= trial['outcome_draw'] < 1


def test_live_walk_rule():
    sched = make_schedule(300, 5, 1, walk_mode='live')
    assert sched[0]['probs'] == [config.WALK_INITIAL_PROB] * len(config.ARM_X_POSITIONS)
    for prev, cur in zip(sched, sched[1:]):
        for p0, p1 in zip(prev['probs'], cur['probs']):
            assert config.WALK_MIN_PROB <= p1 <= config.WALK_MAX_PROB
            assert abs(p1 - p0) < 6 * config.WALK_STEP_SD


def test_walk_from_file(tmp_path, monkeypatch):
    path = tmp_path / 'walk.csv'
    path.write_text('p0,p1,p2,p3\n' + '\n'.join('0.2,0.4,0.6,0.8' for _ in range(10)))
    monkeypatch.setitem(config.BANDIT_WALK_FILES, 1, str(path))
    sched = make_schedule(10, 1, 1, walk_mode='file')
    assert all(t['probs'] == [0.2, 0.4, 0.6, 0.8] for t in sched)
    with pytest.raises(ValueError):
        make_schedule(11, 1, 1, walk_mode='file')


def test_reward_uses_chosen_arm_probability():
    trial = {'probs': [0.1, 0.9, 0.5, 0.5], 'outcome_draw': 0.5}
    assert not is_rewarded(trial, 0) and is_rewarded(trial, 1)


def test_reward_rate_matches_probability():
    sched = make_schedule(20000, 3, 1)
    rate = sum(is_rewarded(t, 0) for t in sched) / len(sched)
    mean_p = sum(t['probs'][0] for t in sched) / len(sched)
    assert rate == pytest.approx(mean_p, abs=0.02)


def test_hebrew_layout_keys():
    assert [key_to_arm(k) for k in config.ARM_KEYS] == [0, 1, 2, 3]
    assert [key_to_arm(k) for k in ['ד', 'כ', 'י', 'ל']] == [0, 1, 2, 3]
