// Checks tools/build_pavlovia.py: (1) each built project runs its own day whatever ?day= says,
// (2) rebuilding an existing clone keeps .git/ and data/. Run from online/: node tests/test_build.js
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');
const fs = require('fs'), http = require('http'), path = require('path'), os = require('os');

const SRC = path.join(__dirname, '..');
const OUT = fs.mkdtempSync(path.join(os.tmpdir(), 'pav-build-'));
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png' };
const check = (c, m) => { if (!c) throw new Error('CHECK FAILED: ' + m); };

(async () => {
    execFileSync('python3', [path.join(SRC, 'tools', 'build_pavlovia.py'), '--out', OUT]);
    const server = http.createServer((req, res) => {
        const p = path.join(OUT, decodeURIComponent(req.url.split('?')[0]));
        fs.readFile(p, (err, buf) => {
            if (err) { res.writeHead(404); res.end(); return; }
            res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
            res.end(buf);
        });
    }).listen(0);
    await new Promise(r => server.on('listening', r));
    const browser = await chromium.launch();
    for (const [built, urlDay] of [[1, 2], [2, 1]]) {
        const page = await browser.newPage();
        await page.goto(`http://localhost:${server.address().port}/subliminal-reward-pilot-day${built}/index.html?day=${urlDay}&bot=1`);
        await page.waitForFunction(() => typeof SESSION !== 'undefined' && SESSION.T, null, { timeout: 20000 });
        const day = await page.evaluate(() => SESSION.day);
        check(day === built, `project day${built} opened with ?day=${urlDay} runs day ${day}`);
        console.log(`OK project day${built} ignores ?day=${urlDay} (runs day ${day})`);
        await page.close();
    }
    await browser.close();
    server.close();

    // rebuild over an existing "clone": .git and data/ must survive, stale files must go
    const d1 = path.join(OUT, 'subliminal-reward-pilot-day1');
    fs.mkdirSync(path.join(d1, '.git'));
    fs.writeFileSync(path.join(d1, '.git', 'HEAD'), 'ref: refs/heads/master\n');
    fs.mkdirSync(path.join(d1, 'data'));
    fs.writeFileSync(path.join(d1, 'data', 'participant.csv'), 'keep me');
    fs.writeFileSync(path.join(d1, 'stale.txt'), 'old');
    execFileSync('python3', [path.join(SRC, 'tools', 'build_pavlovia.py'), '--out', OUT]);
    check(fs.readFileSync(path.join(d1, 'data', 'participant.csv'), 'utf8') === 'keep me', 'data/ kept');
    check(fs.existsSync(path.join(d1, '.git', 'HEAD')), '.git kept');
    check(!fs.existsSync(path.join(d1, 'stale.txt')), 'stale files removed');
    check(/FIXED_DAY = 1;/.test(fs.readFileSync(path.join(d1, 'js', 'day.js'), 'utf8')), 'day.js fixed to 1');
    console.log('OK rebuild keeps .git/ and data/, removes stale files');
    fs.rmSync(OUT, { recursive: true, force: true });
})().catch(e => { console.error(e.message); process.exit(1); });
