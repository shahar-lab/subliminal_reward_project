"""Four-armed bandit ("casino game") - Day 1 (conscious) and Day 2 (subliminal).

Flow: instructions -> quiz (repeat until all correct) -> practice -> blocks with breaks -> total.
Trial: empty arms (ITI) -> two coloured + two grey circles -> choice (s/f/h/k, max CHOICE_TIME_LIMIT)
-> empty arms -> feedback sequence (mask-coin-mask) -> [optional awareness probe: PAS + 2AFC].
A miss (no choice in time) or a grey-arm choice ("unavailable", UNAVAILABLE_CHOICE_DURATION penalty
screen) is logged as a trial with no outcome; both count towards the trial total.

Coin opacity: Day 1 = DAY1_COIN_OPACITY; Day 2 = this session's calibrated threshold (else the day stops).
"""
import random

from psychopy import core

import config
from common.awareness import AwarenessQuestions
from common.day import StopDay
from common.display import show
from common.io import TaskData
from common.scene import CasinoScene, REWARD, NO_REWARD
from tasks.bandit.schedule import make_seed, make_schedule, is_rewarded
from texts import bandit as T

TASK = 'bandit'


def run_day1(ctx):
    return run(ctx, day=1)


def run_day2(ctx):
    return run(ctx, day=2)


def coin_opacity(ctx, day):
    """Day 1: DAY1_COIN_OPACITY. Day 2: ONLY the final threshold of the calibration completed
    earlier in this same session (same participant ID). Never read from other files."""
    if day == 1:
        return config.DAY1_COIN_OPACITY, 'config'
    threshold = getattr(ctx, 'calibration_threshold', None)
    if threshold is None:
        raise StopDay(f'No calibration value for subject {ctx.participant["subject"]} in this session - '
                      f'the casino game cannot start. Run Day 2 again from the start (python run_day_2.py).')
    return threshold, 'this_session_calibration'


def run(ctx, day):
    opacity, opacity_source = coin_opacity(ctx, day)
    seed = make_seed()
    n_main = config.BANDIT_N_BLOCKS * config.BANDIT_TRIALS_PER_BLOCK
    practice = make_schedule(config.BANDIT_N_PRACTICE, seed + 1, day, walk_mode='live')
    schedule = make_schedule(n_main, seed, day)
    probe_rate = config.AWARENESS_PROBE_RATE.get(day, 0.0)
    probe_rng = random.Random(seed + 2)

    scene = CasinoScene(ctx.win)
    awareness = AwarenessQuestions(ctx.win, ctx.keys, ctx.screens, ctx.participant['subject'])
    extra = {**ctx.runtime, 'seed': seed, 'coin_opacity_used': opacity, 'opacity_source': opacity_source,
             'reward_walk': config.REWARD_WALK, 'probe_rate': probe_rate, 'gold_side': awareness.gold_side}
    print(f'Bandit day {day}: coin opacity {opacity:.4f} ({opacity_source}), seed {seed}')

    with TaskData(ctx.participant, TASK, extra) as td:
        ctx.screens.instructions_with_quiz(build_pages(scene, day, probe_rate), build_quiz(), log=td.add_row)

        if practice:
            ctx.screens.message(T.PRACTICE_START.format(n=len(practice)))
            previous = None
            for i, trial in enumerate(practice, start=1):
                row = run_trial(ctx, scene, awareness, trial, opacity, probe=False)
                td.add_row({'phase': 'practice', 'trial': i, 'reward_oneback': previous, **row})
                previous = row['reward']
            ctx.screens.message(T.PRACTICE_END)

        coins, previous = 0, None
        for t, trial in enumerate(schedule, start=1):
            block = (t - 1) // config.BANDIT_TRIALS_PER_BLOCK + 1
            probe = probe_rate > 0 and probe_rng.random() < probe_rate
            row = run_trial(ctx, scene, awareness, trial, opacity, probe)
            coins += row['reward'] or 0
            td.add_row({'phase': 'main', 'block': block, 'trial': t,
                        'trial_in_block': (t - 1) % config.BANDIT_TRIALS_PER_BLOCK + 1,
                        'coins_total': coins, 'reward_oneback': previous, **row})
            previous = row['reward']
            if t % config.BANDIT_TRIALS_PER_BLOCK == 0 and block < config.BANDIT_N_BLOCKS:
                ctx.screens.break_screen(T.BREAK.format(done=block, total=config.BANDIT_N_BLOCKS))

        shekel = round(coins * config.COIN_VALUE_SHEKEL, 2)
        td.add_row({'phase': 'main', 'event': 'bandit_total', 'coins_total': coins, 'payment_shekel': shekel})
    print(f'Bandit day {day}: {coins} gold coins = {shekel:.2f} NIS')
    if config.SHOW_TOTAL_DAY.get(day, True):
        ctx.screens.message(T.END_WITH_TOTAL.format(coins=coins, shekel=shekel))
    else:
        ctx.screens.message(T.END_NO_TOTAL)
    return coins


def key_to_arm(key):
    key = config.ARM_KEY_ALIASES.get(key, key)
    return config.ARM_KEYS.index(key)


