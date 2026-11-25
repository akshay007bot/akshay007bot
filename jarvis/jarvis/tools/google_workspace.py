"""Gmail and Google Calendar, through Google's free APIs.

Setup (once): follow docs/GOOGLE_SETUP.md, then run

    python -m jarvis.tools.google_workspace --login

The OAuth client file lives at settings.google_credentials and the signed-in
token is cached at DATA_DIR/google_token.json. Without them (or without the
packages in requirements-google.txt) every tool here answers with a friendly
"not connected yet" message instead of failing.
"""

from __future__ import annotations

import base64
import html
import logging
import re
import threading
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr
from zoneinfo import ZoneInfo

from ..config import DATA_DIR, settings
from . import tool

log = logging.getLogger("jarvis.google")

TOKEN_FILE = DATA_DIR / "google_token.json"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",  # read, label, compose and send
    "https://www.googleapis.com/auth/calendar",
]
SETUP_DOC = "docs/GOOGLE_SETUP.md"

_lock = threading.RLock()
_services: dict[str, object] = {}
_last_results: list[str] = []  # message ids from the last check_email, for "read the second one"


class NotConnected(Exception):
    """Raised when Google can't be used yet; the message is safe to speak."""


# --------------------------------------------------------------------------- auth

def _libs():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as e:
        raise NotConnected(
            "Google isn't connected yet: the Google libraries aren't installed. Run "
            f"pip install -r requirements-google.txt, then see {SETUP_DOC}.") from e
    return Request, Credentials, InstalledAppFlow, build


def login(force: bool = False):
    """Run the browser sign-in and cache the token. Returns the credentials."""
    Request, Credentials, InstalledAppFlow, build = _libs()
    if not settings.google_credentials.exists():
        raise NotConnected(f"Google isn't connected yet — see {SETUP_DOC}. "
                           f"(No OAuth client file at {settings.google_credentials}.)")
    if force and TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
    flow = InstalledAppFlow.from_client_secrets_file(str(settings.google_credentials), SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True, timeout_seconds=300,
                                  authorization_prompt_message="Opening your browser to sign in to Google: {url}",
                                  success_message="Jarvis is connected to Google. You can close this tab.")
    if not creds:
        raise NotConnected("Google sign-in didn't finish. Please try again.")
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    _services.clear()
    return creds


def _creds(interactive: bool = False):  # tools never pop a browser mid-conversation
    Request, Credentials, InstalledAppFlow, build = _libs()
    creds = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception:  # noqa: BLE001 - corrupt or old token: sign in again
            creds = None
        if creds and not set(SCOPES) <= set(creds.scopes or SCOPES):
            creds = None  # permissions changed since the token was made
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
            return creds
        except Exception as e:  # noqa: BLE001 - RefreshError: revoked or 7-day testing expiry
            log.info("Google token refresh failed: %s", e)
            creds = None
    if not settings.google_credentials.exists():
        raise NotConnected(f"Google isn't connected yet — see {SETUP_DOC}.")
    if not interactive:
        raise NotConnected("Google needs you to sign in. Double-click google-login.bat in the Jarvis folder, then ask again.")
    try:
        return login()
    except NotConnected:
        raise
    except Exception as e:  # noqa: BLE001
        raise NotConnected("I couldn't sign in to Google (" + str(e)[:120] + "). "
                           "Run: python -m jarvis.tools.google_workspace --login") from e


def _svc(name: str):
    with _lock:
        if name not in _services:
            *_, build = _libs()
            creds = _creds()
            version = "v1" if name == "gmail" else "v3"
            _services[name] = build(name, version, credentials=creds, cache_discovery=False)
        return _services[name]


def _gmail():
    return _svc("gmail").users()


def _calendar():
    return _svc("calendar")


