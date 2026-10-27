"""Quiet Orbits: isolated Frameworks composition, motion and GIF encoding.

No import of render_sections: the caller supplies identity/configuration, SVG
sources, font access and activity colors. Frozen, audited contour samples avoid
system FreeType changing the approved particle silhouettes on regeneration.
"""
from __future__ import annotations

import hashlib
import io
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
# ORIGINAL_KEYS describes the immutable historical fixture, not the inventory.
EXPANSION_FIXTURE = Path(__file__).with_name("framework_expansion_contours.json")
EXPANSION_SHA256 = "b2e27c86ba99bb4c0946c4e1d7d3c522b00774d19faeaada8b25291969b99670"
REFINEMENT_FIXTURE = Path(__file__).with_name("framework_refinement_contours.json")
REFINEMENT_SHA256 = "a283c2615f578f9c6460f0d58af43d99e85c91c95ce95dcec8c07b62d6079701"
POLISH_FIXTURE = Path(__file__).with_name("framework_polish_contours.json")
POLISH_SHA256 = "4dc725dc2fb0743379188bc3492605db0bbb44eaf5ce0c4346e7546603fa2d48"
POLISHED_KEYS = ("framermotion", "googleappsscript")
PRESERVED_KEYS = ("react", "nextjs", "nodejs", "r3f", "threedotjs",
                  "vue", "tailwindcss", "jquery", "prisma")
BOOTSTRAP_SVG = Path(__file__).with_name("framework_brand_sources") / "bootstrap-logo.svg"
BOOTSTRAP_PNG = BOOTSTRAP_SVG.with_name("bootstrap-logo-128.png")
BOOTSTRAP_SVG_SHA256 = "df11d37a123e36a768f2a6064973c4c6ab17d1e3c6501c8bf434ca5c0134c9a2"
BOOTSTRAP_PNG_SHA256 = "72cc867688c2a915ad0b720fa63718cde4237a931f74e43458801f87b5974fef"
BOOTSTRAP_RGBA_SHA256 = "1168ac356ead386fceaf7a1ad5578cd4c1e89029a15e7e2348ccdd19636e3ecc"
BOOTSTRAP_SIZE = (128, 102)  # Exactly 1/4 of the official 512 x 408 canvas.
BOOTSTRAP_CLEAR_SPACE = 12  # Local layout allowance, not an upstream rule.
BOOTSTRAP_VERSION = "v5.3.8"
BOOTSTRAP_COMMIT = "25aa8cc0b32f0d1a54be575347e6d84b70b1acd7"
BOOTSTRAP_OUTLINE = Path(__file__).with_name("bootstrap_outline_contours.json")
BOOTSTRAP_OUTLINE_SHA256 = "4fb2dcc4f5ac36791e5d7a103709c0caf9b170164d72d4ebf2b93c1657731185"


def bootstrap_fixture():
    content = BOOTSTRAP_OUTLINE.read_bytes()
    if hashlib.sha256(content).hexdigest() != BOOTSTRAP_OUTLINE_SHA256:
        raise ValueError("Reviewed Bootstrap particle contours changed")
    data = json.loads(content)
    if data["version"] != 1 or len(data["points"]) != 1000 or len(data["colors"]) != 1000:
        raise ValueError("Invalid Bootstrap particle fixture")
    if hashlib.sha256(BOOTSTRAP_SVG.read_bytes()).hexdigest() != data["source"]["sha256"]:
        raise ValueError("Bootstrap contour reference changed")
    return data


