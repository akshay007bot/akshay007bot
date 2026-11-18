// VedRx Tours — "Amara's Journey": a flat-illustration animated story. 30 s, 9:16, 80 bpm (bar = 3 s).
// Fictional, illustrative character. Steps and services are the site's own (vedrxtours.in). No outcome claims.
import * as M from './lib/motion.js';
import { W, H, E, clamp, lerp, B, p, sp, coverAt, shade, text, measure, rise, voItems, grain, vignette, words, hash01 } from './lib/kit.js';

const C = { navy: '#0f1729', night: '#141f3a', teal: '#128271', hi: '#2fc4a5', blue: '#38bdf8', cream: '#f6f1e7', warm: '#ffcc66', ink: '#0f1729', muted: '#8b97ab', day: '#cfeef0' };
const D = 'Display', U = 'UI';
const AMARA = { skin: '#6b4226', hair: '#1b1410', top: '#f2b134', pants: '#3b3f6b', style: 'bun' };
const COORD = { skin: '#b98256', hair: '#141414', top: '#128271', pants: '#0f5f53', style: 'pony' };
const DOC = { skin: '#e0b48a', hair: '#3a2a1e', top: '#ffffff', pants: '#2d3a55', style: 'short' };
const grad = (ctx, x, y, w) => { const g = ctx.createLinearGradient(x, 0, x + Math.max(w, 200), 0); g.addColorStop(0, '#2fd1ad'); g.addColorStop(1, '#38bdf8'); return g; };
const cap = (ctx, t, bar, o = {}) => rise(ctx, t, voItems(bar, { hi: o.hi || [], col: o.col || grad, br: o.br || [] }), { x: 80, y: o.y || 300, size: o.size || 80, family: D, weight: 500, color: o.color || '#fff', maxW: W - 160, align: o.align || 'left' });
const lab = (ctx, s, x, y, color = C.hi, size = 24, align = 'left') => text(ctx, s, x, y, `600 ${size}px ${U}`, color, align, size * 0.12);

const HITS = [
  [B(0.1), 'night', 'swell'], [B(1.4), 'question', 'pop', { pitch: 'C6' }],
  [B(3), 'phone', 'bell', { pitch: 'F6' }],
  ...[0, 1, 2].map((i) => [B(6.4 + i * 0.35), 'paper ' + i, 'whoosh', { len: 0.25, from: 900, to: 2600 }]), [B(8.0), 'reviewed', 'thud'],
  [B(9.1), 'pin', 'pop', { pitch: 'A5' }], ...[0, 1, 2, 3].map((i) => [B(9.9 + i * 0.3), 'hosp ' + i, 'tok', { pitch: ['F5', 'A5', 'C6', 'F6'][i] }]),
  ...[0, 1, 2, 3, 4].map((i) => [B(12.5 + i * 0.35), 'tick ' + i, 'tick']),
  [B(15), 'plane', 'whoosh', { len: 1.2, from: 300, to: 1800 }], ...[0, 1, 2].map((i) => [B(16.3 + i * 0.4), 'check ' + i, 'blip', { pitch: 'C6' }]),
  [B(18.6), 'wave', 'boing', { pitch: 'F5', to: 'C6' }],
  [B(22.6), 'heart', 'bell', { pitch: 'A6' }],
  [B(24.4), 'call', 'blip', { pitch: 'F6' }],
  [B(27), 'cta', 'impact'],
];

