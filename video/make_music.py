"""Generate an original, royalty-free cinematic background score (no samples used).

Usage: python3 make_music.py <seconds> <out.wav>
"""
import sys
import numpy as np
from scipy.io import wavfile

SR = 44100
dur = float(sys.argv[1])
out = sys.argv[2]
t = np.arange(int(SR * dur)) / SR
rng = np.random.default_rng(7)


def note(f):
    return 440.0 * 2 ** ((f - 69) / 12)


# Chord progression (MIDI): Am - F - C - G, 8 s per chord, minor/heroic mood
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]
bar = 8.0
pad = np.zeros_like(t)
bass = np.zeros_like(t)
for i in range(int(dur // bar) + 1):
    c = chords[i % len(chords)]
    s, e = int(i * bar * SR), min(int((i + 1) * bar * SR), len(t))
    if s >= len(t):
        break
    tt = t[s:e] - i * bar
    env = np.minimum(1, tt / 1.5) * np.minimum(1, (bar - tt) / 1.5)
    for n in c:
        f = note(n)
        for det in (-0.15, 0.0, 0.15):  # detuned saw-ish pad via few harmonics
            ph = 2 * np.pi * f * (1 + det / 100) * tt
            pad[s:e] += env * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)) / 9
    fb = note(c[0] - 12)
    # pulsing bass on 8th notes (tempo 120 bpm)
    pulse = np.exp(-((tt % 0.25) * 14))
    bass[s:e] += env * pulse * np.sin(2 * np.pi * fb * tt) * 0.5

# Drums: kick on beats, hats on off-beats, building after intro
beat = 0.5
kick = np.zeros_like(t)
hat = np.zeros_like(t)
klen = int(0.25 * SR)
kt = np.arange(klen) / SR
kshape = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 12)
hlen = int(0.05 * SR)
hshape = rng.standard_normal(hlen) * np.exp(-np.arange(hlen) / SR * 90)
hshape = np.diff(np.concatenate([[0], hshape]))  # crude high-pass
for k in range(int(dur / beat)):
    pos = int(k * beat * SR)
    if k * beat < 6 or pos + klen >= len(t):
        continue
    kick[pos:pos + klen] += kshape
    hp = pos + int(beat / 2 * SR)
    if hp + hlen < len(t):
        hat[hp:hp + hlen] += hshape * 0.25

mix = 0.55 * pad + 0.45 * bass + 0.5 * kick + 0.3 * hat
# overall fade in/out
fade = np.minimum(1, t / 3) * np.minimum(1, (dur - t) / 4)
mix *= fade
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.8
stereo = np.stack([mix, np.roll(mix, int(0.012 * SR))], axis=1)
wavfile.write(out, SR, (stereo * 32767).astype(np.int16))
print("wrote", out, dur, "s")
