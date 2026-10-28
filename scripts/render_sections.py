#!/usr/bin/env python3
"""Render independent README GIF/PNG particle constellations by technology group.

This uses frozen data from the user's portfolio plus a pinned supplemental icon
snapshot. All renders are offline, deterministic and README-compatible.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import random
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
from render_constellation import font, glyph_svg, sample_outline

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
        # Keep existing sampling order/phase. Shift only first-row anchors
        # to six columns; the second row remains at its approved positions.
        # Shell / BAT is appended to preserve the other ten icon RNG samples.
        "positions": (
            (145, 231), (405, 231), (665, 231), (925, 231), (1185, 231),
            (164, 531), (482, 531), (800, 531), (1118, 531), (1436, 531),
            (1445, 231),
        ),
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
            ("shellbat", "Shell / BAT", "used", "#8bcdf9", None),
        ],
    },
    "frameworks": {
        "title": "02  /  FRAMEWORKS & RUNTIMES",
        "subtitle": "FROM UI LIBRARIES TO APPLICATION SYSTEMS",
        "height": 1110,
        "rows": (191, 431, 671, 911),
        "positions": ((215,191),(600,191),(985,191),
                      (215,431),(600,431),(985,431),
                      (215,671),(600,671),(985,671),
                      (215,911),(600,911),(985,911)),
        "icons": [
            ("react", "React", "building", "#79f1ff", None),
            ("nextjs", "Next.js", "used", "#f1f3fd", None),
            ("nodejs", "Node.js", "used", "#a9efb8", None),
            ("r3f", "R3F", "building", "#dcc2ff", None),
            ("threedotjs", "Three.js", "used", "#c6e9f9", None),
            ("vue", "Vue.js", "used", "#42b883", None),
            ("googleappsscript", "Google Apps Script", "used", "#4285f4", None),
            ("tailwindcss", "TailwindCSS", "used", "#80e5ef", None),
            ("bootstrap", "Bootstrap", "used", "#c9a4ff", None),
            ("framermotion", "Framer Motion", "used", "#fef62a", None),
            ("jquery", "jQuery", "used", "#7acef4", None),
            ("prisma", "Prisma", "used", "#edf3ff", None),
        ],
    },
    "tools": {
        "title": "03  /  TOOLS & PLATFORMS",
        "subtitle": "INSTRUMENTS, INFRASTRUCTURE & AI ASSISTANTS",
        "height": 900,
        "columns": (215, 600, 985),
        "rows": (222, 444, 666),
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


def make_language_background(height: int, seed: int, width: int) -> Image.Image:
    """Static origin field: warped nebula, clustered dust and three star depths.

    Build the haze at quarter resolution once; a separate local RNG leaves all
    icon samples and motion untouched. No downloaded textures or extra packages.
    """
    rng = random.Random(seed)
    size = (width // 4, height // 4)

    def noise(columns, rows):
        field = Image.new("L", (columns, rows))
        field.putdata([rng.randrange(256) for _ in range(columns * rows)])
        return field.resize(size, Image.Resampling.BICUBIC)

    broad = noise(7, 4)
    cloud = Image.blend(noise(15, 8), noise(33, 17), .32)
    cloud = Image.blend(cloud, noise(68, 35), .14)
    broad_px, cloud_px = broad.load(), cloud.load()
    haze, density = Image.new("RGB", size), Image.new("L", size)
    pixels, dust_density = haze.load(), density.load()
    cfg = SECTIONS["languages"]
    for y in range(size[1]):
        v = y / (size[1] - 1)
        for x in range(size[0]):
            u = x / (size[0] - 1)
            large, detail = broad_px[x, y] / 255, cloud_px[x, y] / 255
            # A bent, broken cloud bank, with dark pockets rather than circles.
            spine = .72 - .40 * u + .10 * math.sin(u * math.tau - .6)
            spine += .16 * (large - .5)
            bank = math.exp(-((v - spine) / (.10 + .10 * large)) ** 2)
            veil = math.exp(-((v - spine - .13) / .30) ** 2)
            structure = max(0, detail - .18) ** 1.6
            cloud_light = (bank * .80 + veil * .22) * structure
            # A dim blue wisp in the upper right balances the violet dust bank.
            cloud_light += .14 * math.exp(-((u - .87) / .32) ** 2
                                          - ((v - .15) / .29) ** 2) * large
            # Soft protection follows existing UI coordinates, never their pixels.
            quiet = max(
                math.exp(-((u * width - cx) / 115) ** 4
                         - ((v * height - cy) / 110) ** 4)
                for cx, cy in cfg["positions"]
            )
            cloud_light *= 1 - .35 * quiet
            edge = max(.58, 1 - .28 * ((u - .5) ** 2 + (v - .5) ** 2))
            violet = (1 - u) * .72 + .16 * large
            tint = (24 + 29 * violet, 72 - 33 * violet, 122 - 16 * violet)
            pixels[x, y] = tuple(round(base + c * cloud_light * edge)
                                  for base, c in zip((4, 10, 26), tint))
            dust_density[x, y] = round(min(255, bank * structure * 450))
    bg = haze.resize((width, height), Image.Resampling.BICUBIC)
    draw = ImageDraw.Draw(bg, "RGBA")

    def quiet_area(x, y):
        if y < 158 or y > height - 60:
            return True
        return any(abs(x - cx) < 113 and (abs(y - cy) < 105
                   or abs(y - cy - 120) < 32)
                   for cx, cy in cfg["positions"])

    # Dust follows the cloud density, not a uniform sheet of white noise.
    for _ in range(4200):
        x, y = rng.randrange(width), rng.randrange(height)
        if rng.randrange(256) >= dust_density[x // 4, y // 4]:
            continue
        alpha = rng.randrange(5, 22) // (2 if quiet_area(x, y) else 1)
        draw.point((x, y), fill=(95, 138, 179, alpha))

    # Far field: many faint pinpoints; mid field: fewer, uneven small stars.
    for layer, count in (("far", 680), ("mid", 125)):
        for _ in range(count):
            x, y = rng.randrange(width), rng.randrange(height)
            if layer == "mid" and (quiet_area(x, y) or rng.random() < .25
                                   * (1 - dust_density[x // 4, y // 4] / 255)):
                continue
            value = rng.randrange(24, 69) if layer == "far" else rng.randrange(75, 136)
            if quiet_area(x, y):
                value = round(value * .65)
            color = (round(value * .66), round(value * .84), value, 255)
            if layer == "mid" and rng.random() < .22:
                draw.ellipse((x - .6, y - .6, x + .6, y + .6), fill=color)
            else:
                draw.point((x, y), fill=color)

    # Near field: sparse soft glows, placed away from icons, names and headings.
    glow = Image.new("RGBA", bg.size)
    glow_draw = ImageDraw.Draw(glow)
    stars = []
    while len(stars) < 9:
        x, y = rng.randrange(25, width - 25), rng.randrange(165, height - 65)
        if quiet_area(x, y):
            continue
        stars.append((x, y))
        glow_draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(88, 166, 201, 64))
    glow = glow.filter(ImageFilter.GaussianBlur(3))
    bg.paste(glow, (0, 0), glow)
    draw = ImageDraw.Draw(bg)
    for x, y in stars:
        draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(108, 159, 184))
        draw.point((x, y), fill=(167, 200, 216))
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


def sample_language_wordmark(key, originals, extras, count):
    """Keep the existing TS/VBS letters, without their enclosing rectangle."""
    svg = ET.fromstring(glyph_svg(key, originals, extras))
    frames = svg.findall("{http://www.w3.org/2000/svg}rect")
    if len(frames) != 1:
        raise ValueError(f"Expected one enclosing frame for {key}")
    svg.remove(frames[0])
    binary = cairosvg.svg2png(bytestring=ET.tostring(svg),
                             output_width=560, output_height=560)
    alpha = Image.open(io.BytesIO(binary)).convert("RGBA").getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError(f"Empty wordmark: {key}")
    alpha = alpha.crop(bounds)
    alpha.thumbnail((150, 121), Image.Resampling.LANCZOS)
    if key == "typescript":
        alpha = alpha.filter(ImageFilter.GaussianBlur(.85))
    alpha = ImageOps.expand(alpha, border=6, fill=0)
    edge = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(5)))
    w, h = alpha.size
    pixels = edge.load()
    choices = [(x - w / 2, y - h / 2) for y in range(h) for x in range(w)
               if pixels[x, y] > 30]
    if len(choices) < 100:
        raise ValueError(f"Incomplete wordmark: {key}")
    # Isolated sampling leaves all subsequent icons' particle RNG untouched.
    random.Random(SEED + sum(map(ord, key))).shuffle(choices)
    return [choices[i % len(choices)] for i in range(count)]


def prepared_nodes(section_id, cfg, originals, extras, *, wordmarks=True):
    rng = random.Random(SEED + len(section_id) * 23)
    nodes = []
    for i, (key, label, category, color, tag) in enumerate(cfg["icons"]):
        # More points for every icon than the original low-visibility last rows.
        count = 1450 if section_id == "languages" else 1000
        if key == "moonbit":
            samples = sample_official_moonbit(count, rng)
        else:
            # Consume the original sampling RNG even when replacing a wordmark;
            # later icons must retain their exact particle placement and pulse.
            samples = sample_outline(key, originals, extras, count, rng)
        if wordmarks and section_id == "languages" and key in ("typescript", "vbscript"):
            samples = sample_language_wordmark(key, originals, extras, count)
        if key == "typescript" and section_id == "languages":
            # The TS glyph previously appeared smaller; round its raster edges
            # in the source sampler and normalize optical scale with label clearance.
            samples = [(x * 1.04, y * 1.04) for x, y in samples]
        if section_id == "languages":
            x, y = cfg["positions"][i]
        else:
            columns = cfg.get("columns", COLUMNS)
            x, y = columns[i % len(columns)], cfg["rows"][i // len(columns)]
        nodes.append((key, label, category, color, tag, x, y, samples))
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

    # Languages float freely; retain the other sections' constellation lanes.
    if section_id != "languages":
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
        # One fixed label baseline clears even MoonBit's tall contour at the
        # bottom of its float; larger language names survive mobile scaling.
        label_y = y0 + (120 if section_id == "languages" else 82)
        draw.text((x0, label_y), label, anchor="mm", font=font(40 if section_id == "languages" else 30, True),
                  fill=(207, 228, 245))
        if tag and section_id != "languages":
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
    if section_id == "tools":
        from tools_observatory import StationGrid, render_assets
        render_assets(StationGrid(cfg), ROOT / "assets", frames)
        return
    if section_id == "frameworks":
        from framework_orbits import ORIGINAL_KEYS, QuietOrbits, prepared_contours, render_assets
        sources = {key: glyph_svg(key, original, extra["paths"])
                   for key in ORIGINAL_KEYS}
        nodes = prepared_contours(cfg, COLUMNS, sources)
        render_assets(QuietOrbits(cfg, nodes, font, ACTIVITY_BRIGHTNESS), ROOT / "assets", frames)
        return
    height = cfg["height"]
    width = cfg.get("width", WIDTH)
    background = make_language_background if section_id == "languages" else make_background
    bg = background(height, SEED + len(section_id) * 19, width)
    nodes = prepared_nodes(section_id, cfg, original, extra["paths"])
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    path = assets / f"constellation-{section_id}"
    png = path.with_suffix(".png")
    gif = path.with_suffix(".gif")
    poster = render_frame(section_id, cfg, bg, nodes, 0, freeze=True)
    poster.save(png, optimize=True)
    animation = [
        render_frame(section_id, cfg, bg, nodes, math.tau * n / frames)
        for n in range(frames)
    ]
    if section_id == "languages":
        # One palette keeps static nebula/dust pixels identical in every frame.
        # No error-diffusion noise, extra background motion or palette shimmer.
        # Retain the approved framed poster only as a color-table reference;
        # rebuilding a palette from the new letters would recolor other pixels.
        palette_nodes = prepared_nodes(section_id, cfg, original, extra["paths"],
                                       wordmarks=False)
        palette_poster = render_frame(section_id, cfg, bg, palette_nodes, 0, freeze=True)
        palette = palette_poster.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        animation = [frame.quantize(palette=palette, dither=Image.Dither.NONE)
                     for frame in animation]
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
    if total != 32 or len(set(keys)) != total:
        raise ValueError("Unexpected icon count or duplicate key")
    for section_id in ([args.only] if args.only else SECTIONS):
        defaults = {"languages": 36, "frameworks": 64, "tools": 48}
        frame_count = args.frames if args.frames is not None else defaults[section_id]
        render_section(section_id, original, extras, frame_count)


if __name__ == "__main__":
    main()
