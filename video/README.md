# ವೇಗದ ಹಿಂದಿನ ಕಥೆ: Indian racing, behind the scenes (Kannada)

A 96-second Kannada documentary-style video about the hidden work behind Indian motor racing:
karting beginnings, fitness training, simulator practice, track practice and data, mechanics'
long nights, pit-stop drills, travel by road and abroad, and the team effort behind every podium.

- **Video:** `out/indian_racing_behind_the_scenes_kannada.mp4` (1920x1080, H.264/AAC, 96 s)
- **Subtitles:** `out/indian_racing_behind_the_scenes_kannada.srt` (Kannada, also burned into the video)
- **Script:** `script_kn.json` (narration and chapter titles)
- **Photos:** real photos of Indian circuits and racing from Wikimedia Commons, see `CREDITS.md`

## Rebuild

```bash
apt-get install -y fonts-noto-core ffmpeg
pip install sherpa-onnx soundfile scipy pillow numpy
# Kannada voice model: https://huggingface.co/willwade/mms-tts-multilingual-models-onnx (folder kan/)
python3 tts.py /path/to/kan          # writes audio/*.wav
python3 build_video.py               # writes out/*.mp4 and out/*.srt (fails if over 120 s)
```

Note: the MMS voice is CC BY-NC 4.0, so this build is for non-commercial use. For commercial
publishing, re-record the narration with a human voice-over using `script_kn.json`.
