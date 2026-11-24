"""PC control for Windows 10/11: apps, websites, files, keyboard, volume, media,
screenshots, power, PowerShell and the clipboard.

Windows-only and GUI libraries (pycaw, comtypes, ctypes.windll, pyautogui) are
imported inside the functions that need them, so this module imports cleanly
on Linux for tests. Tools that cannot work off Windows say so.
"""

from __future__ import annotations

import difflib
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path

from . import tool

IS_WINDOWS = sys.platform == "win32"
NEEDS_WINDOWS = "Error: this needs Windows."
# Hide the console window of child processes on Windows.
_NO_WINDOW = 0x08000000 if IS_WINDOWS else 0


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9+ ]", "", s.lower().replace("_", " ").replace("-", " ")).strip()


def _open_target(target: str) -> None:
    """Open a file, folder, URI or App-Paths program name with the OS default handler."""
    if IS_WINDOWS:
        os.startfile(target)  # noqa: S606 - ShellExecute, no shell parsing
    elif sys.platform == "darwin":
        subprocess.Popen(["open", target])
    else:
        subprocess.Popen(["xdg-open", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --------------------------------------------------------------------------- apps

# friendly name -> (ShellExecute target or None, Start Menu name to search, process names)
APPS: dict[str, tuple[str | None, str | None, tuple[str, ...]]] = {
    "chrome": ("chrome", "Google Chrome", ("chrome.exe",)),
    "edge": ("msedge", "Microsoft Edge", ("msedge.exe",)),
    "firefox": ("firefox", "Firefox", ("firefox.exe",)),
    "notepad": ("notepad", None, ("notepad.exe",)),
    "calculator": ("calculator:", None, ("CalculatorApp.exe", "calc.exe")),
    "file explorer": ("explorer", None, ()),
    "settings": ("ms-settings:", None, ("SystemSettings.exe",)),
    "task manager": ("taskmgr", None, ("Taskmgr.exe",)),
    "control panel": ("control", None, ()),
    "command prompt": ("cmd", None, ("cmd.exe",)),
    "powershell": ("powershell", None, ("powershell.exe",)),
    "terminal": ("wt", "Terminal", ("WindowsTerminal.exe",)),
    "paint": ("mspaint", "Paint", ("mspaint.exe",)),
    "snipping tool": ("ms-screenclip:", "Snipping Tool", ("SnippingTool.exe",)),
    "camera": ("microsoft.windows.camera:", "Camera", ("WindowsCamera.exe",)),
    "photos": ("ms-photos:", "Photos", ("Photos.exe",)),
    "store": ("ms-windows-store:", "Microsoft Store", ("WinStore.App.exe",)),
    "mail": ("outlookmail:", "Mail", ("HxOutlook.exe", "olk.exe")),
    "outlook": ("outlook", "Outlook", ("OUTLOOK.EXE", "olk.exe")),
    "calendar": ("outlookcal:", "Calendar", ()),
    "clock": ("ms-clock:", "Clock", ("Time.exe",)),
    "spotify": ("spotify:", "Spotify", ("Spotify.exe",)),
    "whatsapp": ("whatsapp:", "WhatsApp", ("WhatsApp.exe", "WhatsApp.Root.exe")),
    "telegram": ("tg:", "Telegram", ("Telegram.exe",)),
    "discord": (None, "Discord", ("Discord.exe",)),
    "zoom": (None, "Zoom", ("Zoom.exe",)),
    "teams": ("msteams:", "Microsoft Teams", ("ms-teams.exe", "Teams.exe")),
    "vs code": ("code", "Visual Studio Code", ("Code.exe",)),
    "word": ("winword", "Word", ("WINWORD.EXE",)),
    "excel": ("excel", "Excel", ("EXCEL.EXE",)),
    "powerpoint": ("powerpnt", "PowerPoint", ("POWERPNT.EXE",)),
    "onenote": ("onenote", "OneNote", ("ONENOTE.EXE",)),
    "vlc": ("vlc", "VLC media player", ("vlc.exe",)),
    "steam": ("steam:", "Steam", ("steam.exe",)),
}
ALIASES = {
    "google chrome": "chrome", "browser": "chrome", "microsoft edge": "edge",
    "calc": "calculator", "explorer": "file explorer", "files": "file explorer",
    "file manager": "file explorer", "my computer": "file explorer", "this pc": "file explorer",
    "windows settings": "settings", "cmd": "command prompt", "windows terminal": "terminal",
    "vscode": "vs code", "visual studio code": "vs code", "code": "vs code",
    "microsoft word": "word", "ms word": "word", "microsoft excel": "excel", "ms excel": "excel",
    "ppt": "powerpoint", "microsoft teams": "teams", "whats app": "whatsapp",
    "microsoft store": "store", "snip": "snipping tool", "screen snip": "snipping tool",
    "task mgr": "task manager",
}


def resolve_app(name: str) -> str | None:
    """Friendly name -> key in APPS, or None."""
    n = _norm(name)
    for prefix in ("the ", "my "):
        if n.startswith(prefix):
            n = n[len(prefix):]
    for suffix in (" app", " application", " program"):
        if n.endswith(suffix):
            n = n[: -len(suffix)]
    if n in APPS:
        return n
    if n in ALIASES:
        return ALIASES[n]
    if n.replace(" ", "") in {k.replace(" ", "") for k in APPS}:
        return next(k for k in APPS if k.replace(" ", "") == n.replace(" ", ""))
    return None


def start_menu_dirs() -> list[Path]:
    dirs = []
    for var in ("ProgramData", "APPDATA"):
        base = os.environ.get(var)
        if base:
            dirs.append(Path(base) / "Microsoft" / "Windows" / "Start Menu" / "Programs")
    return [d for d in dirs if d.is_dir()]


_SKIP_SHORTCUT = re.compile(r"uninstall|readme|help|documentation|release notes|website|license",
                            re.I)


def find_shortcut(name: str, dirs: list[Path] | None = None, cutoff: float = 0.6) -> Path | None:
    """Best-matching Start Menu .lnk/.url/.appref-ms for a name, or None."""
    want = _norm(name)
    if not want:
        return None
    shortcuts: dict[str, Path] = {}
    for d in dirs if dirs is not None else start_menu_dirs():
        for p in d.rglob("*"):
            if p.suffix.lower() in (".lnk", ".url", ".appref-ms") and not _SKIP_SHORTCUT.search(p.stem):
                shortcuts.setdefault(_norm(p.stem), p)
    if not shortcuts:
        return None
    if want in shortcuts:
        return shortcuts[want]
    best, best_score = None, 0.0
    for stem, p in shortcuts.items():
        score = difflib.SequenceMatcher(None, want, stem).ratio()
        words = stem.split()
        if want in words or stem.startswith(want + " "):
            score = max(score, 0.9)  # "word" -> "Word 2016", "zoom" -> "Zoom Workplace"
        elif len(want) >= 4 and want in stem:
            score = max(score, 0.75)
        # Prefer shorter names on ties ("Excel" over "Excel Viewer Helper").
        if score > best_score or (score == best_score and best and len(stem) < len(_norm(best.stem))):
            best, best_score = p, score
    return best if best_score >= cutoff else None


@tool("open_app", "Open an application on the computer by its everyday name, e.g. chrome, edge, "
      "notepad, calculator, file explorer, settings, spotify, vs code, word, excel, whatsapp, "
      "camera, or any installed program.",
      {"name": {"type": "string", "description": "The app's name as the user said it."}},
      ["name"])
def open_app(name: str) -> str:
    if not IS_WINDOWS:
        return NEEDS_WINDOWS
    key = resolve_app(name)
    label = key or name.strip()
    if key:
        target, menu_name, _ = APPS[key]
        if target:
            try:
                _open_target(target)
                return f"Opening {label}."
            except OSError:
                pass
        lnk = find_shortcut(menu_name or key)
        if lnk:
            _open_target(str(lnk))
            return f"Opening {label}."
    lnk = find_shortcut(name)
    if lnk:
        _open_target(str(lnk))
        return f"Opening {lnk.stem}."
    try:
        _open_target(name.strip())
        return f"Opening {label}."
    except OSError:
        return f"Error: I couldn't find an app called {name}."


# Never kill these: Windows itself, or Jarvis.
_PROTECTED = {"system", "system idle process", "csrss.exe", "wininit.exe", "winlogon.exe",
              "services.exe", "lsass.exe", "smss.exe", "svchost.exe", "dwm.exe", "explorer.exe",
              "fontdrvhost.exe", "registry", "memory compression"}


def _matching_processes(name: str):
    import psutil  # noqa: PLC0415

    key = resolve_app(name)
    wanted = {p.lower() for p in APPS[key][2]} if key else set()
    plain = _norm(name).replace(" ", "")
    me = os.getpid()
    found = []
    for proc in psutil.process_iter(["name", "pid"]):
        pname = (proc.info["name"] or "").lower()
        if not pname or pname in _PROTECTED or proc.info["pid"] == me:
            continue
        stem = pname.removesuffix(".exe")
        if pname in wanted or (plain and (stem == plain or (len(plain) >= 4 and stem.startswith(plain)))):
            found.append(proc)
    return found


def _close_windows_by_title(name: str) -> int:
    try:
        import pygetwindow as gw  # noqa: PLC0415
    except ImportError:
        return 0
    n = 0
    for w in gw.getWindowsWithTitle(name):
        if w.title.strip():
            try:
                w.close()
                n += 1
            except Exception:  # noqa: BLE001
                pass
    return n


@tool("close_app", "Close a running application by its name or window title.",
      {"name": {"type": "string", "description": "App name or part of its window title."}},
      ["name"], confirm=True, describe=lambda a: f"close {a.get('name')}")
def close_app(name: str) -> str:
    try:
        import psutil  # noqa: PLC0415
    except ImportError:
        return "Error: the psutil package is not installed."
    if resolve_app(name) == "file explorer" or _norm(name) in ("explorer", "windows"):
        return "I won't close Windows Explorer, it runs the taskbar and desktop."
    procs = _matching_processes(name)
    if procs:
        for p in procs:
            try:
                p.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        _, alive = psutil.wait_procs(procs, timeout=3)
        for p in alive:
            try:
                p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return f"Closed {name}."
    if IS_WINDOWS and _close_windows_by_title(name):
        return f"Closed the {name} window."
    return f"{name} doesn't seem to be running."


# --------------------------------------------------------------------------- web

_URL_RE = re.compile(r"^(https?://|www\.)\S+$|^[\w-]+(\.[\w-]+)*\.[a-z]{2,}(:\d+)?(/\S*)?$", re.I)
_YT_RE = re.compile(r"^(?:play|watch|search|find|show me)?\s*(.+?)\s+on\s+youtube$"
                    r"|^(?:search\s+)?youtube\s+(?:for\s+)?(.+)$", re.I)


def website_url(text: str) -> str:
    """Turn what the user said into the URL to open."""
    t = text.strip().strip('"\'')
    if _URL_RE.match(t) and " " not in t:
        return t if re.match(r"^https?://", t, re.I) else "https://" + t
    m = _YT_RE.match(t)
    if m:
        q = (m.group(1) or m.group(2)).strip()
        return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q)
    if t.lower() in ("youtube", "gmail", "google", "facebook", "instagram", "netflix", "amazon",
                     "twitter", "x", "linkedin", "reddit", "github", "wikipedia", "chatgpt"):
        known = {"gmail": "mail.google.com", "x": "x.com", "twitter": "x.com",
                 "chatgpt": "chatgpt.com", "wikipedia": "www.wikipedia.org"}
        return "https://" + known.get(t.lower(), f"www.{t.lower()}.com")
    q = re.sub(r"^(?:search|google)\s+(?:for\s+)?", "", t, flags=re.I)
    return "https://www.google.com/search?q=" + urllib.parse.quote_plus(q)


@tool("open_website", "Open a website in the default browser, or search Google or YouTube. "
      "Accepts a URL ('github.com'), a site name ('gmail'), 'play <song> on youtube', or any "
      "search words.",
      {"url_or_query": {"type": "string", "description": "A URL, site name, or what to search."}},
      ["url_or_query"])
def open_website(url_or_query: str) -> str:
    url = website_url(url_or_query)
    if not webbrowser.open(url):
        return "Error: I couldn't open the browser."
    if "youtube.com/results" in url:
        return f"Here are YouTube results for {urllib.parse.unquote_plus(url.split('=', 1)[1])}."
    if "google.com/search" in url:
        return f"Searching Google for {urllib.parse.unquote_plus(url.split('=', 1)[1])}."
    return f"Opening {urllib.parse.urlparse(url).netloc.removeprefix('www.')}."


# --------------------------------------------------------------------------- files

_USER_FOLDERS = ("Desktop", "Documents", "Downloads", "Pictures", "Videos", "Music")
_last_matches: list[Path] = []


def user_folder(name: str) -> Path:
    """Path of a user folder, following OneDrive redirection when it exists."""
    home = Path.home()
    canon = next((f for f in _USER_FOLDERS if f.lower() == name.lower().rstrip("s") + "s"
                  or f.lower() == name.lower()), name)
    for base in (os.environ.get("OneDrive"), str(home / "OneDrive")):
        if base and (Path(base) / canon).is_dir():
            return Path(base) / canon
    return home / canon


def _search_roots(folder: str) -> list[Path]:
    f = (folder or "home").strip()
    if f.lower() in ("home", "all", "everywhere", "", "user", "my files"):
        roots = [user_folder(n) for n in _USER_FOLDERS]
    elif Path(os.path.expanduser(f)).is_absolute():
        roots = [Path(os.path.expanduser(f))]
    else:
        roots = [user_folder(f)]
    seen, out = set(), []
    for r in roots:
        if r.is_dir() and r.resolve() not in seen:
            seen.add(r.resolve())
            out.append(r)
    return out


def search_files(query: str, roots: list[Path], max_depth: int = 5, time_limit: float = 4.0,
                 limit: int = 5) -> list[Path]:
    """Fuzzy filename search; returns the best matches, best first."""
    q = _norm(query)
    if not q:
        return []
    q_words = q.split()
    deadline = time.monotonic() + time_limit
    scored: list[tuple[float, Path]] = []
    for root in roots:
        base_depth = len(root.parts)
        for dirpath, dirnames, filenames in os.walk(root):
            if time.monotonic() > deadline:
                break
            depth = len(Path(dirpath).parts) - base_depth
            dirnames[:] = [] if depth >= max_depth else [
                d for d in dirnames if not d.startswith((".", "$", "__")) and d.lower() not in
                ("node_modules", "appdata", "site-packages", "venv", ".venv")]
            for entry in filenames + dirnames:
                name = _norm(Path(entry).stem if entry in filenames else entry)
                if not name:
                    continue
                score = difflib.SequenceMatcher(None, q, name).ratio()
                if q in name:
                    score = max(score, 0.8 + 0.2 * len(q) / len(name))
                elif all(w in name for w in q_words):
                    score = max(score, 0.75)
                if score >= 0.55:
                    scored.append((score, Path(dirpath) / entry))
    scored.sort(key=lambda s: (-s[0], len(str(s[1]))))
    out, seen = [], set()
    for _, p in scored:
        if p not in seen:
            seen.add(p)
            out.append(p)
        if len(out) >= limit:
            break
    return out


def _speak_path(p: Path) -> str:
    try:
        return "~" + os.sep + str(p.relative_to(Path.home()))
    except ValueError:
        return str(p)


@tool("find_files", "Find files or folders by (approximate) name in the user's Desktop, "
      "Documents, Downloads, Pictures, Videos and Music. Returns numbered matches that "
      "open_path can open by number.",
      {"query": {"type": "string", "description": "Part of the file name, e.g. 'budget 2024'."},
       "folder": {"type": "string", "description": "'home' for all user folders (default), a "
                  "folder name like 'downloads', or a full path."}},
      ["query"])
def find_files(query: str, folder: str = "home") -> str:
    global _last_matches
    roots = _search_roots(folder)
    if not roots:
        return f"Error: I couldn't find the folder {folder}."
    _last_matches = search_files(query, roots)
    if not _last_matches:
        return f"I didn't find anything matching {query}."
    lines = [f"{i}. {p.name} in {_speak_path(p.parent)}" for i, p in enumerate(_last_matches, 1)]
    return f"Found {len(lines)}: " + "; ".join(lines) + "."


@tool("open_path", "Open a file or folder with its default program. Accepts a full path, a "
      "user folder name ('downloads'), a number from the last find_files results, or a file "
      "name to search for.",
      {"path": {"type": "string", "description": "Path, folder name, result number, or name."}},
      ["path"])
def open_path(path: str) -> str:
    p = path.strip().strip('"\'')
    target: Path | None = None
    m = re.fullmatch(r"(?:number\s+)?(\d+)|(first|second|third|fourth|fifth)(?:\s+one)?", p, re.I)
    if m and _last_matches:
        idx = int(m.group(1)) - 1 if m.group(1) else \
            ["first", "second", "third", "fourth", "fifth"].index(m.group(2).lower())
        if not 0 <= idx < len(_last_matches):
            return f"Error: there are only {len(_last_matches)} results."
        target = _last_matches[idx]
    elif Path(os.path.expanduser(os.path.expandvars(p))).exists():
        target = Path(os.path.expanduser(os.path.expandvars(p)))
    elif p.lower().rstrip("s") + "s" in [f.lower() for f in _USER_FOLDERS] or \
            p.lower() in [f.lower() for f in _USER_FOLDERS]:
        target = user_folder(p)
    else:
        hits = search_files(p, _search_roots("home"), limit=1)
        target = hits[0] if hits else None
    if target is None or not target.exists():
        return f"Error: I couldn't find {path}."
    try:
        _open_target(str(target))
    except OSError as e:
        return f"Error: couldn't open {target.name}: {e}"
    return f"Opening {target.name}."


# --------------------------------------------------------------------------- keyboard

def _pyautogui():
    import pyautogui  # noqa: PLC0415 - needs a display, so import lazily
    pyautogui.FAILSAFE = True
    return pyautogui


_KEY_ALIASES = {"control": "ctrl", "windows": "win", "window": "win", "start": "win",
                "super": "win", "cmd": "win", "escape": "esc", "return": "enter",
                "del": "delete", "ins": "insert", "pgup": "pageup", "page up": "pageup",
                "pgdn": "pagedown", "page down": "pagedown", "spacebar": "space",
                "plus": "+", "option": "alt", "caps lock": "capslock", "print screen": "printscreen",
                "arrow up": "up", "arrow down": "down", "arrow left": "left", "arrow right": "right",
                "backspace": "backspace", "back space": "backspace"}


def parse_keys(keys: str) -> list[str]:
    """'Ctrl + Shift + Esc' -> ['ctrl', 'shift', 'esc']."""
    parts = [k.strip().lower() for k in re.split(r"\s*\+\s*|\s+and\s+", keys.strip()) if k.strip()]
    if keys.strip().endswith("++"):
        parts.append("+")
    return [_KEY_ALIASES.get(k, k) for k in parts]


@tool("type_text", "Type text at the cursor, as if on the keyboard, into whatever window is "
      "focused.",
      {"text": {"type": "string", "description": "The exact text to type."}},
      ["text"])
def type_text(text: str) -> str:
    if len(text) > 5000:
        return "Error: that's too much text to type at once."
    try:
        pg = _pyautogui()
    except Exception as e:  # noqa: BLE001
        return f"Error: keyboard control isn't available: {e}"
    if text.isascii():
        pg.write(text, interval=0.01)
    else:  # pyautogui can't type non-ASCII; paste it, then restore the clipboard.
        import pyperclip  # noqa: PLC0415
        old = pyperclip.paste()
        pyperclip.copy(text)
        pg.hotkey("ctrl", "v")
        time.sleep(0.2)
        pyperclip.copy(old)
    return "Typed it."


@tool("press_keys", "Press a key or keyboard shortcut, e.g. 'enter', 'ctrl+s', 'alt+tab', "
      "'win+d', 'ctrl+shift+esc'.",
      {"keys": {"type": "string", "description": "Keys joined with '+'."},
       "times": {"type": "integer", "description": "How many times to press it (default 1)."}},
      ["keys"])
def press_keys(keys: str, times: int = 1) -> str:
    combo = parse_keys(keys)
    try:
        pg = _pyautogui()
    except Exception as e:  # noqa: BLE001
        return f"Error: keyboard control isn't available: {e}"
    bad = [k for k in combo if k not in pg.KEYBOARD_KEYS]
    if not combo or bad:
        return f"Error: I don't know the key {', '.join(bad) or keys}."
    for _ in range(max(1, min(int(times), 50))):
        pg.hotkey(*combo) if len(combo) > 1 else pg.press(combo[0])
    return f"Pressed {keys}."


# --------------------------------------------------------------------------- audio

def _endpoint_volume():
    import comtypes  # noqa: PLC0415
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # noqa: PLC0415

    try:
        comtypes.CoInitialize()  # tools may run off the main thread
    except OSError:
        pass
    dev = AudioUtilities.GetSpeakers()
    ev = getattr(dev, "EndpointVolume", None)  # pycaw >= 2025 wraps the device
    if ev is None:
        from ctypes import POINTER, cast  # noqa: PLC0415
        iface = dev.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        ev = cast(iface, POINTER(IAudioEndpointVolume))
    return ev


def _volume_keys(action: str, level: int | None) -> str:
    pg = _pyautogui()
    if action == "set":  # each key press is about 2 percent
        pg.press("volumedown", presses=50, interval=0.01)
        pg.press("volumeup", presses=round((level or 0) / 2), interval=0.01)
        return f"Volume set to about {level} percent."
    if action in ("mute", "unmute"):
        pg.press("volumemute")
        return "Toggled mute."
    step = max(1, round((level or 10) / 2))
    pg.press("volumeup" if action == "up" else "volumedown", presses=step, interval=0.01)
    return f"Volume {action}."


@tool("volume", "Change or check the computer's speaker volume.",
      {"action": {"type": "string", "enum": ["up", "down", "mute", "unmute", "set", "get"]},
       "level": {"type": "integer", "description": "For 'set': 0-100. For up/down: how many "
                 "percent to change (default 10)."}},
      ["action"])
def volume(action: str, level: int | None = None) -> str:
    action = action.lower().strip()
    if action not in ("up", "down", "mute", "unmute", "set", "get"):
        return "Error: action must be up, down, mute, unmute, set or get."
    if action == "set" and level is None:
        return "Error: tell me what level to set, from 0 to 100."
    if level is not None:
        level = max(0, min(100, int(level)))
    if not IS_WINDOWS:
        return NEEDS_WINDOWS
    try:
        ev = _endpoint_volume()
    except Exception:  # noqa: BLE001 - pycaw missing or COM failure: use media keys
        if action == "get":
            return "Error: I can't read the volume without the pycaw package."
        try:
            return _volume_keys(action, level)
        except Exception as e:  # noqa: BLE001
            return f"Error: couldn't change the volume: {e}"
    current = round(ev.GetMasterVolumeLevelScalar() * 100)
    if action == "get":
        muted = " and muted" if ev.GetMute() else ""
        return f"Volume is at {current} percent{muted}."
    if action == "mute":
        ev.SetMute(1, None)
        return "Muted."
    if action == "unmute":
        ev.SetMute(0, None)
        return f"Unmuted, volume is {current} percent."
    new = level if action == "set" else current + (level or 10) * (1 if action == "up" else -1)
    new = max(0, min(100, new))
    ev.SetMasterVolumeLevelScalar(new / 100, None)
    if new > 0:
        ev.SetMute(0, None)
    return f"Volume {new} percent."


_MEDIA_KEYS = {"play_pause": "playpause", "play": "playpause", "pause": "playpause",
               "resume": "playpause", "next": "nexttrack", "skip": "nexttrack",
               "previous": "prevtrack", "prev": "prevtrack", "back": "prevtrack", "stop": "stop"}


@tool("media_control", "Control whatever media is playing (Spotify, YouTube, etc.): play/pause, "
      "next track, previous track, stop.",
      {"action": {"type": "string", "enum": ["play_pause", "next", "previous", "stop"]}},
      ["action"])
def media_control(action: str) -> str:
    key = _MEDIA_KEYS.get(action.lower().strip().replace(" ", "_"))
    if not key:
        return "Error: action must be play_pause, next, previous or stop."
    try:
        _pyautogui().press(key)
    except Exception as e:  # noqa: BLE001
        return f"Error: media keys aren't available: {e}"
    return {"playpause": "Done.", "nexttrack": "Next track.", "prevtrack": "Previous track.",
            "stop": "Stopped."}[key]


# --------------------------------------------------------------------------- screen

@tool("screenshot", "Take a screenshot of the whole screen and save it to Pictures\\Jarvis.")
def screenshot() -> str:
    folder = user_folder("Pictures") / "Jarvis"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"screenshot-{datetime.now():%Y-%m-%d_%H-%M-%S}.png"
    try:
        from PIL import ImageGrab  # noqa: PLC0415
        ImageGrab.grab(all_screens=IS_WINDOWS).save(path)
    except Exception:  # noqa: BLE001
        try:
            _pyautogui().screenshot(str(path))
        except Exception as e:  # noqa: BLE001
            return f"Error: couldn't take a screenshot: {e}"
    return f"Screenshot saved to {path}."


# --------------------------------------------------------------------------- power

def _shutdown_exe(*args: str) -> str:
    if not IS_WINDOWS:
        return NEEDS_WINDOWS
    r = subprocess.run(["shutdown", *args], capture_output=True, text=True,
                       creationflags=_NO_WINDOW, timeout=15)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout).strip().splitlines()
        return f"Error: {msg[-1] if msg else 'shutdown failed'}"
    return ""


