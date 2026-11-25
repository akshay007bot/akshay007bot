"""Speech-to-text: record one utterance from the mic, transcribe with faster-whisper.

Only English and Kannada are expected, so language detection is restricted to those two.
"""

from __future__ import annotations

import logging
import queue
import threading
from typing import Iterable

from ..config import settings
from . import SAMPLE_RATE, open_mic_stream

log = logging.getLogger("jarvis.stt")

LANGS = ("en", "kn")
INITIAL_PROMPT = "Hey Jarvis."  # biases Whisper toward spelling the name "Jarvis"

FRAME_MS = 30                                   # webrtcvad accepts 10/20/30 ms frames
FRAME = SAMPLE_RATE * FRAME_MS // 1000          # 480 samples
START_FRAMES = 3                                # ~90 ms of voice before we call it "speech"
END_SILENCE_S = 0.8                             # trailing silence that ends the utterance
MAX_UTTERANCE_S = 20.0
PRE_ROLL_S = 0.3                                # keep audio from just before speech began

_model = None
_model_lock = threading.Lock()


# --------------------------------------------------------------------------- pure logic

def choose_language(detected: str | None, probs: Iterable[tuple[str, float]] | None) -> str:
    """Restrict Whisper's language guess to English or Kannada.

    ``detected`` is Whisper's top guess; ``probs`` its (lang, prob) list. If the guess is
    neither en nor kn, pick whichever of en/kn scored higher (English when unknown).
    """
    if detected in LANGS:
        return detected
    scores = {lang: p for lang, p in (probs or []) if lang in LANGS}
    if not scores:
        return "en"
    return max(LANGS, key=lambda lang: scores.get(lang, 0.0))


class Endpointer:
    """Decides when speech starts and ends from a stream of per-frame voiced/unvoiced flags."""

    def __init__(self, frame_s: float, timeout_s: float,
                 start_frames: int = START_FRAMES, end_silence_s: float = END_SILENCE_S,
                 max_utterance_s: float = MAX_UTTERANCE_S):
        self.frame_s = frame_s
        self.timeout_frames = int(timeout_s / frame_s)
        self.start_frames = start_frames
        self.end_frames = int(end_silence_s / frame_s)
        self.max_frames = int(max_utterance_s / frame_s)
        self.started = False
        self._waited = 0
        self._run = 0       # consecutive voiced frames before start
        self._silence = 0   # consecutive unvoiced frames after start
        self._length = 0    # frames since start

    def update(self, voiced: bool) -> str:
        """Feed one frame. Returns 'wait', 'start', 'speech', 'end' or 'timeout'."""
        if not self.started:
            self._waited += 1
            self._run = self._run + 1 if voiced else 0
            if self._run >= self.start_frames:
                self.started = True
                self._length = self._run
                return "start"
            return "timeout" if self._waited >= self.timeout_frames else "wait"
        self._length += 1
        self._silence = 0 if voiced else self._silence + 1
        if self._silence >= self.end_frames or self._length >= self.max_frames:
            return "end"
        return "speech"


def _make_vad():
    """Return a function frame(int16 ndarray) -> bool. webrtcvad if available, else energy."""
    try:
        import webrtcvad  # provided by the 'webrtcvad-wheels' package (has Windows wheels)
        vad = webrtcvad.Vad(2)  # 0 = permissive .. 3 = strict
        return lambda f: vad.is_speech(f.tobytes(), SAMPLE_RATE)
    except ImportError:
        log.info("webrtcvad not installed; using a simple energy detector")
        import numpy as np
        state = {"noise": 300.0}

        def energy(f) -> bool:
            rms = float(np.sqrt(np.mean(f.astype(np.float32) ** 2)) + 1e-6)
            voiced = rms > max(500.0, state["noise"] * 3.0)
            if not voiced:  # slowly track the background noise floor
                state["noise"] = 0.95 * state["noise"] + 0.05 * rms
            return voiced
        return energy


# --------------------------------------------------------------------------- recording

