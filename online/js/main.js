// ─── main.js ──────────────────────────────────────────────────────────────────
// Session setup and the day timelines (as run_day_1.py / run_day_2.py):
//   Day 1: working memory -> casino game (conscious coin) -> questionnaires
//   Day 2: STEP calibration -> casino game at the calibrated opacity -> questionnaires
// Around them (as ioc-wm / ioc-all): Pavlovia init, desktop-only gate, preload, CAPTCHA,
// fullscreen, refresh-rate measurement ... end screen, Pavlovia finish, Prolific redirect.

(function () {
    'use strict';
    const C = CONFIG;
    const url = new URLSearchParams(window.location.search);

    // ── session settings ─────────────────────────────────────────────────────
    const day = url.get('day') === '2' ? 2 : 1;
    const lang = (url.get('lang') || C.DEFAULT_LANGUAGE) === 'he' ? 'he' : 'en';
    const botParam = url.get('bot');
    const bot = botParam === '1' || botParam === 'full';
    const short = url.get('short') === '1' || botParam === '1';
    if (short) Object.assign(C, C.SHORT);
    // test hooks (bot only): &test=quiz_fail (bot answers quizzes wrongly), &test=calib_cap (calibration cannot converge)
    const testHook = bot ? url.get('test') : null;
    if (testHook === 'calib_cap') Object.assign(C, { CALIB_MAX_TRIALS: 4, CALIB_CWIR_STOP: 1000 });
    const onPavlovia = /(^|\.)pavlovia\.org$/.test(window.location.hostname);

    let experimentEnded = true, blurCount = 0, fullscreenExitCount = 0;
    const jsPsych = initJsPsych({
        on_data_update: () => {
            jsPsych.data.addDataToLastTrial({ blur_count: blurCount, fullscreen_exit_count: fullscreenExitCount });
        },
        on_interaction_data_update: data => {
            if (!C.PAUSE_ON_BLUR || bot) return;
            if (data.event === 'blur' && !experimentEnded) {
                blurCount++;
                jsPsych.pauseExperiment();
                alert(SESSION.T.common.PAUSE_ALERT);
            }
            if (data.event === 'focus' && !experimentEnded) jsPsych.resumeExperiment();
        },
    });
    window.jsPsych = jsPsych;   // the Pavlovia plugin uses the global name 'jsPsych'
    document.addEventListener('fullscreenchange', () => {
        if (!document.fullscreenElement && !experimentEnded) fullscreenExitCount++;
    });

    const subjectId = url.get('PROLIFIC_PID') || (bot ? 'bot' : short ? 'demo' : 'not_provided');
    Object.assign(SESSION, {
        day, lang, T: lang === 'he' ? TEXTS_HE : TEXTS_EN, bot, short, jsPsych,
        on_pavlovia: onPavlovia, subject_id: subjectId,
        // counterbalancing from the character code of one ID character (CONFIG.ID_CHAR_INDEX; lab: numeric subject ID)
        id_code: subjectId.charCodeAt(C.ID_CHAR_INDEX < 0 ? subjectId.length + C.ID_CHAR_INDEX : C.ID_CHAR_INDEX),
        stopped: false,                 // '' / 'calibration_cap' / 'quiz_failed_<task>'
        bot_quiz_wrong: testHook === 'quiz_fail',
    });
    SESSION.gold_side = ((SESSION.id_code % 2 === 0) === C.GOLD_LEFT_FOR_EVEN_IDS) ? 'left' : 'right';
    document.documentElement.setAttribute('lang', lang);
    const T = SESSION.T;

    const ua = navigator.userAgent || '';
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|Tablet/i.test(ua)
                  || ((navigator.maxTouchPoints > 1) && (window.screen.width < 1024));
    jsPsych.data.addProperties({
        subject_id: subjectId, study_id: url.get('STUDY_ID') || 'not_provided',
        session_id: url.get('SESSION_ID') || 'not_provided', day: day, language: lang,
        experiment: C.EXPERIMENT_NAME, run_mode: bot ? (short ? 'bot' : 'bot_full') : (short ? 'short_demo' : 'real'),
        device_type: isMobile ? 'mobile_or_tablet' : 'desktop', gold_side: SESSION.gold_side, id_code: SESSION.id_code,
        user_agent: ua, screen_width: window.screen.width, screen_height: window.screen.height,
        device_pixel_ratio: window.devicePixelRatio || 1,
        session_start: new Date().toISOString(),
    });

    // ── timeline ─────────────────────────────────────────────────────────────
    const timeline = [];
    if (onPavlovia) timeline.push({ type: jsPsychPavlovia, command: 'init' });

    if (C.BLOCK_MOBILE && isMobile) {
        timeline.push({
            type: jsPsychHtmlButtonResponse,
            stimulus: pageHtml(T.common.MOBILE_TITLE, para(T.common.MOBILE_TEXT)),
            choices: [T.common.MOBILE_BUTTON],
            on_finish: () => jsPsych.endExperiment('Participant was on a mobile/tablet device.'),
        });
    }

    const images = [C.COIN_REWARD_IMAGE, C.COIN_NO_REWARD_IMAGE].concat(C.MASK_IMAGES)
        .concat(C.WM_COLORS.map(c => `stimuli/squares/${c}.png`))
        .concat(['example1', 'example2', 'example3', 'fixation', 'keyboard'].map(e => `stimuli/examples/${e}.png`));
    timeline.push({ type: jsPsychPreload, images: images });
    timeline.push({ type: jsPsychCallFunction, async: true,
                    func: done => { DISPLAY.loadAssets().then(() => done()).catch(e => { console.error(e); done(); }); } });

    if (C.ENABLE_CAPTCHA && onPavlovia && !bot) {
        timeline.push({
            type: jsPsychHtmlKeyboardResponse,
            stimulus: `<div class="instr-page" dir="${T.dir}"><p>${T.common.CAPTCHA}</p><div id="recaptcha"></div><br>`
                    + `<button id="captcha-submit" class="jspsych-btn" type="button">${T.common.CAPTCHA_SUBMIT}</button></div>`,
            choices: 'NO_KEYS',
            data: { screen: 'captcha' },
            on_load: () => {
                if (typeof grecaptcha !== 'undefined') grecaptcha.render('recaptcha', { sitekey: C.RECAPTCHA_SITE_KEY });
                else console.error('reCAPTCHA script not loaded.');
                document.getElementById('captcha-submit').addEventListener('click', () => {
                    if (typeof grecaptcha === 'undefined' || grecaptcha.getResponse().length > 0) jsPsych.finishTrial();
                    else alert(T.common.CAPTCHA_ALERT);
                });
            },
        });
    }

    if (!bot) {
        timeline.push({
            type: jsPsychFullscreen, fullscreen_mode: true,
            message: pageHtml('', para(T.common.FULLSCREEN)),
            button_label: T.common.FULLSCREEN_BUTTON,
            data: { screen: 'fullscreen' },
        });
    }
    // refresh rate (after fullscreen, so it is measured on the screen used)
    timeline.push({
        type: jsPsychCallFunction, async: true,
        func: done => {
            jsPsych.getDisplayElement().innerHTML = pageHtml('', para(T.common.REFRESH_MEASURING));
            setTimeout(() => DISPLAY.measureRefresh(C.REFRESH_MEASURE_FRAMES).then(r => {
                jsPsych.data.addProperties({ refresh_hz: r.hz, frame_ms: r.frame_ms, frame_sd_ms: r.sd_ms,
                                             low_refresh_flag: r.hz < C.MIN_REFRESH_HZ_WARNING ? 1 : 0,
                                             window_width: window.innerWidth, window_height: window.innerHeight });
                console.log('Refresh rate', r);
                done();
            }), 500);
        },
        data: { screen: 'refresh_measurement' },
        on_finish: () => { experimentEnded = false; },
    });

    timeline.push(messageScreen(T.common[day === 1 ? 'WELCOME_DAY1' : 'WELCOME_DAY2'] + '\n\n' + T.common.WELCOME_CONTINUE,
                                { screen: 'welcome' }));

    // a task runs only if nothing stopped the session before it (quiz failed / calibration did not converge)
    if (day === 1) {
        timeline.push(unlessStopped(wmTimeline()));
        timeline.push(unlessStopped(banditTimeline(1)));
    } else {
        timeline.push(unlessStopped(calibrationTimeline()));
        timeline.push(unlessStopped(banditTimeline(2)));
    }
    timeline.push(unlessStopped(questionnairesTimeline()));

    // end
    timeline.push(callFunction(() => {
        experimentEnded = true;
        jsPsych.data.addProperties({ session_end: new Date().toISOString(), stopped: SESSION.stopped || '' });
    }));
    timeline.push({ timeline: [messageScreen(T.common.DAY_END, { screen: 'day_end' })],
                    conditional_function: () => !SESSION.stopped });
    // calibration did not converge: 'an error occurred ... you will be paid' (quiz failures have their own screen)
    timeline.push({ timeline: [withBot({
        type: jsPsychHtmlButtonResponse, stimulus: () => pageHtml('', para(T.common.CALIB_ERROR)),
        choices: [T.common.DAY_STOPPED_BUTTON], data: { screen: 'day_stopped' },
    }, () => BOT.click('#jspsych-html-button-response-button-0'))], conditional_function: () => SESSION.stopped === 'calibration_cap' });
    if (!bot) timeline.push({ type: jsPsychFullscreen, fullscreen_mode: false });

    const fileId = `${subjectId}_day${day}`;
    // quiz failed -> screened-out code; completed or calibration error -> normal completion code (paid)
    const completionCode = () => (/^quiz_failed/.test(SESSION.stopped || '') ? C.SCREENED_OUT_CODE : C.COMPLETION_CODE[day]);
    function finalPage() {
        const code = completionCode();
        window.__completionCode = code;   // read by tests/e2e_bot.js
        const dir = T.dir;
        if (!onPavlovia || bot || short || /^XXXX/.test(code)) {
            document.body.innerHTML = `<div class="end-page" dir="${dir}">${para(T.common.THANK_YOU_END)}</div>`;
            return;
        }
        const link = 'https://app.prolific.com/submissions/complete?cc=' + code;
        document.body.innerHTML = `<div class="end-page" dir="${dir}">${para(T.common.REDIRECT)}`
            + `<p>${T.common.REDIRECT_LINK} <a href="${link}">${link}</a></p></div>`;
        setTimeout(() => { window.location.href = link; }, 4000);
    }
    if (onPavlovia) {
        timeline.push({
            type: jsPsychPavlovia, command: 'finish', participantId: fileId,
            completedCallback: () => {},      // default shows an alert; the end page is shown in on_finish
            on_finish: finalPage,
        });
    } else {
        // local run: offer the CSV for download (bot and demo runs too), then the end page
        timeline.push(callFunction(() => {
            const stamp = new Date().toISOString().replace(/[:.]/g, '-');
            window.__experimentCsv = jsPsych.data.get().csv();
            if (!bot) jsPsych.data.get().localSave('csv', `${C.EXPERIMENT_NAME}_${fileId}_${stamp}.csv`);
            window.__experimentDone = true;
            finalPage();
        }));
    }

    jsPsych.run(timeline);
})();
