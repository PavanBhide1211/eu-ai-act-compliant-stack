#!/usr/bin/env python3
"""patch_locale.py — runtime locale management CLI.

Subcommands:
  list                       — list supported locales
  show <locale>              — print the locale dict as JSON
  create <locale>            — bootstrap a new locale, cloned from en.json
                               with empty values
  set <locale> <key> <value> — set a single dot-path key in a locale
  unset <locale> <key>       — remove a single dot-path key
  validate <locale>          — report any keys missing relative to en.json
  reload [--api URL]         — POST /i18n/reload on a running backend
                               (default URL: http://localhost:8000)

Locale files live under i18n/locales/ and are read by the backend loader on
every request (cached). Use `reload` after a patch to refresh the cache without
bouncing the service.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib import request as urlrequest


HERE = Path(__file__).resolve().parent
LOCALES_DIR = HERE / "locales"
EN_FILE = LOCALES_DIR / "en.json"


# ---------- helpers
def _load(locale: str) -> dict:
    p = LOCALES_DIR / f"{locale}.json"
    if not p.exists():
        raise SystemExit(f"locale '{locale}' not found at {p}")
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(locale: str, data: dict) -> None:
    p = LOCALES_DIR / f"{locale}.json"
    with p.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def _walk(d: dict, parts: list[str]):
    cur = d
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    return cur, parts[-1]


def _flatten(d: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in (d or {}).items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten(v, key))
        else:
            out[key] = v
    return out


def _empty_clone(template: dict) -> dict:
    """Clone a dict, replacing every leaf string with an empty string."""
    out: dict = {}
    for k, v in template.items():
        if isinstance(v, dict):
            out[k] = _empty_clone(v)
        elif isinstance(v, str):
            out[k] = ""
        else:
            out[k] = v
    return out


# ---------- commands
def cmd_list(_args) -> None:
    if not LOCALES_DIR.exists():
        print("(no locales directory)", file=sys.stderr)
        return
    for p in sorted(LOCALES_DIR.glob("*.json")):
        print(p.stem)


def cmd_show(args) -> None:
    data = _load(args.locale)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_create(args) -> None:
    target = LOCALES_DIR / f"{args.locale}.json"
    if target.exists() and not args.force:
        raise SystemExit(
            f"locale '{args.locale}' already exists. Use --force to overwrite."
        )
    template = _load("en")
    cloned = _empty_clone(template)
    if "_meta" in cloned and isinstance(cloned["_meta"], dict):
        cloned["_meta"]["locale"] = args.locale
        cloned["_meta"]["name"] = args.name or args.locale
        cloned["_meta"]["reviewer"] = "patch_locale create"
    _save(args.locale, cloned)
    print(
        f"created {target} with empty values for {len(_flatten(cloned))} keys."
    )
    print(
        f"Next: edit {target}, run `python i18n/patch_locale.py validate "
        f"{args.locale}`, then `python i18n/patch_locale.py reload`."
    )


def cmd_set(args) -> None:
    data = _load(args.locale)
    parent, last = _walk(data, args.key.split("."))
    parent[last] = args.value
    _save(args.locale, data)
    print(f"set {args.locale}.{args.key}")


def cmd_unset(args) -> None:
    data = _load(args.locale)
    parts = args.key.split(".")
    parent, last = _walk(data, parts)
    if last in parent:
        del parent[last]
        _save(args.locale, data)
        print(f"unset {args.locale}.{args.key}")
    else:
        print(f"(no such key {args.locale}.{args.key})", file=sys.stderr)


def cmd_validate(args) -> None:
    if not EN_FILE.exists():
        raise SystemExit("en.json is missing — cannot validate")
    en_keys = set(_flatten(_load("en")))
    target_keys = set(_flatten(_load(args.locale)))
    en_keys.discard("_meta.locale")
    en_keys.discard("_meta.name")
    en_keys.discard("_meta.schema_version")
    en_keys.discard("_meta.reviewer")
    en_keys.discard("_meta.reviewed_on")
    missing = sorted(en_keys - target_keys)
    extra = sorted(target_keys - en_keys)
    ok = not missing
    print(json.dumps({"ok": ok, "missing": missing, "extra": extra}, indent=2))
    if not ok:
        sys.exit(1)


def cmd_reload(args) -> None:
    url = args.api.rstrip("/") + "/i18n/reload"
    req = urlrequest.Request(url, method="POST")
    try:
        with urlrequest.urlopen(req, timeout=5) as resp:
            print(resp.read().decode("utf-8"))
    except Exception as e:  # pragma: no cover
        raise SystemExit(f"reload failed: {e}")


# ---------- entrypoint
def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list").set_defaults(func=cmd_list)

    s = sub.add_parser("show")
    s.add_argument("locale")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("create")
    s.add_argument("locale")
    s.add_argument("--name", help="human-readable name (e.g. 'Nederlands')")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_create)

    s = sub.add_parser("set")
    s.add_argument("locale")
    s.add_argument("key")
    s.add_argument("value")
    s.set_defaults(func=cmd_set)

    s = sub.add_parser("unset")
    s.add_argument("locale")
    s.add_argument("key")
    s.set_defaults(func=cmd_unset)

    s = sub.add_parser("validate")
    s.add_argument("locale")
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("reload")
    s.add_argument("--api", default="http://localhost:8000")
    s.set_defaults(func=cmd_reload)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
