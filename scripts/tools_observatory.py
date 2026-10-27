"""Station Grid: rigid floating instruments, fixed station and periodic signals."""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import random
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "scripts/tools_particles.json"
FIXTURE_SHA256 = "b64c8d900729f0dbebfc2cbfad50ba3e4bae7585c084a257fe79b94574dacc21"
MOTION_FIXTURE = ROOT / "scripts/tools_motion_v1.json"
MOTION_SHA256 = "642b62f62fe5eae0add1d898b5263bcb5d8d3875b0a5988619fd6d189880b5c3"
# Literal frozen pixels already include emphasized-dot radii. Integer placement
# adds no resampling/AA/glow support; two extra pixels cover palette diagnostics.
ENVELOPE_PAD = 2
SIZE = (1200, 900)
FRAMES, DURATION_MS = 48, 160
COLUMNS, ROWS = (215, 600, 985), (222, 444, 666)
LABEL_SIZE, LABEL_OFFSET = 38, 95
TITLE = "03  /  TOOLS & PLATFORMS"
SUBTITLE = "INSTRUMENTS, INFRASTRUCTURE & AI ASSISTANTS"
SIGNATURE = "DUST  →  ORBITS  →  OBSERVATORY"
HEADER = "YT-TECHDEV   /   SKILL CONSTELLATION"
SUPPORTS = (407, 793)
SIGNALS = ((407, 254, 0, 69), (793, 475, 0, 69),
           (365, 146, 42, 0), (1032, 820, 42, 0))
# The study's third carrier (165,146) was fully occluded by its fixed logo
# mask. Move only that carrier along the SAME top deck so all four are visible.
NAVIGATION = ((65, 182), (1135, 182), (65, 784), (1135, 784))
FONT_SHA256 = {
    False: "ae7b7855e115a5966d8b1b3f80f254ccc117ec86f9965e202ee2940453837280",
    True: "5c1247acef7f2b8522a31742c76d6adcb5569bacc0be7ceaa4dc39dd252ce895",
}


def load_fixture(path=FIXTURE):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != FIXTURE_SHA256:
        raise ValueError("Frozen Tools fixture changed; separate identity review required")
    return json.loads(data)


def signal_state(index, phase):
    """Integer harmonics only; round periodic outputs to eliminate float epsilon."""
    x, y, dx, dy = SIGNALS[index]
    t = round(math.sin(phase + index * 1.17), 12)
    return (round(x + dx * t, 9), round(y + dy * t, 9))


def load_motion(path=MOTION_FIXTURE):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != MOTION_SHA256:
        raise ValueError("Reviewed Tools motion fixture changed")
    return json.loads(data)['logos']


def floating_offset(spec, phase, *, raster=True):
    """A slow reversible diagonal drift, never an orbit around the grid anchor.

    Both axes share one scalar. Different slopes and evenly separated phases
    prevent synchronization. Round scalar epsilon before integer placement so
    the exact periodic endpoint cannot flip a half-pixel rounding decision.
    """
    t = round(math.sin(spec['harmonic'] * phase + math.tau * spec['phase_turns']), 12)
    values = (spec['ax'] * t, spec['ay'] * t)
    return tuple(round(v) if raster else v for v in values)


def navigation_strength(index, phase):
    return round(66 + 24 * math.sin(phase + index * .74))


def empty_layer():
    return Image.new("RGBA", SIZE)


def tools_font(size, bold=False):
    """Fonts frozen from the approved study, independent of runner font packages."""
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    return ImageFont.truetype(str(ROOT / 'scripts/tools_fonts' / name), size)


