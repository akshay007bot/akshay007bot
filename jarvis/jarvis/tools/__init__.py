"""Tool registry.

Every ability Jarvis has is a plain Python function decorated with ``@tool``.
Modules in this package are imported automatically; a module that cannot be
imported (missing optional dependency, wrong OS) is skipped with a warning, so
one broken ability never takes Jarvis down.

Contract for tool authors:
  * The function takes keyword arguments matching ``params`` and returns a
    ``str`` (short, speakable, factual). Return errors as text starting with
    "Error:" rather than raising, when you can.
  * ``params`` is a JSON-Schema "properties" dict; ``required`` lists required keys.
  * Set ``confirm=True`` for anything that changes the world (sends, deletes,
    buys, runs commands, controls devices that matter). Jarvis then asks the
    user "shall I go ahead?" before running it. ``describe`` (optional) turns
    the arguments into the sentence used in that question.
"""

from __future__ import annotations

import importlib
import json
import logging
import pkgutil
import traceback
from dataclasses import dataclass
from typing import Any, Callable

log = logging.getLogger("jarvis.tools")


@dataclass
class Tool:
    name: str
    description: str
    params: dict[str, Any]
    required: list[str]
    fn: Callable[..., str]
    confirm: bool = False
    describe: Callable[[dict], str] | None = None

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.params,
                    "required": self.required,
                },
            },
        }


REGISTRY: dict[str, Tool] = {}


def tool(name: str, description: str, params: dict | None = None,
         required: list[str] | None = None, confirm: bool = False,
         describe: Callable[[dict], str] | None = None):
    def deco(fn):
        REGISTRY[name] = Tool(name, description, params or {}, required or [], fn, confirm, describe)
        return fn
    return deco


def load_all() -> list[str]:
    """Import every tool module. Returns the names of modules that were skipped."""
    skipped = []
    for mod in pkgutil.iter_modules(__path__):
        try:
            importlib.import_module(f"{__name__}.{mod.name}")
        except Exception as e:  # noqa: BLE001 - one bad module must not stop Jarvis
            skipped.append(f"{mod.name} ({e.__class__.__name__}: {e})")
            log.warning("Skipped tool module %s: %s", mod.name, e)
    return skipped


def schemas() -> list[dict]:
    return [t.schema() for t in REGISTRY.values()]


def run(name: str, raw_args: str | dict, confirm_fn: Callable[[str], bool] | None = None) -> str:
    t = REGISTRY.get(name)
    if t is None:
        return f"Error: no tool named {name}."
    try:
        args = json.loads(raw_args or "{}") if isinstance(raw_args, str) else dict(raw_args or {})
    except (json.JSONDecodeError, TypeError, ValueError):
        return "Error: the arguments were not valid JSON."
    if args is None:  # some models send "null" for tools without parameters
        args = {}
    if not isinstance(args, dict):
        return "Error: the arguments must be a JSON object."
    missing = [k for k in t.required if k not in args]
    if missing:
        return f"Error: missing required argument(s): {', '.join(missing)}."
    from ..config import settings  # local import: config must not depend on tools
    if t.confirm and confirm_fn is not None and settings.confirm_actions:
        try:
            what = t.describe(args) if t.describe else None
        except Exception:  # noqa: BLE001 - a bad describe() must not skip the question
            what = None
        if not confirm_fn(what or f"{name.replace('_', ' ')} with {args}"):
            return "The user declined, so nothing was done."
    try:
        result = t.fn(**args)
        return str(result) if result is not None else "Done."
    except Exception as e:  # noqa: BLE001
        log.debug(traceback.format_exc())
        return f"Error: {e.__class__.__name__}: {e}"
