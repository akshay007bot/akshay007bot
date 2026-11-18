// VedRx Tours — "Boarding Pass". 30 s, 9:16, 80 bpm (bar = 3 s). Plan: docs/shotlist.md
// Client rules: no Taj Mahal; Bengaluru hospitals; IVF beyond Apollo; a hook every 3 s; visuals = words.
import * as M from './lib/motion.js';
import { W, H, E, clamp, lerp, B, p, sp, logZ, coverAt, shade, text, measure, rise, voItems, flapRow, grain, vignette, words } from './lib/kit.js';

const C = { navy: '#0f1729', navy2: '#17223a', teal: '#128271', hi: '#2fc4a5', blue: '#38bdf8', cream: '#f5f8fa', muted: '#8b97ab', board: '#0a0f1c', cell: '#1b2335' };
const D = 'Display', U = 'UI';
const grad = (ctx, x, y, w) => { const g = ctx.createLinearGradient(x, 0, x + Math.max(w, 200), 0); g.addColorStop(0, '#2fd1ad'); g.addColorStop(1, '#38bdf8'); return g; };
const head = (ctx, t, bar, o = {}) => rise(ctx, t, voItems(bar, { hi: o.hi || [], col: grad, br: o.br || [] }), { x: 80, y: o.y || 330, size: o.size || 92, family: D, weight: 500, color: '#fff', align: o.align || 'left', maxW: W - 160, shadow: o.shadow || 0 });
const lab = (ctx, s, x, y, color = C.hi, size = 24, align = 'left') => text(ctx, s, x, y, `600 ${size}px ${U}`, color, align, size * 0.16);

const HITS = [
  [B(0), 'board', 'type', { len: 0.9 }],
  [B(3), 'cities', 'type', { len: 1.3 }],
  [B(6), 'blr', 'type', { len: 1.3 }],
  [B(9), 'ivf', 'type', { len: 1.3 }],
  [B(12.2), 'pass', 'whoosh', { len: 0.4 }],
  [B(14.4), 'tear', 'click'],
  ...[0, 1, 2].map((i) => [B(15.2 + i * 0.55), 'stamp ' + i, 'thud']),
  [B(18), 'window', 'swell'],
  ...[0, 1, 2, 3].map((i) => [B(21.3 + i * 0.55), 'stop ' + i, 'blip', { pitch: ['G5', 'B5', 'D6', 'G6'][i] }]),
  [B(24), 'arrivals', 'type', { len: 0.9 }],
  [B(25.2), 'arrived', 'bell', { pitch: 'G6' }],
  [B(27), 'cta', 'impact'],
];

function bg(ctx) { ctx.fillStyle = C.navy; ctx.fillRect(0, 0, W, H); const r = ctx.createRadialGradient(W * 0.9, -100, 0, W * 0.9, -100, 1000); r.addColorStop(0, 'rgba(56,189,248,.18)'); r.addColorStop(1, 'rgba(56,189,248,0)'); ctx.fillStyle = r; ctx.fillRect(0, 0, W, H);
  const r2 = ctx.createRadialGradient(0, H, 0, 0, H, 900); r2.addColorStop(0, 'rgba(47,209,173,.14)'); r2.addColorStop(1, 'rgba(47,209,173,0)'); ctx.fillStyle = r2; ctx.fillRect(0, 0, W, H); }
