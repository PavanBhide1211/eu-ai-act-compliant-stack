"""i18n routes: list supported locales, fetch a locale, hot-reload after patch."""

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException


def _ensure_i18n_importable() -> None:
    """Add whichever ancestor contains an `i18n/` package to sys.path.

    Works for both Docker (i18n at /app/i18n) and local (i18n at the repo root)
    layouts.
    """
    here = Path(__file__).resolve()
    for cand in [here.parents[2], here.parents[3]]:  # /app/app -> /app  AND repo-root
        if (cand / "i18n" / "loader.py").exists():
            if str(cand) not in sys.path:
                sys.path.insert(0, str(cand))
            return


_ensure_i18n_importable()
from i18n import loader as i18n_loader  # noqa: E402


router = APIRouter(prefix="/i18n", tags=["i18n"])


@router.get("/locales")
def list_locales() -> dict:
    return {
        "supported": i18n_loader.supported_locales(),
        "default": "en",
    }


@router.get("/locales/{locale}")
def get_locale(locale: str) -> dict:
    sup = i18n_loader.supported_locales()
    if locale not in sup:
        raise HTTPException(
            status_code=404,
            detail=f"locale '{locale}' not supported. Available: {sup}",
        )
    return i18n_loader.dump(locale)


@router.post("/reload")
def reload_locales() -> dict:
    """Hot-reload locales after a `patch_locale.py` run."""
    return {"ok": True, "counts": i18n_loader.reload()}
