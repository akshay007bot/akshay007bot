// MR Communications — "On Air". 30 s, 9:16, 100 bpm (bar = 3 s = 5 beats). Plan: docs/shotlist.md
import * as M from './lib/motion.js';
import { W, H, E, clamp, lerp, B, p, sp, coverAt, shade, text, measure, rise, voItems, roll, grain, vignette, words, hash01 } from './lib/kit.js';

const C = { bg: '#08090c', card: '#111318', amber: '#fc9f30', text: '#f8f8f8', muted: '#95989f' };
const D = 'Display', U = 'UI';
const silver = (ctx, x, y, w, size) => { const g = ctx.createLinearGradient(0, y - size, 0, y); g.addColorStop(0, '#ffffff'); g.addColorStop(1, '#9da1a8'); return g; };
const CH = [
  { n: '01', cat: 'TWO-WAY RADIOS', img: 'dmr', spec: ['IP-RATED', 'MIL-STD TESTED', 'UL913 WHERE NEEDED'], hi: ['Two-way', 'radios.'] },
  { n: '02', cat: 'POC · MISSION-CRITICAL', img: 'poc', spec: ['4G / 5G', 'AI NOISE CANCELLATION', 'PMR / LTE'], hi: ['Push', 'to', 'talk,', 'nationwide.'] },
  { n: '03', cat: 'BODY-WORN CAMERAS', img: 'bodycam', spec: ['AES-256', 'IP68', '130–216° FOV'], hi: ['Encrypted', 'body', 'cameras.'] },
  { n: '04', cat: 'LICENSE-FREE', img: 'license', spec: ['NO PAPERWORK', 'READY OUT OF THE BOX', 'PRESS TO TALK'], hi: ['Just', 'press', 'to', 'talk.'] },
];
const IND = ['Security & Law Enforcement', 'Manufacturing', 'Oil, Gas & Hazardous', 'Hospitality & Retail', 'Construction', 'Event Management', 'Logistics', 'Corporate Campuses'];
const SVC = ['SALES', 'RENTAL', 'PROGRAMMING', 'INSTALLATION', 'AMC'];

const HITS = [
  [B(0.02), 'static', 'crash', { len: 1.2 }],
  [B(1.15), 'led', 'blip', { pitch: 'A5' }],
  [B(3), 'signal', 'thud'],
  ...[0, 1, 2, 3, 4].map((i) => [B(3.25 + i * 0.3), 'bar ' + i, 'tick']),
  ...[6, 9, 12, 15].map((t0, i) => [B(t0), 'channel ' + (i + 1), 'click']),
  [B(12.4), 'rec', 'blip', { pitch: 'E6' }],
  [B(16.3), 'ptt', 'boing', { pitch: 'A4', to: 'E5' }],
  [B(18), 'scope', 'impact'],
  [B(21), 'radar', 'whoosh', { len: 0.5 }],
  ...[0, 1, 2, 3, 4].map((i) => [B(24.05 + i * 0.5), 'svc ' + i, 'thud']),
  [B(27), 'cta', 'impact'],
  [B(29.2), 'over', 'blip', { pitch: 'A5' }],
];

function bg(ctx, t) {
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  const r = ctx.createRadialGradient(W / 2, -150, 0, W / 2, -150, 1100); r.addColorStop(0, 'rgba(252,159,48,.16)'); r.addColorStop(1, 'rgba(252,159,48,0)'); ctx.fillStyle = r; ctx.fillRect(0, 0, W, H);
}
function scan(ctx, a = 0.08) { ctx.fillStyle = `rgba(0,0,0,${a})`; for (let y = 0; y < H; y += 4) ctx.fillRect(0, y, W, 2); }
function staticN(ctx, t, a) { if (a <= 0) return; const f = Math.floor(t * 30); ctx.save(); ctx.globalAlpha = a;
  for (let i = 0; i < 900; i++) { const x = hash01(i * 3 + f * 7919, 1) * W, y = hash01(i * 5 + f * 104729, 2) * H, v = Math.floor(hash01(i + f * 31, 3) * 255); ctx.fillStyle = `rgb(${v},${v},${v})`; ctx.fillRect(x, y, 3 + hash01(i, 4) * 40, 3); }
  ctx.restore(); }
function hud(ctx, s, x, y, color = C.amber, size = 24, align = 'left') { text(ctx, s, x, y, `500 ${size}px ${U}`, color, align, size * 0.16); }
const head = (ctx, t, bar, y = 360, size = 84, hi = []) => rise(ctx, t, voItems(bar, { hi, col: C.amber }), { x: 80, y, size, family: D, weight: 700, track: -2, color: '#fff', maxW: W - 160 });

