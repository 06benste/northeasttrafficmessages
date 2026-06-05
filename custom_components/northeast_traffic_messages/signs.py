"""Supported VMS sign codes shipped with the integration."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

_SIGN_LIST_PATH = Path(__file__).with_name("supported_signs.json")


class SupportedSign(TypedDict):
    friendly_id: str
    utmc_id: str
    name: str


def _normalize_lookup_key(value: str) -> str:
    return value.strip().upper()


@lru_cache(maxsize=1)
def load_supported_signs() -> tuple[SupportedSign, ...]:
    """Return supported sign metadata from the bundled JSON list."""
    with _SIGN_LIST_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("supported_signs.json must contain a JSON array")
    signs: list[SupportedSign] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        friendly_id = str(item.get("friendly_id", item.get("id", ""))).strip()
        utmc_id = str(item.get("utmc_id", item.get("id", ""))).strip()
        if not friendly_id or not utmc_id:
            continue
        signs.append(
            {
                "friendly_id": friendly_id,
                "utmc_id": utmc_id,
                "name": str(item.get("name", friendly_id)).strip(),
            }
        )
    return tuple(signs)


@lru_cache(maxsize=1)
def _friendly_index() -> dict[str, SupportedSign]:
    """Map normalized friendly IDs to sign metadata."""
    return {
        _normalize_lookup_key(sign["friendly_id"]): sign for sign in load_supported_signs()
    }


@lru_cache(maxsize=1)
def supported_friendly_ids() -> frozenset[str]:
    """Return the allowlisted friendly sign IDs (normalized uppercase)."""
    return frozenset(_friendly_index().keys())


def resolve_friendly_sign_id(friendly_id: str) -> SupportedSign | None:
    """Return sign metadata when the friendly code is on the bundled list."""
    return _friendly_index().get(_normalize_lookup_key(friendly_id))


def is_supported_friendly_sign_id(friendly_id: str) -> bool:
    """Return True when the friendly sign code is on the bundled allowlist."""
    return resolve_friendly_sign_id(friendly_id) is not None
