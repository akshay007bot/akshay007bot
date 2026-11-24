"""Text-to-speech: free Microsoft Edge neural voices (edge-tts), offline SAPI fallback.

Playback uses ``pygame.mixer``: its Windows wheels bundle SDL2 + an MP3 decoder, so it
needs no system codecs or ffmpeg, it blocks/polls cleanly, and it can play both the
edge-tts MP3s and in-memory numpy buffers (the chime). miniaudio would also work, but
pygame has the longer track record on Windows and broader Python-version wheel coverage.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from ..config import settings

log = logging.getLogger("jarvis.tts")

KANNADA = re.compile(r"[ಀ-೿]")
EDGE_TIMEOUT_S = 15

_lock = threading.RLock()       # one voice at a time (main loop + reminder threads)
_mixer_ready = False


# --------------------------------------------------------------------------- pure logic

def has_kannada(text: str) -> bool:
    return bool(KANNADA.search(text or ""))


def pick_voice(text: str) -> str:
    return settings.voice_kn if has_kannada(text) else settings.voice_en


_URL = re.compile(r"(https?://|www\.)\S+", re.I)
_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")


def clean_text(text: str) -> str:
    """Strip markdown, code and URLs so the voice doesn't read out symbols."""
    t = text or ""
    t = re.sub(r"```.*?```", " ", t, flags=re.S)                 # fenced code blocks
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", t)              # images -> alt text
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)               # [text](url) -> text
    t = re.sub(r"<(https?://[^>]+)>", " ", t)                    # <url>
    t = _URL.sub(" ", t)                                         # bare urls
    t = re.sub(r"`([^`]*)`", r"\1", t)                           # inline code
    t = re.sub(r"^\s{0,3}#{1,6}\s*", "", t, flags=re.M)          # headings
    t = re.sub(r"^\s*>\s?", "", t, flags=re.M)                   # quotes
    t = re.sub(r"^\s*([-*+•]|\d+[.)])\s+", "", t, flags=re.M)    # list bullets / numbers
    t = re.sub(r"^\s*\|?[\s:|-]{3,}\|?\s*$", "", t, flags=re.M)  # table separator rows
    t = t.replace("|", ", ")
    t = re.sub(r"(\*\*|__|\*|~~)", "", t)                        # bold/italic/strike
    t = re.sub(r"(?<!\w)_(\S.*?)_(?!\w)", r"\1", t)              # _italic_
    t = _EMOJI.sub("", t)
    # Headings, list items and paragraphs become separate sentences (a short pause each).
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    if len(lines) > 1:
        lines = [ln if ln[-1] in ".!?,:;।" else ln + "." for ln in lines]
    t = " ".join(lines)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    t = re.sub(r"([.!?])(\s*[.,])+", r"\1", t)                   # "Hi.." / "Hi.," -> "Hi."
    return t.strip(" ,")


_SENT_END = re.compile(r"(?<=[.!?।])\s+")


def split_sentences(text: str, min_len: int = 25, max_len: int = 300) -> list[str]:
    """Split into sentence-sized chunks so speech can start before the whole reply is synthesized.

    Very short sentences are merged with the next one (fewer round trips, more natural flow);
    over-long ones are cut at commas/spaces.
    """
    parts = [p.strip() for p in _SENT_END.split(text or "") if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in parts:
        buf = f"{buf} {p}".strip() if buf else p
        if len(buf) >= min_len:
            chunks.append(buf)
            buf = ""
    if buf:
        if chunks and len(buf) < min_len:
            chunks[-1] = f"{chunks[-1]} {buf}"
        else:
            chunks.append(buf)

    out: list[str] = []
    for c in chunks:
        while len(c) > max_len:
            cut = max(c.rfind(", ", 0, max_len), c.rfind(" ", 0, max_len))
            cut = cut if cut > 0 else max_len
            out.append(c[:cut + 1].strip())
            c = c[cut + 1:].strip()
        if c:
            out.append(c)
    return out


# --------------------------------------------------------------------------- synthesis

def synthesize(text: str, voice: str, path: str) -> None:
    """Write an MP3 of ``text`` spoken by ``voice`` to ``path`` using edge-tts (needs internet)."""
    import edge_tts

    async def run() -> None:
        await asyncio.wait_for(edge_tts.Communicate(text, voice).save(path), EDGE_TIMEOUT_S)

    # Each call gets its own event loop, so this is safe from any thread.
    asyncio.run(run())
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise RuntimeError("edge-tts returned no audio")


def _synth_to_temp(text: str, voice: str) -> str:
    fd, path = tempfile.mkstemp(prefix="jarvis_tts_", suffix=".mp3")
    os.close(fd)
    try:
        synthesize(text, voice, path)
        return path
    except BaseException:
        _remove(path)
        raise


def _remove(path: str) -> None:
    for _ in range(5):  # Windows may hold the file briefly after playback
        try:
            os.remove(path)
            return
        except FileNotFoundError:
            return
        except OSError:
            time.sleep(0.1)


# --------------------------------------------------------------------------- playback

def _mixer():
    global _mixer_ready
    try:
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame
    except ImportError as e:
        raise RuntimeError("pygame is not installed. Run: pip install -r requirements-voice.txt") from e
    if not _mixer_ready:
        try:
            # edge-tts produces 24 kHz mono MP3; other rates are resampled by SDL.
            pygame.mixer.init(frequency=24000, size=-16, channels=1)
        except pygame.error as e:
            raise RuntimeError(
                f"No audio output device ({e}). Plug in speakers/headphones and check the default "
                "playback device in Windows Settings > System > Sound."
            ) from e
        _mixer_ready = True
    return pygame


def play_file(path: str) -> None:
    """Play an audio file and block until it finishes."""
    pygame = _mixer()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.03)
    pygame.mixer.music.unload()  # release the file so it can be deleted on Windows


