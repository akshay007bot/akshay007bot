# ವೇಗದ ಹಿಂದಿನ ಕಥೆ: Indian racing, behind the scenes (Kannada)

A 96-second Kannada documentary-style video about the hidden work behind Indian motor racing:
karting beginnings, fitness training, simulator practice, track practice and data, mechanics'
long nights, pit-stop drills, travel by road and abroad, and the team effort behind every podium.

- **English narration version:** `out/indian_racing_behind_the_scenes_kannada_english_audio.mp4` (82 s, English voice, Kannada titles and subtitles on screen)
  - Subtitle files: `...english_audio.en.srt` (English) and `...english_audio.kn.srt` (Kannada)
- **Kannada narration version:** `out/indian_racing_behind_the_scenes_kannada.mp4` (96 s), subtitles `...kannada.kn.srt`
- **Script:** `script_kn.json` (Kannada narration `text`, English narration `text_en`, chapter titles)
- **Photos:** real photos of Indian circuits and racing from Wikimedia Commons, see `CREDITS.md`

## Rebuild

```bash
apt-get install -y fonts-noto-core ffmpeg
pip install sherpa-onnx soundfile scipy pillow numpy
# Kannada voice model: https://huggingface.co/willwade/mms-tts-multilingual-models-onnx (folder kan/)
python3 tts.py /path/to/kan          # writes audio/*.wav
python3 build_video.py               # writes out/*.mp4 and out/*.srt (fails if over 120 s)

# English narration (Piper voice en_US-norman-medium, public domain):
pip install piper-tts
# https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/norman/medium
python3 tts_en.py /path/to/en_US-norman-medium.onnx   # writes audio_en/*.wav
python3 build_video.py en
```

Note: the Kannada MMS voice is CC BY-NC 4.0, so the Kannada-narration build is for non-commercial use (the English voice is public domain). For commercial
publishing, re-record the narration with a human voice-over using `script_kn.json`.
