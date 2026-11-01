// ─── plugin-casino-trial.js ───────────────────────────────────────────────────
// jsPsych plugin: ONE casino trial, drawn on a canvas with frame-counted timing.
// Used by both the bandit and the STEP calibration, so the coin is shown in exactly
// the same setting (as CasinoScene in the lab version); only the opacity differs.
//
// mode 'bandit':        empty arms (WAIT_INITIAL) -> offer (2 coloured + 2 grey circles)
//                       -> choice (s/f/h/k, max CHOICE_TIME_LIMIT)
//                       -> miss: 'too late' message | grey arm: 'unavailable' message (penalty)
//                       -> valid: empty arms (WAIT_POST_CHOICE) -> fwd mask -> coin -> bwd mask -> empty arms
// mode 'feedback_only': empty arms (WAIT_POST_CHOICE) -> fwd mask -> coin -> bwd mask -> empty arms
//                       (calibration trial: no arm choice)
// probe = true:         after the feedback, PAS (keys 0-3) and the gold/black coin choice (arrows)
//
// All t_* data are requestAnimationFrame timestamps (ms since page load) of the first frame
// after each screen was drawn; *_measured are differences between them.

var jsPsychCasinoTrial = (function (jspsych) {
    'use strict';

    const P = jspsych.ParameterType;
    const info = {
        name: 'casino-trial',
        parameters: {
            mode: { type: P.STRING, default: 'bandit' },
            offered_arms: { type: P.COMPLEX, default: [] },
            colours: { type: P.COMPLEX, default: [] },
            probs: { type: P.COMPLEX, default: [] },
            outcome_draw: { type: P.FLOAT, default: null },
            outcome: { type: P.STRING, default: null },          // feedback_only: 'reward' | 'no_reward'
            opacity: { type: P.FLOAT, default: 1.0 },
            coin_duration: { type: P.INT, default: 33 },
            probe: { type: P.BOOL, default: false },
            gold_side: { type: P.STRING, default: 'left' },
            texts: { type: P.COMPLEX, default: {} },             // too_late, unavailable, pas_*, choice_*
            rtl: { type: P.BOOL, default: false },
            bot: { type: P.BOOL, default: false },
        },
    };

    const ARROWS = ['ArrowLeft', 'ArrowRight'];
    const PAS_CODES = { Digit0: 0, Digit1: 1, Digit2: 2, Digit3: 3, Numpad0: 0, Numpad1: 1, Numpad2: 2, Numpad3: 3 };

    class CasinoTrialPlugin {
        constructor(jsPsych) { this.jsPsych = jsPsych; }

        trial(display_element, trial) {
            this.run(display_element, trial).catch(err => {
                console.error(err);
                this.jsPsych.finishTrial({ error: String(err) });
            });
        }

        async run(display_element, trial) {
            const C = CONFIG, D = DISPLAY;
            const F = ms => D.framesFor(ms);
            display_element.innerHTML = '';
            const { canvas, ctx, w, h } = D.makeCanvas(display_element);
            document.body.classList.add('casino-running');
            const draw = state => () => D.drawScene(ctx, w, h, state, { rtl: trial.rtl });
            const bg = draw({ circles: null });
            const offerState = { circles: { offered: trial.offered_arms, colours: trial.colours } };
            const row = {
                task_mode: trial.mode, coin_opacity: trial.opacity, coin_duration_planned: trial.coin_duration,
                frame_ms: D.refresh.frame_ms, probe: trial.probe ? 1 : 0, gold_side: trial.gold_side,
                pas: null, pas_rt: null, coin_chosen: null, twoafc_rt: null, twoafc_correct: null,
            };
            let outcome = trial.outcome;

            if (trial.mode === 'bandit') {
                const colourOf = {};
                trial.offered_arms.forEach((a, i) => { colourOf[a] = trial.colours[i]; });
                Object.assign(row, {
                    offered_arms: trial.offered_arms.join(';'),
                    colour_arm0: colourOf[0] || '', colour_arm1: colourOf[1] || '',
                    colour_arm2: colourOf[2] || '', colour_arm3: colourOf[3] || '',
                    p_arm0: trial.probs[0], p_arm1: trial.probs[1], p_arm2: trial.probs[2], p_arm3: trial.probs[3],
                    outcome_draw: trial.outcome_draw,
                    choice_key: null, choice_arm: null, choice_colour: null, rt: null,
                    missed: 0, unavailable_choice: 0, reward: null,
                });

                // ITI, then the offer; listen from the moment the offer is drawn
                const iti = await D.runSequence([{ name: 't_iti', draw: bg, frames: F(C.WAIT_INITIAL) }]);
                row.t_iti = iti.onsets.t_iti;
                const choiceP = this.waitKey(C.ARM_KEYS, C.CHOICE_TIME_LIMIT, trial.bot ? this.botArm(trial) : null);
                const offer = await D.runSequence([{ name: 't_offer', draw: draw(offerState), frames: 1 }]);
                row.t_offer = offer.onsets.t_offer;
                const resp = await choiceP;
                if (resp === null) {                                  // miss
                    row.missed = 1;
                    const s = await D.runSequence([{ name: 't_too_late_msg', draw: draw({ circles: null, message: trial.texts.too_late }), frames: F(C.INVALID_MSG_DURATION) },
                                                   { name: 't_end', draw: bg, frames: 1 }]);
                    row.t_too_late_msg = s.onsets.t_too_late_msg;
                    return this.finish(display_element, row);
                }
                const arm = C.ARM_KEYS.indexOf(resp.code);
                row.choice_key = C.ARM_KEY_NAMES[arm];
                row.choice_arm = arm;
                row.rt = resp.time - row.t_offer;
                if (!trial.offered_arms.includes(arm)) {             // grey arm: penalty, no outcome
                    row.unavailable_choice = 1;
                    const s = await D.runSequence([{ name: 't_unavailable_msg', draw: draw({ circles: null, message: trial.texts.unavailable }), frames: F(C.UNAVAILABLE_CHOICE_DURATION) },
                                                   { name: 't_end', draw: bg, frames: 1 }]);
                    row.t_unavailable_msg = s.onsets.t_unavailable_msg;
                    return this.finish(display_element, row);
                }
                const rewarded = trial.outcome_draw < trial.probs[arm];
                outcome = rewarded ? 'reward' : 'no_reward';
                row.choice_colour = colourOf[arm];
                row.reward = rewarded ? 1 : 0;
            }

            // feedback: empty arms -> forward mask -> coin -> backward mask -> empty arms
            const nMasks = C.MASK_IMAGES.length;
            const fwdIdx = Math.floor(Math.random() * nMasks), bwdIdx = Math.floor(Math.random() * nMasks);
            const coinFrames = F(trial.coin_duration), bwdFrames = F(C.FEEDBACK_BWD_MASK_DURATION);
            const seq = [
                { name: 't_post_choice', draw: bg, frames: F(C.WAIT_POST_CHOICE) },
                { name: 't_fwd_mask', draw: draw({ circles: null, mask: fwdIdx }), frames: F(C.FEEDBACK_FWD_MASK_DURATION) },
                { name: 't_coin', draw: draw({ circles: null, coin: { outcome: outcome, opacity: trial.opacity } }), frames: coinFrames },
                { name: 't_bwd_mask', draw: draw({ circles: null, mask: bwdIdx }), frames: bwdFrames },
                { name: 't_feedback_end', draw: bg, frames: 1 },
            ];
            const fb = await D.runSequence(seq);
            const t = fb.onsets;
            Object.assign(row, {
                coin_shown: outcome, t_post_choice: t.t_post_choice, t_fwd_mask: t.t_fwd_mask, t_coin: t.t_coin,
                t_bwd_mask: t.t_bwd_mask, t_feedback_end: t.t_feedback_end,
                fwd_mask_idx: fwdIdx, bwd_mask_idx: bwdIdx, coin_frames: coinFrames, bwd_mask_frames: bwdFrames,
                coin_duration_measured: t.t_bwd_mask - t.t_coin,
                bwd_mask_duration_measured: t.t_feedback_end - t.t_bwd_mask,
                feedback_long_frames: fb.n_long_frames,
            });

            if (trial.probe) {
                canvas.style.visibility = 'hidden';
                const pas = await this.pas(display_element, trial);
                const choice = await this.coinChoice(display_element, trial);
                Object.assign(row, { pas: pas.value, pas_rt: pas.rt, seen: pas.value > 0 ? 1 : 0,
                                     coin_chosen: choice.coin, twoafc_rt: choice.rt,
                                     twoafc_correct: choice.coin === outcome ? 1 : 0 });
            }
            return this.finish(display_element, row);
        }

        finish(display_element, row) {
            document.body.classList.remove('casino-running');
            display_element.innerHTML = '';
            this.jsPsych.finishTrial(row);
        }

        // Resolves with {code, time} (time = event timestamp, same clock as rAF) or null after timeout.
        // codes: KeyboardEvent.code values. botAnswer: {code, delay} or null (a bot "presses" it).
        waitKey(codes, timeout, botAnswer) {
            return new Promise(resolve => {
                let timer = null, botTimer = null;
                const done = val => {
                    document.removeEventListener('keydown', onKey, true);
                    clearTimeout(timer);
                    clearTimeout(botTimer);
                    resolve(val);
                };
                const onKey = e => {
                    if (codes.includes(e.code)) {
                        e.preventDefault();
                        done({ code: e.code, time: e.timeStamp });
                    }
                };
                document.addEventListener('keydown', onKey, true);
                if (timeout) timer = setTimeout(() => done(null), timeout);
                if (botAnswer && botAnswer.code) {
                    botTimer = setTimeout(() => done({ code: botAnswer.code, time: performance.now() }), botAnswer.delay);
                }
            });
        }

        botArm(trial) {
            const r = Math.random();
            if (r < 0.05) return { code: null };                                  // miss
            const arms = r < 0.12 ? [0, 1, 2, 3].filter(a => !trial.offered_arms.includes(a)) : trial.offered_arms;
            const arm = arms[Math.floor(Math.random() * arms.length)];
            return { code: CONFIG.ARM_KEYS[arm], delay: 200 + Math.random() * 400 };
        }

        overlay(display_element, html, rtl) {
            let div = display_element.querySelector('.casino-overlay');
            if (!div) {
                div = document.createElement('div');
                div.className = 'casino-overlay';
                display_element.appendChild(div);
            }
            div.setAttribute('dir', rtl ? 'rtl' : 'ltr');
            div.innerHTML = html;
            return div;
        }

        async pas(display_element, trial) {
            const T = trial.texts;
            const opts = T.pas_options.map((o, i) => `<div class="pas-option"><span class="pas-num">${i}</span> ${o}</div>`).join('');
            this.overlay(display_element, `<div class="overlay-question">${T.pas_question}</div>
                <div class="pas-options">${opts}</div><div class="overlay-footer">${T.pas_footer}</div>`, trial.rtl);
            const t0 = performance.now();
            const bot = trial.bot ? { code: 'Digit0', delay: CONFIG.BOT_RESPONSE_DELAY } : null;
            const resp = await this.waitKey(Object.keys(PAS_CODES), null, bot);
            return { value: PAS_CODES[resp.code], rt: resp.time - t0 };
        }

        async coinChoice(display_element, trial) {
            const T = trial.texts;
            const gold = `<img src="${CONFIG.COIN_REWARD_IMAGE}" style="width:${CONFIG.CHOICE_COIN_SIZE}px;height:${CONFIG.CHOICE_COIN_SIZE}px;">`;
            const black = `<img src="${CONFIG.COIN_NO_REWARD_IMAGE}" style="width:${CONFIG.CHOICE_COIN_SIZE}px;height:${CONFIG.CHOICE_COIN_SIZE}px;">`;
            const [left, right] = trial.gold_side === 'left' ? [gold, black] : [black, gold];
            this.overlay(display_element, `<div class="overlay-question">${T.choice_question}</div>
                <div class="choice-coins" dir="ltr" style="gap:${2 * CONFIG.CHOICE_COIN_X - CONFIG.CHOICE_COIN_SIZE}px">${left}${right}</div>
                <div class="overlay-footer">${T.choice_footer}</div>`, trial.rtl);
            const t0 = performance.now();
            const bot = trial.bot ? { code: ARROWS[Math.floor(Math.random() * 2)], delay: CONFIG.BOT_RESPONSE_DELAY } : null;
            const resp = await this.waitKey(ARROWS, null, bot);
            const side = resp.code === 'ArrowLeft' ? 'left' : 'right';
            return { coin: side === trial.gold_side ? 'reward' : 'no_reward', rt: resp.time - t0, side: side };
        }
    }
    CasinoTrialPlugin.info = info;
    return CasinoTrialPlugin;
})(jsPsychModule);