@tool("lock_pc", "Lock the computer (go to the sign-in screen).",
      confirm=True, describe=lambda a: "lock the computer")
def lock_pc() -> str:
    if not IS_WINDOWS:
        return NEEDS_WINDOWS
    import ctypes  # noqa: PLC0415
    if not ctypes.windll.user32.LockWorkStation():
        return "Error: Windows refused to lock."
    return "Locked."


@tool("sleep_pc", "Put the computer to sleep.",
      confirm=True, describe=lambda a: "put the computer to sleep")
def sleep_pc() -> str:
    if not IS_WINDOWS:
        return NEEDS_WINDOWS
    import ctypes  # noqa: PLC0415
    # (hibernate=False, force=True, wake_events_disabled=False). If hibernation is enabled in
    # Windows this may hibernate instead; `powercfg /h off` makes it a true sleep.
    ctypes.windll.powrprof.SetSuspendState(False, True, False)
    return "Good night."


def _minutes(m) -> int:
    try:
        return max(0, min(24 * 60, int(float(m or 0))))
    except (TypeError, ValueError):
        return 0


def _when(m: int) -> str:
    return "now" if m == 0 else f"in {m} minute{'s' if m != 1 else ''}"


@tool("shutdown_pc", "Shut down the computer, now or after a delay. It can be cancelled with "
      "cancel_shutdown.",
      {"delay_minutes": {"type": "number", "description": "Minutes to wait first (default 1)."}},
      confirm=True, describe=lambda a: f"shut down the computer {_when(_minutes(a.get('delay_minutes', 1)))}")
