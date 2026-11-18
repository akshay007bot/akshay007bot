// Shared helpers for the client reels. Time here is in SECONDS (t); bars are 3 s.
// Pure functions of time only: no Math.random, no state between frames.
import * as M from './motion.js';
export const { W, H, E, clamp, lerp, font, spring, SPRING, hash01, mulberry32, rrect, fill } = M;

export const GRID = await fetch('beats.json').then((r) => r.json());
export const VO = await fetch('vo.json').then((r) => r.json()).catch(() => []);
export const B = (s) => (s - GRID.offset) / GRID.period;            // seconds -> beats (for HITS)
export const BAR = (i) => i * 3;                                      // bar start, seconds
export const p = (t, a, b) => clamp((t - a) / (b - a));
export const sp = (t, t0, cfg = SPRING.snappy) => spring(t - t0, cfg);
export const logZ = (a, b, k) => a * (b / a) ** k;

// cover-fit an image so image point (cx, cy) sits at the box centre
export function coverAt(ctx, img, x, y, w, h, cx = 0.5, cy = 0.5, zoom = 1, radius = 0) {
  if (!img) return;
  const s = Math.max(w / img.width, h / img.height) * zoom, dw = img.width * s, dh = img.height * s;
  const dx = clamp(x + w / 2 - cx * dw, x + w - dw, x), dy = clamp(y + h / 2 - cy * dh, y + h - dh, y);
  ctx.save(); ctx.beginPath(); if (radius) ctx.roundRect(x, y, w, h, radius); else ctx.rect(x, y, w, h); ctx.clip();
  ctx.drawImage(img, dx, dy, dw, dh); ctx.restore();
}
export function shade(ctx, y0, y1, a0, a1, rgb = '0,0,0') {
  const g = ctx.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, `rgba(${rgb},${a0})`); g.addColorStop(1, `rgba(${rgb},${a1})`);
  ctx.fillStyle = g; ctx.fillRect(0, Math.min(y0, y1), W, Math.abs(y1 - y0));
}
export function text(ctx, s, x, y, f, color, align = 'left', track = 0) {
  ctx.font = f; ctx.fillStyle = color; ctx.textAlign = align; ctx.letterSpacing = `${track}px`; ctx.fillText(s, x, y); ctx.letterSpacing = '0px';
}
export function measure(ctx, s, f, track = 0) { ctx.font = f; ctx.letterSpacing = `${track}px`; const w = ctx.measureText(s).width; ctx.letterSpacing = '0px'; return w; }

// VO words for a bar; each word appears when spoken
export const words = (bar) => (VO.find((v) => v.bar === bar) || { words: [] }).words;

// Kinetic headline: words rise out of a mask as they are spoken. lines: array of arrays of words or
// strings (explicit layout). colorFn(word, i) picks a fill (string or gradient).
export function rise(ctx, t, items, { x, y, size, family, weight = 500, lead = 1.08, color = '#fff', align = 'left', maxW = W - 2 * x, track = 0, italic = false, shadow = 0, exit = null }) {
  const f = `${italic ? 'italic ' : ''}${weight} ${size}px ${family}`;
  ctx.font = f; const spc = ctx.measureText(' ').width;
  let lx = 0, line = 0; const pos = [];
  const fi = `italic ${weight} ${size}px ${family}`;
  for (const it of items) { const w = measure(ctx, it.w, it.italic ? fi : f, track); if (lx > 0 && (lx + w > maxW || it.br)) { lx = 0; line++; } pos.push({ ...it, lx, line, ww: w }); lx += w + spc; }
  const lw = []; pos.forEach((q) => { lw[q.line] = Math.max(lw[q.line] || 0, q.lx + q.ww); });
  const ex = exit == null ? 0 : E.inCubic(p(t, exit, exit + 0.35));
  for (const q of pos) {
    const k = sp(t, q.t - 0.08); if (k <= 0) continue;
    const bx = align === 'center' ? (W - lw[q.line]) / 2 + q.lx : x + q.lx, by = y + q.line * size * lead;
    ctx.save(); ctx.beginPath(); ctx.rect(bx - 20, by - size * 1.05, q.ww + 50, size * 1.4); ctx.clip();
    if (shadow) { ctx.shadowColor = `rgba(0,0,0,${shadow})`; ctx.shadowBlur = 30; ctx.shadowOffsetY = 4; }
    ctx.font = q.italic ? fi : f; ctx.letterSpacing = `${track}px`; ctx.textAlign = 'left';
    ctx.fillStyle = typeof q.color === 'function' ? q.color(ctx, bx, by, q.ww, size) : (q.color || color);
    ctx.fillText(q.w, bx, by + (1 - k) * size * 0.95 + ex * size * 1.2); ctx.restore();
  }
  ctx.letterSpacing = '0px';
  return y + line * size * lead;
}
// items from a VO bar, with optional per-word colours and forced breaks
export const voItems = (bar, { hi = [], br = [], col, it = [] } = {}) => words(bar).map((w) => ({ w: w.w, t: w.t, color: hi.includes(w.w) ? col : null, br: br.includes(w.w), italic: it.includes(w.w) }));
// items from fixed text, appearing on a schedule
export const seqItems = (s, t0, step, opts = {}) => s.split(' ').map((w, i) => ({ w, t: t0 + i * step, color: (opts.hi || []).includes(w) ? opts.col : null, br: (opts.br || []).includes(w) }));

