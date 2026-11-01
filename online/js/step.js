// ─── step.js ──────────────────────────────────────────────────────────────────
// STEP staircase (Elbaz, Yaron & Mudrik, 2025) - pure logic, no jsPsych.
// Line-by-line port of ../tasks/calibration/step.py (see its docstring for the rules and
// the two deliberate deviations from Eden Elbaz's original code). Verified against the
// Python implementation by tests/test_step.js.

(function (root) {
    'use strict';

    const STEP_DECIMALS = 10;

    function roundTo(x, decimals) {
        const f = Math.pow(10, decimals);
        return Math.round(x * f) / f;
    }

    // log of the binomial coefficient, exact enough for n <= a few thousand
    function logChoose(n, k) {
        let s = 0;
        for (let i = 1; i <= k; i++) s += Math.log(n - k + i) - Math.log(i);
        return s;
    }

    // one-tailed exact binomial test, H1: p > 0.5  ->  P(X >= k | n, 0.5)
    // (= scipy.stats.binomtest(k, n, 0.5, alternative='greater').pvalue)
    function binomGreaterP(k, n) {
        if (k <= 0) return 1.0;
        let p = 0;
        const logHalfN = n * Math.log(0.5);
        for (let i = k; i <= n; i++) p += Math.exp(logChoose(n, i) + logHalfN);
        return Math.min(1.0, p);
    }

    const DEFAULT_PARAMS = {
        start_intensity: 1.0, max_intensity: 1.0, min_intensity: 0.1,
        initial_step: 0.2, step_decrease: 0.05, min_step: 0.05,
        cwir_stop: 50, min_trials: 50, max_trials: 300, alpha: 0.05,
    };

    class StepStaircase {
        constructor(params) {
            this.p = Object.assign({}, DEFAULT_PARAMS, params || {});
            this.intensity = this.p.start_intensity;   // intensity to show on the NEXT trial
            this.boundary = this.p.max_intensity;
            this.trial = 0;
            this.cwir = 0;
            this.history = [];                         // [intensity, correct, seen]
            this.sequences = [];                       // [mean intensity, weight]
            this._runLen = 0;
            this._runWeight = 0;
            this._runIntensities = [];
        }

        update(correct, seen) {
            const p = this.p;
            correct = correct ? 1 : 0;
            seen = seen ? 1 : 0;
            const x = this.intensity;
            this.trial += 1;
            const t = this.trial;
            this.history.push([x, correct, seen]);
            const log = { step_trial: t, intensity: x, correct: correct, seen: seen,
                          boundary_before: this.boundary, cwir_before: this.cwir };

            // a. upper boundary
            const inRange = this.history.filter(h => x <= h[0] && h[0] <= this.boundary);
            const n = inRange.length;
            const nCorrect = inRange.reduce((s, h) => s + h[1], 0);
            const seenRatio = inRange.reduce((s, h) => s + h[2], 0) / n;
            const pValue = binomGreaterP(nCorrect, n);
            const alpha = p.alpha / (1 + this.cwir);
            const boundaryUpdated = pValue <= alpha;
            if (boundaryUpdated) this.boundary = (1 - seenRatio) * this.boundary + seenRatio * x;
            Object.assign(log, { boundary_n_trials: n, boundary_n_correct: nCorrect,
                                 boundary_seen_ratio: seenRatio, boundary_p: pValue,
                                 boundary_alpha: alpha, boundary_updated: boundaryUpdated ? 1 : 0,
                                 boundary_after: this.boundary });

            // b. CWIR and incorrect sequences
            if (correct) {
                this._closeRun();
            } else {
                this._runLen += 1;
                this._runWeight += this._runLen;
                this._runIntensities.push(x);
                this.cwir += this._runLen;
            }

            // c. next intensity
            const step = roundTo(Math.max(p.min_step, p.initial_step - p.step_decrease * (t - 1)), STEP_DECIMALS);
            const direction = correct ? -1 : 1;
            const seenRule = (!correct) && seen && step > roundTo(p.min_step, STEP_DECIMALS);
            const applied = seenRule ? 0.0 : direction * step;
            this.intensity = Math.min(this.boundary, Math.max(p.min_intensity, x + applied));

            Object.assign(log, { step: step, direction: direction, seen_rule_applied: seenRule ? 1 : 0,
                                 applied_step: applied, next_intensity: this.intensity,
                                 cwir_after: this.cwir, incorrect_run_length: this._runLen,
                                 done: this.done ? 1 : 0, cap_reached: this.capReached ? 1 : 0 });
            return log;
        }

        _closeRun() {
            if (this._runLen) {
                const mean = this._runIntensities.reduce((a, b) => a + b, 0) / this._runIntensities.length;
                this.sequences.push([mean, this._runWeight]);
            }
            this._runLen = 0;
            this._runWeight = 0;
            this._runIntensities = [];
        }

        get converged() { return this.cwir >= this.p.cwir_stop && this.trial >= this.p.min_trials; }
        get capReached() { return this.trial >= this.p.max_trials && !this.converged; }
        get done() { return this.converged || this.capReached; }

        // CWIR-weighted mean intensity of all incorrect sequences (an open one counts once); null if none
        threshold() {
            const seqs = this.sequences.slice();
            if (this._runLen) {
                const mean = this._runIntensities.reduce((a, b) => a + b, 0) / this._runIntensities.length;
                seqs.push([mean, this._runWeight]);
            }
            const total = seqs.reduce((s, q) => s + q[1], 0);
            if (total === 0) return null;
            return seqs.reduce((s, q) => s + q[0] * q[1], 0) / total;
        }
    }

    const api = { StepStaircase, binomGreaterP, DEFAULT_PARAMS };
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    else Object.assign(root, api);
})(typeof window !== 'undefined' ? window : this);
