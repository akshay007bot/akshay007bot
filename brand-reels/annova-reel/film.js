// ANNOVA 360 — "Sketch to Key". 30 s, 9:16, 80 bpm (bar = 3 s). Plan: docs/shotlist.md
import * as M from './lib/motion.js';
import { W, H, E, clamp, lerp, B, p, sp, logZ, coverAt, shade, text, measure, rise, voItems, grain, vignette, words, hash01 } from './lib/kit.js';

const C = { bg: '#0f0f0f', cream: '#f3f1ee', gold: '#cea359', muted: '#a9adb3' };
const D = 'Display', U = 'UI';
const GOLD = 'rgba(206,163,89,';
const lab = (ctx, s, x, y, color = C.gold, size = 22, align = 'left') => text(ctx, s.toUpperCase(), x, y, `500 ${size}px ${U}`, color, align, size * 0.3);
const head = (ctx, t, bar, o = {}) => rise(ctx, t, voItems(bar, { hi: o.hi || [], it: o.hi || [], col: C.gold, br: o.br || [] }), { x: 84, y: o.y || 360, size: o.size || 104, family: D, weight: 300, lead: 1.04, color: C.cream, shadow: o.shadow ?? 0.5, align: o.align || 'left', maxW: W - 168 });

const HITS = [
  [B(0.05), 'pen', 'riser', { len: 2.6 }],
  [B(3), 'reveal', 'swell'],
  [B(6.35), 'stamp', 'impact'],
  ...[0, 1, 2].map((i) => [B(9.1 + i * 0.5), 'dbd ' + i, 'tok', { pitch: ['D5', 'F5', 'A5'][i] }]),
  ...[0, 1, 2].map((i) => [B(12.4 + i * 0.75), 'dim ' + i, 'tick']),
  [B(15), 'ankuraa', 'whoosh', { len: 0.6, from: 400, to: 1800 }],
  [B(18), 'venus', 'whoosh', { len: 0.6, from: 400, to: 1800 }],
  [B(21), 'residence', 'whoosh', { len: 0.6, from: 400, to: 1800 }],
  [B(26.0), 'key turn', 'click'],
  [B(27), 'cta', 'bell', { pitch: 'D6' }],
];

function bg(ctx) { ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); const r = ctx.createRadialGradient(W / 2, H * 0.4, 0, W / 2, H * 0.4, 1100); r.addColorStop(0, 'rgba(206,163,89,.07)'); r.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = r; ctx.fillRect(0, 0, W, H); }
function gridLines(ctx, a) { ctx.strokeStyle = `${GOLD}${a})`; ctx.lineWidth = 1; for (let x = 0; x < W; x += 60) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); } for (let y = 0; y < H; y += 60) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); } }
// blueprint drawn in bands, each band sketched left→right at its own pace
function blueprint(ctx, I, t, t0, dur, alpha = 1) {
  const n = 24, bh = H / n; ctx.save(); ctx.globalAlpha = alpha;
  for (let i = 0; i < n; i++) { const st = t0 + hash01(i, 5) * dur * 0.45, k = E.inOutSine(p(t, st, st + dur * 0.55)); if (k <= 0) continue;
    const dir = hash01(i, 8) > 0.5; ctx.save(); ctx.beginPath(); ctx.rect(dir ? 0 : W * (1 - k), i * bh, W * k, bh + 1); ctx.clip(); ctx.drawImage(I.bp, 0, 0, W, H); ctx.restore(); }
  ctx.restore();
}
function caption(ctx, t, t0, kind, name, sub) {
  const k = sp(t, t0 + 0.6, M.SPRING.gentle); if (k <= 0) return; ctx.save(); ctx.globalAlpha = clamp(k); ctx.translate(0, (1 - k) * 30);
  ctx.fillStyle = C.gold; ctx.fillRect(84, 1290, 60, 2); lab(ctx, kind, 164, 1298, C.gold, 20);
  text(ctx, name, 84, 1380, `300 70px ${D}`, C.cream); lab(ctx, sub, 86, 1430, C.muted, 18); ctx.restore();
}