def wait_for_choice(ctx):
    """Wait for any arm key. Returns (arm, key, rt) or (None, None, None) after CHOICE_TIME_LIMIT."""
    key, rt = ctx.keys.wait(config.ARM_KEYS + list(config.ARM_KEY_ALIASES), max_wait=config.CHOICE_TIME_LIMIT)
    if key is None:
        return None, None, None
    return key_to_arm(key), key, rt


def run_trial(ctx, scene, awareness, trial, opacity, probe):
    offered, colours = trial['offered_arms'], trial['colours']
    colour_of = dict(zip(offered, colours))
    scene.set_offer(offered, colours)
    ctx.keys.check_abort()

    t_iti = show(ctx.win, scene.draw_background, config.WAIT_INITIAL)
    ctx.keys.clear()
    ctx.keys.reset_clock_on_flip(ctx.win)
    t_offer = show(ctx.win, scene.draw_offer)
    arm, key, rt = wait_for_choice(ctx)

    row = {'offered_arms': ';'.join(map(str, offered)),
           **{f'colour_arm{a}': colour_of.get(a, '') for a in range(scene.n_arms)},
           **{f'p_arm{a}': p for a, p in enumerate(trial['probs'])},
           'outcome_draw': trial['outcome_draw'], 'coin_opacity': opacity,
           't_iti': t_iti, 't_offer': t_offer,
           'choice_key': key, 'choice_arm': arm, 'rt': rt,
           'missed': 0, 'unavailable_choice': 0, 'reward': None, 'probe': 0,
           'pas': None, 'pas_rt': None, 'twoafc_choice': None, 'twoafc_rt': None, 'twoafc_correct': None}

    if arm is None:                                   # miss: counts as a trial, no outcome
        show(ctx.win, lambda: scene.draw_message(T.TOO_LATE), config.INVALID_MSG_DURATION)
        return {**row, 'missed': 1, 'choice_colour': None}
    if arm not in offered:                            # grey (unavailable) arm: penalty, no outcome
        t_penalty = show(ctx.win, lambda: scene.draw_message(T.UNAVAILABLE), config.UNAVAILABLE_CHOICE_DURATION)
        return {**row, 'unavailable_choice': 1, 'choice_colour': None, 't_unavailable_msg': t_penalty}

    rewarded = is_rewarded(trial, arm)
    outcome = REWARD if rewarded else NO_REWARD
    t_post = show(ctx.win, scene.draw_background, config.WAIT_POST_CHOICE)
    timing = scene.feedback_sequence(outcome, opacity)
    timing.pop('coin_opacity')
    row.update({'choice_colour': colour_of[arm], 'reward': int(rewarded), 't_post_choice': t_post, **timing})

    row['probe'] = int(probe)
    if probe:                                         # awareness questions (empty columns otherwise)
        pas, pas_rt = awareness.pas()
        chosen, choice_rt = awareness.coin_choice()
        row.update({'pas': pas, 'pas_rt': pas_rt, 'twoafc_choice': chosen,
                    'twoafc_rt': choice_rt, 'twoafc_correct': int(chosen == outcome)})
    return row


# ── instructions ─────────────────────────────────────────────────────────────
def _fmt(text):
    n_trials = config.BANDIT_N_BLOCKS * config.BANDIT_TRIALS_PER_BLOCK
    return text.format(n_trials=n_trials, n_breaks=config.BANDIT_N_BLOCKS - 1,
                       time_limit=f'{config.CHOICE_TIME_LIMIT:g}',
                       penalty=f'{config.UNAVAILABLE_CHOICE_DURATION:g}')


def build_quiz():
    return [{**q, 'prompt': _fmt(q['prompt']), 'options': [_fmt(o) for o in q['options']]} for q in T.QUIZ]


def build_pages(scene, day, probe_rate):
    specs = T.PAGES_DAY1 if day == 1 else T.PAGES_DAY2
    title = T.TITLE if day == 1 else T.TITLE_DAY2
    pages = []
    for spec in specs:
        text = _fmt(spec['text'])
        if spec.get('mask') and probe_rate > 0:
            text += T.PROBE_SENTENCE
        page = {'title': title, 'text': text}
        size = config.CHOICE_COIN_SIZE
        if spec.get('reward_coin'):
            page['images'] = [(config.COIN_REWARD_IMAGE, (0, -2.0), size)]
        if spec.get('no_reward_coin'):
            page['images'] = [(config.COIN_NO_REWARD_IMAGE, (0, -2.0), size)]
        if spec.get('mask'):
            page['images'] = [(config.MASK_IMAGES[0], (0, -3.0), size)]
        if 'offer' in spec:
            page['draw'] = _offer_example(scene, spec['offer'])
        pages.append(page)
    return pages


def _offer_example(scene, arms):
    """Live casino screen (shifted down) with the given arms available, for instruction pages."""
    def draw():
        colours = config.CIRCLE_ACTIVE_COLORS[:len(arms)]
        scene.set_offer(arms, colours)
        shift = config.INSTR_SCENE_SHIFT_Y
        stims = scene.arms + scene.circles + [scene.feedback_box]
        for s in stims:
            s.pos = (s.pos[0], s.pos[1] + shift)
        for s in stims:
            s.draw()
        for s in stims:
            s.pos = (s.pos[0], s.pos[1] - shift)
    return draw
