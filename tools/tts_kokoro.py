# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["kokoro>=0.9", "soundfile", "numpy", "torch"]
# ///
"""Natural voice-over with Kokoro (free, runs offline after first download).

Usage:
  uv run tools/tts_kokoro.py script.json out_dir [voice] [speed]
script.json = [{"text": "Planning IVF in India?"}, {"text": "..."}]   (one line per scene)
voices: af_heart (warm US female, default), af_bella, am_michael, bf_emma (UK female), bm_george (UK male)
Writes out_dir/line_00.wav, line_01.wav ... at 24 kHz.
"""
import json, os, sys
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
import numpy as np, soundfile as sf
from kokoro import KPipeline
script, out = sys.argv[1], sys.argv[2]
voice = sys.argv[3] if len(sys.argv) > 3 else "af_heart"
speed = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
os.makedirs(out, exist_ok=True)
p = KPipeline(lang_code="a" if voice[0] == "a" else "b")
for i, l in enumerate(json.load(open(script))):
    a = np.concatenate([r.audio.numpy() for r in p(l["text"], voice=voice, speed=speed)])
    sf.write(f"{out}/line_{i:02d}.wav", a, 24000)
    print(f"line_{i:02d}.wav  {len(a)/24000:.2f}s  {l['text']}")
