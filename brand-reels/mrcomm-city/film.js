// MR Communications — "Signal City": an isometric night city connected by radio. 30 s, 9:16, 100 bpm (bar = 3 s).
// The city is an illustration of the industries the site lists; product images are the site's own.
import * as M from './lib/motion.js';
import { W, H, E, clamp, lerp, B, p, sp, coverAt, shade, text, measure, rise, voItems, roll, grain, vignette, words, hash01 } from './lib/kit.js';

const C = { bg: '#07080b', amber: '#fc9f30', text: '#f8f8f8', muted: '#95989f', top: '#20242d', left: '#161920', right: '#0f1116', line: 'rgba(255,255,255,.06)' };
const D = 'Display', U = 'UI';
const hud = (ctx, s, x, y, color = C.amber, size = 22, align = 'left') => text(ctx, s, x, y, `500 ${size}px ${U}`, color, align, size * 0.16);
const head = (ctx, t, bar, hi = [], size = 84) => rise(ctx, t, voItems(bar, { hi, col: C.amber }), { x: 80, y: 300, size, family: D, weight: 700, track: -2, color: '#fff', maxW: W - 160, shadow: 0.6 });

// sites: [id, x, z, w, d, h, label, bar-it-lights-on]
const SITES = [
  ['build', -5, -3, 3, 3, 1.2, 'CONSTRUCTION', 1], ['hotel', 2, -5, 2.4, 2.4, 7, 'HOTEL', 2], ['retail', 5, -2, 2.6, 2, 2.2, 'RETAIL', 2],
  ['event', -5, 3, 4, 3.4, 1.0, 'EVENTS', 3], ['security', 0, 5, 1.6, 1.6, 1.6, 'SECURITY', 3], ['factory', 5, 3, 3.4, 2.6, 2.6, 'FACTORY', 4], ['ware', 2, 7, 3.6, 2.2, 1.8, 'WAREHOUSE', 4],
  ['campus', -1, -8, 3, 2, 3.4, 'CAMPUS', 5], ['office', 7, -7, 2, 2, 5, 'OFFICE', 5],
];
const TOWER = [0, 0];
const HITS = [
  [B(0.05), 'pulse', 'sub', { len: 0.8 }], ...[1, 2, 3, 4].map((i) => [B(i * 3 + 0.2), 'site ' + i, 'blip', { pitch: ['A5', 'C6', 'E6', 'G6'][i - 1] }]),
  [B(15.2), 'all connect', 'riser', { len: 0.8 }], [B(16.0), 'connected', 'impact'],
  ...[0, 1, 2].map((i) => [B(18.2 + i * 0.6), 'product ' + i, 'click']), [B(21.2), 'devices', 'coins'],
  ...[0, 1, 2].map((i) => [B(24.2 + i * 0.55), 'svc ' + i, 'thud']), [B(27), 'cta', 'impact'],
];

let CAM = { x: 0, z: 0, s: 60 };
const ISO = (x, y, z) => [W / 2 + (x - CAM.x - (z - CAM.z)) * 0.866 * CAM.s, H * 0.6 + ((x - CAM.x) + (z - CAM.z)) * 0.5 * CAM.s - y * CAM.s];
function camAt(t) { // [time, x, z, scale]
  const K = [[0, 0, 0, 52], [3, -3.5, -1.5, 90], [6, 4.4, -2.6, 74], [9, -2.4, 4.4, 80], [12, 5.0, 5.8, 74], [15, 0.5, 0, 46], [18, 0.5, 0, 46], [30, 0.5, 0, 40]];
  let i = 0; while (i < K.length - 2 && t > K[i + 1][0]) i++; const [t0, x0, z0, s0] = K[i], [t1, x1, z1, s1] = K[i + 1], k = E.inOutCubic(clamp((t - t0 + 0.6) / 0.9));
  CAM.x = lerp(x0, x1, k); CAM.z = lerp(z0, z1, k); CAM.s = lerp(s0, s1, k); }
