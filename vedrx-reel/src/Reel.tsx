import '@fontsource/playfair-display/600.css';
import '@fontsource/playfair-display/700.css';
import '@fontsource/playfair-display/700-italic.css';
import React from 'react';
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, Easing,
} from 'remotion';
import tl from './timeline.json';

const W = 1080, H = 1920;
const TEAL = '#128271', MINT = '#2dd4bf', SKY = '#0ea5e9', NAVY = '#0f1729';
const SERIF = '"Playfair Display", Georgia, serif';
const SANS = 'Inter, system-ui, sans-serif';
const cl = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const L = Object.fromEntries(tl.lines.map((l) => [l.id, l])) as Record<string, (typeof tl.lines)[number]>;
const wf = (id: string, i: number) => L[id].words[i].f; // absolute frame of word i of a line
const p = (f: number, a: number, d = 14, e = ease) => interpolate(f - a, [0, d], [0, 1], { ...cl, easing: e });

// all cut points (for punch-in + flash)
const CUTS: number[] = [];

// ---------------- media shots ----------------
type Move = 'in' | 'out' | 'left' | 'right' | 'up';
const kb = (t: number, move: Move) => {
  switch (move) {
    case 'in': return `scale(${1.04 + t * 0.14})`;
    case 'out': return `scale(${1.18 - t * 0.14})`;
    case 'left': return `scale(1.16) translateX(${30 - t * 60}px)`;
    case 'right': return `scale(1.16) translateX(${-30 + t * 60}px)`;
    case 'up': return `scale(1.14) translateY(${30 - t * 60}px)`;
  }
};
const Punch: React.FC<{ from: number; children: React.ReactNode }> = ({ from, children }) => {
  const f = useCurrentFrame();
  const k = interpolate(f - from, [0, 7], [1.09, 1], { ...cl, easing: Easing.out(Easing.cubic) });
  return <AbsoluteFill style={{ transform: `scale(${k})` }}>{children}</AbsoluteFill>;
};
const Cover: React.FC<{ src: string; from: number; to: number; move?: Move; pos?: string }> = ({ src, from, to, move = 'in', pos = 'center' }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [from, to], [0, 1], cl);
  return (
    <AbsoluteFill style={{ overflow: 'hidden' }}>
      <Img src={staticFile(src)} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: pos, transform: kb(t, move) }} />
    </AbsoluteFill>
  );
};
const Vid: React.FC<{ src: string; from: number; to: number; start?: number; move?: Move; pos?: string; rate?: number }> = ({ src, from, to, start = 0, move = 'in', pos = 'center', rate = 1 }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [from, to], [0, 1], cl);
  return (
    <AbsoluteFill style={{ overflow: 'hidden' }}>
      <Sequence from={from} durationInFrames={to - from} layout="none">
        <OffthreadVideo src={staticFile(src)} startFrom={start} playbackRate={rate} muted style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: pos, transform: kb(t, move), filter: 'contrast(1.35) saturate(1.4) brightness(0.95)' }} />
      </Sequence>
    </AbsoluteFill>
  );
};
// framed photo card over a blurred version of itself (for lower-res stills)
const Card: React.FC<{ src: string; bg: string; from: number; to: number; h?: number; pos?: string; tilt?: number }> = ({ src, bg, from, to, h = 1180, pos = 'center', tilt = 1 }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [from, to], [0, 1], cl);
  const inn = p(f, from, 12);
  return (
    <AbsoluteFill style={{ overflow: 'hidden' }}>
      <Img src={staticFile(bg)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.15 + t * 0.08})` }} />
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', perspective: 1600 }}>
        <div style={{
          width: 940, height: h, borderRadius: 40, overflow: 'hidden', marginTop: -140,
          boxShadow: '0 60px 120px rgba(0,0,0,0.55), 0 0 0 2px rgba(255,255,255,0.12)',
          transform: `translateY(${(1 - inn) * 80}px) rotateY(${tilt * (-6 + t * 12)}deg) rotateX(${2 - t * 4}deg) scale(${0.94 + inn * 0.06})`,
        }}>
          <Img src={staticFile(src)} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: pos, transform: `scale(${1.08 + t * 0.1})` }} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
const Shot: React.FC<{ from: number; to: number; children: React.ReactNode }> = ({ from, to, children }) => {
  const f = useCurrentFrame();
  if (!CUTS.includes(from)) CUTS.push(from);
  if (f < from || f >= to) return null;
  return <AbsoluteFill><Punch from={from}>{children}</Punch></AbsoluteFill>;
};

// ---------------- graphics ----------------
const Glass: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ background: 'rgba(255,255,255,0.92)', borderRadius: 34, boxShadow: '0 40px 100px rgba(0,0,0,0.45)', color: NAVY, fontFamily: SANS, ...style }}>{children}</div>
);
const MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL'];
const Calendar: React.FC<{ at: number; end: number }> = ({ at, end }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const i = Math.min(MONTHS.length - 1, Math.floor((f - at) / 7));
  const flip = ((f - at) % 7) / 7;
  const inn = p(f, at, 10);
  return (
    <div style={{ position: 'absolute', top: 300, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: inn * interpolate(f, [end - 6, end], [1, 0], cl) }}>
      <Glass style={{ width: 380, overflow: 'hidden', transform: `scale(${0.8 + 0.2 * inn}) rotate(-4deg)` }}>
        <div style={{ background: '#e11d48', color: '#fff', textAlign: 'center', fontWeight: 800, fontSize: 40, padding: '14px 0', letterSpacing: 8 }}>{MONTHS[i]}</div>
        <div style={{ height: 230, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 150, fontWeight: 900, transform: `rotateX(${flip * 50}deg)` }}>{(i + 1) * 4}</div>
        <div style={{ textAlign: 'center', paddingBottom: 18, fontSize: 26, fontWeight: 700, color: '#64748b', letterSpacing: 3 }}>WEEKS WAITING</div>
      </Glass>
    </div>
  );
};
const Receipt: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  const inn = p(f, at, 16);
  const items = ['Consultation', 'Diagnostics', 'Surgery', 'Hospital stay', 'Medicines'];
  const total = Math.floor(interpolate(f, [at + 8, at + 34], [0, 98765], { ...cl, easing: Easing.out(Easing.quad) }));
  return (
    <AbsoluteFill style={{ alignItems: 'center', paddingTop: 230 }}>
      <div style={{ width: 700, background: '#fbfaf7', borderRadius: '10px 10px 0 0', padding: '44px 50px 30px', fontFamily: '"Courier New", monospace', color: '#1f2937', boxShadow: '0 50px 120px rgba(0,0,0,0.6)', transform: `translateY(${(1 - inn) * 900}px) rotate(${3 - inn * 5}deg)`, clipPath: 'polygon(0 0,100% 0,100% 97%,95% 100%,90% 97%,85% 100%,80% 97%,75% 100%,70% 97%,65% 100%,60% 97%,55% 100%,50% 97%,45% 100%,40% 97%,35% 100%,30% 97%,25% 100%,20% 97%,15% 100%,10% 97%,5% 100%,0 97%)' }}>
        <div style={{ textAlign: 'center', fontWeight: 700, fontSize: 34, letterSpacing: 6 }}>MEDICAL BILL</div>
        <div style={{ borderTop: '3px dashed #9ca3af', margin: '22px 0' }} />
        {items.map((it, k) => (
          <div key={it} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 32, margin: '12px 0', opacity: p(f, at + 6 + k * 3, 6) }}>
            <span>{it}</span><span>$ ••••</span>
          </div>
        ))}
        <div style={{ borderTop: '3px dashed #9ca3af', margin: '22px 0' }} />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 44, fontWeight: 700, color: '#dc2626' }}>
          <span>TOTAL</span><span>$ {total.toLocaleString('en-US')}</span>
        </div>
        <div style={{ height: 30 }} />
      </div>
    </AbsoluteFill>
  );
};
const ECG: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  const pts: string[] = [];
  for (let x = 0; x <= 1080; x += 6) {
    const ph = (x % 270) / 270;
    let y = 0;
    if (ph > 0.42 && ph < 0.46) y = -30; else if (ph >= 0.46 && ph < 0.5) y = 160; else if (ph >= 0.5 && ph < 0.55) y = -230; else if (ph >= 0.55 && ph < 0.59) y = 60; else if (ph > 0.7 && ph < 0.8) y = -26 * Math.sin((ph - 0.7) * Math.PI * 10);
    pts.push(`${x},${y}`);
  }
  const reveal = interpolate(f, [at, at + 22], [0, 1080], cl);
  return (
    <svg width={W} height={500} style={{ position: 'absolute', top: 360, left: 0, overflow: 'visible' }}>
      <defs><clipPath id="ecg"><rect x={0} y={-400} width={reveal} height={900} /></clipPath></defs>
      <g clipPath="url(#ecg)" transform="translate(0,250)">
        <polyline points={pts.join(' ')} fill="none" stroke={MINT} strokeWidth={14} opacity={0.25} />
        <polyline points={pts.join(' ')} fill="none" stroke="#eafffb" strokeWidth={5} />
      </g>
      <circle cx={reveal} cy={250} r={14} fill="#fff" opacity={reveal < 1080 ? 1 : 0} style={{ filter: `drop-shadow(0 0 12px ${MINT})` }} />
    </svg>
  );
};
const Scan: React.FC<{ at: number; to: number }> = ({ at, to }) => {
  const f = useCurrentFrame();
  const y = interpolate(f, [at, to], [380, 1420], cl);
  return (
    <>
      <div style={{ position: 'absolute', left: 70, right: 70, top: y, height: 4, background: MINT, boxShadow: `0 0 30px 8px ${MINT}` }} />
      <div style={{ position: 'absolute', left: 70, right: 70, top: y - 160, height: 160, background: `linear-gradient(transparent, rgba(45,212,191,0.25))` }} />
    </>
  );
};
const LogoBadge: React.FC<{ src?: string; text?: string; at: number; w?: number }> = ({ src, text, at, w = 520 }) => {
  const f = useCurrentFrame();
  const k = p(f, at, 10, Easing.out(Easing.back(1.8)));
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ transform: `scale(${0.6 + 0.4 * k})`, opacity: k, marginTop: -160 }}>
        <Glass style={{ padding: '50px 70px', display: 'flex', alignItems: 'center', justifyContent: 'center', minWidth: 560 }}>
          {src ? <Img src={staticFile(src)} style={{ width: w }} /> : <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 110, color: '#ef4444', letterSpacing: -2 }}>{text}<span style={{ fontWeight: 500, fontSize: 52, color: '#334155', marginLeft: 18, letterSpacing: 0 }}>Healthcare</span></div>}
        </Glass>
      </div>
    </AbsoluteFill>
  );
};
const Stamp: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const k = interpolate(f - at, [0, 6], [2.4, 1], { ...cl, easing: Easing.in(Easing.cubic) });
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ marginTop: -200, transform: `scale(${k}) rotate(-10deg)`, opacity: Math.min(1, (f - at) / 3), border: `10px solid ${MINT}`, borderRadius: 26, padding: '18px 46px', color: MINT, fontFamily: SANS, fontWeight: 900, fontSize: 120, letterSpacing: 6, background: 'rgba(15,23,41,0.55)', boxShadow: `0 0 60px rgba(45,212,191,0.5)` }}>HANDLED ✓</div>
    </AbsoluteFill>
  );
};
const MiniTags: React.FC<{ items: [string, number][] }> = ({ items }) => {
  const f = useCurrentFrame();
  return (
    <div style={{ position: 'absolute', top: 250, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 18 }}>
      {items.map(([t, at]) => {
        const k = p(f, at, 10, Easing.out(Easing.back(2)));
        const done = f >= at;
        return <div key={t} style={{ opacity: done ? k : 0.0, transform: `scale(${0.6 + 0.4 * k})`, padding: '16px 30px', borderRadius: 999, background: 'rgba(255,255,255,0.95)', fontFamily: SANS, fontWeight: 800, fontSize: 36, color: NAVY, boxShadow: '0 20px 50px rgba(0,0,0,0.35)' }}><span style={{ color: TEAL }}>✓</span> {t}</div>;
      })}
    </div>
  );
};
const CallUI: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  const k = p(f, at, 14);
  const ring = 1 + 0.06 * Math.sin((f - at) / 2.5);
  return (
    <div style={{ position: 'absolute', top: 220, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: k, transform: `translateY(${(1 - k) * -60}px)` }}>
      <Glass style={{ display: 'flex', alignItems: 'center', gap: 26, padding: '26px 40px', borderRadius: 999 }}>
        <div style={{ width: 84, height: 84, borderRadius: 42, background: `linear-gradient(135deg, ${TEAL}, ${MINT})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 44, transform: `scale(${ring})` }}>📞</div>
        <div>
          <div style={{ fontWeight: 800, fontSize: 38 }}>Follow-up call</div>
          <div style={{ fontWeight: 500, fontSize: 28, color: '#64748b' }}>VedRxTours care team</div>
        </div>
      </Glass>
    </div>
  );
};
const EstimateCard: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  const inn = p(f, at, 16);
  const rows: [string, string][] = [['Treatment', 'Knee replacement'], ['Hospital', 'Matched to your needs'], ['Travel & stay', 'Planned for you'], ['Follow-up', 'Included in your plan']];
  return (
    <AbsoluteFill style={{ alignItems: 'center', paddingTop: 230 }}>
      <Glass style={{ width: 880, padding: '50px 54px', transform: `translateY(${(1 - inn) * 200}px) scale(${0.92 + 0.08 * inn})`, opacity: inn }}>
        <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: 5, color: TEAL }}>YOUR PERSONALISED ESTIMATE</div>
        <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 60, marginTop: 10 }}>Built around you.</div>
        <div style={{ height: 26 }} />
        {rows.map(([a, b], k) => {
          const on = p(f, at + 14 + k * 9, 8);
          return (
            <div key={a} style={{ display: 'flex', alignItems: 'center', gap: 22, padding: '20px 0', borderTop: '2px solid #e2e8f0', opacity: 0.25 + 0.75 * on }}>
              <div style={{ width: 52, height: 52, borderRadius: 26, background: on > 0.5 ? TEAL : '#e2e8f0', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30, fontWeight: 900, transform: `scale(${0.7 + 0.3 * on})` }}>✓</div>
              <div><div style={{ fontSize: 34, fontWeight: 800 }}>{a}</div><div style={{ fontSize: 28, color: '#64748b' }}>{b}</div></div>
            </div>
          );
        })}
        <div style={{ marginTop: 26, padding: '24px 0', textAlign: 'center', borderRadius: 20, background: `linear-gradient(90deg, ${TEAL}, ${SKY})`, color: '#fff', fontSize: 36, fontWeight: 800, opacity: p(f, at + 52, 8) }}>Estimate ready ✓</div>
      </Glass>
    </AbsoluteFill>
  );
};

