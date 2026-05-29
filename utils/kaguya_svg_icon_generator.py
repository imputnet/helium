#!/usr/bin/env python3

# Copyright 2026 The Kaguya Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Generate Kaguya branding icons from the procedural crescent geometry."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFilter, ImageFont


_BASE_CANVAS = 1254.0
_OUTER_CENTER_X = 695.0
_OUTER_CENTER_Y = 625.0
_INNER_CENTER_X = 882.0
_INNER_CENTER_Y = 570.0
_OUTER_RADIUS = 399.5
_INNER_RADIUS = 326.0

_APP_ICON_SIZE = 1024
_APP_ICON_OUTER_CORNER = 0.262  # tuned to match previous icon rounding.

_CRESCENT_CANVAS = 56.0
_CRESCENT_PATH: Sequence[tuple[float, float]] = (
    (33.3232, 52.0297),
    (28.0, 56.0),
    (22.6768, 52.0297),
    (25.0958, 33.0855),
    (10.0649, 44.6731),
    (4.0, 42.0),
    (4.74054, 35.3577),
    (22.1898, 28.0),
    (4.74054, 20.6423),
    (4.0, 14.0),
    (10.0649, 11.3269),
    (25.0958, 22.9145),
    (22.6768, 3.97031),
    (28.0, 0.0),
    (33.3232, 3.97031),
    (30.9042, 22.9145),
    (45.9351, 11.3269),
    (52.0, 14.0),
    (51.2595, 20.6423),
    (33.8102, 28.0),
    (51.2595, 35.3577),
    (52.0, 42.0),
    (45.9351, 44.6731),
    (30.9042, 33.0855),
)


def _lerp(start: int, end: int, t: float) -> int:
    return int(start + (end - start) * t)


def _font_path(preferred: Iterable[str]) -> str | None:
    fc_match = shutil.which("fc-match")
    if fc_match is None:
        return None
    for font in preferred:
        try:
            output = subprocess.check_output(
                [fc_match, "-f", "%{file}", font],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (CalledProcessError, OSError):
            continue
        if output:
            font_path = Path(output)
            if font_path.exists():
                return str(font_path)
    return None


def _load_font(height: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    families = (
        "DejaVuSans-Bold" if bold else "DejaVu Sans",
        "Liberation Sans",
        "Arial",
    )
    fallback = None

    font_path = _font_path(families)
    if font_path:
        try:
            return ImageFont.truetype(font_path, height)
        except OSError:
            fallback = None

    try:
        return ImageFont.truetype("DejaVuSans.ttf", height)
    except OSError:
        fallback = None

    return fallback or ImageFont.load_default()


def _draw_icon_mask(size: int) -> Image.Image:
    scale = size / _BASE_CANVAS
    outer_x = _OUTER_CENTER_X * scale
    outer_y = _OUTER_CENTER_Y * scale
    inner_x = _INNER_CENTER_X * scale
    inner_y = _INNER_CENTER_Y * scale
    outer_r = _OUTER_RADIUS * scale
    inner_r = _INNER_RADIUS * scale

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (outer_x - outer_r, outer_y - outer_r, outer_x + outer_r, outer_y + outer_r),
        fill=255,
    )
    draw.ellipse(
        (inner_x - inner_r, inner_y - inner_r, inner_x + inner_r, inner_y + inner_r),
        fill=0,
    )
    return mask


def _render_crescent(size: int, color: tuple[int, int, int, int]) -> Image.Image:
    mask = _draw_icon_mask(size)
    crescent = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    core = Image.new("RGBA", (size, size), color)
    crescent.paste(core, mask=mask)

    highlight = Image.new("RGBA", (size, size), (255, 255, 255, 40))
    highlight.putalpha(mask)
    highlight = highlight.filter(ImageFilter.GaussianBlur(size * 0.02))
    crescent.alpha_composite(highlight)
    return crescent


def _render_background(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    top = (4, 7, 39)
    mid = (23, 28, 99)
    bottom = (81, 41, 188)
    for y in range(size):
        ratio = y / max(1, (size - 1))
        if ratio < 0.47:
            t = ratio / 0.47
            rgb = (_lerp(top[0], mid[0], t), _lerp(top[1], mid[1], t), _lerp(top[2], mid[2], t))
        else:
            t = (ratio - 0.47) / 0.53
            rgb = (_lerp(mid[0], bottom[0], t), _lerp(mid[1], bottom[1], t), _lerp(mid[2], bottom[2], t))
        draw.line((0, y, size, y), fill=rgb + (255,), width=1)

    corner = int(size * _APP_ICON_OUTER_CORNER)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=corner, fill=255)
    image.putalpha(mask)

    glow_left = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_left)
    left_radius = int(size * 0.68)
    glow_draw.ellipse(
        (size * 0.11, -size * 0.06, size * 0.58, size * 0.75),
        fill=(79, 102, 234, 88),
    )
    glow_left = glow_left.filter(ImageFilter.GaussianBlur(size * 0.08))

    glow_bottom = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_bottom)
    glow_draw.ellipse(
        (size * 0.26, size * 0.55, size * 1.03, size * 1.55),
        fill=(56, 11, 94, 96),
    )
    glow_bottom = glow_bottom.filter(ImageFilter.GaussianBlur(size * 0.10))

    moon = _render_crescent(size, (246, 246, 254, 255))

    image.alpha_composite(glow_left)
    image.alpha_composite(glow_bottom)
    image.alpha_composite(moon)
    return image


