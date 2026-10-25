#!/usr/bin/env python3
"""Verify actual Quiet Orbits assets, original logos, masks, timing and isolation."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageChops, ImageDraw, ImageStat

import render_sections as sections
from framework_orbits import (
    CONTOUR_SHA256, DOT_RADIUS, DRIFT, DURATION_MS, FIXTURE, FRAMES,
    LABEL_OFFSET, LABEL_SIZE, ORBITS, SIZE, QuietOrbits, floating_offset,
    global_palette, light_angle, logo_envelope, particle_pulse, prepared_contours,
)

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("React", "Next.js", "Node.js", "R3F", "Three.js", "WebAssembly")
KEYS = ("react", "nextjs", "nodejs", "r3f", "threedotjs", "webassembly")
COLORS = ("#79f1ff", "#f1f3fd", "#a9efb8", "#dcc2ff", "#c6e9f9", "#b7bdff")
PROTECTED_BLOBS = {
    "assets/constellation-languages.gif": "9f5a84ddae394f44992215c59a4271e37a932fb4",
    "assets/constellation-languages.png": "50ae288464fd4e9de3db5bc69d3b479ebf88b385",
    "assets/constellation-tools.gif": "d2399da46c1b971a2ed070a0b1c6c45b1d40374c",
    "assets/constellation-tools.png": "b71675893426c6e1797b25c985e4c584ef87528c",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_sha(path):
    content = path.read_bytes()
    return hashlib.sha1(f"blob {len(content)}\0".encode()+content).hexdigest()


def load_renderer():
    original = json.loads((ROOT/"data/icon-paths.json").read_text())
    extra = json.loads((ROOT/"data/supplemental-icons.json").read_text())
    extra["paths"].update(extra["devicon_paths"])
    cfg = sections.SECTIONS["frameworks"]
    sources = {n[0]: sections.glyph_svg(n[0], original, extra["paths"])
               for n in cfg["icons"]}
    nodes = prepared_contours(cfg, sections.COLUMNS, sources)
    return QuietOrbits(cfg, nodes, sections.font, sections.ACTIVITY_BRIGHTNESS)


def distance(a, b, mask=None):
    return sum(ImageStat.Stat(ImageChops.difference(a, b), mask=mask).mean)/3


def verify_structure(renderer):
    nodes = renderer.nodes
    assert tuple(n[0] for n in nodes) == KEYS
    assert tuple(n[1] for n in nodes) == NAMES, "Six names/order changed"
    assert tuple(n[3] for n in nodes) == COLORS, "Original logo colors changed"
    assert tuple((n[5], n[6]) for n in nodes) == (
        (187, 177), (600, 177), (1013, 177), (187, 385), (600, 385), (1013, 385))
    assert len(ORBITS) == 2
    assert tuple(o[:5] for o in ORBITS) == ((600, 281, 574, 138, -7), (606, 282, 657, 217, 9))
    assert sha256(FIXTURE) == CONTOUR_SHA256
    fixture = json.loads(FIXTURE.read_text())
    assert all(len(n[-1]) == 1000 for n in nodes), "Missing contour samples"

    texts = []
    original_text = ImageDraw.ImageDraw.text

    def record_text(draw, xy, text, *args, **kwargs):
        texts.append((xy, text, kwargs))
        return original_text(draw, xy, text, *args, **kwargs)

    with patch.object(ImageDraw.ImageDraw, "text", record_text):
        black = renderer.foreground(Image.new("RGB", SIZE), 0, freeze=True)
    assert [t for _, t, _ in texts][3:9] == list(NAMES)
    assert len(texts) == 11, "Unexpected labels or badges"
    draw = ImageDraw.Draw(black)
    gaps, silhouettes = [], {}
    for node in nodes:
        key, name, category, color, _, x, y, points = node
        xy, _, options = next(entry for entry in texts if entry[1] == name)
        assert xy == (x, y+88) and options["anchor"] == "mm"
        assert options["font"].size == 36
        box = draw.textbbox(xy, name, font=options["font"], anchor="mm")
        gap = box[1] - (y+max(py for _, py in points)+DRIFT[1]+DOT_RADIUS+.5)
        assert gap >= 8, f"Logo/name collision: {name}: {gap}"
        gaps.append(gap)
        envelope = logo_envelope(node)
        assert 0 <= envelope[0] < envelope[2] < SIZE[0], f"{name} clipped horizontally"
        assert 108 < envelope[1] < envelope[3] < 516, f"{name} clipped/header collision"
        assert 0 <= box[0] < box[2] < SIZE[0] and box[3] < 516
        rgb = tuple(round(int(color[k:k+2],16)*renderer.brightness[category]) for k in (1,3,5))
        mask = bytes(255 if black.getpixel((px, py)) == rgb else 0
                     for py in range(y-75,y+75) for px in range(x-90,x+90))
        digest = hashlib.sha256(mask).hexdigest()
        assert digest == fixture["baseline_logo_masks"][key], f"{key}: committed silhouette changed"
        silhouettes[key] = digest
        # Every point's complete motion envelope is contained in the fixed core.
        assert renderer.protected.crop((envelope[0], envelope[1], envelope[2]+1, envelope[3]+1)).getextrema() == (255,255)
    for _, text, options in texts:
        assert options["font"].path, "Unexpected default font fallback"
    assert ImageChops.multiply(renderer.keep, renderer.protected).getbbox() is None
    assert ImageChops.multiply(renderer.structure.getchannel("A"), renderer.protected).getbbox() is None
    return {"minimum_logo_name_gap_px": min(gaps), "baseline_logo_masks_sha256": silhouettes}


def verify_assets(renderer, assets):
    png, gif = (assets/f"constellation-frameworks.{ext}" for ext in ("png", "gif"))
    with Image.open(png) as image:
        image.verify()
    poster = Image.open(png).convert("RGB")
    assert poster.size == SIZE
    assert ImageChops.difference(poster, renderer.render(0, freeze=True)).getbbox() is None, "PNG content mismatch"
    assert gif.stat().st_size <= 3_500_000, "GIF exceeds approved preferred size"

    for i in range(6):
        assert all(abs(a-b) < 1e-10 for a,b in zip(floating_offset(i, 0),floating_offset(i,math.tau)))
        for n in (0, 499, 999):
            assert abs(particle_pulse(i,n,0)-particle_pulse(i,n,math.tau)) < 1e-10
    for i in range(2):
        assert abs(light_angle(i,0)-light_angle(i,math.tau)) < 1e-10
    assert ImageChops.difference(renderer.render(0),renderer.render(math.tau)).getbbox() is None, "RGB endpoint seam"

    source = [renderer.render(math.tau*n/FRAMES) for n in range(FRAMES)]
    palette = global_palette(source)
    static_mask = ImageChops.invert(renderer.animated_mask())
    assert static_mask.histogram()[255] > 500_000, "Insufficient exposed background checked"
    decoded, durations, quantization_errors = [], [], []
    with Image.open(gif) as animation:
        assert animation.size == SIZE and animation.n_frames == FRAMES
        assert animation.info.get("loop") == 0, "GIF does not loop infinitely"
        for n in range(FRAMES):
            animation.seek(n)
            durations.append(animation.info.get("duration"))
            frame = animation.convert("RGB")
            frame.load()
            assert frame.size == SIZE
            expected = source[n].quantize(palette=palette,dither=Image.Dither.NONE).convert("RGB")
            assert ImageChops.difference(frame, expected).getbbox() is None, f"Encoded frame {n} mismatch"
            light = renderer.light_layer(math.tau*n/FRAMES)
            assert ImageChops.multiply(light.getchannel("A"),renderer.protected).getbbox() is None, "Light crosses protection core"
            if n:
                assert ImageChops.multiply(ImageChops.difference(source[0],source[n]),static_mask.convert("RGB")).getbbox() is None, "RGB background shimmer"
                assert ImageChops.multiply(ImageChops.difference(decoded[0],frame),static_mask.convert("RGB")).getbbox() is None, "Decoded background shimmer"
            # Palette fidelity on the actual illuminated foreground, not its
            # mostly-dark bounding rectangle.
            bright = source[n].convert("L").point(lambda v: 255 if v > 100 else 0)
            quantization_errors.append(distance(source[n],frame,bright))
            decoded.append(frame)
    assert set(durations) == {DURATION_MS} and sum(durations) == 6400, "GIF timing changed"
    steps = [distance(decoded[n],decoded[(n+1)%FRAMES]) for n in range(FRAMES)]
    assert min(steps) > 0, "Frozen transition"
    assert steps[-1] <= max(steps[:-1])*1.25, "Decoded seam is abnormally large"
    assert max(quantization_errors) < 8, "Foreground color fidelity degraded"
    for width in (375,320):
        small = poster.resize((width,round(SIZE[1]*width/SIZE[0])),Image.Resampling.LANCZOS)
        for node in renderer.nodes:
            _,name,_,_,_,x,y,_ = node
            box = ImageDraw.Draw(poster).textbbox((x,y+88),name,font=renderer.font(36,True),anchor="mm")
            crop = small.crop(tuple(round(v*width/1200) for v in box)).convert("L")
            assert crop.getextrema()[1] > 100 and sum(crop.histogram()[100:]) > 10, f"Reduced label invisible: {name}"
    return {"canvas": list(SIZE), "frames": len(decoded), "durations_ms": sorted(set(durations)),
            "total_ms": sum(durations), "loop": 0, "gif_bytes": gif.stat().st_size,
            "seam_mean_abs_rgb": steps[-1], "interior_mean_abs_rgb": sum(steps[:-1])/63,
            "interior_max_abs_rgb": max(steps[:-1]),
            "seam_active_mean_abs_rgb": distance(decoded[-1],decoded[0],renderer.animated_mask()),
            "periodic_endpoint_equal": True, "static_pixels_checked": static_mask.histogram()[255],
            "rgb_background_changed_pixels": 0, "decoded_background_changed_pixels": 0,
            "foreground_quantization_mean_abs_rgb_max": max(quantization_errors),
            "sha256": {p.name: sha256(p) for p in (png,gif)}}


def verify_protected():
    actual = {p: blob_sha(ROOT/p) for p in PROTECTED_BLOBS}
    assert actual == PROTECTED_BLOBS, "Frozen Languages/Tools bytes changed"
    return actual


def verify_determinism(assets):
    with tempfile.TemporaryDirectory(prefix="quiet-orbits-") as directory:
        checkout = Path(directory)/"repo"
        shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git","__pycache__"))
        pair = ["constellation-frameworks.png","constellation-frameworks.gif"]
        expected = {p: sha256(assets/p) for p in pair}
        def other_files():
            return {str(p.relative_to(checkout)):sha256(p) for p in checkout.rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts
                    and p.relative_to(checkout).as_posix() not in {"assets/"+name for name in pair}}
        preserved = other_files()
        for iteration in range(2):
            subprocess.run([sys.executable,str(checkout/"scripts/render_sections.py"),"--only","frameworks"],check=True)
            actual = {p:sha256(checkout/"assets"/p) for p in pair}
            assert actual == expected, f"Canonical generation {iteration+1} differs"
            assert other_files() == preserved, "Frameworks CLI modified another file"
        return {"canonical_runs": 2, "identical_to_validated_assets": True,
                "unselected_files_unchanged": True, "sha256": expected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets",type=Path,default=ROOT/"assets")
    parser.add_argument("--determinism",action="store_true")
    parser.add_argument("--protected",action="store_true",help="Assert this phase's frozen Languages/Tools blobs")
    parser.add_argument("--report",type=Path)
    args = parser.parse_args()
    renderer = load_renderer()
    result = {"structure":verify_structure(renderer),"animation":verify_assets(renderer,args.assets)}
    if args.protected:
        result["protected_blobs"] = verify_protected()
    if args.determinism:
        result["determinism"] = verify_determinism(args.assets)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print("Frameworks content, original contours, fixed masks, timing and loop: PASS")


if __name__ == "__main__":
    main()
