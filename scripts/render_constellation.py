#!/usr/bin/env python3
"""Render a GitHub README-safe particle constellation from pinned icon data."""
from __future__ import annotations

import argparse
import io
import json
import math
import random
import re
from pathlib import Path

import cairosvg
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
W, H = 1200, 960
SEED = 847291
X = (151, 450, 750, 1049)
Y = (141, 311, 480, 649, 815)
# Editorial activity categories, not proficiency ratings or GitHub API data.
SPECS = [
    ("react", "React", "building", "#7beafe"),
    ("typescript", "TypeScript", "building", "#73adff"),
    ("nextjs", "Next.js", "used", "#e6ebfb"),
    ("r3f", "R3F", "building", "#c9adfc"),
    ("javascript", "JavaScript", "used", "#f2d969"),
    ("nodejs", "Node.js", "used", "#91e5a4"),
    ("python", "Python", "used", "#a9cde7"),
    ("postgresql", "PostgreSQL", "used", "#9bbae4"),
    ("docker", "Docker", "used", "#71c7ff"),
    ("cloudflare", "Cloudflare", "used", "#ffbf77"),
    ("git", "Git", "used", "#fa9c81"),
    ("threedotjs", "Three.js", "used", "#bce6fa"),
    ("cplusplus", "C++", "exploring", "#9aa8ff"),
    ("rust", "Rust", "exploring", "#e5a57f"),
    ("linux", "Linux", "used", "#d9c5ae"),
    ("webassembly", "WebAssembly", "used", "#a5a8f8"),
    ("vscode", "VS Code", "used", "#7ba8ef"),
    ("blender", "Blender", "used", "#f8ad75"),
    ("chatgpt", "ChatGPT", "tool", "#a4e4c7"),
    ("claude", "Claude", "tool", "#f0ad8d"),
]
EDGES = tuple((i, i + 1) for i in range(20) if i % 4 != 3) + tuple(
    (i, i + 4) for i in range(16) if i % 4 in (0, 2)
)