def _google(fn):
    """Turn "not connected" and API errors into speakable text."""
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except NotConnected as e:
            return str(e)
        except Exception as e:  # noqa: BLE001
            status = getattr(getattr(e, "resp", None), "status", None)
            if status in (401, 403):
                _services.clear()
                return ("Google refused that request. Try signing in again with "
                        "python -m jarvis.tools.google_workspace --login.")
            if e.__class__.__name__ in ("RefreshError",):
                _services.clear()
                return "Your Google sign-in has expired. Run: python -m jarvis.tools.google_workspace --login"
            log.exception("Google call failed")
            return f"Error: Google said {e.__class__.__name__}: {str(e)[:200]}"
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


# --------------------------------------------------------------------------- helpers

def _tz() -> ZoneInfo:
    try:
        return ZoneInfo(settings.timezone)
    except Exception:  # noqa: BLE001
        return ZoneInfo("UTC")


def _now() -> datetime:
    return datetime.now(_tz())


def _clock(dt: datetime) -> str:
    h = dt.hour % 12 or 12
    ampm = "AM" if dt.hour < 12 else "PM"
    return f"{h} {ampm}" if dt.minute == 0 else f"{h}:{dt.minute:02d} {ampm}"


def _speak_day(d) -> str:
    days = (d - _now().date()).days
    if days == 0:
        return "today"
    if days == 1:
        return "tomorrow"
    if 1 < days < 7:
        return f"on {d:%A}"
    return f"on {d:%A}, {d.day} {d:%B}"


def _parse_when(when: str, default_hour: int = 9) -> datetime | None:
    from .reminders import parse_when  # shared natural-language parser
    return parse_when(when, default_hour=default_hour)


def _has_time(when: str) -> bool:
    from .reminders import has_time
    return has_time(when)


def _short(text: str, n: int) -> str:
    text = re.sub(r"\s+", " ", html.unescape(text or "")).strip()
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"


def _name(header_from: str) -> str:
    name, addr = parseaddr(header_from or "")
    return name.strip('" ') or addr or "someone"


def _headers(msg: dict) -> dict[str, str]:
    return {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}


def _b64(data: str) -> str:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", "replace")


def _body_text(payload: dict) -> str:
    """Best plain-text body of a Gmail message payload."""
    plain, htmls = [], []

    def walk(p):
        mime = p.get("mimeType", "")
        data = p.get("body", {}).get("data")
        if data and mime == "text/plain":
            plain.append(_b64(data))
        elif data and mime == "text/html":
            htmls.append(_b64(data))
        for part in p.get("parts", []) or []:
            walk(part)

    walk(payload)
    if plain:
        text = "\n".join(plain)
    elif htmls:
        h = re.sub(r"(?is)<(script|style).*?</\1>", " ", "\n".join(htmls))
        h = re.sub(r"(?i)<br\s*/?>|</p>|</div>", "\n", h)
        text = html.unescape(re.sub(r"<[^>]+>", " ", h))
    else:
        text = ""
    # Drop quoted history and signatures so it reads well aloud.
    lines = []
    for line in text.splitlines():
        if line.strip().startswith(">"):
            continue
        if re.match(r"^\s*On .+wrote:\s*$", line) or line.strip() in ("--", "-- "):
            break
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"https?://\S{40,}", "[link]", text)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", text)).strip()


def _is_email(s: str) -> bool:
    return bool(re.fullmatch(r"[^@\s<>,]+@[^@\s<>,]+\.[^@\s<>,]+", s.strip()))


