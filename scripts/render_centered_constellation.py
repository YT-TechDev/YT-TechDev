#!/usr/bin/env python3
"""Preview center-aligned, enlarged headings in full-length animated GIFs.

Original GIFs and generators are immutable. Every derived output frame must
preserve the exact decoded RGB pixels at y >= 120 and the source timing.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_DIR = ROOT / "scripts" / "tools_fonts"
SOURCE_HEADER_HEIGHT = 120
# The Languages footer rule begins at y=1021; remove it by cropping the
# final 54px without redrawing the cosmic background or changing particles.
LANGUAGES_FOOTER_TRIM = 54
# Safe-frame experiment: trim only proven empty outer margins. The
# Frameworks "Google Apps Script" label approaches the left edge, so its
# borders are intentionally untouched. Existing particle/label positions
# and color data within the retained region must be byte-pixel identical.
HORIZONTAL_CROP = {
    "languages": (24, 24),
    "frameworks": (0, 0),
    "tools": (20, 20),
}

SECTIONS = {
    "languages": (36, 150, "01  /  LANGUAGES & MARKUP",
                  "FRONTEND & WEB  →  BACKEND & SYSTEMS  →  OTHERS"),
    "frameworks": (64, 100, "02  /  FRAMEWORKS & RUNTIMES",
                   "FROM UI LIBRARIES TO APPLICATION SYSTEMS"),
    "tools": (48, 160, "03  /  TOOLS & PLATFORMS",
              "INSTRUMENTS, INFRASTRUCTURE & AI ASSISTANTS"),
}


def nearest(colors, target):
    return min(range(len(colors)), key=lambda n: sum(
        (a - b) ** 2 for a, b in zip(colors[n], target)
    ))


def indexed_frame(source):
    # Reconstruct an exact per-frame color table from the already decoded GIF.
    # This avoids lossy global RGB re-quantization or palette assumptions.
    colors_with_counts = source.getcolors(maxcolors=257)
    if colors_with_counts is None:
        raise AssertionError("A decoded source frame contains over 256 RGB colors")
    colors = [color for _, color in sorted(colors_with_counts, reverse=True)]
    palette = Image.new("P", (1, 1))
    entries = [component for rgb in colors for component in rgb]
    palette.putpalette(entries + [0] * (768 - len(entries)))
    # Pillow's nearest-palette quantizer is not mathematically exact even
    # when the palette already contains every source color. Map RGB tuples
    # directly to indices to prevent any source-body pixel modifications.
    lookup = {rgb: n for n, rgb in enumerate(colors)}
    indexed = Image.new("P", source.size)
    indexed.putpalette(palette.getpalette())
    indexed.putdata([lookup[rgb] for rgb in source.getdata()])
    if ImageChops.difference(indexed.convert("RGB"), source).getbbox() is not None:
        raise AssertionError("Exact color-index mapping changed source RGB")
    return indexed, colors


def decorate(indexed, colors, heading, subtitle):
    width, height = indexed.size
    foreground = ImageDraw.Draw(indexed)
    background = nearest(colors, (3, 9, 22))
    primary = nearest(colors, (118, 190, 222))
    secondary = nearest(colors, (87, 138, 169))
    foreground.rectangle((0, 0, width - 1, SOURCE_HEADER_HEIGHT - 1), fill=background)
    font_bold = str(FONT_DIR / "DejaVuSans-Bold.ttf")
    font_regular = str(FONT_DIR / "DejaVuSans.ttf")
    center = width // 2
    # The README displays every section at the same CSS width; Languages is
    # 1600px wide, whereas Frameworks and Tools are 1200px. Equal source
    # font sizes therefore render Languages at only 75% of their apparent
    # size. Normalize by source canvas width (67 vs 50px).
    heading_size = round(50 * width / 1200)
    assert abs(heading_size / width - 50 / 1200) < 0.0003
    heading_font = ImageFont.truetype(font_bold, heading_size)
    # Match subtitle optical size across the 1600px Languages art and
    # 1200px Frameworks / Tools art when all images use README width=100%.
    subtitle_size = round(22 * width / 1200)
    subtitle_font = ImageFont.truetype(font_regular, subtitle_size)
    title_box = foreground.textbbox((center, 26), heading,
                                    font=heading_font, anchor="mt")
    subtitle_box = foreground.textbbox((center, 93), subtitle,
                                       font=subtitle_font, anchor="mt")
    assert title_box[0] > 24 and title_box[2] < width - 24, "Title too wide"
    assert title_box[3] < subtitle_box[1] - 2, "Title collides with subtitle"
    assert subtitle_box[0] >= 24 and subtitle_box[2] <= width - 24, (
        "Subtitle exceeds horizontal canvas bounds"
    )
    assert subtitle_box[3] <= SOURCE_HEADER_HEIGHT - 4, (
        "Subtitle clips into particle/body image"
    )
    foreground.text((center, 26), heading, fill=primary,
                    font=heading_font, anchor="mt")
    foreground.text((center, 93), subtitle, fill=secondary,
                    font=subtitle_font, anchor="mt")
    return indexed


def generate(section):
    count, duration, heading, subtitle = SECTIONS[section]
    source_path = ASSETS / f"constellation-{section}.gif"
    target = ASSETS / f"constellation-{section}-centered.gif"
    with Image.open(source_path) as source:
        assert source.n_frames == count and source.info.get("loop") == 0
        frames = []
        for n in range(count):
            source.seek(n)
            assert source.info.get("duration") == duration
            original_rgb = source.convert("RGB")
            indexed, colors = indexed_frame(original_rgb)
            frame = decorate(indexed, colors, heading, subtitle)
            if section == "languages":
                # The footer rule/text live entirely in the cropped strip.
                frame = frame.crop(
                    (0, 0, frame.width, frame.height - LANGUAGES_FOOTER_TRIM)
                )
            left, right = HORIZONTAL_CROP[section]
            assert left >= 0 and right >= 0 and left + right < frame.width
            if left or right:
                frame = frame.crop((left, 0, frame.width - right, frame.height))
            frames.append(frame)

        # No optional global palette: local source RGBs are reconstructed for
        # each frame so the source body's original colors are not discarded.
        frames[0].save(target, format="GIF", save_all=True,
                       append_images=frames[1:], duration=duration,
                       disposal=2, loop=0, optimize=False)

    verify(section)
    print(f"{section}: centered enlarged heading, {count}x{duration}ms: PASS")


def verify(section):
    count, duration, _, _ = SECTIONS[section]
    with Image.open(ASSETS / f"constellation-{section}.gif") as source, \
         Image.open(ASSETS / f"constellation-{section}-centered.gif") as output:
        expected_height = (source.height - LANGUAGES_FOOTER_TRIM
                           if section == "languages" else source.height)
        left, right = HORIZONTAL_CROP[section]
        expected_width = source.width - left - right
        assert output.size == (expected_width, expected_height)
        assert source.n_frames == output.n_frames == count
        assert source.info.get("loop") == output.info.get("loop") == 0
        header = None
        for n in range(count):
            source.seek(n)
            output.seek(n)
            assert source.info.get("duration") == output.info.get("duration") == duration
            expected = source.convert("RGB").crop(
                (left, SOURCE_HEADER_HEIGHT, source.width - right, expected_height))
            actual = output.convert("RGB")
            bottom = actual.crop((0, SOURCE_HEADER_HEIGHT, output.width, output.height))
            if ImageChops.difference(expected, bottom).getbbox() is not None:
                raise AssertionError(f"{section}: frame {n} particle/body pixels differ")
            top = actual.crop((0, 0, output.width, SOURCE_HEADER_HEIGHT))
            if header is None:
                header = top
            elif ImageChops.difference(top, header).getbbox() is not None:
                raise AssertionError(f"{section}: static heading flickers in frame {n}")
    if section == "languages":
        assert expected_height == 1006, "Languages footer removal changed"
        # At x=43 the Languages in-body lane headers begin; do not crop them.
        assert left <= 24 and right <= 24, "Languages crop exceeds approved safety inset"
    if section == "frameworks":
        assert left == right == 0, "Frameworks outer Google Apps Script label at risk"
    if section == "tools":
        assert left <= 20 and right <= 20, "Tools outer station frame at risk"
    print(f"{section}: exact body preservation, heading stability, "
          f"size {expected_width}x{expected_height}, GIF timing PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    for section in SECTIONS:
        (verify if args.verify_only else generate)(section)


if __name__ == "__main__":
    main()
