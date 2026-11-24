"""The brain: a tool-using chat loop over free OpenAI-compatible LLM endpoints.

Providers are tried in order (Gemini free tier -> Groq free tier -> local
Ollama). If one fails (rate limit, outage, no internet) the same turn is
retried on the next, so Jarvis keeps working.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Callable
from zoneinfo import ZoneInfo

from openai import OpenAI

from . import tools
from .config import Provider, providers, settings
from .tools import memory

log = logging.getLogger("jarvis.brain")

MAX_TOOL_ROUNDS = 8
MAX_HISTORY_TURNS = 12  # user turns kept in short-term context
COOLDOWN_S = 60  # skip a provider this long after it fails

SYSTEM_PROMPT = """You are JARVIS, the personal assistant of {user}. You run on their Windows PC \
and can act through your tools: control the computer, read and draft email, manage the calendar \
and reminders, search the web, check weather and news, and control the smart home.

How to behave:
- You are speaking out loud. Answer in one to three short sentences unless asked for detail. \
No markdown, bullet lists, emojis or URLs in spoken replies.
- Reply in the language the user spoke: Kannada (in Kannada script) or English. If they mix, \
follow their main language. A message tagged [spoken in Kannada] was said in Kannada even \
if it is written in English letters: understand it and always reply in Kannada script.
- Be calm, precise and slightly witty, like a capable butler. Address the user as "{user}" now and then.
- Use tools whenever they give a better answer than memory: anything current (news, prices, \
weather, scores), anything on the PC, email, calendar or home. Never invent tool results.
- If a request is ambiguous and acting wrongly would matter (who to email, which file to delete), \
ask one short question first. Otherwise just do it.
- After acting, say briefly what you did. If a tool fails, say so plainly and suggest a fix.
- Save lasting personal facts with the remember tool when the user shares them.

Current time: {now} ({tz}). Home city: {city}.
What you remember about the user:
{facts}"""


class Brain:
    def __init__(self, confirm_fn: Callable[[str], bool] | None = None):
        self.confirm_fn = confirm_fn
        self.history: list[dict] = []
        self.providers: list[Provider] = providers()
        self._clients = {p.name: OpenAI(base_url=p.base_url, api_key=p.api_key, timeout=60, max_retries=1)
                         for p in self.providers}
        if not self.providers:
            raise RuntimeError("No AI provider configured. Add GEMINI_API_KEY to .env or enable Ollama.")
        self._down_until: dict[str, float] = {}

    # ------------------------------------------------------------------ prompt
    def _system(self) -> dict:
        tz = ZoneInfo(settings.timezone)
        facts = memory.all_facts()
        return {"role": "system", "content": SYSTEM_PROMPT.format(
            user=settings.user_name,
            now=datetime.now(tz).strftime("%A %d %B %Y, %I:%M %p"),
            tz=settings.timezone,
            city=settings.city,
            facts="\n".join(f"- {f}" for f in facts) if facts else "(nothing yet)",
        )}

    def _trim(self) -> None:
        """Keep the last N user turns; always cut at a user message so tool calls stay paired."""
        user_idx = [i for i, m in enumerate(self.history) if m["role"] == "user"]
        if len(user_idx) > MAX_HISTORY_TURNS:
            self.history = self.history[user_idx[-MAX_HISTORY_TURNS]:]

    def reset(self) -> None:
        self.history.clear()

    # -------------------------------------------------------------------- LLM
    def _complete(self, messages: list[dict]):
        errors = []
        now = time.monotonic()
        live = [p for p in self.providers if self._down_until.get(p.name, 0) <= now]
        for p in live or self.providers:  # if all are cooling down, try them all anyway
            try:
                resp = self._clients[p.name].chat.completions.create(
                    model=p.model, messages=messages, tools=tools.schemas() or None,
                )
                self._down_until.pop(p.name, None)
                return p, resp.choices[0].message
            except Exception as e:  # noqa: BLE001 - fall through to the next provider
                log.warning("Provider %s failed: %s", p.name, e)
                self._down_until[p.name] = time.monotonic() + COOLDOWN_S
                errors.append(f"{p.name}: {e.__class__.__name__}")
        raise RuntimeError("All AI providers failed (" + "; ".join(errors) + ")")

    def ask(self, text: str, on_tool: Callable[[str], None] | None = None) -> str:
        self.history.append({"role": "user", "content": text})
        self._trim()
        try:
            for _ in range(MAX_TOOL_ROUNDS):
                provider, msg = self._complete([self._system(), *self.history])
                calls = msg.tool_calls or []
                entry: dict = {"role": "assistant", "content": msg.content or ""}
                if calls:
                    entry["tool_calls"] = [
                        {"id": c.id, "type": "function",
                         "function": {"name": c.function.name, "arguments": c.function.arguments or "{}"}}
                        for c in calls
                    ]
                self.history.append(entry)
                if not calls:
                    return (msg.content or "").strip() or "Done."
                for c in calls:
                    if on_tool:
                        on_tool(c.function.name)
                    result = tools.run(c.function.name, c.function.arguments, self.confirm_fn)
                    log.info("[%s] %s(%s) -> %s", provider.name, c.function.name,
                             c.function.arguments, result[:200])
                    self.history.append({"role": "tool", "tool_call_id": c.id,
                                         "name": c.function.name, "content": result[:8000]})
            return "I got stuck going back and forth with my tools. Could you rephrase that?"
        except RuntimeError as e:
            # Drop the failed turn so history stays valid for the next request.
            last_user = max(i for i, m in enumerate(self.history) if m["role"] == "user")
            self.history = self.history[:last_user]
            log.error("%s", e)
            return "I can't reach my brain right now. Check the internet connection or start Ollama."
