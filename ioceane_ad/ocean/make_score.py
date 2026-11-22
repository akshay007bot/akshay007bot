"""Original score + sound design for "An Ocean of Ideas" (synthesized, royalty-free).

Usage: python3 make_score.py <out.wav>
Deep-ocean drone -> water-drop "plink" + sub boom on impact -> swelling pads and ripple chimes ->
the wave (whoosh) -> a driving pulse under the four service shapes, a shimmer on each morph ->
an airy, expansive bed for the "ocean of ideas" -> a big resolving hit as the logo forms.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter

SR = 44100; DUR = 30.0; N = int(SR * DUR)
mix = np.zeros((N, 2)); rng = np.random.default_rng(5)
O = 1.0
IMPACT, IDEA, WAVE = 3.45 + O, 4.07 + O, 7.7 + O
SHAPES = [8.93 + O, 10.93 + O, 12.6 + O, 14.41 + O]; SHEND = 16.45 + O
STATS, OCEAN, LOGO = 16.59 + O, 20.04 + O, 22.0 + O
f = lambda m: 440 * 2 ** ((m - 69) / 12)
lp = lambda x, a: lfilter([1 - a], [1, -a], x)
tt = lambda d: np.arange(int(d * SR)) / SR


def add(sig, start, pan=0.0, gain=1.0):
    s = int(start * SR)
    if s >= N: return
    sig = sig[: N - s] * gain
    mix[s:s + len(sig), 0] += sig * np.sqrt((1 - pan) / 2)
    mix[s:s + len(sig), 1] += sig * np.sqrt((1 + pan) / 2)


def pad(notes, dur, att=1.5, rel=1.5, bright=.88):
    t = tt(dur); env = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel)
    s = sum(np.sin(2 * np.pi * f(m) * t * (1 + d) + d * 50) for m in notes for d in (-.003, 0, .003))
    return lp(s * env, bright) / len(notes)


def bell(m, d=2.5):
    t = tt(d); fr = f(m)
    return (np.sin(2 * np.pi * fr * t) + .4 * np.sin(2 * np.pi * fr * 2.76 * t) * np.exp(-t * 3) + .2 * np.sin(2 * np.pi * fr * 5.4 * t) * np.exp(-t * 6)) * np.exp(-t * 1.6) * np.minimum(1, t / .002)


def boom(d=3.0, f0=34):
    t = tt(d); return np.sin(2 * np.pi * np.cumsum(f0 + 70 * np.exp(-t * 8)) / SR) * np.exp(-t * 1.4)


def whoosh(d, rev=False):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n); a = .97
    sweep = (t / d) if not rev else (1 - t / d)
    for i in range(0, len(n), 512):  # stepped filter sweep
        k = sweep[i]; out[i:i + 512] = lp(n[i:i + 512], .97 - .8 * k)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 if not rev else (t / d) ** 3
    return out * env


def kick():
    t = tt(.45); return np.sin(2 * np.pi * np.cumsum(40 + 110 * np.exp(-t * 28)) / SR) * np.exp(-t * 6)


def tick():
    t = tt(.06); n = rng.standard_normal(len(t)); n = n - lp(n, .25); return n * np.exp(-t * 70)


# deep ocean drone (whole piece, swelling)
t = np.arange(N) / SR
drone = (np.sin(2 * np.pi * f(33) * t) * .6 + np.sin(2 * np.pi * f(40) * t + 1) * .3) * (.5 + .5 * np.sin(t * .4) ** 2)
surf = rng.standard_normal(N); surf = lp(lp(surf, .985), .985) * 6
denv = np.minimum(1, t / 2) * (1 - .6 * np.clip((t - LOGO) / 3, 0, 1))
mix += ((drone * .10 + surf * .05) * denv)[:, None]

# the drop: rising tone as it falls, then plink + sub boom + splash
add(np.sin(2 * np.pi * np.cumsum(np.linspace(900, 1500, int(2.2 * SR))) / SR) * np.linspace(0, 1, int(2.2 * SR)) ** 3 * .04, IMPACT - 2.2)
pt = tt(.5); plink = np.sin(2 * np.pi * np.cumsum(1400 * np.exp(-pt * 9) + 500) / SR) * np.exp(-pt * 12)
add(plink, IMPACT, gain=.5); add(boom(4, 30), IMPACT, gain=.8)
sp = rng.standard_normal(int(1.2 * SR)); sp = (sp - lp(sp, .4)) * np.exp(-tt(1.2) * 4)
add(sp, IMPACT, pan=-.3, gain=.12); add(sp[::-1].copy() * 0 + sp, IMPACT + .01, pan=.3, gain=.12)

# "one idea" — a single bell, then ripple chimes spreading in stereo
add(bell(81, 4), IDEA, gain=.18)
for i, (m, dt) in enumerate([(76, .5), (79, .9), (84, 1.3), (83, 1.8), (79, 2.2)]):
    add(bell(m, 2.5), IDEA + dt, pan=(-1) ** i * .5, gain=.07)
add(pad([57, 64, 69, 72], WAVE - IDEA + 1.5, att=2.5, rel=1.2), IDEA, gain=.22)

# the wave: big whoosh + boom
add(whoosh(2.6), WAVE - 1.6, gain=.3); add(boom(3, 36), WAVE, gain=.5)

# shapes section: driving pulse 120 bpm in A minor -> F -> C -> G
beat = .5; chords = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]
for si, a in enumerate(SHAPES):
    b = SHAPES[si + 1] if si < 3 else SHEND
    add(pad(chords[si], b - a + .6, att=.2, rel=.5, bright=.8), a, gain=.28)
    add(whoosh(.7, rev=True), a - .7, gain=.18)                       # suck-in before each morph
    for k, m in enumerate([chords[si][0] + 24, chords[si][1] + 24, chords[si][2] + 24]):
        add(bell(m, 1.5), a + k * .06, pan=-.4 + .4 * k, gain=.06)     # shimmer on the morph
    x = a
    while x < b - .05:
        add(kick(), x, gain=.45); add(tick(), x + beat / 2, pan=.3, gain=.25); add(tick(), x + beat / 4 * 3, pan=-.3, gain=.15)
        bt = tt(beat); add(np.sin(2 * np.pi * f(chords[si][0] - 24) * bt) * np.exp(-bt * 3), x, gain=.3)
        x += beat

# stats + ocean of ideas: airy, open major bed with gentle arpeggio
add(pad([60, 67, 72, 76], LOGO - STATS + 1, att=.8, rel=1, bright=.9), STATS, gain=.28)
k = 0; x = STATS
while x < LOGO - .2:
    m = [72, 76, 79, 83, 84, 83, 79, 76][k % 8]; add(bell(m, 1.2), x, pan=.5 * np.sin(k), gain=.05); x += .25; k += 1
for i in range(14):  # distant drop plinks across the ocean of ideas
    s0 = STATS + .4 + i * .42 + rng.uniform(0, .2); add(plink, s0, pan=rng.uniform(-.8, .8), gain=.06 + .04 * rng.random())

# logo: riser into a resolving hit
add(whoosh(2.0), LOGO - 1.2, gain=.25)
add(boom(5, 32), LOGO + .9, gain=.9)
add(pad([48, 55, 64, 67, 72, 76], DUR - LOGO - .5, att=.4, rel=3.5, bright=.9), LOGO + .9, gain=.35)
for i, m in enumerate([72, 76, 79, 84]):
    add(bell(m, 4), LOGO + .9 + i * .09, pan=-.3 + .2 * i, gain=.1)

mix *= np.minimum(1, (DUR - t) / 1.8)[:, None]
mix /= np.max(np.abs(mix)) + 1e-9
wavfile.write(sys.argv[1], SR, (mix * .89 * 32767).astype(np.int16))
print('wrote', sys.argv[1])
