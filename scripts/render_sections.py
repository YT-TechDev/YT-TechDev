#!/usr/bin/env python3
"""Render independent README GIF/PNG particle constellations by technology group.

This uses frozen data from the user's portfolio plus a pinned supplemental icon
snapshot. All renders are offline, deterministic and README-compatible.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter
from render_constellation import font, sample_outline

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1200
SEED = 847291
COLUMNS = (187, 600, 1013)
ACTIVITY_BRIGHTNESS = {
    "building": 1.00,
    "used": .96,
    "exploring": .94,
    "ai-tool": .96,
}
SECTIONS = {
    "languages": {
        "title": "01  /  LANGUAGES & MARKUP",
        "subtitle": "FRONTEND & WEB  →  SCRIPTING  →  BACKEND & SYSTEMS",
        "width": 1600,
        "height": 780,
        "columns": (164, 482, 800, 1118, 1436),
        "rows": (231, 531),
        "icons": [
            ("html", "HTML", "used", "#ffb081", "PROFESSIONAL"),
            ("css", "CSS", "used", "#8dd6ff", "PROFESSIONAL"),
            ("javascript", "JavaScript", "used", "#f3dc79", None),
            ("typescript", "TypeScript", "building", "#74b8ff", None),
            ("vbscript", "VBScript", "used", "#c6b8fb", "DEPLOYED"),
            ("python", "Python", "used", "#a7d8fa", None),
            ("java", "Java", "used", "#ffd19b", "PROFESSIONAL"),
            ("moonbit", "MoonBit", "used", "#d2a7f5", "WIF RUNTIME"),
            ("cplusplus", "C++", "exploring", "#b8baff", "EXPLORING"),
            ("rust", "Rust", "exploring", "#edab8f", "EXPLORING"),
        ],
    },
    "frameworks": {
        "title": "02  /  FRAMEWORKS & RUNTIMES",
        "subtitle": "FROM WEB FRAMEWORKS TO WASM EXECUTION",
        "height": 560,
        "rows": (177, 385),
        "icons": [
            ("react", "React", "building", "#79f1ff", None),
            ("nextjs", "Next.js", "used", "#f1f3fd", None),
            ("nodejs", "Node.js", "used", "#a9efb8", None),
            ("r3f", "R3F", "building", "#dcc2ff", None),
            ("threedotjs", "Three.js", "used", "#c6e9f9", None),
            ("webassembly", "WebAssembly", "used", "#b7bdff", None),
        ],
    },
    "tools": {
        "title": "03  /  TOOLS & PLATFORMS",
        "subtitle": "DEVELOPMENT, INFRASTRUCTURE & AI ASSISTANTS",
        "height": 810,
        "rows": (172, 392, 611),
        "icons": [
            ("postgresql", "PostgreSQL", "used", "#a8d4ff", None),
            ("docker", "Docker", "used", "#8dd9ff", None),
            ("git", "Git", "used", "#ffaf8f", None),
            ("cloudflare", "Cloudflare", "used", "#ffd49a", None),
            ("linux", "Linux", "used", "#eed4b5", None),
            ("vscode", "VS Code", "used", "#a2c8ff", None),
            ("blender", "Blender", "used", "#fbc392", None),
            ("chatgpt", "ChatGPT", "ai-tool", "#aeefd8", "AI TOOL"),
            ("claude", "Claude", "ai-tool", "#ffbfa4", "AI TOOL"),
        ],
    },
}


def make_background(height: int, seed: int, width: int = WIDTH) -> Image.Image:
    rng = random.Random(seed)
    bg = Image.new("RGB", (width, height), "#040d1d")
    nebula = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(nebula, "RGBA")
    d.ellipse((120, -290, 1100, height + 390), fill=(23, 67, 128, 67))
    d.ellipse((580, -160, 1510, height + 120), fill=(10, 108, 166, 32))
    d.ellipse((-250, 190, 460, height + 240), fill=(87, 51, 145, 30))
    nebula = nebula.filter(ImageFilter.GaussianBlur(110))
    bg.paste(nebula, (0, 0), nebula)
    draw = ImageDraw.Draw(bg)
    for _ in range(int(height * .34)):
        x, y = rng.randrange(width), rng.randrange(height)
        s = rng.choice((33, 42, 55, 71, 96, 135, 170))
        draw.point((x, y), fill=(s // 2, s * 3 // 4, min(255, s)))
    return bg


def sample_official_moonbit(count, rng):
    """Sample silhouette and interior edges of MoonBit's OWN logo artwork.

    Frozen from moonbitlang/moonbit-docs at commit
    50bbd2f59ba80ed046b6ecad57c7e8507ca06e9e/next/_static/logo.png.
    Not a hand-drawn moon or approximate M glyph.
    """
    source = ROOT / "assets/moonbit-official.png"
    with Image.open(source) as source_image:
        img = source_image.convert("RGBA")
    bounds = img.getchannel("A").getbbox()
    if not bounds:
        raise ValueError("Official MoonBit logo has no painted pixels")
    img = img.crop(bounds)
    img.thumbnail((174, 166), Image.Resampling.LANCZOS)
    w, h = img.size
    pixels = img.load()
    alpha = img.getchannel("A")
    outer = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(5)))
    outline = outer.load()
    choices = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            rgba = pixels[x, y]
            if rgba[3] < 72:
                continue
            neighbors = (pixels[x + 1, y], pixels[x, y + 1])
            color_edge = any(
                v[3] > 72 and max(abs(rgba[i] - v[i]) for i in range(3)) > 43
                for v in neighbors
            )
            if outline[x, y] > 26 or color_edge:
                choices.append((x - w / 2, y - h / 2))
    if len(choices) < 500:
        raise ValueError("Official MoonBit contour incomplete")
    rng.shuffle(choices)
    return [choices[i % len(choices)] for i in range(count)]


def prepared_nodes(section_id, cfg, originals, extras):
    rng = random.Random(SEED + len(section_id) * 23)
    nodes = []
    for i, (key, label, category, color, tag) in enumerate(cfg["icons"]):
        # More points for every icon than the original low-visibility last rows.
        count = 1450 if section_id == "languages" else 1000
        if key == "moonbit":
            samples = sample_official_moonbit(count, rng)
        else:
            samples = sample_outline(key, originals, extras, count, rng)
        if key == "typescript" and section_id == "languages":
            # The TS glyph previously appeared smaller; round its raster edges
            # in the source sampler and normalize optical scale with label clearance.
            samples = [(x * 1.04, y * 1.04) for x, y in samples]
        columns = cfg.get("columns", COLUMNS)
        nodes.append((key, label, category, color, tag, columns[i % len(columns)],
                      cfg["rows"][i // len(columns)], samples))
    return nodes


def floating_offset(index: int, phase: float) -> tuple[float, float]:
    """Smooth periodic zero-gravity drift for one language constellation."""
    x = (1.6 * math.sin(phase + index * .61)
         + .35 * math.sin(2.0 * phase + index * .37))
    y = (10.5 * math.sin(phase + index * .83)
         + 1.8 * math.sin(2.0 * phase + index * .42))
    return x, y


def render_frame(section_id, cfg, bg, nodes, phase, *, freeze=False):
    result = bg.copy()
    draw = ImageDraw.Draw(result)

    draw.text((43, 27), "YT-TECHDEV   /   SKILL CONSTELLATION",
              fill=(177, 220, 242), font=font(20, True))
    draw.text((43, 59), cfg["title"], fill=(118, 190, 222), font=font(25, True))
    draw.text((43, 95), cfg["subtitle"], fill=(87, 138, 169), font=font(13))

    # Directional constellation lanes. Only the Languages layout is modified.
    columns = cfg.get("columns", COLUMNS)
    for row in range(len(cfg["rows"])):
        for col in range(len(columns) - 1):
            draw.line((columns[col] + 91, cfg["rows"][row] - 4,
                       columns[col + 1] - 91, cfg["rows"][row] - 4),
                      fill=(26, 60, 83), width=1)
    for row in range(len(cfg["rows"]) - 1):
        for col in range(len(columns)):
            x = columns[col] + (22 if col % 2 == 0 else -22)
            draw.line((x, cfg["rows"][row] + 74, x,
                       cfg["rows"][row + 1] - 68), fill=(23, 56, 80), width=1)
    if section_id == "languages":
        draw.text((43, 136), "WEB / FRONTEND  →  SCRIPTING",
                  fill=(93, 153, 184), font=font(17, True))
        draw.text((43, 434), "BACKEND  →  RUNTIME  →  SYSTEMS",
                  fill=(93, 153, 184), font=font(17, True))

    for i, (key, label, category, color, tag, x0, y0, points) in enumerate(nodes):
        if freeze:
            dx, dy = 0.0, 0.0
        elif section_id == "languages":
            # Seamless 5.4s zero-gravity loop: independent phase offsets per
            # icon, a slow vertical float and only subtle horizontal drift.
            # Integer harmonics ensure f(0) == f(2*pi) at the GIF loop seam.
            dx, dy = floating_offset(i, phase)
        else:
            # Other sections are deliberately unchanged until their review.
            dx = math.sin(phase + i * .63) * 2.4
            dy = math.cos(phase + i * .78) * 2.8
        x, y = x0 + dx, y0 + dy
        brightness = ACTIVITY_BRIGHTNESS[category]
        rgb = tuple(int(color[j:j + 2], 16) for j in (1, 3, 5))
        # Bright, dense outlines: categories conveyed by labels, not dimness.
        for n, (px, py) in enumerate(points):
            if freeze:
                pulse = 1.0
            elif section_id == "languages":
                # Gentle breathing, with exactly periodic endpoints.
                pulse = .96 + .04 * math.sin(phase + n * .13 + i * .7)
            else:
                pulse = .92 + .08 * math.sin(phase * 1.6 + n * .19 + i)
            point_color = tuple(min(255, round(c * brightness * pulse)) for c in rgb)
            px0, py0 = round(x + px), round(y + py)
            draw.point((px0, py0), fill=point_color)
            if n % 8 == 0:
                draw.ellipse((px0 - 1, py0 - 1, px0 + 1, py0 + 1), fill=point_color)
        draw.text((x0, y0 + 82), label, anchor="mm", font=font(28 if section_id == "languages" else 30, True),
                  fill=(207, 228, 245))
        if tag:
            draw.text((x0, y0 + 116), tag, anchor="mm", font=font(16, True),
                      fill=(147, 195, 219))

    width = cfg.get("width", WIDTH)
    base = cfg["height"] - 34
    draw.line((43, base - 5, width - 42, base - 5), fill=(29, 67, 93), width=1)
    draw.text((43, base + 3), "SKILL STATUS IS DESCRIPTIVE, NOT A PROFICIENCY SCORE",
              fill=(111, 156, 182), font=font(13))
    draw.text((width - 43, base + 3), "YT-TECHDEV  /  " + section_id.upper(),
              anchor="ra", fill=(114, 165, 193), font=font(13))
    return result


def render_section(section_id, original, extra, frames):
    cfg = SECTIONS[section_id]
    height = cfg["height"]
    width = cfg.get("width", WIDTH)
    bg = make_background(height, SEED + len(section_id) * 19, width)
    nodes = prepared_nodes(section_id, cfg, original, extra["paths"])
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    path = assets / f"constellation-{section_id}"
    png = path.with_suffix(".png")
    gif = path.with_suffix(".gif")
    render_frame(section_id, cfg, bg, nodes, 0, freeze=True).save(png, optimize=True)
    animation = [
        render_frame(section_id, cfg, bg, nodes, math.tau * n / frames)
        for n in range(frames)
    ]
    animation[0].save(
        gif, format="GIF", save_all=True, append_images=animation[1:],
        duration=150 if section_id == "languages" else 105,
        loop=0, disposal=2, optimize=True,
    )
    with Image.open(png) as p, Image.open(gif) as g:
        assert p.size == g.size == (width, height), "Bad image geometry"
        assert g.n_frames == frames, "Bad GIF frame count"
    print(f"{section_id}: {len(nodes)} nodes; GIF {gif.stat().st_size:,} bytes; PNG {png.stat().st_size:,} bytes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=None)
    parser.add_argument("--only", choices=list(SECTIONS))
    args = parser.parse_args()
    if args.frames is not None and not 2 <= args.frames <= 80:
        parser.error("--frames must be between 2 and 80")
    original = json.loads((ROOT / "data/icon-paths.json").read_text("utf-8"))
    extras = json.loads((ROOT / "data/supplemental-icons.json").read_text("utf-8"))
    if original["source_commit"] != "6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27":
        raise ValueError("Portfolio path revision changed; review required")
    if extras["revision"] != "90646e4bf7f3b89df6c37e65baf3e7bc759a517c":
        raise ValueError("Supplemental paths changed; review required")
    # Devicon's pinned, normalized 128×128 HTML5/CSS3 shields.
    if extras.get("devicon_revision") != "6a37858047b0e8d9c9c0e68f4a071fc410652e89":
        raise ValueError("Unexpected Devicon source revision")
    extras["paths"].update(extras["devicon_paths"])
    total = sum(len(s["icons"]) for s in SECTIONS.values())
    keys = [row[0] for section in SECTIONS.values() for row in section["icons"]]
    if total != 25 or len(set(keys)) != total:
        raise ValueError("Unexpected icon count or duplicate key")
    for section_id in ([args.only] if args.only else SECTIONS):
        frame_count = args.frames if args.frames is not None else (36 if section_id == "languages" else 18)
        render_section(section_id, original, extras, frame_count)


if __name__ == "__main__":
    main()