// ---------------- captions (word-synced, keyword highlight) ----------------
type Chunk = { line: string; idx: number; text: string; hi?: string[]; big?: boolean };
const CHUNKS: Chunk[] = [
  { line: 'l01', idx: 0, text: 'WAITING MONTHS', hi: ['MONTHS'] }, { line: 'l01', idx: 2, text: 'FOR TREATMENT' }, { line: 'l01', idx: 4, text: 'BACK HOME?', hi: ['HOME?'] },
  { line: 'l02', idx: 0, text: 'SCARED OF', }, { line: 'l02', idx: 2, text: 'THE BILLS?', hi: ['BILLS?'], big: true },
  { line: 'l03', idx: 0, text: 'WHAT IF' }, { line: 'l03', idx: 2, text: 'BETTER CARE', hi: ['BETTER'] }, { line: 'l03', idx: 4, text: 'WAS CLOSER', hi: ['CLOSER'] }, { line: 'l03', idx: 6, text: 'THAN YOU THINK?' },
  { line: 'l04', idx: 0, text: 'WELCOME TO' }, { line: 'l04', idx: 2, text: 'INDIA', hi: ['INDIA'], big: true },
  { line: 'l05', idx: 0, text: 'WORLD-CLASS', hi: ['WORLD-CLASS'] }, { line: 'l05', idx: 2, text: 'HOSPITALS' }, { line: 'l05', idx: 3, text: 'APOLLO' }, { line: 'l05', idx: 4, text: 'FORTIS' }, { line: 'l05', idx: 5, text: 'ARTEMIS' }, { line: 'l05', idx: 6, text: 'MAX' },
  { line: 'l06', idx: 0, text: 'HEART SURGERY', hi: ['HEART'] }, { line: 'l06', idx: 2, text: 'KNEE REPLACEMENT', hi: ['KNEE'] },
  { line: 'l07', idx: 0, text: 'CANCER CARE', hi: ['CANCER'] }, { line: 'l07', idx: 2, text: 'IVF', hi: ['IVF'], big: true }, { line: 'l07', idx: 3, text: 'DENTAL', hi: ['DENTAL'], big: true },
  { line: 'l09', idx: 0, text: 'YOU GET ONE' }, { line: 'l09', idx: 3, text: 'DEDICATED', hi: ['DEDICATED'] }, { line: 'l09', idx: 4, text: 'CARE COORDINATOR' },
  { line: 'l10', idx: 0, text: 'VISA', big: true }, { line: 'l10', idx: 1, text: 'FLIGHTS', big: true }, { line: 'l10', idx: 2, text: 'YOUR STAY', big: true },
  { line: 'l11', idx: 0, text: 'EVEN YOUR' }, { line: 'l11', idx: 2, text: 'FOLLOW-UP', hi: ['FOLLOW-UP'] }, { line: 'l11', idx: 4, text: 'AFTER YOU' }, { line: 'l11', idx: 6, text: 'FLY HOME', hi: ['HOME'] },
  { line: 'l12', idx: 0, text: 'A PERSONAL' }, { line: 'l12', idx: 3, text: 'ESTIMATE', hi: ['ESTIMATE'] }, { line: 'l12', idx: 4, text: 'BUILT JUST', }, { line: 'l12', idx: 6, text: 'FOR YOU', hi: ['YOU'] },
];
const chunkTimes = CHUNKS.map((c, i) => {
  const at = wf(c.line, c.idx);
  const nxt = CHUNKS[i + 1];
  const end = nxt && nxt.line === c.line ? wf(nxt.line, nxt.idx) : L[c.line].end + 4;
  return { ...c, at, end };
});
const Captions: React.FC = () => {
  const f = useCurrentFrame();
  const c = chunkTimes.find((c) => f >= c.at && f < c.end);
  if (!c) return null;
  const k = p(f, c.at, 7, Easing.out(Easing.back(2.2)));
  const words = c.text.split(' ');
  return (
    <div style={{ position: 'absolute', top: 1180, left: 50, right: 50, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0 22px', transform: `scale(${0.8 + 0.2 * k})`, opacity: Math.min(1, k * 1.5) }}>
      {words.map((w, i) => {
        const hi = c.hi?.includes(w);
        return (
          <span key={i} style={{
            fontFamily: SANS, fontWeight: 900, fontSize: c.big ? 150 : 104, lineHeight: 1.05, letterSpacing: -2,
            color: hi ? MINT : '#fff', WebkitTextStroke: '3px rgba(0,0,0,0.85)', paintOrder: 'stroke fill',
            textShadow: '0 8px 30px rgba(0,0,0,0.7)',
          }}>{w}</span>
        );
      })}
    </div>
  );
};

// ---------------- the "best part" pattern interrupt ----------------
const BestPart: React.FC<{ at: number; end: number }> = ({ at, end }) => {
  const f = useCurrentFrame();
  const glitch = (f - at) < 6 || (f - wf('l08', 3)) >= 0 && (f - wf('l08', 3)) < 4;
  const k1 = p(f, at, 10); const k2 = p(f, wf('l08', 3), 10, Easing.out(Easing.back(2)));
  const zoom = interpolate(f, [at, end], [1, 1.12], cl);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 45%, #0f3b36 0%, #060b14 70%)`, justifyContent: 'center', alignItems: 'center', transform: `scale(${zoom})` }}>
      <div style={{ textAlign: 'center', transform: glitch ? `translateX(${(f % 2 ? 1 : -1) * 12}px)` : 'none', textShadow: glitch ? '-8px 0 rgba(255,0,80,0.8), 8px 0 rgba(0,240,255,0.8)' : 'none' }}>
        <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontWeight: 700, fontSize: 96, color: '#cbd5e1', opacity: k1, marginTop: -200 }}>But here's</div>
        <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 190, color: '#fff', opacity: k2, transform: `scale(${0.6 + 0.4 * k2})`, lineHeight: 1 }}>the <span style={{ color: MINT }}>best</span><br />part.</div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------- end card ----------------
