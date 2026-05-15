"""Backend locale loader.

Reads JSON locale files from i18n/locales/ at runtime, caches them in-process,
and exposes a small lookup API. The backend uses this to render the Article 50
candidate-facing disclosure in the requested locale. Hot-reloadable via the
`reload()` function — no process restart needed when a locale file is patched.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from threading import RLock
from typing import Any


# Resolve relative to the repo root, not the cwd, so it works whether the
# backend is run from ./backend or from the repo root.
_HERE = Path(__file__).resolve().parent
_LOCALES_DIR = _HERE / "locales"

_DEFAULT_LOCALE = "en"

_lock = RLock()
_cache: dict[str, dict[str, Any]] = {}


def supported_locales() -> list[str]:
    if not _LOCALES_DIR.exists():
        return [_DEFAULT_LOCALE]
    return sorted(p.stem for p in _LOCALES_DIR.glob("*.json"))


def _load(locale: str) -> dict[str, Any]:
    path = _LOCALES_DIR / f"{locale}.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _ensure_loaded(locale: str) -> dict[str, Any]:
    with _lock:
        if locale not in _cache:
            _cache[locale] = _load(locale)
        return _cache[locale]


def reload() -> dict[str, int]:
    """Drop the in-process cache. Returns the new locale -> key-count map.

    The /i18n/reload endpoint (added in compliance_routes) calls this so a
    deployer can roll out a patched locale without bouncing the service.
    """
    with _lock:
        _cache.clear()
    return {loc: len(_ensure_loaded(loc)) for loc in supported_locales()}


def t(key: str, *, locale: str | None = None, default: str | None = None) -> str:
    """Translate a dot-path key. Falls back to English, then to the default
    argument, then to the key itself. Never raises."""
    locale = locale or _DEFAULT_LOCALE
    for candidate in (locale, _DEFAULT_LOCALE):
        d = _ensure_loaded(candidate)
        v = _walk(d, key)
        if isinstance(v, str) and v.strip():
            return v
    return default if default is not None else key


def _walk(d: dict[str, Any], dotted_key: str) -> Any:
    cur: Any = d
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def parse_accept_language(header: str | None) -> str:
    """Best-effort Accept-Language parser. Returns the most-preferred supported
    locale, defaulting to English."""
    if not header:
        return _DEFAULT_LOCALE
    sup = set(supported_locales())
    # "de-DE,de;q=0.9,en;q=0.8" -> ["de-DE","de","en"]
    candidates = []
    for chunk in header.split(","):
        tag = chunk.split(";")[0].strip().lower()
        if not tag:
            continue
        candidates.append(tag)
        primary = tag.split("-")[0]
        if primary != tag:
            candidates.append(primary)
    for c in candidates:
        if c in sup:
            return c
    return _DEFAULT_LOCALE


def dump(locale: str) -> dict[str, Any]:
    """Return the full locale dictionary. Used by the /i18n/locales/{locale}
    endpoint so the frontend can hydrate from the backend."""
    return _ensure_loaded(locale)