def shutdown_pc(delay_minutes: float = 1) -> str:
    m = _minutes(delay_minutes)
    err = _shutdown_exe("/s", "/t", str(max(m * 60, 5)))
    return err or f"Shutting down {_when(m)}. Say cancel shutdown to stop it."


@tool("restart_pc", "Restart the computer, now or after a delay.",
      {"delay_minutes": {"type": "number", "description": "Minutes to wait first (default 0)."}},
      confirm=True, describe=lambda a: f"restart the computer {_when(_minutes(a.get('delay_minutes', 0)))}")
def restart_pc(delay_minutes: float = 0) -> str:
    m = _minutes(delay_minutes)
    err = _shutdown_exe("/r", "/t", str(max(m * 60, 5)))
    return err or f"Restarting {_when(m)}."


@tool("cancel_shutdown", "Cancel a scheduled shutdown or restart.")
def cancel_shutdown() -> str:
    # Not confirmed on purpose: it only undoes a pending power action, and a confirmation
    # prompt could make it arrive too late.
    err = _shutdown_exe("/a")
    if err and ("1116" in err or "not in progress" in err.lower()):
        return "There was no shutdown scheduled."
    return err or "Shutdown cancelled."


# --------------------------------------------------------------------------- PowerShell

_DRIVE_ROOT = r"""(?:^|[\s'"(=,])(?:[a-z]:[\\/]?\*?|[\\/]\*?|~[\\/]?\*?|\$env:(?:systemdrive|userprofile|systemroot|windir|homedrive)[\\/]?\*?|[a-z]:[\\/](?:windows|users|program files(?: \(x86\))?|programdata)[\\/]?\*?|[\\/](?:bin|boot|etc|home|lib|usr|var)[\\/]?\*?)(?=$|[\s'");,])"""
_BLOCKED = [
    (r"\bformat-volume\b|\bformat\s+[a-z]:|\bmkfs(\.\w+)?\b", "formats a drive"),
    (r"\bdiskpart\b|\bclear-disk\b|\binitialize-disk\b|\bremove-partition\b|\bresize-partition\b"
     r"|\bset-partition\b", "changes disk partitions"),
    (r"\bdd\s+if=|\bof=/dev/", "writes raw disk data"),
    (r"\bbcdedit\b|\bbootrec\b|\bbcdboot\b", "changes the boot setup"),
    (r"\bcipher\s+/w\b|\bsdelete\b", "wipes free space"),
    (r"\bvssadmin\b.*\bdelete\b|\bwmic\b.*shadowcopy.*\bdelete\b|\bwbadmin\b.*\bdelete\b",
     "deletes backups or restore points"),
    (r"\breg(\.exe)?\s+delete\s+hk(lm|ey_local_machine)|remove-item\s+.*hklm:", "deletes system registry keys"),
    (r"\btakeown\b.*\b[a-z]:\\windows|\bicacls\b.*\b[a-z]:\\(windows)?\s.*(/grant|/reset|/remove)",
     "changes system file ownership"),
    (r"-(e|ec|enc|encodedcommand)\s+[a-z0-9+/=]{16,}", "hides its contents in an encoded command"),
    (r"\b(iex|invoke-expression)\b.*\b(iwr|irm|invoke-webrequest|invoke-restmethod|downloadstring|curl|wget)\b"
     r"|\b(iwr|irm|invoke-webrequest|invoke-restmethod|downloadstring|curl|wget)\b.*\|\s*(iex|invoke-expression|sh|bash)\b",
     "downloads and runs code from the internet"),
    (r"\bstop-computer\b|\brestart-computer\b|\bshutdown(\.exe)?\s+[/-][srp]", "shuts down the PC "
     "(use the shutdown or restart tool instead)"),
    (r":\(\)\s*\{\s*:\|:&\s*\};:", "is a fork bomb"),
    (r"\bset-mppreference\b.*-disable|\buninstall-windowsfeature\b|\bdisable-computerrestore\b",
     "weakens system protection"),
]
_REMOVE_VERB = re.compile(r"\b(remove-item|rm|rmdir|rd|del|erase|ri)\b", re.I)
_RECURSIVE = re.compile(r"(?:^|\s)(-r\b|-rf\b|-fr\b|-recurse\b|/s\b|-force\b|/q\b)", re.I)


