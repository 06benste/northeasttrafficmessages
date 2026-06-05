"""UTMC Open Data API client for Variable Message Signs."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_DYNAMIC_URL,
    API_RETRY_BASE_DELAY_SECONDS,
    API_RETRY_MAX_ATTEMPTS,
    API_STATIC_URL,
    DOMAIN,
    STATIC_CACHE_TTL_SECONDS,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


class UTMCError(Exception):
    """Base UTMC API error."""


class InvalidAuth(UTMCError):
    """Invalid credentials."""


class CannotConnect(UTMCError):
    """Connection or unexpected response error."""


class VmsNotFound(UTMCError):
    """VMS ID not found in feed."""


@dataclass
class VmsStatic:
    """Static VMS metadata."""

    system_code_number: str
    short_description: str | None
    long_description: str | None
    easting: float | None
    northing: float | None
    latitude: float | None
    longitude: float | None
    road_name: str | None
    creation_date: datetime | None
    data_source: str | None


@dataclass
class VmsDynamic:
    """Dynamic sign display data."""

    message_text: str | None
    message_text_split: str | None
    sign_setting_reason: str | None
    last_updated: datetime | None
    lantern_state: int | None
    category: str | None
    message_name: str | None
    pictogram_id: str | None


@dataclass
class VmsData:
    """Merged static and dynamic data for one sign."""

    static: VmsStatic
    dynamic: VmsDynamic | None


def _parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    if len(normalized) >= 5 and normalized[-5] in "+-" and normalized[-3] != ":":
        normalized = f"{normalized[:-2]}:{normalized[-2:]}"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _first(items: list[Any] | None) -> dict[str, Any] | None:
    if not items:
        return None
    item = items[0]
    return item if isinstance(item, dict) else None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_point(raw: dict[str, Any]) -> dict[str, Any]:
    """Return a point dict from flat or nested UTMC payloads."""
    point = raw.get("point")
    if isinstance(point, dict):
        return point
    definition = _first(raw.get("definitions")) or {}
    nested = definition.get("point")
    return nested if isinstance(nested, dict) else {}


def _extract_text_fields(raw: dict[str, Any], *keys: str) -> dict[str, str | None]:
    """Read description fields from root or definitions[0]."""
    definition = _first(raw.get("definitions")) or {}
    out: dict[str, str | None] = {}
    for key in keys:
        value = raw.get(key)
        if value is None and definition:
            value = definition.get(key)
        out[key] = str(value) if value is not None else None
    return out


def parse_static_item(raw: dict[str, Any]) -> VmsStatic:
    """Parse one VMS static feed item."""
    point = _extract_point(raw)
    text = _extract_text_fields(raw, "shortDescription", "longDescription")

    return VmsStatic(
        system_code_number=str(raw.get("systemCodeNumber", "")),
        short_description=text["shortDescription"],
        long_description=text["longDescription"],
        easting=_to_float(point.get("easting")),
        northing=_to_float(point.get("northing")),
        latitude=_to_float(point.get("latitude")),
        longitude=_to_float(point.get("longitude")),
        road_name=raw.get("roadName"),
        creation_date=_parse_iso8601(raw.get("creationDate")),
        data_source=raw.get("dataSource"),
    )


def parse_dynamic_item(raw: dict[str, Any]) -> VmsDynamic:
    """Parse one VMS dynamic feed item."""
    dynamics = _first(raw.get("dynamics")) or raw

    return VmsDynamic(
        message_text=dynamics.get("messageText"),
        message_text_split=dynamics.get("messageTextSplit"),
        sign_setting_reason=dynamics.get("signSettingReason"),
        last_updated=_parse_iso8601(dynamics.get("lastUpdated")),
        lantern_state=_to_int(dynamics.get("lanternState")),
        category=dynamics.get("category"),
        message_name=dynamics.get("messageName"),
        pictogram_id=dynamics.get("pictogramId"),
    )


def message_lines(message_text_split: str | None) -> list[str]:
    """Split UTMC line breaks (~) into display lines."""
    if not message_text_split:
        return []
    return [line for line in message_text_split.split("~") if line]


def display_lines(dynamic: VmsDynamic | None) -> list[str]:
    """Return the lines shown on the sign face."""
    if dynamic is None:
        return []
    if dynamic.message_text_split:
        return message_lines(dynamic.message_text_split)
    if dynamic.message_text:
        return [dynamic.message_text]
    return []


def display_text(dynamic: VmsDynamic | None) -> str:
    """Return raw sign text as a single string."""
    lines = display_lines(dynamic)
    return "\n".join(lines)


def _build_static_index(items: list[dict[str, Any]]) -> dict[str, VmsStatic]:
    """Build an O(1) lookup from system code number to static VMS data."""
    index: dict[str, VmsStatic] = {}
    for item in items:
        sign = parse_static_item(item)
        if sign.system_code_number:
            index[sign.system_code_number] = sign
    return index


def _build_dynamic_index(items: list[dict[str, Any]]) -> dict[str, VmsDynamic]:
    """Build an O(1) lookup from system code number to dynamic VMS data."""
    index: dict[str, VmsDynamic] = {}
    for item in items:
        system_code_number = str(item.get("systemCodeNumber", ""))
        if system_code_number:
            index[system_code_number] = parse_dynamic_item(item)
    return index


CredentialsKey = tuple[str, str]


class UTMCStaticCache:
    """Shared static metadata cache keyed by UTMC credentials."""

    def __init__(self) -> None:
        self._indexes: dict[CredentialsKey, dict[str, VmsStatic]] = {}
        self._expires_at: dict[CredentialsKey, float] = {}
        self._locks: dict[CredentialsKey, asyncio.Lock] = {}

    @staticmethod
    def _credentials_key(username: str, password: str) -> CredentialsKey:
        """Return a cache key for a credential pair."""
        return (username, password)

    def invalidate(self, username: str, password: str) -> None:
        """Drop cached static metadata for one credential pair."""
        key = self._credentials_key(username, password)
        self._indexes.pop(key, None)
        self._expires_at.pop(key, None)

    def invalidate_all(self) -> None:
        """Drop all cached static metadata."""
        self._indexes.clear()
        self._expires_at.clear()

    def get_cached_index(self, username: str, password: str) -> dict[str, VmsStatic]:
        """Return the cached static index when still valid, otherwise an empty dict."""
        key = self._credentials_key(username, password)
        if key not in self._indexes:
            return {}
        if time.monotonic() >= self._expires_at.get(key, 0.0):
            return {}
        return self._indexes[key]

    async def async_get_index(
        self,
        username: str,
        password: str,
        fetcher: Callable[[], Awaitable[list[dict[str, Any]]]],
    ) -> dict[str, VmsStatic]:
        """Return the static index for credentials, fetching at most once per TTL."""
        key = self._credentials_key(username, password)
        now = time.monotonic()
        if key in self._indexes and now < self._expires_at.get(key, 0.0):
            return self._indexes[key]

        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            now = time.monotonic()
            if key in self._indexes and now < self._expires_at.get(key, 0.0):
                return self._indexes[key]

            items = await fetcher()
            self._indexes[key] = _build_static_index(items)
            self._expires_at[key] = now + STATIC_CACHE_TTL_SECONDS
            return self._indexes[key]


def get_static_cache(hass: HomeAssistant) -> UTMCStaticCache:
    """Return the shared static metadata cache for this Home Assistant instance."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if "static_cache" not in domain_data:
        domain_data["static_cache"] = UTMCStaticCache()
    return domain_data["static_cache"]


