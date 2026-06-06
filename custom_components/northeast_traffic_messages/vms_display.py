"""Simulated VMS dot-matrix display renderer.

Renders UTMC message lines as an amber-on-black LED matrix, similar to
portable motorway VMS units (MS4-style four-line signs).
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import TYPE_CHECKING, Literal

try:
    from .pictograms import (
        WIND_PICTOGRAM_ID,
        normalize_pictogram_id,
        paste_pictogram,
        paste_pictogram_led_cells,
    )
except ImportError:
    from pictograms import (
        WIND_PICTOGRAM_ID,
        normalize_pictogram_id,
        paste_pictogram,
        paste_pictogram_led_cells,
    )

if TYPE_CHECKING:
    from PIL import Image

# 5x7 dot-matrix glyphs (# = lit, . = off). Space is included.
_DOT_FONT: dict[str, tuple[str, ...]] = {
    " ": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    "A": (
        ".###.",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    "B": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#...#",
        "#...#",
        "####.",
    ),
    "C": (
        ".####",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        ".####",
    ),
    "D": (
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "####.",
    ),
    "E": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#####",
    ),
    "F": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "G": (
        ".####",
        "#....",
        "#....",
        "#.###",
        "#...#",
        "#...#",
        ".####",
    ),
    "H": (
        "#...#",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    "I": (
        ".###.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ),
    "J": (
        "..###",
        "...#.",
        "...#.",
        "...#.",
        "...#.",
        "#..#.",
        ".##..",
    ),
    "K": (
        "#...#",
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    "L": (
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ),
    "M": (
        "#...#",
        "##.##",
        "#.#.#",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
    ),
    "N": (
        "#...#",
        "##..#",
        "#.#.#",
        "#..##",
        "#...#",
        "#...#",
        "#...#",
    ),
    "O": (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "P": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "Q": (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#..#.",
        ".##.#",
    ),
    "R": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    "S": (
        ".####",
        "#....",
        "#....",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    "T": (
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "U": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "V": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
    ),
    "W": (
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#.#.#",
        "##.##",
        "#...#",
    ),
    "X": (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
        "#...#",
    ),
    "Y": (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "Z": (
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#####",
    ),
    "0": (
        ".###.",
        "#...#",
        "#..##",
        "#.#.#",
        "##..#",
        "#...#",
        ".###.",
    ),
    "1": (
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ),
    "2": (
        ".###.",
        "#...#",
        "....#",
        "..##.",
        ".#...",
        "#....",
        "#####",
    ),
    "3": (
        "#####",
        "....#",
        "....#",
        "..##.",
        "....#",
        "#...#",
        ".###.",
    ),
    "4": (
        "...#.",
        "..##.",
        ".#.#.",
        "#..#.",
        "#####",
        "...#.",
        "...#.",
    ),
    "5": (
        "#####",
        "#....",
        "#....",
        "####.",
        "....#",
        "#...#",
        ".###.",
    ),
    "6": (
        "..##.",
        ".#...",
        "#....",
        "####.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "7": (
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        ".#...",
        ".#...",
    ),
    "8": (
        ".###.",
        "#...#",
        "#...#",
        ".###.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "9": (
        ".###.",
        "#...#",
        "#...#",
        ".####",
        "....#",
        "...#.",
        ".##..",
    ),
    ".": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        "..#..",
        "..#..",
    ),
    ",": (
        ".....",
        ".....",
        ".....",
        ".....",
        "..#..",
        "..#..",
        ".#...",
    ),
    "-": (
        ".....",
        ".....",
        ".....",
        "#####",
        ".....",
        ".....",
        ".....",
    ),
    "/": (
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        ".....",
        ".....",
    ),
    "'": (
        "..#..",
        "..#..",
        ".#...",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    "&": (
        ".##..",
        "#..#.",
        "#..#.",
        ".##..",
        "#.#.#",
        "#..#.",
        ".##.#",
    ),
    "?": (
        ".###.",
        "#...#",
        "....#",
        "..##.",
        "..#..",
        ".....",
        "..#..",
    ),
    "!": (
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".....",
        "..#..",
    ),
    "(": (
        ".....",
        "..#..",
        ".#...",
        ".#...",
        ".#...",
        ".#...",
        "..#..",
    ),
    ")": (
        ".....",
        "..#..",
        "...#.",
        "...#.",
        "...#.",
        "...#.",
        "..#..",
    ),
    ":": (
        ".....",
        "..#..",
        ".....",
        ".....",
        ".....",
        "..#..",
        ".....",
    ),
}

CHAR_WIDTH = 5
CHAR_HEIGHT = 7
CHAR_GAP = 1
LINE_GAP = 2
DEFAULT_MAX_LINES = 4
# UK MS4 strategic text signs: four lines of up to 18 characters each.
MS4_MAX_LINES = 4
MS4_MAX_CHARS_PER_LINE = 18
MS4_MATRIX_COLS = (
    MS4_MAX_CHARS_PER_LINE * CHAR_WIDTH
    + (MS4_MAX_CHARS_PER_LINE - 1) * CHAR_GAP
)
MS4_MATRIX_ROWS = (
    MS4_MAX_LINES * CHAR_HEIGHT + (MS4_MAX_LINES - 1) * LINE_GAP
)


@dataclass(frozen=True)
class VmsDisplayOptions:
    """Rendering options for the simulated sign."""

    max_lines: int = DEFAULT_MAX_LINES
    lanterns_on: bool = False
    sign_id: str | None = None
    sign_name: str | None = None
    pictogram_id: str | None = None
    message_category: str | None = None


def _is_pictogram_full_category(category: str | None) -> bool:
    if not category:
        return False
    return "pictogram full" in category.casefold()


def normalize_char(char: str) -> str:
    """Map a character to a supported glyph key."""
    if char in _DOT_FONT:
        return char
    upper = char.upper()
    if upper in _DOT_FONT:
        return upper
    return "?"


def line_pixel_width(text: str) -> int:
    """Width in LED columns for one line of text."""
    if not text:
        return 0
    return len(text) * CHAR_WIDTH + max(0, len(text) - 1) * CHAR_GAP


def _pad_ms4_lines(lines: list[str], *, max_lines: int = MS4_MAX_LINES) -> list[str]:
    """Normalise to a fixed MS4 line layout, truncating overlong lines."""
    padded: list[str] = []
    for index in range(MS4_MAX_LINES):
        if index < len(lines) and index < max_lines:
            padded.append(lines[index][:MS4_MAX_CHARS_PER_LINE])
        else:
            padded.append("")
    return padded


def render_lines_to_grid(
    lines: list[str],
    *,
    max_lines: int = MS4_MAX_LINES,
) -> list[list[bool]]:
    """Build a fixed-size MS4 dot grid from up to four message lines."""
    grid = [[False] * MS4_MATRIX_COLS for _ in range(MS4_MATRIX_ROWS)]

    row_offset = 0
    for line in _pad_ms4_lines(lines, max_lines=max_lines):
        line_width = line_pixel_width(line)
        col_offset = (MS4_MATRIX_COLS - line_width) // 2 if line_width else 0

        char_col = col_offset
        for char in line:
            glyph = _DOT_FONT[normalize_char(char)]
            for row_idx, pattern in enumerate(glyph):
                for col_idx, pixel in enumerate(pattern):
                    if pixel == "#":
                        grid[row_offset + row_idx][char_col + col_idx] = True
            char_col += CHAR_WIDTH + CHAR_GAP

        row_offset += CHAR_HEIGHT + LINE_GAP

    return grid


def _ansi_enabled() -> bool:
    import os
    import sys

    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return True


def _terminal_symbols() -> dict[str, str]:
    """Pick glyphs that the active stdout encoding can print."""
    import sys

    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    unicode_symbols = {
        "lit": "●",
        "off": "·",
        "frame_h": "═",
        "frame_v": "║",
        "lamp_on": "◉",
        "lamp_off": "○",
    }
    ascii_symbols = {
        "lit": "#",
        "off": ".",
        "frame_h": "=",
        "frame_v": "|",
        "lamp_on": "@",
        "lamp_off": "o",
    }
    try:
        for value in unicode_symbols.values():
            value.encode(encoding)
        return unicode_symbols
    except UnicodeEncodeError:
        return ascii_symbols


def render_terminal(
    lines: list[str],
    *,
    options: VmsDisplayOptions | None = None,
) -> str:
    """Render message lines as an amber dot matrix in the terminal."""
    options = options or VmsDisplayOptions()
    display_lines = lines[: options.max_lines]
    grid = render_lines_to_grid(display_lines, max_lines=options.max_lines)

    symbols = _terminal_symbols()
    amber = "\033[38;5;208m" if _ansi_enabled() else ""
    dim = "\033[2m" if _ansi_enabled() else ""
    reset = "\033[0m" if _ansi_enabled() else ""
    bg = "\033[48;5;232m" if _ansi_enabled() else ""

    lit = f"{amber}{symbols['lit']}{reset}"
    off = f"{dim}{symbols['off']}{reset}" if _ansi_enabled() else symbols["off"]

    inner_width = len(grid[0]) if grid else 0
    frame_h = symbols["frame_h"] * (inner_width + 2)
    corner_lamps = symbols["lamp_on"] if options.lanterns_on else symbols["lamp_off"]

    out: list[str] = []
    out.append(f"{corner_lamps}{frame_h}{corner_lamps}")
    for row in grid:
        dots = "".join(lit if on else off for on in row)
        out.append(f"{symbols['frame_v']}{bg}{dots}{reset}{symbols['frame_v']}")
    out.append(f"{corner_lamps}{frame_h}{corner_lamps}")

    if options.sign_id or options.sign_name:
        meta = " - ".join(
            part for part in (options.sign_id, options.sign_name) if part
        )
        out.append(meta)

    return "\n".join(out)


def render_html(
    lines: list[str],
    *,
    options: VmsDisplayOptions | None = None,
) -> str:
    """Render a self-contained HTML page simulating a portable VMS."""
    options = options or VmsDisplayOptions()
    display_lines = lines[: options.max_lines]
    grid = render_lines_to_grid(display_lines, max_lines=options.max_lines)

    rows_html: list[str] = []
    for row in grid:
        cells = "".join(
            '<span class="dot on"></span>' if on else '<span class="dot"></span>'
            for on in row
        )
        rows_html.append(f'<div class="row">{cells}</div>')

    lantern_class = "lantern on" if options.lanterns_on else "lantern"
    title_parts = [p for p in (options.sign_id, options.sign_name) if p]
    title = " — ".join(title_parts) if title_parts else "VMS Display"
    message_plain = "\n".join(display_lines)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(180deg, #6eb5e8 0%, #9ed0f0 45%, #c8e4c0 100%);
      font-family: system-ui, sans-serif;
    }}
    .scene {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
      padding: 2rem;
    }}
    .vms-unit {{
      position: relative;
      background: #1a1a1a;
      border: 6px solid #111;
      border-radius: 4px;
      padding: 14px;
      box-shadow: 0 12px 40px rgba(0,0,0,0.45);
    }}
    .vms-unit::before {{
      content: "";
      position: absolute;
      inset: 14px;
      background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(255,255,255,0.03) 2px,
        rgba(255,255,255,0.03) 4px
      );
      pointer-events: none;
      z-index: 1;
    }}
    .frame {{
      position: relative;
      background: #050505;
      padding: 18px 14px;
      border: 2px solid #222;
    }}
    .lantern {{
      position: absolute;
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: #333;
      border: 2px solid #444;
      z-index: 3;
    }}
    .lantern.on.tl,
    .lantern.on.tr {{
      animation: flash-top-pair 0.8s step-end infinite;
    }}
    .lantern.on.bl,
    .lantern.on.br {{
      animation: flash-bottom-pair 0.8s step-end infinite;
    }}
    .lantern.tl {{ top: 6px; left: 6px; }}
    .lantern.tr {{ top: 6px; right: 6px; }}
    .lantern.bl {{ bottom: 6px; left: 6px; }}
    .lantern.br {{ bottom: 6px; right: 6px; }}
    @keyframes flash-top-pair {{
      0%, 49% {{
        background: #ffaa00;
        border-color: #ffcc44;
        box-shadow: 0 0 12px #ffaa00, 0 0 24px rgba(255,170,0,0.6);
      }}
      50%, 100% {{
        background: #333;
        border-color: #444;
        box-shadow: none;
      }}
    }}
    @keyframes flash-bottom-pair {{
      0%, 49% {{
        background: #333;
        border-color: #444;
        box-shadow: none;
      }}
      50%, 100% {{
        background: #ffaa00;
        border-color: #ffcc44;
        box-shadow: 0 0 12px #ffaa00, 0 0 24px rgba(255,170,0,0.6);
      }}
    }}
    .matrix {{
      position: relative;
      z-index: 2;
      display: flex;
      flex-direction: column;
      gap: 1px;
      line-height: 0;
    }}
    .row {{
      display: flex;
      gap: 1px;
      justify-content: center;
    }}
    .dot {{
      width: 3px;
      height: 3px;
      border-radius: 50%;
      background: #1a1208;
      flex-shrink: 0;
    }}
    .dot.on {{
      background: #ffaa00;
      box-shadow: 0 0 2px #ffaa00;
    }}
    .post {{
      width: 28px;
      height: 48px;
      background: linear-gradient(90deg, #111, #333, #111);
      margin: 0 auto;
    }}
    .trailer {{
      width: 120px;
      height: 28px;
      background: #e8c400;
      border-radius: 3px;
      margin: 0 auto;
      box-shadow: inset 0 -4px 0 #c9a800;
    }}
    .caption {{
      color: #1a2a3a;
      font-size: 0.85rem;
      text-align: center;
      max-width: 420px;
      white-space: pre-wrap;
    }}
    .caption strong {{
      display: block;
      font-size: 1rem;
      margin-bottom: 0.25rem;
    }}
  </style>
</head>
<body>
  <div class="scene">
    <div class="vms-unit">
      <div class="frame">
        <span class="{lantern_class} tl"></span>
        <span class="{lantern_class} tr"></span>
        <span class="{lantern_class} bl"></span>
        <span class="{lantern_class} br"></span>
        <div class="matrix">
          {"".join(rows_html)}
        </div>
      </div>
      <div class="post"></div>
      <div class="trailer"></div>
    </div>
    <div class="caption">
      <strong>{escape(title)}</strong>
      {escape(message_plain) if message_plain else "(blank display)"}
    </div>
  </div>
</body>
</html>
"""


