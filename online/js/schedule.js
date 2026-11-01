// ─── schedule.js ──────────────────────────────────────────────────────────────
// Seeded random numbers and the bandit trial schedule - pure logic, no jsPsych.
// Port of ../tasks/bandit/schedule.py ('live' Gaussian random walk). The random number
// generator differs from Python's (mulberry32 here), so the same seed gives a different
// sequence than in PsychoPy; within the online version a seed regenerates a session exactly.

(function (root) {
    'use strict';

    // mulberry32: small, fast, good-enough seeded PRNG -> float in [0, 1)
    function makeRng(seed) {
        let a = seed >>> 0;
        const rng = function () {
            a = (a + 0x6D2B79F5) >>> 0;
            let t = a;
            t = Math.imul(t ^ (t >>> 15), t | 1);
            t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
        rng.int = n => Math.floor(rng() * n);                       // 0 .. n-1
        rng.gauss = (mu, sd) => {                                    // Box-Muller
            let u = 0;
            while (u === 0) u = rng();
            const v = rng();
            return mu + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
        };
        rng.shuffle = arr => {                                       // returns a shuffled copy
            const a2 = arr.slice();
            for (let i = a2.length - 1; i > 0; i--) {
                const j = rng.int(i + 1);
                [a2[i], a2[j]] = [a2[j], a2[i]];
            }
            return a2;
        };
        rng.sample = (arr, k) => rng.shuffle(arr).slice(0, k);
        rng.choice = arr => arr[rng.int(arr.length)];
        return rng;
    }

    function makeSeed(fixed) {
        if (fixed !== null && fixed !== undefined) return fixed;
        if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
            return crypto.getRandomValues(new Uint32Array(1))[0] % 2147483648;
        }
        return Math.floor(Math.random() * 2147483648);
    }

    // Every arm starts at initial and takes a Gaussian step (clipped) after each trial.
    function liveWalk(rng, nTrials, nArms, cfg) {
        let probs = new Array(nArms).fill(cfg.WALK_INITIAL_PROB);
        const walk = [];
        for (let t = 0; t < nTrials; t++) {
            walk.push(probs.slice());
            probs = probs.map(p => Math.min(cfg.WALK_MAX_PROB,
                Math.max(cfg.WALK_MIN_PROB, p + rng.gauss(0, cfg.WALK_STEP_SD))));
        }
        return walk;
    }

    // List of trials: offered_arms (sorted), colours (names, per offered arm), probs (all arms), outcome_draw.
    function makeSchedule(nTrials, seed, cfg) {
        const nArms = cfg.ARM_X_POSITIONS.length;
        const rng = makeRng(seed);
        const walk = liveWalk(makeRng(rng.int(2147483647)), nTrials, nArms, cfg);
        const arms = [...Array(nArms).keys()];
        const schedule = [];
        for (let t = 0; t < nTrials; t++) {
            const offered = rng.sample(arms, cfg.N_ACTIVE_ARMS).sort((a, b) => a - b);
            const colours = rng.sample(cfg.CIRCLE_COLOR_NAMES, cfg.N_ACTIVE_ARMS);
            schedule.push({ offered_arms: offered, colours: colours, probs: walk[t], outcome_draw: rng() });
        }
        return schedule;
    }

    function isRewarded(trial, arm) {
        return trial.outcome_draw < trial.probs[arm];
    }

    const api = { makeRng, makeSeed, liveWalk, makeSchedule, isRewarded };
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    else Object.assign(root, api);
})(typeof window !== 'undefined' ? window : this);
