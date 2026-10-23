"""Working-memory task logic vs the ground-truth jsPsych task. Run: python -m pytest tests"""
import os
import random
import sys
from collections import Counter

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402
from common.awareness import gold_side  # noqa: E402
from tasks.wm.run import (location_positions, make_trial, condition_sequence, practice_sequence,  # noqa: E402
                          capacity, same_key_for, pick_locations)


def css_centre(name, W=1536, H=960, step=105, sq=51.4):
    """Square centre (px, origin centre, y up) computed exactly as the original CSS places it."""
    k = {'a': 1, 'b': 2, 'c': 3, 'd': 1, 'e': 2, 'f': 3, 'g': 1, 'h': 2, 'i': 3, 'j': 1, 'k': 2, 'l': 3}
    if name in k:
        n = k[name]
        if name in 'abc':   # top/left
            left, top = W / 2 - n * step, H / 2 - n * step
        elif name in 'def':  # top/right
            left, top = W - (W / 2 - n * step) - sq, H / 2 - n * step
        elif name in 'ghi':  # bottom/right
            left, top = W - (W / 2 - n * step) - sq, H - (H / 2 - n * step) - sq
        else:                # bottom/left
            left, top = W / 2 - n * step, H - (H / 2 - n * step) - sq
    else:
        n = {'upper1': 3, 'upper2': 2, 'upper3': 1, 'lower1': 3, 'lower2': 2, 'lower3': 1}[name]
        left = W / 2 - sq / 2
        top = H / 2 - n * step if name.startswith('upper') else H - (H / 2 - n * step) - sq
    cx, cy = left + sq / 2, top + sq / 2
    return cx - W / 2, H / 2 - cy


def test_positions_match_original_css():
    pos = location_positions()
    assert len(pos) == 18
    for name, (x, y) in pos.items():
        assert (x, y) == pytest.approx(css_centre(name)), name


def test_locations_one_or_two_per_quadrant():
    rng = random.Random(0)
    for size, per_quadrant in ((4, 1), (8, 2)):
        for _ in range(200):
            locs = pick_locations(rng, size)
            assert len(set(locs)) == size
            for letters in ('abc', 'def', 'ghi', 'jkl'):
                assert sum(l in letters for l in locs) == per_quadrant
    assert pick_locations(rng, 1)[0].startswith(('upper', 'lower'))


def test_trial_colours():
    rng = random.Random(1)
    for _ in range(500):
        size = rng.choice([1, 4, 8])
        for cond in ('same', 'diff'):
            t = make_trial(rng, size, cond)
            assert len(set(t['array_colours'])) == size
            assert t['original_colour'] == t['array_colours'][t['test_index']]
            if cond == 'same':
                assert t['test_colour'] == t['original_colour']
            else:
                assert t['test_colour'] not in t['array_colours']   # a colour that was not shown


def test_condition_sequences():
    rng = random.Random(2)
    balanced = Counter(condition_sequence(rng, 120, [4, 8], balanced=True))
    assert set(balanced.values()) == {30}
    random_seq = condition_sequence(rng, 120, [4, 8], balanced=False)
    assert len(random_seq) == 120 and set(random_seq) <= {(4, 'same'), (4, 'diff'), (8, 'same'), (8, 'diff')}
    for _ in range(50):
        prac = practice_sequence(rng, 5)
        assert len(prac) == 5 and prac[0][0] == 1


def test_capacity_formula():
    rows = [{'set_size': 4, 'accuracy': a} for a in [1, 1, 1, 0]] + [{'set_size': 4, 'accuracy': None}]
    acc, k = capacity(rows, 4)
    assert acc == pytest.approx(3 / 5) and k == pytest.approx(4 * (2 * 0.6 - 1))


def test_key_counterbalancing_independent_of_gold_side():
    combos = Counter((same_key_for(i), gold_side(i)) for i in range(1, 401))
    assert len(combos) == 4 and set(combos.values()) == {100}
