// iOceane — "Blank Screen → Brand". 30 s, 9:16, 120 bpm (bar = 3 s). Plan: docs/shotlist.md
import * as M from './lib/motion.js';
import { W, H, E, clamp, lerp, B, p, sp, logZ, coverAt, shade, text, measure, rise, voItems, seqItems, typed, caret, roll, grain, vignette, words } from './lib/kit.js';

const C = { bg0: '#14181f', bg1: '#121c30', blue: '#3c83f6', teal: '#22c3b0', grey: '#9aa3b2', white: '#ffffff' };
const D = 'Display', U = 'UI';
const gradFill = (ctx, x, y, w, size) => { const g = ctx.createLinearGradient(x, 0, x + Math.max(w, 300), 0); g.addColorStop(0, C.blue); g.addColorStop(1, C.teal); return g; };
const LOGOS = ['ramaiah', 'cadabams-group', 'rambus-new', 'eureka-forbes', 'apollo-homecare', 'india-post-new', 'alliance-university', 'physio-tattva-new', 'dr-lohits', 'esmee-clinics', 'destination-dubai', 'zen-shastra-new', 'organic-express', 'jolle-group', 'fit-zone', 'mystik-new'];
const SVC = ['Branding', 'Digital Marketing', 'Web Development', 'AI Automation', 'Video Production', 'Events'];
const SEARCH = 'best digital marketing agency in bangalore';

const HITS = [
  [B(0), 'open', 'sub', { len: 0.6 }],
  ...[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => [B(i * 3), 'bar ' + i, i === 2 ? 'impact' : 'thud']),
  ...SVC.map((_, i) => [B(6.25 + i * 0.32), 'tile ' + i, 'click']),
  [B(9.2), 'typing', 'type', { len: 1.9 }],
  ...[0, 1, 2].map((i) => [B(10.9 + i * 0.35), 'engine ' + i, 'blip', { pitch: ['E5', 'G#5', 'B5'][i] }]),
  ...[0, 1, 2].map((i) => [B(12.55 + i * 0.7), 'counter ' + i, 'pop', { pitch: 'E5' }]),
  [B(15.1), 'logos', 'whoosh', { len: 0.4 }],
  [B(19.2), '98', 'pop', { pitch: 'B5' }],
  [B(21.0), 'ring', 'whoosh', { len: 0.5, from: 600, to: 2600 }],
  [B(24.2), 'typing 2', 'type', { len: 1.4 }],
  [B(28.6), 'button', 'bell', { pitch: 'E6' }],
];

function bg(ctx, t, glow = 1) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, C.bg0); g.addColorStop(1, C.bg1); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const r = ctx.createRadialGradient(W * 0.85, -100, 0, W * 0.85, -100, 1100); r.addColorStop(0, `rgba(60,131,246,${0.3 * glow})`); r.addColorStop(1, 'rgba(60,131,246,0)'); ctx.fillStyle = r; ctx.fillRect(0, 0, W, H);
  const r2 = ctx.createRadialGradient(0, H, 0, 0, H, 900); r2.addColorStop(0, `rgba(34,195,176,${0.18 * glow})`); r2.addColorStop(1, 'rgba(34,195,176,0)'); ctx.fillStyle = r2; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.045)'; ctx.lineWidth = 1; const off = (t * 12) % 80;
  for (let x = -80 + off; x < W; x += 80) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = -80 + off; y < H; y += 80) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.restore();
}
const punch = (ctx, t, t0) => { const s = 1 + 0.05 * (1 - E.outCubic(p(t, t0, t0 + 0.35))); ctx.translate(W / 2, H / 2); ctx.scale(s, s); ctx.translate(-W / 2, -H / 2); };
const top = (ctx, t, bar, opts = {}) => rise(ctx, t, voItems(bar, { hi: opts.hi || [], col: gradFill, br: opts.br || [] }), { x: 80, y: opts.y || 330, size: opts.size || 84, family: D, weight: 700, ...opts });

