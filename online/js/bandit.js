// ─── bandit.js ────────────────────────────────────────────────────────────────
// Four-armed bandit ("casino game") - Day 1 (conscious coin) and Day 2 (subliminal coin).
// Port of ../tasks/bandit/run.py.
// Flow: instructions -> quiz (repeat until all correct) -> practice -> blocks with breaks -> bonus earned.
// ONLINE: money bonus (main trials only): gold coin +BONUS_WIN, silver coin -BONUS_LOSS, never below 0.
// Not shown during the game; shown at the end and saved (bonus_total per trial, bandit_bonus on every row).
// One casino-trial row per trial (phase practice/main). A miss or a grey-arm choice counts as a trial.
// Coin opacity: Day 1 = DAY1_COIN_OPACITY; Day 2 = this session's calibrated threshold (SESSION.calibration).

function casinoTexts() {
    const A = SESSION.T.awareness, B = SESSION.T.bandit;
    return { too_late: B.TOO_LATE, unavailable: B.UNAVAILABLE, pas_question: A.PAS_QUESTION,
             pas_options: A.PAS_OPTIONS, pas_footer: A.PAS_FOOTER,
             choice_question: para(A.CHOICE_QUESTION), choice_footer: A.CHOICE_FOOTER };
}

function banditTimeline(day) {
    const C = CONFIG, T = SESSION.T, B = T.bandit;
    const nMain = C.BANDIT_N_BLOCKS * C.BANDIT_TRIALS_PER_BLOCK;
    const seed = makeSeed(C.BANDIT_SEED);
    const practice = makeSchedule(C.BANDIT_N_PRACTICE, seed + 1, C);
    const schedule = makeSchedule(nMain, seed, C);
    const probeRate = C.AWARENESS_PROBE_RATE[day] || 0;
    const probeRng = makeRng(seed + 2);
    const values = { n_trials: nMain, n_breaks: C.BANDIT_N_BLOCKS - 1, time_limit: C.CHOICE_TIME_LIMIT / 1000,
                     penalty: C.UNAVAILABLE_CHOICE_DURATION / 1000 };
    const money = x => C.BONUS_CURRENCY + x.toFixed(2);
    values.win = money(C.BONUS_WIN);
    values.loss = money(C.BONUS_LOSS);
    values.zero = money(0);
    const state = { coins: 0, previous: null, bonusCents: 0 };     // cents: no floating-point drift
    const winCents = Math.round(C.BONUS_WIN * 100), lossCents = Math.round(C.BONUS_LOSS * 100);

    const opacity = () => (day === 1 ? C.DAY1_COIN_OPACITY : SESSION.calibration.threshold);
    const opacitySource = () => (day === 1 ? 'config' : 'this_session_calibration');

    function pages() {
        const title = day === 1 ? B.TITLE : B.TITLE_DAY2;
        const specs = (day === 1 ? B.PAGES_DAY1_INTRO : B.PAGES_DAY2_INTRO)
            .concat(B.PAGES_RULES, day === 2 ? [B.PAGE_MASK_DAY2] : [], B.PAGES_TIPS);
        return specs.map(spec => {
            let text = fmt(spec.text, values);
            if (spec.mask && probeRate > 0) text += B.PROBE_SENTENCE;
            let pic = '';
            if (spec.reward_coin) pic = coinImg(C.COIN_REWARD_IMAGE);
            if (spec.no_reward_coin) pic = coinImg(C.COIN_NO_REWARD_IMAGE);
            if (spec.mask) pic = coinImg(C.MASK_IMAGES[0]);
            if (spec.offer) pic = DISPLAY.sceneImageHtml({ circles: { offered: spec.offer, colours: C.CIRCLE_COLOR_NAMES.slice(0, spec.offer.length) } });
            return pageHtml(title, para(text) + `<div class="instr-picture">${pic}</div>`);
        });
    }
    const quiz = B.QUIZ.map(q => Object.assign({}, q, { prompt: fmt(q.prompt, values), options: q.options.map(o => fmt(o, values)) }));

    function trialNode(trial, info, probe) {
        return {
            type: jsPsychCasinoTrial,
            mode: 'bandit',
            offered_arms: trial.offered_arms, colours: trial.colours, probs: trial.probs, outcome_draw: trial.outcome_draw,
            opacity: opacity,
            coin_duration: C.FEEDBACK_COIN_DURATION[day],
            probe: probe,
            gold_side: () => SESSION.gold_side,
            texts: casinoTexts,
            rtl: T.dir === 'rtl',
            bot: SESSION.bot,
            data: Object.assign({ task: 'bandit', day: day, seed: seed, opacity_source: opacitySource }, info),
            on_finish: data => {
                if (data.phase === 'main') {
                    state.coins += data.reward || 0;
                    data.coins_total = state.coins;
                    const before = state.bonusCents;
                    if (data.reward === 1) state.bonusCents += winCents;
                    else if (data.reward === 0) state.bonusCents = Math.max(0, state.bonusCents - lossCents);
                    data.bonus_change = (state.bonusCents - before) / 100;
                    data.bonus_total = state.bonusCents / 100;
                }
                data.reward_oneback = state.previous;
                state.previous = data.reward;
            },
        };
    }

    const tl = [];
    tl.push(callFunction(() => {
        SESSION.jsPsych.data.addProperties({ bandit_seed: seed, probe_rate: probeRate });
        console.log(`Bandit day ${day}: coin opacity ${opacity()} (${opacitySource()}), seed ${seed}`);
    }));
    tl.push(instructionsWithQuiz('bandit', pages, quiz));
    if (practice.length) {
        tl.push(messageScreen(fmt(B.PRACTICE_START, { n: practice.length }), { task: 'bandit' }));
        practice.forEach((trial, i) => tl.push(trialNode(trial, { phase: 'practice', trial: i + 1 }, false)));
        tl.push(callFunction(() => { state.previous = null; }));
        tl.push(messageScreen(B.PRACTICE_END, { task: 'bandit' }));
    }
    schedule.forEach((trial, i) => {
        const t = i + 1;
        const block = Math.floor(i / C.BANDIT_TRIALS_PER_BLOCK) + 1;
        const probe = probeRate > 0 && probeRng() < probeRate;
        tl.push(trialNode(trial, { phase: 'main', block: block, trial: t,
                                   trial_in_block: i % C.BANDIT_TRIALS_PER_BLOCK + 1 }, probe));
        if (t % C.BANDIT_TRIALS_PER_BLOCK === 0 && block < C.BANDIT_N_BLOCKS) {
            tl.push(messageScreen(fmt(B.BREAK, { done: block, total: C.BANDIT_N_BLOCKS }), { task: 'bandit', screen: 'break' }));
        }
    });
    tl.push(messageScreen(() => (C.SHOW_TOTAL_DAY[day] ? fmt(B.END_WITH_TOTAL, { coins: state.coins, bonus: money(state.bonusCents / 100) }) : B.END_NO_TOTAL),
                          { task: 'bandit', screen: 'bandit_end' }));
    tl.push(callFunction(() => {
        SESSION.jsPsych.data.addProperties({ bandit_coins_total: state.coins, bandit_bonus: state.bonusCents / 100 });
        console.log(`Bandit day ${day}: ${state.coins} gold coins, bonus ${money(state.bonusCents / 100)}`);
    }));
    return guardAfterQuiz(tl);
}