# JPEG sign colours (sign face only — no post, trailer, or captions)
_COLOUR_FRAME = (17, 17, 17)
_COLOUR_PANEL = (0, 0, 0)
_COLOUR_DOT_OFF = (20, 20, 20)
_COLOUR_DOT_ON = (255, 153, 0)
_COLOUR_DOT_GLOW = (255, 120, 0)
_COLOUR_LANTERN_OFF = (64, 64, 64)
_COLOUR_LANTERN_ON = (255, 153, 0)
_COLOUR_WIND_TRIANGLE = (215, 20, 20)
_COLOUR_WIND_WHITE = (245, 245, 245)
# TSRGD: amber lamps flash 60–90 times/minute in alternating horizontal pairs.
_LANTERN_FLASHES_PER_MIN = 75
_GIF_FRAME_MS = 60000 // (2 * _LANTERN_FLASHES_PER_MIN)  # 400ms → 75 flashes/min

LanternPair = Literal["top", "bottom", "off"]
IMAGE_CELL_PX = 6
IMAGE_LIT_DOT_RADIUS = 2
IMAGE_OFF_DOT_RADIUS = 1
# Side-winds cabinets are pictogram-only and much narrower than MS4 text signs.
WIND_PICTOGRAM_AREA_WIDTH = 30 * IMAGE_CELL_PX
WIND_PICTOGRAM_AREA_HEIGHT = 28 * IMAGE_CELL_PX