function poly(ctx, pts, fill) { ctx.fillStyle = fill; ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); ctx.fill(); }
function box(ctx, x, z, w, d, h, lit = 0, seed = 1) {
  const a = ISO(x, 0, z + d), b = ISO(x + w, 0, z + d), c = ISO(x + w, 0, z), at = ISO(x, h, z + d), bt = ISO(x + w, h, z + d), ct = ISO(x + w, h, z), dt = ISO(x, h, z);
  poly(ctx, [a, b, bt, at], C.left); poly(ctx, [b, c, ct, bt], C.right); poly(ctx, [at, bt, ct, dt], C.top);
  if (lit > 0) { poly(ctx, [a, b, bt, at], `rgba(252,159,48,${0.22 * lit})`); poly(ctx, [b, c, ct, bt], `rgba(252,159,48,${0.12 * lit})`); poly(ctx, [at, bt, ct, dt], `rgba(252,159,48,${0.5 * lit})`); }
  // windows
  const rows = Math.max(1, Math.floor(h * 1.6)), cols = Math.max(1, Math.floor(w * 1.4));
  for (let r = 0; r < rows; r++) for (let q = 0; q < cols; q++) { const on = hash01(r * 31 + q + seed * 97, 3) > 0.5; if (!on) continue; const u0 = (q + 0.25) / cols, u1 = (q + 0.7) / cols, v0 = (r + 0.3) / rows, v1 = (r + 0.75) / rows;
    const P = (u, v) => [lerp(a[0], b[0], u), lerp(a[1], b[1], u) - (at[1] - a[1]) * -v]; const p0 = P(u0, v0), p1 = P(u1, v0), p2 = P(u1, v1), p3 = P(u0, v1);
    poly(ctx, [p0, p1, p2, p3], `rgba(255,${190 + lit * 40},${110 + lit * 30},${0.25 + 0.6 * lit})`); }
  ctx.strokeStyle = lit ? `rgba(252,159,48,${0.4 * lit + 0.1})` : 'rgba(255,255,255,.07)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(at[0], at[1]); ctx.lineTo(bt[0], bt[1]); ctx.lineTo(ct[0], ct[1]); ctx.lineTo(dt[0], dt[1]); ctx.closePath(); ctx.stroke();
}
function crane(ctx, x, z, lit) { const b = ISO(x, 0, z), t0 = ISO(x, 5, z), j = ISO(x + 3.5, 5, z - 0.5); ctx.strokeStyle = lit ? C.amber : '#3a3f4a'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(b[0], b[1]); ctx.lineTo(t0[0], t0[1]); ctx.lineTo(j[0], j[1]); ctx.stroke(); const h = ISO(x + 3, 3.2, z - 0.4); ctx.beginPath(); ctx.moveTo(lerp(t0[0], j[0], 0.85), lerp(t0[1], j[1], 0.85)); ctx.lineTo(h[0], h[1]); ctx.lineWidth = 1.5; ctx.stroke(); }
function ground(ctx) { ctx.strokeStyle = C.line; ctx.lineWidth = 1; ctx.beginPath(); for (let i = -12; i <= 12; i++) { let a = ISO(i, 0, -12), b = ISO(i, 0, 12); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); a = ISO(-12, 0, i); b = ISO(12, 0, i); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); } ctx.stroke(); }
function tower(ctx, t, glow) { box(ctx, TOWER[0] - 0.6, TOWER[1] - 0.6, 1.2, 1.2, 1.4, glow, 50); const b = ISO(0, 1.4, 0), tp = ISO(0, 6.5, 0); ctx.strokeStyle = C.amber; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(b[0], b[1]); ctx.lineTo(tp[0], tp[1]); ctx.stroke();
  ctx.fillStyle = C.amber; ctx.shadowColor = C.amber; ctx.shadowBlur = 30; ctx.beginPath(); ctx.arc(tp[0], tp[1], 9, 0, 7); ctx.fill(); ctx.shadowBlur = 0;
  for (let i = 0; i < 3; i++) { const ph = ((t * 0.7 + i / 3) % 1); ctx.strokeStyle = `rgba(252,159,48,${(1 - ph) * 0.7 * glow})`; ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(tp[0], tp[1] + 40, ph * 520 * CAM.s / 50, ph * 300 * CAM.s / 50, 0, 0, 7); ctx.stroke(); } }
