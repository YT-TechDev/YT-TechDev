#!/usr/bin/env python3
"""Preview center-aligned, enlarged headings in full-length animated GIFs.

Original GIFs and generators are immutable. Every derived output frame must
preserve the exact decoded RGB pixels at y >= 120 and the source timing.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_DIR = ROOT / "scripts" / "tools_fonts"
SOURCE_HEADER_HEIGHT = 120

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
    indexed = source.quantize(palette=palette, dither=Image.Dither.NONE)
    if ImageChops.difference(indexed.convert("RGB"), source).getbbox() is not None:
        raise AssertionError("RGB colors changed when mapping to the exact input palette")
    return indexed, colors


def decorate(indexed, colors, heading, subtitle):
    width, height = indexed.size
    foreground = ImageDraw.Draw(indexed)
    background = nearest(colors, (3, 9, 22))
    eyebrow = nearest(colors, (177, 220, 242))
    primary = nearest(colors, (118, 190, 222))
    secondary = nearest(colors, (87, 138, 169))
    foreground.rectangle((0, 0, width - 1, SOURCE_HEADER_HEIGHT - 1), fill=background)
    font_bold = str(FONT_DIR / "DejaVuSans-Bold.ttf")
    font_regular = str(FONT_DIR / "DejaVuSans.ttf")
    center = width // 2
    foreground.text((center, 11), "YT-TECHDEV   /   SKILL CONSTELLATION",
                    fill=eyebrow, font=ImageFont.truetype(font_bold, 25), anchor="mt")
    foreground.text((center, 45), heading, fill=primary,
                    font=ImageFont.truetype(font_bold, 40), anchor="mt")
    foreground.text((center, 98), subtitle, fill=secondary,
                    font=ImageFont.truetype(font_regular, 17), anchor="mt")
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
            frames.append(decorate(indexed, colors, heading, subtitle))

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
        assert source.size == output.size
        assert source.n_frames == output.n_frames == count
        assert source.info.get("loop") == output.info.get("loop") == 0
        header = None
        for n in range(count):
            source.seek(n)
            output.seek(n)
            assert source.info.get("duration") == output.info.get("duration") == duration
            expected = source.convert("RGB").crop(
                (0, SOURCE_HEADER_HEIGHT, source.width, source.height))
            actual = output.convert("RGB")
            bottom = actual.crop((0, SOURCE_HEADER_HEIGHT, output.width, output.height))
            if ImageChops.difference(expected, bottom).getbbox() is not None:
                raise AssertionError(f"{section}: frame {n} particle/body pixels differ")
            top = actual.crop((0, 0, output.width, SOURCE_HEADER_HEIGHT))
            if header is None:
                header = top
            elif ImageChops.difference(top, header).getbbox() is not None:
                raise AssertionError(f"{section}: static heading flickers in frame {n}")
    print(f"{section}: exact body preservation, heading stability and GIF timing PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    for section in SECTIONS:
        (verify if args.verify_only else generate)(section)


if __name__ == "__main__":
    main()
