// Replays the Python reference runs (step_reference.json) through js/step.js.
// Run: node online/tests/test_step.js
const assert = require('assert');
const path = require('path');
const { StepStaircase, binomGreaterP } = require(path.join(__dirname, '..', 'js', 'step.js'));
const runs = require(path.join(__dirname, 'step_reference.json'));

const close = (a, b, tol = 1e-9) => (a === null && b === null) || Math.abs(a - b) <= tol * Math.max(1, Math.abs(b));

// binomial test sanity values (scipy.stats.binomtest(k, n, 0.5, alternative='greater'))
assert(close(binomGreaterP(5, 5), 0.03125));
assert(close(binomGreaterP(0, 7), 1.0));
assert(close(binomGreaterP(60, 100), 0.028443966820490392, 1e-9));

let nTrials = 0;
runs.forEach((run, r) => {
    const s = new StepStaircase(run.params);
    run.responses.forEach(([correct, seen], i) => {
        const log = s.update(correct, seen);
        const ref = run.logs[i];
        for (const key of Object.keys(ref)) {
            const a = log[key], b = ref[key];
            if (typeof b === 'number') assert(close(a, b, 1e-7), `run ${r} trial ${i + 1} ${key}: js ${a} py ${b}`);
            else assert.strictEqual(a, b, `run ${r} trial ${i + 1} ${key}`);
        }
        nTrials++;
    });
    assert(s.done, `run ${r} should be done`);
    assert.strictEqual(s.trial, run.trials);
    assert.strictEqual(s.capReached, run.cap_reached);
    assert(close(s.threshold(), run.threshold), `run ${r} threshold js ${s.threshold()} py ${run.threshold}`);
});
console.log(`test_step.js: OK - ${runs.length} runs, ${nTrials} trials identical to the Python STEP`);
