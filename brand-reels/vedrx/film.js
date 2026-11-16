// Ved Rx Tours brand reel (9:16, 30 s, 80 bpm: one bar = 3 s = one hook).
// Pure function of time: window.seek(t) paints frame t. Plan: docs/shotlist.md.
// Every headline is the voice-over line, revealed word by word as it is spoken (vo.json),
// over the real asset it names.
import * as M from './lib/motion.js';

const { W, H, E, prog, lerp, clamp, springU, springKeys, SPRING, font, layout, text, fill, rrect, crop, hash01 } = M;

const C = { navy: '#0f1729', navy2: '#16213a', teal: '#128271', tealHi: '#2fc4a5', white: '#ffffff', mist: '#c9d3e0', grey: '#65758b', paper: '#f7f9fb' };
const DISPLAY = 'Display', UI = 'UI';
const P = 0.750006, O = 0.0012;                 // beats.json grid
const ub = (sec) => (sec - O) / P;              // seconds -> beats
const SX = 72, SW = W - 144;                    // safe column (9x16)

// Voice-over lines as placed by the VO edit (vo.json); word times are spread by characters.
const VO = [
  { s: 0.189, e: 1.598, t: 'Planning IVF in India?', hi: ['IVF'] },
  { s: 3.189, e: 5.391, t: 'Compare top hospitals, before you decide.', hi: ['hospitals,'] },
  { s: 6.189, e: 8.086, t: 'Bengaluru. Chennai. Delhi. Mumbai.' },
  { s: 9.189, e: 11.07, t: 'Get your personalized treatment estimate.', hi: ['estimate.'] },
  { s: 12.189, e: 14.282, t: 'Visa, travel, stay... we guide you.' },
  { s: 15.189, e: 16.918, t: 'With a dedicated care coordinator.', hi: ['care', 'coordinator.'] },
  { s: 18.189, e: 20.789, t: 'World-class care, and a warm Indian welcome.', hi: ['welcome.'], br: ['care,'] },
  { s: 21.189, e: 23.09, t: 'A simpler journey, step by step.', hi: ['step', 'by', 'step.'], br: ['journey,'] },
  { s: 24.189, e: 26.949, t: "You focus on getting better. We'll help with the journey.", hi: ["We'll", 'help', 'with', 'the', 'journey.'], br: ['better.'] },
  { s: 27.189, e: 29.126, t: 'Start your journey with VedRxTours.' },
];
for (const l of VO) {
  const ws = l.t.split(' '), n = l.t.length;
  let c = 0;
  l.words = ws.map((w) => { const u = ub(l.s + (c / n) * (l.e - l.s)); c += w.length + 1; return { w, u }; });
}
const wordU = (bar, i) => VO[bar].words[i].u;

// Every accent, so sfx.mjs voices it on the same frame.
const HITS = [
  [0, 'hook: Delhi clinic', 'impact'],
  [wordU(0, 1), 'IVF', 'tick'],
  [3.7, 'into logos', 'whoosh', { len: 0.35, from: 500, to: 2200 }],
  [4, 'Apollo', 'pop', { pitch: 'D5' }],
  [5, 'Fortis', 'pop', { pitch: 'F#5' }],
  [6, 'Artemis', 'pop', { pitch: 'A5' }],
  [8, 'city grid', 'thud'],
  ...[0, 1, 2, 3].map((i) => [wordU(2, i), 'city ' + i, 'click']),
  [11.7, 'push out', 'whoosh', { len: 0.4, from: 2400, to: 700 }],
  [12, 'estimate card', 'thud'],
  [15, 'button pulse', 'blip', { pitch: 'A5' }],
  [16, 'support panel', 'click'],
  ...[0, 1, 2].map((i) => [wordU(4, i), 'word ' + i, 'tick']),
  [wordU(4, 3), 'we guide you', 'bell', { pitch: 'D6' }],
  [20, 'coordinator', 'swell'],
  [23.85, 'whip to Taj', 'whoosh', { len: 0.45, from: 700, to: 2600, pan: 0.2 }],
  [28, 'step 01', 'tok', { pitch: 'D5' }],
  [29, 'step 02', 'tok', { pitch: 'E5' }],
  [30, 'step 03', 'tok', { pitch: 'F#5' }],
  [31, 'step 04', 'tok', { pitch: 'A5' }],
  [32, 'couple', 'sub', { len: 0.8 }],
  [36, 'end card', 'impact'],
  [38, 'Find care press', 'bell', { pitch: 'A5' }],
];

