// End-to-end check: runs each day with the automatic participant (?bot=1) in headless Chromium,
// then checks the data. Needs Playwright + Chromium.
// Run from the online/ folder:   node tests/e2e_bot.js            (both days, English + Hebrew)
// The CSVs are written to tests/output/ (git-ignored).
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(__dirname, 'output');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.json': 'application/json' };

function serve() {
    return new Promise(resolve => {
        const server = http.createServer((req, res) => {
            const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
            fs.readFile(p.endsWith('/') ? p + 'index.html' : p, (err, buf) => {
                if (err) { res.writeHead(404); res.end(); return; }
                res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
                res.end(buf);
            });
        }).listen(0, () => resolve(server));
    });
}

function parseCsv(text) {
    const rows = [];
    let row = [], field = '', q = false;
    for (let i = 0; i < text.length; i++) {
        const c = text[i];
        if (q) {
            if (c === '"' && text[i + 1] === '"') { field += '"'; i++; } else if (c === '"') q = false; else field += c;
        } else if (c === '"') q = true;
        else if (c === ',') { row.push(field); field = ''; }
        else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(field); rows.push(row); row = []; field = ''; }
        else field += c;
    }
    if (field || row.length) { row.push(field); rows.push(row); }
    const head = rows.shift();
    // jsPsych writes missing values as "null"; treat them as empty cells
    return rows.filter(r => r.length === head.length).map(r => Object.fromEntries(head.map((h, i) => [h, r[i] === 'null' ? '' : r[i]])));
}

function check(cond, msg) {
    if (!cond) throw new Error('CHECK FAILED: ' + msg);
}

async function runDay(browser, base, day, lang) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error' && !/recaptcha|ERR_|Failed to load resource/i.test(m.text())) errors.push(m.text()); });
    const t0 = Date.now();
    await page.goto(`${base}/index.html?day=${day}&lang=${lang}&bot=1`);
    await page.waitForFunction(() => window.__experimentDone === true, null, { timeout: 15 * 60 * 1000, polling: 500 });
    const csv = await page.evaluate(() => window.__experimentCsv);
    await page.close();
    fs.mkdirSync(OUT, { recursive: true });
    const file = path.join(OUT, `bot_day${day}_${lang}.csv`);
    fs.writeFileSync(file, csv);
    const rows = parseCsv(csv);
    check(errors.length === 0, `page errors: ${errors.join(' | ')}`);
    const casino = rows.filter(r => r.trial_type === 'casino-trial');
    const valid = casino.filter(r => r.coin_shown);
    const coin = valid.map(r => +r.coin_duration_measured);
    const summary = { day, lang, seconds: Math.round((Date.now() - t0) / 1000), rows: rows.length, casino_trials: casino.length,
                      coin_ms: coin.length ? `${Math.min(...coin).toFixed(1)}-${Math.max(...coin).toFixed(1)}` : '-',
                      refresh_hz: rows[0] && (+rows[0].refresh_hz).toFixed(1), file: path.relative(ROOT, file) };

    const C = { BANDIT_N_BLOCKS: 2, BANDIT_TRIALS_PER_BLOCK: 3, BANDIT_N_PRACTICE: 2, WM_N_TRIALS: 6 };
    const bandit = casino.filter(r => r.task === 'bandit');
    check(bandit.filter(r => r.phase === 'practice').length === C.BANDIT_N_PRACTICE, 'practice trial count');
    check(bandit.filter(r => r.phase === 'main').length === C.BANDIT_N_BLOCKS * C.BANDIT_TRIALS_PER_BLOCK, 'main trial count');
    bandit.forEach(r => {
        const n = (+r.missed) + (+r.unavailable_choice) + (r.reward !== '' ? 1 : 0);
        check(n === 1, `exactly one of missed/unavailable/reward per trial (trial ${r.trial})`);
        if (r.reward !== '') check((+r.outcome_draw < +r['p_arm' + r.choice_arm]) === (r.reward === '1'), 'reward follows the schedule');
    });
    // coin duration = planned frames, except on trials flagged as having long (dropped) frames
    const clean = valid.filter(r => r.feedback_long_frames === '0');
    clean.forEach(r => check(Math.abs(+r.coin_duration_measured - (+r.coin_frames) * (+r.frame_ms)) < 0.5 * (+r.frame_ms),
                             `coin duration ${r.coin_duration_measured} vs ${r.coin_frames} frames`));
    summary.trials_with_dropped_frames = valid.length - clean.length;
    if (day === 1) {
        const wm = rows.filter(r => r.screen === 'wm_test' && r.phase === 'exp');
        check(wm.length === C.WM_N_TRIALS, 'WM trial count');
        check(rows.some(r => r.event === 'wm_capacity' && r.K_mean !== ''), 'WM capacity row');
        check(bandit.every(r => +r.coin_opacity === 1), 'day 1 opacity = 1');
    } else {
        const cal = casino.filter(r => r.task === 'calibration');
        check(cal.length >= 2 * 3, 'calibration trials');
        check(cal.every(r => r.pas !== '' && r.coin_chosen !== '' && r.step_trial !== ''), 'calibration rows complete');
        const fin = rows.find(r => r.event === 'final_threshold');
        check(fin && fin.final_threshold !== '', 'final threshold');
        check(bandit.every(r => Math.abs(+r.coin_opacity - +fin.final_threshold) < 1e-9), 'day 2 bandit uses the calibrated opacity');
        summary.threshold = (+fin.final_threshold).toFixed(3);
        summary.calibration_trials = cal.length;
    }
    const imi = rows.find(r => r.event === 'imi_summary');
    check(imi && imi.failed_attention_checks === '0', 'IMI summary, bot passes attention checks');
    check(rows.filter(r => r.phase === 'imi' && r.trial_type === 'survey-likert').length === 36, '36 IMI items');
    console.log('OK', JSON.stringify(summary));
}

(async () => {
    const server = await serve();
    const base = `http://localhost:${server.address().port}`;
    const browser = await chromium.launch();
    const runs = process.argv.slice(2).length ? process.argv.slice(2).map(a => a.split(':')) : [['1', 'en'], ['2', 'en'], ['1', 'he'], ['2', 'he']];
    let failed = false;
    for (const [day, lang] of runs) {
        try { await runDay(browser, base, +day, lang); } catch (e) { failed = true; console.error(`day ${day} ${lang}:`, e.message); }
    }
    await browser.close();
    server.close();
    process.exit(failed ? 1 : 0);
})();