def _candidates(name: str) -> list[tuple[str, str]]:
    """(display name, address) pairs from recent mail that match a person's name."""
    words = [w.lower() for w in re.findall(r"\w+", name)]
    if not words:
        return []
    g = _gmail()
    res = g.messages().list(userId="me", q=f'from:"{name}" OR to:"{name}" OR cc:"{name}"',
                            maxResults=25).execute()
    seen: dict[str, list] = {}
    for m in res.get("messages", []):
        msg = g.messages().get(userId="me", id=m["id"], format="metadata",
                               metadataHeaders=["From", "To", "Cc"]).execute()
        hdr = _headers(msg)
        for disp, addr in getaddresses([hdr.get("from", ""), hdr.get("to", ""), hdr.get("cc", "")]):
            addr = addr.strip().lower()
            if not addr or "@" not in addr:
                continue
            hay = f"{disp} {addr}".lower()
            if all(w in hay for w in words):
                entry = seen.setdefault(addr, [disp or addr, 0])
                entry[1] += 1
                if disp and entry[0] == addr:
                    entry[0] = disp
    return [(d, a) for a, (d, _) in sorted(seen.items(), key=lambda kv: -kv[1][1])]


def _resolve(to: str) -> tuple[list[str], str | None]:
    """Return (addresses, problem). ``problem`` is a speakable question when ambiguous."""
    out = []
    for part in [p.strip() for p in re.split(r"[,;]| and ", to) if p.strip()]:
        _, addr = parseaddr(part)
        if addr and _is_email(addr):
            out.append(part if "<" in part else addr)
            continue
        cands = _candidates(part)
        if not cands:
            return [], (f"I couldn't find an email address for {part} in your recent mail. "
                        "What's their email address?")
        if len(cands) > 1:
            opts = "; ".join(f"{d} at {a}" for d, a in cands[:4])
            return [], f"I found more than one address for {part}: {opts}. Which one should I use?"
        d, a = cands[0]
        out.append(f"{d} <{a}>" if d and d != a else a)
    return out, None


def _send_raw(msg: EmailMessage, thread_id: str | None = None, draft: bool = False):
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body = {"raw": raw}
    if thread_id:
        body["threadId"] = thread_id
    g = _gmail()
    if draft:
        return g.drafts().create(userId="me", body={"message": body}).execute()
    return g.messages().send(userId="me", body=body).execute()


def _compose(to: list[str], subject: str, body: str) -> EmailMessage:
    msg = EmailMessage()
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject or "(no subject)"
    msg.set_content(body or "")
    return msg


# --------------------------------------------------------------------------- Gmail tools

@tool("check_email", "Summarise emails in the user's Gmail: sender, subject and a short snippet. "
      "Defaults to unread inbox mail. Uses Gmail search syntax, e.g. 'from:amazon', "
      "'is:unread newer_than:1d', 'subject:invoice'.",
      {"query": {"type": "string", "description": "Gmail search query. Default 'is:unread in:inbox'."},
       "max": {"type": "integer", "description": "How many to summarise (default 5, max 10)."}})
@_google
def check_email(query: str = "is:unread in:inbox", max: int = 5) -> str:  # noqa: A002 - name from spec
    n = min(10, int(max or 5))
    g = _gmail()
    res = g.messages().list(userId="me", q=query or "is:unread in:inbox", maxResults=n).execute()
    msgs = res.get("messages", [])
    _last_results[:] = [m["id"] for m in msgs]
    if not msgs:
        return "No unread email in your inbox." if "is:unread" in (query or "") else "No emails match that."
    total = res.get("resultSizeEstimate", len(msgs))
    lines = []
    for i, m in enumerate(msgs, 1):
        msg = g.messages().get(userId="me", id=m["id"], format="metadata",
                               metadataHeaders=["From", "Subject", "Date"]).execute()
        h = _headers(msg)
        lines.append(f"{i}. From {_name(h.get('from'))}: {_short(h.get('subject') or 'no subject', 80)}"
                     f" — {_short(msg.get('snippet', ''), 110)}")
    kind = "unread email" if "is:unread" in (query or "") else "matching email"
    head = (f"You have {total} {kind}{'s' if total != 1 else ''}"
            + (f"; here are the first {len(msgs)}" if total > len(msgs) else "") + ". ")
    return head + " ".join(lines)


