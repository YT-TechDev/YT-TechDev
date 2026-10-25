#!/usr/bin/env python3
"""Check Languages artwork, label clearance and the encoded animation seam.

These checks complement, rather than replace, inspection of the PNG/GIF.
"""
from __future__ import annotations

import json
import math
from unittest.mock import patch

from PIL import Image, ImageChops, ImageDraw, ImageStat

from render_sections import (
    ROOT, SEED, SECTIONS, floating_offset, make_language_background, prepared_nodes,
    render_frame,
)

NAMES = (
    "HTML", "CSS", "JavaScript", "TypeScript", "VBScript",
    "Python", "Java", "MoonBit", "C++", "Rust",
)


def main():
    cfg = SECTIONS["languages"]
    original = json.loads((ROOT / "data/icon-paths.json").read_text("utf-8"))
    extra = json.loads((ROOT / "data/supplemental-icons.json").read_text("utf-8"))
    extra["paths"].update(extra["devicon_paths"])
    nodes = prepared_nodes("languages", cfg, original, extra["paths"])
    assert tuple(node[1] for node in nodes) == NAMES, "Language order changed"
    assert cfg["columns"] == (164, 482, 800, 1118, 1436)
    assert cfg["rows"] == (231, 531), "Expected five columns and two rows"
    bg = make_language_background(780, SEED + len("languages") * 19, 1600)
    repeated_bg = make_language_background(780, SEED + len("languages") * 19, 1600)
    assert ImageChops.difference(bg, repeated_bg).getbbox() is None, "Background seed is unstable"
    # The icon field must stay dark even with the new stars, haze and dust.
    for _, _, _, _, _, x, y, _ in nodes:
        field = bg.crop((x - 105, y - 100, x + 105, y + 100)).convert("L")
        assert field.getextrema()[1] < 60, "Background competes with an icon"

    texts, lines = [], []
    original_text, original_line = ImageDraw.ImageDraw.text, ImageDraw.ImageDraw.line

    def record_text(draw, xy, text, *args, **kwargs):
        texts.append((xy, text, kwargs))
        return original_text(draw, xy, text, *args, **kwargs)

    def record_line(draw, xy, *args, **kwargs):
        lines.append(xy)
        return original_line(draw, xy, *args, **kwargs)

    with patch.object(ImageDraw.ImageDraw, "text", record_text), \
         patch.object(ImageDraw.ImageDraw, "line", record_line):
        expected_png = render_frame("languages", cfg, bg, nodes, 0, freeze=True)
    assert lines == [(43, 741, 1558, 741)], "Only the footer rule may remain"
    drawn_text = [text for _, text, _ in texts]
    for tag in {node[4] for node in nodes if node[4]}:
        assert tag not in drawn_text, f"Secondary label displayed: {tag}"

    draw = ImageDraw.Draw(expected_png)
    gaps = []
    for _, name, _, _, _, x, y, points in nodes:
        matches = [(xy, options) for xy, text, options in texts if text == name]
        assert len(matches) == 1, f"Missing or repeated name: {name}"
        xy, options = matches[0]
        assert xy == (x, y + 120) and options["anchor"] == "mm"
        assert options["font"].size == 40, "Language label font differs"
        box = draw.textbbox(xy, name, font=options["font"], anchor="mm")
        # Continuous worst case: both vertical sine amplitudes plus dot radius.
        gap = box[1] - (y + max(py for _, py in points) + 10.5 + 1.8 + 1)
        assert gap >= 12, f"Floating icon can collide with {name}: {gap:.1f}px"
        assert x - 150 <= box[0] < box[2] <= x + 150, "Label leaves its column"
        gaps.append(gap)

    png_path = ROOT / "assets/constellation-languages.png"
    with Image.open(png_path) as png:
        png.verify()
    with Image.open(png_path) as png:
        assert png.size == (1600, 780)
        assert ImageChops.difference(png.convert("RGB"), expected_png).getbbox() is None

    for index in range(10):
        start = floating_offset(index, 0)
        end = floating_offset(index, math.tau)
        assert all(abs(a - b) < 1e-10 for a, b in zip(start, end)), "Position seam"
    first = render_frame("languages", cfg, bg, nodes, 0)
    endpoint = render_frame("languages", cfg, bg, nodes, math.tau)
    assert ImageChops.difference(first, endpoint).getbbox() is None, "Rendered seam"

    frames = []
    with Image.open(ROOT / "assets/constellation-languages.gif") as gif:
        assert gif.size == (1600, 780) and gif.n_frames == 36
        assert gif.info.get("loop") == 0
        for index in range(gif.n_frames):
            gif.seek(index)
            assert gif.info.get("duration") == 150, "GIF timing changed"
            frame = gif.convert("RGB")
            frame.load()  # Fully decode every frame, including partial GIF frames.
            assert frame.size == (1600, 780)
            frames.append(frame)

    # Decode real GIF pixels: a common palette must prevent haze/dust shimmer.
    background_mask = Image.new("L", (1600, 780), 255)
    mask_draw = ImageDraw.Draw(background_mask)
    mask_draw.rectangle((0, 0, 1599, 159), fill=0)
    mask_draw.rectangle((0, 730, 1599, 779), fill=0)
    for _, _, _, _, _, x, y, _ in nodes:
        mask_draw.rectangle((x - 120, y - 110, x + 120, y + 110), fill=0)
        mask_draw.rectangle((x - 153, y + 90, x + 153, y + 150), fill=0)
    assert background_mask.getbbox(), "No exposed background checked"
    for frame in frames[1:]:
        delta = ImageChops.difference(frames[0], frame)
        assert ImageChops.multiply(delta, background_mask.convert("RGB")).getbbox() is None, "Static background flickers"

    def distance(a, b):
        return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3

    steps = [distance(frames[i], frames[(i + 1) % 36]) for i in range(36)]
    assert min(steps) > 0, "Animation contains a frozen transition"
    assert steps[-1] <= max(steps[:-1]) * 1.25, "Encoded GIF jumps at its seam"
    print("Languages: 10 names, no status labels/connectors; PNG verified")
    print(f"Minimum moving-icon/label clearance: {min(gaps):.1f}px")
    print("GIF: 36 decoded frames, 1600x780, 150ms/frame, 5.4s, infinite loop")
    print("Cosmic background: deterministic, dark behind icons, no encoded shimmer")
    print(f"Loop pixel delta: {steps[-1]:.4f}; interior maximum: {max(steps[:-1]):.4f}")
    print("Asset and loop checks passed; visual review is a separate check")


if __name__ == "__main__":
    main()
