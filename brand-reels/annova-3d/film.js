// ANNOVA 360 — "Built Exactly": a 2.5-D architectural sequence. 30 s, 9:16, 80 bpm (bar = 3 s).
// The massing model is an abstract illustration of design-build; real projects appear as the site's own photos.
import * as M from './lib/motion.js';
import { W, H, E, clamp, lerp, B, p, sp, logZ, coverAt, shade, text, measure, rise, voItems, grain, vignette, words, hash01 } from './lib/kit.js';

const C = { bg: '#0d0d0d', cream: '#f3f1ee', gold: '#cea359', muted: '#a9adb3', warm: '#ffcf7a' };
const D = 'Display', U = 'UI', GOLD = (a) => `rgba(206,163,89,${a})`;
const lab = (ctx, s, x, y, color = C.gold, size = 22, align = 'left') => text(ctx, s.toUpperCase(), x, y, `500 ${size}px ${U}`, color, align, size * 0.3);
const head = (ctx, t, bar, o = {}) => rise(ctx, t, voItems(bar, { hi: o.hi || [], it: o.hi || [], col: C.gold, br: o.br || [] }), { x: 84, y: o.y || 330, size: o.size || 100, family: D, weight: 300, color: C.cream, maxW: W - 168, align: o.align || 'left', shadow: 0.5 });

const HITS = [
  [B(0.05), 'plan', 'riser', { len: 2.8 }], [B(3), 'tilt', 'whoosh', { len: 1.2, from: 300, to: 1400 }], [B(4.2), 'walls', 'thud'],
  [B(6.3), 'floor 2', 'thud'], [B(7.2), 'roof', 'thud'],
  ...[9.2, 10.0, 12.2, 13.1].map((s, i) => [B(s), 'tag ' + i, 'tok', { pitch: ['E5', 'G5', 'B5', 'E6'][i] }]),
  [B(15), 'orbit', 'whoosh', { len: 2.0, from: 400, to: 2000 }], [B(19.6), 'dissolve', 'swell'], [B(21.3), 'seal', 'impact'],
  ...[0, 1, 2].map((i) => [B(24.2 + i * 0.9), 'card ' + i, 'click']), [B(27), 'cta', 'bell', { pitch: 'E6' }],
];

// ---------- tiny 3-D
let CAM = { yaw: 0, pitch: 1.45, dist: 28, tx: 1, ty: 2.4, tz: 1.5, f: 1950 };
function P(x, y, z) {
  x -= CAM.tx; y -= CAM.ty; z -= CAM.tz; const cy = Math.cos(CAM.yaw), sy = Math.sin(CAM.yaw); let X = x * cy - z * sy, Z = x * sy + z * cy;
  const cp = Math.cos(CAM.pitch), spi = Math.sin(CAM.pitch); const Y = y * cp - Z * spi; Z = y * spi + Z * cp; Z += CAM.dist; const s = CAM.f / Z; return [W / 2 + X * s, H * 0.6 - Y * s, Z];
}
const BOX = { g: [-6, 6, 0, 3.2, -4, 4], u: [-4, 9, 3.2, 6.2, -3.5, 3.5], r: [-5, 10, 6.2, 6.6, -4.2, 4.2] };
function boxFaces(b, h) { const [x0, x1, y0, y1f, z0, z1] = b, y1 = y0 + (y1f - y0) * h; const v = [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]];
  return { v, edges: [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]], faces: [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]] }; }
