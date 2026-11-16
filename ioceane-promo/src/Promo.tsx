import '@fontsource/comfortaa/400.css';
import '@fontsource/comfortaa/700.css';
import React from 'react';
import {
  AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing,
} from 'remotion';

const C = {
  bg: '#0a1020', ink: '#ffffff', muted: '#9aa4b8', blue: '#3c83f6', teal: '#14b8a6', line: 'rgba(255,255,255,0.10)',
};
const HEAD = 'Comfortaa, system-ui, sans-serif';
const BODY = 'Inter, system-ui, sans-serif';
const GRAD = `linear-gradient(90deg, ${C.blue}, ${C.teal})`;
const VO = 15; // voice starts 0.5s into each scene

// scene lengths in frames (voice length + breathing room)
const SCENES = [
  { id: 's1', len: 141 }, { id: 's2', len: 242 }, { id: 's3', len: 285 }, { id: 's4', len: 332 },
  { id: 's5', len: 257 }, { id: 's6', len: 146 }, { id: 's7', len: 234 },
];
export const TOTAL = SCENES.reduce((a, s) => a + s.len, 0);

const ease = Easing.bezier(0.16, 1, 0.3, 1);
const useIn = (delay: number, dur = 22) => {
  const f = useCurrentFrame();
  return interpolate(f - delay, [0, dur], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease });
};
const Rise: React.FC<{ delay?: number; y?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ delay = 0, y = 40, children, style }) => {
  const p = useIn(delay);
  return <div style={{ opacity: p, transform: `translateY(${(1 - p) * y}px)`, filter: `blur(${(1 - p) * 8}px)`, ...style }}>{children}</div>;
};
const GradText: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span style={{ background: GRAD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }}>{children}</span>
);
// scene exit: fade last 10 frames
const SceneFade: React.FC<{ len: number; children: React.ReactNode }> = ({ len, children }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 8, len - 10, len], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};

// ---------- background: navy, drifting glyph columns, glow ----------
const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789アイウエオカキクケコ';
const rand = (i: number) => { const x = Math.sin(i * 9301 + 49297) * 233280; return x - Math.floor(x); };
const Background: React.FC = () => {
  const f = useCurrentFrame();
  const cols = 34;
  return (
    <AbsoluteFill style={{ background: C.bg, overflow: 'hidden' }}>
      <AbsoluteFill style={{ background: `radial-gradient(1100px 700px at ${30 + 10 * Math.sin(f / 90)}% 30%, rgba(60,131,246,0.22), transparent 70%), radial-gradient(900px 600px at ${75 + 8 * Math.cos(f / 110)}% 80%, rgba(20,184,166,0.16), transparent 70%)` }} />
      {Array.from({ length: cols }).map((_, i) => {
        const speed = 0.6 + rand(i) * 1.4;
        const y = ((f * speed + rand(i + 7) * 1400) % 1500) - 400;
        const chars = Array.from({ length: 14 }, (_, k) => GLYPHS[Math.floor(rand(i * 31 + k + Math.floor(f / 12)) * GLYPHS.length)]).join('\n');
        return (
          <div key={i} style={{ position: 'absolute', left: (i / cols) * 1920 + rand(i + 3) * 30, top: y, whiteSpace: 'pre', fontFamily: 'monospace', fontSize: 16, lineHeight: '22px', color: i % 3 === 0 ? 'rgba(20,184,166,0.10)' : 'rgba(120,150,210,0.08)' }}>{chars}</div>
        );
      })}
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at center, transparent 50%, rgba(5,8,16,0.75) 100%)' }} />
    </AbsoluteFill>
  );
};

const Pill: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12, padding: '12px 26px', borderRadius: 999, border: `1px solid rgba(255,255,255,0.18)`, background: 'rgba(255,255,255,0.05)', color: '#dfe6f3', fontFamily: BODY, fontSize: 26, fontWeight: 500 }}>
    <span style={{ width: 10, height: 10, borderRadius: 5, background: GRAD }} />{children}
  </div>
);
const Wrap: React.FC<{ children: React.ReactNode; center?: boolean }> = ({ children, center }) => (
  <AbsoluteFill style={{ padding: '0 160px', justifyContent: 'center', alignItems: center ? 'center' : 'flex-start', textAlign: center ? 'center' : 'left' }}>{children}</AbsoluteFill>
);

