"""Smart home control through Home Assistant's local REST API (free).

Configure HOME_ASSISTANT_URL (e.g. http://homeassistant.local:8123) and
HOME_ASSISTANT_TOKEN (a long-lived access token) in .env.
See docs/SMART_HOME_SETUP.md.

Everyday devices (lights, fans, switches, AC, TV) are controlled straight away.
Security devices (locks, garage doors / covers, alarm panels) go through
``secure_device``, which asks the user to confirm first.
"""

from __future__ import annotations

import difflib
import re
import time

import requests

from ..config import settings
from . import tool

NOT_CONNECTED = "Smart home isn't connected yet — see docs/SMART_HOME_SETUP.md."
TIMEOUT = 10

CONTROL_DOMAINS = ("light", "switch", "fan", "climate", "cover", "media_player", "lock",
                   "input_boolean", "humidifier", "vacuum", "water_heater", "alarm_control_panel")
LIST_DOMAINS = ("light", "switch", "fan", "climate", "cover", "media_player", "lock",
                "sensor", "binary_sensor", "alarm_control_panel", "vacuum")
SECURE_DOMAINS = {"lock", "cover", "alarm_control_panel"}

_DOMAIN_WORDS = {
    "lights": "light", "light": "light", "lamps": "light", "switches": "switch",
    "switch": "switch", "plugs": "switch", "fans": "fan", "fan": "fan", "ac": "climate",
    "acs": "climate", "climate": "climate", "thermostat": "climate", "covers": "cover",
    "curtains": "cover", "blinds": "cover", "garage": "cover", "cover": "cover",
    "tv": "media_player", "tvs": "media_player", "media": "media_player",
    "media_players": "media_player", "media_player": "media_player", "speakers": "media_player",
    "sensors": "sensor", "sensor": "sensor", "binary_sensor": "binary_sensor",
    "locks": "lock", "lock": "lock", "alarm": "alarm_control_panel",
    "alarm_control_panel": "alarm_control_panel", "vacuum": "vacuum",
}

_LABELS = {"light": "Lights", "switch": "Switches", "fan": "Fans", "climate": "AC / climate",
           "cover": "Curtains & doors", "media_player": "TVs & speakers", "lock": "Locks",
           "sensor": "Sensors", "binary_sensor": "Binary sensors", "alarm_control_panel": "Alarms",
           "vacuum": "Vacuums"}

# --------------------------------------------------------------------------- HA client

_cache: dict = {"t": 0.0, "states": []}


def _configured() -> bool:
    return bool(settings.home_assistant_url and settings.home_assistant_token)


def _base() -> str:
    url = settings.home_assistant_url.rstrip("/")
    return url[:-4] if url.endswith("/api") else url


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.home_assistant_token}",
            "Content-Type": "application/json"}


class HAError(Exception):
    pass


def _request(method: str, path: str, payload: dict | None = None):
    try:
        r = requests.request(method, f"{_base()}{path}", headers=_headers(), json=payload,
                             timeout=TIMEOUT)
    except requests.Timeout:
        raise HAError("Home Assistant didn't answer in time. Is it running?") from None
    except requests.ConnectionError:
        raise HAError(f"I can't reach Home Assistant at {_base()}. Is it switched on "
                      "and on the same network?") from None
    if r.status_code == 401:
        raise HAError("Home Assistant rejected the token. Please create a new long-lived "
                      "token and update HOME_ASSISTANT_TOKEN.")
    if r.status_code == 404:
        raise HAError("Home Assistant doesn't know that device or service.")
    if r.status_code >= 400:
        raise HAError(f"Home Assistant returned an error ({r.status_code}): {r.text[:150]}")
    try:
        return r.json()
    except ValueError:
        return None


def _states(fresh: bool = False) -> list[dict]:
    if fresh or time.time() - _cache["t"] > 5:
        _cache["states"] = _request("GET", "/api/states") or []
        _cache["t"] = time.time()
    return _cache["states"]


def _call(domain: str, service: str, data: dict) -> None:
    _request("POST", f"/api/services/{domain}/{service}", data)
    _cache["t"] = 0.0  # states changed


def _name(s: dict) -> str:
    return s.get("attributes", {}).get("friendly_name") or s["entity_id"].split(".", 1)[1].replace("_", " ")


