import '@fontsource/comfortaa/400.css';
import '@fontsource/comfortaa/700.css';
import React from 'react';
import {
  AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, Easing, random,
} from 'remotion';
import tl from './timeline.json';

const W = 1080, H = 1920;
const BLUE = '#3c83f6', TEAL = '#14b8a6', ICE = '#bfe9ff';
const HEAD = 'Comfortaa, system-ui, sans-serif';
const BLACK = 'Inter, system-ui, sans-serif';
const GRAD = `linear-gradient(100deg, ${BLUE} 10%, ${TEAL} 60%, ${ICE} 100%)`;
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const cl = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// ---------- hit energy (drives shake, flash, chromatic split) ----------
const energy = (f: number, decay = 7) =>
  tl.hits.reduce((a, h) => (f >= h.f ? a + h.s * Math.exp(-(f - h.f) / decay) : a), 0);
const bigHit = (f: number) =>
  tl.braams.reduce((a, b) => (f >= b ? a + Math.exp(-(f - b) / 14) : a), 0);

const prog = (f: number, start: number, dur = 18, e = ease) => interpolate(f - start, [0, dur], [0, 1], { ...cl, easing: e });

// ---------- WORLD: volumetric light, fog, bokeh dust, glowing ocean lines ----------
const World: React.FC = () => {
  const f = useCurrentFrame();
  const push = interpolate(f, [0, tl.total], [1.0, 1.22]);
  const e = bigHit(f);
  const dust = Array.from({ length: 70 }, (_, i) => {
    const z = random(`z${i}`); // depth 0 far .. 1 near
    const x = random(`x${i}`) * W;
    const y = ((random(`y${i}`) * (H + 400) - f * (0.4 + z * 2.2)) % (H + 400) + (H + 400)) % (H + 400) - 200;
    const size = 2 + z * z * 26;
    return { x: x + Math.sin(f / 50 + i) * 20 * z, y, size, blur: z > 0.75 ? (z - 0.75) * 40 : (1 - z) * 1.5, o: 0.15 + 0.6 * z * (0.6 + 0.4 * Math.sin(f / 20 + i)) };
  });
  const waves = Array.from({ length: 9 }, (_, k) => {
    const amp = 40 + k * 14 + e * 30;
    const pts = Array.from({ length: 41 }, (_, i) => {
      const x = (i / 40) * (W + 200) - 100;
      const y = 1480 + k * 34 + Math.sin(i / 4 + f / (28 - k) + k) * amp * 0.5 + Math.sin(i / 9 - f / 45 + k * 2) * amp * 0.4;
      return `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
    return { d: pts, o: 0.55 - k * 0.05, w: 2.5 - k * 0.18 };
  });
  return (
    <AbsoluteFill style={{ background: 'radial-gradient(120% 80% at 50% 0%, #0d1a35 0%, #050912 55%, #02040a 100%)', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${push})` }}>
        {/* god rays from top */}
        <AbsoluteFill style={{
          background: `conic-gradient(from ${180 + Math.sin(f / 70) * 8}deg at 50% -8%, transparent 0deg, rgba(60,131,246,0.20) 8deg, transparent 16deg, rgba(20,184,166,0.16) 26deg, transparent 34deg, rgba(120,170,255,0.14) 330deg, transparent 338deg, rgba(20,184,166,0.12) 348deg, transparent 356deg)`,
          opacity: 0.55 + e * 0.35,
        }} />
        {/* fog blobs */}
        {[0, 1, 2].map((i) => (
          <div key={i} style={{
            position: 'absolute', width: 1400, height: 900, left: -160 + Math.sin(f / (90 + i * 30) + i) * 200, top: 300 + i * 420 + Math.cos(f / 110 + i) * 80,
            background: `radial-gradient(closest-side, ${i === 1 ? 'rgba(20,184,166,0.16)' : 'rgba(60,131,246,0.16)'}, transparent)`,
          }} />
        ))}
        {/* ocean lines */}
        <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
          <defs>
            <linearGradient id="wg" x1="0" x2="1"><stop offset="0" stopColor={BLUE} stopOpacity={0} /><stop offset="0.3" stopColor={BLUE} /><stop offset="0.7" stopColor={TEAL} /><stop offset="1" stopColor={TEAL} stopOpacity={0} /></linearGradient>
            <filter id="glow"><feGaussianBlur stdDeviation="6" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
          </defs>
          <g>
            {waves.map((w, k) => <path key={`h${k}`} d={w.d} fill="none" stroke="url(#wg)" strokeWidth={w.w * 6} opacity={w.o * 0.18} />)}
            {waves.map((w, k) => <path key={k} d={w.d} fill="none" stroke="url(#wg)" strokeWidth={w.w} opacity={w.o} />)}
          </g>
        </svg>
        {/* bokeh dust */}
        {dust.map((d, i) => (
          <div key={i} style={{ position: 'absolute', left: d.x, top: d.y, width: d.size, height: d.size, borderRadius: '50%', background: `radial-gradient(closest-side, ${i % 4 === 0 ? TEAL : '#9cc4ff'} ${Math.max(0, 70 - d.blur * 6)}%, transparent)`, opacity: d.o }} />
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- overlays ----------
const Grain: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ mixBlendMode: 'overlay', opacity: 0.28, pointerEvents: 'none' }}>
      <Img src={staticFile(`grain/g${f % 8}.png`)} style={{ width: W, height: H, imageRendering: 'pixelated' }} />
    </AbsoluteFill>
  );
};
const Flash: React.FC = () => {
  const f = useCurrentFrame();
  const e = tl.hits.reduce((a, h) => (f >= h.f ? a + h.s * Math.exp(-(f - h.f) / 2.2) : a), 0);
  const b = bigHit(f);
  return (
    <>
      <AbsoluteFill style={{ background: '#dff4ff', opacity: Math.min(0.85, e * 0.55), mixBlendMode: 'screen' }} />
      {/* anamorphic streak on big hits */}
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', opacity: Math.min(1, b) }}>
        <div style={{ width: 2600, height: 10 + b * 30, background: `linear-gradient(90deg, transparent, ${TEAL}, #ffffff, ${BLUE}, transparent)`, filter: 'blur(10px)', transform: `scaleX(${0.4 + (1 - Math.min(1, b)) * 0.8})` }} />
      </AbsoluteFill>
    </>
  );
};
const Vignette: React.FC = () => (
  <AbsoluteFill style={{ background: 'radial-gradient(ellipse 80% 65% at 50% 48%, transparent 55%, rgba(0,0,0,0.85) 100%)', pointerEvents: 'none' }} />
);
const LightLeak: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      {tl.braams.map((b) => {
        const p = interpolate(f, [b - 4, b + 40], [0, 1], cl);
        if (p <= 0 || p >= 1) return null;
        return (
          <AbsoluteFill key={b} style={{ mixBlendMode: 'screen', opacity: Math.sin(p * Math.PI) * 0.8 }}>
            <div style={{ position: 'absolute', width: 1300, height: 2400, left: -900 + p * 1800, top: -200, transform: 'rotate(18deg)', background: `linear-gradient(90deg, transparent, rgba(20,184,166,0.45), rgba(255,200,140,0.3), rgba(60,131,246,0.45), transparent)` }} />
          </AbsoluteFill>
        );
      })}
    </>
  );
};

