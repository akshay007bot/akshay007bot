"""Entry point:  python -m jarvis [--text | --ptt] [--verbose]"""

import argparse
import logging
import sys

from . import assistant


def _utf8_console() -> None:
    """Kannada text would raise UnicodeEncodeError on a cp1252/cp437 console or a redirected pipe."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main() -> None:
    _utf8_console()
    ap = argparse.ArgumentParser(prog="jarvis", description="Your personal voice assistant.")
    ap.add_argument("--text", action="store_true", help="type instead of talking")
    ap.add_argument("--ptt", action="store_true", help="push-to-talk (Enter) instead of the wake word")
    ap.add_argument("--verbose", "-v", action="store_true", help="show detailed logs")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING,
                        format="%(asctime)s %(name)s %(levelname)s: %(message)s", datefmt="%H:%M:%S")
    if a.text:
        assistant.run_text()
    else:
        assistant.run_voice(push_to_talk=a.ptt)


if __name__ == "__main__":
    main()