def _norm(text: str) -> str:
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower().replace("_", " "))
    text = re.sub(r"\b(the|my|please|room)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_secure(s: dict) -> bool:
    """Locks, alarm panels and garage doors/gates/doors need the user's confirmation."""
    domain = s["entity_id"].split(".")[0]
    if domain in ("lock", "alarm_control_panel"):
        return True
    if domain == "cover":
        dc = (s.get("attributes", {}).get("device_class") or "").lower()
        return dc in ("garage", "gate", "door") or bool(
            re.search(r"garage|gate|door|shutter", (_name(s) + " " + s["entity_id"]).lower()))
    return False


def _find(name: str, domains: tuple[str, ...] | set[str] | None = None) -> dict | None:
    """Fuzzy-match a spoken name to one entity's state dict."""
    states = [s for s in _states() if not domains or s["entity_id"].split(".")[0] in domains]
    if not states:
        return None
    query = name.strip().lower()
    for s in states:  # exact entity_id or friendly name
        if query in (s["entity_id"].lower(), _name(s).lower()):
            return s
    q = _norm(query)
    best, best_score = None, 0.0
    for s in states:
        cands = {_norm(_name(s)), _norm(s["entity_id"].split(".", 1)[1])}
        for c in cands:
            score = difflib.SequenceMatcher(None, q, c).ratio()
            q_words, c_words = set(q.split()), set(c.split())
            if q_words and q_words <= c_words:
                score = max(score, 0.85 + 0.1 * len(q_words) / max(len(c_words), 1))
            elif q and (q in c or c in q):
                score = max(score, 0.8)
            if score > best_score:
                best, best_score = s, score
    return best if best_score >= 0.6 else None


def _describe_state(s: dict) -> str:
    domain = s["entity_id"].split(".")[0]
    st, a = s.get("state", "unknown"), s.get("attributes", {})
    if domain == "light" and st == "on" and a.get("brightness") is not None:
        return f"on at {round(a['brightness'] / 255 * 100)}%"
    if domain == "climate":
        bits = [st]
        if a.get("temperature") is not None:
            bits.append(f"set to {a['temperature']}°")
        if a.get("current_temperature") is not None:
            bits.append(f"room {a['current_temperature']}°")
        return ", ".join(bits)
    if domain == "sensor" and a.get("unit_of_measurement"):
        return f"{st} {a['unit_of_measurement']}"
    if domain == "media_player" and a.get("media_title"):
        return f"{st} ({a['media_title']})"
    return st


# --------------------------------------------------------------------------- tools

@tool("list_devices", "List smart home devices and their states (lights, switches, fans, AC, "
      "covers, TVs, sensors, locks). Optionally filter by type.",
      {"domain": {"type": "string", "description": "Optional type: lights, switches, fans, "
                  "climate, covers, media_players, sensors, locks."}})
def list_devices(domain: str = "") -> str:
    if not _configured():
        return NOT_CONNECTED
    want = _DOMAIN_WORDS.get((domain or "").strip().lower().replace(" ", "_"))
    if domain and not want:
        want = domain.strip().lower()
    try:
        states = _states(fresh=True)
    except HAError as e:
        return f"Error: {e}"
    groups: dict[str, list[str]] = {}
    for s in states:
        d = s["entity_id"].split(".")[0]
        if (want and d != want) or (not want and d not in LIST_DOMAINS):
            continue
        if s.get("state") in ("unavailable",) and d in ("sensor", "binary_sensor"):
            continue
        groups.setdefault(d, []).append(f"{_name(s)}: {_describe_state(s)}")
    if not groups:
        return f"I found no {domain or 'smart'} devices in Home Assistant."
    lines = []
    for d, items in groups.items():
        more = f" (+{len(items) - 25} more)" if len(items) > 25 else ""
        lines.append(f"{_LABELS.get(d, d.replace('_', ' ').title())}: " + "; ".join(sorted(items)[:25]) + more)
    return "\n".join(lines)


def _plan(entity: str, action: str, value) -> tuple[str, str, dict] | str:
    """Map (entity, action, value) to (domain, service, data) or an error string."""
    domain = entity.split(".")[0]
    data: dict = {"entity_id": entity}
    a = action.strip().lower().replace(" ", "_")
    a = {"turn_on": "on", "switch_on": "on", "start": "on", "turn_off": "off", "switch_off": "off",
         "stop": "off", "dim": "brightness", "set_brightness": "brightness", "colour": "color",
         "set_color": "color", "set_temperature": "temperature", "temp": "temperature",
         "raise": "open", "lower": "close", "arm": "arm_away", "disarm": "disarm",
         "set_speed": "speed", "mute": "mute", "unmute": "unmute",
         "volume_up": "volume_up", "volume_down": "volume_down"}.get(a, a)

    if a in ("on", "off", "toggle"):
        if domain == "lock":
            return "That's a lock — use lock or unlock."
        if domain == "cover":
            return "cover", {"on": "open_cover", "off": "close_cover", "toggle": "toggle"}[a], data
        if domain == "alarm_control_panel":
            return "That's an alarm panel — use arm or disarm."
        svc = {"on": "turn_on", "off": "turn_off", "toggle": "toggle"}[a]
        if domain in ("sensor", "binary_sensor"):
            return "That's a sensor; it can only be read, not switched."
        return domain, svc, data
    if a == "brightness":
        if domain != "light":
            return "Only lights have brightness."
        try:
            pct = max(0, min(100, int(float(str(value).rstrip("%")))))
        except (TypeError, ValueError):
            return "Tell me a brightness between 0 and 100."
        if pct == 0:
            return "light", "turn_off", data
        return "light", "turn_on", {**data, "brightness_pct": pct}
    if a == "color":
        if domain != "light":
            return "Only lights can change colour."
        c = str(value or "").strip().lower()
        if not c:
            return "Which colour?"
        if c in ("warm", "warm white", "yellow white"):
            return "light", "turn_on", {**data, "color_temp_kelvin": 2700}
        if c in ("cool", "cool white", "daylight", "white"):
            return "light", "turn_on", {**data, "color_temp_kelvin": 5500 if c != "white" else 4000}
        return "light", "turn_on", {**data, "color_name": c.replace(" ", "")}
    if a == "temperature":
        try:
            t = float(value)
        except (TypeError, ValueError):
            return "Tell me the temperature as a number."
        if domain == "climate":
            return "climate", "set_temperature", {**data, "temperature": t}
        if domain == "water_heater":
            return "water_heater", "set_temperature", {**data, "temperature": t}
        return "Only an AC, thermostat or water heater has a temperature setting."
    if a == "mode" and domain == "climate":
        return "climate", "set_hvac_mode", {**data, "hvac_mode": str(value).lower()}
    if a == "speed" and domain == "fan":
        try:
            return "fan", "set_percentage", {**data, "percentage": max(0, min(100, int(float(value))))}
        except (TypeError, ValueError):
            return "Tell me the fan speed as a percentage."
    if a == "volume" and domain == "media_player":
        try:
            return "media_player", "volume_set", {**data, "volume_level": max(0, min(100, float(value))) / 100}
        except (TypeError, ValueError):
            return "Tell me the volume from 0 to 100."
    if a in ("volume_up", "volume_down") and domain == "media_player":
        return "media_player", a, data
    if a in ("mute", "unmute") and domain == "media_player":
        return "media_player", "volume_mute", {**data, "is_volume_muted": a == "mute"}
    if a in ("play", "pause") and domain == "media_player":
        return "media_player", f"media_{a}", data
    if a in ("open", "close"):
        if domain == "cover":
            return "cover", f"{a}_cover", data
        if domain == "lock":
            return "lock", "unlock" if a == "open" else "lock", data
        if domain == "valve":
            return "valve", f"{a}_valve", data
        return f"{a.title()} only works for curtains, blinds, garage doors or locks."
    if a in ("lock", "unlock"):
        if domain != "lock":
            return "That device isn't a lock."
        return "lock", a, data
    if a in ("arm_away", "arm_home", "arm_night", "disarm"):
        if domain != "alarm_control_panel":
            return "That device isn't an alarm panel."
        if value:
            data["code"] = str(value)
        return "alarm_control_panel", f"alarm_{a}", data
    return f"I don't know how to '{action}' a {domain.replace('_', ' ')}."


def _act(name: str, action: str, value, domains) -> str:
    if not _configured():
        return NOT_CONNECTED
    try:
        s = _find(name, domains)
    except HAError as e:
        return f"Error: {e}"
    if s is None:
        return f"I couldn't find a device called '{name}'. Ask me to list devices to see the names."
    plan = _plan(s["entity_id"], action, value)
    if isinstance(plan, str):
        return plan
    domain, service, data = plan
    if domains is None and is_secure(s):
        # Locks, garage doors and alarms only change through the confirmed secure_device tool.
        return (f"{_name(s)} is a security device. Use secure_device so I can confirm "
                "with you before I do that.")
    try:
        _call(domain, service, data)
    except HAError as e:
        return f"Error: {e}"
    friendly = _name(s)
    pretty = {"turn_on": "on", "turn_off": "off", "toggle": "toggled", "open_cover": "opening",
              "close_cover": "closing", "lock": "locked", "unlock": "unlocked",
              "set_temperature": f"set to {data.get('temperature', 0):g}°",
              "set_hvac_mode": f"in {data.get('hvac_mode')} mode",
              "set_percentage": f"at {data.get('percentage')}% speed",
              "volume_set": f"at volume {round(data.get('volume_level', 0) * 100)}",
              "media_play": "playing", "media_pause": "paused",
              "alarm_disarm": "disarmed"}.get(service, service.replace("_", " "))
    if "brightness_pct" in data:
        pretty = f"at {data['brightness_pct']}%"
    elif "color_name" in data:
        pretty = f"set to {data['color_name']}"
    elif "color_temp_kelvin" in data:
        pretty = "set to " + ("warm white" if data["color_temp_kelvin"] < 3500 else "cool white")
    if service.startswith("alarm_arm"):
        pretty = "armed"
    return f"Done — {friendly} is {pretty}."


@tool("control_device", "Control an everyday smart home device by name: lights, fans, "
      "switches/plugs, AC/thermostat, TV, curtains. Actions: on, off, toggle, brightness "
      "(value 0-100), color (value e.g. 'red', 'warm white'), temperature (value °C), "
      "mode (AC: cool/heat/auto/off), speed (fan %), volume (0-100), play, pause, mute, "
      "open/close (curtains, blinds). For locks, garage doors and alarms use secure_device.",
      {"name": {"type": "string", "description": "Device name as the user says it, e.g. 'bedroom light'."},
       "action": {"type": "string", "description": "on, off, toggle, brightness, color, temperature, "
                  "mode, speed, volume, play, pause, mute, open, close."},
       "value": {"type": "string", "description": "Value for brightness/color/temperature/etc."}},
      ["name", "action"])
def control_device(name: str, action: str, value=None) -> str:
    return _act(name, action, value, None)


def _describe_secure(args: dict) -> str:
    return f"{args.get('action', 'change')} the {args.get('name', 'device')}"


@tool("secure_device", "Lock, unlock, open or close a SECURITY device: door locks, garage "
      "doors / gates (covers) and alarm panels (arm_away, arm_home, disarm).",
      {"name": {"type": "string", "description": "Device name, e.g. 'front door' or 'garage'."},
       "action": {"type": "string", "description": "lock, unlock, open, close, arm_away, arm_home, disarm."},
       "code": {"type": "string", "description": "Alarm code if the panel needs one."}},
      ["name", "action"], confirm=True, describe=_describe_secure)
def secure_device(name: str, action: str, code: str = "") -> str:
    return _act(name, action, code or None, SECURE_DOMAINS)


@tool("device_state", "Check one smart home device or sensor: is it on, its brightness, "
      "temperature, humidity, battery, etc.",
      {"name": {"type": "string", "description": "Device or sensor name, e.g. 'living room AC'."}},
      ["name"])
def device_state(name: str) -> str:
    if not _configured():
        return NOT_CONNECTED
    try:
        s = _find(name)
    except HAError as e:
        return f"Error: {e}"
    if s is None:
        return f"I couldn't find a device called '{name}'."
    a = s.get("attributes", {})
    bits = [f"{_name(s)} is {_describe_state(s)}"]
    for key, label, unit in (("current_temperature", "room temperature", "°"),
                             ("temperature", "temperature", "°"),
                             ("current_humidity", "humidity", "%"), ("humidity", "humidity", "%"),
                             ("battery_level", "battery", "%"), ("percentage", "speed", "%"),
                             ("current_position", "position", "%"), ("hvac_action", "currently", ""),
                             ("volume_level", "volume", "")):
        if a.get(key) is not None and label not in " ".join(bits):
            v = a[key]
            if key == "volume_level":
                v, unit = round(v * 100), "%"
            if s["entity_id"].startswith("climate.") and key in ("temperature", "current_temperature"):
                continue  # already in the state description
            bits.append(f"{label} {v}{unit}")
    return ", ".join(bits) + "."


def _run(kind: str, name: str) -> str:
    if not _configured():
        return NOT_CONNECTED
    try:
        s = _find(name, (kind,))
        if s is None:
            return f"I couldn't find a {kind} called '{name}'."
        _call(kind, "turn_on", {"entity_id": s["entity_id"]})
    except HAError as e:
        return f"Error: {e}"
    return f"Done — {'activated' if kind == 'scene' else 'started'} {_name(s)}."


@tool("run_scene", "Activate a Home Assistant scene, e.g. 'movie time' or 'good night'.",
      {"name": {"type": "string", "description": "Scene name."}}, ["name"])
def run_scene(name: str) -> str:
    return _run("scene", name)


@tool("run_script", "Run a Home Assistant script (an automation routine), e.g. 'morning routine'.",
      {"name": {"type": "string", "description": "Script name."}}, ["name"])
def run_script(name: str) -> str:
    return _run("script", name)
