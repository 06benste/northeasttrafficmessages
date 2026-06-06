"""Demo VMS sign data for integration preview."""

from __future__ import annotations

from homeassistant.util import dt as dt_util

from .api import VmsData, VmsDynamic, VmsStatic
from .const import DEMO_FRIENDLY_ID, DEMO_SIGN_ID
from .vms_display import demo_lines


def is_demo_sign_id(sign_id: str) -> bool:
    """Return True when the config entry is the built-in demo sign."""
    return sign_id == DEMO_SIGN_ID


def is_demo_sign_code(sign_code: str) -> bool:
    """Return True when the user entered the demo sign code."""
    return sign_code.strip().upper() == DEMO_FRIENDLY_ID.upper()


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
