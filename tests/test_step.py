"""STEP staircase tests.

1. Lockstep equivalence with Eden Elbaz's original functions (copied verbatim below
   from her ISI_calcu.py): same intensity, boundary and CWIR on every trial, and the
   same threshold whenever her known double-counting does not occur.
2. The two deliberate differences (see tasks/calibration/step.py) behave as documented.
3. A simulated observer lands at chance (the paper's goal), and the trial cap works.
"""
import os
import random
import sys

import numpy as np
import pandas as pd
import pytest
from scipy.stats import binomtest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tasks.calibration.step import StepStaircase, StepParams  # noqa: E402


# ─── Eden Elbaz's functions, verbatim from ISI_calcu.py ─────────────────────────
def calculate_next_ISI(df, ISI, trial, max_indicators, w_list, incorrect_ISI_list, num_incorrect_seq_to, num_incorrect_seq, num_of_indicators, correct):  # noqa: E501
    if correct == 1:
        adj_dir = -1
    else:
        adj_dir = 1
    if adj_dir == -1:
        if len(w_list) != 0:
            w_last = np.mean(w_list)
            incorrect_ISI_list.extend([w_last] * num_incorrect_seq_to)
            num_incorrect_seq_to = 0
            num_incorrect_seq = 0
            w_list = []
    else:
        num_incorrect_seq = num_incorrect_seq + 1
        w_list.append(ISI)
        num_incorrect_seq_to = num_incorrect_seq_to + num_incorrect_seq
        num_of_indicators = num_of_indicators + num_incorrect_seq
        if num_of_indicators >= max_indicators:
            w_last = np.mean(w_list)
            incorrect_ISI_list.extend([w_last] * num_incorrect_seq_to)
    return df, w_list, incorrect_ISI_list, num_incorrect_seq_to, num_incorrect_seq, num_of_indicators, adj_dir


def step_isi(ISI, initial_step, trial, min_step, df, correct, correct_seen, max_ISI, min_ISI, adj_dir, prev_adj_dir):
    step = initial_step - (min_step * (trial - 1))
    step = max(min_step, step)
    df.loc[trial - 1, 'step_size'] = step
    seen_adj = 1
    if (correct == 0) & (correct_seen == 1) & (step != min_step):
        seen_adj = 0
    df.loc[trial - 1, 'final_step'] = adj_dir * step * seen_adj
    ISI = ISI + (adj_dir * step * seen_adj)
    ISI = min(max_ISI, ISI)
    ISI = max(min_ISI, ISI)
    return ISI, df


def boundary(df, ISI, max_ISI, trial, last_update, num_of_indicators):
    relevent_ISI_df = df.copy()
    relevent_ISI_df = relevent_ISI_df[(relevent_ISI_df['Contrast'] >= ISI) & (relevent_ISI_df['Contrast'] <= max_ISI)]
    if len(relevent_ISI_df) == 0:
        return df, last_update, max_ISI
    cumulative_trials = relevent_ISI_df.shape[0]
    cumulative_correct = relevent_ISI_df['Correct'].sum()
    cumulative_seen = relevent_ISI_df['Seen'].sum()
    seen_ratio = cumulative_seen / cumulative_trials
    binom_result = binomtest(int(cumulative_correct), int(cumulative_trials), p=0.5, alternative='greater')
    if binom_result.pvalue <= (0.05 / (1 + num_of_indicators)):
        if (trial - last_update) >= 0:
            max_ISI = ((1 - seen_ratio) * max_ISI) + (seen_ratio * ISI)
            last_update = trial
    return df, last_update, max_ISI


class EdenRun:
    """Her per-trial loop from word_cali.py (one repetition), driven one trial at a time."""

    def __init__(self):
        self.contrast, self.max_contrast, self.min_contrast = 1, 1, 0.1
        self.trial, self.last_update, self.num_of_indicators, self.num_incorrect_seq = 1, 0, 0, 0
        self.w_list, self.incorrect_ISI_list, self.num_incorrect_seq_to = [], [], 0
        self.prev_adj_dir = np.nan
        self.df = pd.DataFrame(columns=['Contrast', 'Correct', 'Seen'])
        self.first_stop_trial = None

    @property
    def running(self):
        return (self.num_of_indicators < 50) | (self.trial <= 50)

    def step(self, correct, seen):
        t = self.trial
        self.df.loc[t - 1, ['Contrast', 'Correct', 'Seen']] = [self.contrast, correct, seen]
        self.df = self.df.astype(float)
        self.df, self.last_update, self.max_contrast = boundary(
            self.df, self.contrast, self.max_contrast, t, self.last_update, self.num_of_indicators)
        (self.df, self.w_list, self.incorrect_ISI_list, self.num_incorrect_seq_to, self.num_incorrect_seq,
         self.num_of_indicators, adj_dir) = calculate_next_ISI(
            self.df, self.contrast, t, 50, self.w_list, self.incorrect_ISI_list,
            self.num_incorrect_seq_to, self.num_incorrect_seq, self.num_of_indicators, correct)
        if self.num_of_indicators >= 50 and self.first_stop_trial is None:
            self.first_stop_trial = t
        self.contrast, self.df = step_isi(self.contrast, 0.2, t, 0.05, self.df, correct, seen,
                                          self.max_contrast, self.min_contrast, adj_dir, self.prev_adj_dir)
        self.trial += 1
        self.prev_adj_dir = adj_dir

    def threshold(self):
        return float(np.mean(self.incorrect_ISI_list))


