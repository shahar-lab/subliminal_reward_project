"""STEP calibration task (Day 2) - shown in the casino scene, exactly like the bandit's feedback.

Flow: instructions -> quiz (repeat until all correct) -> practice -> block 1 -> break -> block 2.
Trial: empty arms (WAIT_POST_CHOICE) -> scene.feedback_sequence(coin, opacity) -> PAS -> coin choice.

Saved (PsychoPy ExperimentHandler, one CSV): quiz answers, every practice and staircase trial,
one 'block_threshold' row per block and one 'final_threshold' row. A row is also added to
data/calibration_summary.csv. If a block reaches CALIB_MAX_TRIALS without converging, the
calibration stops, the participant is asked to call the experimenter, and the day ends.
"""
import random

import config
from common.awareness import AwarenessQuestions
from common.day import StopDay
from common.display import show
from common.io import TaskData, append_calibration_summary, CALIBRATION_TASK, FINAL_THRESHOLD_EVENT
from common.scene import CasinoScene, REWARD, NO_REWARD
from tasks.calibration.step import StepStaircase, StepParams
from texts import calibration as T


def step_params():
    return StepParams(start_intensity=config.CALIB_START_OPACITY,
                      max_intensity=config.CALIB_MAX_OPACITY,
                      min_intensity=config.CALIB_MIN_OPACITY,
                      initial_step=config.CALIB_INITIAL_STEP,
                      step_decrease=config.CALIB_STEP_DECREASE,
                      min_step=config.CALIB_MIN_STEP,
                      cwir_stop=config.CALIB_CWIR_STOP,
                      min_trials=config.CALIB_MIN_TRIALS,
                      max_trials=config.CALIB_MAX_TRIALS)


def run(ctx):
    """Run the calibration; returns the final threshold (also stored on ctx.calibration_threshold)."""
    scene = CasinoScene(ctx.win)
    awareness = AwarenessQuestions(ctx.win, ctx.keys, ctx.screens, ctx.participant['subject'])
    extra = {**ctx.runtime, 'gold_side': awareness.gold_side}

    with TaskData(ctx.participant, CALIBRATION_TASK, extra) as td:
        ctx.screens.instructions_with_quiz(build_pages(scene, awareness.gold_side), T.QUIZ, log=td.add_row)

        ctx.screens.message(T.PRACTICE_START)
        practice = list(config.CALIB_PRACTICE_OPACITIES)
        random.shuffle(practice)
        for i, opacity in enumerate(practice, start=1):
            row = run_trial(ctx, scene, awareness, opacity)
            td.add_row({'phase': 'practice', 'trial': i, **row})
        ctx.screens.message(T.PRACTICE_END)

        block_thresholds, block_trials, status = [], [], 'completed'
        for block in range(1, config.CALIB_N_BLOCKS + 1):
            if block > 1:
                ctx.screens.break_screen(T.BREAK)
            ctx.screens.message(T.BLOCK_START.format(block=block, n_blocks=config.CALIB_N_BLOCKS))
            staircase = StepStaircase(step_params())
            while not staircase.done:
                opacity = staircase.intensity
                row = run_trial(ctx, scene, awareness, opacity)
                step_log = staircase.update(row['correct'], row['seen'])
                step_log.pop('intensity')   # same as 'opacity'
                td.add_row({'phase': 'calibration', 'block': block, 'trial': staircase.trial,
                            **row, **step_log})
            threshold = staircase.threshold()
            block_trials.append(staircase.trial)
            td.add_row({'phase': 'calibration', 'block': block, 'event': 'block_threshold',
                        'block_threshold': threshold, 'block_n_trials': staircase.trial,
                        'block_cwir': staircase.cwir, 'cap_reached': int(staircase.cap_reached)})
            if staircase.cap_reached:
                status = f'cap_reached_block{block}'
                break
            block_thresholds.append(threshold)

        final = sum(block_thresholds) / len(block_thresholds) if status == 'completed' else None
        if final is not None:
            td.add_row({'phase': 'calibration', 'event': FINAL_THRESHOLD_EVENT, 'final_threshold': final,
                        'block_thresholds': ';'.join(f'{t:.4f}' for t in block_thresholds)})
        append_calibration_summary({
            'subject': ctx.participant['subject'], 'day': ctx.participant['day'],
            'session_date': ctx.participant['date'], 'status': status,
            'final_threshold': final if final is not None else '',
            **{f'block{b}_threshold': (block_thresholds[b - 1] if b <= len(block_thresholds) else '')
               for b in range(1, config.CALIB_N_BLOCKS + 1)},
            **{f'block{b}_n_trials': (block_trials[b - 1] if b <= len(block_trials) else '')
               for b in range(1, config.CALIB_N_BLOCKS + 1)},
            'gold_side': awareness.gold_side,
            'coin_duration_s': config.FEEDBACK_COIN_DURATION,
            'data_file': td.base + '.csv'})

    if final is None:
        raise StopDay(f'Calibration reached {config.CALIB_MAX_TRIALS} trials without converging '
                      f'({status}); the subliminal task will not run. See {td.base}.csv')
    ctx.screens.message(T.END)
    ctx.calibration_threshold = final
    return final


def run_trial(ctx, scene, awareness, opacity):
    """One calibration trial at the given opacity. Returns the data row."""
    outcome = REWARD if random.random() < config.CALIB_GOLD_PROBABILITY else NO_REWARD
    ctx.keys.check_abort()
    t_pre = show(ctx.win, scene.draw_background, config.WAIT_POST_CHOICE)
    timing = scene.feedback_sequence(outcome, opacity)
    timing.pop('coin_opacity')               # same as 'opacity'
    pas, pas_rt = awareness.pas()
    chosen, choice_rt = awareness.coin_choice()
    return {'opacity': opacity, 'coin_shown': outcome, 'pas': pas, 'pas_rt': pas_rt,
            'seen': int(pas > 0), 'coin_chosen': chosen, 'choice_rt': choice_rt,
            'correct': int(chosen == outcome), 't_pre_feedback': t_pre, **timing}


def build_pages(scene, gold_side):
    """Instruction pages with their pictures; the scene example uses the real casino scene."""
    gold_key = T.SIDE_NAMES[gold_side]
    black_key = T.SIDE_NAMES['right' if gold_side == 'left' else 'left']
    pages = []
    for spec in T.PAGES:
        page = {'title': T.TITLE, 'text': spec['text'].format(gold_key=gold_key, black_key=black_key)}
        if spec.get('scene'):
            page['draw'] = _scene_example(scene)
        if spec.get('coins'):
            size = config.CHOICE_COIN_SIZE
            page['images'] = [(config.COIN_REWARD_IMAGE, (config.CHOICE_COIN_X, -1.0), size),
                              (config.COIN_NO_REWARD_IMAGE, (-config.CHOICE_COIN_X, -1.0), size)]
        if spec.get('mask'):
            page['images'] = [(config.MASK_IMAGES[0], (0, -2.0), config.CHOICE_COIN_SIZE)]
        pages.append(page)
    return pages


def _scene_example(scene):
    """Draw the casino scene, shifted down, with a full-opacity gold coin in the feedback box."""
    def draw():
        shift = config.INSTR_SCENE_SHIFT_Y
        stims = scene.arms + [scene.feedback_box, scene.coins[REWARD]]
        for s in stims:
            s.pos = (s.pos[0], s.pos[1] + shift)
        scene.coins[REWARD].opacity = 1.0
        for s in stims:
            s.draw()
        for s in stims:
            s.pos = (s.pos[0], s.pos[1] - shift)
    return draw