def _draw_lit_dot(draw, x: int, y: int, radius: int) -> None:
    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill=_COLOUR_DOT_ON,
    )


def _lantern_corners(
    panel_left: int,
    panel_top: int,
    panel_right: int,
    panel_bottom: int,
    inset: int,
) -> tuple[tuple[int, int], ...]:
    return (
        (panel_left + inset, panel_top + inset),
        (panel_right - inset, panel_top + inset),
        (panel_left + inset, panel_bottom - inset),
        (panel_right - inset, panel_bottom - inset),
    )


def _lit_lantern_indices(pair: LanternPair) -> frozenset[int]:
    """Corner indices: 0=top-left, 1=top-right, 2=bottom-left, 3=bottom-right."""
    if pair == "top":
        return frozenset({0, 1})
    if pair == "bottom":
        return frozenset({2, 3})
    return frozenset()


def _draw_lanterns(
    draw,
    corners: tuple[tuple[int, int], ...],
    *,
    pair: LanternPair,
    radius: int,
) -> None:
    lit_corners = _lit_lantern_indices(pair)
    for index, (lx, ly) in enumerate(corners):
        lit = index in lit_corners
        if lit:
            draw.ellipse(
                (
                    lx - radius - 3,
                    ly - radius - 3,
                    lx + radius + 3,
                    ly + radius + 3,
                ),
                fill=(255, 190, 60),
            )
        draw.ellipse(
            (lx - radius, ly - radius, lx + radius, ly + radius),
            fill=_COLOUR_LANTERN_ON if lit else _COLOUR_LANTERN_OFF,
            outline=(48, 48, 48),
        )


