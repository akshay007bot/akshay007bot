"""Lets background jobs (reminders, alarms) talk to the user.

Tool modules call ``announce("...")``. The running assistant installs the real
speaker with ``set_announcer``; until then messages are printed.
"""

from __future__ import annotations

import threading
from typing import Callable

_lock = threading.Lock()
_announcer: Callable[[str], None] = lambda text: print(f"\n[JARVIS] {text}")


def set_announcer(fn: Callable[[str], None]) -> None:
    global _announcer
    _announcer = fn


def announce(text: str) -> None:
    with _lock:  # never talk over ourselves
        _announcer(text)
