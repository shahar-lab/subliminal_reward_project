// ─── wm.js ────────────────────────────────────────────────────────────────────
// Visual working-memory capacity: change-detection task (Day 1). Based on ioc-wm's
// js/working_memory.js (same geometry, images, timings) with the structure of the lab port
// ../tasks/wm/run.py:
//   instructions -> quiz (any mistake -> back to instructions)
//   -> practice (WM_N_PRACTICE trials, WM_PRACTICE_N_SET1 of them set size 1 incl. the first; repeated until every
//      set-size-1 trial is correct) -> WM_N_TRIALS test trials -> K per set size (summary row).
//   Trial: fixation 1000 -> memory array 200 -> fixation 900 -> test square (s/k, max 6000) -> feedback 500.
// Same/different keys: from the first character of the participant ID (code // 2, as the lab's ID // 2).

function wmTimeline() {
    const C = CONFIG, T = SESSION.T, W = T.wm;
    const sameKey = C.WM_KEYS[Math.floor(SESSION.id_code / 2) % 2];   // independent of the gold-side parity
    const diffKey = C.WM_KEYS.find(k => k !== sameKey);
    const keyValues = { same_key: sameKey, diff_key: diffKey };
    const rng = makeRng(makeSeed(null));
    const QUADRANTS = ['abc', 'def', 'ghi', 'jkl'];                  // top-left, top-right, bottom-right, bottom-left
    const SIGNS = [[-1, 1], [1, 1], [1, -1], [-1, -1]];
    const MIDLINE = ['upper1', 'upper2', 'upper3', 'lower1', 'lower2', 'lower3'];

    // centre offsets (px, y up) - identical to ioc-wm's CSS positions
    const offset = k => C.WM_STEP * k - C.WM_SQUARE_SIZE / 2;
    const POS = {};
    QUADRANTS.forEach((letters, q) => letters.split('').forEach((l, k) => {
        POS[l] = [SIGNS[q][0] * offset(k + 1), SIGNS[q][1] * offset(k + 1)];
    }));
    [3, 2, 1].forEach((k, i) => { POS['upper' + (i + 1)] = [0, offset(k)]; POS['lower' + (i + 1)] = [0, -offset(k)]; });

    function pickLocations(setSize) {
        if (setSize === 1) return [rng.choice(MIDLINE)];
        const locs = [];
        QUADRANTS.forEach(letters => {
            const two = rng.sample(letters.split(''), 2);
            locs.push(two[0]);
            if (setSize > 4) locs.push(two[1]);
        });
        return locs;
    }
    function makeTrial(setSize, condition) {
        const colours = rng.shuffle(C.WM_COLORS);
        const locs = pickLocations(setSize);
        const testIndex = rng.int(setSize);
        const original = colours[testIndex];
        const testColour = condition === 'same' ? original : rng.choice(colours.slice(setSize));
        return { set_size: setSize, condition: condition, array_colours: colours.slice(0, setSize), array_locations: locs,
                 test_index: testIndex, test_location: locs[testIndex], original_colour: original, test_colour: testColour };
    }
    function conditionSequence(n) {
        const conds = [];
        C.WM_SET_SIZES.forEach(s => ['same', 'diff'].forEach(c => conds.push([s, c])));
        if (!C.WM_BALANCED_CONDITIONS) return Array.from({ length: n }, () => rng.choice(conds));
        let seq = [];
        while (seq.length + conds.length <= n) seq = seq.concat(conds);
        seq = seq.concat(rng.sample(conds, n - seq.length));
        return rng.shuffle(seq);
    }
    // first trial set size 1; nSet1 set-size-1 trials in total (the others at random positions); the rest 4 or 8
    function practiceSequence(n, nSet1) {
        const set1 = () => [1, rng.choice(['same', 'diff'])];
        const big = () => [rng.choice([4, 8]), rng.choice(['same', 'diff'])];
        const k = Math.max(1, Math.min(nSet1, n));
        const rest = rng.shuffle(Array.from({ length: n - 1 }, (_, i) => (i < k - 1 ? set1() : big())));
        return [set1()].concat(rest);
    }

    const fixation = '<div class="wm-fixation">+</div>';
    function squaresHtml(colours, locs) {
        const cx = window.innerWidth / 2, cy = window.innerHeight / 2, s = C.WM_SQUARE_SIZE;
        return colours.map((col, i) => {
            const [x, y] = POS[locs[i]];
            return `<img class="wm-square" src="stimuli/squares/${col}.png" `
                 + `style="left:${cx + x - s / 2}px;top:${cy - y - s / 2}px;width:${s}px;height:${s}px;">`;
        }).join('') + fixation;
    }

    let current = null;
    const allExpRows = [];
    let practiceRows = [];
    let practiceAttempt = 0;

    function trialNodes(getTrial, phase, info) {
        const fix = { type: jsPsychHtmlKeyboardResponse, stimulus: fixation, choices: 'NO_KEYS',
                      trial_duration: C.WM_FIXATION_DURATION, on_start: () => { current = getTrial(); },
                      data: { task: 'wm', screen: 'wm_fixation' } };
        const memory = { type: jsPsychHtmlKeyboardResponse, stimulus: () => squaresHtml(current.array_colours, current.array_locations),
                         choices: 'NO_KEYS', trial_duration: C.WM_MEMORY_DURATION, data: { task: 'wm', screen: 'wm_memory' } };
        const retention = { type: jsPsychHtmlKeyboardResponse, stimulus: fixation, choices: 'NO_KEYS',
                            trial_duration: C.WM_RETENTION_DURATION, data: { task: 'wm', screen: 'wm_retention' } };
        const test = withBot({
            type: jsPsychHtmlKeyboardResponse,
            stimulus: () => squaresHtml([current.test_colour], [current.test_location]),
            choices: C.WM_KEYS,
            trial_duration: C.WM_RESPONSE_LIMIT,
            data: Object.assign({ task: 'wm', screen: 'wm_test', phase: phase }, info),
            on_finish: data => {
                const correctKey = current.condition === 'same' ? sameKey : diffKey;
                const response = data.response === null ? null : String(data.response).toLowerCase();
                const accuracy = response === null ? null : (response === correctKey ? 1 : 0);
                Object.assign(data, {
                    set_size: current.set_size, condition: current.condition,
                    array_colours: current.array_colours.join(';'), array_locations: current.array_locations.join(';'),
                    test_location: current.test_location, test_index: current.test_index,
                    original_colour: current.original_colour, test_colour: current.test_colour,
                    same_key: sameKey, correct_key: correctKey, accuracy: accuracy,
                });
                if (phase === 'practice') { data.practice_attempt = practiceAttempt; practiceRows.push(data); }
                else allExpRows.push(data);
            },
        }, () => {
            const correctKey = current.condition === 'same' ? sameKey : diffKey;
            const ok = current.set_size === 1 || Math.random() < C.BOT_WM_ACCURACY;
            BOT.key(ok ? correctKey : C.WM_KEYS.find(k => k !== correctKey));
        });
        const feedback = {
            type: jsPsychHtmlKeyboardResponse,
            stimulus: () => {
                const acc = SESSION.jsPsych.data.getLastTrialData().values()[0].accuracy;
                const text = acc === null ? W.FEEDBACK_TOO_SLOW : (acc ? W.FEEDBACK_CORRECT : W.FEEDBACK_INCORRECT);
                return `<div class="wm-fixation wm-feedback" dir="${T.dir}">${text}</div>`;
            },
            choices: 'NO_KEYS', trial_duration: C.WM_FEEDBACK_DURATION, data: { task: 'wm', screen: 'wm_feedback' },
        };
        return [fix, memory, retention, test, feedback];
    }

    // instructions
    function pages() {
        const imgs = { fixation: 'fixation', example_memory: 'example1', example_same: 'example2', example_diff: 'example3' };
        return W.PAGES.map(spec => {
            let pic = '';
            Object.keys(imgs).forEach(k => { if (spec[k]) pic = `<img class="wm-example-img" src="stimuli/examples/${imgs[k]}.png">`; });
            return pageHtml(W.TITLE, para(fmt(spec.text, keyValues)) + pic, 'wm-page');
        });
    }
    const quiz = W.QUIZ.map(q => Object.assign({}, q, { options: q.options.map(o => fmt(o, keyValues)) }));

    const tl = [];
    tl.push(callFunction(() => {
        document.body.classList.add('wm-background');
        SESSION.jsPsych.data.addProperties({ wm_same_key: sameKey });
    }));
    tl.push(instructionsWithQuiz('wm', pages, quiz, W.QUIZ_FAILED));

    // practice, repeated until all set-size-1 trials are correct
    let practicePassed = false;
    const practiceBlock = {
        timeline: [
            callFunction(() => { practiceAttempt++; practiceRows = []; }),
            messageScreen(() => fmt(W.PRACTICE_START, keyValues) + '\n\n[[KEYBOARD]]\n\n' + fmt(W.PRACTICE_KEYS, keyValues)
                                + '\n\n' + W.PRACTICE_ACCURATE, { task: 'wm' }, 'wm-page'),
        ],
        loop_function: () => !practicePassed,
    };
    // the practice trial list is drawn anew on every attempt
    let practiceList = [], practiceIdx = 0;
    practiceBlock.timeline.push(callFunction(() => { practiceList = practiceSequence(C.WM_N_PRACTICE, C.WM_PRACTICE_N_SET1); practiceIdx = 0; }));
    for (let i = 0; i < C.WM_N_PRACTICE; i++) {
        trialNodes(() => { const [s, c] = practiceList[practiceIdx++]; return makeTrial(s, c); }, 'practice', { trial: i + 1 })
            .forEach(n => practiceBlock.timeline.push(n));
    }
    practiceBlock.timeline.push(callFunction(() => {
        practicePassed = practiceRows.filter(r => r.set_size === 1).every(r => r.accuracy === 1);
    }));
    practiceBlock.timeline.push({ timeline: [messageScreen(W.PRACTICE_FAILED, { task: 'wm' }, 'wm-page')],
                                  conditional_function: () => !practicePassed });
    tl.push(practiceBlock);

    tl.push(messageScreen(W.EXP_START, { task: 'wm' }, 'wm-page'));
    conditionSequence(C.WM_N_TRIALS).forEach(([s, c], i) => {
        trialNodes(() => makeTrial(s, c), 'exp', { trial: i + 1 }).forEach(n => tl.push(n));
    });

    // summary: K = set size x (2 x accuracy - 1); no response = incorrect
    tl.push({
        type: jsPsychCallFunction, func: () => {},
        data: { task: 'wm', event: 'wm_capacity', phase: 'exp' },
        on_finish: data => {
            const ks = [];
            C.WM_SET_SIZES.forEach(size => {
                const rows = allExpRows.filter(r => r.set_size === size);
                data['n_trials_set' + size] = rows.length;
                if (!rows.length) return;
                const acc = rows.reduce((a, r) => a + (r.accuracy || 0), 0) / rows.length;
                data['accuracy_set' + size] = acc;
                data['K_set' + size] = size * (2 * acc - 1);
                ks.push(data['K_set' + size]);
            });
            data.K_mean = ks.length ? ks.reduce((a, b) => a + b, 0) / ks.length : null;
            SESSION.jsPsych.data.addProperties({ wm_K_mean: data.K_mean });
            console.log('WM capacity: K_mean', data.K_mean);
        },
    });
    tl.push(messageScreen(W.EXP_END, { task: 'wm' }, 'wm-page'));
    tl.push(callFunction(() => { document.body.classList.remove('wm-background'); }));
    return guardAfterQuiz(tl);
}