# ─── simulated observer (paper Eq. 1 for accuracy, Eq. 2 for "seen") ───────────
def observer(theta, rate=0.15, seen_mid_offset=0.08, seen_spread=0.04, lapse=0.02):
    def p_correct(x):
        return 0.5 if x <= theta else 0.5 + (0.5 - lapse) * (1 - np.exp(-((x - theta) / rate)))

    def p_seen(x):
        return 1 / (1 + np.exp((theta + seen_mid_offset - x) / seen_spread))
    return p_correct, p_seen


def respond(rng, x, p_correct, p_seen):
    return int(rng.random() < p_correct(x)), int(rng.random() < p_seen(x))


# ─── 1. equivalence ─────────────────────────────────────────────────────────────
def test_lockstep_equivalence_with_original():
    rng = random.Random(1)
    n_threshold_compared = n_double_count_cases = 0
    for run in range(60):
        pc, ps = observer(rng.uniform(0.15, 0.6))
        mine, eden = StepStaircase(StepParams(max_trials=10_000)), EdenRun()
        while eden.running:
            assert mine.intensity == pytest.approx(eden.contrast, abs=1e-9)
            correct, seen = respond(rng, mine.intensity, pc, ps)
            if mine.trial + 1 == 4 and not correct:
                seen = 0     # trial 4, incorrect & seen: the documented float difference - tested separately
            mine.update(correct, seen)
            eden.step(correct, seen)
            assert mine.boundary == pytest.approx(eden.max_contrast, abs=1e-9)
            assert mine.cwir == eden.num_of_indicators
        assert mine.done and not mine.cap_reached and mine.trial == eden.trial - 1
        if eden.first_stop_trial >= 50:      # her double count cannot happen
            assert mine.threshold() == pytest.approx(eden.threshold(), abs=1e-9)
            n_threshold_compared += 1
        else:
            n_double_count_cases += 1
    assert n_threshold_compared >= 10        # make sure the comparison actually ran


# ─── 2. the two deliberate differences ──────────────────────────────────────────
def test_sequence_counted_once_when_cwir_reaches_stop_before_min_trials():
    # 10 incorrect in a row reach CWIR 55 by trial 10; then correct answers until trial 50.
    mine, eden = StepStaircase(), EdenRun()
    responses = [0] * 10 + [1] * 45
    for r in responses:
        if not eden.running:
            break
        mine.update(r, 0)
        eden.step(r, 0)
    # one sequence of 10 incorrect trials, weight 55
    assert mine.sequences and len(mine.sequences) == 1 and mine.sequences[0][1] == 55
    # the original added the same sequence twice (at CWIR >= 50 and again when it ended)
    assert len(eden.incorrect_ISI_list) == 55 + 55
    # both average the same single sequence here, so values agree; the weight differs
    assert mine.threshold() == pytest.approx(eden.threshold())


def test_double_count_changes_threshold_when_sequences_differ():
    # sequence A (intensities high) counted twice by the original -> its threshold is pulled up
    mine, eden = StepStaircase(), EdenRun()
    responses = [1, 1] + [0] * 10 + [1] * 5 + [0, 0] + [1] * 40
    for r in responses:
        if not eden.running:
            break
        mine.update(r, 0)
        eden.step(r, 0)
    weights = [w for _, w in mine.sequences]
    assert weights == [55, 3]
    single = sum(m * w for m, w in mine.sequences) / sum(weights)
    assert mine.threshold() == pytest.approx(single)
    assert eden.threshold() != pytest.approx(single)


def test_seen_rule_stops_at_minimal_step():
    # trials 1-3: step 0.2/0.15/0.1 -> incorrect & seen keeps the intensity
    s = StepStaircase()
    for _ in range(3):
        before = s.intensity
        log = s.update(correct=0, seen=1)
        assert log['seen_rule_applied'] == 1 and s.intensity == before
    # trial 4: step is the minimal step (0.05) -> the rule no longer applies
    log = s.update(correct=0, seen=1)
    assert log['step'] == 0.05 and log['seen_rule_applied'] == 0


# ─── 3. behaviour ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize('theta', [0.2, 0.35, 0.5])
def test_simulated_observer_lands_at_chance(theta):
    rng = random.Random(int(theta * 100))
    pc, ps = observer(theta)
    estimates = []
    for _ in range(150):
        blocks = []
        for _ in range(2):                      # two calibration blocks, averaged
            s = StepStaircase()
            while not s.done:
                s.update(*respond(rng, s.intensity, pc, ps))
            blocks.append(s.threshold())
        estimates.append(np.mean(blocks))
    accuracy_at_estimate = np.mean([pc(e) for e in estimates])
    assert accuracy_at_estimate < 0.53
    assert np.mean(estimates) < theta + 0.03


def test_trial_cap():
    s = StepStaircase(StepParams(max_trials=300))
    while not s.done:
        s.update(correct=1, seen=1)             # never wrong -> CWIR stays 0
    assert s.trial == 300 and s.cap_reached and not s.converged
    assert s.threshold() is None
    assert s.intensity == pytest.approx(0.1)    # sits at the floor


def test_stops_only_after_min_trials():
    s = StepStaircase()
    while not s.done:
        s.update(correct=0, seen=0)             # always wrong: CWIR 55 after 10 trials
    assert s.trial == 50 and s.converged