_ORDINALS = {"first": 1, "1st": 1, "latest": 1, "newest": 1, "last": -1, "second": 2, "2nd": 2,
             "third": 3, "3rd": 3, "fourth": 4, "4th": 4, "fifth": 5, "5th": 5, "sixth": 6,
             "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "one": 1, "two": 2,
             "three": 3, "four": 4, "five": 5}


@tool("read_email", "Read out one email in full (trimmed). `which` is a number or ordinal from the "
      "last check_email results ('2', 'second', 'latest'), or words from the subject/sender.",
      {"which": {"type": "string", "description": "e.g. '1', 'second', 'the one from Rahul', 'invoice'."}},
      ["which"])
@_google
def read_email(which: str) -> str:
    g = _gmail()
    key = str(which).strip().lower()
    key = re.sub(r"^(the|email|mail|message|number|no\.?)\s+", "", key)
    key = re.sub(r"\s+(one|email|mail|message)$", "", key).strip()
    idx = int(key) if key.isdigit() else _ORDINALS.get(key)
    msg_id = None
    if idx is not None:
        if not _last_results:
            res = g.messages().list(userId="me", q="in:inbox", maxResults=10).execute()
            _last_results[:] = [m["id"] for m in res.get("messages", [])]
        if not _last_results:
            return "Your inbox is empty."
        if idx == -1:
            idx = len(_last_results)
        if not 1 <= idx <= len(_last_results):
            return f"I only have {len(_last_results)} emails from the last check."
        msg_id = _last_results[idx - 1]
    else:
        term = re.sub(r"^(from|by)\s+", "", key)
        for q in (f"subject:({term})", f"from:({term})", term):
            res = g.messages().list(userId="me", q=q, maxResults=1).execute()
            if res.get("messages"):
                msg_id = res["messages"][0]["id"]
                break
        if not msg_id:
            return f"I couldn't find an email matching '{which}'."
    msg = g.messages().get(userId="me", id=msg_id, format="full").execute()
    h = _headers(msg)
    text = _body_text(msg.get("payload", {})) or msg.get("snippet", "")
    if len(text) > 1500:
        text = text[:1500].rsplit(" ", 1)[0] + "… That's the gist; the rest is longer."
    if "UNREAD" in msg.get("labelIds", []):
        try:
            g.messages().modify(userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute()
        except Exception:  # noqa: BLE001 - marking read is a nicety
            pass
    return f"Email from {_name(h.get('from'))}, subject {h.get('subject') or 'none'}. {text}"


@tool("find_email_address", "Look up a person's email address from recent Gmail messages by name. "
      "Use before send_email when the user gives a name, so they can confirm the address.",
      {"name": {"type": "string", "description": "Person's name, e.g. 'Rahul' or 'Priya Sharma'."}},
      ["name"])
@_google
def find_email_address(name: str) -> str:
    cands = _candidates(name)
    if not cands:
        return f"I couldn't find {name} in your recent email."
    if len(cands) == 1:
        d, a = cands[0]
        return f"{d}: {a}."
    return f"Possible matches for {name}: " + "; ".join(f"{d} at {a}" for d, a in cands[:5]) + "."


@tool("send_email", "Send an email from the user's Gmail. `to` can be an email address or a name "
      "found in recent mail (if a name matches several people, the candidates are returned and "
      "nothing is sent).",
      {"to": {"type": "string", "description": "Email address(es) or a name; separate several with commas."},
       "subject": {"type": "string"},
       "body": {"type": "string", "description": "The full email text, signed off as the user."}},
      ["to", "subject", "body"], confirm=True,
      describe=lambda a: f"send an email to {a.get('to')} about {a.get('subject') or 'nothing in particular'}")
@_google
def send_email(to: str, subject: str, body: str) -> str:
    addrs, problem = _resolve(to)
    if problem:
        return problem + " Nothing was sent."
    _send_raw(_compose(addrs, subject, body))
    return f"Sent to {', '.join(addrs)}."


@tool("reply_to_latest_from", "Reply to the most recent email from a sender (name or address), "
      "in the same thread.",
      {"sender": {"type": "string", "description": "Name or email address of who wrote to the user."},
       "body": {"type": "string", "description": "The reply text."}},
      ["sender", "body"], confirm=True,
      describe=lambda a: f"reply to the latest email from {a.get('sender')} saying: {_short(a.get('body', ''), 120)}")
@_google
def reply_to_latest_from(sender: str, body: str) -> str:
    g = _gmail()
    who = sender.strip()
    q = f"from:({who}) -in:sent -in:drafts"
    res = g.messages().list(userId="me", q=q, maxResults=1).execute()
    if not res.get("messages"):
        return f"I couldn't find any email from {sender}."
    orig = g.messages().get(userId="me", id=res["messages"][0]["id"], format="metadata",
                            metadataHeaders=["From", "Reply-To", "Subject", "Message-ID", "References"]).execute()
    h = _headers(orig)
    subject = h.get("subject", "")
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}".strip()
    to = h.get("reply-to") or h.get("from")
    msg = _compose([to], subject, body)
    if h.get("message-id"):
        msg["In-Reply-To"] = h["message-id"]
        msg["References"] = (h.get("references", "") + " " + h["message-id"]).strip()
    _send_raw(msg, thread_id=orig.get("threadId"))
    return f"Replied to {_name(h.get('from'))} about {subject[4:] if subject.lower().startswith('re:') else subject}."