const EndCard: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  const a = p(f, at, 18);
  const tag = p(f, wf('l13', 2), 14);
  const cta = p(f, wf('l13', 7) + 12, 14);
  const pulse = 1 + 0.03 * Math.sin((f - at) / 6);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(120% 80% at 50% 30%, #13534b 0%, ${NAVY} 70%)`, alignItems: 'center', justifyContent: 'center' }}>
      {/* light sweep */}
      <AbsoluteFill style={{ background: `linear-gradient(105deg, transparent ${interpolate(f - at, [0, 40], [-30, 130])}%, rgba(255,255,255,0.12) ${interpolate(f - at, [0, 40], [-20, 140])}%, transparent ${interpolate(f - at, [0, 40], [-10, 150])}%)` }} />
      <div style={{ marginTop: -260, opacity: a, transform: `scale(${0.9 + 0.1 * a})`, filter: `blur(${(1 - a) * 10}px)` }}>
        <Img src={staticFile('img/logo-light.png')} style={{ width: 880 }} />
      </div>
      <div style={{ marginTop: 50, fontFamily: SERIF, fontStyle: 'italic', fontWeight: 600, fontSize: 64, color: '#e2f7f3', opacity: tag, transform: `translateY(${(1 - tag) * 30}px)`, textAlign: 'center' }}>
        Quality you trust,<br />price you love.
      </div>
      <div style={{ marginTop: 80, opacity: cta, transform: `translateY(${(1 - cta) * 40}px)`, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 26 }}>
        <div style={{ padding: '30px 64px', borderRadius: 999, background: `linear-gradient(90deg, ${TEAL}, ${SKY})`, color: '#fff', fontFamily: SANS, fontWeight: 800, fontSize: 46, transform: `scale(${pulse})`, boxShadow: '0 20px 60px rgba(14,165,233,0.45)' }}>Get your treatment estimate →</div>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 42, color: '#fff', letterSpacing: 2 }}>vedrxtours.in</div>
        <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 34, color: '#a5b4c8' }}>+91 95356 99931</div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------- global overlays ----------------