// 1 · blank screen
function s0(ctx, t, I) {
  bg(ctx, t, 0.5);
  const k = sp(t, -0.3, M.SPRING.gentle), w = 760, h = 1000, x = (W - w) / 2, y = 600 + (1 - k) * 80;
  ctx.save(); ctx.shadowColor = 'rgba(60,131,246,0.35)'; ctx.shadowBlur = 80; ctx.fillStyle = '#f7f9fc'; ctx.beginPath(); ctx.roundRect(x, y, w, h, 40); ctx.fill(); ctx.restore();
  ctx.fillStyle = '#e6eaf1'; ctx.beginPath(); ctx.roundRect(x, y, w, 70, [40, 40, 0, 0]); ctx.fill();
  ['#ff5f57', '#febc2e', '#28c840'].forEach((c, i) => { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(x + 44 + i * 34, y + 35, 10, 0, 7); ctx.fill(); });
  if (caret(t)) { ctx.fillStyle = C.blue; ctx.fillRect(x + 70, y + 160, 8, 90); }
  // the screen grows to fill frame at the end of the bar
  const z = E.inCubic(p(t, 2.55, 3.0));
  if (z > 0) { ctx.fillStyle = `rgba(20,24,31,${z})`; ctx.fillRect(0, 0, W, H); }
  top(ctx, t, 0, { y: 330, size: 82, br: ['starts'] });
}
// 2 · We build brands that dominate
function s1(ctx, t) {
  bg(ctx, t); ctx.save(); punch(ctx, t, 3);
  rise(ctx, t, voItems(1, { hi: ['that', 'dominate.'], col: gradFill, br: ['brands', 'that'] }), { x: 80, y: 760, size: 150, family: D, weight: 700, lead: 1.05 });
  const k = sp(t, 2.8);
  ctx.globalAlpha = clamp(k); ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.strokeStyle = 'rgba(255,255,255,.18)'; ctx.beginPath(); ctx.roundRect(80, 520, 470, 64, 32); ctx.fill(); ctx.stroke();
  ctx.fillStyle = C.blue; ctx.beginPath(); ctx.arc(116, 552, 8, 0, 7); ctx.fill(); text(ctx, 'AI-Driven Creative Agency', 140, 562, `600 28px ${U}`, '#fff');
  ctx.restore();
}
// 3 · slot-machine services
function s2(ctx, t) {
  bg(ctx, t); ctx.save(); punch(ctx, t, 6);
  top(ctx, t, 2, { y: 330, size: 80, hi: ['AI.', 'Video.'] });
  const tw = 440, th = 230, gx = 40, gy = 34, x0 = (W - 2 * tw - gx) / 2, y0 = 640;
  SVC.forEach((s, i) => {
    const x = x0 + (i % 2) * (tw + gx), y = y0 + Math.floor(i / 2) * (th + gy), land = 6.25 + i * 0.32;
    const a = clamp(sp(t, 5.8 + i * 0.03) * 1.6); if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = 'rgba(255,255,255,.06)'; ctx.strokeStyle = 'rgba(255,255,255,.14)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.roundRect(x, y, tw, th, 28); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.roundRect(x, y, tw, th, 28); ctx.clip();
    const settle = sp(t, land, M.SPRING.bouncy), spin = t < land ? (t - 6) * 9 : 0;
    const idx = t < land ? Math.floor(spin + i * 2) % SVC.length : i;
    const off = t < land ? ((spin % 1) - 0.5) * th : (1 - settle) * -60;
    text(ctx, SVC[idx], x + tw / 2, y + th / 2 + 18 + off, `700 40px ${D}`, t < land ? 'rgba(255,255,255,.55)' : '#fff', 'center');
    if (t >= land) { ctx.fillStyle = C.blue; ctx.fillRect(x + tw / 2 - 30, y + th - 46, 60 * settle, 6); }
    ctx.restore();
  });
  ctx.restore();
}
// 4 · search
function s3(ctx, t) {
  bg(ctx, t); ctx.save(); punch(ctx, t, 9);
  top(ctx, t, 3, { y: 330, size: 80, hi: ['Google,', 'ChatGPT', 'Gemini.'] });
  const k = sp(t, 8.75, M.SPRING.gentle), y = 760 + (1 - k) * 120, x = 80, w = W - 160, h = 130;
  ctx.save(); ctx.globalAlpha = clamp(k * 1.5); ctx.shadowColor = 'rgba(60,131,246,.45)'; ctx.shadowBlur = 70; ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(x, y, w, h, 65); ctx.fill(); ctx.restore();
  ctx.strokeStyle = C.blue; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(x + 74, y + 60, 22, 0, 7); ctx.stroke(); ctx.beginPath(); ctx.moveTo(x + 90, y + 76); ctx.lineTo(x + 106, y + 92); ctx.stroke();
  const s = typed(SEARCH, t, 9.2, 22); ctx.save(); ctx.beginPath(); ctx.rect(x + 130, y, w - 160, h); ctx.clip();
  const f = `500 34px ${U}`; const tw = measure(ctx, s, f); const shift = Math.max(0, tw - (w - 200));
  text(ctx, s, x + 130 - shift, y + 77, f, '#14181f'); if (caret(t) || s.length < SEARCH.length) { ctx.fillStyle = C.blue; ctx.fillRect(x + 136 + tw - shift, y + 40, 4, 52); } ctx.restore();
  ['Google', 'ChatGPT', 'Gemini'].forEach((e, i) => {
    const k2 = sp(t, 10.9 + i * 0.35, M.SPRING.bouncy); if (k2 <= 0) return;
    const cw = 270, cx = 80 + i * (cw + 25), cy = 960;
    ctx.save(); ctx.translate(cx + cw / 2, cy + 45); ctx.scale(k2, k2); ctx.fillStyle = 'rgba(60,131,246,.16)'; ctx.strokeStyle = C.blue; ctx.lineWidth = 2; ctx.beginPath(); ctx.roundRect(-cw / 2, -45, cw, 90, 45); ctx.fill(); ctx.stroke();
    text(ctx, e, 0, 12, `700 34px ${U}`, '#fff', 'center'); ctx.restore();
  });
  // ranking card
  const k3 = sp(t, 11.2, M.SPRING.bouncy);
  if (k3 > 0) { ctx.save(); ctx.globalAlpha = clamp(k3); ctx.translate(0, (1 - k3) * 60); ctx.fillStyle = 'rgba(255,255,255,.06)'; ctx.beginPath(); ctx.roundRect(80, 1110, W - 160, 150, 28); ctx.fill();
    text(ctx, '#1', 130, 1210, `700 80px ${D}`, C.teal); text(ctx, 'Rank Higher. Get Found.', 260, 1180, `700 36px ${D}`, '#fff'); text(ctx, 'Grow Faster.', 260, 1230, `700 36px ${D}`, C.blue); ctx.restore(); }
  ctx.restore();
}
// 5 · counters
function s4(ctx, t) {
  bg(ctx, t); ctx.save(); punch(ctx, t, 12);
  top(ctx, t, 4, { y: 330, size: 80, hi: ['real', 'clients.'] });
  const rows = [[954, 'K+', 'Impressions', 12.55, 0], [10.6, 'K', 'Clicks delivered', 13.25, 1], [78, '%', 'Organic growth', 13.95, 0]];
  rows.forEach(([v, suf, lab, t0, dec], i) => {
    const k = sp(t, t0 - 0.75, M.SPRING.gentle); if (k <= 0) return; const y = 720 + i * 300;
    ctx.save(); ctx.globalAlpha = clamp(k * 1.5); ctx.translate((1 - k) * -120, 0);
    const val = roll(v, t, t0 - 0.6, 0.6), s = (dec ? val.toFixed(1) : Math.round(val)) + suf;
    ctx.font = `700 190px ${D}`; const g = gradFill(ctx, 80, 0, 600); text(ctx, s, 80, y + 150, `700 190px ${D}`, i === 1 ? '#fff' : g);
    text(ctx, lab.toUpperCase(), 84, y + 210, `600 28px ${U}`, C.grey, 'left', 4);
    const sl = p(t, t0, t0 + 0.15); if (sl > 0 && sl < 1) { ctx.globalAlpha = 1 - sl; ctx.fillStyle = C.teal; ctx.fillRect(80, y + 230, 920 * sl, 4); }
    ctx.restore();
  });
  ctx.restore();
}
// 6 · logo wall
function s5(ctx, t, I) {
  bg(ctx, t); ctx.save(); punch(ctx, t, 15);
  top(ctx, t, 5, { y: 330, size: 80, hi: ['120', 'brands.'] });
  const cols = 4, tw = 210, th = 128, gap = 18, x0 = (W - cols * tw - (cols - 1) * gap) / 2, y0 = 640;
  LOGOS.forEach((k, i) => {
    const c = i % cols, r = Math.floor(i / cols), x = x0 + c * (tw + gap), y = y0 + r * (th + gap);
    const d = Math.hypot(c - 1.5, r - 1.5), s = sp(t, 14.8 + d * 0.16, M.SPRING.bouncy); if (s <= 0) return;
    ctx.save(); ctx.translate(x + tw / 2, y + th / 2); ctx.scale(s, s); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(-tw / 2, -th / 2, tw, th, 18); ctx.fill();
    const im = I[k]; if (im) { const sc = Math.min((tw - 20) / im.width, (th - 16) / im.height); ctx.drawImage(im, -im.width * sc / 2, -im.height * sc / 2, im.width * sc, im.height * sc); }
    ctx.restore();
  });
  const k2 = sp(t, 16.6); if (k2 > 0) { ctx.globalAlpha = clamp(k2); text(ctx, '120+ HAPPY CLIENTS · 150+ PROJECTS', W / 2, 1300, `600 28px ${U}`, C.grey, 'center', 4); }
  ctx.restore();
}
// 7 · kinetic stack
function s6(ctx, t) {
  bg(ctx, t); ctx.save(); punch(ctx, t, 18);
  const w = words(6); const tA = 17.85, tB = w[2]?.t ?? 19.2;
  const big = (s, lab, t0, y, grad) => { const k = sp(t, t0 - 0.05, M.SPRING.bouncy); if (k <= 0) return; ctx.save(); ctx.translate(W / 2, y); ctx.scale(lerp(1.25, 1, clamp(k)), lerp(1.25, 1, clamp(k))); ctx.globalAlpha = clamp(k * 1.5);
    ctx.font = `700 260px ${D}`; const g = grad ? gradFill(ctx, -300, 0, 600) : '#fff'; text(ctx, s, 0, 0, `700 260px ${D}`, g, 'center'); text(ctx, lab, 0, 70, `600 30px ${U}`, C.grey, 'center', 5); ctx.restore(); };
  big('15+', 'YEARS EXPERIENCE', tA, 640, false); big('150+', 'PROJECTS DELIVERED', tB, 1000, true); big('98%', 'CLIENT SATISFACTION', 20.0, 1360, false);
  ctx.restore();
}
// 8 · 360 ring
function s7(ctx, t) {
  bg(ctx, t); ctx.save(); punch(ctx, t, 21);
  const items = voItems(7).map((it) => (it.w === 'three-sixty' ? { ...it, w: '360°', color: gradFill } : it));
  rise(ctx, t, items, { x: 80, y: 330, size: 80, family: D, weight: 700, maxW: W - 160 });
  const cx = W / 2, cy = 1010, R = 300, rot = (t - 21) * 0.9, k = E.outCubic(p(t, 20.75, 21.6));
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); const g = ctx.createConicGradient(0, 0, 0); g.addColorStop(0, C.blue); g.addColorStop(0.5, C.teal); g.addColorStop(1, C.blue);
  ctx.strokeStyle = g; ctx.lineWidth = 56; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(0, 0, R, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * k); ctx.stroke(); ctx.restore();
  text(ctx, '360°', cx, cy + 50, `700 150px ${D}`, '#fff', 'center');
  SVC.forEach((s, i) => { const a = -rot * 0.6 + (i / SVC.length) * Math.PI * 2, rr = R + 150, o = clamp(sp(t, 21.4 + i * 0.12)); if (o <= 0) return;
    const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr * 0.92; ctx.globalAlpha = o; ctx.font = `600 26px ${U}`; const tw = ctx.measureText(s).width + 40;
    ctx.fillStyle = 'rgba(20,24,31,.85)'; ctx.strokeStyle = 'rgba(255,255,255,.2)'; ctx.beginPath(); ctx.roundRect(x - tw / 2, y - 28, tw, 56, 28); ctx.fill(); ctx.stroke(); text(ctx, s, x, y + 9, `600 26px ${U}`, '#fff', 'center'); });
  ctx.globalAlpha = 1; ctx.restore();
}
// 9 · ready to transform
function s8(ctx, t) {
  bg(ctx, t); ctx.save(); punch(ctx, t, 24);
  const L1 = 'Ready to', L2 = 'transform', L3 = 'your brand?', all = L1 + L2 + L3, n = clamp(Math.floor((t - 24.15) * 20), 0, all.length);
  const f = `700 150px ${D}`; const a = L1.slice(0, n), b = L2.slice(0, Math.max(0, n - L1.length)), c = L3.slice(0, Math.max(0, n - L1.length - L2.length));
  text(ctx, a, 80, 760, f, '#fff'); text(ctx, b, 80, 920, f, '#fff'); ctx.font = f; text(ctx, c, 80, 1080, f, gradFill(ctx, 80, 0, 800));
  const line = c.length ? [c, 1080] : b.length ? [b, 920] : [a, 760]; if (caret(t) || n < all.length || n === 0) { ctx.fillStyle = C.blue; ctx.fillRect(90 + measure(ctx, line[0], f), line[1] - 120, 10, 140); }
  ctx.restore();
}
// 10 · CTA
function s9(ctx, t, I) {
  bg(ctx, t, 1.2); ctx.save(); punch(ctx, t, 27);
  const lk = sp(t, 26.75, M.SPRING.gentle), lw = 640, lh = lw * 401 / 1017; ctx.globalAlpha = clamp(lk * 1.4); if (I.logo) ctx.drawImage(I.logo, (W - lw) / 2, 420 + (1 - lk) * 40, lw, lh); ctx.globalAlpha = 1;
  rise(ctx, t, voItems(9, { hi: ['extraordinary,', 'together.'], col: gradFill }), { x: 80, y: 860, size: 66, family: D, weight: 700, align: 'center', maxW: W - 160 });
  const bk = sp(t, 27.9, M.SPRING.bouncy); if (bk > 0) {
    const press = 1 - 0.07 * Math.max(0, Math.sin(Math.PI * p(t, 28.6, 28.9))), bw = 720, bh = 130, bx = (W - bw) / 2, by = 1080;
    ctx.save(); ctx.translate(W / 2, by + bh / 2); ctx.scale(lerp(0.6, 1, bk) * press, lerp(0.6, 1, bk) * press); ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(60,131,246,.5)'; ctx.shadowBlur = 60; ctx.beginPath(); ctx.roundRect(-bw / 2, -bh / 2, bw, bh, 65); ctx.fill(); ctx.shadowColor = 'transparent';
    text(ctx, 'Book Free Strategy Call  →', 0, 14, `700 40px ${U}`, '#14181f', 'center'); ctx.restore();
    const rp = p(t, 28.6, 29.6); if (rp > 0 && rp < 1) { ctx.strokeStyle = `rgba(60,131,246,${1 - rp})`; ctx.lineWidth = 4; ctx.beginPath(); ctx.roundRect(bx - rp * 50, by - rp * 50, bw + rp * 100, bh + rp * 100, 65 + rp * 50); ctx.stroke(); }
  }
  const ck = sp(t, 28.3); if (ck > 0) { ctx.globalAlpha = clamp(ck); text(ctx, '+91 90199 31101', W / 2, 1340, `700 52px ${U}`, '#fff', 'center'); text(ctx, 'ioceane.com  ·  @ioceanebranding', W / 2, 1410, `600 30px ${U}`, C.grey, 'center'); }
  ctx.restore();
}

const SC = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9];
const images = { logo: 'assets/img/logo-white.png' }; LOGOS.forEach((k) => { images[k] = `assets/img/${k}.jpg`; });
M.film({
  fonts: [`700 100px ${D}`, `600 40px ${U}`, `500 40px ${U}`], images, hits: HITS, samples: 8,
  draw(ctx, u, t, I) { const i = clamp(Math.floor(t / 3), 0, 9); SC[i](ctx, t, I); },
  post(ctx, u, t) { vignette(ctx, 0.3); grain(ctx, t, 0.05); },
});