def font(size: int, bold: bool = False):
    choices = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    )
    for path in choices:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def glyph_svg(key: str, originals: dict, extras: dict) -> str:
    base = '<svg xmlns="http://www.w3.org/2000/svg"'
    if key == "react":
        rings = "".join(
            f'<ellipse rx="1.55" ry=".48" transform="rotate({a})" '
            'stroke="white" stroke-width=".095" fill="none"/>'
            for a in (0, 60, 120)
        )
        return base + ' viewBox="-1.8 -1.8 3.6 3.6">' + rings + '<circle r=".18" fill="white"/></svg>'
    if key == "nextjs":
        return (base + ' viewBox="-2 -2 4 4">'
                '<circle r="1.48" stroke="white" stroke-width=".11" fill="none"/>'
                '<path d="M-.72 1V-1L.72 1V-1" stroke="white" stroke-width=".13" fill="none"/></svg>')
    if key == "r3f":
        return (base + ' viewBox="0 0 240 160">'
                '<text x="120" y="119" text-anchor="middle" font-family="sans-serif" '
                'font-size="108" font-weight="bold" fill="white">R3F</text></svg>')
    if key == "moonbit":
        # Illustrative lunar / MB mark; this is not the official MoonBit logo.
        return (base + ' viewBox="0 0 240 160">'
                '<path d="M94 15 A65 65 0 1 0 145 133 A55 55 0 0 1 94 15Z" '
                'fill="white"/>'
                '<text x="159" y="110" text-anchor="middle" font-family="sans-serif" '
                'font-size="82" font-weight="bold" fill="white">M</text></svg>')
    if key == "webassembly":
        # Compact symbolic WASM hexagon. The upstream glyph had separated
        # elements too small to recognize after GitHub mobile downscaling.
        return (base + ' viewBox="0 0 240 160">'
                '<path d="M120 8 222 52 222 109 120 153 18 109 18 52Z" '
                'stroke="white" stroke-width="6" fill="none"/>'
                '<text x="120" y="99" text-anchor="middle" font-family="sans-serif" '
                'font-size="61" font-weight="bold" fill="white">WASM</text></svg>')
    if key == "vscode":
        # Illustrative symbol, not an official VS Code trademark.
        return (base + ' viewBox="0 0 120 120">'
                '<path d="M37 29 15 59 37 88M84 29l22 30-22 29M73 13 48 105" '
                'stroke="white" stroke-width="9" stroke-linecap="round" '
                'stroke-linejoin="round" fill="none"/></svg>')
    if key == "chatgpt":
        # Abstract particle knot, not an official OpenAI/ChatGPT logo.
        rings = "".join(
            f'<ellipse cx="60" cy="60" rx="39" ry="16" transform="rotate({a} 60 60)" '
            'stroke="white" stroke-width="6" fill="none"/>'
            for a in (0, 60, 120)
        )
        return (base + ' viewBox="0 0 120 120">' + rings
                + '<circle cx="60" cy="60" r="7" fill="white"/></svg>')
    if key == "typescript":
        # Readable TS monogram with gently rounded rectangular corners.
        # The supplemental official SVG outline is retained in the data.
        return (base + ' viewBox="0 0 180 150">'
                '<rect x="17" y="10" width="146" height="129" rx="16" '
                'stroke="white" stroke-width="6" fill="none"/>'
                '<text x="90" y="105" text-anchor="middle" '
                'font-family="sans-serif" font-size="79" font-weight="bold" '
                'fill="white">TS</text></svg>')
    if key in ("html", "css"):
        # Devicon's full shields preserve the 5/3 inner shapes.
        if key not in extras:
            raise ValueError(f"Missing Devicon shield: {key}")
        outline = f'<path fill="white" d="{extras[key]}"/>'
        if key == "css":
            # Explicit top seam: the shield's thin upper horizontal edge
            # disappeared during contour rasterization on mobile previews.
            # This follows the Devicon CSS3 shield's x=8.76..119.24 top edge.
            outline += ('<path d="M9 2 H119" fill="none" stroke="white" '
                        'stroke-width="3.5" stroke-linecap="round"/>')
        return base + ' viewBox="0 0 128 128">' + outline + '</svg>'
    if key == "vbscript":
        # Portfolio VBS artwork resembles a Visual Studio mark, so use a
        # neutral labeled wordmark instead of misattributing that trademark.
        return (base + ' viewBox="0 0 220 150">'
                '<rect x="12" y="16" width="196" height="112" rx="20" '
                'fill="none" stroke="white" stroke-width="6"/>'
                '<text x="110" y="99" text-anchor="middle" font-family="sans-serif" '
                'font-size="76" font-weight="bold" fill="white">VBS</text></svg>')
    if key == "java":
        paths = originals["paths"].get("java")
        if not paths:
            raise ValueError("Missing portfolio Java outline")
        shapes = "".join(f'<path fill="white" d="{p}"/>' for p in paths)
        return base + ' viewBox="0 0 265 360">' + shapes + "</svg>"
    if key == "rust":
        return base + ' viewBox="0 0 24 24"><path fill="white" d="' + originals["rust_path"] + '"/></svg>'
    if key in extras:
        # Fixed viewBox: the old numeric heuristic was clipping some logos.
        return base + ' viewBox="0 0 24 24"><path fill="white" d="' + extras[key] + '"/></svg>'

    if key not in {"javascript", "nodejs", "python", "cloudflare"}:
        raise ValueError(f"Unexpected icon source {key}")
    paths = originals["paths"].get(key)
    if not paths:
        raise ValueError(f"Missing portfolio path: {key}")
    numbers = [abs(float(n)) for p in paths for n in re.findall(
        r"(?<![A-Za-z])[-+]?(?:\d*\.\d+|\d+)(?:[Ee][-+]?\d+)?", p
    )]
    size = max(max(numbers, default=24) * 1.8, 28)
    offset = -size * .14
    shapes = "".join(f'<path fill="white" d="{p}"/>' for p in paths)
    return base + f' viewBox="{offset:.2f} {offset:.2f} {size:.2f} {size:.2f}">' + shapes + '</svg>'


