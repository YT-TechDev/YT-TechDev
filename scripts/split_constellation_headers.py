#!/usr/bin/env python3
"""Build README-only header PNGs and cropped particle GIFs from frozen assets.

The original three posters and GIFs are deliberately immutable; the derived
assets are lossless spatial crops of their decoded pixels. No particle renderer
or motion function is changed.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
HEADER_HEIGHT = 120
SECTIONS = {
    "languages": ((1600, 1060), 36, 150),
    "frameworks": ((1200, 1110), 64, 100),
    "tools": ((1200, 900), 48, 160),
}


def paths(section):
    return (
        ASSETS / f"constellation-{section}.png",
        ASSETS / f"constellation-{section}.gif",
        ASSETS / f"constellation-{section}-header.png",
        ASSETS / f"constellation-{section}-body.gif",
    )


def generate(section):
    size, count, duration = SECTIONS[section]
    poster_path, original_path, header_path, body_path = paths(section)
    width, height = size
    with Image.open(poster_path) as poster:
        assert poster.size == size, f"{section}: unexpected poster size"
        header = poster.convert("RGB").crop((0, 0, width, HEADER_HEIGHT))
        header.save(header_path, format="PNG", optimize=True)

    # Gifsicle preserves the original GIF color tables, timing and frame data;
    # re-quantizing decoded RGB frames with Pillow changed approved colors.
    # Crop before final verification, without resampling or dithering.
    subprocess.run(
        [
            "gifsicle",
            "--crop", f"0,{HEADER_HEIGHT}+{width}x{height-HEADER_HEIGHT}",
            "--logical-screen", f"{width}x{height-HEADER_HEIGHT}",
            str(original_path), "-o", str(body_path),
        ],
        check=True,
    )
    verify(section)
    print(f"{section}: header {width}x{HEADER_HEIGHT}, body {width}x{height-HEADER_HEIGHT}, "
          f"{count} frames x {duration}ms: PASS")


def verify(section):
    size, count, duration = SECTIONS[section]
    width, height = size
    poster_path, original_path, header_path, body_path = paths(section)
    with Image.open(poster_path) as poster, Image.open(header_path) as header:
        assert header.size == (width, HEADER_HEIGHT)
        expected = poster.convert("RGB").crop((0, 0, width, HEADER_HEIGHT))
        assert ImageChops.difference(header.convert("RGB"), expected).getbbox() is None, (
            section, "header pixels differ"
        )

    with Image.open(original_path) as original, Image.open(body_path) as body:
        assert body.size == (width, height - HEADER_HEIGHT)
        assert body.n_frames == original.n_frames == count
        assert body.info.get("loop") == original.info.get("loop") == 0
        for i in range(count):
            original.seek(i)
            body.seek(i)
            assert body.info.get("duration") == original.info.get("duration") == duration
            expected = original.convert("RGB").crop((0, HEADER_HEIGHT, width, height))
            actual = body.convert("RGB")
            delta = ImageChops.difference(actual, expected)
            assert delta.getbbox() is None, f"{section}: decoded frame {i} differs"
    print(f"{section}: decoded GIF pixels and metadata match the original crop")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    for section in SECTIONS:
        if args.verify_only:
            verify(section)
        else:
            generate(section)


if __name__ == "__main__":
    main()