// ---------- camera: shake + slow drift ----------
const Camera: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  const e = energy(f, 5);
  const x = Math.sin(f * 2.3) * e * 14 + Math.sin(f / 60) * 6;
  const y = Math.cos(f * 2.9) * e * 12;
  const r = Math.sin(f * 1.7) * e * 0.5;
  return <AbsoluteFill style={{ transform: `translate(${x}px, ${y}px) rotate(${r}deg) scale(${1 + e * 0.015})` }}>{children}</AbsoluteFill>;
};

// ---------- text primitives ----------
const chroma = (k: number) => k > 0.02 ? `${-6 * k}px 0 0 rgba(255,40,80,${0.7 * Math.min(1, k)}), ${6 * k}px 0 0 rgba(0,230,255,${0.7 * Math.min(1, k)})` : 'none';

// slam: scales down from big, blur-to-sharp, chromatic split
const Slam: React.FC<{ at: number; children: React.ReactNode; size: number; grad?: boolean; font?: string; track?: number; style?: React.CSSProperties }> = ({ at, children, size, grad, font = BLACK, track = -2, style }) => {
  const f = useCurrentFrame();
  const p = prog(f, at, 10, Easing.out(Easing.exp));
  if (f < at) return null;
  const k = Math.exp(-(f - at) / 5);
  return (
    <div style={{
      fontFamily: font, fontWeight: font === BLACK ? 900 : 700, fontSize: size, letterSpacing: track, lineHeight: 0.95, textAlign: 'center', textTransform: 'uppercase',
      transform: `scale(${1.6 - 0.6 * p})`, opacity: p,
      ...(grad ? { background: GRAD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', filter: `blur(${(1 - p) * 18}px) drop-shadow(0 0 ${30 * k + 12}px rgba(20,184,166,0.55))` } : { color: '#fff', textShadow: `${chroma(k)}, 0 0 40px rgba(120,180,255,0.35)`, filter: `blur(${(1 - p) * 18}px)` }),
      ...style,
    }}>{children}</div>
  );
};
// tracking reveal: letters expand from tight + fade, trailer title style
const Track: React.FC<{ at: number; children: string; size: number; dur?: number; color?: string; style?: React.CSSProperties }> = ({ at, children, size, dur = 60, color = '#e8f1ff', style }) => {
  const f = useCurrentFrame();
  const p = prog(f, at, dur, Easing.out(Easing.cubic));
  return (
    <div style={{ fontFamily: HEAD, fontWeight: 700, fontSize: size, color, textAlign: 'center', letterSpacing: 2 + p * size * 0.35, opacity: interpolate(f - at, [0, 14], [0, 1], cl), filter: `blur(${(1 - p) * 6}px)`, textTransform: 'uppercase', whiteSpace: 'nowrap', ...style }}>{children}</div>
  );
};
// mask reveal: rises from behind a line
const Mask: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ at, children, style }) => {
  const f = useCurrentFrame();
  const p = prog(f, at, 22);
  return <div style={{ overflow: 'hidden', paddingBottom: 12 }}><div style={{ transform: `translateY(${(1 - p) * 110}%)`, ...style }}>{children}</div></div>;
};
const Center: React.FC<{ children: React.ReactNode; gap?: number; style?: React.CSSProperties }> = ({ children, gap = 20, style }) => (
  <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap, padding: '0 70px', ...style }}>{children}</AbsoluteFill>
);
// fade in/out per scene
const Scene: React.FC<{ from: number; to: number; children: React.ReactNode; fadeIn?: number; fadeOut?: number }> = ({ from, to, children, fadeIn = 2, fadeOut = 6 }) => (
  <Sequence from={from} durationInFrames={to - from}>
    <SceneOpacity len={to - from} fi={fadeIn} fo={fadeOut}>{children}</SceneOpacity>
  </Sequence>
);
const SceneOpacity: React.FC<{ len: number; fi: number; fo: number; children: React.ReactNode }> = ({ len, fi, fo, children }) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ opacity: interpolate(f, [0, Math.max(fi, 0.001), len - fo, len], [fi ? 0 : 1, 1, 1, 0], cl) }}>{children}</AbsoluteFill>;
};

