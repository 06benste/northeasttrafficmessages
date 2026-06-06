"""Demo VMS sign data for integration preview."""

from __future__ import annotations

from homeassistant.util import dt as dt_util

from .api import VmsData, VmsDynamic, VmsStatic
from .const import (
    DEMO_FRIENDLY_ID,
    DEMO_SIGN_ID,
    DEMO_WIND_FRIENDLY_ID,
    DEMO_WIND_SIGN_ID,
    DEMO_WIND_RENDER_SIGN_ID,
)
from .vms_display import demo_lines


def is_demo_sign_id(sign_id: str) -> bool:
    """Return True when the config entry is the built-in demo sign."""
    return sign_id == DEMO_SIGN_ID


def is_demo_wind_sign_id(sign_id: str) -> bool:
    """Return True when the config entry is the built-in wind demo sign."""
    return sign_id == DEMO_WIND_SIGN_ID


def is_offline_demo_sign_id(sign_id: str) -> bool:
    """Return True for demo signs that do not use the UTMC API."""
    return is_demo_sign_id(sign_id) or is_demo_wind_sign_id(sign_id)


def is_demo_sign_code(sign_code: str) -> bool:
    """Return True when the user entered the demo sign code."""
    return sign_code.strip().upper() == DEMO_FRIENDLY_ID.upper()


def is_demo_wind_sign_code(sign_code: str) -> bool:
    """Return True when the user entered the wind demo sign code."""
    return sign_code.strip().lower() == DEMO_WIND_FRIENDLY_ID.lower()


def render_sign_id_for_config(sign_id: str) -> str:
    """Return the sign ID passed to the VMS renderer for a config entry."""
    if is_demo_wind_sign_id(sign_id):
        return DEMO_WIND_RENDER_SIGN_ID
    return sign_id


def build_demo_vms() -> tuple[VmsData, list[str], str]:
    """Return VMS data for the sample sign with flashing lanterns."""
    lines = demo_lines()
    text = "\n".join(lines)
    now = dt_util.utcnow()
    static = VmsStatic(
        system_code_number=DEMO_SIGN_ID,
        short_description="VMS Demo",
        long_description="Sample event parking message (no UTMC connection)",
        easting=None,
        northing=None,
        latitude=None,
        longitude=None,
        road_name=None,
        creation_date=now,
        data_source="Demo",
    )
    dynamic = VmsDynamic(
        message_text=text,
        message_text_split="~".join(lines),
        sign_setting_reason="No Override",
        last_updated=now,
        lantern_state=1,
        category="Demo",
        message_name="Demo",
        pictogram_id=None,
    )
    return VmsData(static=static, dynamic=dynamic), lines, text


def build_demo_wind_vms() -> tuple[VmsData, list[str], str]:
    """Return VMS data for the side-winds pictogram demo sign."""
    lines: list[str] = []
    text = ""
    now = dt_util.utcnow()
    static = VmsStatic(
        system_code_number=DEMO_WIND_SIGN_ID,
        short_description="WIND VMS Demo",
        long_description="Sample side-winds warning pictogram (no UTMC connection)",
        easting=None,
        northing=None,
        latitude=None,
        longitude=None,
        road_name=None,
        creation_date=now,
        data_source="Demo",
    )
    dynamic = VmsDynamic(
        message_text=text,
        message_text_split="",
        sign_setting_reason="No Override",
        last_updated=now,
        lantern_state=1,
        category="Demo",
        message_name="Side winds",
        pictogram_id="G7",
    )
    return VmsData(static=static, dynamic=dynamic), lines, text