function link(ctx, t, s, k) { if (k <= 0) return; const [, x, z, w, d, h] = s, a = ISO(0, 6.5, 0), b = ISO(x + w / 2, h + 0.3, z + d / 2), mx = (a[0] + b[0]) / 2, my = Math.min(a[1], b[1]) - 120;
  ctx.save(); ctx.strokeStyle = `rgba(252,159,48,${0.75 * k})`; ctx.lineWidth = 3; ctx.setLineDash([12, 10]); ctx.lineDashOffset = -t * 60; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.quadraticCurveTo(mx, my, lerp(a[0], b[0], 1), lerp(a[1], b[1], 1)); ctx.stroke(); ctx.restore();
  ctx.fillStyle = C.amber; ctx.beginPath(); ctx.arc(b[0], b[1], 7 * k, 0, 7); ctx.fill(); }
function siteLabel(ctx, s, k) { if (k <= 0) return; const [, x, z, w, d, h, label] = s, q = ISO(x + w / 2, h + 0.4, z + d / 2); ctx.globalAlpha = clamp(k); const f = `500 22px ${U}`, tw = measure(ctx, label, f, 4) + 28;
  ctx.fillStyle = 'rgba(7,8,11,.88)'; ctx.strokeStyle = C.amber; ctx.lineWidth = 2; ctx.beginPath(); ctx.roundRect(q[0] - tw / 2, q[1] - 70, tw, 44, 6); ctx.fill(); ctx.stroke(); hud(ctx, label, q[0], q[1] - 40, '#fff', 22, 'center'); ctx.globalAlpha = 1; }
// a little worker with a walkie-talkie; ping rings when talking
function worker(ctx, t, x, z, k, seed) { if (k <= 0) return; const q = ISO(x, 0, z), s = CAM.s / 60; ctx.fillStyle = '#ffd38a'; ctx.beginPath(); ctx.arc(q[0], q[1] - 46 * s, 9 * s, 0, 7); ctx.fill(); ctx.fillStyle = C.amber; ctx.fillRect(q[0] - 8 * s, q[1] - 36 * s, 16 * s, 26 * s); ctx.fillStyle = '#222'; ctx.fillRect(q[0] + 8 * s, q[1] - 40 * s, 6 * s, 14 * s);
  const ph = (t * 1.3 + seed) % 1; ctx.strokeStyle = `rgba(252,159,48,${(1 - ph) * k})`; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(q[0] + 11 * s, q[1] - 46 * s, 10 + ph * 50 * s, -1.2, 0.2); ctx.stroke(); }

function city(ctx, t, opt = {}) {
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); const r = ctx.createRadialGradient(W / 2, H * 0.55, 0, W / 2, H * 0.55, 1000); r.addColorStop(0, 'rgba(252,159,48,.08)'); r.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = r; ctx.fillRect(0, 0, W, H);
  ground(ctx); const order = [...SITES].sort((a, b) => (a[1] + a[2]) - (b[1] + b[2]));
  const litOf = (s) => opt.all ? 1 : clamp(p(t, s[7] * 3 - 0.1, s[7] * 3 + 0.4)) * (opt.only ? (s[7] === opt.only ? 1 : 0.15) : 1);
  for (const s of order) { if (s[1] + s[2] > 0 && !opt._tw) { opt._tw = 1; tower(ctx, t, opt.tower ?? 0.4); } const L = litOf(s); box(ctx, s[1], s[2], s[3], s[4], s[5], L, s[0].length); if (s[0] === 'build') crane(ctx, s[1] + 0.5, s[2] + 1, L > 0.2); if (s[0] === 'event') { const c = ISO(s[1] + 2, 1.05, s[2] + 1.7); ctx.strokeStyle = `rgba(252,159,48,${0.3 + 0.6 * L})`; ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(c[0], c[1], 110 * CAM.s / 60, 55 * CAM.s / 60, 0, 0, 7); ctx.stroke(); } }
  if (!opt._tw) tower(ctx, t, opt.tower ?? 0.4);
  SITES.forEach((s, i) => { const L = litOf(s); if (opt.links) link(ctx, t, s, clamp(opt.links(i))); if (L > 0.5 && opt.workers !== false) { worker(ctx, t, s[1] + s[3] + 0.4, s[2] + 0.3, L, i * 0.3); worker(ctx, t, s[1] - 0.3, s[2] + s[4] + 0.2, L, i * 0.3 + 0.5); } });
  SITES.forEach((s) => { if (opt.labels !== false && (opt.all || s[7] === opt.only)) siteLabel(ctx, s, opt.all ? opt.labelK ?? 1 : litOf(s)); });
}

