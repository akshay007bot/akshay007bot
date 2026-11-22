"""Original score + sound design for the live-action iOceane commercial (synthesized, royalty-free).

Usage: python3 make_score.py <out.wav>
Arc (seconds, video time): 0-5.25 rain + lonely piano (night café), 5.25 heartbeat pulse as the
team appears, 9.1 riser, 11.1 drop with full groove + notification pings, 22.2 final hit on the
logo, then resolve and fade.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter

SR = 44100; DUR = 31.0; N = int(SR * DUR)
mix = np.zeros((N, 2)); rng = np.random.default_rng(11)
O = 0.5
TEAM, RISE, DROP, HIT = 4.75 + O, 9.1 + O, 10.6 + O, 21.7 + O
NOTES = [10.75 + O, 11.25 + O, 11.7 + O, 12.05 + O]
BPM = 112; beat = 60 / BPM
f = lambda m: 440 * 2 ** ((m - 69) / 12)
lp = lambda x, a: lfilter([1 - a], [1, -a], x)


def add(sig, start, pan=0.0, gain=1.0):
    s = int(start * SR)
    if s >= N or s + len(sig) <= 0: return
    if s < 0: sig = sig[-s:]; s = 0
    sig = sig[: N - s] * gain
    mix[s:s + len(sig), 0] += sig * np.sqrt((1 - pan) / 2)
    mix[s:s + len(sig), 1] += sig * np.sqrt((1 + pan) / 2)


def env_t(n): return np.arange(n) / SR


def piano(m, L=2.5, vel=1.0):
    t = env_t(int(L * SR)); fr = f(m)
    tone = sum(np.sin(2 * np.pi * fr * k * t) * np.exp(-t * (1.5 + k * 1.2)) / k ** 1.4 for k in range(1, 6))
    return tone * np.minimum(1, t / .003) * vel


def kick():
    t = env_t(int(.4 * SR)); fr = 42 + 120 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 7)


def snare():
    t = env_t(int(.25 * SR)); n = rng.standard_normal(len(t)); n = n - lp(n, .55)
    return (n * .6 + np.sin(2 * np.pi * 190 * t) * .4) * np.exp(-t * 16)


def hat(o=False):
    t = env_t(int((.18 if o else .05) * SR)); n = rng.standard_normal(len(t)); n = n - lp(n, .2)
    return n * np.exp(-t * (18 if o else 75)) * .2


def ping():  # notification chime
    t = env_t(int(.7 * SR))
    return (np.sin(2 * np.pi * 1568 * t) + .6 * np.sin(2 * np.pi * 2093 * t)) * np.exp(-t * 7) * np.minimum(1, t / .002)


# 1) rain ambience (fades out by the team shot)
rain = rng.standard_normal(N); rain = lp(rain - lp(rain, .3), .55)
drops = np.zeros(N)
for _ in range(600):
    p = rng.integers(0, int(6 * SR)); L = 300
    drops[p:p + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / 40) * rng.uniform(.2, 1)
rk = np.clip(1 - (np.arange(N) / SR - (TEAM - .6)) / 1.0, 0, 1) * np.minimum(1, np.arange(N) / SR / .8)
amb = (rain * .09 + drops * .05) * rk
mix[:, 0] += amb; mix[:, 1] += np.roll(amb, 300)

# 2) lonely piano motif in A minor during the night
for i, (m, tt) in enumerate([(69, .6), (72, 1.4), (76, 2.2), (74, 3.1), (72, 3.8), (64, 4.4)]):
    add(piano(m, 3.0, .9), tt + O * 0, pan=-.2 + .08 * i, gain=.16)
add(piano(45, 4, .8), .6, gain=.14); add(piano(41, 3, .8), 3.1, gain=.12)

# 3) heartbeat pulse + soft pad from the team shot to the drop
t = 0.0
while TEAM + t < DROP - .05:
    add(kick() * .7, TEAM + t, gain=.45); add(kick() * .5, TEAM + t + .22, gain=.3); t += 2 * beat
padL = int((DROP - TEAM) * SR); tp = env_t(padL)
pad = sum(np.sin(2 * np.pi * f(m) * tp * (1 + d)) for m in (57, 60, 64, 67) for d in (-.002, .002))
pad *= np.minimum(1, tp / 1.5) * (0.6 + 0.4 * tp / tp[-1])
add(lp(pad, .9) * .04, TEAM)
# arpeggio sneaks in
k = 0; ta = TEAM + 1.0
while ta < DROP - .1:
    m = [69, 72, 76, 79][k % 4] - (2 if (ta - TEAM) > 2.6 else 0)
    add(piano(m, .6, .7), ta, pan=.3 * np.sin(k), gain=.07 + .04 * (ta - TEAM) / (DROP - TEAM)); ta += beat / 2; k += 1

# 4) riser + reverse whoosh into the drop
L = DROP - RISE; t = env_t(int(L * SR))
nz = rng.standard_normal(len(t)); nz = nz - lp(nz, .2 + .7 * 0.5)
add(nz * (t / L) ** 2.5 * .16 + np.sin(2 * np.pi * (180 * t + 500 * t ** 2 / L)) * (t / L) ** 2 * .05, RISE)

# 5) the drop: uplifting groove in C major (C G Am F) until the end-card hit
chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
bar = 4 * beat; b = 0; tb = DROP
while tb < HIT - .05:
    c = chords[b % 4]
    for q in range(4):
        tq = tb + q * beat
        if tq >= HIT - .05: break
        add(kick(), tq, gain=.6)
        if q in (1, 3): add(snare(), tq, gain=.35)
        add(hat(), tq + beat / 2, pan=.25); add(hat(), tq + beat / 4, pan=-.25, gain=.6)
        tb2 = env_t(int(beat * SR)); bass = np.sin(2 * np.pi * f(c[0] - 24) * tb2) * np.exp(-tb2 * 2.5)
        add(bass * .35, tq)
    for s16 in range(16):
        ts = tb + s16 * beat / 4
        if ts >= HIT - .05: break
        m = c[[0, 1, 2, 1][s16 % 4]] + 12 * (s16 % 8 == 7)
        add(piano(m + 12, .35, .6), ts, pan=.4 * np.sin(s16), gain=.06)
    Lp = int(bar * SR); tpad = env_t(Lp)
    padc = sum(np.sin(2 * np.pi * f(m) * tpad) for m in c) * np.minimum(1, tpad / .3) * np.minimum(1, (bar - tpad) / .3)
    add(lp(padc, .85) * .05, tb)
    tb += bar; b += 1
add(kick(), DROP, gain=.6); add(snare(), DROP, gain=.3)  # impact on the drop
# notification pings
for i, tn in enumerate(NOTES): add(ping(), tn, pan=.3 - .2 * i, gain=.22)

# 6) final hit + resolving chord on the logo
t = env_t(int(5 * SR))
boom = np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-t * 9)) / SR) * np.exp(-t * 1.8)
shine = sum(np.sin(2 * np.pi * f(m) * t) for m in (60, 67, 72, 76, 79)) * np.exp(-t * .55) * .07
add(boom * .8 + shine, HIT)
add(piano(72, 4, .8), HIT + .02, gain=.15); add(piano(76, 4, .8), HIT + .5, gain=.12); add(piano(79, 4, .8), HIT + 1.0, gain=.12)

tt = np.arange(N) / SR
mix *= np.minimum(1, (DUR - tt) / 2.0)[:, None]
mix /= np.max(np.abs(mix)) + 1e-9
wavfile.write(sys.argv[1], SR, (mix * .89 * 32767).astype(np.int16))
print('wrote', sys.argv[1])
