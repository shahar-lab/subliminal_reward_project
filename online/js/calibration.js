// ─── calibration.js ───────────────────────────────────────────────────────────
// STEP calibration (Day 2), shown in the casino scene exactly like the bandit's feedback.
// Port of ../tasks/calibration/run.py.
// Flow: instructions -> quiz (repeat until all correct) -> block 1 -> break -> block 2.
// Trial (casino-trial, mode 'feedback_only', probe): empty arms -> mask - coin - mask -> PAS -> coin choice.
// Rows: one per staircase trial (phase 'calibration'), one 'block_threshold' row per block, one
// 'final_threshold' row. The result is stored in SESSION.calibration = {threshold, status, ...}.
//
// Cap (a block reaches CALIB_MAX_TRIALS without converging): see CALIB_CAP_ACTION in config.js.

function calibrationTimeline() {
    const C = CONFIG, T = SESSION.T, K = T.calibration;
    const params = {
        start_intensity: C.CALIB_START_OPACITY, max_intensity: C.CALIB_MAX_OPACITY, min_intensity: C.CALIB_MIN_OPACITY,
        initial_step: C.CALIB_INITIAL_STEP, step_decrease: C.CALIB_STEP_DECREASE, min_step: C.CALIB_MIN_STEP,
        cwir_stop: C.CALIB_CWIR_STOP, min_trials: C.CALIB_MIN_TRIALS, max_trials: C.CALIB_MAX_TRIALS,
    };
    const blocks = [];          // {threshold, n_trials, cwir, cap_reached}
    let staircase = null;
    let capStop = false;        // CALIB_CAP_ACTION = 'stop' and a block hit the cap
    SESSION.calibration = { threshold: null, status: 'not_run' };

    function pages() {
        const goldKey = K.SIDE_NAMES[SESSION.gold_side];
        const blackKey = K.SIDE_NAMES[SESSION.gold_side === 'left' ? 'right' : 'left'];
        return K.PAGES.map(spec => {
            const text = fmt(spec.text, { gold_key: goldKey, black_key: blackKey });
            let pic = '';
            if (spec.scene) pic = DISPLAY.sceneImageHtml({ circles: null, coin: { outcome: 'reward', opacity: 1 } });
            if (spec.coins) {   // gold on the right, silver on the left (as the text says), as in the lab version
                pic = `<div class="choice-coins" dir="ltr" style="gap:${2 * C.CHOICE_COIN_X - C.CHOICE_COIN_SIZE}px">`
                    + coinImg(C.COIN_NO_REWARD_IMAGE) + coinImg(C.COIN_REWARD_IMAGE) + '</div>';
            }
            if (spec.mask) pic = coinImg(C.MASK_IMAGES[0]);
            return pageHtml(K.TITLE, para(text) + `<div class="instr-picture">${pic}</div>`);
        });
    }

    const trialNode = block => ({
        type: jsPsychCasinoTrial,
        mode: 'feedback_only',
        outcome: () => (Math.random() < C.CALIB_GOLD_PROBABILITY ? 'reward' : 'no_reward'),
        opacity: () => staircase.intensity,
        coin_duration: C.FEEDBACK_COIN_DURATION[2],
        probe: true,
        gold_side: () => SESSION.gold_side,
        texts: casinoTexts,
        rtl: T.dir === 'rtl',
        bot: SESSION.bot,
        data: { task: 'calibration', phase: 'calibration', block: block },
        on_finish: data => {
            const log = staircase.update(data.twoafc_correct, data.seen);
            delete log.intensity;          // = coin_opacity
            Object.assign(data, log, { trial: staircase.trial, opacity: data.coin_opacity, correct: data.twoafc_correct });
        },
    });

    const tl = [];
    tl.push(instructionsWithQuiz('calibration', pages, K.QUIZ));
    tl.push(messageScreen(K.CALIBRATION_START, { task: 'calibration' }));
    for (let block = 1; block <= C.CALIB_N_BLOCKS; block++) {
        const blockTl = [];
        if (block > 1) blockTl.push(messageScreen(K.BREAK, { task: 'calibration', screen: 'break' }));
        blockTl.push(messageScreen(fmt(K.BLOCK_START, { block: block, n_blocks: C.CALIB_N_BLOCKS }), { task: 'calibration' }));
        blockTl.push(callFunction(() => { staircase = new StepStaircase(params); }));
        blockTl.push({ timeline: [trialNode(block)], loop_function: () => !staircase.done });
        blockTl.push({
            type: jsPsychCallFunction,
            func: () => {},
            data: { task: 'calibration', phase: 'calibration', block: block, event: 'block_threshold' },
            on_finish: data => {
                const b = { threshold: staircase.threshold(), n_trials: staircase.trial, cwir: staircase.cwir,
                            cap_reached: staircase.capReached };
                blocks.push(b);
                if (b.cap_reached && C.CALIB_CAP_ACTION === 'stop') capStop = true;
                Object.assign(data, { block_threshold: b.threshold, block_n_trials: b.n_trials, block_cwir: b.cwir,
                                      cap_reached: b.cap_reached ? 1 : 0 });
            },
        });
        tl.push({ timeline: blockTl, conditional_function: () => !capStop });
    }
    tl.push({
        type: jsPsychCallFunction,
        func: () => {},
        data: { task: 'calibration', phase: 'calibration', event: 'final_threshold' },
        on_finish: data => {
            const capped = blocks.map((b, i) => (b.cap_reached ? i + 1 : null)).filter(x => x !== null);
            const status = capped.length ? 'cap_reached_block' + capped.join('_') : 'completed';
            const usable = blocks.filter(b => b.threshold !== null && (!b.cap_reached || C.CALIB_CAP_ACTION === 'continue'));
            let final = null, source = status === 'completed' ? 'staircase' : 'staircase_with_cap';
            if (capStop) final = null;
            else if (usable.length) final = usable.reduce((s, b) => s + b.threshold, 0) / usable.length;
            else { final = C.CALIB_FALLBACK_OPACITY; source = 'fallback'; }
            SESSION.calibration = { threshold: final, status: status, source: source,
                                    block_thresholds: blocks.map(b => b.threshold) };
            if (capStop) SESSION.stopped = 'calibration_cap';   // main.js shows CALIB_ERROR, completion code
            Object.assign(data, { final_threshold: final, calibration_status: status, threshold_source: source,
                                  block_thresholds: blocks.map(b => (b.threshold === null ? '' : b.threshold.toFixed(4))).join(';') });
            SESSION.jsPsych.data.addProperties({ calibration_threshold: final, calibration_status: status });
            console.log('Calibration:', SESSION.calibration);
        },
    });
    tl.push({ timeline: [messageScreen(K.END, { task: 'calibration' })], conditional_function: () => !SESSION.stopped });
    return guardAfterQuiz(tl);
}