// ---------- characters (flat vector, posed procedurally)
function person(ctx, x, y, s, o, t, { mood = 'happy', wave = 0, hold = null, walk = 0, seed = 1, face = 1 } = {}) {
  const bob = Math.sin(t * 3 + seed) * 3 * s, sw = Math.sin(t * 9) * walk;
  ctx.save(); ctx.translate(x, y + bob); ctx.scale(s * face, s); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.fillStyle = 'rgba(0,0,0,.18)'; ctx.beginPath(); ctx.ellipse(0, 0, 60, 12, 0, 0, 7); ctx.fill();
  // legs
  ctx.strokeStyle = o.pants; ctx.lineWidth = 26; ctx.beginPath(); ctx.moveTo(-14, -120); ctx.lineTo(-16 - sw * 18, -8); ctx.moveTo(14, -120); ctx.lineTo(16 + sw * 18, -8); ctx.stroke();
  ctx.fillStyle = '#1b1b1b'; [-16 - sw * 18, 16 + sw * 18].forEach((fx) => { ctx.beginPath(); ctx.ellipse(fx + 6, -6, 18, 9, 0, 0, 7); ctx.fill(); });
  // torso
  ctx.fillStyle = o.top; ctx.beginPath(); ctx.roundRect(-46, -250, 92, 140, [36, 36, 14, 14]); ctx.fill();
  if (o.style === 'short') { ctx.fillStyle = '#9fb7d8'; ctx.fillRect(-10, -248, 20, 70); ctx.strokeStyle = '#cfd8e6'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(-30, -150); ctx.lineTo(-30, -112); ctx.stroke(); }
  if (o === COORD) { ctx.strokeStyle = '#0d5e52'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-18, -248); ctx.lineTo(0, -214); ctx.lineTo(18, -248); ctx.stroke(); }
  // arms
  ctx.strokeStyle = o.top === '#ffffff' ? '#f1f1f1' : o.top; ctx.lineWidth = 22;
  const wa = wave > 0 ? Math.sin(t * 14) * 0.35 * wave : 0;
  ctx.beginPath(); ctx.moveTo(-40, -232); ctx.lineTo(-62, -170 + sw * 10); ctx.lineTo(-58, -120); ctx.stroke();
  if (wave > 0) { ctx.beginPath(); ctx.moveTo(40, -232); ctx.lineTo(80, -270); ctx.lineTo(96 + wa * 60, -330); ctx.stroke(); ctx.fillStyle = o.skin; ctx.beginPath(); ctx.arc(96 + wa * 60, -338, 13, 0, 7); ctx.fill(); }
  else if (hold) { ctx.beginPath(); ctx.moveTo(40, -232); ctx.lineTo(66, -180); ctx.lineTo(34, -170); ctx.stroke(); ctx.fillStyle = o.skin; ctx.beginPath(); ctx.arc(30, -172, 12, 0, 7); ctx.fill(); hold(ctx); }
  else { ctx.beginPath(); ctx.moveTo(40, -232); ctx.lineTo(62, -170 - sw * 10); ctx.lineTo(58, -120); ctx.stroke(); }
  ctx.fillStyle = o.skin; ctx.beginPath(); ctx.arc(-58, -116, 12, 0, 7); ctx.fill(); if (!wave && !hold) { ctx.beginPath(); ctx.arc(58, -116, 12, 0, 7); ctx.fill(); }
  // neck + head
  ctx.fillStyle = o.skin; ctx.fillRect(-12, -276, 24, 30); ctx.beginPath(); ctx.arc(0, -318, 48, 0, 7); ctx.fill();
  ctx.fillStyle = o.hair;
  if (o.style === 'bun') { ctx.beginPath(); ctx.arc(0, -330, 50, Math.PI * 1.05, Math.PI * 1.95); ctx.fill(); ctx.beginPath(); ctx.arc(0, -384, 26, 0, 7); ctx.fill(); }
  if (o.style === 'pony') { ctx.beginPath(); ctx.arc(0, -330, 50, Math.PI * 1.0, Math.PI * 2.0); ctx.fill(); ctx.beginPath(); ctx.ellipse(-50, -300, 14, 44, 0.3, 0, 7); ctx.fill(); }
  if (o.style === 'short') { ctx.beginPath(); ctx.arc(0, -332, 50, Math.PI * 1.0, Math.PI * 2.0); ctx.fill(); }
  const blink = hash01(Math.floor((t + seed) * 2.3), seed) < 0.12; ctx.fillStyle = '#1b1410';
  if (blink) { ctx.fillRect(4, -322, 14, 3); ctx.fillRect(26, -322, 14, 3); } else { ctx.beginPath(); ctx.ellipse(12, -320, 5, 7, 0, 0, 7); ctx.ellipse(32, -320, 5, 7, 0, 0, 7); ctx.fill(); }
  ctx.strokeStyle = '#3a1f12'; ctx.lineWidth = 4; ctx.beginPath();
  if (mood === 'sad') { ctx.arc(22, -286, 12, Math.PI * 1.15, Math.PI * 1.85); ctx.moveTo(4, -338); ctx.lineTo(18, -342); ctx.moveTo(26, -342); ctx.lineTo(40, -338); }
  else ctx.arc(22, -300, 14, Math.PI * 0.15, Math.PI * 0.85);
  ctx.stroke(); ctx.restore();
}
const phoneHold = (ctx) => { ctx.fillStyle = '#222'; ctx.beginPath(); ctx.roundRect(14, -214, 30, 52, 6); ctx.fill(); ctx.fillStyle = '#bfe9ff'; ctx.fillRect(18, -208, 22, 38); };
function bgNight(ctx, t) { const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0b1226'); g.addColorStop(1, '#1a2a4d'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 60; i++) { const a = 0.4 + 0.6 * Math.abs(Math.sin(t * 2 + i)); ctx.fillStyle = `rgba(255,255,255,${a * 0.6})`; ctx.fillRect(hash01(i, 1) * W, hash01(i, 2) * 700, 3, 3); } }
function bgSoft(ctx, top = '#122046', bot = '#0f1729') { const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, top); g.addColorStop(1, bot); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
function floor(ctx, y, col = 'rgba(255,255,255,.06)') { ctx.fillStyle = col; ctx.fillRect(0, y, W, H - y); }
function check(ctx, x, y, s, k, col = C.hi) { if (k <= 0) return; ctx.save(); ctx.translate(x, y); ctx.scale(k * s, k * s); ctx.fillStyle = col; ctx.beginPath(); ctx.arc(0, 0, 24, 0, 7); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-10, 1); ctx.lineTo(-3, 9); ctx.lineTo(11, -8); ctx.stroke(); ctx.restore(); }

