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

from PIL import Image, ImageDraw, ImageFilter
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
        "title": "01  /  LANGUAGES",
        "subtitle": "LANGUAGES USED & EXPLORED",
        "height": 560,
        "rows": (177, 385),
        "icons": [
            ("typescript", "TypeScript", "building", "#74b8ff", None),
            ("javascript", "JavaScript", "used", "#f3dc79", None),
            ("python", "Python", "used", "#a7d8fa", None),
            ("moonbit", "MoonBit", "used", "#a1c6ff", "WIF RUNTIME"),
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


def make_background(height: int, seed: int) -> Image.Image:
    rng = random.Random(seed)
    bg = Image.new("RGB", (WIDTH, height), "#040d1d")
    nebula = Image.new("RGBA", (WIDTH, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(nebula, "RGBA")
    d.ellipse((120, -290, 1100, height + 390), fill=(23, 67, 128, 67))
    d.ellipse((580, -160, 1510, height + 120), fill=(10, 108, 166, 32))
    d.ellipse((-250, 190, 460, height + 240), fill=(87, 51, 145, 30))
    nebula = nebula.filter(ImageFilter.GaussianBlur(110))
    bg.paste(nebula, (0, 0), nebula)
    draw = ImageDraw.Draw(bg)
    for _ in range(int(height * .34)):
        x, y = rng.randrange(WIDTH), rng.randrange(height)
        s = rng.choice((33, 42, 55, 71, 96, 135, 170))
        draw.point((x, y), fill=(s // 2, s * 3 // 4, min(255, s)))
    return bg


def prepared_nodes(section_id, cfg, originals, extras):
    rng = random.Random(SEED + len(section_id) * 23)
    nodes = []
    for i, (key, label, category, color, tag) in enumerate(cfg["icons"]):
        # More points for every icon than the original low-visibility last rows.
        samples = sample_outline(key, originals, extras, 1000, rng)
        nodes.append((key, label, category, color, tag, COLUMNS[i % 3],
                      cfg["rows"][i // 3], samples))
    return nodes


def render_frame(section_id, cfg, bg, nodes, phase, *, freeze=False):
    result = bg.copy()
    draw = ImageDraw.Draw(result)

    draw.text((43, 27), "YT-TECHDEV   /   SKILL CONSTELLATION",
              fill=(177, 220, 242), font=font(20, True))
    draw.text((43, 59), cfg["title"], fill=(118, 190, 222), font=font(25, True))
    draw.text((43, 95), cfg["subtitle"], fill=(87, 138, 169), font=font(13))

    # Constellation connections: always behind and outside readable labels.
    for row in range(len(cfg["rows"])):
        for col in range(2):
            draw.line((COLUMNS[col] + 91, cfg["rows"][row] - 4,
                       COLUMNS[col + 1] - 91, cfg["rows"][row] - 4),
                      fill=(26, 60, 83), width=1)
    for row in range(len(cfg["rows"]) - 1):
        for col in range(3):
            x = COLUMNS[col] + (22 if col % 2 == 0 else -22)
            draw.line((x, cfg["rows"][row] + 74, x,
                       cfg["rows"][row + 1] - 68), fill=(23, 56, 80), width=1)

    for i, (key, label, category, color, tag, x0, y0, points) in enumerate(nodes):
        dx = 0 if freeze else math.sin(phase + i * .63) * 2.4
        dy = 0 if freeze else math.cos(phase + i * .78) * 2.8
        x, y = x0 + dx, y0 + dy
        brightness = ACTIVITY_BRIGHTNESS[category]
        rgb = tuple(int(color[j:j + 2], 16) for j in (1, 3, 5))
        # Bright, dense outlines: categories conveyed by labels, not dimness.
        for n, (px, py) in enumerate(points):
            pulse = 1 if freeze else .92 + .08 * math.sin(phase * 1.6 + n * .19 + i)
            point_color = tuple(min(255, round(c * brightness * pulse)) for c in rgb)
            px0, py0 = round(x + px), round(y + py)
            draw.point((px0, py0), fill=point_color)
            if n % 8 == 0:
                draw.ellipse((px0 - 1, py0 - 1, px0 + 1, py0 + 1), fill=point_color)
        draw.text((x0, y0 + 82), label, anchor="mm", font=font(30, True),
                  fill=(207, 228, 245))
        if tag:
            draw.text((x0, y0 + 116), tag, anchor="mm", font=font(16, True),
                      fill=(147, 195, 219))

    base = cfg["height"] - 34
    draw.line((43, base - 5, 1158, base - 5), fill=(29, 67, 93), width=1)
    draw.text((43, base + 3), "SKILL STATUS IS DESCRIPTIVE, NOT A PROFICIENCY SCORE",
              fill=(111, 156, 182), font=font(13))
    draw.text((1158, base + 3), "YT-TECHDEV  /  " + section_id.upper(),
              anchor="ra", fill=(114, 165, 193), font=font(13))
    return result


def render_section(section_id, original, extra, frames):
    cfg = SECTIONS[section_id]
    height = cfg["height"]
    bg = make_background(height, SEED + len(section_id) * 19)
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
        duration=105, loop=0, disposal=2, optimize=True,
    )
    with Image.open(png) as p, Image.open(gif) as g:
        assert p.size == g.size == (WIDTH, height), "Bad image geometry"
        assert g.n_frames == frames, "Bad GIF frame count"
    print(f"{section_id}: {len(nodes)} nodes; GIF {gif.stat().st_size:,} bytes; PNG {png.stat().st_size:,} bytes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=18)
    parser.add_argument("--only", choices=list(SECTIONS))
    args = parser.parse_args()
    if not 2 <= args.frames <= 80:
        parser.error("--frames must be between 2 and 80")
    original = json.loads((ROOT / "data/icon-paths.json").read_text("utf-8"))
    extras = json.loads((ROOT / "data/supplemental-icons.json").read_text("utf-8"))
    if original["source_commit"] != "6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27":
        raise ValueError("Portfolio path revision changed; review required")
    if extras["revision"] != "90646e4bf7f3b89df6c37e65baf3e7bc759a517c":
        raise ValueError("Supplemental paths changed; review required")
    total = sum(len(s["icons"]) for s in SECTIONS.values())
    keys = [row[0] for section in SECTIONS.values() for row in section["icons"]]
    if total != 21 or len(set(keys)) != total:
        raise ValueError("Unexpected icon count or duplicate key")
    for section_id in ([args.only] if args.only else SECTIONS):
        render_section(section_id, original, extras, args.frames)


if __name__ == "__main__":
    main()
