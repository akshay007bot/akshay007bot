"""Kannada narration using Meta's MMS-TTS Kannada voice (facebook/mms-tts-kan, CC-BY-NC 4.0),
run through sherpa-onnx (ONNX export: huggingface.co/willwade/mms-tts-multilingual-models-onnx, kan/).

Usage: python3 tts.py <model_dir containing model.onnx + tokens.txt>
Writes audio/<scene id>.wav for each entry in script_kn.json.
"""
import json
import os
import re
import sys
import numpy as np
import sherpa_onnx
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
mdir = sys.argv[1]
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
script = json.load(open(os.path.join(HERE, "script_kn.json"), encoding="utf-8"))

vocab = {ln.rsplit(" ", 1)[0] for ln in open(os.path.join(mdir, "tokens.txt"), encoding="utf-8").read().split("\n") if ln}
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=os.path.join(mdir, "model.onnx"),
                                               tokens=os.path.join(mdir, "tokens.txt"),
                                               noise_scale=0.55, noise_scale_w=0.7, length_scale=1.0),
    num_threads=4)))

for sc in script:
    # speak phrase-by-phrase so punctuation becomes natural pauses
    phrases = [p.strip() for p in re.split(r"([.,!?])", sc["text"])]
    out, sr = [], 16000
    i = 0
    while i < len(phrases):
        p = phrases[i]
        punct = phrases[i + 1] if i + 1 < len(phrases) else "."
        i += 2
        txt = "".join(ch for ch in p if ch in vocab or ch == " ")
        txt = re.sub(r"\s+", " ", txt).strip()
        if not txt:
            continue
        a = tts.generate(txt, sid=0, speed=1.0)
        sr = a.sample_rate
        out.append(np.array(a.samples, dtype=np.float32))
        out.append(np.zeros(int(sr * (0.45 if punct in ".!?" else 0.22)), dtype=np.float32))
    audio = np.concatenate(out)
    audio = audio / (np.abs(audio).max() + 1e-9) * 0.9
    p = os.path.join(HERE, "audio", f"{sc['id']}.wav")
    sf.write(p, audio, sr, subtype="PCM_16")
    print(p, f"{len(audio)/sr:.1f}s")