// 1 · night, worried
function s0(ctx, t) {
  bgNight(ctx, t); ctx.fillStyle = '#f5e6b8'; ctx.beginPath(); ctx.arc(860, 560, 70, 0, 7); ctx.fill(); ctx.fillStyle = '#0b1226'; ctx.beginPath(); ctx.arc(890, 545, 62, 0, 7); ctx.fill();
  for (let i = 0; i < 9; i++) { const bx = i * 125 - 20, bh = 200 + hash01(i, 4) * 260; ctx.fillStyle = '#0d1630'; ctx.fillRect(bx, 1250 - bh, 110, bh); for (let j = 0; j < 14; j++) if (hash01(i * 30 + j, 6) > 0.55) { ctx.fillStyle = 'rgba(255,204,102,.55)'; ctx.fillRect(bx + 14 + (j % 3) * 32, 1270 - bh + Math.floor(j / 3) * 50, 18, 26); } }
  floor(ctx, 1250, '#1a2440');
  person(ctx, 540, 1560, 1.3, AMARA, t, { mood: 'sad', hold: phoneHold });
  ctx.save(); const k = sp(t, 1.3, M.SPRING.bouncy); if (k > 0) { ctx.translate(720, 900); ctx.scale(k, k); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.ellipse(0, 0, 80, 66, 0, 0, 7); ctx.fill(); ctx.beginPath(); ctx.arc(-70, 70, 14, 0, 7); ctx.arc(-96, 100, 8, 0, 7); ctx.fill(); text(ctx, '?', 0, 32, `600 96px ${D}`, C.navy, 'center'); } ctx.restore();
  cap(ctx, t, 0, { hi: ['Amara.'], br: ['She'], size: 78 });
}
// 2 · finds VedRx on her phone
function s1(ctx, t, I) {
  bgSoft(ctx); const k = sp(t, 2.8, M.SPRING.gentle), z = lerp(0.6, 1, clamp(k)), px = W / 2, py = 1020;
  ctx.save(); ctx.translate(px, py); ctx.scale(z, z); ctx.rotate((1 - clamp(k)) * -0.2);
  ctx.fillStyle = '#111'; ctx.beginPath(); ctx.roundRect(-260, -480, 520, 960, 64); ctx.fill(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(-236, -456, 472, 912, 48); ctx.fill();
  if (I.logo) ctx.drawImage(I.logo, -200, -200, 400, 400 * 280 / 1355);
  text(ctx, 'Better care.', 0, 40, `500 54px ${D}`, C.navy, 'center'); text(ctx, 'Closer than you think.', 0, 104, `500 38px ${D}`, C.teal, 'center');
  ctx.fillStyle = C.teal; ctx.beginPath(); ctx.roundRect(-150, 180, 300, 84, 20); ctx.fill(); text(ctx, 'Find care', 0, 232, `600 32px ${U}`, '#fff', 'center'); ctx.restore();
  for (let i = 0; i < 10; i++) { const a = i / 10 * 6.28 + t, r = 380 + Math.sin(t * 3 + i) * 30, s2 = clamp(sp(t, 3.0 + i * 0.05)); ctx.fillStyle = i % 2 ? C.hi : C.warm; ctx.globalAlpha = s2; ctx.beginPath(); ctx.arc(px + Math.cos(a) * r, py + Math.sin(a) * r * 1.3, 8, 0, 7); ctx.fill(); }
  ctx.globalAlpha = 1;
  const items = words(1).filter((q) => !['R', 'X', 'Tours.'].includes(q.w)).map((q) => ({ w: q.w === 'Ved' ? 'VedRxTours.' : q.w, t: q.t, color: q.w === 'Ved' ? grad : null }));
  rise(ctx, t, items, { x: 80, y: 300, size: 80, family: D, weight: 500, color: '#fff', maxW: W - 160 });
}
// 3 · shares reports
function s2(ctx, t) {
  bgSoft(ctx); floor(ctx, 1500);
  person(ctx, 260, 1660, 1.3, AMARA, t, { mood: 'happy', seed: 2 });
  const fx = 800, fy = 1180; ctx.fillStyle = C.teal; ctx.beginPath(); ctx.roundRect(fx - 150, fy - 110, 300, 220, 18); ctx.fill(); ctx.fillStyle = '#0f6e60'; ctx.beginPath(); ctx.roundRect(fx - 150, fy - 140, 130, 40, [14, 14, 0, 0]); ctx.fill();
  lab(ctx, 'MEDICAL REPORTS', fx, fy + 10, '#fff', 22, 'center');
  [0, 1, 2].forEach((i) => { const k = E.inOutCubic(p(t, 6.1 + i * 0.35, 6.9 + i * 0.35)); if (k <= 0 || k >= 1) return; const x = lerp(330, fx, k), y = lerp(1300, fy, k) - Math.sin(k * Math.PI) * 300;
    ctx.save(); ctx.translate(x, y); ctx.rotate(k * 6 + i); ctx.fillStyle = '#fff'; ctx.fillRect(-50, -64, 100, 128); ctx.fillStyle = '#c9d3e0'; for (let j = 0; j < 5; j++) ctx.fillRect(-36, -44 + j * 20, 72, 6); ctx.restore(); });
  const rk = sp(t, 7.9, M.SPRING.bouncy); if (rk > 0) { ctx.save(); ctx.translate(fx + 110, fy - 110); ctx.rotate(-0.2); ctx.scale(rk, rk); ctx.strokeStyle = C.warm; ctx.lineWidth = 6; ctx.beginPath(); ctx.roundRect(-110, -36, 220, 72, 12); ctx.stroke(); lab(ctx, 'REVIEWED', 0, 10, C.warm, 28, 'center'); ctx.restore(); }
  cap(ctx, t, 2, { hi: ['medical', 'reports.'] });
}
// 4 · compares hospitals in Bengaluru
function s3(ctx, t) {
  bgSoft(ctx, '#0f2a3a', '#0f1729');
  ctx.fillStyle = '#16324a'; ctx.beginPath(); ctx.roundRect(70, 520, W - 140, 940, 40); ctx.fill(); ctx.strokeStyle = 'rgba(47,196,165,.25)'; ctx.lineWidth = 2;
  for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.moveTo(70, 620 + i * 150); ctx.bezierCurveTo(400, 560 + i * 160, 700, 700 + i * 120, W - 70, 600 + i * 150); ctx.stroke(); }
  const pk = sp(t, 8.85, M.SPRING.bouncy), px = W / 2, py = 900 - (1 - clamp(pk)) * 200; ctx.save(); ctx.globalAlpha = clamp(pk * 1.5); ctx.fillStyle = '#ff6b5b'; ctx.beginPath(); ctx.arc(px, py - 60, 44, Math.PI, 0); ctx.lineTo(px, py + 10); ctx.closePath(); ctx.fill(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(px, py - 60, 16, 0, 7); ctx.fill(); ctx.restore();
  lab(ctx, 'BENGALURU', px, py + 60, '#fff', 34, 'center');
  const H4 = [['Manipal', 220, 1180], ['Narayana', 860, 1180], ['Aster CMI', 260, 760], ['SPARSH', 830, 760]];
  H4.forEach(([n, x, y], i) => { const k = sp(t, 9.8 + i * 0.3, M.SPRING.bouncy); if (k <= 0) return; ctx.save(); ctx.translate(x, y); ctx.scale(k, k);
    ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(-70, -110, 140, 120, 10); ctx.fill(); ctx.fillStyle = C.teal; ctx.fillRect(-14, -96, 28, 8); ctx.fillRect(-4, -106, 8, 28); ctx.fillStyle = '#c9d8e6'; for (let j = 0; j < 6; j++) ctx.fillRect(-52 + (j % 3) * 38, -66 + Math.floor(j / 3) * 34, 26, 22);
    ctx.fillStyle = 'rgba(15,23,41,.85)'; const tw = measure(ctx, n, `600 26px ${U}`) + 30; ctx.beginPath(); ctx.roundRect(-tw / 2, 24, tw, 46, 23); ctx.fill(); text(ctx, n, 0, 56, `600 26px ${U}`, '#fff', 'center'); ctx.restore(); });
  cap(ctx, t, 3, { hi: ['Bengaluru.'] });
}
// 5 · personalized estimate (no prices: the site's own list)
function s4(ctx, t) {
  bgSoft(ctx); const k = sp(t, 11.75, M.SPRING.gentle), x = 120, y = 560 + (1 - k) * 500, w = W - 240, h = 880;
  ctx.save(); ctx.globalAlpha = clamp(k * 1.3); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(x, y, w, h, 28); ctx.fill();
  ctx.fillStyle = C.teal; ctx.beginPath(); ctx.roundRect(x, y, w, 130, [28, 28, 0, 0]); ctx.fill(); text(ctx, 'Your personalized', x + 50, y + 62, `500 40px ${D}`, '#fff'); text(ctx, 'estimate', x + 50, y + 108, `500 40px ${D}`, '#bff3e6');
  ['Medical reports', 'Diagnosis', 'Procedure', 'Chosen hospital', 'Length of stay'].forEach((s, i) => { const yy = y + 210 + i * 118; ctx.fillStyle = '#eef3f8'; ctx.beginPath(); ctx.roundRect(x + 40, yy - 44, w - 80, 88, 18); ctx.fill();
    text(ctx, s, x + 80, yy + 12, `600 34px ${U}`, C.ink); check(ctx, x + w - 90, yy, 1, sp(t, 12.5 + i * 0.35, M.SPRING.bouncy)); });
  lab(ctx, 'NO ONE-SIZE-FITS-ALL PRICES', x + w / 2, y + h - 40, C.muted, 20, 'center'); ctx.restore();
  cap(ctx, t, 4, { hi: ['personalized', 'estimate.'] });
}
// 6 · visa, travel, stay
function s5(ctx, t) {
  bgSoft(ctx, '#1b3b6b', '#0f1729');
  ctx.strokeStyle = 'rgba(255,255,255,.12)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(W / 2, 1480, 640, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke();
  const k = E.inOutSine(p(t, 14.9, 17.6)), a = lerp(Math.PI * 1.12, Math.PI * 1.88, k), R = 560, cx = W / 2, cy = 1480, px = cx + Math.cos(a) * R, py = cy + Math.sin(a) * R;
  ctx.setLineDash([14, 14]); ctx.strokeStyle = 'rgba(255,255,255,.6)'; ctx.beginPath(); ctx.arc(cx, cy, R, Math.PI * 1.12, a); ctx.stroke(); ctx.setLineDash([]);
  ctx.save(); ctx.translate(px, py); ctx.rotate(a + Math.PI / 2); ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.ellipse(0, 0, 70, 16, 0, 0, 7); ctx.fill(); ctx.beginPath(); ctx.moveTo(-10, 0); ctx.lineTo(-40, -60); ctx.lineTo(-20, -60); ctx.lineTo(20, 0); ctx.closePath(); ctx.fill(); ctx.beginPath(); ctx.moveTo(-10, 0); ctx.lineTo(-40, 60); ctx.lineTo(-20, 60); ctx.lineTo(20, 0); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.moveTo(-60, 0); ctx.lineTo(-76, -26); ctx.lineTo(-64, -26); ctx.lineTo(-48, 0); ctx.closePath(); ctx.fill(); ctx.restore();
  ['Visa', 'Travel', 'Stay'].forEach((s, i) => { const kk = sp(t, 16.2 + i * 0.4, M.SPRING.bouncy); if (kk <= 0) return; const x = 180 + i * 300, y = 1380;
    ctx.save(); ctx.translate(x, y); ctx.scale(kk, kk); ctx.fillStyle = 'rgba(255,255,255,.1)'; ctx.beginPath(); ctx.roundRect(-120, -70, 240, 140, 24); ctx.fill(); text(ctx, s, 0, -4, `600 38px ${U}`, '#fff', 'center'); check(ctx, 0, 44, 0.8, 1); ctx.restore(); });
  cap(ctx, t, 5, { hi: ['coordinated.'] });
}
// 7 · arrival: coordinator meets her
function s6(ctx, t) {
  bgSoft(ctx, '#e6f4f2', '#bfe3dc'); ctx.fillStyle = '#a9d3cb'; ctx.fillRect(0, 1450, W, H); ctx.fillStyle = '#d4ece7'; for (let i = 0; i < 4; i++) ctx.fillRect(60 + i * 260, 620, 220, 520);
  lab(ctx, 'ARRIVALS · BENGALURU', W / 2, 580, C.teal, 28, 'center');
  const wx = lerp(-160, 330, E.outCubic(p(t, 17.8, 19.2)));
  person(ctx, wx, 1620, 1.05, AMARA, t, { mood: 'happy', walk: t < 19.2 ? 1 : 0, seed: 3 });
  ctx.fillStyle = '#7a5c3a'; ctx.beginPath(); ctx.roundRect(wx - 130, 1500, 70, 100, 10); ctx.fill();
  person(ctx, 770, 1620, 1.05, COORD, t, { mood: 'happy', wave: t > 18.6 ? 1 : 0, seed: 5, face: -1 });
  ctx.save(); ctx.translate(700, 1360); ctx.rotate(-0.05); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(-120, -60, 240, 110, 10); ctx.fill(); text(ctx, 'AMARA', 0, 10, `700 44px ${U}`, C.teal, 'center'); lab(ctx, 'VEDRXTOURS', 0, 40, C.muted, 16, 'center'); ctx.restore();
  cap(ctx, t, 6, { hi: ['care', 'coordinator'], color: C.navy, col: C.teal, size: 78 });
}
// 8 · care planned with the hospital team
function s7(ctx, t) {
  bgSoft(ctx, '#eef6fb', '#d6e9f3'); ctx.fillStyle = '#c2dcea'; ctx.fillRect(0, 1460, W, H);
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(150, 560, W - 300, 560, 20); ctx.fill(); ctx.fillStyle = C.teal; ctx.fillRect(W / 2 - 30, 600, 60, 18); ctx.fillRect(W / 2 - 9, 579, 18, 60);
  ctx.fillStyle = '#cfe3ef'; for (let j = 0; j < 12; j++) ctx.fillRect(200 + (j % 4) * 175, 680 + Math.floor(j / 4) * 140, 120, 90);
  person(ctx, 250, 1640, 0.95, AMARA, t, { mood: 'happy', seed: 4 });
  person(ctx, 540, 1640, 0.95, DOC, t, { mood: 'happy', seed: 6, hold: (c) => { c.fillStyle = '#e9d9b8'; c.fillRect(20, -220, 50, 66); c.fillStyle = '#fff'; c.fillRect(26, -212, 38, 50); } });
  person(ctx, 830, 1640, 0.95, COORD, t, { mood: 'happy', seed: 7, face: -1 });
  const hk = sp(t, 22.6, M.SPRING.bouncy); if (hk > 0) { const hy = 1180 - (t - 22.6) * 40; ctx.save(); ctx.translate(540, hy); ctx.scale(hk, hk); ctx.fillStyle = '#ff6b8a'; ctx.beginPath(); ctx.moveTo(0, 30); ctx.bezierCurveTo(-60, -10, -40, -60, 0, -30); ctx.bezierCurveTo(40, -60, 60, -10, 0, 30); ctx.fill(); ctx.restore(); }
  lab(ctx, 'CARE PLAN', 540, 1530 - 0, C.teal, 20, 'center');
  cap(ctx, t, 7, { hi: ["hospital's", 'team.'], color: C.navy, col: C.teal, size: 76 });
}
// 9 · back home, follow-up call
function s8(ctx, t) {
  bgSoft(ctx, '#ffe9c4', '#ffd79a'); ctx.fillStyle = '#fff3d9'; ctx.beginPath(); ctx.arc(860, 560, 90, 0, 7); ctx.fill(); ctx.fillStyle = '#e8c48a'; ctx.fillRect(0, 1420, W, H);
  ctx.fillStyle = '#8a6a48'; ctx.fillRect(560, 1240, 420, 24); ctx.fillRect(600, 1264, 20, 200); ctx.fillRect(920, 1264, 20, 200);
  ctx.fillStyle = '#2b2b2b'; ctx.beginPath(); ctx.roundRect(610, 940, 320, 220, 14); ctx.fill(); ctx.fillStyle = '#cfeef0'; ctx.fillRect(626, 956, 288, 188); ctx.fillStyle = '#3a3a3a'; ctx.beginPath(); ctx.moveTo(580, 1240); ctx.lineTo(960, 1240); ctx.lineTo(930, 1160); ctx.lineTo(610, 1160); ctx.fill();
  ctx.save(); ctx.beginPath(); ctx.rect(626, 956, 288, 188); ctx.clip(); person(ctx, 770, 1250, 0.55, COORD, t, { mood: 'happy', wave: 1, seed: 8, face: -1 }); ctx.restore();
  const ck = sp(t, 24.4); if (ck > 0) { ctx.globalAlpha = clamp(ck); ctx.fillStyle = C.teal; ctx.beginPath(); ctx.roundRect(640, 880, 260, 46, 23); ctx.fill(); lab(ctx, '● FOLLOW-UP CALL', 770, 912, '#fff', 20, 'center'); ctx.globalAlpha = 1; }
  person(ctx, 330, 1620, 1.05, AMARA, t, { mood: 'happy', wave: t > 24.6 ? 0.6 : 0, seed: 9 });
  cap(ctx, t, 8, { hi: ['follow-up.'], color: C.navy, col: C.teal, size: 76 });
}
// 10 · CTA
function s9(ctx, t, I) {
  bgSoft(ctx); const k = sp(t, 26.75, M.SPRING.gentle);
  ctx.save(); ctx.globalAlpha = clamp(k * 1.3); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.roundRect(80, 540, W - 160, 300, 30); ctx.fill(); if (I.logo) ctx.drawImage(I.logo, 140, 600, W - 280, (W - 280) * 280 / 1355); ctx.restore();
  cap(ctx, t, 9, { y: 360, hi: ['today.'], size: 92, br: ['start'] });
  const c2 = sp(t, 27.8); if (c2 > 0) { ctx.globalAlpha = clamp(c2); text(ctx, '+91 9535699931', W / 2, 1010, `600 60px ${U}`, '#fff', 'center'); text(ctx, 'vedrxtours.in', W / 2, 1090, `600 44px ${U}`, C.hi, 'center');
    ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.beginPath(); ctx.roundRect(140, 1170, W - 280, 110, 20); ctx.fill(); lab(ctx, 'ILLUSTRATIVE STORY. OUTCOMES DEPEND ON', W / 2, 1218, C.muted, 18, 'center'); lab(ctx, 'INDIVIDUAL CIRCUMSTANCES.', W / 2, 1250, C.muted, 18, 'center'); ctx.globalAlpha = 1; }
  person(ctx, 200, 1660, 0.7, AMARA, t, { mood: 'happy', wave: 1, seed: 10 }); person(ctx, 880, 1660, 0.7, COORD, t, { mood: 'happy', wave: 1, seed: 11, face: -1 });
}

const SC = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9];
M.film({
  fonts: [`500 100px ${D}`, `600 40px ${U}`, `700 40px ${U}`],
  images: { logo: 'assets/img/vedrx-logo.png' }, hits: HITS, samples: 8,
  draw(ctx, u, t, I) { SC[clamp(Math.floor(t / 3), 0, 9)](ctx, t, I); },
  post(ctx, u, t) { vignette(ctx, 0.25); grain(ctx, t, 0.04); },
});