def official_bootstrap():
    """Verified unchanged SVG plus its faithful, filter-aware lossless raster.

    Retained as historical evidence. Active rendering uses bootstrap_fixture();
    this raster is not composited into the current particle composition.
    """
    for path, digest in ((BOOTSTRAP_SVG, BOOTSTRAP_SVG_SHA256),
                         (BOOTSTRAP_PNG, BOOTSTRAP_PNG_SHA256)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Official Bootstrap asset changed: " + path.name)
    with Image.open(BOOTSTRAP_PNG) as source:
        source.load()
        if source.mode != "RGBA" or source.size != BOOTSTRAP_SIZE:
            raise ValueError("Official Bootstrap raster format changed")
        image = source.copy()
    if hashlib.sha256(image.tobytes()).hexdigest() != BOOTSTRAP_RGBA_SHA256:
        raise ValueError("Official Bootstrap lossless pixels changed")
    return image


def polish_fixture():
    content = POLISH_FIXTURE.read_bytes()
    if hashlib.sha256(content).hexdigest() != POLISH_SHA256:
        raise ValueError("Reviewed visual polish fixture changed")
    data = json.loads(content)
    if data["version"] != 1 or set(data["points"]) != {"framermotion"}:
        raise ValueError("Invalid visual polish fixture")
    for source in data["sources"].values():
        if hashlib.sha256((POLISH_FIXTURE.parent/source["file"]).read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Reviewed Motion reference changed")
    return data


def refinement_fixture():
    content = REFINEMENT_FIXTURE.read_bytes()
    if hashlib.sha256(content).hexdigest() != REFINEMENT_SHA256:
        raise ValueError("Reviewed refinement contour samples changed")
    data = json.loads(content)
    if data["version"] != 1 or set(data["points"]) != {"vue", "googleappsscript", "prisma"}:
        raise ValueError("Invalid refinement fixture")
    for source in data["sources"].values():
        if hashlib.sha256((REFINEMENT_FIXTURE.parent/source["file"]).read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Reviewed brand reference changed")
    return data


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
    # Archived WASM/Spring/crate/GAS remain reproducible in the old fixtures.
    # Only cfg['icons'] selects active marks; the new GAS explicitly overrides
    # its historical source-file illustration without rewriting that evidence.
    points = {**frozen["points"], **added["points"], **refinement_fixture()["points"],
              **polish_fixture()["points"], "bootstrap": bootstrap_fixture()["points"]}
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


def logo_envelope(node, padding=0, *, legacy=False):
    """Continuous full drift, rounded pixel centers, and emphasized dot radius."""
    key, *_, x, y, points = node
    # Local 3x AA has a 3px Lanczos footprint in addition to a 1.25px
    # accent radius. Five pixels conservatively contain its complete support.
    radius = 5 if key in (*POLISHED_KEYS, "bootstrap") and not legacy else DOT_RADIUS
    padx, pady = DRIFT[0] + radius + .5 + padding, DRIFT[1] + radius + .5 + padding
    return (math.floor(x + min(px for px, _ in points) - padx),
            math.floor(y + min(py for _, py in points) - pady),
            math.ceil(x + max(px for px, _ in points) + padx),
            math.ceil(y + max(py for _, py in points) + pady))


def fixed_protection(nodes, font, *, legacy=False):
    protected = Image.new("L", SIZE)
    draw = ImageDraw.Draw(protected)
    boxes = [("header", (0, 0, SIZE[0]-1, 113))]
    for node in nodes:
        key, label, _, _, _, x, y, _ = node
        padding = BOOTSTRAP_CLEAR_SPACE if key == "bootstrap" and not legacy else 3
        boxes.append((key, logo_envelope(node, padding=padding, legacy=legacy)))
        box = draw.textbbox((x, y + LABEL_OFFSET), label,
                           font=font(LABEL_SIZE, True), anchor="mm")
        boxes.append((label, (box[0]-8, box[1]-6, box[2]+8, box[3]+6)))
    for _, box in boxes:
        draw.rectangle(box, fill=255)
    soft = protected.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
    return boxes, protected, ImageChops.invert(ImageChops.lighter(protected, soft))


class QuietOrbits:
    def __init__(self, cfg, nodes, font, brightness):
        self.cfg, self.nodes = cfg, nodes
        self.font, self.brightness = font, brightness
        self.bootstrap_image = official_bootstrap()
        self.bootstrap_mode = "outline-particles"
        bootstrap = bootstrap_fixture()
        self.bootstrap_style = bootstrap["style"]
        polish = polish_fixture()
        self.sample_colors = {**refinement_fixture()["colors"], **polish["colors"],
                              "bootstrap": bootstrap["colors"]}
        self.polish_styles = polish["styles"]
        # All clipping/masking occurs AFTER orbital glow and AA, so zero is exact.
        self.protection_boxes, self.protected, self.keep = fixed_protection(nodes, font)
        # A fixed outer falloff prevents sharp rectangular ends without moving
        # the zero-alpha core as icons float. No frame-dependent mask exists.
        # Star attenuation is frozen to the pre-polish geometry. Enlarging an
        # orbital exclusion core must not brighten/dim any distant star.
        historical = {**json.loads(FIXTURE.read_bytes())["points"],
                      **json.loads(EXPANSION_FIXTURE.read_bytes())["points"],
                      **refinement_fixture()["points"]}
        historical_nodes = [(*n[:-1], historical[n[0]]) for n in nodes]
        _, _, self.background_keep = fixed_protection(historical_nodes, font, legacy=True)
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
        mask = self.background_keep.load()
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
        for i, (key, label, activity, color, _, x0, y0, points) in enumerate(self.nodes):
            dx, dy = (0, 0) if freeze else floating_offset(i, phase)
            rgb = tuple(int(color[j:j+2], 16) for j in (1, 3, 5))
            if key == "bootstrap" and self.bootstrap_mode == "outline-particles":
                self.polished_particles(image, self.nodes[i], i, phase, freeze,
                                        style=self.bootstrap_style)
                draw.text((x0, y0+LABEL_OFFSET), label, anchor="mm",
                          font=font(LABEL_SIZE, True), fill=(207, 228, 245))
                continue
            if key == "bootstrap" and self.bootstrap_mode == "official-svg-raster":
                # Archived renderer, exercised only by regression controls.
                width, height = self.bootstrap_image.size
                image.paste(self.bootstrap_image, (x0-width//2, y0-height//2), self.bootstrap_image)
                draw.text((x0, y0+LABEL_OFFSET), label, anchor="mm",
                          font=font(LABEL_SIZE, True), fill=(207, 228, 245))
                continue
            if key in self.polish_styles:
                self.polished_particles(image, self.nodes[i], i, phase, freeze)
                draw.text((x0, y0+LABEL_OFFSET), label, anchor="mm",
                          font=font(LABEL_SIZE, True), fill=(207, 228, 245))
                continue
            for n, (px, py) in enumerate(points):
                pulse = 1 if freeze else particle_pulse(i, n, phase)
                sample_color = self.sample_colors.get(key)
                if key == "bootstrap" and self.bootstrap_mode == "historical-particles":
                    sample_color = None
                source_rgb = (tuple(int(sample_color[n][j:j+2], 16) for j in (1, 3, 5))
                              if sample_color is not None else rgb)
                ink = tuple(min(255, round(c*self.brightness[activity]*pulse)) for c in source_rgb)
                x, y = round(x0+dx+px), round(y0+dy+py)
                draw.point((x, y), fill=ink)
                if n % 8 == 0:
                    draw.ellipse((x-1, y-1, x+1, y+1), fill=ink)
            draw.text((x0, y0+LABEL_OFFSET), label, anchor="mm",
                      font=font(LABEL_SIZE, True), fill=(207, 228, 245))
        return image

    def polished_particles(self, image, node, index, phase, freeze, *, style=None):
        key, _, activity, color, _, x0, y0, points = node
        style = self.polish_styles[key] if style is None else style
        scale = style["scale"]
        layer = Image.new("RGBA", (180*scale, 180*scale))
        draw = ImageDraw.Draw(layer)
        dx, dy = (0, 0) if freeze else floating_offset(index, phase)
        colors = self.sample_colors.get(key, [color]*len(points))
        for n, (px, py) in enumerate(points):
            pulse = 1 if freeze else particle_pulse(index, n, phase)
            ink = tuple(round(int(colors[n][j:j+2], 16)*self.brightness[activity]*pulse)
                        for j in (1, 3, 5))
            radius = style["accent_radius"] if n % style["accent_stride"] == 0 else style["radius"]
            x, y = (90+dx+px)*scale, (90+dy+py)*scale
            draw.ellipse((x-radius*scale, y-radius*scale, x+radius*scale, y+radius*scale),
                         fill=(*ink, 255))
        layer = layer.resize((180, 180), Image.Resampling.LANCZOS)
        image.paste(layer, (x0-90, y0-90), layer)

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
    bootstrap_ink = []
    for i, fraction in enumerate((0, .2, .4, .6, .8)):
        frame = frames[int(len(frames)*fraction)]
        sheet.paste(frame, (0, i*SIZE[1]))
        crop = frame.crop((910,605,1060,735))
        bootstrap_ink.extend(rgb for rgb, value in zip(crop.getdata(),crop.convert("L").getdata()) if value > 60)
    # Sparse violet edges otherwise lose their hue to the much larger navy and
    # text regions. Reserve 32 colors from their actual five-phase RGB samples;
    # retain one deterministic, shared palette and no dithering for every frame.
    palette = sheet.quantize(colors=224, method=Image.Quantize.MEDIANCUT)
    if not bootstrap_ink:
        raise ValueError("Bootstrap particle ink missing from palette samples")
    strip = Image.new("RGB", (len(bootstrap_ink),1))
    strip.putdata(bootstrap_ink)
    priority = strip.quantize(colors=32, method=Image.Quantize.MEDIANCUT)
    palette.putpalette(palette.getpalette()[:224*3] + priority.getpalette()[:32*3])
    return palette


def render_assets(renderer, destination, frames=FRAMES):
    destination.mkdir(parents=True, exist_ok=True)
    png = destination / "constellation-frameworks.png"
    gif = destination / "constellation-frameworks.gif"
    # Neutral, undrifted/unpulsed poster; orbital light is at phase zero.
    # Validate a complete in-memory PNG before replacing the visible file.
    # This also prevents readers from observing partial IDAT chunks during a
    # slow direct encoder write. The encoded format/optimization is unchanged.
    encoded = io.BytesIO()
    renderer.render(0, freeze=True).save(encoded, format="PNG", optimize=True)
    png_bytes = encoded.getvalue()
    with Image.open(io.BytesIO(png_bytes)) as check:
        check.verify()
    temporary = png.with_suffix(".png.tmp")
    temporary.write_bytes(png_bytes)
    temporary.replace(png)
    animation = [renderer.render(math.tau*n/frames) for n in range(frames)]
    palette = global_palette(animation)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in animation]
    indexed[0].save(gif, save_all=True, append_images=indexed[1:],
                    duration=DURATION_MS, loop=0, disposal=1, optimize=True)
    if png.read_bytes() != png_bytes:
        raise ValueError("Completed Frameworks PNG changed during GIF generation")
    print(f"frameworks: {len(renderer.nodes)} nodes; GIF {gif.stat().st_size:,} bytes; "
          f"PNG {png.stat().st_size:,} bytes; {frames} x {DURATION_MS}ms")