class UTMCApiClient:
    """HTTP client for UTMC VMS feeds."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        static_cache: UTMCStaticCache,
    ) -> None:
        self._session = session
        self._auth = aiohttp.BasicAuth(username, password)
        self._username = username
        self._password = password
        self._static_cache = static_cache

    async def _request_json_once(self, url: str) -> list[dict[str, Any]]:
        """Perform a single HTTP request and parse the JSON array response."""
        headers = {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        try:
            async with self._session.get(
                url,
                auth=self._auth,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 401:
                    raise InvalidAuth("Invalid credentials")
                if response.status == 403:
                    raise CannotConnect(
                        f"HTTP {response.status}: access denied (check credentials)"
                    )
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except InvalidAuth:
            raise
        except aiohttp.ClientError as err:
            raise CannotConnect(str(err)) from err
        except (ValueError, TypeError) as err:
            raise CannotConnect(f"Invalid response from UTMC API: {err}") from err

        if not isinstance(payload, list):
            raise CannotConnect(f"Expected JSON array, got {type(payload).__name__}")
        return payload

    async def _request_json(self, url: str) -> list[dict[str, Any]]:
        """Request JSON with exponential backoff retry on transient failures."""
        last_error: CannotConnect | None = None

        for attempt in range(API_RETRY_MAX_ATTEMPTS):
            try:
                return await self._request_json_once(url)
            except InvalidAuth:
                raise
            except CannotConnect as err:
                last_error = err
                if attempt < API_RETRY_MAX_ATTEMPTS - 1:
                    delay = API_RETRY_BASE_DELAY_SECONDS * (2**attempt)
                    _LOGGER.debug(
                        "UTMC request to %s failed (attempt %s/%s), retrying in %ss: %s",
                        url,
                        attempt + 1,
                        API_RETRY_MAX_ATTEMPTS,
                        delay,
                        err,
                    )
                    await asyncio.sleep(delay)

        assert last_error is not None
        raise last_error

    async def _ensure_sign_index(self) -> dict[str, VmsStatic]:
        """Return the shared static sign index for these credentials."""
        return await self._static_cache.async_get_index(
            self._username,
            self._password,
            lambda: self._request_json(API_STATIC_URL),
        )

    async def async_validate_credentials(self) -> None:
        """Verify credentials by fetching the static VMS feed."""
        await self._ensure_sign_index()

    async def async_get_static_sign(self, sign_id: str) -> VmsStatic:
        """Return cached static data for one sign."""
        index = await self._ensure_sign_index()
        if sign_id not in index:
            raise VmsNotFound(sign_id)
        return index[sign_id]

    async def async_get_dynamic_sign(self, sign_id: str) -> VmsDynamic | None:
        """Return dynamic display data for one sign, if available."""
        try:
            items = await self._request_json(API_DYNAMIC_URL)
            return _build_dynamic_index(items).get(sign_id)
        except UTMCError as err:
            _LOGGER.debug("Dynamic feed unavailable for %s: %s", sign_id, err)
            return None

    async def async_get_sign_data(self, sign_id: str) -> VmsData:
        """Return static and dynamic data for one sign."""
        static = await self.async_get_static_sign(sign_id)
        dynamic = await self.async_get_dynamic_sign(sign_id)
        return VmsData(static=static, dynamic=dynamic)


def create_client(hass: HomeAssistant, username: str, password: str) -> UTMCApiClient:
    """Create an API client using Home Assistant's aiohttp session."""
    return UTMCApiClient(
        async_get_clientsession(hass),
        username,
        password,
        get_static_cache(hass),
    )
