"""Download the wake-word and speech-recognition models ahead of time.

Run by install.ps1 so the first "Hey Jarvis" isn't a multi-minute wait.
    python -m jarvis.setup_models
"""

from __future__ import annotations


def main() -> None:
    from .config import settings
    print(f"Downloading wake word model ({settings.wake_word})...")
    try:
        from .voice import wake
        wake._get_model()
        print("  ok")
    except Exception as e:  # noqa: BLE001
        print(f"  failed: {e} (it will retry on first start)")
    print(f"Downloading speech model ({settings.whisper_model}); this can take a few minutes...")
    try:
        from .voice import stt
        stt._load_model()
        print("  ok")
    except Exception as e:  # noqa: BLE001
        print(f"  failed: {e} (it will retry on first start)")


if __name__ == "__main__":
    main()
