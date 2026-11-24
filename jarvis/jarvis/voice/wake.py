"""Wake-word detection with openWakeWord's pre-trained "hey_jarvis" model.

We use the ONNX inference framework: onnxruntime ships Windows wheels, while
tflite-runtime does not exist for Windows (or for newer Pythons at all).
"""

from __future__ import annotations

import logging
import os
import threading

from ..config import settings
from . import SAMPLE_RATE, open_mic_stream

log = logging.getLogger("jarvis.wake")

FRAME = 1280  # 80 ms at 16 kHz: openWakeWord's native hop size

_model = None
_model_lock = threading.Lock()


def _resolve_model_path(name: str) -> str:
    """Return a local .onnx path for ``name``, downloading pre-trained models on first use.

    ``name`` may be a pre-trained model name ("hey_jarvis") or a path to a custom .onnx model.
    """
    if os.path.isfile(name):
        return name

    import openwakeword
    from openwakeword.utils import download_file

    key = name.replace(" ", "_")
    if key not in openwakeword.MODELS:
        raise RuntimeError(
            f"Unknown wake word model '{name}'. Use one of {sorted(openwakeword.MODELS)} "
            "or a path to a custom .onnx file (JARVIS_WAKE_MODEL in .env)."
        )

    # The feature models (melspectrogram + embedding) are needed for every wake word.
    # openwakeword.utils.download_models() skips a model when its .tflite exists even if
    # the .onnx is missing, so we check and fetch the .onnx files ourselves.
    needed = [m["model_path"] for m in openwakeword.FEATURE_MODELS.values()]
    needed.append(openwakeword.MODELS[key]["model_path"])
    urls = [m["download_url"] for m in openwakeword.FEATURE_MODELS.values()]
    urls.append(openwakeword.MODELS[key]["download_url"])
    for path, url in zip(needed, urls):
        onnx_path = path.replace(".tflite", ".onnx")
        if not os.path.exists(onnx_path):
            log.info("Downloading wake word model %s ...", os.path.basename(onnx_path))
            os.makedirs(os.path.dirname(onnx_path), exist_ok=True)
            try:
                download_file(url.replace(".tflite", ".onnx"), os.path.dirname(onnx_path))
            except Exception as e:  # noqa: BLE001
                raise RuntimeError(
                    f"Could not download the wake word model ({e}). Connect to the internet once "
                    "so Jarvis can fetch it, or use push-to-talk: python -m jarvis --ptt"
                ) from e
    return openwakeword.MODELS[key]["model_path"].replace(".tflite", ".onnx")


def _get_model():
    """Create the openWakeWord model once (lazily) and reuse it."""
    global _model
    with _model_lock:
        if _model is None:
            try:
                from openwakeword.model import Model
            except ImportError as e:
                raise RuntimeError(
                    "openWakeWord is not installed. Run: pip install -r requirements-voice.txt "
                    "(or use push-to-talk: python -m jarvis --ptt)"
                ) from e
            path = _resolve_model_path(settings.wake_word)
            _model = Model(wakeword_models=[path], inference_framework="onnx")
            log.info("Wake word model loaded: %s (threshold %.2f)", path, settings.wake_threshold)
        return _model


def wait_for_wake() -> None:
    """Block until the wake word is heard on the default microphone."""
    import numpy as np

    model = _get_model()
    model.reset()  # start clean: no leftover audio/scores from a previous round
    threshold = settings.wake_threshold

    with open_mic_stream(blocksize=FRAME) as stream:
        while True:
            data, overflowed = stream.read(FRAME)
            if overflowed:
                log.debug("Mic input overflow (CPU busy?)")
            frame = np.asarray(data, dtype=np.int16).reshape(-1)
            scores = model.predict(frame)  # {model_name: score in 0..1}
            score = max(scores.values()) if scores else 0.0
            if score >= threshold:
                log.info("Wake word detected (score %.2f)", score)
                # Clear the rolling feature/prediction buffers so the same utterance
                # can't trigger again the next time we're called.
                model.reset()
                return


__all__ = ["wait_for_wake", "SAMPLE_RATE"]
