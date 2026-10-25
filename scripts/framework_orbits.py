"""Quiet Orbits: isolated Frameworks composition, motion and GIF encoding.

No import of render_sections: the caller supplies identity/configuration, SVG
sources, font access and activity colors. Frozen, audited contour samples avoid
system FreeType changing the approved particle silhouettes on regeneration.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

SIZE = (1200, 1110)
FRAMES = 64
DURATION_MS = 100
LABEL_SIZE = 38
LABEL_OFFSET = 96
SEED = 847491
DRIFT = (1.2, 5.0)
DOT_RADIUS = 1
ORBITS = (
    (600, 558, 560, 430, -8, (98, 181, 225), .76),
    (606, 570, 600, 490, 9, (151, 136, 213), .60),
)
LIGHT_STARTS = (.14, 2.45)
LIGHT_ARCS = (.08, .10)
LIGHT_RADIUS = 8  # 5px glow plus the 3x -> 1x Lanczos filter's 3px support.
FIXTURE = Path(__file__).with_name("framework_contours.json")
CONTOUR_SHA256 = "03f39f7807a8a7ec3d496d167eaaeacdbdd81b74da63cfaf8f44e528cf418745"
ORIGINAL_KEYS = ("react", "nextjs", "nodejs", "r3f", "threedotjs", "webassembly")
EXPANSION_FIXTURE = Path(__file__).with_name("framework_expansion_contours.json")
EXPANSION_SHA256 = "b2e27c86ba99bb4c0946c4e1d7d3c522b00774d19faeaada8b25291969b99670"


def prepared_contours(cfg, columns, sources):
    """Reuse the original ordered 1,000 samples per mark; reject source drift."""
    content = FIXTURE.read_bytes()
    if hashlib.sha256(content).hexdigest() != CONTOUR_SHA256:
        raise ValueError("Approved Frameworks contour samples changed")
    frozen = json.loads(content)
    if frozen["version"] != 1:
        raise ValueError("Unknown Frameworks contour format")
    expected = frozen["glyph_sha256"]
    actual = {key: hashlib.sha256(value.encode()).hexdigest()
              for key, value in sources.items()}
    if actual != expected:
        raise ValueError("Frameworks SVG sources changed; contour review required")
    expansion = EXPANSION_FIXTURE.read_bytes()
    if hashlib.sha256(expansion).hexdigest() != EXPANSION_SHA256:
        raise ValueError("Expanded Frameworks contour samples changed")
    added = json.loads(expansion)
    if added["version"] != 1 or set(added["points"]) & set(frozen["points"]):
        raise ValueError("Invalid or overlapping expansion fixture")
    points = {**frozen["points"], **added["points"]}
    positions = cfg["positions"]
    if len(positions) != len(cfg["icons"]):
        raise ValueError("Missing Frameworks positions")
    return [(*spec, *positions[i],
             [tuple(point) for point in points[spec[0]]])
            for i, spec in enumerate(cfg["icons"])]


def orbit_point(orbit, t):
    cx, cy, rx, ry, degrees, _, _ = orbit
    angle = math.radians(degrees)
    x, y = rx * math.cos(t), ry * math.sin(t)
    return (cx + x * math.cos(angle) - y * math.sin(angle),
            cy + x * math.sin(angle) + y * math.cos(angle))


def floating_offset(index, phase):
    return (DRIFT[0] * math.sin(phase + index * .63),
            DRIFT[1] * math.cos(phase + index * .78))


def particle_pulse(index, sample, phase):
    return .96 + .04 * math.sin(phase + sample * .19 + index)


def light_angle(index, phase):
    return LIGHT_STARTS[index] + LIGHT_ARCS[index] * math.sin(phase + index * .7)


def logo_envelope(node, padding=0):
    """Continuous full drift, rounded pixel centers, and emphasized dot radius."""
    *_, x, y, points = node
    padx, pady = DRIFT[0] + DOT_RADIUS + .5 + padding, DRIFT[1] + DOT_RADIUS + .5 + padding
    return (math.floor(x + min(px for px, _ in points) - padx),
            math.floor(y + min(py for _, py in points) - pady),
            math.ceil(x + max(px for px, _ in points) + padx),
            math.ceil(y + max(py for _, py in points) + pady))


class QuietOrbits:
    def __init__(self, cfg, nodes, font, brightness):
        self.cfg, self.nodes = cfg, nodes
        self.font, self.brightness = font, brightness
        self.protected = Image.new("L", SIZE)
        draw = ImageDraw.Draw(self.protected)
        # All clipping/masking occurs AFTER orbital glow and AA, so zero is exact.
        self.protection_boxes = [("header", (0, 0, SIZE[0]-1, 113)),
                                 ("footer", (0, SIZE[1]-44, SIZE[0]-1, SIZE[1]-1))]
        for node in nodes:
            key, label, _, _, _, x, y, _ = node
            self.protection_boxes.append((key, logo_envelope(node, padding=3)))
            box = draw.textbbox((x, y + LABEL_OFFSET), label,
                                font=font(LABEL_SIZE, True), anchor="mm")
            self.protection_boxes.append((label, (box[0]-8, box[1]-6, box[2]+8, box[3]+6)))
        for _, box in self.protection_boxes:
            draw.rectangle(box, fill=255)
        # A fixed outer falloff prevents sharp rectangular ends without moving
        # the zero-alpha core as icons float. No frame-dependent mask exists.
        soft = self.protected.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
        exclusion = ImageChops.lighter(self.protected, soft)
        self.keep = ImageChops.invert(exclusion)
        self.background = self.make_background()
        self.structure = self.make_structure()
        self.base = Image.alpha_composite(self.background.convert("RGBA"), self.structure)

    def mask_orbits(self, layer):
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), self.keep))
        return layer

    def make_background(self):
        width, height = SIZE
        image = Image.new("RGB", SIZE)
        pixels = image.load()
        # Smooth depth only: deliberately distinct from Languages' cloud/dust.
        for y in range(height):
            v = y / height
            for x in range(width):
                u = x / width
                light = math.exp(-((u-.59)/.49)**2 - ((v-.53)/.72)**2)
                violet = math.exp(-((u-.09)/.43)**2 - ((v-.84)/.7)**2)
                pixels[x, y] = (int(4+3*light+3*violet), int(10+7*light),
                                int(24+14*light+5*violet))
        rng, draw = random.Random(SEED), ImageDraw.Draw(image)
        mask = self.keep.load()
        for count, lo, hi in ((290, 20, 57), (39, 68, 109)):
            for _ in range(count):
                x, y = rng.randrange(width), rng.randrange(height)
                value = rng.randrange(lo, hi)
                if y < 114 or y > height-45 or mask[x, y] < 36:
                    value = round(value * .38)
                draw.point((x, y), fill=(round(value*.55), round(value*.77), value))
        return image

    def make_structure(self):
        scale = 3
        layer = Image.new("RGBA", (SIZE[0]*scale, SIZE[1]*scale))
        draw = ImageDraw.Draw(layer)
        for j, orbit in enumerate(ORBITS):
            for n in range(960):
                t, t2 = math.tau*n/960, math.tau*(n+1)/960
                if (j == 0 and 2.15 < t < 3.55) or (j == 1 and 3.68 < t < 3.9):
                    continue
                x, y = orbit_point(orbit, t)
                x2, y2 = orbit_point(orbit, t2)
                near = .48 + .52*(.5 + .5*math.sin(t))
                alpha = round(145*orbit[6]*near)
                draw.line((x*scale, y*scale, x2*scale, y2*scale),
                          fill=(*orbit[5], alpha), width=4 if j == 0 else 3)
        layer = layer.resize(SIZE, Image.Resampling.LANCZOS)
        glow = layer.filter(ImageFilter.GaussianBlur(3))
        glow.putalpha(glow.getchannel("A").point(lambda v: round(v*.28)))
        return self.mask_orbits(Image.alpha_composite(glow, layer))

    def light_layer(self, phase):
        scale = 3
        layer = Image.new("RGBA", (SIZE[0]*scale, SIZE[1]*scale))
        draw = ImageDraw.Draw(layer)
        for j, orbit in enumerate(ORBITS):
            x, y = orbit_point(orbit, light_angle(j, phase))
            color = (147, 213, 237) if j == 0 else (187, 174, 231)
            for radius, alpha in ((5, 9), (3, 20), (1.2, 155), (.45, 235)):
                draw.ellipse(((x-radius)*scale, (y-radius)*scale,
                              (x+radius)*scale, (y+radius)*scale), fill=(*color, alpha))
        return self.mask_orbits(layer.resize(SIZE, Image.Resampling.LANCZOS))

    def foreground(self, image, phase, freeze=False):
        draw = ImageDraw.Draw(image)
        font, cfg = self.font, self.cfg
        draw.text((43, 27), "YT-TECHDEV   /   SKILL CONSTELLATION",
                  fill=(177, 220, 242), font=font(20, True))
        draw.text((43, 59), cfg["title"], fill=(118, 190, 222), font=font(25, True))
        draw.text((43, 95), cfg["subtitle"], fill=(87, 138, 169), font=font(13))
        for i, (_, label, activity, color, _, x0, y0, points) in enumerate(self.nodes):
            dx, dy = (0, 0) if freeze else floating_offset(i, phase)
            rgb = tuple(int(color[j:j+2], 16) for j in (1, 3, 5))
            for n, (px, py) in enumerate(points):
                pulse = 1 if freeze else particle_pulse(i, n, phase)
                ink = tuple(min(255, round(c*self.brightness[activity]*pulse)) for c in rgb)
                x, y = round(x0+dx+px), round(y0+dy+py)
                draw.point((x, y), fill=ink)
                if n % 8 == 0:
                    draw.ellipse((x-1, y-1, x+1, y+1), fill=ink)
            draw.text((x0, y0+LABEL_OFFSET), label, anchor="mm",
                      font=font(LABEL_SIZE, True), fill=(207, 228, 245))
        draw.line((43, SIZE[1]-39, 1158, SIZE[1]-39), fill=(29, 67, 93), width=1)
        draw.text((43, SIZE[1]-31), "SKILL STATUS IS DESCRIPTIVE, NOT A PROFICIENCY SCORE",
                  fill=(111, 156, 182), font=font(13))
        # Preserve the committed baseline's right anchor (the prototype was 1px left).
        draw.text((1158, SIZE[1]-31), "YT-TECHDEV  /  FRAMEWORKS", anchor="ra",
                  fill=(114, 165, 193), font=font(13))
        return image

    def render(self, phase, *, freeze=False):
        image = Image.alpha_composite(self.base, self.light_layer(phase)).convert("RGB")
        return self.foreground(image, phase, freeze)

    def animated_mask(self):
        """Conservative, continuous support, including moving-light AA footprint."""
        mask = Image.new("L", SIZE)
        draw = ImageDraw.Draw(mask)
        for node in self.nodes:
            draw.rectangle(logo_envelope(node), fill=255)
        for j, orbit in enumerate(ORBITS):
            # Bounds over the complete allowed arc, expanded by a derivative
            # bound for the space between samples. No frame-only approximation.
            step = 2*LIGHT_ARCS[j]/1000
            pad = LIGHT_RADIUS + math.ceil((orbit[2]+orbit[3])*step)
            points = [orbit_point(orbit, LIGHT_STARTS[j]-LIGHT_ARCS[j]+step*n)
                      for n in range(1001)]
            draw.rectangle((math.floor(min(x for x, _ in points)-pad),
                            math.floor(min(y for _, y in points)-pad),
                            math.ceil(max(x for x, _ in points)+pad),
                            math.ceil(max(y for _, y in points)+pad)), fill=255)
        return mask


def global_palette(frames):
    sheet = Image.new("RGB", (SIZE[0], SIZE[1]*5))
    for i, fraction in enumerate((0, .2, .4, .6, .8)):
        sheet.paste(frames[int(len(frames)*fraction)], (0, i*SIZE[1]))
    return sheet.quantize(colors=256, method=Image.Quantize.MEDIANCUT)


def render_assets(renderer, destination, frames=FRAMES):
    destination.mkdir(parents=True, exist_ok=True)
    png = destination / "constellation-frameworks.png"
    gif = destination / "constellation-frameworks.gif"
    # Neutral, undrifted/unpulsed poster; orbital light is at phase zero.
    renderer.render(0, freeze=True).save(png, optimize=True)
    animation = [renderer.render(math.tau*n/frames) for n in range(frames)]
    palette = global_palette(animation)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in animation]
    indexed[0].save(gif, save_all=True, append_images=indexed[1:],
                    duration=DURATION_MS, loop=0, disposal=1, optimize=True)
    print(f"frameworks: {len(renderer.nodes)} nodes; GIF {gif.stat().st_size:,} bytes; "
          f"PNG {png.stat().st_size:,} bytes; {frames} x {DURATION_MS}ms")
