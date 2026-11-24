"""Reminders, alarms and timers. Fully local: no account, no internet.

Reminders live in SQLite at DATA_DIR/reminders.db, so they survive restarts.
A daemon thread (started on import, once) wakes up at least every
CHECK_INTERVAL seconds, and right away when a new reminder is added, and
announces whatever is due through ``notify.announce``. On Windows it also
tries to pop a toast notification (win11toast or plyer, both optional).
Reminders that came due while Jarvis was not running are announced at the
next start as "While you were away...".
"""

from __future__ import annotations

import logging
import re
import sqlite3
import sys
import threading
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .. import notify
from ..config import DATA_DIR, settings
from . import tool

log = logging.getLogger("jarvis.reminders")

DB_FILE = DATA_DIR / "reminders.db"
CHECK_INTERVAL = 15.0  # seconds; the loop also wakes early for the next due item
ALARM_REPEATS = 3
ALARM_GAP = 4.0  # seconds between repeated alarm announcements

_db_lock = threading.Lock()
_wake = threading.Event()
_start_lock = threading.Lock()
_thread: threading.Thread | None = None
_started_at = time.time()


# --------------------------------------------------------------------------- time

def _tz() -> ZoneInfo:
    try:
        return ZoneInfo(settings.timezone)
    except Exception:  # noqa: BLE001 - bad tz name or no tzdata: fall back to UTC
        return ZoneInfo("UTC")


def _now() -> datetime:
    return datetime.now(_tz())


_TIME_HINT = re.compile(
    r"\d{1,2}\s*(:|\.)\s*\d{2}|\d\s*(am|pm|a\.m\.|p\.m\.)|\b(noon|midnight|morning|afternoon|"
    r"evening|night|tonight)\b|\bin\s+(a|an|\d+|half|one|two|three|few)\b|\bat\s+\d|\bo'?clock\b",
    re.I)


def has_time(text: str) -> bool:
    """True if a natural-language phrase names a time of day (not just a date)."""
    return bool(_TIME_HINT.search(text or ""))