function s0(ctx, t) { camAt(t); city(ctx, t, { tower: clamp(p(t, 0, 1.2)), labels: false, workers: false, only: -1 }); head(ctx, t, 0, ['clear', 'line.']); }
const siteScene = (bar, hi) => (ctx, t) => { camAt(t); city(ctx, t, { only: bar }); head(ctx, t, bar, hi); hud(ctx, `SITE 0${bar} · CHANNEL OPEN`, 80, 1700, C.muted, 22); };
const s1 = siteScene(1, ['Construction']), s2 = siteScene(2, ['Hotels', 'retail']), s3 = siteScene(3, ['Event', 'security.']), s4 = siteScene(4, ['Factories', 'warehouses.']);
function s5(ctx, t) { camAt(t); city(ctx, t, { all: true, tower: 1, links: (i) => p(t, 15.1 + i * 0.1, 15.6 + i * 0.1), labelK: clamp(p(t, 15.8, 16.3)) }); head(ctx, t, 5, ['M', 'R', 'Communications.']); }
function s6(ctx, t, I) { camAt(t); ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); ctx.save(); ctx.globalAlpha = 0.45; city(ctx, t, { all: true, tower: 1, labels: false, links: () => 1 }); ctx.restore(); head(ctx, t, 6, ['Radios,', 'push', 'to', 'talk,', 'body', 'cameras.']);
  [['dmr', 'TWO-WAY RADIOS'], ['poc', 'PUSH-TO-TALK'], ['bodycam', 'BODY CAMERAS']].forEach(([k, l], i) => { const kk = sp(t, 18.2 + i * 0.6, M.SPRING.bouncy); if (kk <= 0) return; const x = 80 + i * 320, y = 820 + Math.sin(t * 2 + i) * 10;
    ctx.save(); ctx.translate(x + 140, y + 200); ctx.scale(kk, kk); ctx.translate(-140, -200); ctx.fillStyle = '#111318'; ctx.strokeStyle = C.amber; ctx.lineWidth = 2; ctx.beginPath(); ctx.roundRect(0, 0, 280, 400, 24); ctx.fill(); ctx.stroke();
    coverAt(ctx, I[k], 10, 10, 260, 300, 0.5, 0.5, 1.05, 18); hud(ctx, l, 140, 360, '#fff', 18, 'center'); const b = ISO(0, 6.5, 0); ctx.restore(); }); }
function s7(ctx, t) { camAt(t); city(ctx, t, { all: true, tower: 1, labels: false, links: () => 1, workers: false });
  const n = Math.floor(roll(160, t, 21.0, 1.6)); for (let i = 0; i < n; i++) { const x = -9 + hash01(i, 11) * 18, z = -9 + hash01(i, 12) * 18, q = ISO(x, 0.1, z); ctx.fillStyle = C.amber; ctx.globalAlpha = 0.6 + 0.4 * Math.sin(t * 6 + i); ctx.beginPath(); ctx.arc(q[0], q[1], 4, 0, 7); ctx.fill(); } ctx.globalAlpha = 1;
  shade(ctx, 0, 700, 0.95, 0, '7,8,11'); head(ctx, t, 7, ['thousand', 'devices']); const k = sp(t, 21.2, M.SPRING.bouncy); if (k > 0) { ctx.globalAlpha = clamp(k); text(ctx, Math.round(roll(1000, t, 21.0, 1.2)) + '+', W / 2, 1640, `700 170px ${D}`, C.amber, 'center', -6); hud(ctx, 'DEVICES DEPLOYED · SINCE 2006', W / 2, 1700, C.muted, 22, 'center'); ctx.globalAlpha = 1; } }