@tool("draft_email", "Save an email as a Gmail draft (does not send it).",
      {"to": {"type": "string", "description": "Email address(es) or a name."},
       "subject": {"type": "string"},
       "body": {"type": "string"}},
      ["to", "subject", "body"])
@_google
def draft_email(to: str, subject: str, body: str) -> str:
    addrs, problem = _resolve(to)
    if problem:
        return problem + " I haven't saved the draft yet."
    _send_raw(_compose(addrs, subject, body), draft=True)
    return f"Draft saved to {', '.join(addrs)}. It's in your Gmail drafts."


# --------------------------------------------------------------------------- Calendar tools

def _event_start(ev: dict) -> tuple[datetime, bool]:
    s = ev.get("start", {})
    if "dateTime" in s:
        return datetime.fromisoformat(s["dateTime"].replace("Z", "+00:00")).astimezone(_tz()), False
    d = datetime.fromisoformat(s.get("date", "1970-01-01"))
    return d.replace(tzinfo=_tz()), True


def _events(start: datetime, end: datetime, limit: int = 50) -> list[dict]:
    res = _calendar().events().list(
        calendarId="primary", timeMin=start.isoformat(), timeMax=end.isoformat(),
        singleEvents=True, orderBy="startTime", maxResults=limit).execute()
    return [e for e in res.get("items", []) if e.get("status") != "cancelled"]


def _speak_event(ev: dict) -> str:
    dt, all_day = _event_start(ev)
    title = _short(ev.get("summary") or "untitled event", 80)
    where = f" at {_short(ev['location'], 40)}" if ev.get("location") else ""
    return f"all day, {title}" if all_day else f"{_clock(dt)}, {title}{where}"


@tool("todays_schedule", "What's on the user's Google Calendar for one day.",
      {"day": {"type": "string", "description": "'today' (default), 'tomorrow', 'friday', '5 december'..."}})
@_google
def todays_schedule(day: str = "today") -> str:
    day = (day or "today").strip()
    if day.lower() == "today":
        d = _now()
    else:
        d = _parse_when(day, default_hour=12)
        if d is None:
            return f"Error: I couldn't work out which day '{day}' is."
    start = d.replace(hour=0, minute=0, second=0, microsecond=0)
    evs = _events(start, start + timedelta(days=1))
    when = _speak_day(start.date())
    if not evs:
        return f"Your calendar is clear {when}."
    items = "; ".join(_speak_event(e) for e in evs[:12])
    return f"{when.capitalize()} you have {len(evs)} event{'s' if len(evs) != 1 else ''}: {items}."