// Split-flap: each character flips through random glyphs, then lands; lands left to right from t0
const FLAP = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
export function flapStr(s, t, t0, perChar = 0.035, spin = 0.32, seed = 1) {
  let out = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i]; if (ch === ' ') { out += ' '; continue; }
    const land = t0 + i * perChar + spin;
    if (t >= land) out += ch;
    else if (t < t0 + i * perChar * 0.5) out += ' ';
    else out += FLAP[Math.floor(hash01(i * 97 + Math.floor(t * 30), seed) * FLAP.length)];
  }
  return out;
}
export function flapRow(ctx, s, t, t0, x, y, cell, { fg = '#f5f5f5', bg = '#1b2232', gap = 6, f, seed = 1, per = 0.035 } = {}) {
  const str = flapStr(s, t, t0, per, 0.32, seed); const h = cell * 1.45;
  for (let i = 0; i < s.length; i++) {
    const cx = x + i * (cell + gap);
    ctx.fillStyle = bg; ctx.beginPath(); ctx.roundRect(cx, y, cell, h, 6); ctx.fill();
    ctx.fillStyle = 'rgba(0,0,0,.45)'; ctx.fillRect(cx, y + h / 2 - 1, cell, 2);
    if (str[i] && str[i] !== ' ') text(ctx, str[i], cx + cell / 2, y + h * 0.72, f || `600 ${cell * 0.95}px UI`, fg, 'center');
  }
  return s.length * (cell + gap);
}
export const typed = (s, t, t0, cps = 18) => s.slice(0, clamp(Math.floor((t - t0) * cps), 0, s.length));
export const caret = (t) => (Math.floor(t * 2.2) % 2 === 0);

// rolling number: value eases from 0 to target
export function roll(target, t, t0, d = 0.9) { const k = E.outCubic(p(t, t0, t0 + d)); return target * k; }

// film grain + vignette for post()
let NOISE = null;
export function grain(ctx, t, amt = 0.06) {
  if (!NOISE) { NOISE = document.createElement('canvas'); NOISE.width = NOISE.height = 512; const c = NOISE.getContext('2d'); const d = c.createImageData(512, 512); const r = mulberry32(7);
    for (let i = 0; i < d.data.length; i += 4) { const v = r() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; } c.putImageData(d, 0, 0); }
  const f = Math.floor(t * 24); ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = amt;
  ctx.translate(-Math.floor(hash01(f, 3) * 512), -Math.floor(hash01(f, 9) * 512)); ctx.fillStyle = ctx.createPattern(NOISE, 'repeat'); ctx.fillRect(0, 0, W + 512, H + 512); ctx.restore();
}
export function vignette(ctx, a = 0.35) { const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.78); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
// slide A out / B in, both on screen
export function push(ctx, t, t0, d, A, B, dir = [-1, 0]) {
  const k = E.inOutCubic(p(t, t0, t0 + d)); if (k <= 0) return A(); if (k >= 1) return B();
  ctx.save(); ctx.translate(dir[0] * k * W, dir[1] * k * H); A(); ctx.restore();
  ctx.save(); ctx.translate(dir[0] * (k - 1) * W, dir[1] * (k - 1) * H); B(); ctx.restore();
}
