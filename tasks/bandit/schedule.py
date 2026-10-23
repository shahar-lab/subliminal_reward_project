"""Trial schedule for the bandit - pure logic, no PsychoPy.

Everything random in a session comes from one seed (saved in the data file), so a
session can be regenerated exactly: which arms are offered, their colours, the reward
probabilities of all arms on every trial, and the random number that decides the outcome.
"""
import csv
import os
import random

import config


def make_seed():
    return config.BANDIT_SEED if config.BANDIT_SEED is not None else random.SystemRandom().randrange(2 ** 31)


def live_walk(rng, n_trials, n_arms):
    """Original rule: every arm starts at WALK_INITIAL_PROB and takes a Gaussian step after each trial."""
    probs = [config.WALK_INITIAL_PROB] * n_arms
    walk = []
    for _ in range(n_trials):
        walk.append(list(probs))
        probs = [min(config.WALK_MAX_PROB, max(config.WALK_MIN_PROB, p + rng.gauss(0, config.WALK_STEP_SD)))
                 for p in probs]
    return walk


def walk_from_file(path, n_trials, n_arms):
    """Pre-generated walk: CSV with columns p0..p{n_arms-1}, one row per trial."""
    full = path if os.path.isabs(path) else os.path.join(config.ROOT_DIR, path)
    with open(full, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    if len(rows) < n_trials:
        raise ValueError(f'{full} has {len(rows)} rows, {n_trials} needed')
    return [[float(r[f'p{a}']) for a in range(n_arms)] for r in rows[:n_trials]]


def make_schedule(n_trials, seed, day, walk_mode=None):
    """List of per-trial dicts: offered_arms, colours (per offered arm), probs (all arms), outcome_draw."""
    n_arms = len(config.ARM_X_POSITIONS)
    rng = random.Random(seed)
    walk_mode = walk_mode or config.REWARD_WALK
    if walk_mode == 'live':
        walk = live_walk(random.Random(rng.randrange(2 ** 31)), n_trials, n_arms)
    elif walk_mode == 'file':
        walk = walk_from_file(config.BANDIT_WALK_FILES[day], n_trials, n_arms)
    else:
        raise ValueError(f'Unknown REWARD_WALK {walk_mode!r}')
    schedule = []
    for t in range(n_trials):
        arms = sorted(rng.sample(range(n_arms), config.N_ACTIVE_ARMS))
        colours = rng.sample(config.CIRCLE_ACTIVE_COLORS, config.N_ACTIVE_ARMS)
        schedule.append({'offered_arms': arms, 'colours': colours, 'probs': walk[t],
                         'outcome_draw': rng.random()})
    return schedule


def is_rewarded(trial, chosen_arm):
    return trial['outcome_draw'] < trial['probs'][chosen_arm]