const Grade: React.FC = () => (
  <>
    <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(5,30,40,0.55) 0%, rgba(0,0,0,0) 28%, rgba(0,0,0,0) 52%, rgba(3,10,20,0.75) 100%)' }} />
    <AbsoluteFill style={{ background: 'radial-gradient(ellipse 85% 70% at 50% 45%, transparent 55%, rgba(0,0,0,0.6) 100%)' }} />
    <AbsoluteFill style={{ background: 'rgba(18,130,113,0.08)', mixBlendMode: 'color' }} />
  </>
);
const Flash: React.FC = () => {
  const f = useCurrentFrame();
  const e = CUTS.reduce((a, c) => (f >= c ? Math.max(a, Math.exp(-(f - c) / 1.6)) : a), 0);
  return <AbsoluteFill style={{ background: '#fff', opacity: e * 0.35, mixBlendMode: 'screen' }} />;
};
const Grain: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ mixBlendMode: 'overlay', opacity: 0.2 }}><Img src={staticFile(`grain/g${f % 8}.png`)} style={{ width: W, height: H }} /></AbsoluteFill>;
};
const GradeUntil: React.FC<{ end: number }> = ({ end }) => { const f = useCurrentFrame(); return f < end ? <Grade /> : null; };
// tiny progress bar at top: an extra "keep watching" cue
const Progress: React.FC = () => {
  const f = useCurrentFrame();
  return <div style={{ position: 'absolute', top: 0, left: 0, height: 8, width: `${(f / tl.total) * 100}%`, background: `linear-gradient(90deg, ${TEAL}, ${MINT})` }} />;
};