def is_wind_vms_sign(sign_id: str | None) -> bool:
    """Return True for Durham wind-warning VMS assets (WIND VMS 1, etc.)."""
    if not sign_id:
        return False
    return sign_id.strip().upper().startswith("WIND VMS")


def _sign_face_layout(
    grid: list[list[bool]],
) -> tuple[int, int, int, int, int, int, int, int, int, int, int]:
    """Return sign face dimensions shared by text and pictogram renders."""
    cell = IMAGE_CELL_PX
    matrix_cols = len(grid[0]) if grid else 1
    matrix_rows = len(grid) if grid else 1
    return _sign_face_layout_for_matrix(
        matrix_cols * cell,
        matrix_rows * cell,
    )


def _sign_face_layout_for_matrix(
    matrix_w: int,
    matrix_h: int,
) -> tuple[int, int, int, int, int, int, int, int, int, int, int]:
    """Return sign face dimensions for a matrix of the given pixel size."""
    panel_pad_x = 28
    panel_pad_y = 28
    frame_border = 8
    lantern_r = 8
    lantern_inset = 14

    panel_w = matrix_w + panel_pad_x * 2
    panel_h = matrix_h + panel_pad_y * 2
    img_w = panel_w + frame_border * 2
    img_h = panel_h + frame_border * 2

    panel_left = frame_border
    panel_top = frame_border
    panel_right = panel_left + panel_w
    panel_bottom = panel_top + panel_h
    matrix_left = panel_left + panel_pad_x
    matrix_top = panel_top + panel_pad_y

    return (
        img_w,
        img_h,
        panel_left,
        panel_top,
        panel_right,
        panel_bottom,
        matrix_left,
        matrix_top,
        matrix_w,
        matrix_h,
        lantern_inset,
        lantern_r,
    )