// ---------- scenes ----------
const S1: React.FC = () => (
  <Wrap center>
    <Rise delay={VO}><div style={{ fontFamily: HEAD, fontSize: 78, color: C.ink, fontWeight: 700 }}>Your brand deserves more<br />than being seen.</div></Rise>
    <Rise delay={VO + 62} style={{ marginTop: 40 }}><div style={{ fontFamily: HEAD, fontSize: 110, fontWeight: 700 }}><GradText>It deserves to lead.</GradText></div></Rise>
  </Wrap>
);

const S2: React.FC = () => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f - 4, fps, config: { damping: 14 } });
  return (
    <Wrap>
      <div style={{ transform: `scale(${0.8 + 0.2 * s})`, opacity: s, transformOrigin: 'left center', marginBottom: 40 }}>
        <Img src={staticFile('img/logo-white.png')} style={{ height: 120 }} />
      </div>
      <Rise delay={14}><Pill>AI-Driven Creative Agency</Pill></Rise>
      <Rise delay={VO + 30}><div style={{ fontFamily: HEAD, fontSize: 132, fontWeight: 700, color: C.ink, lineHeight: 1.08, marginTop: 36 }}>We Build Brands</div></Rise>
      <Rise delay={VO + 42}><div style={{ fontFamily: HEAD, fontSize: 132, fontWeight: 700, lineHeight: 1.15 }}><GradText>That Dominate</GradText></div></Rise>
      <div style={{ display: 'flex', gap: 22, marginTop: 44 }}>
        {['Creativity', 'AI', 'Strategy', '15+ years'].map((w, i) => (
          <Rise key={w} delay={VO + 80 + i * 14} y={20}>
            <div style={{ fontFamily: BODY, fontSize: 34, color: i === 3 ? C.teal : C.muted, fontWeight: 500, padding: '8px 0' }}>{w}{i < 3 ? <span style={{ color: 'rgba(255,255,255,0.25)', marginLeft: 22 }}>·</span> : null}</div>
          </Rise>
        ))}
      </div>
    </Wrap>
  );
};

