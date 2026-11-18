// iOceane — "Two Brands": a before/after split screen. 30 s, 9:16, 120 bpm (bar = 3 s).
// Top half: a business without a strategy (generic illustration). Bottom: the same business with iOceane.
// Only real numbers are iOceane's own published client metrics.
import * as M from './lib/motion.js';
import { W, H, E, clamp, lerp, B, p, sp, text, measure, rise, words, typed, caret, roll, grain, vignette, hash01 } from './lib/kit.js';

const C = { bg0: '#14181f', bg1: '#121c30', blue: '#3c83f6', teal: '#22c3b0', grey: '#9aa3b2', dull: '#2a2d33', dull2: '#3a3e46', dtext: '#8a8f98' };
const D = 'Display', U = 'UI', MID = 960;
const grad = (ctx, x, y, w) => { const g = ctx.createLinearGradient(x, 0, x + Math.max(w, 300), 0); g.addColorStop(0, C.blue); g.addColorStop(1, C.teal); return g; };

const HITS = [
  [B(0.05), 'split', 'impact'], ...[1, 2, 3, 4, 5].map((i) => [B(i * 3), 'compare ' + i, 'click']),
  [B(7.6), 'notice', 'pop', { pitch: 'D6' }], [B(10.6), 'rank', 'bell', { pitch: 'A5' }], [B(13.6), 'convert', 'click'], [B(16.4), 'growth', 'riser', { len: 0.8 }],
  ...[0, 1].map((i) => [B(18.6 + i * 0.7), 'metric ' + i, 'pop', { pitch: 'D5' }]),
  [B(21), 'merge', 'whoosh', { len: 0.6, from: 400, to: 2400 }], [B(24), 'logo', 'impact'], [B(28.6), 'button', 'bell', { pitch: 'D6' }],
];

// VO split: first sentence → top half, the rest → bottom half
function halves(bar) { const ws = words(bar); const i = ws.findIndex((w) => /[.?]$/.test(w.w)); return [ws.slice(0, i + 1), ws.slice(i + 1)]; }
function dullBg(ctx, y0, y1) { ctx.fillStyle = C.dull; ctx.fillRect(0, y0, W, y1 - y0); }
function brandBg(ctx, t, y0, y1) { const g = ctx.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, C.bg0); g.addColorStop(1, C.bg1); ctx.fillStyle = g; ctx.fillRect(0, y0, W, y1 - y0);
  const r = ctx.createRadialGradient(W * 0.85, y0, 0, W * 0.85, y0, 900); r.addColorStop(0, 'rgba(60,131,246,.3)'); r.addColorStop(1, 'rgba(60,131,246,0)'); ctx.fillStyle = r; ctx.fillRect(0, y0, W, y1 - y0); }
function topLine(ctx, t, ws, y) { rise(ctx, t, ws.map((w) => ({ w: w.w, t: w.t })), { x: 70, y, size: 60, family: U, weight: 600, color: C.dtext, maxW: W - 140 }); }
function botLine(ctx, t, ws, y) { rise(ctx, t, ws.map((w) => ({ w: w.w, t: w.t, color: grad })), { x: 70, y, size: 66, family: D, weight: 700, color: '#fff', maxW: W - 140 }); }
function divider(ctx, t, y = MID) { ctx.fillStyle = '#fff'; ctx.fillRect(0, y - 3, W, 6); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(W / 2, y, 46, 0, 7); ctx.fill(); text(ctx, 'VS', W / 2, y + 13, `700 34px ${D}`, '#14181f', 'center'); }
function card(ctx, x, y, w, h, r, fill, stroke) { ctx.fillStyle = fill; ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fill(); if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 2; ctx.stroke(); } }
const enter = (t, t0) => sp(t, t0 - 0.25, M.SPRING.snappy);