// ---------- scenes (frames are absolute timeline frames, converted inside) ----------
const NOISE = ['ADS', 'POSTS', 'REELS', 'CLICKS', 'TRENDS', 'NOISE', 'SCROLL', 'SPAM', 'FEEDS', 'PINGS', 'VIRAL', 'CONTENT', 'ALGORITHM', 'LIKES', 'SALE', '50% OFF', 'SWIPE', 'FOLLOW'];
const S_Noise: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      {Array.from({ length: 46 }, (_, i) => {
        const on = random(`on${i}-${Math.floor(f / 3)}`) > 0.45;
        const z = random(`nz${i}`);
        return (
          <div key={i} style={{ position: 'absolute', left: random(`nx${i}`) * 900, top: 180 + random(`ny${i}`) * 1500, fontFamily: BLACK, fontWeight: 800, fontSize: 24 + z * 70, color: z > 0.6 ? 'rgba(200,220,255,0.35)' : 'rgba(120,150,200,0.25)', filter: `blur(${(1 - z) * 4}px)`, opacity: on ? 1 : 0.15, transform: `translateX(${Math.sin(f / 9 + i) * 8}px)` }}>{NOISE[i % NOISE.length]}</div>
        );
      })}
      <Center gap={6}>
        <Track at={tl.vo.v1 - 4} size={46}>In a world</Track>
        <Slam at={tl.vo.v1 + 26} size={150}>full of</Slam>
        <Slam at={tl.vo.v1 + 34} size={190} style={{ color: '#fff' }}>noise</Slam>
      </Center>
    </>
  );
};
const S_Remember: React.FC = () => {
  const s = tl.vo.v2 - 90;
  return (
    <Center gap={10}>
      <Track at={s - 4} size={42} color="#9fb3d6">only a few brands</Track>
      <Track at={s + 14} size={42} color="#9fb3d6">are</Track>
      <Slam at={s + 44} size={132} grad track={-4}>remem&shy;bered.</Slam>
    </Center>
  );
};
const S_Pillars: React.FC = () => {
  const s = tl.vo.v3 - 200;
  return (
    <Center gap={8}>
      <Track at={s} size={40} color="#9fb3d6">we blend</Track>
      <Slam at={s + 22} size={150}>creativity</Slam>
      <Slam at={s + 52} size={260} grad>AI</Slam>
      <Slam at={s + 82} size={160}>strategy</Slam>
    </Center>
  );
};
const S_Dominate: React.FC = () => {
  const f = useCurrentFrame();
  const s = tl.vo.v4 - 330;
  const k = Math.exp(-Math.max(0, f - (s + 46)) / 6);
  return (
    <Center gap={0}>
      <Mask at={s}><div style={{ fontFamily: HEAD, fontWeight: 700, fontSize: 92, color: '#fff', textAlign: 'center' }}>We build brands</div></Mask>
      <Mask at={s + 14}><div style={{ fontFamily: HEAD, fontWeight: 700, fontSize: 92, color: '#fff', textAlign: 'center' }}>that</div></Mask>
      <div style={{ transform: `scale(${1 + k * 0.08})`, marginTop: 10 }}>
        <Slam at={s + 46} size={176} grad track={-6}>dominate</Slam>
      </div>
    </Center>
  );
};
const SERVICES = [
  ['Branding', '& Strategy'], ['Digital', 'Marketing'], ['Web', 'Development'], ['AI', 'Automation'], ['Video', 'Production'], ['Events', '& Activations'],
];
const S_Services: React.FC = () => {
  const f = useCurrentFrame();
  const i = Math.min(5, Math.floor(f / 20));
  const local = f - i * 20;
  const [a, b] = SERVICES[i];
  const zoom = interpolate(local, [0, 20], [1.0, 1.08]);
  return (
    <Center gap={14} style={{ transform: `scale(${zoom})` }}>
      <div style={{ fontFamily: BLACK, fontWeight: 700, fontSize: 30, letterSpacing: 10, color: TEAL }}>0{i + 1} / 06</div>
      <Slam key={`a${i}`} at={i * 20} size={a.length > 7 ? 150 : 190}>{a}</Slam>
      <Slam key={`b${i}`} at={i * 20 + 3} size={70} grad font={HEAD} track={2}>{b}</Slam>
      <div style={{ width: interpolate(local, [0, 16], [0, 520], { ...cl, easing: ease }), height: 3, background: GRAD, marginTop: 20, boxShadow: `0 0 20px ${TEAL}` }} />
    </Center>
  );
};
const Counter: React.FC<{ at: number; to: number; dec?: number; suf: string; dur?: number }> = ({ at, to, dec = 0, suf, dur = 36 }) => {
  const f = useCurrentFrame();
  const v = interpolate(f - at, [0, dur], [0, to], { ...cl, easing: Easing.out(Easing.cubic) });
  return <>{v.toFixed(dec)}{suf}</>;
};
const S_Search: React.FC = () => {
  const f = useCurrentFrame();
  const s = tl.vo.v5 - 560;
  const eng: [string, number][] = [['Google', s + 26], ['ChatGPT', s + 52], ['Gemini', s + 82]];
  return (
    <Center gap={18}>
      <Track at={s} size={42} color="#9fb3d6">found on</Track>
      {eng.map(([e, at]) => (
        <Slam key={e} at={at} size={150} font={HEAD} track={-2} style={{ textTransform: 'none' }}>{e}</Slam>
      ))}
      <div style={{ display: 'flex', gap: 60, marginTop: 50, opacity: prog(f, s + 100, 14) }}>
        {[[954, 'K+', 'Impressions', 0], [78, '%', 'Organic growth', 0]].map(([to, suf, lab], i) => (
          <div key={i} style={{ textAlign: 'center' }}>
            <div style={{ fontFamily: HEAD, fontWeight: 700, fontSize: 96, background: GRAD, WebkitBackgroundClip: 'text', color: 'transparent' }}><Counter at={s + 100} to={to as number} suf={suf as string} /></div>
            <div style={{ fontFamily: BLACK, fontWeight: 600, fontSize: 26, letterSpacing: 6, color: '#9fb3d6', textTransform: 'uppercase' }}>{lab}</div>
          </div>
        ))}
      </div>
    </Center>
  );
};
const LOGOS = ['ramaiah', 'rambus', 'cadabams-group', 'india-post', 'physio-tattva', 'mystik', '2050-healthcare', 'zen-shastra', 'dr-lohits', 'organic-express', 'esmee-clinics', 'greystone'];
const LogoTunnel: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ perspective: 900, perspectiveOrigin: '50% 50%' }}>
      {Array.from({ length: 24 }, (_, i) => {
        const lane = i % 4; const L = LOGOS[i % LOGOS.length];
        const span = 3400;
        const z = ((f * 14 + i * (span / 24)) % span) - span + 500; // -2900 .. 500
        const x = [-470, 470, -440, 440][lane] + (random(`lx${i}`) - 0.5) * 80;
        const y = [-640, -330, 420, 720][lane] + (random(`ly${i}`) - 0.5) * 120;
        const o = interpolate(z, [-2900, -2000, 200, 500], [0, 0.9, 0.9, 0], cl);
        const blur = Math.min(4, z > 0 ? z / 60 : Math.max(0, (-z - 1600) / 400));
        return (
          <div key={i} style={{ position: 'absolute', left: W / 2 - 160 + x, top: H / 2 - 80 + y, width: 320, height: 160, borderRadius: 20, overflow: 'hidden', transform: `translateZ(${z}px) rotateY(${x > 0 ? -18 : 18}deg)`, opacity: o * 0.85, filter: `blur(${blur}px)`, boxShadow: '0 30px 80px rgba(0,0,0,0.6)' }}>
            <Img src={staticFile(`img/${L}.jpg`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scale(1.05)' }} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
const S_Proof: React.FC = () => {
  const f = useCurrentFrame();
  const s = tl.vo.v6 - 700;
  const dim = interpolate(f, [s + 125, s + 140], [1, 0.25], cl);
  return (
    <>
      <AbsoluteFill style={{ opacity: dim }}><LogoTunnel /></AbsoluteFill>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse 45% 30% at 50% 50%, rgba(3,6,14,0.92), rgba(3,6,14,0.0))' }} />
      <Center gap={10}>
        <div style={{ opacity: interpolate(f, [s + 125, s + 135], [1, 0], cl), display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
          <Slam at={s + 6} size={220} grad font={HEAD} track={-6}><Counter at={s + 6} to={150} suf="+" dur={30} /></Slam>
          <Track at={s + 14} size={40}>projects</Track>
          <div style={{ height: 40 }} />
          <Slam at={s + 74} size={220} grad font={HEAD} track={-6}><Counter at={s + 74} to={120} suf="+" dur={30} /></Slam>
          <Track at={s + 82} size={40}>happy clients</Track>
        </div>
      </Center>
      <Center gap={0}>
        <Track at={s + 128} size={44} color="#9fb3d6">one</Track>
        <Slam at={s + 136} size={156}>obsession.</Slam>
      </Center>
    </>
  );
};
const S_Logo: React.FC = () => {
  const f = useCurrentFrame();
  const s = tl.vo.v7 - 890;
  const rev = prog(f, 0, 40, Easing.out(Easing.cubic));
  const shine = interpolate(f, [10, 50], [-60, 160], cl);
  const flareX = interpolate(f, [0, 70], [-200, 1280], { ...cl, easing: Easing.inOut(Easing.cubic) });
  return (
    <>
      <Center gap={0}>
        {/* halo ring */}
        <div style={{ position: 'absolute', width: 900, height: 900, borderRadius: '50%', border: `2px solid rgba(20,184,166,${0.35 * rev})`, transform: `scale(${0.6 + rev * 0.5})`, boxShadow: `0 0 120px rgba(60,131,246,${0.35 * rev}), inset 0 0 120px rgba(20,184,166,${0.25 * rev})`, top: 380 }} />
        <div style={{ position: 'relative', transform: `scale(${1.25 - 0.25 * rev})`, filter: `blur(${(1 - rev) * 14}px) drop-shadow(0 0 40px rgba(60,131,246,0.6))`, opacity: rev, marginTop: -120 }}>
          <Img src={staticFile('img/logo-white.png')} style={{ width: 780, display: 'block' }} />
          {/* shine sweep masked to logo */}
          <div style={{ position: 'absolute', inset: 0, WebkitMaskImage: `url(${staticFile('img/logo-white.png')})`, WebkitMaskSize: '100% 100%', background: `linear-gradient(105deg, transparent ${shine - 15}%, rgba(255,255,255,0.95) ${shine}%, transparent ${shine + 15}%)` }} />
        </div>
        <div style={{ height: 70 }} />
        <Mask at={s + 36}><div style={{ fontFamily: HEAD, fontWeight: 700, fontSize: 84, color: '#fff', textAlign: 'center' }}>Let's build <span style={{ background: GRAD, WebkitBackgroundClip: 'text', color: 'transparent' }}>yours.</span></div></Mask>
        <div style={{ height: 70 }} />
        <div style={{ opacity: prog(f, s + 70, 16), transform: `translateY(${(1 - prog(f, s + 70, 16)) * 30}px)`, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22 }}>
          <div style={{ padding: '26px 60px', borderRadius: 999, background: GRAD, fontFamily: BLACK, fontWeight: 800, fontSize: 40, color: '#fff', boxShadow: `0 0 ${50 + 20 * Math.sin(f / 7)}px rgba(20,184,166,0.55)` }}>Book a free strategy call</div>
          <div style={{ fontFamily: BLACK, fontWeight: 600, fontSize: 36, color: '#dbe7ff', letterSpacing: 4 }}>ioceane.com</div>
          <div style={{ fontFamily: BLACK, fontWeight: 500, fontSize: 28, color: '#8ea0c2', letterSpacing: 2 }}>AI-Driven Creative Agency · Bangalore</div>
        </div>
      </Center>
      {/* lens flare travelling across */}
      <AbsoluteFill style={{ mixBlendMode: 'screen', pointerEvents: 'none', opacity: interpolate(f, [0, 10, 60, 80], [0, 1, 1, 0], cl) }}>
        <div style={{ position: 'absolute', left: flareX - 150, top: 560, width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(255,255,255,0.95), rgba(120,200,255,0.4) 40%, transparent)' }} />
        <div style={{ position: 'absolute', left: flareX - 900, top: 700, width: 1800, height: 8, background: `linear-gradient(90deg, transparent, rgba(120,200,255,0.9), transparent)`, filter: 'blur(3px)' }} />
        {[0.4, 0.7, 1.3].map((k, i) => (
          <div key={i} style={{ position: 'absolute', left: W / 2 + (W / 2 - flareX) * k - 40 * (i + 1), top: 960 + (960 - 700) * k * 0.4, width: 80 * (i + 1), height: 80 * (i + 1), borderRadius: '50%', border: `2px solid rgba(20,184,166,0.35)`, background: 'rgba(60,131,246,0.08)' }} />
        ))}
      </AbsoluteFill>
    </>
  );
};

export const Reel: React.FC = () => {
  const f = useCurrentFrame();
  const endFade = interpolate(f, [tl.total - 20, tl.total], [1, 0], cl);
  const startFade = interpolate(f, [0, 18], [0, 1], cl);
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      <AbsoluteFill style={{ opacity: Math.min(startFade, endFade) }}>
        <World />
        <Camera>
          <Scene from={0} to={90} fadeOut={1}><S_Noise /></Scene>
          <Scene from={90} to={200} fadeOut={1}><S_Remember /></Scene>
          <Scene from={200} to={330} fadeOut={1}><S_Pillars /></Scene>
          <Scene from={330} to={440} fadeOut={1}><S_Dominate /></Scene>
          <Scene from={440} to={560} fadeIn={0} fadeOut={1}><S_Services /></Scene>
          <Scene from={560} to={700} fadeOut={1}><S_Search /></Scene>
          <Scene from={700} to={872} fadeOut={14}><S_Proof /></Scene>
          <Scene from={890} to={tl.total} fadeIn={0} fadeOut={1}><S_Logo /></Scene>
        </Camera>
        <LightLeak />
        <Flash />
        <Vignette />
        <Grain />
        {/* thin cinematic bars */}
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 70, background: 'linear-gradient(#000, transparent)' }} />
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 70, background: 'linear-gradient(transparent, #000)' }} />
      </AbsoluteFill>
      <Audio src={staticFile('audio/score.wav')} volume={0.55} />
      {Object.entries(tl.vo).map(([k, at]) => (
        <Sequence key={k} from={at}><Audio src={staticFile(`audio/${k}.wav`)} volume={1} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};
