"""IMI scoring and item table. Run: python -m pytest tests"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tasks.questionnaires.run import score_imi  # noqa: E402
from texts.questionnaires import IMI_ITEMS  # noqa: E402


def test_items_match_ioc_wm():
    assert len(IMI_ITEMS) == 36
    attention = [it for it in IMI_ITEMS if it[4]]
    assert len(attention) == 6 and all(it[5] in (1, 7) for it in attention)
    assert all(it[5] is None for it in IMI_ITEMS if not it[4])


def test_scoring():
    rows = [{'attention': a, 'response': r, 'expected_answer': e, 'reverse_scored': rev, 'category': c}
            for a, r, e, rev, c in [(True, 1, 1, False, 'Attention'), (True, 3, 7, True, 'Attention'),
                                    (False, 6, None, False, 'Interest/Enjoyment'),
                                    (False, 2, None, True, 'Interest/Enjoyment')]]
    failed, means = score_imi(rows)
    assert failed == 1 and means == {'imi_interest_enjoyment': 6.0}