// ---------------------------------------------------------------- helpers
// Cover an image so that image point (cx, cy) (0..1) sits at the box centre, zoom >= 1.
function coverAt(ctx, img, x, y, w, h, cx, cy, zoom = 1, radius = 0) {
  const s = Math.max(w / img.width, h / img.height) * zoom;
  const dw = img.width * s, dh = img.height * s;
  let dx = x + w / 2 - cx * dw, dy = y + h / 2 - cy * dh;
  dx = clamp(dx, x + w - dw, x); dy = clamp(dy, y + h - dh, y);
  ctx.save();
  if (radius) rrect(ctx, x, y, w, h, radius); else { ctx.beginPath(); ctx.rect(x, y, w, h); }
  ctx.clip();
  ctx.drawImage(img, dx, dy, dw, dh);
  ctx.restore();
}
const logZoom = (a, b, p) => a * (b / a) ** p;

// Wrap words into lines; returns [{w, x, line}] plus line height.
function wrap(ctx, words, f, maxW, br = []) {
  ctx.font = f;
  const sp = ctx.measureText(' ').width;
  const out = []; let x = 0, line = 0;
  for (const w of words) {
    const ww = ctx.measureText(w.w).width;
    if (x > 0 && x + ww > maxW) { x = 0; line++; }
    out.push({ ...w, x, line, ww }); x += ww + sp;
    if (br.includes(w.w)) { x = 0; line++; }
  }
  return out;
}
// Headline: each word rises out of a mask on the beat it is spoken.
function headline(ctx, u, bar, { x = SX, y, size, color = C.white, hiColor = C.tealHi, maxW = SW, lead = 1.08, shadow = false, exitU = null, align = 'left' }) {
  const f = font(size, 500, DISPLAY);
  const L = wrap(ctx, VO[bar].words, f, maxW, VO[bar].br || []);
  const lines = Math.max(...L.map((w) => w.line)) + 1;
  const lineW = [...Array(lines)].map((_, i) => { const ws = L.filter((w) => w.line === i); const l = ws[ws.length - 1]; return l.x + l.ww; });
  ctx.font = f; ctx.textAlign = 'left';
  const ex = exitU == null ? 0 : E.inCubic(prog(u, exitU, exitU + 0.5));
  for (const w of L) {
    const k = springU(u, w.u - 0.15, SPRING.snappy);
    if (k <= 0) continue;
    const bx = x + w.x + (align === 'center' ? (maxW - lineW[w.line]) / 2 : 0);
    const by = y + w.line * size * lead;
    ctx.save();
    ctx.beginPath(); ctx.rect(bx - 10, by - size * 1.05, w.ww + 40, size * 1.4); ctx.clip();
    const dy = (1 - k) * size * 0.9 - ex * size * 1.2;
    if (shadow) { ctx.shadowColor = 'rgba(5,10,25,0.55)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 4; }
    ctx.fillStyle = (VO[bar].hi || []).includes(w.w) ? hiColor : color;
    ctx.fillText(w.w, bx, by + dy);
    ctx.restore();
  }
  return { bottom: y + (lines - 1) * size * lead, lines };
}
function shade(ctx, y0, y1, a0, a1, rgb = '8,13,28') {
  const g = ctx.createLinearGradient(0, y0, 0, y1);
  g.addColorStop(0, `rgba(${rgb},${a0})`); g.addColorStop(1, `rgba(${rgb},${a1})`);
  ctx.fillStyle = g; ctx.fillRect(0, Math.min(y0, y1), W, Math.abs(y1 - y0));
}
function blurBg(ctx, BL, key, drift = 0) {
  fill(ctx, C.navy);
  const im = BL[key]; if (!im) return;
  ctx.save(); ctx.globalAlpha = 0.55;
  ctx.drawImage(im, -60 + drift * 40, -60, W + 120, H + 120);
  ctx.restore();
  shade(ctx, 0, H, 0.35, 0.75);
}
function card(ctx, x, y, w, h, r = 28) {
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 24;
  rrect(ctx, x, y, w, h, r); ctx.fillStyle = '#fff'; ctx.fill(); ctx.restore();
}
function label(ctx, str, x, y, size = 30, color = C.tealHi, align = 'left') {
  text(ctx, str.toUpperCase(), x, y, font(size, 600, UI), color, align, size * 0.14);
}

// ---------------------------------------------------------------- scenes (u = beats)
const BL = {};   // pre-blurred backgrounds, built once in init

// 1 · 0-4 · "Planning IVF in India?" over the Apollo Fertility reception, Delhi NCR
function s1(ctx, u, I) {
  blurBg(ctx, BL, 'delhi', prog(u, 0, 4));
  const k = springU(u, -0.6, SPRING.gentle);
  const w = SW, h = 760, x = SX, y = 780 + (1 - k) * 120;
  const z = logZoom(1.05, 1.9, E.inOutSine(prog(u, 0, 4.2)));
  card(ctx, x - 8, y - 8, w + 16, h + 16, 34);
  coverAt(ctx, I.delhi, x, y, w, h, 0.5, 0.36, z, 28);
  label(ctx, 'Apollo Fertility · Delhi NCR', x, y + h + 70, 30, C.mist);
  headline(ctx, u, 0, { y: 420, size: 128 });
}
// 2 · 4-8 · "Compare top hospitals, before you decide." over the real partner logos
function s2(ctx, u, I) {
  blurBg(ctx, BL, 'delhi', 1);
  headline(ctx, u, 1, { y: 400, size: 104 });
  const logos = [['apollo', 'Apollo Hospitals'], ['fortis', 'Fortis Healthcare'], ['artemis', 'Artemis Hospital']];
  const ch = 230, gap = 34, y0 = 760;
  logos.forEach(([k, name], i) => {
    const p = springU(u, 4 + i - 0.1, SPRING.snappy);
    if (p <= 0) return;
    const out = E.inCubic(prog(u, 7.55 + i * 0.06, 7.95 + i * 0.06));
    const x = SX + (1 - p) * 0 - out * (W + 100), y = y0 + i * (ch + gap) + (1 - p) * 220;
    ctx.save(); ctx.globalAlpha = clamp(p * 1.4);
    card(ctx, x, y, SW, ch, 26);
    const im = I[k]; const lh = k === 'apollo' ? 170 : 110, lw = (im.width / im.height) * lh;
    ctx.drawImage(im, x + 50, y + (ch - lh) / 2, lw, lh);
    text(ctx, name, x + SW - 48, y + ch / 2 + 14, font(40, 600, UI), C.navy, 'right');
    ctx.restore();
  });
}
// 3 · 8-12 · "Bengaluru. Chennai. Delhi. Mumbai." the four real clinics, one per spoken city
function s3(ctx, u, I) {
  blurBg(ctx, BL, 'chennai', prog(u, 8, 12));
  const t = springU(u, 7.8, SPRING.snappy);
  ctx.save(); ctx.globalAlpha = clamp(t);
  text(ctx, 'IVF care.', SX, 400 + (1 - t) * 60, font(120, 500, DISPLAY), C.white);
  text(ctx, 'Find your city.', SX, 530 + (1 - t) * 60, font(120, 500, DISPLAY), C.tealHi);
  ctx.restore();
  const tiles = [['bengaluru', 'Bengaluru', 0.5, 0.45], ['chennai', 'Chennai', 0.5, 0.4], ['delhi', 'Delhi NCR', 0.5, 0.4], ['mumbai', 'Mumbai', 0.45, 0.5]];
  const g = 24, tw = (SW - g) / 2, th = 400, y0 = 650;
  // push into the grid at the end of the bar
  const pz = logZoom(1, 1.25, E.inCubic(prog(u, 11.4, 12)));
  ctx.save(); M.zoomAbout(ctx, pz, SX + tw / 2, y0 + th / 2);
  tiles.forEach(([k, name, cx, cy], i) => {
    const p = springU(u, wordU(2, i) - 0.1, SPRING.bouncy);
    if (p <= 0) return;
    const x = SX + (i % 2) * (tw + g), y = y0 + Math.floor(i / 2) * (th + g);
    const s = lerp(0.6, 1, p);
    ctx.save(); M.zoomAbout(ctx, s, x + tw / 2, y + th / 2); ctx.globalAlpha = clamp(p * 1.5);
    card(ctx, x, y, tw, th, 24);
    coverAt(ctx, I[k], x, y, tw, th, cx, cy, logZoom(1.15, 1.0, clamp(p)), 24);
    ctx.save(); rrect(ctx, x, y, tw, th, 24); ctx.clip();
    const gr = ctx.createLinearGradient(0, y + th * 0.45, 0, y + th); gr.addColorStop(0, 'rgba(8,13,28,0)'); gr.addColorStop(1, 'rgba(8,13,28,0.85)');
    ctx.fillStyle = gr; ctx.fillRect(x, y, tw, th); ctx.restore();
    text(ctx, name, x + 28, y + th - 34, font(48, 600, UI), C.white);
    ctx.restore();
  });
  ctx.restore();
}
// 4 · 12-16 · "Get your personalized treatment estimate." the site's real estimate card
function s4(ctx, u, I) {
  fill(ctx, C.navy); shade(ctx, 0, H, 0.0, 0.5);
  headline(ctx, u, 3, { y: 400, size: 112 });
  const k = springU(u, 11.2, SPRING.gentle);
  const src = [0, 0, 1764, 945], w = SW, h = (w * 945) / 1764;
  const x = SX, y = 880 + (1 - k) * 700;
  // camera: slow push toward the button
  const z = logZoom(1, 1.32, E.inOutSine(prog(u, 12.5, 15.5)));
  const bx = x + (99 / 1764) * w, by = y + (723 / 945) * h, bw = (700 / 1764) * w, bh = (120 / 945) * h;
  ctx.save(); M.zoomAbout(ctx, z, bx + bw / 2, by + bh / 2);
  card(ctx, x, y, w, h, 22);
  ctx.save(); rrect(ctx, x, y, w, h, 22); ctx.clip(); crop(ctx, I.estimate, src, x, y, w, h); ctx.restore();
  // pulse on the real button
  const pp = prog(u, 15, 16);
  if (pp > 0 && pp < 1) {
    ctx.strokeStyle = `rgba(47,196,165,${(1 - pp) * 0.9})`; ctx.lineWidth = 6;
    const g = pp * 34; rrect(ctx, bx - g, by - g, bw + 2 * g, bh + 2 * g, 14 + g); ctx.stroke();
  }
  ctx.restore();
}
// 5 · 16-20 · "Visa, travel, stay... we guide you." the site's real support list
function s5(ctx, u, I) {
  fill(ctx, C.navy);
  const words = VO[4].words;
  const big = [['Visa?', 0], ['Travel?', 1], ['Stay?', 2]];
  big.forEach(([w, i]) => {
    const k = springU(u, words[i].u - 0.15, SPRING.snappy);
    if (k <= 0) return;
    ctx.save(); ctx.beginPath(); ctx.rect(0, 280 + i * 140, W, 150); ctx.clip();
    text(ctx, w, SX, 400 + i * 140 + (1 - k) * 130, font(130, 500, DISPLAY), C.white);
    ctx.restore();
  });
  const kg = springU(u, words[3].u - 0.15, SPRING.snappy);
  if (kg > 0) { ctx.save(); ctx.beginPath(); ctx.rect(0, 720, W, 160); ctx.clip(); text(ctx, 'We guide you.', SX, 820 + (1 - kg) * 130, font(130, 500, DISPLAY), C.tealHi); ctx.restore(); }
  // panel: real rows from the site (crop of the dark section)
  const k = springU(u, 15.2, SPRING.gentle);
  const src = [2509, 280, 1451, 730], w = SW, h = (w * 730) / 1451, x = SX + (1 - k) * W, y = 960;
  rrect(ctx, x - 4, y - 4, w + 8, h + 8, 26); ctx.fillStyle = '#1b2742'; ctx.fill();
  ctx.save(); rrect(ctx, x, y, w, h, 24); ctx.clip(); crop(ctx, I.support, src, x, y, w, h);
  // the row being talked about lights up: Visa, travel & accommodation (row 2)
  const hl = springU(u, words[0].u - 0.1, SPRING.snappy) - E.inCubic(prog(u, 19.4, 19.9));
  if (hl > 0) {
    const ry = y + ((551 - 280 - 70) / 730) * h, rh = (190 / 730) * h;
    ctx.fillStyle = `rgba(47,196,165,${0.18 * hl})`; ctx.fillRect(x, ry, w * hl, rh);
    ctx.fillStyle = C.tealHi; ctx.fillRect(x, ry, 8, rh * hl);
  }
  ctx.restore();
}
// 6 · 20-24 · "With a dedicated care coordinator." the coordinator, close
function s6(ctx, u, I) {
  const z = logZoom(1.12, 1.42, E.inOutSine(prog(u, 19.6, 24.2)));
  coverAt(ctx, I.consult, 0, 0, W, H, 0.84, 0.42, z);
  shade(ctx, 0, 1050, 0.92, 0); shade(ctx, H - 600, H, 0, 0.6);
  headline(ctx, u, 5, { y: 400, size: 120, shadow: true });
}
// 7 · 24-28 · "World-class care, and a warm Indian welcome." the Taj, dolly down the pool
function s7(ctx, u, I) {
  const p = E.inOutSine(prog(u, 23.8, 28.2));
  coverAt(ctx, I.taj, 0, 0, W, H, 0.5, lerp(0.62, 0.32, p), logZoom(1.0, 1.28, p));
  shade(ctx, 0, 820, 0.78, 0); shade(ctx, H - 500, H, 0, 0.5);
  headline(ctx, u, 6, { y: 400, size: 108, shadow: true });
}
// 8 · 28-32 · "A simpler journey, step by step." the site's four steps, one per beat
function s8(ctx, u, I) {
  blurBg(ctx, BL, 'consult', prog(u, 28, 32));
  headline(ctx, u, 7, { y: 400, size: 110 });
  const steps = [['01', 'Tell us what you need', 'Share your medical needs and what matters to you.'],
    ['02', 'Explore your options', 'Discuss suitable hospitals and an individual care plan.'],
    ['03', 'Plan with confidence', 'Coordinate your documents, travel, and accommodation.'],
    ['04', 'Care beyond arrival', 'Stay connected during treatment and follow-up.']];
  steps.forEach(([n, t, d], i) => {
    const k = springU(u, 28 + i - (i === 0 ? 0.45 : 0.1), SPRING.snappy);
    if (k <= 0) return;
    const y = 820 + i * 175, x = SX + (1 - k) * 260;
    ctx.save(); ctx.globalAlpha = clamp(k * 1.6);
    ctx.fillStyle = 'rgba(255,255,255,0.14)'; ctx.fillRect(SX, y - 70, SW, 2);
    text(ctx, n, x, y + 20, font(84, 500, DISPLAY), C.tealHi);
    text(ctx, t, x + 150, y - 4, font(48, 600, UI), C.white);
    text(ctx, d, x + 150, y + 50, font(31, 600, UI), C.mist);
    ctx.restore();
  });
}
// 9 · 32-36 · "You focus on getting better. We'll help with the journey." pull back on the couple
function s9(ctx, u, I) {
  const p = E.outCubic(prog(u, 31.8, 36));
  coverAt(ctx, I.consult, 0, 0, W, H, lerp(0.6, 0.7, p), 0.45, logZoom(1.55, 1.0, p));
  shade(ctx, 0, 980, 0.85, 0); shade(ctx, H - 500, H, 0, 0.5);
  headline(ctx, u, 8, { y: 380, size: 100, shadow: true });
}
// 10 · 36-40 · CTA end card: real logo, the site's own CTA
function s10(ctx, u, I) {
  fill(ctx, C.paper);
  const lk = springU(u, 35.9, SPRING.gentle);
  const lw = 820, lh = (lw * 280) / 1355;
  ctx.save(); ctx.globalAlpha = clamp(lk * 1.3);
  ctx.drawImage(I.logo, (W - lw) / 2, 470 + (1 - lk) * 60, lw, lh);
  ctx.restore();
  const t1 = springU(u, 36.6, SPRING.snappy), t2 = springU(u, 36.9, SPRING.snappy);
  const fs = 112;
  ctx.save(); ctx.globalAlpha = clamp(t1 * 1.5);
  text(ctx, 'Start your', W / 2, 900 + (1 - t1) * 50, font(fs, 500, DISPLAY), C.navy, 'center');
  ctx.restore();
  ctx.save(); ctx.globalAlpha = clamp(t2 * 1.5);
  ctx.font = font(fs, 500, DISPLAY);
  const a = 'treatment ', b = 'journey';
  const wa = ctx.measureText(a).width, wb = ctx.measureText(b).width, x0 = (W - wa - wb) / 2;
  text(ctx, a, x0, 1030 + (1 - t2) * 50, font(fs, 500, DISPLAY), C.teal);
  text(ctx, b, x0 + wa, 1030 + (1 - t2) * 50, font(fs, 500, DISPLAY), C.navy);
  ctx.restore();
  // button: "Find care", pressed on beat 38
  const bk = springU(u, 37.2, SPRING.bouncy);
  if (bk > 0) {
    const press = 1 - 0.07 * Math.max(0, Math.sin(Math.PI * prog(u, 38, 38.5)));
    const bw = 520, bh = 132, bx = (W - bw) / 2, by = 1150;
    ctx.save(); M.zoomAbout(ctx, lerp(0.7, 1, bk) * press, W / 2, by + bh / 2);
    ctx.shadowColor = 'rgba(18,130,113,0.35)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 18;
    rrect(ctx, bx, by, bw, bh, 18); ctx.fillStyle = C.teal; ctx.fill(); ctx.shadowColor = 'transparent';
    text(ctx, 'Find care', W / 2, by + bh / 2 + 18, font(52, 600, UI), C.white, 'center');
    ctx.restore();
    const rp = prog(u, 38, 39.2);
    if (rp > 0 && rp < 1) { ctx.strokeStyle = `rgba(18,130,113,${(1 - rp) * 0.7})`; ctx.lineWidth = 5; const g = rp * 60; rrect(ctx, bx - g, by - g, bw + 2 * g, bh + 2 * g, 18 + g); ctx.stroke(); }
  }
  const uk = springU(u, 37.6, SPRING.snappy);
  if (uk > 0) { ctx.save(); ctx.globalAlpha = clamp(uk); text(ctx, 'vedrxtours.in', W / 2, 1400, font(50, 600, UI), C.grey, 'center', 1); ctx.restore(); }
}

// Whip: A slides out as B slides in, both on screen (no empty frames).
function whip(ctx, u, u0, len, A, B, I, dir = -1) {
  const p = E.inOutCubic(prog(u, u0, u0 + len));
  if (p <= 0) return A(ctx, u, I);
  if (p >= 1) return B(ctx, u, I);
  ctx.save(); ctx.translate(dir * p * W, 0); A(ctx, u, I); ctx.restore();
  ctx.save(); ctx.translate(dir * (p - 1) * W, 0); B(ctx, u, I); ctx.restore();
}
function rise(ctx, u, u0, len, A, B, I) {
  const p = E.inOutCubic(prog(u, u0, u0 + len));
  if (p <= 0) return A(ctx, u, I);
  if (p >= 1) return B(ctx, u, I);
  ctx.save(); ctx.translate(0, -p * H * 0.35); A(ctx, u, I); ctx.restore();
  ctx.save(); ctx.translate(0, (1 - p) * H); B(ctx, u, I); ctx.restore();
}

M.film({
  fonts: [font(100, 500, DISPLAY), font(40, 600, UI)],
  images: {
    delhi: 'assets/photos/delhi.jpg', bengaluru: 'assets/photos/bengaluru.jpg', chennai: 'assets/photos/chennai.jpg', mumbai: 'assets/photos/mumbai.jpg',
    consult: 'assets/photos/consultation.jpg', taj: 'assets/photos/taj.jpg', logo: 'assets/photos/vedrx-logo.png',
    apollo: 'assets/photos/apollo.png', fortis: 'assets/photos/fortis.png', artemis: 'assets/photos/artemis.png',
    estimate: 'assets/shots/hi_estimate.png', support: 'assets/shots/hi_support.png',
  },
  hits: HITS,
  samples: 10,
  init(ctx, I) {
    for (const k of ['delhi', 'chennai', 'consult']) {
      const c = document.createElement('canvas'); c.width = W / 4; c.height = H / 4;
      const x = c.getContext('2d'); x.filter = 'blur(10px)';
      coverAt(x, I[k], -20, -20, c.width + 40, c.height + 40, 0.5, 0.45, 1.1);
      BL[k] = c;
    }
    const n = document.createElement('canvas'); n.width = 512; n.height = 512;
    const nx = n.getContext('2d'), id = nx.createImageData(512, 512), r = M.mulberry32(7);
    for (let i = 0; i < id.data.length; i += 4) { const v = r() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    nx.putImageData(id, 0, 0); BL.noise = n;
  },
  draw(ctx, u, t, I) {
    if (u < 4) s1(ctx, u, I);
    else if (u < 8) s2(ctx, u, I);
    else if (u < 12) s3(ctx, u, I);
    else if (u < 16) s4(ctx, u, I);
    else if (u < 20) s5(ctx, u, I);
    else if (u < 23.85) s6(ctx, u, I);
    else if (u < 28) whip(ctx, u, 23.85, 0.5, s6, s7, I);
    else if (u < 32) s8(ctx, u, I);
    else if (u < 35.7) s9(ctx, u, I);
    else rise(ctx, u, 35.7, 0.5, s9, s10, I);
  },
  // grain + vignette after motion blur, so the average doesn't erase them
  post(ctx, u, t) {
    const f = Math.floor(t * 24);
    ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.07;
    const ox = Math.floor(hash01(f, 3) * 512), oy = Math.floor(hash01(f, 9) * 512);
    ctx.fillStyle = ctx.createPattern(BL.noise, 'repeat'); ctx.translate(-ox, -oy); ctx.fillRect(0, 0, W + 512, H + 512);
    ctx.restore();
    if (u < 35.8) {
      const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.75);
      g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.35)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    }
  },
});