function drawBox(ctx, b, h, { line = 1, fill = 0, fillCol = '206,163,89', glass = 0 } = {}) {
  if (h <= 0.001) return; const m = boxFaces(b, h), pv = m.v.map((q) => P(...q));
  const faces = m.faces.map((f) => ({ f, z: f.reduce((s, i) => s + pv[i][2], 0) / 4 })).sort((a, b2) => b2.z - a.z);
  for (const { f } of faces) { if (fill > 0) { ctx.fillStyle = `rgba(${fillCol},${fill})`; ctx.beginPath(); f.forEach((i, k) => (k ? ctx.lineTo(pv[i][0], pv[i][1]) : ctx.moveTo(pv[i][0], pv[i][1]))); ctx.closePath(); ctx.fill(); }
    if (glass > 0) { const [a, b2, c, d] = f.map((i) => pv[i]); for (let k = 1; k < 6; k++) { const q = k / 6; ctx.strokeStyle = `rgba(255,207,122,${glass * 0.5})`; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(lerp(a[0], b2[0], q), lerp(a[1], b2[1], q)); ctx.lineTo(lerp(d[0], c[0], q), lerp(d[1], c[1], q)); ctx.stroke(); } } }
  ctx.strokeStyle = GOLD(line); ctx.lineWidth = 3; ctx.lineJoin = 'round'; ctx.beginPath(); m.edges.forEach(([a, b2]) => { ctx.moveTo(pv[a][0], pv[a][1]); ctx.lineTo(pv[b2][0], pv[b2][1]); }); ctx.stroke();
}
const PLAN = [[-6, -4, 6, -4], [6, -4, 6, 4], [6, 4, -6, 4], [-6, 4, -6, -4], [-1, -4, -1, 1], [-6, 1, -2.2, 1], [-0.2, 1, 3, 1], [3, -4, 3, -1.2], [3, 0.4, 3, 4], [-6, -1, -3, -1], [-7, 4.6, 9, 4.6], [9, 4.6, 9, 8], [9, 8, -7, 8], [-7, 8, -7, 4.6]];
function drawPlan(ctx, k, a = 1) {
  const L = PLAN.map(([x0, z0, x1, z1]) => Math.hypot(x1 - x0, z1 - z0)), tot = L.reduce((s, v) => s + v, 0); let rem = tot * k;
  ctx.strokeStyle = GOLD(a); ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.beginPath();
  PLAN.forEach(([x0, z0, x1, z1], i) => { if (rem <= 0) return; const f = Math.min(1, rem / L[i]); rem -= L[i]; const A = P(x0, 0, z0), Bq = P(lerp(x0, x1, f), 0, lerp(z0, z1, f)); ctx.moveTo(A[0], A[1]); ctx.lineTo(Bq[0], Bq[1]); }); ctx.stroke();
  if (k > 0.85) { const A = P(-6.8, 0, 4.8), Bq = P(8.8, 0, 7.8), Cq = P(-6.8, 0, 7.8), Dq = P(8.8, 0, 4.8); ctx.fillStyle = `rgba(80,140,170,${0.25 * a * (k - 0.85) / 0.15})`; ctx.beginPath(); ctx.moveTo(A[0], A[1]); ctx.lineTo(Dq[0], Dq[1]); ctx.lineTo(Bq[0], Bq[1]); ctx.lineTo(Cq[0], Cq[1]); ctx.fill(); }
}
function gridGround(ctx, a) { ctx.strokeStyle = GOLD(a); ctx.lineWidth = 1; ctx.beginPath(); for (let i = -12; i <= 14; i += 2) { const A = P(i, 0, -10), Bq = P(i, 0, 12); ctx.moveTo(A[0], A[1]); ctx.lineTo(Bq[0], Bq[1]); const Cq = P(-12, 0, i), Dq = P(14, 0, i); ctx.moveTo(Cq[0], Cq[1]); ctx.lineTo(Dq[0], Dq[1]); } ctx.stroke(); }
function tag(ctx, t, t0, s, wx, wy, wz, side = 1) { const k = sp(t, t0, M.SPRING.snappy); if (k <= 0) return; const [x, y] = P(wx, wy, wz), ex = x + side * 170 * k, ey = y - 120 * k;
  ctx.strokeStyle = C.gold; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(ex, ey); ctx.lineTo(ex + side * 30, ey); ctx.stroke(); ctx.fillStyle = C.gold; ctx.beginPath(); ctx.arc(x, y, 7, 0, 7); ctx.fill();
  ctx.globalAlpha = clamp(k); const f = `500 24px ${U}`, tw = measure(ctx, s.toUpperCase(), f, 7) + 36, bx = clamp(side > 0 ? ex + 30 : ex - 30 - tw, 40, W - 40 - tw); ctx.fillStyle = 'rgba(13,13,13,.9)'; ctx.fillRect(bx, ey - 28, tw, 56); ctx.strokeStyle = GOLD(0.7); ctx.strokeRect(bx, ey - 28, tw, 56); lab(ctx, s, bx + 18, ey + 8, C.gold, 24); ctx.globalAlpha = 1; }
