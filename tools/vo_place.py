"""Place one VO line per bar onto a film's beat grid.
usage: python tools/vo_place.py <film> <beats_per_bar> [lead_s]
reads <film>/audio/vo/script.json + line_NN.wav (24 kHz), writes <film>/audio/vo.wav (48 kHz stereo)
and <film>/vo.json: [{bar, text, start, end, words:[{w, t}]}] (word times spread by characters)."""
import json, sys, numpy as np, soundfile as sf
from scipy.signal import resample_poly
film, bpb = sys.argv[1], float(sys.argv[2]); lead = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
g = json.load(open(f'{film}/beats.json')); P, O = g['period'], g['offset']; dur = json.load(open(f'{film}/film.json'))['duration']
SR = 48000; out = np.zeros(int(dur * SR) + SR); placed = []
for i, l in enumerate(json.load(open(f'{film}/audio/vo/script.json'))):
    a, sr = sf.read(f'{film}/audio/vo/line_{i:02d}.wav'); a = resample_poly(a, SR, sr)
    e = np.abs(a); idx = np.where(e > 10 ** (-40 / 20) * e.max())[0]
    s0, s1 = max(0, idx[0] - int(.03 * SR)), min(len(a), idx[-1] + int(.12 * SR)); seg = a[s0:s1].copy()
    f = int(.01 * SR); seg[:f] *= np.linspace(0, 1, f); f2 = int(.06 * SR); seg[-f2:] *= np.linspace(1, 0, f2)
    on = O + l['bar'] * bpb * P + lead; st = int(on * SR) - int(.03 * SR)
    out[st:st + len(seg)] += seg[:len(out) - st]; sp = (idx[-1] - idx[0]) / SR
    ws, n, c, W = l['text'].split(), len(l['text']), 0, []
    for w in ws: W.append({'w': w, 't': round(on + c / n * sp, 3)}); c += len(w) + 1
    placed.append({'bar': l['bar'], 'text': l['text'], 'start': round(on, 3), 'end': round(on + sp, 3), 'words': W})
for a_, b_ in zip(placed, placed[1:]):
    if b_['start'] - a_['end'] < 0.12: print(f"WARN tight gap bar {a_['bar']}->{b_['bar']}: {b_['start']-a_['end']:.2f}s")
out = out[:int(dur * SR)]; out = out / np.abs(out).max() * 0.7
sf.write(f'{film}/audio/vo.wav', np.stack([out, out], 1), SR); json.dump(placed, open(f'{film}/vo.json', 'w'), indent=1)
print(film, ' '.join(f"{p['bar']}:{p['start']:.2f}-{p['end']:.2f}" for p in placed))