// each comparison: draws top (dull) & bottom (brand) content for its bar
const PAIRS = [
  // 0 · same business
  (ctx, t) => { const k = enter(t, 0); ctx.globalAlpha = clamp(k); text(ctx, 'BRAND A', W / 2, 640, `600 30px ${U}`, C.dtext, 'center', 6); text(ctx, 'no strategy', W / 2, 700, `500 34px ${U}`, C.dtext, 'center');
    text(ctx, 'BRAND B', W / 2, 1500, `700 30px ${U}`, C.teal, 'center', 6); text(ctx, 'with iOceane', W / 2, 1565, `700 44px ${D}`, '#fff', 'center'); ctx.globalAlpha = 1; },
  // 1 · logo vs identity
  (ctx, t) => { const k = enter(t, 3); card(ctx, 380, 520, 320, 220, 10, C.dull2); text(ctx, 'Your Brand', 540, 645, `500 40px ${U}`, '#b3b7bf', 'center');
    const s = sp(t, 3.4, M.SPRING.bouncy); ctx.save(); ctx.translate(300, 1460); ctx.rotate(t * 0.8); const g = ctx.createConicGradient(0, 0, 0); g.addColorStop(0, C.blue); g.addColorStop(0.5, C.teal); g.addColorStop(1, C.blue); ctx.strokeStyle = g; ctx.lineWidth = 28 * s; ctx.beginPath(); ctx.arc(0, 0, 90 * s, 0, 7); ctx.stroke(); ctx.restore();
    ctx.globalAlpha = clamp(s); text(ctx, 'Your Brand', 440, 1470, `700 70px ${D}`, '#fff'); [C.blue, C.teal, '#ffffff', '#14181f'].forEach((c, i) => { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(470 + i * 70, 1540, 22, 0, 7); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.3)'; ctx.stroke(); }); ctx.globalAlpha = 1; },
  // 2 · posts vs gets noticed
  (ctx, t) => { card(ctx, 330, 470, 420, 420, 6, '#e9e9e9'); text(ctx, 'SALE', 540, 690, `700 90px ${U}`, '#555', 'center'); text(ctx, '10% off', 540, 760, `500 40px ${U}`, '#777', 'center');
    const s = 1 + 0.03 * Math.sin(t * 8), k = enter(t, 6); ctx.save(); ctx.translate(540, 1460); ctx.scale(s * k, s * k); const g = ctx.createLinearGradient(-210, -260, 210, 260); g.addColorStop(0, C.blue); g.addColorStop(1, C.teal); ctx.fillStyle = g; ctx.beginPath(); ctx.roundRect(-210, -250, 420, 500, 30); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,.95)'; ctx.beginPath(); ctx.moveTo(-34, -50); ctx.lineTo(50, 0); ctx.lineTo(-34, 50); ctx.fill(); text(ctx, 'REEL', -170, 210, `700 30px ${U}`, '#fff', 'left', 4); ctx.restore();
    for (let i = 0; i < 9; i++) { const a = p(t, 7.4 + i * 0.12, 8.6 + i * 0.12); if (a <= 0 || a >= 1) continue; const x = 790 + hash01(i, 3) * 140, y = 1600 - a * 420; ctx.globalAlpha = 1 - a; ctx.fillStyle = i % 2 ? '#ff5c8a' : '#fff';
      ctx.save(); ctx.translate(x, y); ctx.scale(1.4, 1.4); ctx.beginPath(); ctx.moveTo(0, 10); ctx.bezierCurveTo(-18, -4, -12, -18, 0, -8); ctx.bezierCurveTo(12, -18, 18, -4, 0, 10); ctx.fill(); ctx.restore(); } ctx.globalAlpha = 1; },
  // 3 · hidden vs found
  (ctx, t) => { card(ctx, 90, 520, 900, 110, 55, '#3e424a'); text(ctx, typed('your brand', t, 8.9, 14), 160, 590, `500 38px ${U}`, '#c3c7cf'); if (t > 9.8) text(ctx, 'No results found', 540, 760, `500 40px ${U}`, C.dtext, 'center');
    const k = enter(t, 9); card(ctx, 90, 1280, 900, 110, 55, '#fff'); text(ctx, typed('your brand', t, 9.0, 16), 160, 1350, `500 38px ${U}`, '#14181f');
    const r = sp(t, 10.5, M.SPRING.bouncy); if (r > 0) { ctx.save(); ctx.globalAlpha = clamp(r); ctx.translate(0, (1 - r) * 40); card(ctx, 90, 1430, 900, 200, 26, 'rgba(255,255,255,.08)', 'rgba(60,131,246,.6)');
      ctx.font = `700 110px ${D}`; text(ctx, '#1', 140, 1575, `700 110px ${D}`, grad(ctx, 140, 0, 200)); text(ctx, 'Rank Higher. Get Found.', 330, 1515, `700 40px ${D}`, '#fff'); text(ctx, 'Google · ChatGPT · Gemini', 330, 1575, `600 30px ${U}`, C.grey); ctx.restore(); } },
  // 4 · website vs converts
  (ctx, t) => { card(ctx, 190, 470, 700, 430, 14, '#e4e4e4'); card(ctx, 190, 470, 700, 50, [14, 14, 0, 0], '#cfcfcf'); ctx.save(); ctx.translate(540, 700); ctx.rotate(t * 5); ctx.strokeStyle = '#999'; ctx.lineWidth = 10; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(0, 0, 50, 0, 4.5); ctx.stroke(); ctx.restore(); text(ctx, 'Loading…', 540, 830, `500 32px ${U}`, '#888', 'center');
    const k = enter(t, 12); ctx.save(); ctx.globalAlpha = clamp(k); card(ctx, 190, 1250, 700, 440, 18, '#0d1420', 'rgba(255,255,255,.15)'); ctx.fillStyle = grad(ctx, 230, 0, 400); ctx.fillRect(230, 1320, 380, 24); ctx.fillStyle = 'rgba(255,255,255,.25)'; ctx.fillRect(230, 1370, 520, 14); ctx.fillRect(230, 1400, 440, 14);
      const pr = 1 - 0.08 * Math.max(0, Math.sin(Math.PI * p(t, 13.6, 13.9))); ctx.translate(390, 1530); ctx.scale(pr, pr); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(-160, -45, 320, 90, 45); ctx.fill(); text(ctx, 'Book now', 0, 12, `700 34px ${U}`, '#14181f', 'center'); ctx.restore();
      const cx = lerp(800, 430, E.inOutCubic(p(t, 12.6, 13.5))), cy = lerp(1660, 1550, E.inOutCubic(p(t, 12.6, 13.5))); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + 34, cy + 30); ctx.lineTo(cx + 16, cy + 32); ctx.lineTo(cx + 24, cy + 52); ctx.lineTo(cx + 14, cy + 56); ctx.lineTo(cx + 6, cy + 36); ctx.lineTo(cx - 6, cy + 46); ctx.closePath(); ctx.fill(); },
  // 5 · boosts posts vs runs campaigns
  (ctx, t) => { card(ctx, 340, 520, 400, 100, 50, '#4b5563'); text(ctx, 'Boost post', 540, 585, `600 38px ${U}`, '#c3c7cf', 'center'); ctx.strokeStyle = '#6b7280'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(140, 820); for (let i = 0; i <= 20; i++) ctx.lineTo(140 + i * 40, 820 - Math.sin(i * 1.7) * 8); ctx.stroke();
    const k = E.inOutSine(p(t, 15.0, 16.9)); ctx.save(); ctx.strokeStyle = grad(ctx, 140, 0, 800); ctx.lineWidth = 10; ctx.lineCap = 'round'; ctx.shadowColor = C.blue; ctx.shadowBlur = 20; ctx.beginPath(); ctx.moveTo(140, 1660);
    const n = Math.floor(40 * k); for (let i = 0; i <= n; i++) { const x = 140 + i * 20, y = 1660 - Math.pow(i / 40, 1.8) * 380 - Math.sin(i) * 6; ctx.lineTo(x, y); } ctx.stroke(); ctx.restore();
    ['Targeting', 'Creatives', 'Optimisation'].forEach((s, i) => { const kk = sp(t, 15.4 + i * 0.35, M.SPRING.bouncy); if (kk <= 0) return; ctx.globalAlpha = clamp(kk); const f = `600 26px ${U}`, tw = measure(ctx, s, f) + 40; card(ctx, 90 + i * 300, 1240, tw, 56, 28, 'rgba(60,131,246,.18)', C.blue); text(ctx, s, 90 + i * 300 + tw / 2, 1278, f, '#fff', 'center'); ctx.globalAlpha = 1; }); },
];

