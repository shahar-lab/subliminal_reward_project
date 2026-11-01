// ─── display.js ───────────────────────────────────────────────────────────────
// Browser display helpers shared by the bandit and the calibration:
//   * image assets (loaded once)
//   * refresh-rate measurement
//   * the casino scene, drawn on a canvas  (THE one place the scene is drawn -
//     as common/scene.py in the lab version, the calibration uses exactly the same drawing)
//   * frame-counted presentation of a sequence of screens (requestAnimationFrame)

const DISPLAY = (function () {
    'use strict';

    // ── assets ───────────────────────────────────────────────────────────────
    const images = {};
    function loadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error('could not load ' + src));
            img.src = src;
        });
    }
    let assetsPromise = null;
    function loadAssets() {
        if (!assetsPromise) {
            const list = [['reward', CONFIG.COIN_REWARD_IMAGE], ['no_reward', CONFIG.COIN_NO_REWARD_IMAGE]]
                .concat(CONFIG.MASK_IMAGES.map((src, i) => ['mask' + i, src]));
            assetsPromise = Promise.all(list.map(([key, src]) => loadImage(src).then(img => { images[key] = img; })));
        }
        return assetsPromise;
    }

    // ── refresh rate ─────────────────────────────────────────────────────────
    const refresh = { frame_ms: 1000 / 60, hz: 60, measured: false, sd_ms: null };
    function measureRefresh(nFrames) {
        return new Promise(resolve => {
            const stamps = [];
            function tick(ts) {
                stamps.push(ts);
                if (stamps.length <= nFrames) requestAnimationFrame(tick);
                else {
                    const d = [];
                    for (let i = 1; i < stamps.length; i++) d.push(stamps[i] - stamps[i - 1]);
                    const sorted = d.slice().sort((a, b) => a - b);
                    const median = sorted[Math.floor(sorted.length / 2)];
                    const mean = d.reduce((a, b) => a + b, 0) / d.length;
                    const sd = Math.sqrt(d.reduce((a, b) => a + (b - mean) * (b - mean), 0) / d.length);
                    refresh.frame_ms = median;
                    refresh.hz = 1000 / median;
                    refresh.sd_ms = sd;
                    refresh.measured = true;
                    resolve(refresh);
                }
            }
            requestAnimationFrame(tick);
        });
    }
    function framesFor(ms) {
        return Math.max(1, Math.round(ms / refresh.frame_ms));
    }

    // ── canvas ───────────────────────────────────────────────────────────────
    // A full-window canvas; returns {canvas, ctx, w, h} with ctx in CSS pixels.
    function makeCanvas(parent) {
        const canvas = document.createElement('canvas');
        const dpr = window.devicePixelRatio || 1;
        const w = window.innerWidth, h = window.innerHeight;
        canvas.width = Math.round(w * dpr);
        canvas.height = Math.round(h * dpr);
        canvas.style.width = w + 'px';
        canvas.style.height = h + 'px';
        canvas.style.position = 'fixed';
        canvas.style.left = '0';
        canvas.style.top = '0';
        canvas.style.zIndex = '1';
        parent.appendChild(canvas);
        const ctx = canvas.getContext('2d');
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        return { canvas, ctx, w, h };
    }

    function colourHex(name) {
        const i = CONFIG.CIRCLE_COLOR_NAMES.indexOf(name);
        return i >= 0 ? CONFIG.CIRCLE_ACTIVE_COLORS[i] : name;
    }

    // Draw the casino scene.
    //   state.circles : null (no circles - "background" = empty arms) |
    //                   {offered: [arm indices], colours: [names]}  (others grey)
    //   state.coin    : null | {outcome: 'reward'|'no_reward', opacity}
    //   state.mask    : null | mask index
    //   state.message : null | text (red, between the reward box and the arms)
    // opts: {cx, cy, scale, clear (default true), rtl}
    function drawScene(ctx, w, h, state, opts) {
        opts = opts || {};
        const s = opts.scale || 1;
        const cx = opts.cx !== undefined ? opts.cx : w / 2;
        const cy = opts.cy !== undefined ? opts.cy : h / 2;
        const X = x => cx + x * s;
        const Y = y => cy - y * s;                     // config y is up
        if (opts.clear !== false) {
            ctx.globalAlpha = 1;
            ctx.fillStyle = CONFIG.BACKGROUND_COLOR;
            ctx.fillRect(0, 0, w, h);
        }
        ctx.globalAlpha = 1;
        // arms
        const a = CONFIG.ARM_SIZE * s;
        ctx.fillStyle = CONFIG.ARM_COLOR;
        CONFIG.ARM_X_POSITIONS.forEach(x => ctx.fillRect(X(x) - a / 2, Y(CONFIG.ARM_Y) - a / 2, a, a));
        // feedback box
        const b = CONFIG.FEEDBACK_BOX_SIZE * s;
        const [fx, fy] = CONFIG.FEEDBACK_POS;
        ctx.fillStyle = CONFIG.FEEDBACK_BOX_COLOR;
        ctx.fillRect(X(fx) - b / 2, Y(fy) - b / 2, b, b);
        // circles
        if (state.circles) {
            const colourOf = {};
            (state.circles.offered || []).forEach((arm, i) => { colourOf[arm] = colourHex(state.circles.colours[i]); });
            CONFIG.ARM_X_POSITIONS.forEach((x, arm) => {
                ctx.beginPath();
                ctx.arc(X(x), Y(CONFIG.ARM_Y), CONFIG.CIRCLE_RADIUS * s, 0, 2 * Math.PI);
                ctx.fillStyle = colourOf[arm] || CONFIG.CIRCLE_INACTIVE_COLOR;
                ctx.fill();
            });
        }
        // mask
        if (state.mask !== null && state.mask !== undefined) {
            const m = CONFIG.MASK_SIZE * s;
            ctx.drawImage(images['mask' + state.mask], X(fx) - m / 2, Y(fy) - m / 2, m, m);
        }
        // coin
        if (state.coin) {
            const c = CONFIG.COIN_SIZE * s;
            ctx.globalAlpha = state.coin.opacity;
            ctx.drawImage(images[state.coin.outcome], X(fx) - c / 2, Y(fy) - c / 2, c, c);
            ctx.globalAlpha = 1;
        }
        // message
        if (state.message) {
            const [mx, my] = CONFIG.MESSAGE_POS;
            ctx.fillStyle = CONFIG.MESSAGE_COLOR;
            ctx.font = `bold ${Math.round(CONFIG.MESSAGE_FONT_PX * s)}px ${CONFIG.FONT}`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.direction = opts.rtl ? 'rtl' : 'ltr';
            ctx.fillText(state.message, X(mx), Y(my));
        }
    }

    // A static picture of the scene for instruction pages (an <img> with a data URL).
    // The picture covers the scene area (arms + reward box), scaled by `scale`.
    function sceneImageHtml(state, scale) {
        scale = scale || 0.7;
        const halfW = (Math.max(...CONFIG.ARM_X_POSITIONS.map(Math.abs)) + CONFIG.ARM_SIZE / 2 + 30);
        const top = CONFIG.FEEDBACK_POS[1] + CONFIG.FEEDBACK_BOX_SIZE / 2 + 30;
        const bottom = CONFIG.ARM_Y - CONFIG.ARM_SIZE / 2 - 30;
        const w = Math.round(2 * halfW * scale), h = Math.round((top - bottom) * scale);
        const dpr = window.devicePixelRatio || 1;
        const canvas = document.createElement('canvas');
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        const ctx = canvas.getContext('2d');
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        drawScene(ctx, w, h, state, { cx: w / 2, cy: top * scale, scale: scale });
        return `<img class="scene-example" src="${canvas.toDataURL()}" style="width:${w}px;height:${h}px;">`;
    }

    // ── frame-counted sequence ───────────────────────────────────────────────
    // seq: [{name, draw: () => void, frames: n}, ...]. Each screen is drawn in a
    // requestAnimationFrame callback and stays for exactly `frames` refreshes (unless the
    // browser drops frames). Resolves with onsets {name: ms}: the timestamp of the first frame
    // callback after the draw (~ when the screen became visible), plus frame statistics.
    function runSequence(seq) {
        return new Promise(resolve => {
            const onsets = {};
            let i = 0, left = 0, pending = null, last = null;
            const intervals = [];
            function tick(ts) {
                if (last !== null) intervals.push(ts - last);
                last = ts;
                if (pending) { onsets[pending] = ts; pending = null; }
                if (left === 0) {
                    if (i === seq.length) {
                        const long = intervals.filter(d => d > 1.5 * refresh.frame_ms).length;
                        resolve({ onsets, n_frames: intervals.length, n_long_frames: long });
                        return;
                    }
                    seq[i].draw();
                    pending = seq[i].name;
                    left = seq[i].frames;
                    i++;
                }
                left--;
                requestAnimationFrame(tick);
            }
            requestAnimationFrame(tick);
        });
    }

    return { images, loadAssets, refresh, measureRefresh, framesFor, makeCanvas, drawScene,
             sceneImageHtml, runSequence, colourHex };
})();