class StationGrid:
    def __init__(self, cfg, font=tools_font):
        self.cfg = cfg
        self.font = font
        # Fail explicitly instead of silently falling back to different glyphs.
        for bold, digest in FONT_SHA256.items():
            if hashlib.sha256(Path(font(20, bold).path).read_bytes()).hexdigest() != digest:
                raise ValueError("Tools typography requires the reviewed DejaVu Sans font")
        self.fixture = load_fixture()
        self.nodes = [dict(symbol, anchor=(COLUMNS[i % 3], ROWS[i // 3]))
                      for i, symbol in enumerate(self.fixture["symbols"])]
        self.motion = load_motion()
        if [m['key'] for m in self.motion] != [n['key'] for n in self.nodes]:
            raise ValueError("Tools motion inventory mismatch")
        expected = [(n['key'], n['label'], n['category'], n['color'], n['annotation'])
                    for n in self.nodes]
        if list(cfg['icons']) != expected:
            raise ValueError("Tools inventory differs from frozen identities")
        self.texts = self.text_specs()
        self.boxes = self.protection_boxes()
        self.protected = Image.new("L", SIZE)
        draw = ImageDraw.Draw(self.protected)
        for box in self.boxes:
            draw.rectangle(box, fill=255)
        # Match the approved study's fixed 13px falloff; clear the core AFTER
        # all glow and antialias filtering, including the signal layer.
        self.exclusion = ImageChops.lighter(
            self.protected, self.protected.filter(ImageFilter.GaussianBlur(13)))
        self.background = self.make_background()
        self.structure = self.make_structure()
        self.foreground = self.make_foreground()
        self.symbols = self.make_symbols()
        base = Image.alpha_composite(self.background.convert("RGBA"), self.structure)
        self.static = base.convert("RGB")

    def text_specs(self):
        texts = [((43, 27), HEADER, 20, True, None, (177, 220, 242)),
                 ((43, 59), TITLE, 25, True, None, (118, 190, 222)),
                 ((43, 99), SUBTITLE, 14, False, None, (113, 162, 188)),
                 ((43, 854), SIGNATURE, 17, False, None, (116, 162, 187)),
                 ((1157, 854), "YT-TECHDEV", 17, False, "ra", (127, 168, 189))]
        for node in self.nodes:
            x, y = node['anchor']
            texts.append(((x, y + LABEL_OFFSET), node['label'], LABEL_SIZE,
                          True, "mm", (207, 228, 245)))
            if node['annotation']:
                texts.append(((x, y + 130), node['annotation'], 20, True,
                              "mm", (147, 195, 219)))
        return texts

    def protection_boxes(self):
        boxes = []
        # Union historical cores with analytically bounded continuous motion.
        # The reviewed motion fits inside the old cores: station pixels and
        # signals remain unchanged, including their fixed 13px falloff.
        for node, motion in zip(self.nodes, self.motion):
            x, y = node['anchor']
            l, t, r, b = self.logo_envelope(node, motion, ENVELOPE_PAD)
            boxes.append((min(x - 100, l), min(y - 85, t),
                          max(x + 100, r), max(y + 85, b)))
        d = ImageDraw.Draw(Image.new("L", SIZE))
        for xy, text, size, bold, anchor, _ in self.texts:
            l, t, r, b = d.textbbox(xy, text, font=self.font(size, bold), anchor=anchor)
            if text not in (HEADER, TITLE, SUBTITLE, SIGNATURE, "YT-TECHDEV"):
                boxes.append((l - 6, t - 6, r + 6, b + 6))
        boxes.extend(((34, 19, 1166, 121), (34, 838, 1166, 887)))
        return boxes

    def logo_envelope(self, node, motion, pad=0):
        """Inclusive bounds for every real phase, not a sampled-frame estimate."""
        x, y = node['anchor']
        xs, ys = [p[0] for p in node['pixels']], [p[1] for p in node['pixels']]
        ax, ay = math.ceil(abs(motion['ax'])), math.ceil(abs(motion['ay']))
        return (x + min(xs) - ax - pad, y + min(ys) - ay - pad,
                x + max(xs) + ax + pad, y + max(ys) + ay + pad)

    def protect(self, layer):
        alpha = ImageChops.multiply(layer.getchannel("A"),
                                   ImageChops.invert(self.exclusion))
        alpha.paste(0, mask=self.protected)
        layer.putalpha(alpha)
        return layer

    def make_background(self):
        small = Image.new('RGB', (300, 225))
        pix = small.load()
        for y in range(225):
            for x in range(300):
                u, v = x / 299, y / 224
                blue = math.exp(-((u - .82) / .54) ** 2 - ((v - .23) / .67) ** 2)
                purple = math.exp(-((u - .12) / .65) ** 2 - ((v - .78) / .54) ** 2)
                pix[x, y] = (round(4 + 3 * blue + 5 * purple),
                             round(10 + 9 * blue + 2 * purple),
                             round(24 + 13 * blue + 8 * purple))
        image = small.resize(SIZE, Image.Resampling.BICUBIC)
        d = ImageDraw.Draw(image)
        rng = random.Random(847291 + 193)
        for _ in range(460):
            x, y = rng.randrange(1200), rng.randrange(900)
            if self.protected.getpixel((x, y)):
                continue
            value = rng.randrange(26, 83)
            d.point((x, y), fill=(value // 2, round(value * .76), value))
        for x, y in ((28, 130), (1169, 323), (29, 750), (875, 855), (749, 136), (450, 835)):
            d.point((x, y), fill=(100, 139, 162))
        return image

    def make_structure(self):
        scale = 3
        high = Image.new("RGBA", (3600, 2700))
        d = ImageDraw.Draw(high)

        def line(points, color, width=1):
            d.line([(round(x * scale), round(y * scale)) for x, y in points],
                   fill=color, width=max(1, round(width * scale)), joint="curve")

        # One continuous chamfered station hull, two shared load-bearing rails.
        line([(96,146),(1110,146),(1153,188),(1153,783),(1114,820),
              (90,820),(47,780),(47,190),(96,146)], (116,160,178,74), 1.2)
        line([(110,154),(1095,154)], (68,111,140,43), 1)
        for x in SUPPORTS:
            line([(x,161),(x,804)], (116,154,173,68), 1.15)
            line([(x+7,176),(x+7,791)], (64,110,139,38), 1)
            for y in (187,347,409,569,631,793):
                line([(x-9,y),(x+9,y)], (129,164,181,61), 1)
        # Restrained deck fragments connect the shared system, never nine cards.
        for y in (365,587,820):
            line([(63,y),(1136,y)], (105,150,170,74), 1.1)
            for a, b in ((92,330),(482,717),(870,1107)):
                line([(a,y+5),(b,y+5)], (65,104,134,44), .8)
            for x in (78,386,429,772,815,1122):
                line([(x,y-4),(x+8,y+4)], (120,155,170,70), 1)
        for x, sign in ((47,1),(1153,-1)):
            for y in (235,457,679):
                line([(x,y-22),(x+sign*13,y-10),(x+sign*13,y+11),(x,y+23)],
                     (127,163,177,75), 1.1)
        fine = high.resize(SIZE, Image.Resampling.LANCZOS)
        glow = fine.filter(ImageFilter.GaussianBlur(2))
        glow.putalpha(glow.getchannel("A").point(lambda a: round(a * .25)))
        return self.protect(Image.alpha_composite(glow, fine))

    def make_foreground(self):
        """Stationary typography only; symbol pixels live in separate sprites."""
        layer = empty_layer()
        d = ImageDraw.Draw(layer)
        for xy, text, size, bold, anchor, color in self.texts:
            d.text(xy, text, font=self.font(size, bold), anchor=anchor,
                   fill=(*color, 255))
        return layer

    def make_symbols(self):
        sprites = []
        for node in self.nodes:
            xs, ys = [p[0] for p in node['pixels']], [p[1] for p in node['pixels']]
            l, t, r, b = min(xs), min(ys), max(xs), max(ys)
            sprite = Image.new('RGBA', (r-l+1, b-t+1))
            d = ImageDraw.Draw(sprite)
            for px, py, red, green, blue in node['pixels']:
                d.point((px-l, py-t), fill=(red, green, blue, 255))
            sprites.append((sprite, (l, t)))
        return sprites

    def symbol_layer(self, phase, *, floating=True):
        layer = empty_layer()
        for node, spec, (sprite, origin) in zip(self.nodes, self.motion, self.symbols):
            dx, dy = floating_offset(spec, phase) if floating else (0, 0)
            x, y = node['anchor']
            layer.alpha_composite(sprite, (x + origin[0] + dx, y + origin[1] + dy))
        return layer

    def signal_layer(self, phase, *, only=None):
        high = Image.new("RGBA", (3600, 2700))
        d = ImageDraw.Draw(high)
        def dot(x, y, color, radius):
            d.ellipse(tuple(round(v * 3) for v in (x-radius, y-radius, x+radius, y+radius)), fill=color)
        for i in range(4):
            if only is not None and i != only:
                continue
            x, y = signal_state(i, phase)
            dot(x, y, (128,202,218,144), 1.55)
            points = [(x-5,y),(x+5,y)] if SIGNALS[i][2] else [(x,y-5),(x,y+5)]
            d.line([(round(px*3),round(py*3)) for px,py in points],
                   fill=(99,168,190,60), width=3)
        for i, (x, y) in enumerate(NAVIGATION):
            if only is not None:
                continue
            dot(x, y, (211,164,103,navigation_strength(i,phase)), 1.65)
        core = high.resize(SIZE, Image.Resampling.LANCZOS)
        glow = core.filter(ImageFilter.GaussianBlur(2))
        return self.protect(Image.alpha_composite(glow, core))

    def render(self, phase, *, floating=True):
        base = Image.alpha_composite(self.static.convert("RGBA"), self.signal_layer(phase))
        base = Image.alpha_composite(base, self.symbol_layer(phase, floating=floating))
        return Image.alpha_composite(base, self.foreground).convert("RGB")

    def motion_mask(self):
        """Fixed continuous travel, tail, radius, AA and bounded blur envelope."""
        mask = Image.new("L", SIZE)
        d = ImageDraw.Draw(mask)
        for x, y, dx, dy in SIGNALS:
            d.rectangle((x-dx-20,y-dy-20,x+dx+20,y+dy+20), fill=255)
        for x, y in NAVIGATION:
            d.rectangle((x - 20, y - 18, x + 20, y + 18), fill=255)
        for node, motion in zip(self.nodes, self.motion):
            d.rectangle(self.logo_envelope(node, motion, ENVELOPE_PAD), fill=255)
        return mask


def global_palette(renderer):
    # Reserve literal symbol RGBs, so no frozen silhouette pixel is lost to GIF
    # quantization. The remaining colors describe the static navy composition.
    base = renderer.render(0).quantize(colors=224, method=Image.Quantize.MEDIANCUT)
    colors = base.getpalette()[:224 * 3]
    reserved = [tuple(n['pixels'][0][2:]) for n in renderer.nodes]
    reserved += [(207, 228, 245), (147, 195, 219)]
    reserved += [(v, round(v * .91), round(v * .72)) for v in range(24, 192, 8)]
    colors += [c for rgb in reserved[:32] for c in rgb]
    palette = Image.new("P", (1, 1))
    palette.putpalette((colors + [0] * 768)[:768])
    return palette


def encode_assets(renderer, frames=FRAMES):
    poster = renderer.render(0)
    png = io.BytesIO()
    poster.save(png, format="PNG", optimize=True)
    palette = global_palette(renderer)
    animation = [renderer.render(math.tau * n / frames).quantize(
        palette=palette, dither=Image.Dither.NONE) for n in range(frames)]
    gif = io.BytesIO()
    animation[0].save(gif, format="GIF", save_all=True, append_images=animation[1:],
                      duration=DURATION_MS, loop=0, disposal=1, optimize=False)
    return png.getvalue(), gif.getvalue()


def validate_encoded(png, gif, frames):
    with Image.open(io.BytesIO(png)) as image:
        image.load()
        if image.size != SIZE or image.mode != "RGB":
            raise ValueError("Invalid Tools PNG")
    with Image.open(io.BytesIO(gif)) as image:
        if image.size != SIZE or image.n_frames != frames or image.info.get('loop') != 0:
            raise ValueError("Invalid Tools GIF")
        for n in range(frames):
            image.seek(n)
            image.load()
            if image.info.get('duration') != DURATION_MS:
                raise ValueError("Invalid Tools frame duration")


def render_assets(renderer, assets, frames=FRAMES):
    png, gif = encode_assets(renderer, frames)
    validate_encoded(png, gif, frames)
    assets.mkdir(parents=True, exist_ok=True)
    staged = []
    try:
        # Both encodings are complete and decoded before either destination is
        # replaced. Same-directory fsync+replace prevents partial image writes.
        for suffix, data in (("png", png), ("gif", gif)):
            with tempfile.NamedTemporaryFile(dir=assets, prefix=".tools-", delete=False) as f:
                staged.append((Path(f.name), assets / f"constellation-tools.{suffix}"))
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        for temporary, destination in staged:
            os.replace(temporary, destination)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    print(f"tools: 9 floating frozen symbols; {frames}x{DURATION_MS}ms; GIF {len(gif):,} bytes; PNG {len(png):,} bytes")