def sample_outline(key, originals, extras, count, rng):
    svg = glyph_svg(key, originals, extras)
    binary = cairosvg.svg2png(bytestring=svg.encode(), output_width=560, output_height=560)
    alpha = Image.open(io.BytesIO(binary)).convert("RGBA").getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError(f"Empty icon: {key}")
    alpha = alpha.crop(bounds)
    alpha.thumbnail((150, 121), Image.Resampling.LANCZOS)
    if key == "typescript":
        # Antialias the pixelized TS corners while retaining the recognizable source path.
        alpha = alpha.filter(ImageFilter.GaussianBlur(0.85))
    # A transparent border is essential before applying MinFilter. Without
    # it, the sampler cannot detect edges lying exactly on the cropped top
    # boundary (the missing top horizontal stroke of the CSS3 shield).
    alpha = ImageOps.expand(alpha, border=6, fill=0)
    edge = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(5)))
    w, h = alpha.size
    p = edge.load()
    choices = [(x - w / 2, y - h / 2) for y in range(h) for x in range(w) if p[x, y] > 30]
    if len(choices) < 10:
        p = alpha.load()
        choices = [(x - w / 2, y - h / 2) for y in range(h) for x in range(w) if p[x, y] > 50]
    if len(choices) < 10:
        raise ValueError(f"Too few outline points: {key}")
    if key in ("typescript", "docker", "postgresql", "git"):
        width = max(x for x, _ in choices) - min(x for x, _ in choices)
        height = max(y for _, y in choices) - min(y for _, y in choices)
        if min(width, height) < 44:
            raise ValueError(f"Previously malformed icon still cropped: {key} {width}x{height}")
    if key == "css":
        top_y = min(y for _, y in choices)
        seam = sorted((point for point in choices if point[1] <= top_y + 2),
                      key=lambda point: point[0])
        seam_width = max((x for x, _ in seam), default=0) - min(
            (x for x, _ in seam), default=0
        )
        if len(seam) < 30 or seam_width < 65:
            raise ValueError("CSS top shield edge missing from contour sample")
        # Reserve evenly spread particles across the horizontal top stroke;
        # relying on random sampling alone left visible gaps on phones.
        reserved = min(125, count // 8)
        fixed_seam = [seam[i * (len(seam) - 1) // (reserved - 1)]
                      for i in range(reserved)]
        rng.shuffle(choices)
        return fixed_seam + [choices[i % len(choices)]
                             for i in range(count - reserved)]
    rng.shuffle(choices)
    return [choices[i % len(choices)] for i in range(count)]


def background(rng):
    bg = Image.new("RGB", (W, H), (3, 9, 22))
    haze = Image.new("RGBA", (W, H))
    hd = ImageDraw.Draw(haze, "RGBA")
    hd.ellipse((95, -350, 1030, 850), fill=(35, 53, 112, 54))
    hd.ellipse((550, -100, 1460, 780), fill=(10, 138, 175, 22))
    hd.ellipse((-290, 240, 530, 1110), fill=(83, 50, 137, 27))
    haze = haze.filter(ImageFilter.GaussianBlur(90))
    bg.paste(haze, (0, 0), haze)
    d = ImageDraw.Draw(bg)
    for _ in range(350):
        x, y = rng.randrange(W), rng.randrange(H)
        v = rng.choice((29, 36, 45, 55, 66, 82, 106))
        d.point((x, y), fill=(v, v + 7, v + 28))
    return bg


def render(bg, icons, phase, frozen=False):
    img = bg.copy()
    d = ImageDraw.Draw(img)
    for a, b in EDGES:
        d.line((icons[a][4], icons[a][5], icons[b][4], icons[b][5]), fill=(21, 49, 72))
    d.text((39, 24), "YT-TECHDEV   /   SKILL CONSTELLATION",
           fill=(163, 204, 232), font=font(18, True))
    d.text((39, 52), "TECHNOLOGIES, SYSTEMS & CREATIVE TOOLS",
           fill=(83, 141, 174), font=font(13))
    for i, (key, label, activity, color, ox, oy, points) in enumerate(icons):
        intensity = {"building": .98, "used": .83, "exploring": .59, "tool": .84}[activity]
        x = ox if frozen else ox + math.sin(phase + i * .85) * 2.7
        y = oy if frozen else oy + math.cos(phase + i * .53) * 2.9
        rgb = tuple(int(color[t:t + 2], 16) for t in (1, 3, 5))
        for j, (px, py) in enumerate(points):
            pulse = 1 if frozen else (.86 + .14 * math.sin(phase * 1.5 + j * .16 + i))
            pixel = tuple(round(c * intensity * pulse) for c in rgb)
            sx, sy = round(x + px), round(y + py)
            d.point((sx, sy), fill=pixel)
            if j % 13 == 0:
                d.ellipse((sx - 1, sy - 1, sx + 1, sy + 1), fill=pixel)
        label_color = (197, 212, 229) if activity != "exploring" else (151, 163, 184)
        d.text((ox, oy + 70), label, anchor="mm", font=font(20, True), fill=label_color)
        if activity in ("exploring", "tool"):
            d.text((ox, oy + 93), "EXPLORING" if activity == "exploring" else "AI TOOL",
                   anchor="mm", font=font(11, True), fill=(113, 141, 162))
    d.line((40, 932, 1160, 932), fill=(24, 53, 72))
    d.text((40, 944), "BRIGHTNESS = PROJECT ACTIVITY, NOT PROFICIENCY",
           fill=(103, 147, 172), font=font(11))
    d.text((1158, 944), "BUILDING / USED / EXPLORING / AI TOOL",
           fill=(100, 138, 161), font=font(11), anchor="ra")
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=ROOT / "data/icon-paths.json")
    ap.add_argument("--out", type=Path, default=ROOT / "assets/constellation.gif")
    ap.add_argument("--frames", type=int, default=24)
    ap.add_argument("--static", action="store_true")
    args = ap.parse_args()
    if not 1 <= args.frames <= 120:
        ap.error("Frame count must be 1..120")
    original = json.loads(args.data.read_text("utf-8"))
    extras = json.loads((ROOT / "data/supplemental-icons.json").read_text("utf-8"))
    if original.get("source_commit") != "6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27":
        raise ValueError("Unexpected portfolio source revision")
    if extras.get("revision") != "90646e4bf7f3b89df6c37e65baf3e7bc759a517c":
        raise ValueError("Unexpected supplemental source revision")
    rng = random.Random(SEED)
    icons = []
    for i, (key, label, activity, color) in enumerate(SPECS):
        count = 680 if activity == "building" else 560
        if activity == "exploring":
            count = 480
        pts = sample_outline(key, original, extras["paths"], count, rng)
        icons.append((key, label, activity, color, X[i % 4], Y[i // 4], pts))
    if len(icons) != 20:
        raise AssertionError("Expected 20 technology and tool icons")
    bg = background(rng)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.static:
        render(bg, icons, 0, frozen=True).save(args.out, optimize=True)
    else:
        frames = [render(bg, icons, math.tau * i / args.frames) for i in range(args.frames)]
        frames[0].save(args.out, format="GIF", save_all=True,
                       append_images=frames[1:], duration=110, loop=0, disposal=2, optimize=True)
    print(f"Rendered {args.out}: {args.out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