@tool("upcoming_events", "List the user's Google Calendar events for the next few days.",
      {"days": {"type": "integer", "description": "How many days ahead (default 7)."}})
@_google
def upcoming_events(days: int = 7) -> str:
    days = max(1, min(60, int(days or 7)))
    now = _now()
    evs = _events(now, now + timedelta(days=days), limit=40)
    if not evs:
        return f"Nothing on your calendar in the next {days} days."
    by_day: dict = {}
    for e in evs:
        dt, _ = _event_start(e)
        by_day.setdefault(dt.date(), []).append(_speak_event(e))
    parts = [f"{_speak_day(d).capitalize()}: " + "; ".join(v) for d, v in list(by_day.items())[:10]]
    return f"You have {len(evs)} event{'s' if len(evs) != 1 else ''} in the next {days} days. " + ". ".join(parts) + "."


@tool("add_event", "Add an event to the user's Google Calendar. A day with no time becomes an all-day event.",
      {"title": {"type": "string"},
       "when": {"type": "string", "description": "e.g. 'tomorrow at 3pm', 'next monday 10am', 'friday'."},
       "duration_minutes": {"type": "integer", "description": "Length in minutes (default 60)."},
       "description": {"type": "string", "description": "Optional notes."}},
      ["title", "when"], confirm=True,
      describe=lambda a: f"add '{a.get('title')}' to your calendar for {a.get('when')}")
@_google
def add_event(title: str, when: str, duration_minutes: int = 60, description: str = "") -> str:
    start = _parse_when(when)
    if start is None:
        return f"Error: I couldn't work out when '{when}' is."
    tz = str(_tz())
    body: dict = {"summary": title, "description": description or ""}
    if _has_time(when):
        mins = max(5, int(duration_minutes or 60))
        end = start + timedelta(minutes=mins)
        body["start"] = {"dateTime": start.replace(microsecond=0).isoformat(), "timeZone": tz}
        body["end"] = {"dateTime": end.replace(microsecond=0).isoformat(), "timeZone": tz}
        length = (f"for {mins // 60} hour{'s' if mins // 60 != 1 else ''}" if mins % 60 == 0
                  else f"for {mins} minutes")
        spoken = f"{_speak_day(start.date())} at {_clock(start)} {length}"
    else:
        body["start"] = {"date": start.date().isoformat()}
        body["end"] = {"date": (start.date() + timedelta(days=1)).isoformat()}
        spoken = f"{_speak_day(start.date())}, all day"
    _calendar().events().insert(calendarId="primary", body=body).execute()
    return f"Added {title} {spoken}."


# --------------------------------------------------------------------------- CLI

def _main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="python -m jarvis.tools.google_workspace",
                                description="Connect Jarvis to your Google account (Gmail + Calendar).")
    p.add_argument("--login", action="store_true", help="sign in with your browser and save the token")
    p.add_argument("--logout", action="store_true", help="forget the saved Google token")
    p.add_argument("--status", action="store_true", help="check whether Google is connected")
    a = p.parse_args(argv)
    if a.logout:
        TOKEN_FILE.unlink(missing_ok=True)
        print("Signed out: the saved Google token was deleted.")
        return 0
    try:
        if a.login:
            print(f"Using OAuth client file: {settings.google_credentials}")
            login(force=True)
            print(f"Token saved to {TOKEN_FILE}")
        elif not a.status:
            p.print_help()
            return 0
        creds = _creds(interactive=False)
        _services.clear()
        email = _gmail().getProfile(userId="me").execute().get("emailAddress")
        cal = _calendar().calendarList().get(calendarId="primary").execute().get("summary")
        print(f"Connected as {email}. Gmail OK. Calendar OK ({cal}).")
        if creds and not creds.refresh_token:
            print("Warning: no refresh token was issued; you may need to sign in again later.")
        return 0
    except NotConnected as e:
        print(e)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(_main())