def command_block_reason(command: str) -> str | None:
    """Why a PowerShell command is refused outright, or None if it may run (after confirmation)."""
    c = command.lower()
    for pattern, why in _BLOCKED:
        if re.search(pattern, c, re.I):
            return why
    # Recursive / forced delete aimed at a drive root, the home folder or a system folder.
    for stmt in re.split(r"[;|&\n]+", c):
        if _REMOVE_VERB.search(stmt) and _RECURSIVE.search(stmt) and re.search(_DRIVE_ROOT, stmt, re.I):
            return "deletes a whole drive, your home folder or a system folder"
    return None


def _powershell() -> str | None:
    if IS_WINDOWS:
        return shutil.which("powershell") or shutil.which("pwsh") or "powershell"
    return shutil.which("pwsh")


@tool("run_command", "Run a PowerShell command on the computer and report its output. Use for "
      "tasks no other tool covers. Prefer read-only commands; never use it for things another "
      "tool does.",
      {"command": {"type": "string", "description": "The exact PowerShell command."}},
      ["command"], confirm=True, describe=lambda a: f"run this PowerShell command: {a.get('command')}")
def run_command(command: str) -> str:
    if not command.strip():
        return "Error: the command is empty."
    why = command_block_reason(command)
    if why:
        return f"I won't run that, it {why}."
    exe = _powershell()
    if not exe:
        return NEEDS_WINDOWS
    try:
        r = subprocess.run([exe, "-NoProfile", "-NonInteractive", "-Command", command],
                           capture_output=True, text=True, timeout=60, creationflags=_NO_WINDOW,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return "Error: the command took longer than 60 seconds, so I stopped it."
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    text = out + (("\n" if out else "") + "Errors: " + err if err else "")
    if not text:
        text = "Done, no output." if r.returncode == 0 else f"It failed with exit code {r.returncode}."
    elif r.returncode != 0 and not err:
        text += f"\n(exit code {r.returncode})"
    return text if len(text) <= 2000 else text[:2000] + " ... (output truncated)"


# --------------------------------------------------------------------------- clipboard

@tool("clipboard_read", "Read the text currently on the clipboard.")
def clipboard_read() -> str:
    try:
        import pyperclip  # noqa: PLC0415
        text = pyperclip.paste()
    except Exception as e:  # noqa: BLE001
        return f"Error: I can't reach the clipboard: {str(e).split(". ")[0]}"
    if not text:
        return "The clipboard is empty."
    return text if len(text) <= 2000 else text[:2000] + " ... (truncated)"


@tool("clipboard_write", "Put text on the clipboard so the user can paste it.",
      {"text": {"type": "string", "description": "The text to copy."}},
      ["text"])
def clipboard_write(text: str) -> str:
    try:
        import pyperclip  # noqa: PLC0415
        pyperclip.copy(text)
    except Exception as e:  # noqa: BLE001
        return f"Error: I can't reach the clipboard: {str(e).split(". ")[0]}"
    return "Copied to the clipboard."
