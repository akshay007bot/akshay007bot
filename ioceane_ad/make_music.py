"""Original synthesized music bed for the iOceane ad (no samples, royalty-free).

Usage: python3 make_music.py <seconds> <out.wav>
Bright, modern-corporate feel: 110 bpm, C - G - Am - F, plucked arpeggio, soft pad,
kick + clap from bar 3, riser into the end card, and a final hit.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter

SR = 44100
dur = float(sys.argv[1]); out = sys.argv[2]
N = int(SR * dur)
t = np.arange(N) / SR
mix = np.zeros((N, 2))
rng = np.random.default_rng(3)
BPM = 110; beat = 60 / BPM; bar = 4 * beat
f = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]  # C G Am F
END_HIT = 21.85  # end-card hit (seconds), aligned with the logo reveal


def add(sig, start, pan=0.0, gain=1.0):
    s = int(start * SR)
    if s >= N: return
    sig = sig[: N - s] * gain
    mix[s:s + len(sig), 0] += sig * (1 - pan) / 2 * 2 ** .5
    mix[s:s + len(sig), 1] += sig * (1 + pan) / 2 * 2 ** .5


def lowpass(x, a): return lfilter([1 - a], [1, -a], x)


def pluck(freq, length=0.45):
    tt = np.arange(int(SR * length)) / SR
    env = np.exp(-tt * 9) * np.minimum(1, tt / 0.004)
    return env * (np.sin(2 * np.pi * freq * tt) + 0.3 * np.sin(4 * np.pi * freq * tt) + 0.1 * np.sin(6 * np.pi * freq * tt))


def kick():
    tt = np.arange(int(SR * 0.35)) / SR
    fr = 45 + 110 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 9)


def clap():
    tt = np.arange(int(SR * 0.18)) / SR
    n = rng.standard_normal(len(tt))
    n = n - lowpass(n, 0.6)
    return n * np.exp(-tt * 22) * 0.5


def hat():
    tt = np.arange(int(SR * 0.05)) / SR
    n = rng.standard_normal(len(tt)); n = n - lowpass(n, 0.3)
    return n * np.exp(-tt * 80) * 0.18


nbars = int(dur / bar) + 1
for b in range(nbars):
    c = chords[b % 4]; t0 = b * bar
    if t0 > END_HIT + 0.01 and t0 < END_HIT + bar:  # let the hit breathe
        pass
    # pad
    L = int(bar * SR); tt = np.arange(L) / SR
    env = np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.5)
    pad = sum(np.sin(2 * np.pi * f(m) * (1 + d) * tt) for m in c[:3] for d in (-0.002, 0.002))
    add(lowpass(pad * env, 0.85) * 0.05, t0)
    # sub bass on beats
    for k in range(4):
        tb = np.arange(int(beat * SR)) / SR
        bass = np.sin(2 * np.pi * f(c[0] - 24) * tb) * np.exp(-tb * 3) * np.minimum(1, tb / .01)
        add(bass * 0.32, t0 + k * beat)
    # arpeggio 16ths (enter at bar 1)
    if b >= 1:
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        for k in range(16):
            m = c[pat[k % 8]] + (12 if k % 8 == 3 else 0)
            add(pluck(f(m)), t0 + k * beat / 4, pan=0.35 * np.sin(k), gain=0.09)
    # drums from bar 2
    if b >= 2:
        for k in range(4):
            add(kick(), t0 + k * beat, gain=0.55)
            if k in (1, 3): add(clap(), t0 + k * beat, gain=0.5)
        for k in range(8):
            add(hat(), t0 + k * beat / 2 + beat / 4, pan=0.3)

# riser before the end card
rl = 2.0; tt = np.arange(int(rl * SR)) / SR
noise = rng.standard_normal(len(tt)); noise = noise - lowpass(noise, 0.5 + 0.45 * (1 - tt / rl).mean())
riser = noise * (tt / rl) ** 2 * 0.12 + np.sin(2 * np.pi * (200 * tt + 400 * tt ** 2 / rl)) * (tt / rl) ** 2 * 0.05
add(riser, END_HIT - rl)
# final hit: low boom + bright chord
tt = np.arange(int(3.5 * SR)) / SR
boom = np.sin(2 * np.pi * np.cumsum(40 + 80 * np.exp(-tt * 10)) / SR) * np.exp(-tt * 2.5)
shine = sum(np.sin(2 * np.pi * f(m) * tt) for m in (72, 76, 79, 84)) * np.exp(-tt * 1.2) * 0.12
add(boom * 0.7 + shine, END_HIT)

# master fade out
fade = np.minimum(1, (dur - t) / 2.0)[:, None]
mix *= fade
mix /= np.max(np.abs(mix)) + 1e-9
wavfile.write(out, SR, (mix * 0.89 * 32767).astype(np.int16))
print("wrote", out)