def _render_wordmark(width: int, height: int, color: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    icon_size = max(16, int(height * 0.68))
    spacing = max(6, int(height * 0.15))
    icon = _render_crescent(icon_size, (*color, 255))
    icon_y = max(0, (height - icon_size) // 2)
    image.alpha_composite(icon, (height * 0 // 1, icon_y))

    text = "Kaguya"
    text_color = (*color, 255)
    font_size = int(height * 0.56)
    font = _load_font(font_size, bold=True)

    text_x = icon_size + spacing
    if isinstance(font, ImageFont.FreeTypeFont):
        while True:
            left, top, right, bottom = font.getbbox(text)
            text_w, text_h = right - left, bottom - top
            if text_x + text_w <= width - 2 or font_size <= 12:
                break
            font_size -= 1
            font = _load_font(font_size, bold=True)
    else:
        left = 0
        top = 0
        text_w = len(text) * max(1, font_size // 3)
        text_h = max(1, font_size)

    text_x = max(text_x, 0)
    text_y = max(0, (height - text_h) // 2 - top)
    draw = ImageDraw.Draw(image)
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    return image


def _icon_path_to_text() -> str:
    path_parts = [f"M{_CRESCENT_PATH[0][0]:.4f} {_CRESCENT_PATH[0][1]:.4f}"]
    for point in _CRESCENT_PATH[1:]:
        path_parts.append(f"L{point[0]:.4f} {point[1]:.4f}")
    path_parts.append("Z")
    return " ".join(path_parts)


def _write_svg(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    path = _icon_path_to_text()
    output.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg width="56" height="56" viewBox="0 0 56 56" fill="none" '
        'xmlns="http://www.w3.org/2000/svg">\n'
        '  <rect width="56" height="56" rx="14.56" fill="#3450D1"/>\n'
        f'  <path d="{path}" fill="#FBFCFF"/>\n'
        "</svg>\n",
        encoding="utf-8",
    )


def _write_icon(output: Path, *, has_background: bool) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "// Copyright 2026 The Kaguya Authors\n",
        "// You can use, redistribute, and/or modify this source code under\n",
        "// the terms of the GPL-3.0 license that can be found in the LICENSE file.\n",
        "\n",
        "CANVAS_DIMENSIONS, 56,\n",
    ]

    if has_background:
        lines.append("NEW_PATH,\n")
        lines.append("PATH_COLOR_ARGB, 0xFF, 0x34, 0x50, 0xD1,\n")
        lines.append("ROUND_RECT, 0, 0, 56, 56, 14,\n")

    lines.append("NEW_PATH,\n")
    lines.append("FILL_RULE_NONZERO,\n")
    lines.append("PATH_COLOR_ARGB, 0xFF, 0xFB, 0xFC, 0xFF,\n")
    first_x, first_y = _CRESCENT_PATH[0]
    lines.append(f"MOVE_TO, {first_x:.4f}, {first_y:.4f},\n")
    for point_x, point_y in _CRESCENT_PATH[1:]:
        lines.append(f"LINE_TO, {point_x:.4f}, {point_y:.4f},\n")
    lines.append("CLOSE\n")

    output.write_text("".join(lines), encoding="utf-8")


def _write_crescent_png(output: Path, size: int, color: tuple[int, int, int] = (0, 0, 0)) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    image = _render_crescent(size, (*color, 255))
    image.save(output, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Kaguya-branded resources from procedural geometry."
    )
    parser.add_argument(
        "--resources-dir",
        type=Path,
        default=Path("kaguya-chromium/resources"),
        help="Directory containing branding resources.",
    )
    parser.add_argument(
        "--app-icon-size",
        type=int,
        default=_APP_ICON_SIZE,
        help="Output size for branding/app_icon/raw.png.",
    )
    args = parser.parse_args()

    resources = args.resources_dir
    branding = resources / "branding"
    app_icon = branding / "app_icon"
    app_icon.mkdir(parents=True, exist_ok=True)

    raw_path = app_icon / "raw.png"
    file_path = app_icon / "file.png"
    product_logo_svg = branding / "product_logo.svg"
    product_logo_icon = branding / "product_logo.icon"
    product_logo_color_icon = branding / "product_logo_color.icon"
    product_logo = branding / "product_logo.png"
    product_logo_white = branding / "product_logo_white.png"
    product_logo_200 = branding / "product_logo_200.png"
    product_logo_white_200 = branding / "product_logo_white_200.png"
    product_logo_mono = branding / "product_logo_22_mono.png"

    app = _render_background(args.app_icon_size)
    app.save(raw_path, optimize=True)

    app_thumb = app.resize((512, 512), Image.Resampling.LANCZOS)
    app_thumb.save(file_path, optimize=True)

    _write_svg(product_logo_svg)
    _write_icon(product_logo_icon, has_background=False)
    _write_icon(product_logo_color_icon, has_background=True)

    _write_crescent_png(product_logo_mono, 22, (119, 119, 119))
    _write_crescent_png(product_logo, 32)
    _write_crescent_png(product_logo_white, 32, (255, 255, 255))

    for target, text_color in (
        ((140, 32), (0, 0, 0)),
        ((280, 64), (0, 0, 0)),
    ):
        _render_wordmark(*target, text_color).save(
            product_logo if target == (140, 32) else product_logo_200,
            optimize=True,
        )
        _render_wordmark(*target, (255, 255, 255)).save(
            product_logo_white if target == (140, 32) else product_logo_white_200,
            optimize=True,
        )

    print(f"Generated Kaguya resources into {branding}")


if __name__ == "__main__":
    main()