function split(ctx, t, i) {
  dullBg(ctx, 0, MID); brandBg(ctx, t, MID, H);
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, MID); ctx.clip(); ctx.restore();
  PAIRS[i](ctx, t);
  const [a, b] = halves(i); topLine(ctx, t, a, 330); botLine(ctx, t, b, MID + 200);
  divider(ctx, t);
}
// 6 · results: unknown vs real metrics
function s6(ctx, t) {
  dullBg(ctx, 0, MID); brandBg(ctx, t, MID, H); text(ctx, '?', W / 2, 760, `700 300px ${U}`, '#4b5058', 'center'); text(ctx, 'No data. No direction.', W / 2, 860, `500 34px ${U}`, C.dtext, 'center');
  rise(ctx, t, words(6).map((w) => ({ w: w.w, t: w.t, color: ['real', 'clients.'].includes(w.w) ? grad : null })), { x: 70, y: MID + 170, size: 62, family: D, weight: 700, color: '#fff', maxW: W - 140 });
  [[954, 'K+', 'Impressions', 18.4], [78, '%', 'Organic growth', 19.1]].forEach(([v, s, l, t0], i) => { const k = sp(t, t0 - 0.3, M.SPRING.gentle); if (k <= 0) return; const y = 1430 + i * 230; ctx.globalAlpha = clamp(k * 1.4);
    ctx.font = `700 150px ${D}`; text(ctx, Math.round(roll(v, t, t0 - 0.3, 0.6)) + s, 70, y, `700 150px ${D}`, grad(ctx, 70, 0, 500)); text(ctx, l.toUpperCase(), 600, y - 40, `600 28px ${U}`, C.grey, 'left', 4); ctx.globalAlpha = 1; });
  text(ctx, 'REAL CLIENT RESULTS', W - 70, 1810, `600 20px ${U}`, C.grey, 'right', 4); divider(ctx, t);
}
// 7 · merge: bottom takes over
function s7(ctx, t) {
  const k = E.inOutCubic(p(t, 20.9, 21.7)), mid = lerp(MID, -10, k); brandBg(ctx, t, 0, H); dullBg(ctx, 0, mid); if (k < 1) divider(ctx, t, mid);
  rise(ctx, t, words(7).map((w) => ({ w: w.w, t: w.t, color: ['brand', 'want', 'to', 'be?'].includes(w.w) ? grad : null })), { x: 80, y: 820, size: 130, family: D, weight: 700, color: '#fff', maxW: W - 160, lead: 1.05 });
}
// 8 · we build brands that dominate
function s8(ctx, t, I) {
  brandBg(ctx, t, 0, H); const lk = sp(t, 23.75, M.SPRING.gentle); ctx.globalAlpha = clamp(lk * 1.3); if (I.logo) ctx.drawImage(I.logo, (W - 700) / 2, 420, 700, 700 * 401 / 1017); ctx.globalAlpha = 1;
  rise(ctx, t, words(8).map((w) => ({ w: w.w, t: w.t, color: ['that', 'dominate.'].includes(w.w) ? grad : null, br: w.w === 'that' })), { x: 80, y: 1020, size: 120, family: D, weight: 700, color: '#fff', maxW: W - 160 });
}
// 9 · CTA
function s9(ctx, t, I) {
  brandBg(ctx, t, 0, H); if (I.logo) ctx.drawImage(I.logo, (W - 520) / 2, 360, 520, 520 * 401 / 1017);
  rise(ctx, t, words(9).map((w) => ({ w: w.w, t: w.t, color: ['free', 'strategy', 'call.'].includes(w.w) ? grad : null })), { x: 80, y: 800, size: 96, family: D, weight: 700, color: '#fff', maxW: W - 160, align: 'center' });
  const bk = sp(t, 27.9, M.SPRING.bouncy); if (bk > 0) { const pr = 1 - 0.07 * Math.max(0, Math.sin(Math.PI * p(t, 28.6, 28.9))); ctx.save(); ctx.translate(W / 2, 1150); ctx.scale(lerp(0.6, 1, bk) * pr, lerp(0.6, 1, bk) * pr); ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(60,131,246,.5)'; ctx.shadowBlur = 60; ctx.beginPath(); ctx.roundRect(-360, -65, 720, 130, 65); ctx.fill(); ctx.shadowColor = 'transparent'; text(ctx, 'Book Free Strategy Call  →', 0, 14, `700 40px ${U}`, '#14181f', 'center'); ctx.restore(); }
  const ck = sp(t, 28.3); if (ck > 0) { ctx.globalAlpha = clamp(ck); text(ctx, '+91 90199 31101', W / 2, 1360, `700 52px ${U}`, '#fff', 'center'); text(ctx, 'ioceane.com  ·  @ioceanebranding', W / 2, 1430, `600 30px ${U}`, C.grey, 'center'); ctx.globalAlpha = 1; }
}

M.film({
  fonts: [`700 100px ${D}`, `600 40px ${U}`, `500 40px ${U}`],
  images: { logo: 'assets/img/logo-white.png' }, hits: HITS, samples: 8,
  draw(ctx, u, t, I) { const i = clamp(Math.floor(t / 3), 0, 9); if (i <= 5) split(ctx, t, i); else [s6, s7, s8, s9][i - 6](ctx, t, I); },
  post(ctx, u, t) { vignette(ctx, 0.3); grain(ctx, t, 0.05); },
});
