"""Main loop: wake word -> listen -> think/act -> speak. Also a typed text mode."""

from __future__ import annotations

import logging
import re

from . import notify, tools
from .brain import Brain
from .config import settings

log = logging.getLogger("jarvis")

YES = re.compile(r"\b(yes|yeah|yep|sure|ok|okay|go ahead|do it|confirm|haan|houdu|hoon|sari)\b|ಹೌದು|ಸರಿ|ಹೂಂ", re.I)
STOP_WORDS = re.compile(r"^\s*(stop|cancel|never ?mind|that'?s all|thank you|thanks|bye|goodbye|ಸಾಕು|ಧನ್ಯವಾದ)\W*$", re.I)


def run_text() -> None:
    """Type instead of talk. Useful for testing and for quiet places."""
    def confirm(what: str) -> bool:
        return YES.search(input(f"JARVIS: Shall I {what}? (yes/no) > ") or "") is not None

    brain = Brain(confirm_fn=confirm)
    _startup_report()
    print(f"JARVIS online. Type to talk, 'reset' to clear context, 'quit' to exit.\n")
    while True:
        try:
            text = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text.lower() in ("quit", "exit"):
            break
        if text.lower() == "reset":
            brain.reset()
            print("JARVIS: Context cleared.")
            continue
        print("JARVIS:", brain.ask(text, on_tool=lambda n: print(f"  (using {n})")))


def run_voice(push_to_talk: bool = False) -> None:
    from .voice import stt, tts, wake  # imported here so text mode works without audio libs

    def say(text: str) -> None:
        print(f"JARVIS: {text}")
        tts.speak(text)

    def confirm(what: str) -> bool:
        say(f"Shall I {what}?")
        heard, _ = stt.listen(timeout=6)
        print(f"You: {heard}")
        return bool(heard) and YES.search(heard) is not None

    notify.set_announcer(say)
    brain = Brain(confirm_fn=confirm)
    _startup_report()
    say(f"Jarvis online. At your service, {settings.user_name}.")

    while True:
        try:
            if push_to_talk:
                input("\nPress Enter and speak... ")
            else:
                print("\n(waiting for 'Hey Jarvis')")
                wake.wait_for_wake()
                tts.chime()
            # Follow-up mode: after answering, keep listening briefly so you
            # can continue the conversation without the wake word again.
            while True:
                heard, lang = stt.listen(timeout=7)
                if not heard:
                    break
                print(f"You ({lang}): {heard}")
                if STOP_WORDS.match(heard):
                    say("Very well.")
                    break
                # Whisper often writes Kannada speech in Latin letters; tell the
                # brain the spoken language so it answers in Kannada script.
                prompt = f"[spoken in Kannada] {heard}" if lang == "kn" else heard
                reply = brain.ask(prompt, on_tool=lambda n: print(f"  (using {n})"))
                say(reply)
                if push_to_talk:
                    break
        except KeyboardInterrupt:
            say("Shutting down. Goodbye.")
            break
        except Exception as e:  # noqa: BLE001 - stay alive
            log.exception("Loop error: %s", e)


def _startup_report() -> None:
    skipped = tools.load_all()
    log.info("Loaded %d tools: %s", len(tools.REGISTRY), ", ".join(sorted(tools.REGISTRY)))
    for s in skipped:
        log.warning("Ability unavailable: %s", s)
