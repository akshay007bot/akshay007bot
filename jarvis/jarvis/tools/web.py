"""Knowledge tools: web search, reading pages, news, weather, Wikipedia,
currency conversion and a safe calculator. All free, no API keys.

Only ``requests`` is required. ``ddgs`` (or the older ``duckduckgo_search``),
``trafilatura``, ``beautifulsoup4`` and ``feedparser`` are optional and used
when installed (see requirements-web.txt).
"""

from __future__ import annotations

import ast
import html
import math
import operator
import re
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

import requests

from ..config import settings
from . import tool

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
TIMEOUT = 15

# Endpoints (module constants so they can be pointed elsewhere in tests).
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WIKI_URL = "https://{lang}.wikipedia.org"
FX_URL = "https://open.er-api.com/v6/latest/{base}"
GNEWS_RSS = "https://news.google.com/rss"

_session = requests.Session()
_session.headers.update({"User-Agent": UA, "Accept-Language": "en-IN,en;q=0.9"})


def _get(url: str, **kw) -> requests.Response:
    r = _session.get(url, timeout=kw.pop("timeout", TIMEOUT), **kw)
    r.raise_for_status()
    return r


def _net_error(what: str, e: Exception) -> str:
    if isinstance(e, requests.Timeout):
        return f"Error: {what} timed out. The internet may be slow right now."
    if isinstance(e, requests.ConnectionError):
        return f"Error: couldn't reach {what}. Please check the internet connection."
    if isinstance(e, requests.HTTPError) and e.response is not None:
        return f"Error: {what} answered with HTTP {e.response.status_code}."
    return f"Error: {what} failed ({e.__class__.__name__}: {e})."


def _domain(url: str) -> str:
    d = urlparse(url or "").netloc.lower()
    return d[4:] if d.startswith("www.") else d


def _clip(text: str, n: int) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"


def _ddgs():
    """Return a DDGS instance from whichever package is installed, or None."""
    try:
        from ddgs import DDGS  # type: ignore
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # type: ignore
        except ImportError:
            return None
    return DDGS()


