"""English narration with the Piper voice en_US-norman-medium (public domain).

Usage: python3 tts_en.py /path/to/en_US-norman-medium.onnx
Writes audio_en/<scene id>.wav from the "text_en" field of script_kn.json.
Voice: https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/norman/medium
"""
import json
import os
import sys
import wave
from piper import PiperVoice, SynthesisConfig

HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, "audio_en"), exist_ok=True)
voice = PiperVoice.load(sys.argv[1])
cfg = SynthesisConfig(length_scale=1.05, noise_scale=0.6, noise_w_scale=0.8)

for sc in json.load(open(os.path.join(HERE, "script_kn.json"), encoding="utf-8")):
    p = os.path.join(HERE, "audio_en", f"{sc['id']}.wav")
    with wave.open(p, "wb") as w:
        voice.synthesize_wav(sc["text_en"], w, syn_config=cfg)
    with wave.open(p) as w:
        print(p, f"{w.getnframes() / w.getframerate():.1f}s")
