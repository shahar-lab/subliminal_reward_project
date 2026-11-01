// ─── common.js ────────────────────────────────────────────────────────────────
// Shared building blocks: session settings, text formatting, message screens,
// instructions + quiz loop, and the bot (automatic participant) helpers.

// Session settings (filled by setupSession in main.js before any timeline is built)
const SESSION = { day: 1, lang: 'en', T: null, bot: false, short: false, jsPsych: null,
                  on_pavlovia: false, subject_id: 'not_provided' };

// '\n\n' -> paragraphs, '\n' -> line breaks
function para(text) {
    return String(text).split('\n\n').map(p => `<p>${p.split('\n').join('<br>')}</p>`).join('')
        .replace('<p>[[KEYBOARD]]</p>', '<img class="wm-example-img" src="stimuli/examples/keyboard.png">');
}

// fill {placeholders}
function fmt(text, values) {
    return String(text).replace(/\{(\w+)\}/g, (m, k) => (values && k in values ? values[k] : m));
}

function pageHtml(title, bodyHtml, extraClass) {
    const dir = SESSION.T.dir;
    return `<div class="instr-page ${extraClass || ''}" dir="${dir}">`
         + (title ? `<h2>${title}</h2>` : '') + bodyHtml + '</div>';
}

// ── bot helpers ──────────────────────────────────────────────────────────────
const BOT = {
    after(fn, delay) { setTimeout(fn, delay === undefined ? CONFIG.BOT_RESPONSE_DELAY : delay); },
    key(key, code) {
        const target = SESSION.jsPsych.getDisplayElement();
        const opts = { key: key, code: code || key, bubbles: true, cancelable: true };
        target.dispatchEvent(new KeyboardEvent('keydown', opts));
        target.dispatchEvent(new KeyboardEvent('keyup', opts));
    },
    click(selector) {
        const el = document.querySelector(selector);
        if (el) el.click();
    },
    // press "next" until the instructions end
    instructions() {
        const step = () => {
            const btn = document.getElementById('jspsych-instructions-next');
            if (!btn) return;
            btn.click();
            BOT.after(step, 60);
        };
        BOT.after(step);
    },
};

// Adds an automatic answer to a trial in bot mode. action(trial) runs after the trial loads.
function withBot(trial, action) {
    if (!SESSION.bot) return trial;
    const userLoad = trial.on_load;
    trial.on_load = function () {
        if (userLoad) userLoad.apply(this, arguments);
        BOT.after(() => action(trial));
    };
    return trial;
}

// ── simple screens ───────────────────────────────────────────────────────────
// Text screen; continues with the space bar.
function messageScreen(text, data, extraClass) {
    return withBot({
        type: jsPsychHtmlKeyboardResponse,
        stimulus: typeof text === 'function' ? () => pageHtml('', para(text()), extraClass) : pageHtml('', para(text), extraClass),
        choices: [' '],
        data: Object.assign({ screen: 'message' }, data || {}),
    }, () => BOT.key(' ', 'Space'));
}

function callFunction(func) {
    return { type: jsPsychCallFunction, func: func };
}

// nodes that run only while the session has not been stopped
function unlessStopped(nodes) {
    return { timeline: nodes, conditional_function: () => !SESSION.stopped };
}

// A task timeline [..., quiz loop, rest...]: the rest runs only if the quiz was passed.
function guardAfterQuiz(tl) {
    const i = tl.findIndex(n => n && n.isQuizLoop);
    if (i < 0) return tl;
    delete tl[i].isQuizLoop;   // jsPsych would pass unknown node properties down to the trials
    return tl.slice(0, i + 1).concat([unlessStopped(tl.slice(i + 1))]);
}