const SERVICES = [
  ['Branding & Strategy', 'Memorable identities that resonate'],
  ['Digital Marketing', 'Data-driven campaigns, measurable growth'],
  ['Web Development', 'High-performance sites that convert'],
  ['AI Automation', 'Smart systems that scale your business'],
  ['Video Production', 'Visual stories that captivate'],
  ['Events & Activations', 'Experiences with lasting impact'],
];
const SVC_T = [0, 1.45, 2.85, 4.25, 5.6, 6.9]; // seconds into voice
const S3: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ padding: '110px 140px' }}>
      <Rise delay={0}><div style={{ fontFamily: BODY, letterSpacing: 6, fontSize: 24, color: C.teal, fontWeight: 600 }}>WHAT WE DO</div></Rise>
      <Rise delay={4}><div style={{ fontFamily: HEAD, fontSize: 64, fontWeight: 700, color: C.ink, marginTop: 14 }}>Creative solutions <GradText>powered by intelligence</GradText></div></Rise>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 30, marginTop: 60 }}>
        {SERVICES.map(([t, d], i) => {
          const start = VO + SVC_T[i] * 30;
          const p = interpolate(f - start, [0, 18], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease });
          const active = f >= start && (i === 5 || f < VO + SVC_T[i + 1] * 30);
          return (
            <div key={t} style={{ opacity: 0.15 + 0.85 * p, transform: `translateY(${(1 - p) * 30}px) scale(${active ? 1.03 : 1})`, transition: 'none', height: 250, borderRadius: 28, padding: 40, boxSizing: 'border-box', background: active ? 'rgba(60,131,246,0.12)' : 'rgba(255,255,255,0.04)', border: `1.5px solid ${active ? 'rgba(20,184,166,0.7)' : C.line}`, boxShadow: active ? '0 20px 60px rgba(20,184,166,0.18)' : 'none' }}>
              <div style={{ fontFamily: BODY, fontSize: 24, fontWeight: 700, color: active ? C.teal : '#5d6b85' }}>0{i + 1}</div>
              <div style={{ fontFamily: HEAD, fontSize: 40, fontWeight: 700, color: C.ink, marginTop: 22 }}>{t}</div>
              <div style={{ fontFamily: BODY, fontSize: 26, color: C.muted, marginTop: 14 }}>{d}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Counter: React.FC<{ to: number; start: number; dur?: number; fmt: (n: number) => string }> = ({ to, start, dur = 40, fmt }) => {
  const f = useCurrentFrame();
  const v = interpolate(f - start, [0, dur], [0, to], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
  return <>{fmt(v)}</>;
};

const S4: React.FC = () => {
  const f = useCurrentFrame();
  const draw = interpolate(f, [VO + 100, VO + 250], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
  const pts = Array.from({ length: 13 }, (_, i) => { const x = i / 12; return [x * 760, 330 - (Math.pow(x, 1.7) * 270 + Math.sin(i * 1.7) * 14 + 20)]; });
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ');
  const engines = ['Google', 'ChatGPT', 'Gemini'];
  const stats: [number, (n: number) => string, string, number][] = [
    [954, (n) => `${Math.round(n)}K+`, 'Impressions', VO + 140],
    [10.6, (n) => `${n.toFixed(1)}K`, 'Clicks Delivered', VO + 175],
    [78, (n) => `${Math.round(n)}%`, 'Organic Growth', VO + 205],
  ];
  return (
    <AbsoluteFill style={{ padding: '120px 140px', flexDirection: 'row', gap: 80 }}>
      <div style={{ flex: 1.1 }}>
        <Rise><div style={{ fontFamily: BODY, letterSpacing: 6, fontSize: 24, color: C.teal, fontWeight: 600 }}>SEO & AI SEARCH OPTIMIZATION</div></Rise>
        <Rise delay={6}><div style={{ fontFamily: HEAD, fontSize: 76, fontWeight: 700, color: C.ink, marginTop: 20, lineHeight: 1.15 }}>Rank Higher.<br />Get Found.<br /><GradText>Grow Faster.</GradText></div></Rise>
        <div style={{ display: 'flex', gap: 18, marginTop: 50 }}>
          {engines.map((e, i) => (
            <Rise key={e} delay={VO + 38 + i * 22} y={20}>
              <div style={{ padding: '14px 30px', borderRadius: 16, background: 'rgba(255,255,255,0.06)', border: `1px solid ${C.line}`, fontFamily: BODY, fontSize: 30, fontWeight: 600, color: C.ink }}>{e}</div>
            </Rise>
          ))}
        </div>
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Rise delay={VO + 90}>
          <div style={{ borderRadius: 28, background: 'rgba(255,255,255,0.04)', border: `1px solid ${C.line}`, padding: 40 }}>
            <svg width={760} height={340} style={{ overflow: 'visible' }}>
              <defs>
                <linearGradient id="g" x1="0" x2="1"><stop offset="0" stopColor={C.blue} /><stop offset="1" stopColor={C.teal} /></linearGradient>
                <linearGradient id="fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor={C.teal} stopOpacity={0.3} /><stop offset="1" stopColor={C.teal} stopOpacity={0} /></linearGradient>
                <clipPath id="clip"><rect x={0} y={-20} width={760 * draw} height={400} /></clipPath>
              </defs>
              {[0, 1, 2, 3].map((k) => <line key={k} x1={0} x2={760} y1={30 + k * 100} y2={30 + k * 100} stroke={C.line} />)}
              <g clipPath="url(#clip)">
                <path d={`${d} L760,340 L0,340 Z`} fill="url(#fill)" />
                <path d={d} fill="none" stroke="url(#g)" strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
              </g>
            </svg>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 30 }}>
              {stats.map(([to, fmt, label, st]) => (
                <div key={label}>
                  <div style={{ fontFamily: HEAD, fontSize: 60, fontWeight: 700, color: C.ink }}><Counter to={to} start={st} fmt={fmt} /></div>
                  <div style={{ fontFamily: BODY, fontSize: 24, color: C.muted, marginTop: 6 }}>{label}</div>
                </div>
              ))}
            </div>
          </div>
        </Rise>
      </div>
    </AbsoluteFill>
  );
};

const S5: React.FC = () => {
  const items: [number, string, string, number][] = [
    [150, '+', 'Projects Delivered', VO], [120, '+', 'Happy Clients', VO + 72], [98, '%', 'Client Satisfaction', VO + 140],
  ];
  return (
    <Wrap center>
      <div style={{ display: 'flex', gap: 60, width: '100%' }}>
        {items.map(([to, suf, label, st], i) => (
          <Rise key={label} delay={st - 4} style={{ flex: 1 }}>
            <div style={{ borderRadius: 32, padding: '70px 30px', background: 'rgba(255,255,255,0.04)', border: `1px solid ${C.line}` }}>
              <div style={{ fontFamily: HEAD, fontSize: 170, fontWeight: 700, lineHeight: 1 }}><GradText><Counter to={to} start={st} dur={45} fmt={(n) => `${Math.round(n)}${suf}`} /></GradText></div>
              <div style={{ fontFamily: BODY, fontSize: 36, color: '#dfe6f3', marginTop: 28, fontWeight: 500 }}>{label}</div>
            </div>
          </Rise>
        ))}
      </div>
    </Wrap>
  );
};

const LOGOS = ['ramaiah', 'cadabams-group', 'rambus', 'physio-tattva', 'india-post', 'mystik', 'zen-shastra', 'dr-lohits', 'esmee-clinics', '2050-healthcare', 'organic-express', 'greystone'];
const LogoRow: React.FC<{ list: string[]; dir: 1 | -1 }> = ({ list, dir }) => {
  const f = useCurrentFrame();
  const W = 330 + 36; const total = W * list.length;
  const x = ((f * 3 * dir) % total + total) % total;
  return (
    <div style={{ position: 'relative', height: 170, overflow: 'hidden', width: '100%' }}>
      <div style={{ position: 'absolute', left: -x, display: 'flex', gap: 36 }}>
        {[...list, ...list, ...list].map((l, i) => (
          <div key={i} style={{ width: 330, height: 165, borderRadius: 22, overflow: 'hidden', background: '#f5f5f5', flexShrink: 0 }}>
            <Img src={staticFile(`img/${l}.jpg`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scale(1.05)' }} />
          </div>
        ))}
      </div>
    </div>
  );
};
const S6: React.FC = () => (
  <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 40 }}>
    <Rise><div style={{ fontFamily: BODY, letterSpacing: 6, fontSize: 24, color: C.teal, fontWeight: 600, textAlign: 'center' }}>TRUSTED BY</div></Rise>
    <Rise delay={4}><div style={{ fontFamily: HEAD, fontSize: 72, fontWeight: 700, color: C.ink, textAlign: 'center', marginBottom: 20 }}>Brands We've Helped Grow</div></Rise>
    <Rise delay={10} style={{ width: '100%' }}><LogoRow list={LOGOS.slice(0, 6)} dir={1} /></Rise>
    <Rise delay={16} style={{ width: '100%' }}><LogoRow list={LOGOS.slice(6)} dir={-1} /></Rise>
  </AbsoluteFill>
);

const S7: React.FC = () => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f - (VO + 70), fps, config: { damping: 13 } });
  const glow = 0.5 + 0.5 * Math.sin(f / 8);
  return (
    <Wrap center>
      <Rise delay={VO - 6}><div style={{ fontFamily: HEAD, fontSize: 92, fontWeight: 700, color: C.ink }}>Ready to transform <GradText>your brand?</GradText></div></Rise>
      <Rise delay={VO + 20}><div style={{ fontFamily: BODY, fontSize: 36, color: C.muted, marginTop: 24 }}>Let's create something extraordinary together.</div></Rise>
      <div style={{ marginTop: 60, transform: `scale(${s})`, opacity: s }}>
        <Img src={staticFile('img/logo-white.png')} style={{ height: 150 }} />
      </div>
      <Rise delay={VO + 45} style={{ marginTop: 40 }}>
        <div style={{ display: 'inline-block', padding: '24px 56px', borderRadius: 18, background: GRAD, color: '#fff', fontFamily: BODY, fontSize: 36, fontWeight: 700, boxShadow: `0 20px ${40 + glow * 30}px rgba(60,131,246,${0.35 + glow * 0.2})` }}>Let's Collaborate →</div>
      </Rise>
      <Rise delay={VO + 95} style={{ marginTop: 44 }}>
        <div style={{ fontFamily: BODY, fontSize: 32, color: '#dfe6f3', fontWeight: 500 }}>ioceane.com <span style={{ color: '#4b5874', margin: '0 18px' }}>|</span> +91 90199 31101</div>
        <div style={{ fontFamily: BODY, fontSize: 26, color: C.muted, marginTop: 16 }}>Made with 💙 in Bangalore, India</div>
      </Rise>
    </Wrap>
  );
};

const COMPS: Record<string, React.FC> = { s1: S1, s2: S2, s3: S3, s4: S4, s5: S5, s6: S6, s7: S7 };

export const Promo: React.FC = () => {
  let at = 0;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Background />
      <Audio src={staticFile('audio/music.wav')} volume={(f) => interpolate(f, [0, 30, TOTAL - 60, TOTAL], [0, 0.22, 0.22, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })} />
      {SCENES.map(({ id, len }) => {
        const from = at; at += len; const Comp = COMPS[id];
        return (
          <Sequence key={id} from={from} durationInFrames={len}>
            <SceneFade len={len}><Comp /></SceneFade>
            <Sequence from={VO}><Audio src={staticFile(`audio/${id}.wav`)} volume={1} /></Sequence>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