export const Reel: React.FC = () => {
  const s = (id: string) => L[id].start;
  const w = wf;
  const T = tl.total;
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {/* l01 waiting months */}
      <Shot from={0} to={s('l02')}><Cover src="broll/waiting.jpg" from={0} to={s('l02')} move="in" pos="40% 50%" /><Calendar at={w('l01', 1)} end={s('l02')} /></Shot>
      {/* l02 bills */}
      <Shot from={s('l02')} to={s('l03')}><Img src={staticFile('bg/waiting.jpg')} style={{ width: W, height: H, objectFit: 'cover' }} /><AbsoluteFill style={{ background: 'rgba(120,0,20,0.25)' }} /><Receipt at={s('l02')} /></Shot>
      {/* l03 closer than you think: plane */}
      <Shot from={s('l03')} to={s('l04')}><Cover src="broll/window_sunset.jpg" from={s('l03')} to={s('l04')} move="up" pos="50% 40%" /></Shot>
      {/* l04 welcome to India */}
      <Shot from={s('l04')} to={s('l05')}><Vid src="broll/taj.mp4" from={s('l04')} to={s('l05')} start={0} move="out" /></Shot>
      {/* l05 hospitals */}
      <Shot from={s('l05')} to={w('l05', 3)}><Card src="broll/apollo.jpg" bg="bg/apollo.jpg" from={s('l05')} to={w('l05', 3)} /></Shot>
      <Shot from={w('l05', 3)} to={w('l05', 4)}><Img src={staticFile('bg/apollo.jpg')} style={{ width: W, height: H }} /><LogoBadge src="img/apollo-logo.png" at={w('l05', 3)} w={360} /></Shot>
      <Shot from={w('l05', 4)} to={w('l05', 5)}><Card src="broll/fortis.jpg" bg="bg/fortis.jpg" from={w('l05', 4)} to={w('l05', 5)} tilt={-1} /><LogoBadge src="img/fortis-logo.png" at={w('l05', 4) + 4} w={420} /></Shot>
      <Shot from={w('l05', 5)} to={w('l05', 6)}><Img src={staticFile('bg/surgery.jpg')} style={{ width: W, height: H }} /><LogoBadge src="img/artemis-logo.png" at={w('l05', 5)} w={440} /></Shot>
      <Shot from={w('l05', 6)} to={s('l06')}><Img src={staticFile('bg/consultation.jpg')} style={{ width: W, height: H }} /><LogoBadge text="MAX" at={w('l05', 6)} /></Shot>
      {/* l06 heart / knee */}
      <Shot from={s('l06')} to={w('l06', 2)}><Cover src="broll/surgery.jpg" from={s('l06')} to={w('l06', 2)} move="left" /><ECG at={s('l06')} /></Shot>
      <Shot from={w('l06', 2)} to={s('l07')}><Card src="broll/knee_xray.jpg" bg="bg/knee_xray.jpg" from={w('l06', 2)} to={s('l07')} /><Scan at={w('l06', 2)} to={s('l07')} /></Shot>
      {/* l07 cancer / IVF / dental */}
      <Shot from={s('l07')} to={w('l07', 2)}><Card src="broll/chemo.jpg" bg="bg/chemo.jpg" from={s('l07')} to={w('l07', 2)} /></Shot>
      <Shot from={w('l07', 2)} to={w('l07', 3)}><Card src="img/ivf_chn.jpg" bg="bg/ivf_chn.jpg" from={w('l07', 2)} to={w('l07', 3)} pos="50% 30%" tilt={-1} /></Shot>
      <Shot from={w('l07', 3)} to={s('l08')}><Card src="broll/dentist.jpg" bg="bg/dentist.jpg" from={w('l07', 3)} to={s('l08')} pos="40% 50%" /></Shot>
      {/* l08 pattern interrupt */}
      <Shot from={s('l08')} to={s('l09')}><BestPart at={s('l08')} end={s('l09')} /></Shot>
      {/* l09 coordinator */}
      <Shot from={s('l09')} to={s('l10')}><Card src="img/consultation.jpg" bg="bg/consultation.jpg" from={s('l09')} to={s('l10')} pos="62% 50%" /></Shot>
      {/* l10 visa / flights / stay / handled */}
      <Shot from={s('l10')} to={w('l10', 1)}><Cover src="broll/passport.jpg" from={s('l10')} to={w('l10', 1)} move="in" /></Shot>
      <Shot from={w('l10', 1)} to={w('l10', 2)}><Vid src="broll/landing.mp4" from={w('l10', 1)} to={w('l10', 2)} start={150} move="in" /></Shot>
      <Shot from={w('l10', 2)} to={s('l11')}><Card src="broll/hotel.jpg" bg="bg/hotel.jpg" from={w('l10', 2)} to={s('l11')} pos="55% 50%" /><MiniTags items={[['Visa', w('l10', 2)], ['Flights', w('l10', 2) + 3], ['Stay', w('l10', 2) + 6]]} /><Stamp at={w('l10', 4)} /></Shot>
      {/* l11 follow-up */}
      <Shot from={s('l11')} to={w('l11', 6)}><Card src="broll/followup.jpg" bg="bg/followup.jpg" from={s('l11')} to={w('l11', 6)} pos="45% 40%" /><CallUI at={s('l11') + 6} /></Shot>
      <Shot from={w('l11', 6)} to={s('l12')}><Vid src="broll/landing.mp4" from={w('l11', 6)} to={s('l12')} start={110} move="in" /></Shot>
      {/* l12 estimate */}
      <Shot from={s('l12')} to={s('l13')}><Img src={staticFile('bg/consultation.jpg')} style={{ width: W, height: H }} /><EstimateCard at={s('l12')} /></Shot>
      {/* l13 end card */}
      <Shot from={s('l13')} to={T}><EndCard at={s('l13')} /></Shot>

      <GradeUntil end={s('l13')} />
      <Captions />
      <Flash />
      <Grain />
      <Progress />

      <Audio src={staticFile('audio/score.wav')} volume={0.5} />
      {tl.lines.map((l) => <Sequence key={l.id} from={l.start} layout="none"><Audio src={staticFile(`audio/${l.id}.wav`)} /></Sequence>)}
    </AbsoluteFill>
  );
};