// ── instructions + quiz ──────────────────────────────────────────────────────
// pages: function returning an array of HTML strings (evaluated when the trial starts).
// quiz: [{name, prompt, options, correct (0-based index)}].
// All questions on one page; any mistake -> message -> back to the instructions. After
// CONFIG.QUIZ_MAX_ATTEMPTS failed attempts the session stops (SESSION.stopped = 'quiz_failed_<name>';
// the participant is sent back with SCREENED_OUT_CODE). Every attempt is saved (quiz_attempt, quiz_passed, quiz_wrong).
// Use guardAfterQuiz() on the task timeline so the rest of the task is skipped after a failure.
function instructionsWithQuiz(name, pages, quiz, failText) {
    const T = SESSION.T, C = T.common;
    const rtl = T.dir === 'rtl';
    let attempt = 0, passed = false;

    const instructions = withBot({
        type: jsPsychInstructions,
        pages: () => pages().map(p => p + `<div class="nav-hint" dir="${T.dir}">${C.NAV_HINT}</div>`),
        show_clickable_nav: true,
        key_forward: rtl ? 'ArrowLeft' : 'ArrowRight',
        key_backward: rtl ? 'ArrowRight' : 'ArrowLeft',
        button_label_next: C.NEXT,
        button_label_previous: C.PREV,
        css_classes: rtl ? ['rtl-instructions'] : [],
        data: { screen: 'instructions', instructions: name },
    }, () => BOT.instructions());

    const quizTrial = withBot({
        type: jsPsychSurveyMultiChoice,
        preamble: `<div dir="${T.dir}"><p>${C.QUIZ_PREAMBLE}</p></div>`,
        questions: quiz.map(q => ({ prompt: `<span dir="${T.dir}">${q.prompt}</span>`, name: q.name,
                                    // escaped: the plugin puts each option inside value="..." (a raw " would cut it)
                                    options: q.options.map(o => o.replace(/&/g, '&amp;').replace(/"/g, '&quot;')),
                                    required: true })),
        button_label: C.QUIZ_SUBMIT,
        css_classes: rtl ? ['rtl-survey'] : [],
        data: { screen: 'quiz', quiz: name },
        on_start: () => { attempt++; },
        on_finish: data => {
            const wrong = quiz.filter(q => data.response[q.name] !== q.options[q.correct]).map(q => q.name);
            passed = wrong.length === 0;
            if (!passed && CONFIG.QUIZ_MAX_ATTEMPTS && attempt >= CONFIG.QUIZ_MAX_ATTEMPTS) SESSION.stopped = 'quiz_failed_' + name;
            Object.assign(data, { quiz_attempt: attempt, quiz_passed: passed ? 1 : 0, quiz_n_wrong: wrong.length,
                                  quiz_wrong: wrong.join(';') });
        },
    }, () => {
        quiz.forEach((q, i) => {
            const pick = SESSION.bot_quiz_wrong ? (q.correct + 1) % q.options.length : q.correct;
            const el = document.getElementById(`jspsych-survey-multi-choice-response-${i}-${pick}`);
            if (el) el.checked = true;
        });
        BOT.click('#jspsych-survey-multi-choice-next');
    });

    const out = () => !!SESSION.stopped;
    const failed = {
        timeline: [withBot({
            type: jsPsychHtmlButtonResponse,
            stimulus: () => pageHtml('', para(out() ? fmt(C.QUIZ_OUT, { n: CONFIG.QUIZ_MAX_ATTEMPTS }) : (failText || C.QUIZ_FAILED))),
            choices: () => [out() ? C.DAY_STOPPED_BUTTON : C.BACK_TO_INSTRUCTIONS],
            on_finish: () => { if (out()) document.body.classList.remove('wm-background'); },
            data: { screen: 'quiz_failed', quiz: name },
        }, () => BOT.click('#jspsych-html-button-response-button-0'))],
        conditional_function: () => !passed,
    };

    return { timeline: [instructions, quizTrial, failed], loop_function: () => !passed && !out(), isQuizLoop: true };
}

// Pictures for instruction pages, shared by bandit and calibration
function coinImg(src, size) {
    size = size || CONFIG.CHOICE_COIN_SIZE;
    return `<img class="instr-img" src="${src}" style="width:${size}px;height:${size}px;">`;
}