function bg(ctx) { ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); const r = ctx.createRadialGradient(W / 2, H * 0.55, 0, W / 2, H * 0.55, 1000); r.addColorStop(0, 'rgba(206,163,89,.10)'); r.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = r; ctx.fillRect(0, 0, W, H); }

// camera path (seconds) as eased keys
function camAt(t) {
  const K = [[0, 0.0, 1.5, 30], [3.0, 0.0, 1.5, 30], [5.6, 0.62, 0.42, 34], [9, 0.85, 0.36, 33], [12, 1.25, 0.32, 31], [15, 1.6, 0.34, 32], [18, 3.9, 0.30, 38], [20.5, 6.28 - 0.15, 0.12, 30]];
  let i = 0; while (i < K.length - 2 && t > K[i + 1][0]) i++; const [t0, y0, p0, d0] = K[i], [t1, y1, p1, d1] = K[i + 1], k = E.inOutCubic(clamp((t - t0) / (t1 - t0)));
  CAM.yaw = lerp(y0, y1, k); CAM.pitch = lerp(p0, p1, k); CAM.dist = lerp(d0, d1, k);
}
function model(ctx, t, o = {}) {
  const hg = E.outCubic(p(t, 3.6, 5.4)), hu = E.outBack(p(t, 6.1, 7.0), 1.2), hr = E.outBack(p(t, 7.0, 7.6), 1.4);
  const fill = o.fill ?? 0.06, lit = o.lit || {};
  gridGround(ctx, 0.05 * (o.grid ?? 1)); drawPlan(ctx, 1, 0.5 * (o.plan ?? 1));
  drawBox(ctx, BOX.g, hg, { line: o.line ?? 1, fill: fill + (lit.g || 0) * 0.25, fillCol: lit.g ? '255,207,122' : '206,163,89', glass: o.glass || 0 });
  drawBox(ctx, BOX.u, clamp(hu, 0, 1.08), { line: o.line ?? 1, fill: fill + (lit.u || 0) * 0.25, fillCol: lit.u ? '255,207,122' : '206,163,89', glass: o.glass || 0 });
  drawBox(ctx, BOX.r, clamp(hr, 0, 1.15), { line: o.line ?? 1, fill: fill + 0.1 + (lit.r || 0) * 0.3, fillCol: lit.r ? '255,207,122' : '206,163,89' });
}

// 1 · plan
function s0(ctx, t) { bg(ctx); camAt(t); gridGround(ctx, 0.07); drawPlan(ctx, E.inOutSine(p(t, -0.6, 2.7))); lab(ctx, 'Ground floor plan · Scale 1:100', W / 2, 1640, C.muted, 18, 'center'); head(ctx, t, 0, { hi: ['paper.'] }); }
// 2 · tilt + walls rise
function s1(ctx, t) { bg(ctx); camAt(t); model(ctx, t); head(ctx, t, 1, { hi: ['approved'] }); }
// 3 · floors stack
function s2(ctx, t) { bg(ctx); camAt(t); model(ctx, t, { fill: 0.08 }); head(ctx, t, 2, { hi: ['Exactly.'] }); }
// 4 · architecture / construction
function s3(ctx, t) { bg(ctx); camAt(t); const w = words(3); model(ctx, t, { lit: { g: clamp(p(t, w[0]?.t ?? 9.2, (w[0]?.t ?? 9.2) + 0.4)), u: clamp(p(t, w[1]?.t ?? 10, (w[1]?.t ?? 10) + 0.4)) } });
  tag(ctx, t, w[0]?.t ?? 9.2, 'Architecture', -6, 1.6, 4, -1); tag(ctx, t, w[1]?.t ?? 10.0, 'Construction', 9, 4.7, 3.5, 1); head(ctx, t, 3, { hi: ['Construction.'], size: 92 }); }
