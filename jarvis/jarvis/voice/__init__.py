"""Voice I/O for Jarvis: wake word (``wake``), speech-to-text (``stt``), text-to-speech (``tts``).

Each submodule imports cheaply; the heavy libraries (openwakeword, faster-whisper,
sounddevice, edge-tts, pygame) are only imported when a function actually needs them,
so ``python -m jarvis --text`` works on a machine with no audio stack installed.
"""

from __future__ import annotations

SAMPLE_RATE = 16_000  # Hz; what both openWakeWord and Whisper expect (mono, 16-bit)

MIC_HINT = (
    "Check that a microphone is plugged in and allowed in "
    "Windows Settings > Privacy & security > Microphone (\"Let desktop apps access your microphone\"), "
    "and that it is the default recording device in Sound settings."
)


def open_mic_stream(blocksize: int, callback=None):
    """Open a 16 kHz mono int16 input stream on the default microphone.

    Raises RuntimeError with a fix hint instead of a cryptic PortAudio error.
    """
    try:
        import sounddevice as sd
    except ImportError as e:  # pragma: no cover - depends on install
        raise RuntimeError("The 'sounddevice' package is missing. Run: pip install -r requirements-voice.txt") from e
    except OSError as e:  # PortAudio library not found
        raise RuntimeError(f"Audio system unavailable ({e}). {MIC_HINT}") from e

    try:
        sd.check_input_settings(channels=1, samplerate=SAMPLE_RATE, dtype="int16")
        return sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                              blocksize=blocksize, callback=callback)
    except Exception as e:  # sd.PortAudioError, ValueError("No input device matching ...")
        raise RuntimeError(f"No usable microphone found ({e}). {MIC_HINT}") from e