def _age(when) -> str:
    """'3 hours ago' from an ISO string, a datetime or a time.struct_time."""
    try:
        if isinstance(when, str):
            dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
        elif isinstance(when, datetime):
            dt = when
        else:  # struct_time from feedparser
            dt = datetime(*when[:6], tzinfo=timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        secs = (datetime.now(timezone.utc) - dt).total_seconds()
    except Exception:  # noqa: BLE001
        return ""
    if secs < 0:
        return "just now"
    for unit, size in (("day", 86400), ("hour", 3600), ("minute", 60)):
        if secs >= size:
            n = int(secs // size)
            return f"{n} {unit}{'s' if n != 1 else ''} ago"
    return "just now"


# --------------------------------------------------------------------------- search

@tool("web_search", "Search the web (DuckDuckGo) for current information, facts, prices, "
      "how-tos or anything you don't know. Returns titles, snippets and sources to summarise.",
      {"query": {"type": "string", "description": "What to search for."},
       "max_results": {"type": "integer", "description": "How many results (1-10, default 5)."}},
      ["query"])
def web_search(query: str, max_results: int = 5) -> str:
    max_results = max(1, min(int(max_results or 5), 10))
    d = _ddgs()
    if d is None:
        return "Error: web search needs the 'ddgs' package (pip install ddgs)."
    try:
        results = list(d.text(query, region="in-en", max_results=max_results) or [])
    except Exception as e:  # noqa: BLE001 - ddgs raises its own exception types
        return f"Error: the web search failed ({e.__class__.__name__}). Try again in a moment."
    if not results:
        return f"No web results for '{query}'."
    lines = [f"Web results for '{query}':"]
    for i, r in enumerate(results[:max_results], 1):
        url = r.get("href") or r.get("url") or ""
        lines.append(f"{i}. {_clip(r.get('title', ''), 120)} ({_domain(url)}) — "
                     f"{_clip(r.get('body', ''), 220)} [{url}]")
    return "\n".join(lines)


# --------------------------------------------------------------------------- read page

def _extract_text(raw_html: str, url: str) -> str:
    try:
        import trafilatura  # type: ignore
        text = trafilatura.extract(raw_html, url=url, include_comments=False,
                                   include_tables=True, favor_recall=True)
        if text and len(text) > 200:
            return text
    except Exception:  # noqa: BLE001
        pass
    try:
        from bs4 import BeautifulSoup  # type: ignore
        soup = BeautifulSoup(raw_html, "html.parser")
        for t in soup(["script", "style", "noscript", "nav", "header", "footer", "aside",
                       "form", "svg", "iframe"]):
            t.decompose()
        root = soup.find("article") or soup.find("main") or soup.body or soup
        parts = [p.get_text(" ", strip=True) for p in root.find_all(["h1", "h2", "h3", "p", "li"])]
        text = "\n".join(p for p in parts if len(p) > 1)
        return text or root.get_text("\n", strip=True)
    except ImportError:
        text = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", raw_html)
        return html.unescape(re.sub(r"<[^>]+>", " ", text))


@tool("read_webpage", "Fetch a web page and return its main readable text (for summarising "
      "an article or answering from a specific link).",
      {"url": {"type": "string", "description": "The full http(s) URL."}},
      ["url"])
def read_webpage(url: str, max_chars: int = 6000) -> str:
    url = url.strip()
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    try:
        r = _get(url, headers={"Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    except requests.RequestException as e:
        return _net_error(_domain(url) or "the page", e)
    ctype = r.headers.get("Content-Type", "")
    if "html" not in ctype and "text" not in ctype and "xml" not in ctype:
        return f"That link is not a web page (it's {ctype or 'unknown content'})."
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = r.apparent_encoding
    text = re.sub(r"\n{3,}", "\n\n", _extract_text(r.text, url)).strip()
    if not text:
        return f"I couldn't find readable text on {_domain(url)}."
    title = ""
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", r.text)
    if m:
        title = _clip(html.unescape(m.group(1)), 150)
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + " … [truncated]"
    return f"{title} ({_domain(url)})\n{text}" if title else f"({_domain(url)})\n{text}"


# --------------------------------------------------------------------------- news

_REGIONS = {"india": ("in-en", "IN", "en-IN"), "us": ("us-en", "US", "en-US"),
            "usa": ("us-en", "US", "en-US"), "uk": ("uk-en", "GB", "en-GB"),
            "world": ("wt-wt", "US", "en-US"), "global": ("wt-wt", "US", "en-US")}


def _news_rss(topic: str, region: str) -> list[dict]:
    import feedparser  # type: ignore
    _, gl, hl = _REGIONS.get(region.lower(), _REGIONS["india"])
    params = f"hl={hl}&gl={gl}&ceid={gl}:{hl.split('-')[0]}"
    url = f"{GNEWS_RSS}/search?q={quote(topic)}&{params}" if topic else f"{GNEWS_RSS}?{params}"
    feed = feedparser.parse(_get(url).content)
    out = []
    for e in feed.entries[:5]:
        title = e.get("title", "")
        source = (e.get("source") or {}).get("title", "")
        if source and title.endswith(" - " + source):
            title = title[: -len(source) - 3]
        out.append({"title": title, "source": source,
                    "age": _age(e.get("published_parsed")) if e.get("published_parsed") else ""})
    return out


@tool("news", "Get the latest news headlines, optionally about a topic (e.g. 'cricket', "
      "'Bengaluru', 'stock market'). Default region is India.",
      {"topic": {"type": "string", "description": "Topic to get news about; empty for top headlines."},
       "region": {"type": "string", "description": "India (default), US, UK or World."}})
def news(topic: str = "", region: str = "India") -> str:
    topic = (topic or "").strip()
    items: list[dict] = []
    d = _ddgs()
    if d is not None:
        try:
            ddg_region = _REGIONS.get(region.lower(), _REGIONS["india"])[0]
            res = d.news(topic or f"{region} top news", region=ddg_region,
                         timelimit="d", max_results=8) or []
            items = [{"title": r.get("title", ""), "source": r.get("source", ""),
                      "age": _age(r.get("date", ""))} for r in res][:5]
        except Exception:  # noqa: BLE001 - fall back to RSS
            items = []
    if not items:
        try:
            items = _news_rss(topic, region)
        except ImportError:
            if d is None:
                return "Error: news needs the 'ddgs' or 'feedparser' package."
        except requests.RequestException as e:
            return _net_error("the news service", e)
        except Exception as e:  # noqa: BLE001
            return f"Error: couldn't read the news feed ({e.__class__.__name__})."
    if not items:
        return f"I couldn't find any recent news{' about ' + topic if topic else ''}."
    head = f"Latest news about {topic}:" if topic else f"Top headlines ({region}):"
    lines = [head]
    for i, it in enumerate(items, 1):
        meta = ", ".join(x for x in (it["source"], it["age"]) if x)
        lines.append(f"{i}. {_clip(it['title'], 160)}" + (f" ({meta})" if meta else ""))
    return "\n".join(lines)


# --------------------------------------------------------------------------- weather

WMO = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "freezing fog", 51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    56: "light freezing drizzle", 57: "freezing drizzle", 61: "light rain", 63: "rain",
    65: "heavy rain", 66: "light freezing rain", 67: "freezing rain", 71: "light snow",
    73: "snow", 75: "heavy snow", 77: "snow grains", 80: "light showers", 81: "showers",
    82: "violent showers", 85: "light snow showers", 86: "snow showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "severe thunderstorm with hail",
}


def _geocode(place: str) -> dict | None:
    name = place.split(",")[0].strip()
    r = _get(GEOCODE_URL, params={"name": name, "count": 5, "language": "en", "format": "json"})
    res = r.json().get("results") or []
    if not res:
        return None
    hint = place.split(",", 1)[1].strip().lower() if "," in place else ""
    if hint:
        for g in res:
            if hint in (g.get("country", "") + " " + g.get("admin1", "")).lower():
                return g
    return res[0]


@tool("weather", "Current weather and forecast for a place (default: the user's city). "
      "Use days>1 for a multi-day forecast.",
      {"place": {"type": "string", "description": "City or town, e.g. 'Mysuru' or 'Pune, India'."},
       "days": {"type": "integer", "description": "Forecast days, 1-7 (default 1)."}})
def weather(place: str = "", days: int = 1) -> str:
    place = (place or settings.city or "Bengaluru").strip()
    days = max(1, min(int(days or 1), 7))
    try:
        g = _geocode(place)
        if g is None:
            return f"I couldn't find a place called {place}."
        params = {
            "latitude": g["latitude"], "longitude": g["longitude"],
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                       "weather_code,wind_speed_10m,precipitation",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                     "precipitation_probability_max",
            "hourly": "precipitation_probability",
            "timezone": settings.timezone or "auto", "forecast_days": days,
        }
        data = _get(FORECAST_URL, params=params).json()
    except requests.RequestException as e:
        return _net_error("the weather service", e)
    except (ValueError, KeyError) as e:
        return f"Error: the weather service sent an unexpected reply ({e})."

    cur, daily = data.get("current", {}), data.get("daily", {})
    where = g.get("name", place) + (f", {g['admin1']}" if g.get("admin1") and g.get("admin1") != g.get("name") else "")

    def d(key, i):
        try:
            return daily[key][i]
        except (KeyError, IndexError, TypeError):
            return None

    # Chance of rain for the rest of today from hourly data, fall back to daily max.
    rain = d("precipitation_probability_max", 0)
    try:
        now_h = cur.get("time", "")[:13]
        hours = data["hourly"]["time"]
        probs = data["hourly"]["precipitation_probability"]
        today = now_h[:10]
        rest = [p for t, p in zip(hours, probs) if t[:10] == today and t[:13] >= now_h and p is not None]
        if rest:
            rain = max(rest)
    except (KeyError, TypeError):
        pass

    parts = [f"In {where} it's {round(cur.get('temperature_2m', 0))}°C and "
             f"{WMO.get(cur.get('weather_code'), 'unknown conditions')}"]
    if cur.get("apparent_temperature") is not None:
        parts[0] += f", feels like {round(cur['apparent_temperature'])}°C"
    parts[0] += "."
    hi, lo = d("temperature_2m_max", 0), d("temperature_2m_min", 0)
    if hi is not None and lo is not None:
        parts.append(f"Today's high is {round(hi)}°C and the low {round(lo)}°C.")
    if rain is not None:
        parts.append(f"Chance of rain: {rain}%." + (" Carry an umbrella." if rain >= 50 else ""))
    if cur.get("relative_humidity_2m") is not None:
        parts.append(f"Humidity {cur['relative_humidity_2m']}%, wind {round(cur.get('wind_speed_10m', 0))} km/h.")
    out = " ".join(parts)

    if days > 1:
        lines = []
        for i, day in enumerate((daily.get("time") or [])[1:days], 1):
            try:
                name = datetime.fromisoformat(day).strftime("%A")
            except ValueError:
                name = day
            lines.append(f"{name}: {WMO.get(d('weather_code', i), 'mixed')}, "
                         f"{round(d('temperature_2m_max', i) or 0)}/{round(d('temperature_2m_min', i) or 0)}°C"
                         + (f", {d('precipitation_probability_max', i)}% rain" if d('precipitation_probability_max', i) is not None else ""))
        if lines:
            out += "\nForecast:\n" + "\n".join(lines)
    return out


# --------------------------------------------------------------------------- wikipedia

@tool("wikipedia_summary", "Short encyclopedia summary of a person, place, thing or concept "
      "from Wikipedia. Use lang='kn' for Kannada.",
      {"topic": {"type": "string", "description": "What to look up."},
       "lang": {"type": "string", "description": "Wikipedia language code: 'en' (default) or 'kn'."}},
      ["topic"])
def wikipedia_summary(topic: str, lang: str = "en") -> str:
    lang = (lang or "en").strip().lower()
    if not re.fullmatch(r"[a-z]{2,3}", lang):
        lang = "en"
    base = WIKI_URL.format(lang=lang)

    def summary(title: str) -> dict | None:
        try:
            r = _session.get(f"{base}/api/rest_v1/page/summary/{quote(title.replace(' ', '_'), safe='')}",
                             timeout=TIMEOUT, params={"redirect": "true"})
        except requests.RequestException:
            raise
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    try:
        data = summary(topic.strip())
        if data is None or data.get("type") == "disambiguation":
            s = _get(f"{base}/w/api.php", params={
                "action": "query", "list": "search", "srsearch": topic, "srlimit": 1,
                "format": "json"}).json()
            hits = s.get("query", {}).get("search", [])
            if not hits:
                return f"Wikipedia has no article about {topic}."
            data = summary(hits[0]["title"])
            if data is None:
                return f"Wikipedia has no article about {topic}."
    except requests.RequestException as e:
        return _net_error("Wikipedia", e)
    except ValueError:
        return "Error: Wikipedia sent an unexpected reply."
    extract = data.get("extract") or data.get("description") or ""
    if not extract:
        return f"Wikipedia's article on {data.get('title', topic)} has no summary."
    return f"{data.get('title', topic)}: {_clip(extract, 1200)}"


# --------------------------------------------------------------------------- currency

_CURRENCY_WORDS = {
    "rupee": "INR", "rupees": "INR", "rs": "INR", "₹": "INR", "dollar": "USD", "dollars": "USD",
    "$": "USD", "euro": "EUR", "euros": "EUR", "€": "EUR", "pound": "GBP", "pounds": "GBP",
    "£": "GBP", "yen": "JPY", "dirham": "AED", "dirhams": "AED", "riyal": "SAR",
    "singapore dollar": "SGD", "australian dollar": "AUD", "canadian dollar": "CAD", "yuan": "CNY",
}


def _code(c: str) -> str:
    c = (c or "").strip()
    return _CURRENCY_WORDS.get(c.lower(), c.upper())


@tool("convert_currency", "Convert money between currencies using today's exchange rates "
      "(e.g. 100 USD to INR).",
      {"amount": {"type": "number", "description": "How much money."},
       "from_currency": {"type": "string", "description": "Currency code or name, e.g. USD, INR, euro."},
       "to_currency": {"type": "string", "description": "Target currency code or name."}},
      ["amount", "from_currency", "to_currency"])
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    src, dst = _code(from_currency), _code(to_currency)
    if not (re.fullmatch(r"[A-Z]{3}", src) and re.fullmatch(r"[A-Z]{3}", dst)):
        return "Error: please give three-letter currency codes like INR, USD or EUR."
    try:
        amount = float(amount)
        data = _get(FX_URL.format(base=src)).json()
    except (TypeError, ValueError):
        return "Error: the amount must be a number."
    except requests.RequestException as e:
        return _net_error("the exchange-rate service", e)
    if data.get("result") != "success":
        return f"Error: I don't know the currency {src}."
    rate = (data.get("rates") or {}).get(dst)
    if rate is None:
        return f"Error: I don't know the currency {dst}."
    value = amount * rate
    fmt = (lambda x: f"{x:,.2f}") if abs(value) >= 0.01 else (lambda x: f"{x:.6g}")
    when = (data.get("time_last_update_utc") or "")[:16]
    return (f"{amount:,.2f} {src} is about {fmt(value)} {dst} "
            f"(1 {src} = {rate:.6g} {dst}{', rates from ' + when if when else ''}).")


# --------------------------------------------------------------------------- calculator

_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
        ast.Pow: operator.pow}
_UN = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {name: getattr(math, name) for name in (
    "sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "exp",
    "log10", "log2", "floor", "ceil", "factorial", "degrees", "radians", "hypot", "gcd")}
_FUNCS.update({"abs": abs, "round": round, "min": min, "max": max, "log": math.log,
               "ln": math.log, "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x)})
_CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
        a, b = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and (abs(b) > 1000 or abs(a) > 1e100):
            raise ValueError("that power is too large")
        return _BIN[type(node.op)](a, b)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UN:
        return _UN[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS \
            and not node.keywords:
        args = [_eval(a) for a in node.args]
        if node.func.id == "factorial" and args and args[0] > 1000:
            raise ValueError("that factorial is too large")
        return _FUNCS[node.func.id](*args)
    raise ValueError("unsupported expression")


def _prep(expr: str) -> str:
    e = expr.strip().lower().rstrip("=?").strip()
    e = re.sub(r"^(what is|what's|calculate|compute)\s+", "", e)
    for a, b in (("×", "*"), ("÷", "/"), ("^", "**"), ("√", "sqrt"), ("plus", "+"),
                 ("minus", "-"), ("multiplied by", "*"), ("times", "*"), ("divided by", "/"),
                 ("into", "*"), ("to the power of", "**")):
        e = e.replace(a, b)
    e = re.sub(r"(?<=\d)\s*x\s*(?=\d)", "*", e)          # 12 x 4
    if "(" not in e:
        e = re.sub(r"(?<=\d),(?=\d)", "", e)              # 1,00,000 / 12,500
    # "15% of 200" -> (15/100)*200 ; bare "18%" -> (18/100)
    e = re.sub(r"(\d+(?:\.\d+)?)\s*%\s*of", r"(\1/100)*", e)
    e = re.sub(r"(\d+(?:\.\d+)?)\s*%(?!\s*[\d(])", r"(\1/100)", e)
    e = re.sub(r"sqrt\s*(\d+(?:\.\d+)?)", r"sqrt(\1)", e)
    return e


@tool("calculate", "Do maths exactly: arithmetic, percentages, powers, square roots, trig, "
      "logs. Example: '15% of 2400', 'sqrt(144) + 2^10', '(3.5*4)/7'.",
      {"expression": {"type": "string", "description": "The maths expression."}},
      ["expression"])
def calculate(expression: str) -> str:
    expr = _prep(expression)
    if len(expr) > 300:
        return "Error: that expression is too long."
    try:
        value = _eval(ast.parse(expr, mode="eval"))
    except ZeroDivisionError:
        return "Error: you can't divide by zero."
    except (SyntaxError, ValueError, TypeError, OverflowError) as e:
        return f"Error: I couldn't calculate '{expression}' ({e})."
    if isinstance(value, float):
        if value.is_integer() and abs(value) < 1e15:
            value = int(value)
        else:
            value = float(f"{value:.10g}")
    return f"{expression.strip()} = {value:,}" if isinstance(value, int) and abs(value) >= 10000 \
        else f"{expression.strip()} = {value}"