function board(ctx, title, x, y, w, h) { ctx.fillStyle = C.board; ctx.beginPath(); ctx.roundRect(x, y, w, h, 24); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.08)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = '#ffcc33'; ctx.beginPath(); ctx.roundRect(x + 30, y + 28, 14, 44, 3); ctx.fill(); lab(ctx, title, x + 62, y + 62, '#ffcc33', 30); }
function rows(ctx, t, list, t0, y0, cell, step, status) {
  list.forEach((s, i) => { const y = y0 + i * step; flapRow(ctx, s, t, t0 + i * 0.22, 110, y, cell, { bg: C.cell, fg: '#f5f5f5', gap: 5, f: `600 ${cell * 0.9}px ${U}`, seed: i + 3 });
    if (status && t > t0 + i * 0.22 + 0.9) lab(ctx, status, W - 110, y + cell * 1.05, C.hi, 22, 'right'); });
}
// 1 · departures: destination better care
function s0(ctx, t) {
  bg(ctx); head(ctx, t, 0, { hi: ['India?'] });
  board(ctx, 'DEPARTURES', 70, 560, W - 140, 640);
  lab(ctx, 'DESTINATION', 110, 720, C.muted, 22); flapRow(ctx, 'BETTER CARE', t, -0.35, 110, 750, 70, { bg: C.cell, f: `600 66px ${U}`, seed: 2 });
  lab(ctx, 'FROM', 110, 940, C.muted, 22); flapRow(ctx, 'ANYWHERE', t, 0.2, 110, 965, 50, { bg: C.cell, f: `600 46px ${U}`, seed: 5 });
  if (t > 1.2 && Math.floor(t * 2.5) % 2 === 0) lab(ctx, '● BOARDING', W - 110, 1140, C.hi, 28, 'right');
}
// 2 · cities
function s1(ctx, t) {
  bg(ctx); head(ctx, t, 1, { hi: ['210'] });
  board(ctx, 'MEDICAL CITIES · INDIA', 70, 520, W - 140, 760);
  rows(ctx, t, ['BENGALURU', 'DELHI NCR', 'MUMBAI', 'CHENNAI', 'HYDERABAD'], 2.75, 620, 52, 125, 'ON TIME');
  const k = sp(t, 4.4); if (k > 0) { ctx.globalAlpha = clamp(k); text(ctx, '210', 80, 1450, `500 150px ${D}`, grad(ctx, 80, 0, 300)); lab(ctx, 'HOSPITAL LISTINGS', 360, 1385, '#fff', 26); lab(ctx, 'ACROSS 48 CITIES', 360, 1430, C.muted, 26); ctx.globalAlpha = 1; }
}
// 3 · Bengaluru hospitals
function s2(ctx, t) {
  bg(ctx); head(ctx, t, 2, { hi: ['Bengaluru:'], size: 84 });
  board(ctx, 'GATE BLR · BENGALURU', 70, 560, W - 140, 760);
  rows(ctx, t, ['MANIPAL HOSPITALS', 'NARAYANA HEALTH', 'ASTER CMI', 'SPARSH HOSPITAL', 'MS RAMAIAH', 'APOLLO · FORTIS'], 5.75, 660, 42, 105);
  lab(ctx, '57 HOSPITAL LISTINGS IN BENGALURU', W / 2, 1380, C.muted, 22, 'center');
}
// 4 · IVF beyond Apollo
function s3(ctx, t) {
  bg(ctx); head(ctx, t, 3, { hi: ['IVF'], size: 84 });
  board(ctx, 'IVF · FERTILITY CARE · BLR', 70, 560, W - 140, 700);
  rows(ctx, t, ['CLOUDNINE', 'RAINBOW BIRTHRIGHT', 'APOLLO FERTILITY', 'SPARSH WOMEN', 'COLUMBIA ASIA'], 8.75, 660, 40, 110);
  lab(ctx, 'LISTING DOES NOT IMPLY PARTNERSHIP', W / 2, 1320, C.muted, 18, 'center');
}
// 5 · boarding pass
function s4(ctx, t) {
  bg(ctx); head(ctx, t, 4, { hi: ['estimate.'], size: 86 });
  const k = sp(t, 11.75, M.SPRING.gentle), x = 80, y = 620 + (1 - k) * 600, w = W - 160, h = 640, tear = E.inCubic(p(t, 14.3, 14.9));
  ctx.save(); ctx.globalAlpha = clamp(k * 1.4); ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 60; ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(x, y, w, h - 170, [32, 32, 0, 0]); ctx.fill();
  ctx.save(); ctx.translate(0, tear * 120); ctx.rotate(tear * 0.08); ctx.beginPath(); ctx.roundRect(x, y + h - 160, w, 160, [0, 0, 32, 32]); ctx.fill(); ctx.restore(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = C.navy; ctx.beginPath(); ctx.roundRect(x, y, w, 120, [32, 32, 0, 0]); ctx.fill(); text(ctx, 'VedRxTours', x + 40, y + 78, `500 48px ${D}`, '#fff'); lab(ctx, 'BOARDING PASS', x + w - 40, y + 72, C.hi, 22, 'right');
  const F = (l, v, xx, yy, big = 40) => { lab(ctx, l, xx, yy, '#7a8699', 18); text(ctx, v, xx, yy + big + 10, `600 ${big}px ${U}`, C.navy); };
  F('PASSENGER', 'YOU', x + 40, y + 180); F('FROM', 'ANYWHERE', x + 360, y + 180); F('TO', 'BETTER CARE', x + 40, y + 300, 44);
  lab(ctx, 'CLASS', x + 40, y + h - 115 + tear * 120, '#7a8699', 18); text(ctx, 'PERSONALIZED ESTIMATE', x + 40, y + h - 60 + tear * 120, `600 40px ${U}`, C.teal);
  ctx.setLineDash([14, 12]); ctx.strokeStyle = '#c3cad6'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x + 20, y + h - 165); ctx.lineTo(x + w - 20, y + h - 165); ctx.stroke(); ctx.setLineDash([]);
  for (let i = 0; i < 28; i++) { ctx.fillStyle = C.navy; ctx.fillRect(x + w - 290 + i * 9, y + 300, (i * 7) % 3 + 2, 90); }
  ctx.restore();
}
// 6 · passport stamps
function s5(ctx, t) {
  bg(ctx); head(ctx, t, 5, { hi: ['guided.'] });
  ctx.fillStyle = '#efe9dc'; ctx.beginPath(); ctx.roundRect(90, 560, W - 180, 900, 24); ctx.fill(); ctx.strokeStyle = 'rgba(15,23,41,.08)'; ctx.lineWidth = 1;
  for (let y = 600; y < 1440; y += 36) { ctx.beginPath(); ctx.moveTo(120, y); ctx.lineTo(W - 120, y); ctx.stroke(); } lab(ctx, 'VISAS · ENTRIES', 130, 620, 'rgba(15,23,41,.45)', 20);
  [['VISA', 'GUIDANCE', 300, 820, '#128271', -0.2], ['TRAVEL', 'COORDINATED', 720, 1000, '#1d6fd1', 0.15], ['STAY', 'ARRANGED', 360, 1240, '#7b3fbf', -0.08]].forEach(([a, b, x, y, col, rot], i) => {
    const k = sp(t, 14.95 + i * 0.55, M.SPRING.bouncy); if (k <= 0) return; ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(lerp(1.7, 1, clamp(k)), lerp(1.7, 1, clamp(k))); ctx.globalAlpha = clamp(k * 1.5) * 0.9;
    ctx.strokeStyle = col; ctx.lineWidth = 7; ctx.beginPath(); ctx.roundRect(-170, -90, 340, 180, 22); ctx.stroke(); ctx.lineWidth = 2; ctx.beginPath(); ctx.roundRect(-152, -72, 304, 144, 14); ctx.stroke();
    text(ctx, a, 0, 14, `700 66px ${U}`, col, 'center', 6); text(ctx, b, 0, 54, `600 20px ${U}`, col, 'center', 4); ctx.restore(); });
}
// 7 · window seat → coordinator
function s6(ctx, t, I) {
  bg(ctx); const k = E.inOutSine(p(t, 17.8, 21)), wx = 150, wy = 520, ww = W - 300, wh = 980;
  ctx.save(); ctx.fillStyle = '#d9dee6'; ctx.beginPath(); ctx.roundRect(wx - 50, wy - 50, ww + 100, wh + 100, 300); ctx.fill(); ctx.fillStyle = '#c3c9d3'; ctx.beginPath(); ctx.roundRect(wx - 20, wy - 20, ww + 40, wh + 40, 280); ctx.fill(); ctx.restore();
  coverAt(ctx, I.consult, wx, wy, ww, wh, lerp(0.7, 0.84, k), 0.42, logZ(1.2, 1.55, k), 260);
  const sh = E.inOutCubic(p(t, 17.8, 18.6)); if (sh < 1) { ctx.save(); ctx.beginPath(); ctx.roundRect(wx, wy, ww, wh, 260); ctx.clip(); ctx.fillStyle = '#e8ecf2'; ctx.fillRect(wx, wy, ww, wh * (1 - sh)); ctx.restore(); }
  head(ctx, t, 6, { hi: ['care', 'coordinator.'], size: 84 });
}
// 8 · flight path with 4 steps
function s7(ctx, t) {
  bg(ctx); head(ctx, t, 7, { hi: ['step', 'by', 'step.'], size: 88 });
  const pts = [[170, 1380], [420, 1080], [720, 860], [920, 600]], prog = E.inOutSine(p(t, 20.9, 23.2));
  ctx.setLineDash([16, 14]); ctx.strokeStyle = 'rgba(255,255,255,.35)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(...pts[0]); pts.slice(1).forEach((q) => ctx.lineTo(...q)); ctx.stroke(); ctx.setLineDash([]);
  const L = ['Tell us what you need', 'Explore your options', 'Plan with confidence', 'Care beyond arrival'];
  pts.forEach(([x, y], i) => { const k = sp(t, 20.75 + i * 0.6, M.SPRING.bouncy); if (k <= 0) return;
    ctx.save(); ctx.fillStyle = i === 3 ? C.hi : '#fff'; ctx.beginPath(); ctx.arc(x, y, 26 * k, 0, 7); ctx.fill(); text(ctx, '0' + (i + 1), x, y + 9, `700 24px ${U}`, C.navy, 'center');
    ctx.globalAlpha = clamp(k); const right = i < 2; text(ctx, L[i], right ? x + 50 : x - 50, y + 12, `600 34px ${U}`, '#fff', right ? 'left' : 'right'); ctx.restore(); });
  const seg = Math.min(2.999, prog * 3), si = Math.floor(seg), f = seg - si, px = lerp(pts[si][0], pts[si + 1][0], f), py = lerp(pts[si][1], pts[si + 1][1], f);
  ctx.save(); ctx.translate(px, py); ctx.rotate(Math.atan2(pts[si + 1][1] - pts[si][1], pts[si + 1][0] - pts[si][0])); ctx.fillStyle = C.blue; ctx.beginPath(); ctx.moveTo(30, 0); ctx.lineTo(-20, -18); ctx.lineTo(-10, 0); ctx.lineTo(-20, 18); ctx.closePath(); ctx.fill(); ctx.restore();
}
// 9 · arrivals: better care
function s8(ctx, t) {
  bg(ctx); board(ctx, 'ARRIVALS', 70, 300, W - 140, 520);
  lab(ctx, 'DESTINATION', 110, 460, C.muted, 22); flapRow(ctx, 'BETTER CARE', t, 23.7, 110, 490, 70, { bg: C.cell, f: `600 66px ${U}`, seed: 9 });
  if (t > 25.2) { lab(ctx, '● ARRIVED', W - 110, 760, C.hi, 30, 'right'); }
  head(ctx, t, 8, { y: 1060, size: 110, hi: ['Closer', 'than', 'you', 'think.'], br: ['Closer'] });
}
// 10 · CTA
function s9(ctx, t, I) {
  bg(ctx); const k = sp(t, 26.75, M.SPRING.gentle), x = 80, y = 380 + (1 - k) * 200, w = W - 160, h = 760;
  ctx.save(); ctx.globalAlpha = clamp(k * 1.3); ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(0,0,0,.45)'; ctx.shadowBlur = 60; ctx.beginPath(); ctx.roundRect(x, y, w, h, 34); ctx.fill(); ctx.shadowColor = 'transparent';
  if (I.logo) ctx.drawImage(I.logo, x + 90, y + 60, w - 180, (w - 180) * 280 / 1355);
  ctx.setLineDash([14, 12]); ctx.strokeStyle = '#c3cad6'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x + 30, y + 290); ctx.lineTo(x + w - 30, y + 290); ctx.stroke(); ctx.setLineDash([]);
  const items = words(9).filter((q) => !['R', 'X', 'Tours.'].includes(q.w)).map((q) => ({ w: q.w === 'Ved' ? 'VedRxTours.' : q.w, t: q.t, color: q.w === 'Ved' ? '#128271' : null }));
  rise(ctx, t, items, { x: x + 60, y: y + 400, size: 60, family: D, weight: 500, color: C.navy, maxW: w - 120 });
  lab(ctx, 'CALL / WHATSAPP', x + 60, y + 560, '#7a8699', 18); text(ctx, '+91 9535699931', x + 60, y + 615, `600 46px ${U}`, C.navy);
  lab(ctx, 'WEBSITE', x + 60, y + 680, '#7a8699', 18); text(ctx, 'vedrxtours.in', x + 60, y + 730, `600 46px ${U}`, C.teal); ctx.restore();
  const bk = sp(t, 28.2); if (bk > 0) { ctx.globalAlpha = clamp(bk); lab(ctx, 'MEDICAL DECISIONS BELONG TO YOU AND YOUR TREATING TEAM.', W / 2, 1290, C.muted, 17, 'center'); ctx.globalAlpha = 1; }
}

const SC = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9];
M.film({
  fonts: [`500 100px ${D}`, `600 40px ${U}`, `700 40px ${U}`],
  images: { consult: 'assets/img/consultation.jpg', logo: 'assets/img/vedrx-logo.png' },
  hits: HITS, samples: 8,
  draw(ctx, u, t, I) { SC[clamp(Math.floor(t / 3), 0, 9)](ctx, t, I); },
  post(ctx, u, t) { vignette(ctx, 0.3); grain(ctx, t, 0.05); },
});