def record(timeout: float = 7) -> "object | None":
    """Record one utterance. Returns float32 ndarray at 16 kHz, or None if nobody spoke."""
    import numpy as np

    is_speech = _make_vad()
    ep = Endpointer(FRAME_MS / 1000, timeout)
    frames: "queue.Queue" = queue.Queue()

    def callback(indata, _n, _time, status):  # runs on PortAudio's thread
        if status:
            log.debug("mic status: %s", status)
        frames.put(indata[:, 0].copy())

    pre_roll: list = []
    pre_roll_max = int(PRE_ROLL_S * 1000 / FRAME_MS)
    audio: list = []
    with open_mic_stream(blocksize=FRAME, callback=callback):
        while True:
            try:
                f = frames.get(timeout=2.0)
            except queue.Empty:
                raise RuntimeError("The microphone stopped sending audio. Is it unplugged or in use?") from None
            if len(f) != FRAME:  # webrtcvad needs exact frame sizes
                continue
            state = ep.update(bool(is_speech(f)))
            if state == "timeout":
                return None
            if state == "wait":
                pre_roll.append(f)
                pre_roll = pre_roll[-pre_roll_max:]
            elif state == "start":
                audio.extend(pre_roll)
                audio.append(f)
            else:
                audio.append(f)
                if state == "end":
                    break
    return np.concatenate(audio).astype(np.float32) / 32768.0


# --------------------------------------------------------------------------- whisper

def _load_model():
    """Load faster-whisper once. device 'auto' -> CUDA float16 if available, else CPU int8."""
    global _model
    with _model_lock:
        if _model is not None:
            return _model
        try:
            from faster_whisper import WhisperModel
        except ImportError as e:
            raise RuntimeError("faster-whisper is not installed. Run: pip install -r requirements-voice.txt") from e

        want = (settings.whisper_device or "auto").lower()
        attempts: list[tuple[str, str]] = []
        if want in ("auto", "cuda"):
            try:
                import ctranslate2
                if ctranslate2.get_cuda_device_count() > 0:
                    attempts.append(("cuda", "float16"))
            except Exception:  # noqa: BLE001
                pass
        attempts.append(("cpu", "int8"))

        last: Exception | None = None
        for device, compute in attempts:
            try:
                log.info("Loading Whisper '%s' on %s (%s) - first run downloads it...",
                         settings.whisper_model, device, compute)
                _model = WhisperModel(settings.whisper_model, device=device, compute_type=compute)
                return _model
            except Exception as e:  # noqa: BLE001 - e.g. CUDA present but cuDNN/cuBLAS DLLs missing
                log.warning("Whisper on %s failed: %s", device, e)
                last = e
        raise RuntimeError(
            f"Could not load the Whisper model '{settings.whisper_model}' ({last}). "
            "The first run needs internet to download it; check WHISPER_MODEL in .env."
        ) from last


def transcribe(audio) -> tuple[str, str]:
    """Transcribe float32 16 kHz audio (or a file path). Returns (text, 'en'|'kn')."""
    model = _load_model()
    opts = dict(beam_size=5, vad_filter=True, initial_prompt=INITIAL_PROMPT,
                condition_on_previous_text=False)
    segments, info = model.transcribe(audio, **opts)  # language=None -> auto-detect
    lang = choose_language(info.language, info.all_language_probs)
    if lang != info.language:
        log.info("Whisper guessed '%s' (%.2f); re-running as '%s'", info.language,
                 info.language_probability, lang)
        segments, info = model.transcribe(audio, language=lang, **opts)
    text = "".join(s.text for s in segments).strip()
    return text, lang


def listen(timeout: float = 7) -> tuple[str, str]:
    """Record until the user stops speaking and transcribe it.

    Returns ("", "") if no speech starts within ``timeout`` seconds (or nothing intelligible).
    """
    _load_model()  # load before opening the mic so the first word isn't lost while loading
    audio = record(timeout)
    if audio is None or len(audio) < SAMPLE_RATE * 0.25:
        return "", ""
    text, lang = transcribe(audio)
    return (text, lang) if text else ("", "")


__all__ = ["listen", "transcribe", "record", "choose_language", "Endpointer"]