def _wind_sign_face_layout() -> tuple[int, int, int, int, int, int, int, int, int, int, int]:
    """Return a compact sign face sized to the side-winds pictogram."""
    return _sign_face_layout_for_matrix(
        WIND_PICTOGRAM_AREA_WIDTH,
        WIND_PICTOGRAM_AREA_HEIGHT,
    )


def _draw_led_matrix(
    draw,
    grid: list[list[bool]],
    *,
    matrix_left: int,
    matrix_top: int,
) -> None:
    cell = IMAGE_CELL_PX
    for row_idx, row in enumerate(grid):
        for col_idx, on in enumerate(row):
            cx = matrix_left + col_idx * cell + cell // 2
            cy = matrix_top + row_idx * cell + cell // 2
            if on:
                _draw_lit_dot(draw, cx, cy, IMAGE_LIT_DOT_RADIUS)
            else:
                draw.ellipse(
                    (
                        cx - IMAGE_OFF_DOT_RADIUS,
                        cy - IMAGE_OFF_DOT_RADIUS,
                        cx + IMAGE_OFF_DOT_RADIUS,
                        cy + IMAGE_OFF_DOT_RADIUS,
                    ),
                    fill=_COLOUR_DOT_OFF,
                )


def _draw_wind_warning_pictogram(
    draw,
    *,
    matrix_left: int,
    matrix_top: int,
    matrix_w: int,
    matrix_h: int,
) -> None:
    """Draw the UK side-winds triangle and windsock used on WIND VMS signs."""
    cx = matrix_left + matrix_w // 2
    cy = matrix_top + matrix_h // 2
    tri_size = int(min(matrix_w, matrix_h) * 0.88)
    half_base = tri_size // 2
    tri_height = int(tri_size * 0.866)

    apex = (cx, cy - tri_height // 2)
    base_left = (cx - half_base, cy + tri_height // 2)
    base_right = (cx + half_base, cy + tri_height // 2)

    border = max(5, tri_size // 16)
    draw.polygon([apex, base_left, base_right], fill=_COLOUR_WIND_TRIANGLE)

    inset = border * 2
    inner_half = max(1, half_base - inset)
    inner_height = max(1, tri_height - inset * 2)
    inner_apex = (cx, cy - inner_height // 2)
    inner_left = (cx - inner_half, cy + inner_height // 2)
    inner_right = (cx + inner_half, cy + inner_height // 2)
    draw.polygon([inner_apex, inner_left, inner_right], fill=_COLOUR_PANEL)

    pole_x = cx - inner_half // 4
    pole_top = cy - inner_height // 5
    pole_bottom = cy + inner_height // 3
    pole_w = max(3, tri_size // 36)
    draw.rectangle(
        (pole_x - pole_w, pole_top, pole_x + pole_w, pole_bottom),
        fill=_COLOUR_WIND_WHITE,
    )

    sock_front = pole_x + pole_w + 2
    sock_back = sock_front + int(inner_half * 0.82)
    sock_mid_y = (pole_top + pole_bottom) // 2
    sock_top = pole_top + inner_height // 10
    sock_bottom = pole_bottom - inner_height // 12
    draw.polygon(
        [
            (sock_front, sock_top),
            (sock_back, sock_mid_y - inner_height // 10),
            (sock_back, sock_mid_y + inner_height // 10),
            (sock_front, sock_bottom),
        ],
        fill=_COLOUR_WIND_WHITE,
    )
    stripe_w = max(2, tri_size // 45)
    for offset in (0.28, 0.52, 0.76):
        stripe_x = sock_front + int((sock_back - sock_front) * offset)
        draw.rectangle(
            (
                stripe_x,
                sock_top + inner_height // 14,
                stripe_x + stripe_w,
                sock_bottom - inner_height // 14,
            ),
            fill=_COLOUR_WIND_TRIANGLE,
        )


def render_wind_sign_image(
    *,
    lantern_pair: LanternPair = "off",
    show_pictogram: bool = True,
    pictogram_id: str | None = None,
) -> Image.Image:
    """Render the compact WIND VMS face (blank when inactive, pictogram when active)."""
    from PIL import Image, ImageDraw

    (
        img_w,
        img_h,
        panel_left,
        panel_top,
        panel_right,
        panel_bottom,
        matrix_left,
        matrix_top,
        matrix_w,
        matrix_h,
        lantern_inset,
        lantern_r,
    ) = _wind_sign_face_layout()

    image = Image.new("RGB", (img_w, img_h), _COLOUR_FRAME)
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        (panel_left, panel_top, panel_right, panel_bottom),
        fill=_COLOUR_PANEL,
    )
    if show_pictogram:
        active_id = normalize_pictogram_id(pictogram_id) or WIND_PICTOGRAM_ID
        if not paste_pictogram(
            image,
            active_id,
            left=matrix_left,
            top=matrix_top,
            width=matrix_w,
            height=matrix_h,
        ):
            _draw_wind_warning_pictogram(
                draw,
                matrix_left=matrix_left,
                matrix_top=matrix_top,
                matrix_w=matrix_w,
                matrix_h=matrix_h,
            )
    _draw_lanterns(
        draw,
        _lantern_corners(
            panel_left,
            panel_top,
            panel_right,
            panel_bottom,
            lantern_inset,
        ),
        pair=lantern_pair if show_pictogram else "off",
        radius=lantern_r,
    )
    return image


def render_wind_warning_image(*, lantern_pair: LanternPair = "off") -> Image.Image:
    """Render the side-winds pictogram face used when WIND VMS lanterns flash."""
    return render_wind_sign_image(lantern_pair=lantern_pair, show_pictogram=True)


def render_image(
    lines: list[str],
    *,
    options: VmsDisplayOptions | None = None,
    lantern_pair: LanternPair | None = None,
) -> Image.Image:
    """Render the VMS sign face (matrix + corner lanterns) as a Pillow image."""
    from PIL import Image, ImageDraw

    options = options or VmsDisplayOptions()
    if lantern_pair is None:
        lantern_pair = "top" if options.lanterns_on else "off"
    if is_wind_vms_sign(options.sign_id):
        return render_wind_sign_image(
            lantern_pair=lantern_pair,
            show_pictogram=options.lanterns_on,
            pictogram_id=options.pictogram_id or WIND_PICTOGRAM_ID,
        )

    display_lines = lines[: options.max_lines]
    pictogram_id = normalize_pictogram_id(options.pictogram_id)
    pictogram_full = _is_pictogram_full_category(options.message_category)
    grid = render_lines_to_grid(display_lines, max_lines=options.max_lines)
    (
        img_w,
        img_h,
        panel_left,
        panel_top,
        panel_right,
        panel_bottom,
        matrix_left,
        matrix_top,
        matrix_w,
        matrix_h,
        lantern_inset,
        lantern_r,
    ) = _sign_face_layout(grid)

    image = Image.new("RGB", (img_w, img_h), _COLOUR_FRAME)
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        (panel_left, panel_top, panel_right, panel_bottom),
        fill=_COLOUR_PANEL,
    )
    if pictogram_id and pictogram_full:
        paste_pictogram(
            image,
            pictogram_id,
            left=matrix_left,
            top=matrix_top,
            width=matrix_w,
            height=matrix_h,
        )
    else:
        _draw_led_matrix(
            draw,
            grid,
            matrix_left=matrix_left,
            matrix_top=matrix_top,
        )
        if pictogram_id:
            paste_pictogram_led_cells(
                image,
                pictogram_id,
                left=matrix_left,
                top=matrix_top,
                cell_px=IMAGE_CELL_PX,
            )
    _draw_lanterns(
        draw,
        _lantern_corners(
            panel_left,
            panel_top,
            panel_right,
            panel_bottom,
            lantern_inset,
        ),
        pair=lantern_pair,
        radius=lantern_r,
    )

    return image


def render_gif_frames(
    lines: list[str],
    *,
    options: VmsDisplayOptions | None = None,
) -> list[Image.Image]:
    """Build top/bottom lantern pair frames for a flashing VMS GIF."""
    options = options or VmsDisplayOptions()
    if is_wind_vms_sign(options.sign_id):
        if options.lanterns_on:
            return [
                render_wind_sign_image(
                    lantern_pair="top",
                    show_pictogram=True,
                    pictogram_id=options.pictogram_id or WIND_PICTOGRAM_ID,
                ),
                render_wind_sign_image(
                    lantern_pair="bottom",
                    show_pictogram=True,
                    pictogram_id=options.pictogram_id or WIND_PICTOGRAM_ID,
                ),
            ]
        return [render_wind_sign_image(lantern_pair="off", show_pictogram=False)]
    return [
        render_image(lines, options=options, lantern_pair="top"),
        render_image(lines, options=options, lantern_pair="bottom"),
    ]


def resolve_output_path(path: Path | str) -> Path:
    """Resolve a user-supplied output path within the current working directory."""
    cwd = Path.cwd().resolve()
    target = Path(path).resolve()
    if target != cwd and cwd not in target.parents:
        raise ValueError(f"Output path must stay within {cwd}")
    return target


def write_html(
    lines: list[str],
    path: Path | str,
    *,
    options: VmsDisplayOptions | None = None,
) -> Path:
    """Write simulated VMS HTML to a file."""
    target = resolve_output_path(path)
    target.write_text(
        render_html(lines, options=options),
        encoding="utf-8",
    )
    return target


def _image_output_path(path: Path) -> Path:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"} or suffix != ".gif":
        return path.with_suffix(".gif")
    return path


def write_vms_image(
    lines: list[str],
    path: Path | str,
    *,
    options: VmsDisplayOptions | None = None,
    quality: int = 90,  # noqa: ARG001 — kept for backwards-compatible call sites.
) -> Path:
    """Write the VMS sign face as a GIF (animated if lanterns are flashing)."""
    options = options or VmsDisplayOptions()
    target = _image_output_path(resolve_output_path(path))

    if options.lanterns_on:
        frames = render_gif_frames(lines, options=options)
        frames[0].save(
            target,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=_GIF_FRAME_MS,
            loop=0,
        )
        return target

    render_image(lines, options=options, lantern_pair="off").save(
        target,
        format="GIF",
    )
    return target


def write_gif(
    lines: list[str],
    path: Path | str,
    *,
    options: VmsDisplayOptions | None = None,
    quality: int = 90,
) -> Path:
    """Write simulated VMS sign face to GIF."""
    return write_vms_image(lines, path, options=options, quality=quality)


def render_vms_gif_bytes(
    lines: list[str],
    *,
    options: VmsDisplayOptions | None = None,
) -> bytes:
    """Render the VMS sign face to GIF bytes (animated if lanterns are flashing)."""
    from io import BytesIO

    options = options or VmsDisplayOptions()
    buffer = BytesIO()
    if options.lanterns_on:
        frames = render_gif_frames(lines, options=options)
        frames[0].save(
            buffer,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=_GIF_FRAME_MS,
            loop=0,
        )
    else:
        render_image(lines, options=options, lantern_pair="off").save(
            buffer,
            format="GIF",
        )
    return buffer.getvalue()


def open_image(path: Path | str) -> None:
    """Open an image with the system default viewer."""
    target = Path(path).resolve()
    if sys.platform == "win32":
        os.startfile(target)  # noqa: S606
        return
    if sys.platform == "darwin":
        subprocess.run(["open", str(target)], check=False)
        return
    subprocess.run(["xdg-open", str(target)], check=False)


def demo_lines() -> list[str]:
    """Sample lines matching a typical event parking VMS."""
    return ["FOR EVENT", "PARKING", "TAKE NEXT", "SLIP ROAD"]