// 1 · static → radio
function s0(ctx, t, I) {
  bg(ctx, t);
  const rk = E.outCubic(p(t, -0.5, 1.3));
  ctx.save(); ctx.globalAlpha = rk; coverAt(ctx, I.hero, 0, 520, W, 1150, 0.62, 0.5, lerp(1.25, 1.08, rk)); ctx.restore();
  shade(ctx, 520, 760, 1, 0, '8,9,12'); shade(ctx, 1450, 1670, 0, 1, '8,9,12');
  const on = t > 1.15 && Math.floor(t * 3) % 2 === 0; ctx.fillStyle = on ? C.amber : 'rgba(252,159,48,.25)'; ctx.beginPath(); ctx.arc(130, 260, 14, 0, 7); ctx.fill();
  if (on) { ctx.save(); ctx.shadowColor = C.amber; ctx.shadowBlur = 30; ctx.beginPath(); ctx.arc(130, 260, 14, 0, 7); ctx.fill(); ctx.restore(); }
  hud(ctx, 'CH -- · SEARCHING', 165, 269, C.muted);
  rise(ctx, t, voItems(0, { hi: ['you'], col: C.amber }), { x: 80, y: 430, size: 110, family: D, weight: 700, track: -3 });
  staticN(ctx, t, 1 - E.outCubic(p(t, 0, 1.1))); scan(ctx);
}
// 2 · loud and clear
function s1(ctx, t) {
  bg(ctx, t);
  const bx = 80, by = 900; for (let i = 0; i < 5; i++) { const k = sp(t, 2.95 + i * 0.3, M.SPRING.bouncy), h = 80 + i * 70;
    ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.fillRect(bx + i * 110, by - h, 80, h); ctx.fillStyle = C.amber; ctx.fillRect(bx + i * 110, by - h * clamp(k), 80, h * clamp(k)); }
  hud(ctx, 'SIGNAL · 5/5', 80, 960, C.amber, 26);
  rise(ctx, t, voItems(1, { br: ['for'] }).map((w, i) => ({ ...w, color: i < 3 ? silver : C.amber })), { x: 80, y: 1100, size: 104, family: D, weight: 700, track: -3 });
  hud(ctx, '20 YEARS · TRUSTED COMMUNICATION · SINCE 2006', 80, 1390, C.muted, 22); scan(ctx, 0.06);
}
// 3-6 · channels
function channel(ctx, t, I, i) {
  const c = CH[i], t0 = 6 + i * 3; bg(ctx, t);
  const k = sp(t, t0 - 0.25, M.SPRING.gentle), z = lerp(1.12, 1.0, E.outCubic(p(t, t0 - 0.2, t0 + 3)));
  const x = 80, y = 560, w = W - 160, h = 860;
  ctx.save(); ctx.globalAlpha = clamp(k * 1.6); ctx.beginPath(); ctx.roundRect(x, y, w, h, 36); ctx.clip(); coverAt(ctx, I[c.img], x, y, w, h, 0.5, 0.5, z); shade(ctx, y + h - 460, y + h, 0, 0.97, '8,9,12'); ctx.restore();
  ctx.strokeStyle = 'rgba(252,159,48,.5)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.roundRect(x, y, w, h, 36); ctx.stroke();
  // big channel number + dial
  text(ctx, 'CH ' + c.n, 80, 300, `700 120px ${D}`, C.amber, 'left', -3); hud(ctx, c.cat, 84, 350, C.muted, 24);
  const dk = E.outBack(p(t, t0 - 0.15, t0 + 0.35)); ctx.save(); ctx.translate(W - 170, 250); ctx.rotate(-2.2 + i * 0.9 + dk * 0.9);
  ctx.strokeStyle = 'rgba(255,255,255,.25)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(0, 0, 70, 0, 7); ctx.stroke(); ctx.fillStyle = C.amber; ctx.fillRect(-4, -70, 8, 34); ctx.restore();
  for (let j = 0; j < 8; j++) { const a = -2.6 + j * 0.75; ctx.fillStyle = j === i * 2 + 1 ? C.amber : 'rgba(255,255,255,.3)'; ctx.fillRect(W - 170 + Math.cos(a) * 96 - 3, 250 + Math.sin(a) * 96 - 3, 6, 6); }
  // spec HUD on the photo
  c.spec.forEach((s, j) => { const sk = sp(t, t0 + 0.5 + j * 0.25); if (sk <= 0) return; ctx.globalAlpha = clamp(sk); const f = `500 24px ${U}`; const tw = measure(ctx, s, f, 4) + 36;
    ctx.fillStyle = 'rgba(8,9,12,.75)'; ctx.strokeStyle = 'rgba(252,159,48,.6)'; ctx.beginPath(); ctx.roundRect(110, y + 40 + j * 66, tw, 50, 8); ctx.fill(); ctx.stroke(); hud(ctx, s, 128, y + 74 + j * 66, '#ffd7a6', 24); ctx.globalAlpha = 1; });
  if (i === 2) { const on = Math.floor(t * 2.5) % 2 === 0; ctx.fillStyle = on ? '#ff3b30' : 'rgba(255,59,48,.3)'; ctx.beginPath(); ctx.arc(W - 150, y + 70, 14, 0, 7); ctx.fill(); hud(ctx, 'REC', W - 125, y + 79, '#fff', 24); }
  if (i === 3) { const pk = p(t, 16.3, 17.1); if (pk > 0 && pk < 1) { ctx.strokeStyle = `rgba(252,159,48,${1 - pk})`; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(W / 2, y + h / 2, 80 + pk * 400, 0, 7); ctx.stroke(); } }
  rise(ctx, t, voItems(2 + i, { hi: c.hi, col: C.amber }), { x: 110, y: y + h - 120, size: 64, family: D, weight: 700, track: -2, maxW: w - 60 });
  staticN(ctx, t, 0.9 * (1 - p(t, t0 - 0.02, t0 + 0.16))); scan(ctx, 0.05);
}
// 7 · oscilloscope stats
function s6(ctx, t) {
  bg(ctx, t); head(ctx, t, 6, 330, 84, ['thousand', 'devices']);
  const y0 = 640, prog = E.inOutSine(p(t, 17.8, 20.5));
  ctx.strokeStyle = 'rgba(255,255,255,.08)'; ctx.lineWidth = 1; for (let x = 80; x <= W - 80; x += 46) { ctx.beginPath(); ctx.moveTo(x, y0); ctx.lineTo(x, y0 + 300); ctx.stroke(); }
  ctx.save(); ctx.strokeStyle = C.amber; ctx.lineWidth = 5; ctx.shadowColor = C.amber; ctx.shadowBlur = 18; ctx.beginPath();
  const n = 200; for (let i = 0; i <= n * prog; i++) { const x = 80 + (i / n) * (W - 160); const ph = (i / n) * 4; const pk = Math.exp(-(((ph % 1) - 0.5) ** 2) * 40) * (60 + 40 * Math.floor(ph));
    const y = y0 + 150 - Math.sin(i * 0.9 + t * 8) * 10 - pk; i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); } ctx.stroke(); ctx.restore();
  const st = [['20+', 'YEARS IN BUSINESS'], ['40+', 'PRODUCT MODELS'], ['1000+', 'DEVICES DEPLOYED'], ['100%', 'GENUINE PRODUCTS']];
  st.forEach(([v, l], i) => { const k = sp(t, 17.85 + i * 0.55, M.SPRING.bouncy); if (k <= 0) return; const x = 80 + (i % 2) * 470, y = 1080 + Math.floor(i / 2) * 250;
    ctx.save(); ctx.globalAlpha = clamp(k); ctx.translate(0, (1 - k) * 40); text(ctx, v, x, y, `700 130px ${D}`, i === 2 ? C.amber : '#fff', 'left', -5); hud(ctx, l, x + 4, y + 50, C.muted, 20); ctx.restore(); });
  scan(ctx, 0.05);
}
// 8 · radar
function s7(ctx, t) {
  bg(ctx, t); head(ctx, t, 7, 330, 80, ['signal', 'follows.']);
  const cx = W / 2, cy = 1040, R = 400, ang = (t - 20.8) * 2.4;
  ctx.strokeStyle = 'rgba(252,159,48,.25)'; ctx.lineWidth = 2; for (let r = 100; r <= R; r += 100) { ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(cx - R, cy); ctx.lineTo(cx + R, cy); ctx.moveTo(cx, cy - R); ctx.lineTo(cx, cy + R); ctx.stroke();
  const g = ctx.createConicGradient(ang - 0.9, cx, cy); g.addColorStop(0, 'rgba(252,159,48,0)'); g.addColorStop(0.14, 'rgba(252,159,48,.45)'); g.addColorStop(0.141, 'rgba(252,159,48,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.fill();
  IND.forEach((s, i) => { const a = -1.4 + i * 0.79, rr = 150 + ((i * 2) % 4) * 80, x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr; const appear = 20.8 + ((a + 1.4 + 0.9) / 2.4);
    const k = sp(t, appear, M.SPRING.bouncy); if (k <= 0) return; ctx.save(); ctx.globalAlpha = clamp(k); ctx.fillStyle = C.amber; ctx.shadowColor = C.amber; ctx.shadowBlur = 20; ctx.beginPath(); ctx.arc(x, y, 9 * k, 0, 7); ctx.fill(); ctx.shadowBlur = 0;
    const f = `500 22px ${U}`, tw = measure(ctx, s.toUpperCase(), f, 2) + 24, lx = clamp(x - tw / 2, 40, W - 40 - tw); ctx.fillStyle = 'rgba(8,9,12,.85)'; ctx.beginPath(); ctx.roundRect(lx, y + 16, tw, 40, 6); ctx.fill(); text(ctx, s.toUpperCase(), lx + 12, y + 44, f, '#fff', 'left', 2); ctx.restore(); });
  scan(ctx, 0.05);
}
// 9 · services ticker
function s8(ctx, t) {
  bg(ctx, t); head(ctx, t, 8, 330, 76);
  SVC.forEach((s, i) => { const t0 = 23.85 + i * 0.5, k = sp(t, t0, M.SPRING.bouncy); if (k <= 0) return; const y = 680 + i * 150;
    ctx.save(); ctx.globalAlpha = clamp(k * 1.5); ctx.translate((1 - k) * 200, 0); text(ctx, String(i + 1).padStart(2, '0'), 80, y, `500 30px ${U}`, C.amber); ctx.font = `700 96px ${D}`; text(ctx, s, 150, y + 20, `700 96px ${D}`, i % 2 ? C.amber : silver(ctx, 0, y + 20, 0, 96), 'left', -3); ctx.restore(); });
  scan(ctx, 0.05);
}
// 10 · CTA
function s9(ctx, t, I) {
  bg(ctx, t);
  const lk = sp(t, 26.75, M.SPRING.gentle); ctx.globalAlpha = clamp(lk * 1.4); if (I.logo) ctx.drawImage(I.logo, W / 2 - 150, 240, 300, 300); ctx.globalAlpha = 1;
  hud(ctx, 'READY WHEN YOU ARE', W / 2, 600, C.amber, 24, 'center');
  rise(ctx, t, voItems(9, { hi: ['team', 'communicates.'], col: C.amber, br: ['way'] }), { x: 80, y: 740, size: 92, family: D, weight: 700, track: -3, align: 'center', maxW: W - 160 });
  const ck = sp(t, 27.9, M.SPRING.bouncy); if (ck > 0) { ctx.save(); ctx.translate(W / 2, 1080); ctx.scale(lerp(0.7, 1, ck), lerp(0.7, 1, ck)); ctx.fillStyle = C.amber; ctx.beginPath(); ctx.roundRect(-360, -70, 720, 140, 70); ctx.fill();
    text(ctx, '+91 98450 47487', 0, 20, `700 56px ${D}`, '#120c03', 'center', -1); ctx.restore(); }
  const uk = sp(t, 28.4); if (uk > 0) { ctx.globalAlpha = clamp(uk); hud(ctx, 'MRCOMMUNICATIONS.ORG', W / 2, 1230, '#fff', 30, 'center'); hud(ctx, 'SALES · RENTAL · PROGRAMMING', W / 2, 1290, C.muted, 22, 'center'); ctx.globalAlpha = 1; }
  if (t > 29.2) hud(ctx, '— OVER —', W / 2, 1400, C.amber, 26, 'center');
  scan(ctx, 0.05);
}

const SC = [s0, s1, (c, t, I) => channel(c, t, I, 0), (c, t, I) => channel(c, t, I, 1), (c, t, I) => channel(c, t, I, 2), (c, t, I) => channel(c, t, I, 3), s6, s7, s8, s9];
M.film({
  fonts: [`700 100px ${D}`, `400 100px ${D}`, `500 30px ${U}`],
  images: { hero: 'assets/img/hero-radio.jpg', dmr: 'assets/img/product-dmr.jpg', poc: 'assets/img/product-poc.jpg', bodycam: 'assets/img/product-bodycam.jpg', license: 'assets/img/product-license.jpg', logo: 'assets/img/logo-DCbxs-Mr.png' },
  hits: HITS, samples: 8,
  draw(ctx, u, t, I) { SC[clamp(Math.floor(t / 3), 0, 9)](ctx, t, I); },
  post(ctx, u, t) { vignette(ctx, 0.4); grain(ctx, t, 0.07); },
});