// 5 · interiors / turnkey
function s4(ctx, t) { bg(ctx); camAt(t); const w = words(4); model(ctx, t, { lit: { g: 1, u: 1, r: clamp(p(t, w[2]?.t ?? 13.1, (w[2]?.t ?? 13.1) + 0.4)) }, glass: clamp(p(t, w[0]?.t ?? 12.2, (w[0]?.t ?? 12.2) + 0.6)) });
  tag(ctx, t, w[0]?.t ?? 12.2, 'Interiors', -4, 4.7, -3.5, -1); tag(ctx, t, w[2]?.t ?? 13.1, 'Turnkey delivery', 10, 6.4, 0, 1); head(ctx, t, 4, { hi: ['Turnkey', 'delivery.'], size: 92 }); }
// 6 · orbit
function s5(ctx, t) { bg(ctx); camAt(t); model(ctx, t, { lit: { g: 1, u: 1, r: 1 }, glass: 1, fill: 0.1 }); head(ctx, t, 5, { hi: ['site.'], size: 92 }); }
// 7 · dissolve to the real villa
function s6(ctx, t, I) { bg(ctx); camAt(t); const k = E.inOutSine(p(t, 19.4, 21.0));
  model(ctx, t, { lit: { g: 1 - k, u: 1 - k, r: 1 - k }, glass: 1 - k, line: 1 - k * 0.6 });
  if (k > 0) { ctx.save(); ctx.globalAlpha = k; coverAt(ctx, I.villa, 0, 0, W, H, 0.5, 0.5, logZ(1.12, 1.04, k)); ctx.restore(); ctx.save(); ctx.globalAlpha = 1 - k; ctx.restore(); }
  shade(ctx, 0, 680, 0.9 * Math.max(0.4, k), 0, '10,10,10'); head(ctx, t, 6, { hi: ['approve...'] }); }
// 8 · is what you get + seal
function s7(ctx, t, I) { coverAt(ctx, I.villa, 0, 0, W, H, 0.5, 0.5, logZ(1.04, 1.12, p(t, 21, 24))); ctx.save(); ctx.globalAlpha = 0.5 * (1 - E.outCubic(p(t, 21, 22.6))); ctx.drawImage(I.bp, 0, 0, W, H); ctx.restore();
  shade(ctx, 0, 700, 0.9, 0, '10,10,10'); shade(ctx, H - 700, H, 0, 0.8, '10,10,10'); head(ctx, t, 7, { hi: ['get.'], size: 124 });
  const k = sp(t, 21.25, M.SPRING.bouncy); if (k > 0) { ctx.save(); ctx.translate(W - 280, 1220); ctx.rotate(-0.18 + (1 - k) * 0.4); const s = lerp(1.8, 1, clamp(k)); ctx.scale(s, s); ctx.globalAlpha = clamp(k * 1.3);
    ctx.strokeStyle = C.gold; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(0, 0, 150, 0, 7); ctx.stroke(); ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(0, 0, 128, 0, 7); ctx.stroke(); text(ctx, 'APPROVED', 0, 14, `500 40px ${U}`, C.gold, 'center', 6); lab(ctx, 'Built exactly', 0, 66, C.gold, 16, 'center'); ctx.restore(); } }
