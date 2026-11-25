"""Long-term memory: facts about the user that Jarvis keeps between sessions."""

from __future__ import annotations

import json
import threading
from datetime import datetime

from ..config import DATA_DIR
from . import tool

_FILE = DATA_DIR / "memory.json"
_lock = threading.Lock()


def _load() -> list[dict]:
    try:
        return json.loads(_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(items: list[dict]) -> None:
    tmp = _FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(_FILE)


def all_facts() -> list[str]:
    return [m["fact"] for m in _load()]


@tool("remember", "Save a lasting fact about the user or their preferences (names, birthdays, "
      "likes, routines, where things are). Use whenever the user says 'remember...' or shares "
      "something clearly worth keeping.",
      {"fact": {"type": "string", "description": "The fact, written as a full sentence."}},
      ["fact"])
def remember(fact: str) -> str:
    with _lock:
        items = _load()
        if any(m["fact"].lower() == fact.lower() for m in items):
            return "I already knew that."
        items.append({"fact": fact, "saved": datetime.now().isoformat(timespec="seconds")})
        _save(items)
    return "Noted."


@tool("forget", "Delete remembered facts that contain the given words.",
      {"about": {"type": "string", "description": "Words identifying the fact(s) to forget."}},
      ["about"], confirm=True, describe=lambda a: f"forget everything I remember about '{a['about']}'")
def forget(about: str) -> str:
    with _lock:
        items = _load()
        keep = [m for m in items if about.lower() not in m["fact"].lower()]
        _save(keep)
    n = len(items) - len(keep)
    return f"Forgot {n} fact(s)." if n else "I had nothing saved about that."


@tool("recall", "Search remembered facts. Facts are also shown in your instructions, so use this "
      "only for an explicit lookup.",
      {"query": {"type": "string", "description": "Words to search for; empty lists everything."}})
def recall(query: str = "") -> str:
    hits = [f for f in all_facts() if query.lower() in f.lower()]
    return "\n".join(hits) if hits else "Nothing saved about that."