def _clean(text: str) -> str:
    t = " " + text.strip().lower() + " "
    subs = [
        (r"\bhalf an hour\b", "30 minutes"), (r"\ban hour and a half\b", "90 minutes"),
        (r"\ba couple of\b", "2"), (r"\ba few\b", "3"), (r"\bmins?\b", "minutes"),
        (r"\bhrs?\b", "hours"), (r"\bsecs?\b", "seconds"),
        (r"\bthis (morning|afternoon|evening)\b", r"today \1"),
        (r"\ba\.m\.", "am"), (r"\bp\.m\.", "pm"), (r"\bo'?clock\b", ""),
    ]
    for pat, rep in subs:
        t = re.sub(pat, rep, t)
    t = re.sub(r"^\s*(on|at|for|by)\s+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def parse_when(when: str, default_hour: int = 9) -> datetime | None:
    """Parse "in 10 minutes", "tomorrow at 7am", "at 6:30 pm", "next monday 9am"...

    Returns an aware datetime in settings.timezone, in the future when the
    phrase allows it, or None if it cannot be understood. A date with no
    time ("tomorrow", "friday") defaults to ``default_hour`` o'clock.
    """
    import dateparser  # local import so a missing package only breaks this call

    tz = _tz()
    text = _clean(when or "")
    if not text:
        return None
    night = False
    if re.search(r"\btonight\b|\bat night\b", text):
        night = True
        text = re.sub(r"\btonight\b|\bat night\b", " ", text).strip() or "today 9 pm"
        if not re.search(r"\b(am|pm)\b", text):
            text = re.sub(r"\b(?:at\s+)?(\d{1,2})(:\d{2})?\b", r"\1\2 pm", text, count=1)
        if "today" not in text and "tomorrow" not in text:
            text = "today " + text
    cfg = {
        "TIMEZONE": str(tz),
        "TO_TIMEZONE": str(tz),
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future",
    }
    dt = dateparser.parse(text, languages=["en"], settings=cfg)
    if dt is None:
        try:
            from dateparser.search import search_dates
            found = search_dates(text, languages=["en"], settings=cfg)
            if found:
                dt = found[-1][1]
        except Exception:  # noqa: BLE001
            dt = None
    if dt is None:
        return None
    dt = dt.astimezone(tz)
    if night and dt.hour < 12:
        dt += timedelta(hours=12)
    timed = has_time(when)
    if not timed:
        dt = dt.replace(hour=default_hour, minute=0, second=0, microsecond=0)
    now = _now()
    relative = bool(re.search(r"\bin\b|\bago\b|\bfrom now\b|\blater\b", text))
    if dt <= now and not relative:
        # "at 6:30 pm" said at 8 pm means tomorrow; "monday" means next monday.
        names_day = re.search(r"\b(today|tomorrow)\b|\d{4}|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|"
                              r"oct|nov|dec)[a-z]*\b", text)
        if not names_day or (not timed and "today" not in text):
            for _ in range(7):
                if dt > now:
                    break
                dt += timedelta(days=1)
    return dt


def _clock(dt: datetime) -> str:
    h = dt.hour % 12 or 12
    ampm = "AM" if dt.hour < 12 else "PM"
    return f"{h} {ampm}" if dt.minute == 0 else f"{h}:{dt.minute:02d} {ampm}"


def speak_day(dt: datetime) -> str:
    """'today', 'tomorrow', 'on Friday', or 'on Friday, 5 December'."""
    days = (dt.date() - _now().date()).days
    if days == 0:
        return "today"
    if days == 1:
        return "tomorrow"
    if days == -1:
        return "yesterday"
    if 1 < days < 7:
        return f"on {dt:%A}"
    return f"on {dt:%A}, {dt.day} {dt:%B}" + (f" {dt.year}" if dt.year != _now().year else "")


def speak_when(dt: datetime) -> str:
    secs = (dt - _now()).total_seconds()
    if 0 <= secs < 3600:
        mins = max(1, round(secs / 60)) if secs >= 60 else None
        rel = f"in {mins} minute{'s' if mins != 1 else ''}" if mins else f"in {max(1, round(secs))} seconds"
        return f"{rel}, at {_clock(dt)}"
    return f"{speak_day(dt)} at {_clock(dt)}"


# --------------------------------------------------------------------------- storage

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_FILE, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        due REAL NOT NULL,            -- unix timestamp
        kind TEXT NOT NULL DEFAULT 'reminder',   -- reminder | alarm | timer
        created REAL NOT NULL,
        done INTEGER NOT NULL DEFAULT 0          -- 0 pending, 1 announced, 2 cancelled
    )""")
    return c


def _add(message: str, due: datetime, kind: str) -> int:
    with _db_lock, _conn() as c:
        cur = c.execute("INSERT INTO reminders (message, due, kind, created) VALUES (?, ?, ?, ?)",
                        (message, due.timestamp(), kind, time.time()))
        rid = cur.lastrowid
    _wake.set()
    return int(rid)


def _pending() -> list[sqlite3.Row]:
    with _db_lock, _conn() as c:
        return c.execute("SELECT * FROM reminders WHERE done = 0 ORDER BY due").fetchall()


def _mark(ids: list[int], state: int) -> None:
    if not ids:
        return
    with _db_lock, _conn() as c:
        c.executemany("UPDATE reminders SET done = ? WHERE id = ?", [(state, i) for i in ids])


# --------------------------------------------------------------------------- firing

def _toast(title: str, text: str) -> None:
    if sys.platform != "win32":
        return
    try:
        from win11toast import notify as toast  # type: ignore
        toast(title, text, app_id="Jarvis")
        return
    except Exception:  # noqa: BLE001 - optional
        pass
    try:
        from plyer import notification  # type: ignore
        notification.notify(title=title, message=text, app_name="Jarvis", timeout=10)
    except Exception:  # noqa: BLE001 - optional
        pass


def _say(text: str) -> None:
    try:
        notify.announce(text)
    except Exception:  # noqa: BLE001 - a broken speaker must not kill the scheduler
        log.exception("announce failed")


def _label(row) -> str:
    return row["message"] or ""


def _fire(row) -> None:
    kind, msg = row["kind"], _label(row)
    if kind == "alarm":
        text = f"Alarm: {msg}" if msg else f"Alarm! It's {_clock(_now())}."
        _toast("Jarvis alarm", msg or text)
        for i in range(ALARM_REPEATS):
            _say(text)
            if i < ALARM_REPEATS - 1:
                time.sleep(ALARM_GAP)
    elif kind == "timer":
        text = f"Timer done: {msg}" if msg else "Your timer is done."
        _toast("Jarvis timer", text)
        _say(text)
    else:
        _toast("Jarvis reminder", msg)
        _say(f"Reminder: {msg}")


def _missed_summary(rows) -> str:
    parts = []
    for r in rows:
        when = datetime.fromtimestamp(r["due"], _tz())
        what = {"alarm": "an alarm", "timer": "a timer"}.get(r["kind"], "a reminder")
        detail = f": {r['message']}" if r["message"] else ""
        parts.append(f"{what} {speak_day(when)} at {_clock(when)}{detail}")
    if len(parts) == 1:
        return f"While you were away, you missed {parts[0]}."
    return f"While you were away, you missed {len(parts)} things. " + "; ".join(parts) + "."


def _check_once(first: bool = False) -> float:
    """Announce what is due. Returns seconds until the next pending item (or inf)."""
    now = time.time()
    rows = _pending()
    due = [r for r in rows if r["due"] <= now]
    if due:
        # Due before this process started (with a little slack) = missed while away.
        missed = [r for r in due if r["due"] < _started_at - 60] if first else []
        missed_ids = {r["id"] for r in missed}
        fresh = [r for r in due if r["id"] not in missed_ids]
        _mark([r["id"] for r in due], 1)
        if missed:
            _say(_missed_summary(missed))
        for r in fresh:
            threading.Thread(target=_fire, args=(r,), daemon=True, name="jarvis-reminder-fire").start()
    upcoming = [r["due"] for r in rows if r["due"] > now]
    return (min(upcoming) - now) if upcoming else float("inf")


def _loop() -> None:
    first = True
    while True:
        try:
            wait = _check_once(first)
        except Exception:  # noqa: BLE001
            log.exception("reminder check failed")
            wait = CHECK_INTERVAL
        first = False
        _wake.wait(timeout=max(0.2, min(CHECK_INTERVAL, wait)))
        _wake.clear()


def start() -> None:
    """Start the scheduler thread (safe to call any number of times)."""
    global _thread
    with _start_lock:
        if _thread is not None and _thread.is_alive():
            return
        _thread = threading.Thread(target=_loop, daemon=True, name="jarvis-reminders")
        _thread.start()


# --------------------------------------------------------------------------- tools

def _bad_when(when: str) -> str:
    return (f"Error: I couldn't work out when '{when}' is. Try something like 'in 10 minutes', "
            "'tomorrow at 7 am' or 'next Monday at 9'.")


@tool("set_reminder", "Remind the user about something at a time. Works offline; reminders survive "
      "restarts. Use for 'remind me to...' requests.",
      {"message": {"type": "string", "description": "What to remind about, e.g. 'call mom'."},
       "when": {"type": "string", "description": "Natural-language time, e.g. 'in 10 minutes', "
                "'tomorrow at 7am', 'at 6:30 pm', 'next monday 9am'."}},
      ["message", "when"])
def set_reminder(message: str, when: str) -> str:
    dt = parse_when(when)
    if dt is None:
        return _bad_when(when)
    if dt <= _now() - timedelta(seconds=5):
        return f"Error: {speak_day(dt)} at {_clock(dt)} is already in the past."
    _add(message.strip(), dt, "reminder")
    return f"Okay, I'll remind you {speak_when(dt)}: {message.strip()}."


@tool("set_alarm", "Set an alarm for a time of day (rings by announcing it out loud three times).",
      {"when": {"type": "string", "description": "e.g. '6 am', 'tomorrow at 5:45', 'in 20 minutes'."},
       "label": {"type": "string", "description": "Optional name, e.g. 'gym'."}},
      ["when"])
def set_alarm(when: str, label: str = "") -> str:
    dt = parse_when(when, default_hour=7)
    if dt is None:
        return _bad_when(when)
    _add(label.strip(), dt, "alarm")
    w = speak_when(dt)
    return f"Alarm set {w if w.startswith('in ') else 'for ' + w}" + (f", labelled {label.strip()}." if label.strip() else ".")


@tool("set_timer", "Start a countdown timer.",
      {"minutes": {"type": "number", "description": "Length in minutes (may be fractional, 0.5 = 30 seconds)."},
       "label": {"type": "string", "description": "Optional name, e.g. 'pasta'."}},
      ["minutes"])
def set_timer(minutes: float, label: str = "") -> str:
    try:
        minutes = float(minutes)
    except (TypeError, ValueError):
        return "Error: minutes must be a number."
    if minutes <= 0:
        return "Error: the timer needs a positive length."
    dt = _now() + timedelta(minutes=minutes)
    _add(label.strip(), dt, "timer")
    if minutes < 1:
        length = f"{round(minutes * 60)} second"
    elif minutes >= 120 and minutes % 60 == 0:
        length = f"{int(minutes // 60)} hour"
    else:
        length = f"{minutes:g} minute"
    return f"{length} timer started" + (f" for {label.strip()}." if label.strip() else ".")


def _describe_row(r) -> str:
    when = datetime.fromtimestamp(r["due"], _tz())
    kind = r["kind"]
    what = r["message"] or ("alarm" if kind == "alarm" else "timer" if kind == "timer" else "")
    prefix = {"alarm": "alarm", "timer": "timer"}.get(kind, "")
    lead = f"{prefix} " if prefix and r["message"] else ""
    return f"number {r['id']}, {lead}{what}, {speak_when(when)}"


@tool("list_reminders", "List the user's pending reminders, alarms and timers.")
def list_reminders() -> str:
    rows = _pending()
    if not rows:
        return "You have no reminders, alarms or timers set."
    items = [_describe_row(r) for r in rows[:10]]
    more = f" And {len(rows) - 10} more." if len(rows) > 10 else ""
    n = len(rows)
    return f"You have {n} pending: " + "; ".join(items) + "." + more


@tool("cancel_reminder", "Cancel a pending reminder, alarm or timer by its number, by words in its "
      "message, by kind ('alarm', 'timer'), or 'all'.",
      {"text_or_id": {"type": "string", "description": "Reminder number, words from it, 'alarm', 'timer', or 'all'."}},
      ["text_or_id"], confirm=True,
      describe=lambda a: ("cancel all your reminders" if str(a.get("text_or_id", "")).strip().lower() == "all"
                          else f"cancel the reminder '{a.get('text_or_id', '')}'"))
def cancel_reminder(text_or_id: str) -> str:
    key = str(text_or_id).strip().lower().lstrip("#")
    key = re.sub(r"^(number|reminder|no\.?)\s*", "", key) if re.search(r"\d", key) else key
    rows = _pending()
    if not rows:
        return "There's nothing to cancel."
    if key in ("all", "everything", "all reminders"):
        hits = rows
    elif key.isdigit():
        hits = [r for r in rows if r["id"] == int(key)]
    elif key in ("alarm", "alarms", "timer", "timers"):
        hits = [r for r in rows if r["kind"] == key.rstrip("s")]
    else:
        hits = [r for r in rows if key in (r["message"] or "").lower()]
        if not hits:
            words = [w for w in re.findall(r"\w+", key) if len(w) > 2 and w not in ("the", "about", "reminder")]
            hits = [r for r in rows if words and all(w in (r["message"] or "").lower() for w in words)]
    if not hits:
        return f"I couldn't find a pending reminder matching '{text_or_id}'."
    _mark([r["id"] for r in hits], 2)
    _wake.set()
    if len(hits) == 1:
        r = hits[0]
        return f"Cancelled {r['kind']} {('about ' + r['message']) if r['message'] else 'number ' + str(r['id'])}."
    return f"Cancelled {len(hits)} reminders."


start()