// 9 · 3-D carousel of real projects
function s8(ctx, t, I) { bg(ctx); head(ctx, t, 8, { hi: ['Bengaluru.'], size: 88 });
  const cards = [['ankuraa', 'Ankuraa Lotus', 'Whitefield · 2022'], ['venus', 'Venus Communiti', 'Commercial · Bengaluru'], ['living', 'Family Residence', 'Residential · Bengaluru']];
  const rot = -E.inOutCubic(p(t, 23.9, 27)) * (2 * Math.PI / 3) * 1.6 + 0.3, R = 380, cy = 1010, f = 1400, dist = 1500;
  const items = cards.map((c, i) => { const a = rot + i * 2 * Math.PI / 3, x = Math.sin(a) * R, z = Math.cos(a) * R; return { c, x, z, a }; }).sort((a, b2) => a.z - b2.z);
  for (const { c, x, z, a } of items) { const s = f / (dist - z), cw = 600 * s, ch = 800 * s, sx = W / 2 + x * s, sk = Math.cos(a);
    ctx.save(); ctx.translate(sx, cy); ctx.transform(Math.abs(sk) * 0.6 + 0.4, 0, 0, 1, 0, 0); ctx.globalAlpha = clamp(0.35 + (z + R) / (2 * R) * 0.65);
    coverAt(ctx, I[c[0]], -cw / 2, -ch / 2, cw, ch, 0.5, 0.5, 1.05); ctx.strokeStyle = GOLD(0.8); ctx.lineWidth = 2; ctx.strokeRect(-cw / 2, -ch / 2, cw, ch); ctx.restore(); }
  const front = items[items.length - 1]; ctx.globalAlpha = 1; text(ctx, front.c[1], W / 2, 1520, `300 70px ${D}`, C.cream, 'center'); lab(ctx, front.c[2], W / 2, 1570, C.gold, 20, 'center'); }
// 10 · CTA
function s9(ctx, t, I) { bg(ctx); CAM.yaw = 0.6 + (t - 27) * 0.15; CAM.pitch = 0.38; CAM.dist = 40; ctx.save(); ctx.globalAlpha = 0.35; model(ctx, 99, { lit: { g: 1, u: 1, r: 1 }, glass: 1 }); ctx.restore();
  shade(ctx, 0, H, 0.55, 0.85, '13,13,13'); const lk = sp(t, 26.75, M.SPRING.gentle); ctx.globalAlpha = clamp(lk * 1.3);
  if (I.logo) { const sx = 366, sy = 140, sw = 842, sh = 631, w = 500, h = w * sh / sw; ctx.drawImage(I.logo, sx, sy, sw, sh, (W - w) / 2, 330, w, h); } ctx.globalAlpha = 1;
  head(ctx, t, 9, { y: 900, size: 92, hi: ['consultation.'], align: 'center' });
  const bk = sp(t, 28.0, M.SPRING.gentle); if (bk > 0) { ctx.save(); ctx.globalAlpha = clamp(bk); ctx.fillStyle = C.gold; ctx.fillRect(W / 2 - 300, 1130, 600, 110); lab(ctx, 'Book consultation', W / 2, 1195, '#141006', 26, 'center');
    text(ctx, '+91 88610 35808', W / 2, 1340, `300 66px ${D}`, C.cream, 'center'); lab(ctx, 'annova360.com  ·  Est. 2014', W / 2, 1400, C.muted, 20, 'center'); ctx.restore(); } }

const SC = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9];
M.film({
  fonts: [`300 100px ${D}`, `italic 300 100px ${D}`, `500 30px ${U}`],
  images: { villa: 'assets/img/villa_9x16.jpg', bp: 'assets/img/blueprint.png', ankuraa: 'assets/img/proj-ankuraa-lotus-exterior.jpg', venus: 'assets/img/proj-venus-exterior.jpg', living: 'assets/img/proj-residence-living.jpg', logo: 'assets/img/annova-logo.png' },
  hits: HITS, samples: 8,
  draw(ctx, u, t, I) { SC[clamp(Math.floor(t / 3), 0, 9)](ctx, t, I); },
  post(ctx, u, t) { vignette(ctx, 0.45); grain(ctx, t, 0.05); },
});