// 1 · the sketch
function s0(ctx, t, I) { bg(ctx); gridLines(ctx, 0.05); blueprint(ctx, I, t, -1.3, 3.6); shade(ctx, 0, 620, 0.95, 0, '15,15,15'); head(ctx, t, 0, { hi: ['sketch.'], br: ['begins'] }); }
// 2 · sketch becomes reality
function s1(ctx, t, I) {
  bg(ctx); const k = E.inOutSine(p(t, 2.9, 5.6));
  ctx.save(); ctx.globalAlpha = k; coverAt(ctx, I.villa, 0, 0, W, H, 0.5, 0.5, logZ(1.08, 1.03, k)); ctx.restore();
  blueprint(ctx, I, 99, 0, 1, 1 - E.inCubic(p(t, 3.6, 5.8)));
  shade(ctx, 0, 640, 0.9, 0, '10,10,10'); head(ctx, t, 1, { hi: ['approve...'] });
}
// 3 · is what you get + seal
function s2(ctx, t, I) {
  coverAt(ctx, I.villa, 0, 0, W, H, 0.5, 0.5, logZ(1.03, 1.1, p(t, 6, 9)));
  shade(ctx, 0, 700, 0.9, 0, '10,10,10'); shade(ctx, H - 700, H, 0, 0.85, '10,10,10');
  head(ctx, t, 2, { hi: ['get.'], size: 120 });
  const k = sp(t, 6.3, M.SPRING.bouncy); if (k > 0) { ctx.save(); ctx.translate(W - 280, 1180); ctx.rotate(-0.18 + (1 - k) * 0.4); ctx.scale(lerp(1.8, 1, clamp(k)), lerp(1.8, 1, clamp(k))); ctx.globalAlpha = clamp(k * 1.3);
    ctx.strokeStyle = C.gold; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(0, 0, 150, 0, 7); ctx.stroke(); ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(0, 0, 128, 0, 7); ctx.stroke();
    text(ctx, 'APPROVED', 0, 14, `500 40px ${U}`, C.gold, 'center', 6); lab(ctx, 'ANNOVA 360', 0, 66, C.gold, 16, 'center'); lab(ctx, 'EST. 2014', 0, -44, C.gold, 16, 'center'); ctx.restore(); }
}
// 4 · design build deliver
function s3(ctx, t, I) {
  bg(ctx); ctx.save(); ctx.globalAlpha = 0.18; coverAt(ctx, I.villa, 0, 0, W, H, 0.5, 0.5, 1.15); ctx.restore(); shade(ctx, 0, H, 0.4, 0.8, '15,15,15');
  ['Design', 'Build', 'Deliver'].forEach((s, i) => { const k = sp(t, 8.85 + i * 0.5, M.SPRING.gentle); if (k <= 0) return; const y = 560 + i * 240;
    ctx.save(); ctx.globalAlpha = clamp(k * 1.4); ctx.beginPath(); ctx.rect(0, y - 200, W, 240); ctx.clip();
    text(ctx, s, 84, y + (1 - k) * 160, `${i === 1 ? 'italic ' : ''}300 210px ${D}`, i === 1 ? C.gold : C.cream); ctx.restore();
    ctx.fillStyle = `${GOLD}0.6)`; ctx.fillRect(84, y + 40, (W - 168) * E.outCubic(p(t, 8.9 + i * 0.5, 9.8 + i * 0.5)), 1); });
  head(ctx, t, 3, { y: 1340, size: 80, hi: ['handoffs.'] });
}
// 5 · fixed scope / time / budget as dimension lines
function s4(ctx, t, I) {
  coverAt(ctx, I.villa, 0, 0, W, H, 0.5, 0.5, logZ(1.1, 1.18, p(t, 12, 15))); shade(ctx, 0, H, 0.55, 0.7, '10,10,10');
  head(ctx, t, 4, { y: 340, size: 86, hi: ['budget.'] });
  const w = words(4); const ts = [w[1]?.t ?? 12.4, w[3]?.t ?? 13.1, w[5]?.t ?? 13.8];
  ['Fixed scope', 'Fixed timeline', 'Fixed budget'].forEach((s, i) => { const k = E.outCubic(p(t, ts[i] - 0.1, ts[i] + 0.5)); if (k <= 0) return; const y = 760 + i * 210, x0 = 84, x1 = 84 + (W - 168) * k;
    ctx.strokeStyle = C.gold; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke();
    [x0, x1].forEach((x) => { ctx.beginPath(); ctx.moveTo(x, y - 18); ctx.lineTo(x, y + 18); ctx.moveTo(x - 10, y + 10); ctx.lineTo(x + 10, y - 10); ctx.stroke(); });
    if (k > 0.5) { const a = clamp((k - 0.5) * 3); ctx.globalAlpha = a; ctx.fillStyle = 'rgba(10,10,10,.85)'; const f = `500 24px ${U}`, tw = measure(ctx, s.toUpperCase(), f, 7) + 40; ctx.fillRect(W / 2 - tw / 2, y - 26, tw, 52); lab(ctx, s, W / 2, y + 9, C.gold, 24, 'center'); ctx.globalAlpha = 1; } });
}
// 6-8 · projects
function proj(ctx, t, I, img, t0, move, kind, name, sub, bar) {
  const k = p(t, t0, t0 + 3); const [cx0, cy0, cx1, cy1, z0, z1] = move;
  coverAt(ctx, I[img], 0, 0, W, H, lerp(cx0, cx1, E.inOutSine(k)), lerp(cy0, cy1, E.inOutSine(k)), logZ(z0, z1, k));
  shade(ctx, 0, 820, 0.96, 0, '10,10,10'); shade(ctx, H - 820, H, 0, 0.94, '10,10,10');
  head(ctx, t, bar, { size: 92, hi: bar === 5 ? ['Whitefield.'] : bar === 6 ? ['commercial'] : ['finish.'] }); caption(ctx, t, t0, kind, name, sub);
}
const s5 = (c, t, I) => proj(c, t, I, 'ankuraa', 15, [0.25, 0.5, 0.75, 0.5, 1.0, 1.06], 'Luxury apartments', 'Ankuraa Lotus', 'Whitefield · Pattandur Agrahara · 2022', 5);
const s6 = (c, t, I) => proj(c, t, I, 'venus', 18, [0.5, 0.8, 0.5, 0.25, 1.05, 1.12], 'Commercial', 'Venus Communiti', 'Co-Work, Co-Live & Café · Bengaluru', 6);
const s7 = (c, t, I) => proj(c, t, I, 'living', 21, [0.5, 0.5, 0.55, 0.5, 1.0, 1.18], 'Residential', 'Family Residence', 'Contemporary · Bengaluru', 7);
// 9 · the key
function s8(ctx, t, I) {
  bg(ctx); gridLines(ctx, 0.04);
  const cx = W / 2, cy = 950, k = E.inOutSine(p(t, 23.1, 25.6)), turn = E.inOutCubic(p(t, 25.9, 26.6)) * Math.PI / 2;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(-Math.PI / 4 + turn); ctx.strokeStyle = C.gold; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const path = new Path2D(); path.arc(0, -230, 110, Math.PI / 2, Math.PI / 2 + Math.PI * 2); path.moveTo(0, -120); path.lineTo(0, 300); path.moveTo(0, 200); path.lineTo(70, 200); path.lineTo(70, 240); path.moveTo(0, 270); path.lineTo(50, 270); path.moveTo(-40, -230); path.arc(0, -230, 40, Math.PI, Math.PI * 3);
  ctx.setLineDash([2600]); ctx.lineDashOffset = 2600 * (1 - k); ctx.shadowColor = C.gold; ctx.shadowBlur = 20; ctx.stroke(path); ctx.restore();
  head(ctx, t, 8, { y: 1400, size: 96, hi: ['key.'], align: 'center' });
}
// 10 · CTA
function s9(ctx, t, I) {
  bg(ctx); ctx.save(); ctx.globalAlpha = 0.22; coverAt(ctx, I.villa, 0, 0, W, H, 0.5, 0.5, 1.05); ctx.restore(); shade(ctx, 0, H, 0.6, 0.9, '15,15,15');
  const lk = sp(t, 26.75, M.SPRING.gentle); ctx.globalAlpha = clamp(lk * 1.3);
  if (I.logo) { const sx = 366, sy = 140, sw = 842, sh = 631, w = 520, h = w * sh / sw; ctx.drawImage(I.logo, sx, sy, sw, sh, (W - w) / 2, 330, w, h); }
  ctx.globalAlpha = 1; lab(ctx, 'Est. 2014 · Design • Build • Deliver', W / 2, 800, C.gold, 20, 'center');
  head(ctx, t, 9, { y: 960, size: 92, hi: ['consultation.'], align: 'center' });
  const bk = sp(t, 28.0, M.SPRING.gentle); if (bk > 0) { ctx.save(); ctx.globalAlpha = clamp(bk); ctx.fillStyle = C.gold; ctx.fillRect(W / 2 - 300, 1180, 600, 110); lab(ctx, 'Book consultation', W / 2, 1245, '#141006', 26, 'center');
    text(ctx, '+91 88610 35808', W / 2, 1390, `300 66px ${D}`, C.cream, 'center'); lab(ctx, 'annova360.com  ·  @annova360', W / 2, 1450, C.muted, 20, 'center'); ctx.restore(); }
}

const SC = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9];
M.film({
  fonts: [`300 100px ${D}`, `italic 300 100px ${D}`, `500 30px ${U}`],
  images: { villa: 'assets/img/villa_9x16.jpg', bp: 'assets/img/blueprint.png', ankuraa: 'assets/img/proj-ankuraa-lotus-exterior.jpg', venus: 'assets/img/proj-venus-exterior.jpg', living: 'assets/img/proj-residence-living.jpg', logo: 'assets/img/annova-logo.png' },
  hits: HITS, samples: 8,
  draw(ctx, u, t, I) { SC[clamp(Math.floor(t / 3), 0, 9)](ctx, t, I); },
  post(ctx, u, t) { vignette(ctx, 0.45); grain(ctx, t, 0.06); },
});