def _speak_offline(text: str) -> None:
    """Windows SAPI voice via pyttsx3. English only (SAPI has no Kannada voice by default)."""
    if has_kannada(text):
        log.warning("Offline voice can't speak Kannada; printing only: %s", text)
        return
    try:
        import pyttsx3
    except ImportError:
        log.warning("Offline TTS (pyttsx3) not installed; can't speak: %s", text)
        return
    try:
        engine = pyttsx3.init()  # a fresh engine per call avoids runAndWait() hangs on reuse
        engine.setProperty("rate", 180)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:  # noqa: BLE001 - speaking must never crash the assistant
        log.warning("Offline TTS failed: %s", e)


def speak(text: str) -> None:
    """Speak ``text`` aloud and block until done."""
    clean = clean_text(text)
    if not clean:
        return
    voice = pick_voice(clean)  # choose once per reply so the voice doesn't switch mid-answer
    chunks = split_sentences(clean)

    with _lock:
        # One background worker synthesizes chunks in order while we play the previous one,
        # so the first sentence starts playing as soon as it alone is ready.
        pool = ThreadPoolExecutor(max_workers=1)
        futures = [pool.submit(_synth_to_temp, c, voice) for c in chunks]
        try:
            online = True
            for chunk, fut in zip(chunks, futures):
                if not online:
                    _speak_offline(chunk)
                    continue
                try:
                    path = fut.result()
                except Exception as e:  # noqa: BLE001 - no internet, bad voice name, timeout...
                    log.warning("edge-tts failed (%s); using offline voice", e)
                    online = False
                    for f in futures:
                        f.cancel()
                    _speak_offline(chunk)
                    continue
                try:
                    play_file(path)
                finally:
                    _remove(path)
        finally:
            for f in futures:
                f.cancel()
            pool.shutdown(wait=True)
            # Delete any MP3s synthesized but never played (after an error or interruption).
            for f in futures:
                if not f.cancelled() and f.exception() is None:
                    _remove(f.result())


# --------------------------------------------------------------------------- chime

def make_chime(rate: int = 24000):
    """A soft rising two-tone 'ding-dong' (E5 then A5) as int16 samples, about 0.3 s."""
    import numpy as np

    def tone(freq: float, dur: float) -> "np.ndarray":
        t = np.arange(int(rate * dur)) / rate
        wave = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)  # a bit of warmth
        attack = np.minimum(1.0, t / 0.01)                # 10 ms fade-in: no click
        decay = np.exp(-t * 9.0)                          # bell-like fade-out
        return wave * attack * decay

    gap = np.zeros(int(rate * 0.02))
    sig = np.concatenate([tone(659.25, 0.14), gap, tone(880.0, 0.18)])
    sig = sig / np.max(np.abs(sig)) * 0.35               # gentle volume
    return (sig * 32767).astype(np.int16)


def chime() -> None:
    """Play a short acknowledgement sound (blocking, ~0.35 s). Never raises."""
    try:
        import numpy as np
        with _lock:
            pygame = _mixer()
            freq, _size, channels = pygame.mixer.get_init()
            samples = make_chime(freq)
            if channels > 1:
                samples = np.repeat(samples[:, None], channels, axis=1)
            sound = pygame.mixer.Sound(buffer=np.ascontiguousarray(samples).tobytes())
            ch = sound.play()
            time.sleep(sound.get_length())
            while ch is not None and ch.get_busy():
                time.sleep(0.01)
    except Exception as e:  # noqa: BLE001 - a missing beep is not worth crashing over
        log.warning("Chime failed: %s", e)


__all__ = ["speak", "chime", "clean_text", "split_sentences", "has_kannada", "pick_voice", "synthesize"]