function s8(ctx, t) { camAt(t); ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); ctx.save(); ctx.globalAlpha = 0.3; city(ctx, t, { all: true, tower: 1, labels: false, links: () => 1, workers: false }); ctx.restore(); shade(ctx, 0, H, 0.6, 0.9, '7,8,11'); head(ctx, t, 8, ['Twenty', 'years']);
  ['SALES', 'RENTAL', 'PROGRAMMING', 'SUPPORT · AMC'].forEach((s, i) => { const k = sp(t, 23.95 + i * 0.5, M.SPRING.bouncy); if (k <= 0) return; const y = 760 + i * 170; ctx.save(); ctx.globalAlpha = clamp(k * 1.5); ctx.translate((1 - k) * 200, 0); text(ctx, String(i + 1).padStart(2, '0'), 80, y, `500 28px ${U}`, C.amber); text(ctx, s, 150, y + 20, `700 92px ${D}`, i % 2 ? C.amber : '#fff', 'left', -3); ctx.restore(); }); }
function s9(ctx, t, I) { camAt(t); ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); ctx.save(); ctx.globalAlpha = 0.25; city(ctx, t, { all: true, tower: 1, labels: false, links: () => 1, workers: false }); ctx.restore(); shade(ctx, 0, H, 0.6, 0.9, '7,8,11');
  const lk = sp(t, 26.75, M.SPRING.gentle); ctx.globalAlpha = clamp(lk * 1.4); if (I.logo) ctx.drawImage(I.logo, W / 2 - 150, 230, 300, 300); ctx.globalAlpha = 1; hud(ctx, 'READY WHEN YOU ARE', W / 2, 590, C.amber, 24, 'center');
  rise(ctx, t, voItems(9, { hi: ['team', 'communicates.'], col: C.amber, br: ['way'] }), { x: 80, y: 730, size: 92, family: D, weight: 700, track: -3, align: 'center', maxW: W - 160 });
  const ck = sp(t, 27.9, M.SPRING.bouncy); if (ck > 0) { ctx.save(); ctx.translate(W / 2, 1070); ctx.scale(lerp(0.7, 1, ck), lerp(0.7, 1, ck)); ctx.fillStyle = C.amber; ctx.beginPath(); ctx.roundRect(-360, -70, 720, 140, 70); ctx.fill(); text(ctx, '+91 98450 47487', 0, 20, `700 56px ${D}`, '#120c03', 'center', -1); ctx.restore(); }
  const uk = sp(t, 28.4); if (uk > 0) { ctx.globalAlpha = clamp(uk); hud(ctx, 'MRCOMMUNICATIONS.ORG', W / 2, 1220, '#fff', 30, 'center'); hud(ctx, 'SALES · RENTAL · PROGRAMMING', W / 2, 1280, C.muted, 22, 'center'); ctx.globalAlpha = 1; } }

const SC = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9];
M.film({
  fonts: [`700 100px ${D}`, `500 30px ${U}`],
  images: { dmr: 'assets/img/product-dmr.jpg', poc: 'assets/img/product-poc.jpg', bodycam: 'assets/img/product-bodycam.jpg', logo: 'assets/img/logo-DCbxs-Mr.png' }, hits: HITS, samples: 8,
  draw(ctx, u, t, I) { SC[clamp(Math.floor(t / 3), 0, 9)](ctx, t, I); },
  post(ctx, u, t) { vignette(ctx, 0.45); grain(ctx, t, 0.06); },
});
