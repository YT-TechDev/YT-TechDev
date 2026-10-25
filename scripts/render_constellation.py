#!/usr/bin/env python3
"""Render GitHub profile particle artwork from the pinned portfolio icon snapshot.

Usage:
  python scripts/render_constellation.py --out assets/constellation.gif
  python scripts/render_constellation.py --static --out assets/constellation.png

No network, GitHub tokens, browser runtime or telemetry required.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import random
import re
from pathlib import Path

import cairosvg
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 1200, 620
SEED = 847291

# Manually reviewed public work categories; these are never proficiency scores.
STARS = [
    ("react", "React", "building", "#66e8ff", 150, 158),
    ("typescript", "TypeScript", "building", "#74b8ff", 431, 149),
    ("r3f", "R3F", "building", "#cba8ff", 710, 148),
    ("nextjs", "Next.js", "used", "#eeeeff", 994, 174),
    ("javascript", "JavaScript", "used", "#f2df77", 210, 340),
    ("nodejs", "Node.js", "used", "#8ee9a6", 486, 336),
    ("docker", "Docker", "used", "#69c9fb", 762, 344),
    ("postgresql", "PostgreSQL", "used", "#9ec1ff", 1049, 344),
    ("python", "Python", "used", "#a9d0e8", 153, 506),
    ("cloudflare", "Cloudflare", "used", "#ffbc70", 431, 502),
    ("git", "Git", "used", "#ff967b", 710, 503),
    ("rust", "Rust", "exploring", "#d99368", 991, 500),
]
EDGES = ((0, 1), (1, 2), (2, 3), (0, 4), (1, 5), (2, 6), (3, 7),
         (4, 5), (5, 6), (6, 7), (4, 8), (5, 9), (6, 10), (7, 11),
         (8, 9), (9, 10), (10, 11))


def font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for filename in candidates:
        if Path(filename).is_file():
            return ImageFont.truetype(filename, size)
    return ImageFont.load_default()


def glyph_svg(key: str, paths: dict, rust_path: str) -> str:
    if key == "react":
        ellipse = "".join(
            f'<ellipse cx="0" cy="0" rx="1.55" ry=".48" '
            f'transform="rotate({r})" fill="none" stroke="white" stroke-width=".09"/>'
            for r in (0, 60, 120)
        )
        return ('<svg xmlns="http://www.w3.org/2000/svg" '
                'viewBox="-2 -1.8 4 3.6">' + ellipse +
                '<circle cx="0" cy="0" r=".18" fill="white"/></svg>')
    if key == "nextjs":
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 4 4">'
                '<circle cx="0" cy="0" r="1.45" fill="none" stroke="white" stroke-width=".1"/>'
                '<path d="M-.7 1V-1L.8 1V-1" stroke="white" stroke-width=".13" fill="none"/></svg>')
    if key == "r3f":
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 200">'
                '<text x="130" y="148" font-family="DejaVu Sans,sans-serif" font-size="111" '
                'font-weight="700" fill="white" text-anchor="middle">R3F</text></svg>')
    if key == "rust":
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
                f'<path fill="white" d="{rust_path}"/></svg>')
    outlines = paths.get(key)
    if not outlines:
        raise ValueError(f"Missing outline for {key}")
    # The source paths are not all 24x24; render generously and crop painted bounds.
    values = [abs(float(n)) for p in outlines for n in re.findall(
        r"(?<![A-Za-z])[-+]?(?:\d*\.\d+|\d+)(?:[Ee][-+]?\d+)?", p
    )]
    size = max(max(values, default=24) * 1.8, 28)
    paths_svg = "".join(f'<path fill="white" d="{p}"/>' for p in outlines)
    offset = -size * .14
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{offset:.2f} {offset:.2f} {size:.2f} {size:.2f}">'
            f'{paths_svg}</svg>')


def sample_edge_points(svg: str, key: str, count: int, rng: random.Random):
    binary = cairosvg.svg2png(bytestring=svg.encode(), output_width=520, output_height=520)
    alpha = Image.open(io.BytesIO(binary)).convert("RGBA").getchannel("A")
    box = alpha.getbbox()
    if box is None:
        raise ValueError(f"SVG not visible: {key}")
    alpha = alpha.crop(box)
    alpha.thumbnail((142, 118), Image.Resampling.LANCZOS)
    edge = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(3)))
    width, height = alpha.size
    p = edge.load()
    candidates = [(x - width / 2, y - height / 2)
                  for y in range(height) for x in range(width) if p[x, y] > 24]
    if len(candidates) < 10:
        p = alpha.load()
        candidates = [(x - width / 2, y - height / 2)
                      for y in range(height) for x in range(width) if p[x, y] > 50]
    if len(candidates) < 10:
        raise ValueError(f"Insufficient boundary samples: {key}")
    return [rng.choice(candidates) for _ in range(count)]


def background(rng: random.Random):
    img = Image.new("RGB", (W, H), (3, 9, 22))
    haze = Image.new("RGBA", (W, H))
    hd = ImageDraw.Draw(haze, "RGBA")
    hd.ellipse((95, -350, 1030, 710), fill=(35, 53, 112, 54))
    hd.ellipse((550, -100, 1460, 530), fill=(10, 138, 175, 22))
    hd.ellipse((-290, 140, 530, 780), fill=(83, 50, 137, 27))
    haze = haze.filter(ImageFilter.GaussianBlur(90))
    img.paste(haze, (0, 0), haze)
    draw = ImageDraw.Draw(img)
    for _ in range(280):
        x, y = rng.randrange(W), rng.randrange(H)
        v = rng.choice((29, 36, 45, 55, 66, 82, 106))
        draw.point((x, y), fill=(v, v + 7, v + 28))
    return img


def frame(bg, icons, phase, frozen=False):
    result = bg.copy()
    draw = ImageDraw.Draw(result)
    for a, b in EDGES:
        draw.line((icons[a][4], icons[a][5], icons[b][4], icons[b][5]),
                  fill=(19, 45, 67), width=1)
    draw.text((48, 29), "YT-TECHDEV   /   SKILL CONSTELLATION",
              fill=(148, 190, 217), font=font(16, True))
    draw.text((48, 56), "BUILT FROM PARTICLES, GROUNDED IN WORK",
              fill=(69, 109, 139), font=font(12))
    for i, (key, label, activity, color, x0, y0, samples) in enumerate(icons):
        weight = {"building": 1.0, "used": .72, "exploring": .42}[activity]
        dr = 0 if frozen else math.sin(phase + i * .85) * 2.5
        dy = 0 if frozen else math.cos(phase + i * .53) * 2.9
        x, y = x0 + dr, y0 + dy
        for j, (px, py) in enumerate(samples):
            pulse = 1 if frozen else (.79 + .21 * math.sin(phase * 1.65 + j * .12 + i))
            intensity = weight * pulse
            shade = tuple(int(int(color[n:n+2], 16) * intensity) for n in (1, 3, 5))
            sx, sy = round(x + px), round(y + py)
            draw.point((sx, sy), fill=shade)
            if j % 11 == 0:
                draw.ellipse((sx - 1, sy - 1, sx + 1, sy + 1), fill=shade)
        draw.text((x0, y0 + 70), label, anchor="mm", font=font(14, True),
                  fill=(181, 197, 214) if activity != "exploring" else (120, 125, 140))
    draw.line((48, 590, 1152, 590), fill=(20, 50, 69))
    draw.text((48, 601), "BRIGHTNESS = PROJECT ACTIVITY   /   NOT PROFICIENCY",
              fill=(102, 142, 167), font=font(11))
    draw.text((1148, 601), "BUILDING / USED / EXPLORING",
              fill=(98, 133, 162), font=font(11), anchor="ra")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=ROOT / "data/icon-paths.json")
    ap.add_argument("--out", type=Path, default=ROOT / "assets/constellation.gif")
    ap.add_argument("--frames", type=int, default=28)
    ap.add_argument("--static", action="store_true")
    args = ap.parse_args()
    if not 1 <= args.frames <= 120:
        ap.error("Frame count must be in the range 1..120")
    obj = json.loads(args.data.read_text(encoding="utf8"))
    if obj.get("source_commit") != "6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27":
        raise ValueError("Pinned source commit mismatch: explicit review required")
    rng = random.Random(SEED)
    icons = [(key, label, activity, color, x, y,
              sample_edge_points(glyph_svg(key, obj["paths"], obj["rust_path"]),
                                 key, 350 if activity == "building" else 280, rng))
             for key, label, activity, color, x, y in STARS]
    bg = background(rng)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.static:
        frame(bg, icons, 0, frozen=True).save(args.out, optimize=True)
    else:
        images = [frame(bg, icons, math.tau * i / args.frames)
                  for i in range(args.frames)]
        images[0].save(args.out, format="GIF", save_all=True, append_images=images[1:],
                       duration=95, loop=0, disposal=2, optimize=True)
    print(f"Rendered {args.out}: {args.out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
