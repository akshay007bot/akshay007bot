"""Settings, loaded from the .env file next to the project (see .env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# Everything Jarvis remembers (memory, reminders, Google tokens) lives here.
DATA_DIR = Path(os.getenv("JARVIS_DATA_DIR", Path.home() / ".jarvis"))
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _flag(name: str, default: bool) -> bool:
    return _env(name, "1" if default else "0").lower() in ("1", "true", "yes", "on")


@dataclass
class Provider:
    """One OpenAI-compatible chat endpoint. Tried in order until one answers."""

    name: str
    base_url: str
    api_key: str
    model: str


def providers() -> list[Provider]:
    out: list[Provider] = []
    if _env("GEMINI_API_KEY"):
        out.append(Provider(
            "gemini",
            _env("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
            _env("GEMINI_API_KEY"),
            _env("GEMINI_MODEL", "gemini-3-flash-preview"),
        ))
    if _env("GROQ_API_KEY"):
        out.append(Provider(
            "groq",
            _env("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            _env("GROQ_API_KEY"),
            _env("GROQ_MODEL", "llama-3.3-70b-versatile"),
        ))
    if _flag("OLLAMA_ENABLED", True):
        out.append(Provider(
            "ollama",
            _env("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            "ollama",
            _env("OLLAMA_MODEL", "qwen3:8b"),
        ))
    return out


@dataclass
class Settings:
    user_name: str = field(default_factory=lambda: _env("JARVIS_USER_NAME", "sir"))
    city: str = field(default_factory=lambda: _env("JARVIS_CITY", "Bengaluru"))
    timezone: str = field(default_factory=lambda: _env("JARVIS_TIMEZONE", "Asia/Kolkata"))
    wake_word: str = field(default_factory=lambda: _env("JARVIS_WAKE_MODEL", "hey_jarvis"))
    wake_threshold: float = field(default_factory=lambda: float(_env("JARVIS_WAKE_THRESHOLD", "0.5")))
    whisper_model: str = field(default_factory=lambda: _env("WHISPER_MODEL", "large-v3-turbo"))
    whisper_device: str = field(default_factory=lambda: _env("WHISPER_DEVICE", "auto"))
    voice_en: str = field(default_factory=lambda: _env("VOICE_EN", "en-IN-PrabhatNeural"))
    voice_kn: str = field(default_factory=lambda: _env("VOICE_KN", "kn-IN-GaganNeural"))
    # Actions that change things (send email, delete files, run commands) ask first.
    confirm_actions: bool = field(default_factory=lambda: _flag("JARVIS_CONFIRM_ACTIONS", True))
    home_assistant_url: str = field(default_factory=lambda: _env("HOME_ASSISTANT_URL"))
    home_assistant_token: str = field(default_factory=lambda: _env("HOME_ASSISTANT_TOKEN"))
    google_credentials: Path = field(
        default_factory=lambda: Path(_env("GOOGLE_CREDENTIALS_FILE", str(DATA_DIR / "google_credentials.json")))
    )


settings = Settings()
