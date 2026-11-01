// ─── questionnaires.js ────────────────────────────────────────────────────────
// End-of-day questionnaires (both days), as ../tasks/questionnaires/run.py and ioc-wm:
// the two open questions (typed; pasting disabled, as in ioc-wm), then the 36-item IMI
// (one statement per screen, 1-7) with 6 attention checks, then a summary row
// (failed attention checks, subscale means; reverse-scored items as 8 - response).

// [category, reverse-scored, attention check, expected answer 1-7] - same order as the IMI texts
const IMI_ITEMS = [
        ['Perceived Competence', false, false, null],
        ['Interest/Enjoyment', false, false, null],
        ['Perceived Competence', true, false, null],
        ['Attention', false, true, 1],
        ['Effort/Importance', false, false, null],
        ['Effort/Importance', false, false, null],
        ['Perceived Competence', false, false, null],
        ['Perceived Choice', true, false, null],
        ['Pressure/Tension', true, false, null],
        ['Attention', true, true, 7],
        ['Interest/Enjoyment', false, false, null],
        ['Effort/Importance', true, false, null],
        ['Perceived Choice', true, false, null],
        ['Pressure/Tension', false, false, null],
        ['Interest/Enjoyment', false, false, null],
        ['Attention', true, true, 7],
        ['Pressure/Tension', true, false, null],
        ['Interest/Enjoyment', false, false, null],
        ['Perceived Choice', false, false, null],
        ['Perceived Choice', true, false, null],
        ['Attention', false, true, 1],
        ['Perceived Choice', true, false, null],
        ['Interest/Enjoyment', true, false, null],
        ['Interest/Enjoyment', false, false, null],
        ['Perceived Choice', false, false, null],
        ['Attention', false, true, 1],
        ['Pressure/Tension', false, false, null],
        ['Interest/Enjoyment', true, false, null],
        ['Pressure/Tension', true, false, null],
        ['Perceived Competence', false, false, null],
        ['Attention', true, true, 7],
        ['Perceived Competence', false, false, null],
        ['Effort/Importance', true, false, null],
        ['Perceived Competence', false, false, null],
        ['Perceived Choice', true, false, null],
        ['Effort/Importance', false, false, null],
];

function questionnairesTimeline() {
    const C = CONFIG, T = SESSION.T, Q = T.questionnaires;
    const tl = [];
    const imiRows = [];

    if (C.QUESTIONNAIRE_FINAL_QUESTIONS) {
        tl.push(withBot({
            type: jsPsychSurveyText,
            preamble: `<div dir="${T.dir}"><h2>${Q.FINAL_TITLE}</h2></div>`,
            questions: Q.FINAL_QUESTIONS.map(q => ({ prompt: `<div dir="${T.dir}">${q.prompt}</div>`, name: q.name,
                                                    placeholder: Q.TEXT_PLACEHOLDER, rows: 6, required: true })),
            button_label: Q.CONTINUE,
            css_classes: T.dir === 'rtl' ? ['rtl-survey'] : [],
            data: { task: 'questionnaires', phase: 'final_questions' },
            on_load: () => {
                document.querySelectorAll('textarea').forEach(el => {
                    el.setAttribute('dir', 'auto');
                    el.addEventListener('paste', e => e.preventDefault());
                });
            },
        }, () => {
            document.querySelectorAll('textarea').forEach(el => { el.value = 'bot answer'; });
            BOT.click('#jspsych-survey-text-next');
        }));
    }

    if (C.QUESTIONNAIRE_IMI) {
        tl.push(messageScreen(Q.IMI_INTRO, { task: 'questionnaires' }));
        const labels = ['1<br>(' + Q.IMI_LOW + ')', '2', '3', '4', '5', '6', '7<br>(' + Q.IMI_HIGH + ')'];
        IMI_ITEMS.forEach(([category, reverse, attention, expected], i) => {
            tl.push(withBot({
                type: jsPsychSurveyLikert,
                questions: [{ prompt: `<div dir="${T.dir}"><b>${fmt(Q.IMI_TITLE, { n: i + 1, total: IMI_ITEMS.length })}</b><br>`
                                    + `<span class="imi-statement">${Q.IMI[i]}</span></div>`,
                              name: 'Q' + (i + 1), labels: labels, required: true }],
                scale_width: 600,
                button_label: Q.CONTINUE,
                data: { task: 'questionnaires', phase: 'imi', question_index: i + 1, category: category,
                        reverse_scored: reverse ? 1 : 0, attention: attention ? 1 : 0, expected_answer: expected },
                on_finish: data => {
                    const value = data.response['Q' + (i + 1)] + 1;          // plugin gives 0-6
                    data.imi_response = value;
                    data.attention_failed = attention ? (value !== expected ? 1 : 0) : null;
                    imiRows.push({ category, reverse, attention, expected, value });
                },
            }, () => {
                const value = attention ? expected : 1 + Math.floor(Math.random() * 7);
                const el = document.querySelector(`input[name="Q0"][value="${value - 1}"]`);
                if (el) el.checked = true;
                BOT.click('#jspsych-survey-likert-next');
            }));
        });
        tl.push({
            type: jsPsychCallFunction, func: () => {},
            data: { task: 'questionnaires', phase: 'imi', event: 'imi_summary' },
            on_finish: data => {
                data.failed_attention_checks = imiRows.filter(r => r.attention && r.value !== r.expected).length;
                const byCat = {};
                imiRows.filter(r => !r.attention).forEach(r => {
                    (byCat[r.category] = byCat[r.category] || []).push(r.reverse ? 8 - r.value : r.value);
                });
                Object.keys(byCat).forEach(c => {
                    const key = 'imi_' + c.toLowerCase().replace(/\//g, '_').replace(/ /g, '_');
                    data[key] = byCat[c].reduce((a, b) => a + b, 0) / byCat[c].length;
                });
                SESSION.jsPsych.data.addProperties({ failed_attention_checks: data.failed_attention_checks });
            },
        });
    }
    return tl;
}
