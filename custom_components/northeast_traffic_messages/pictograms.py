"""UTMC VMS pictogram assets shipped with the integration."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from PIL import Image

PICTOGRAM_ID_PATTERN = re.compile(r"(\S+\.bmp)\s*=\s*(G\d+)", re.IGNORECASE)
WIND_PICTOGRAM_ID = "G7"
ASSETS_DIR_NAME = "VMS Pictogram Assets"
ID_LIST_FILENAME = "BITMAP & PICTOGRAM ID LIST.txt"


def _component_dir() -> Path:
    return Path(__file__).resolve().parent


def pictogram_assets_dir() -> Path:
    """Return the bundled UTMC pictogram asset directory."""
    here = _component_dir()
    candidates = (
        here / ASSETS_DIR_NAME,
        here
        / "Homeassistant"
        / "custom_components"
        / "northeast_traffic_messages"
        / ASSETS_DIR_NAME,
    )
    for path in candidates:
        if path.is_dir():
            return path
    return candidates[0]


def normalize_pictogram_id(pictogram_id: str | None) -> str | None:
    """Normalise a UTMC pictogram id for lookup."""
    if not pictogram_id:
        return None
    normalized = pictogram_id.strip().upper().replace(" ", "")
    return normalized or None


@lru_cache(maxsize=1)
def pictogram_filename_by_id() -> dict[str, str]:
    """Map pictogram ids (G7, G23, …) to BMP filenames."""
    mapping: dict[str, str] = {}
    list_path = pictogram_assets_dir() / ID_LIST_FILENAME
    if list_path.is_file():
        for match in PICTOGRAM_ID_PATTERN.finditer(
            list_path.read_text(encoding="utf-8", errors="ignore")
        ):
            mapping[match.group(2).upper()] = match.group(1)
    return mapping


def pictogram_path_for_id(pictogram_id: str | None) -> Path | None:
    """Return the BMP path for a pictogram id, if bundled."""
    normalized = normalize_pictogram_id(pictogram_id)
    if not normalized:
        return None
    filename = pictogram_filename_by_id().get(normalized)
    if not filename:
        return None
    path = pictogram_assets_dir() / filename
    return path if path.is_file() else None


@lru_cache(maxsize=32)
def load_pictogram_rgb(pictogram_id: str) -> Image.Image | None:
    """Load a pictogram asset as an RGB image."""
    path = pictogram_path_for_id(pictogram_id)
    if path is None:
        return None
    with Image.open(path) as handle:
        image = handle.convert("RGB")
    return image.copy()


def scale_pictogram_nearest(
    pictogram: Image.Image,
    *,
    target_width: int,
    target_height: int,
) -> Image.Image:
    """Scale a pictogram to fit within a target box, preserving pixel edges."""
    if pictogram.width <= 0 or pictogram.height <= 0:
        return pictogram
    scale = min(target_width / pictogram.width, target_height / pictogram.height)
    scaled_w = max(1, int(round(pictogram.width * scale)))
    scaled_h = max(1, int(round(pictogram.height * scale)))
    return pictogram.resize((scaled_w, scaled_h), Image.Resampling.NEAREST)


def paste_pictogram(
    target: Image.Image,
    pictogram_id: str | None,
    *,
    left: int,
    top: int,
    width: int,
    height: int,
    align: str = "center",
) -> bool:
    """Paste a bundled pictogram onto an RGB image. Returns True when pasted."""
    pictogram = load_pictogram_rgb(pictogram_id) if pictogram_id else None
    if pictogram is None:
        return False

    scaled = scale_pictogram_nearest(
        pictogram,
        target_width=width,
        target_height=height,
    )
    if align == "topleft":
        paste_x = left
        paste_y = top
    else:
        paste_x = left + (width - scaled.width) // 2
        paste_y = top + (height - scaled.height) // 2
    target.paste(scaled, (paste_x, paste_y))
    return True


def paste_pictogram_led_cells(
    target: Image.Image,
    pictogram_id: str | None,
    *,
    left: int,
    top: int,
    cell_px: int,
) -> bool:
    """Paste a pictogram using one BMP pixel per LED cell."""
    pictogram = load_pictogram_rgb(pictogram_id) if pictogram_id else None
    if pictogram is None:
        return False
    scaled = pictogram.resize(
        (pictogram.width * cell_px, pictogram.height * cell_px),
        Image.Resampling.NEAREST,
    )
    target.paste(scaled, (left, top))
    return True
