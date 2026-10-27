#!/usr/bin/env python3
"""Verify actual Quiet Orbits assets, original logos, masks, timing and isolation."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageChops, ImageDraw, ImageStat

import render_sections as sections
from framework_orbits import (
    CONTOUR_SHA256, DOT_RADIUS, DRIFT, DURATION_MS, FIXTURE, FRAMES,
    LABEL_OFFSET, LABEL_SIZE, ORBITS, SIZE, ORIGINAL_KEYS,
    EXPANSION_FIXTURE, EXPANSION_SHA256, QuietOrbits, floating_offset,
    global_palette, light_angle, logo_envelope, particle_pulse, prepared_contours,
    REFINEMENT_FIXTURE, REFINEMENT_SHA256, PRESERVED_KEYS, refinement_fixture,
    POLISH_FIXTURE, POLISH_SHA256, POLISHED_KEYS, polish_fixture,
    BOOTSTRAP_SVG, BOOTSTRAP_PNG, BOOTSTRAP_SVG_SHA256, BOOTSTRAP_PNG_SHA256,
    BOOTSTRAP_RGBA_SHA256, BOOTSTRAP_SIZE, BOOTSTRAP_CLEAR_SPACE,
    BOOTSTRAP_VERSION, BOOTSTRAP_COMMIT, official_bootstrap,
    BOOTSTRAP_OUTLINE, BOOTSTRAP_OUTLINE_SHA256, bootstrap_fixture,
)

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("React", "Next.js", "Node.js", "R3F", "Three.js", "Vue.js",
         "Google Apps Script", "TailwindCSS", "Bootstrap", "Framer Motion",
         "jQuery", "Prisma")
KEYS = ("react", "nextjs", "nodejs", "r3f", "threedotjs", "vue", "googleappsscript",
        "tailwindcss", "bootstrap", "framermotion", "jquery", "prisma")
COLORS = ("#79f1ff", "#f1f3fd", "#a9efb8", "#dcc2ff", "#c6e9f9", "#42b883",
          "#4285f4", "#80e5ef", "#c9a4ff", "#fef62a", "#7acef4", "#edf3ff")
POSITIONS = ((215,191),(600,191),(985,191),(215,431),(600,431),(985,431),
             (215,671),(600,671),(985,671),(215,911),(600,911),(985,911))
RGB_FIXTURE = ROOT / "scripts/framework_preserved_rgb.json"
RGB_SHA256 = "a9d550ffa38d680c4ff5e66967f5bc78c9c10d3177338d8a2ed6926748d8fd1d"
POLISH_RGB_FIXTURE = ROOT / "scripts/framework_polish_preserved_rgb.json"
POLISH_RGB_SHA256 = "cacce835ecc191e8cc038ddfc534c8d8c697a9e8169b9cd00b89b8a96ff55b4f"
BOOTSTRAP_RGB_FIXTURE = ROOT / "scripts/framework_bootstrap_preserved_rgb.json"
BOOTSTRAP_RGB_SHA256 = "67219d4d327d0a98c29cca3c1b315669f54b51829793c67fcd82b8c74d173091"
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
    sources = {key: sections.glyph_svg(key, original, extra["paths"])
               for key in ORIGINAL_KEYS}
    nodes = prepared_contours(cfg, sections.COLUMNS, sources)
    return QuietOrbits(cfg, nodes, sections.font, sections.ACTIVITY_BRIGHTNESS)


def distance(a, b, mask=None):
    return sum(ImageStat.Stat(ImageChops.difference(a, b), mask=mask).mean)/3


def verify_palette_tables(gif):
    """Parse real GIF blocks: all image color tables must equal the global one."""
    data = gif.read_bytes()
    assert data[:6] in (b"GIF87a", b"GIF89a") and data[10] & 128
    size = 3 * 2**((data[10] & 7)+1)
    global_table, position = data[13:13+size], 13+size
    count = 0

    def skip_subblocks(p):
        while data[p]:
            p += 1 + data[p]
        return p+1

    while data[position] != 59:
        if data[position] == 33:
            position = skip_subblocks(position+2)
        else:
            assert data[position] == 44, "Invalid GIF block"
            flags = data[position+9]
            position += 10
            table = global_table
            if flags & 128:
                length = 3 * 2**((flags & 7)+1)
                table = data[position:position+length]
                position += length
            assert table == global_table, "Frame palette drift"
            count += 1
            position = skip_subblocks(position+1)
    assert count == FRAMES
    return {"image_blocks": count, "all_tables_equal_global": True,
            "palette_table_sha256": hashlib.sha256(global_table).hexdigest()}


def verify_structure(renderer):
    nodes = renderer.nodes
    assert tuple(n[0] for n in nodes) == KEYS
    assert len(nodes) == 12 and len({n[1] for n in nodes}) == 12
    bootstrap = verify_bootstrap_outline(renderer)
    assert tuple(n[1] for n in nodes) == NAMES, "Twelve names/order changed"
    assert tuple(n[3] for n in nodes) == COLORS, "Original logo colors changed"
    assert tuple((n[5], n[6]) for n in nodes) == POSITIONS
    assert len(ORBITS) == 2
    assert tuple(o[:5] for o in ORBITS) == ((600,558,560,430,-8), (606,570,600,490,9))
    assert sha256(FIXTURE) == CONTOUR_SHA256
    fixture = json.loads(FIXTURE.read_text())
    assert sha256(EXPANSION_FIXTURE) == EXPANSION_SHA256
    added = json.loads(EXPANSION_FIXTURE.read_text())
    assert tuple(added["points"]) == ("googleappsscript", "tailwindcss", "bootstrap",
                                    "framermotion", "jquery", "springboot", "rustcrate"), "Historical expansion fixture changed"
    refined = refinement_fixture()
    assert sha256(REFINEMENT_FIXTURE) == REFINEMENT_SHA256
    from build_framework_refinement import build
    assert build() == REFINEMENT_FIXTURE.read_bytes(), "Brand source/contour derivation changed"
    polished = polish_fixture()
    from build_framework_polish import build as build_polish, STYLES
    assert sha256(POLISH_FIXTURE) == POLISH_SHA256
    assert build_polish() == POLISH_FIXTURE.read_bytes(), "Motion source/contour derivation changed"
    assert renderer.polish_styles == STYLES, "Reviewed local particle style changed"
    assert set(renderer.polish_styles) == set(POLISHED_KEYS)
    assert all(len(n[-1]) == 1000 for n in nodes), "Missing contour samples"
    for node in nodes:
        key, *_, points = node
        expected = ({"bootstrap": bootstrap_fixture()["points"]} if key == "bootstrap" else
                    polished["points"] if key in polished["points"] else
                    refined["points"] if key in refined["points"] else
                    fixture["points"] if key in ORIGINAL_KEYS else added["points"])
        assert [list(p) for p in points] == expected[key], f"Coordinates changed: {key}"
        assert len(set(points)) >= 180, f"Degenerate symbol: {key}"
        assert all(math.isfinite(v) and abs(v) <= 80 for point in points for v in point)
        if key not in ORIGINAL_KEYS and key not in refined["points"] and key not in polished["points"]:
            assert added["references"][key].startswith("https://") and added["descriptions"][key]
        if key in refined["points"]:
            assert len(renderer.sample_colors[key]) == 1000
            assert renderer.sample_colors[key] == refined["colors"][key]
        if key in polished["points"]:
            assert renderer.sample_colors[key] == polished["colors"][key]
    assert set(renderer.sample_colors) == {"vue", "googleappsscript", "prisma", "framermotion", "bootstrap"}
    assert set(renderer.sample_colors["framermotion"]) == {"#fef62a"}
    assert set(renderer.sample_colors["googleappsscript"]) == {"#ea4335", "#fbbc04", "#34a853", "#4285f4", "#ffffff"}
    assert set(renderer.sample_colors["vue"]) == {"#42b883", "#80c7c6"}

    texts, lines = [], []
    original_text = ImageDraw.ImageDraw.text
    original_line = ImageDraw.ImageDraw.line

    def record_text(draw, xy, text, *args, **kwargs):
        texts.append((xy, text, kwargs))
        return original_text(draw, xy, text, *args, **kwargs)

    def record_line(draw, xy, *args, **kwargs):
        lines.append(xy)
        return original_line(draw, xy, *args, **kwargs)

    with patch.object(ImageDraw.ImageDraw, "text", record_text), \
         patch.object(ImageDraw.ImageDraw, "line", record_line):
        black = renderer.foreground(Image.new("RGB", SIZE), 0, freeze=True)
    assert [t for _, t, _ in texts][3:] == list(NAMES)
    assert [t for _, t, _ in texts][:3] == ["YT-TECHDEV   /   SKILL CONSTELLATION", "02  /  FRAMEWORKS & RUNTIMES", "FROM UI LIBRARIES TO APPLICATION SYSTEMS"]
    assert texts[2][0] == (43,95) and texts[2][2]["font"].size == 13
    assert texts[2][2]["fill"] == (87,138,169)
    assert ImageDraw.Draw(black).textbbox((43,95), texts[2][1], font=texts[2][2]["font"])[2] < SIZE[0]-43
    assert len(texts) == 15, "Unexpected footer, labels or badges"
    assert not lines, "Frameworks footer rule must be absent"
    assert [key for key, _ in renderer.protection_boxes].count("footer") == 0
    draw = ImageDraw.Draw(black)
    gaps, silhouettes, geometry = [], {}, []
    for node in nodes:
        key, name, category, color, _, x, y, points = node
        xy, _, options = next(entry for entry in texts if entry[1] == name)
        assert xy == (x, y+LABEL_OFFSET) and options["anchor"] == "mm"
        assert options["font"].size == LABEL_SIZE == 38
        box = draw.textbbox(xy, name, font=options["font"], anchor="mm")
        gap = box[1] - logo_envelope(node)[3]
        assert gap >= 8, f"Logo/name collision: {name}: {gap}"
        gaps.append(gap)
        envelope = logo_envelope(node)
        assert 0 <= envelope[0] < envelope[2] < SIZE[0], f"{name} clipped horizontally"
        assert 114 < envelope[1] < envelope[3] < SIZE[1]-44, f"{name} clipped/header collision"
        assert 8 <= box[0] < box[2] < SIZE[0]-8 and box[3] < SIZE[1]-44
        geometry.extend(((key+" symbol", envelope), (name+" label", box)))
        rgb = tuple(round(int(color[k:k+2],16)*renderer.brightness[category]) for k in (1,3,5))
        mask = bytes(255 if black.getpixel((px, py)) == rgb else 0
                     for py in range(y-75,y+75) for px in range(x-90,x+90))
        digest = hashlib.sha256(mask).hexdigest()
        if key in ORIGINAL_KEYS:
            assert digest == fixture["baseline_logo_masks"][key], f"{key}: committed silhouette changed"
        silhouettes[key] = digest
        # Every point's complete motion envelope is contained in the fixed core.
        assert renderer.protected.crop((envelope[0], envelope[1], envelope[2]+1, envelope[3]+1)).getextrema() == (255,255)
        assert renderer.protected.crop(box).getextrema() == (255,255), f"Label mask missing: {name}"
    for i, (name,a) in enumerate(geometry):
        for other,b in geometry[i+1:]:
            assert a[2]+8 < b[0] or b[2]+8 < a[0] or a[3]+8 < b[1] or b[3]+8 < a[1], f"Overlap: {name}, {other}"
    for _, text, options in texts:
        assert options["font"].path, "Unexpected default font fallback"
    assert ImageChops.multiply(renderer.keep, renderer.protected).getbbox() is None
    assert ImageChops.multiply(renderer.structure.getchannel("A"), renderer.protected).getbbox() is None
    assert sha256(RGB_FIXTURE) == RGB_SHA256, "Preserved RGB baseline changed"
    rgb_fixture = json.loads(RGB_FIXTURE.read_text())
    # Keep all 45 independent historical RGB checks. Motion's old drawing
    # is exercised as archived evidence, rather than deleting its coverage.
    archived = copy.copy(renderer)
    archived.bootstrap_mode = "historical-particles"
    archived.polish_styles = {}
    archived.sample_colors = refined["colors"]
    historical_points = {**fixture["points"], **added["points"], **refined["points"]}
    archived.nodes = [(*n[:3], "#f3df83" if n[0] == "framermotion" else n[3],
                       *n[4:-1], historical_points[n[0]]) for n in nodes]
    historical_rgb = {}
    for key in rgb_fixture["rgb_sha256"]:
        hashes = local_rgb_hashes(archived, key, rgb_fixture)
        assert hashes == rgb_fixture["rgb_sha256"][key], f"Historical source RGB changed: {key}"
        historical_rgb[key] = hashes
    assert sha256(POLISH_RGB_FIXTURE) == POLISH_RGB_SHA256, "Current nine-symbol baseline changed"
    current = json.loads(POLISH_RGB_FIXTURE.read_text())
    assert current["baseline_commit"] == "652f79a761bf714f6a3553e8cd2667a086b31abc"
    assert tuple(current["strict_nine"]) == PRESERVED_KEYS
    assert current["held_for_brand_review"] == ["bootstrap"]
    assert hashlib.sha256(renderer.background.tobytes()).hexdigest() == current["background_rgb_sha256"], "Static background/stars changed"
    preserved_rgb = {}
    for key in (*PRESERVED_KEYS, "bootstrap"):
        node = next(n for n in nodes if n[0] == key)
        preserved_points = added["points"][key] if key == "bootstrap" else node[-1]
        point_hash = hashlib.sha256(json.dumps(preserved_points,separators=(",",":")).encode()).hexdigest()
        assert point_hash == current["points_sha256"][key], f"Preserved ordered points changed: {key}"
        # Preserve the old B evidence without keeping it active in production.
        historical_bootstrap = copy.copy(renderer)
        historical_bootstrap.bootstrap_mode = "historical-particles"
        historical_bootstrap.nodes = [(*n[:-1], added["points"]["bootstrap"] if n[0] == "bootstrap" else n[-1]) for n in nodes]
        hashes = local_rgb_hashes(historical_bootstrap if key == "bootstrap" else renderer, key, current)
        assert hashes == current["rgb_sha256"][key], f"Preserved local source RGB changed: {key}"
        preserved_rgb[key] = hashes
    assert sha256(BOOTSTRAP_RGB_FIXTURE) == BOOTSTRAP_RGB_SHA256, "Eleven-symbol baseline changed"
    unchanged = json.loads(BOOTSTRAP_RGB_FIXTURE.read_text())
    assert unchanged["baseline_commit"] == "fc6240cc1e43401c4ae3801186b96bc78802becb"
    assert unchanged["keys"] == [key for key in KEYS if key != "bootstrap"]
    eleven = {}
    for key in unchanged["keys"]:
        eleven[key] = local_rgb_hashes(renderer, key, unchanged)
        assert eleven[key] == unchanged["rgb_sha256"][key], f"Preserved eleven-symbol RGB changed: {key}"
    return {"inventory": list(NAMES), "positions": list(POSITIONS),
            "minimum_logo_name_gap_px": min(gaps), "logo_masks_sha256": silhouettes,
            "original_fixture_sha256": sha256(FIXTURE), "expansion_fixture_sha256": sha256(EXPANSION_FIXTURE),
            "refinement_fixture_sha256": sha256(REFINEMENT_FIXTURE), "polish_fixture_sha256": sha256(POLISH_FIXTURE),
            "historical_local_rgb_sha256": historical_rgb, "preserved_local_rgb_sha256": preserved_rgb,
            "strict_nine": list(PRESERVED_KEYS), "bootstrap": bootstrap,
            "preserved_eleven_local_rgb_sha256": eleven,
            "intentional_changes": {"bootstrap":"official-path-based outline particles; shared float and pulse"},
            "background_rgb_sha256": current["background_rgb_sha256"],
            "foreground_text_calls": len(texts), "foreground_line_calls": len(lines)}


def verify_bootstrap_outline(renderer):
    assert renderer.bootstrap_mode == "outline-particles", "Solid raster or historical B became active"
    assert BOOTSTRAP_VERSION == "v5.3.8"
    assert BOOTSTRAP_COMMIT == "25aa8cc0b32f0d1a54be575347e6d84b70b1acd7"
    assert sha256(BOOTSTRAP_SVG) == BOOTSTRAP_SVG_SHA256 == "df11d37a123e36a768f2a6064973c4c6ab17d1e3c6501c8bf434ca5c0134c9a2"
    assert blob_sha(BOOTSTRAP_SVG) == "f0189652b88bf6148676918156723948862578a8"
    assert sha256(BOOTSTRAP_PNG) == BOOTSTRAP_PNG_SHA256
    svg = ET.fromstring(BOOTSTRAP_SVG.read_bytes())
    assert (svg.attrib["width"], svg.attrib["height"]) == ("512", "408")
    assert BOOTSTRAP_SIZE == (128,102) and 128*408 == 102*512
    assert BOOTSTRAP_CLEAR_SPACE == 12
    reference = official_bootstrap()
    assert renderer.bootstrap_image.mode == "RGBA" and renderer.bootstrap_image.size == BOOTSTRAP_SIZE
    assert hashlib.sha256(renderer.bootstrap_image.tobytes()).hexdigest() == BOOTSTRAP_RGBA_SHA256
    assert ImageChops.difference(reference,renderer.bootstrap_image).getbbox() is None
    node = next(n for n in renderer.nodes if n[0] == "bootstrap")
    assert (node[5],node[6]) == (985,671)
    from build_bootstrap_outline import build, STYLE
    assert sha256(BOOTSTRAP_OUTLINE) == BOOTSTRAP_OUTLINE_SHA256
    assert build() == BOOTSTRAP_OUTLINE.read_bytes(), "Bootstrap contour derivation changed"
    contour = bootstrap_fixture()
    assert contour["source"]["version"] == BOOTSTRAP_VERSION
    assert contour["source"]["commit"] == BOOTSTRAP_COMMIT
    assert contour["size"] == list(BOOTSTRAP_SIZE)
    assert renderer.bootstrap_style == STYLE == contour["style"]
    assert renderer.sample_colors["bootstrap"] == contour["colors"]
    assert set(contour["colors"]) == {"#c9a4ff", "#ede4ff"}
    assert [p["name"] for p in contour["boundaries"]] == ["outer", "B"]
    assert all(p["boundary_points"] > 200 for p in contour["boundaries"])
    assert [list(p) for p in node[-1]] == contour["points"]
    box = (910,605,1060,735)
    for phase in (0, math.pi/2, math.pi, 3*math.pi/2, math.tau):
        expected = Image.new("RGB", SIZE)
        renderer.polished_particles(expected,node,8,phase,False,style=renderer.bootstrap_style)
        actual = renderer.foreground(Image.new("RGB",SIZE),phase)
        assert ImageChops.difference(actual.crop(box),expected.crop(box)).getbbox() is None, "Bootstrap is not the expected particle layer"
    neutral = renderer.foreground(Image.new("RGB",SIZE),0,True).crop((921,620,1049,722)).convert("L")
    lit = sum(neutral.histogram()[80:])
    assert 200 < lit < 128*102*.30, "Bootstrap outline missing or solid fill restored"
    return {"source_version": BOOTSTRAP_VERSION, "source_commit": BOOTSTRAP_COMMIT,
            "svg_sha256": BOOTSTRAP_SVG_SHA256, "png_sha256": BOOTSTRAP_PNG_SHA256,
            "rgba_sha256": BOOTSTRAP_RGBA_SHA256, "intrinsic_size": [512,408],
            "render_size": list(BOOTSTRAP_SIZE), "anchor": [985,671],
            "outline_sha256": BOOTSTRAP_OUTLINE_SHA256, "lit_outline_pixels": lit,
            "clear_space_px": BOOTSTRAP_CLEAR_SPACE,
            "rendering_contract": "12 outline-particle symbols; Bootstrap is an unofficial adaptation",
            "shared_float_and_pulse": True}


def local_rgb_hashes(renderer, key, fixture):
    nodes = renderer.nodes
    local = copy.copy(renderer)
    local.nodes = [(*n[:5], *((200,300) if n[0] == key else (-10000,-10000)), n[-1]) for n in nodes]
    layers = [local.foreground(Image.new("RGB", SIZE), 0, True)]
    layers += [local.foreground(Image.new("RGB", SIZE), p) for p in fixture["phases"]]
    return [hashlib.sha256(layer.crop(fixture["crop"]).tobytes()).hexdigest() for layer in layers]


def verify_assets(renderer, assets):
    png, gif = (assets/f"constellation-frameworks.{ext}" for ext in ("png", "gif"))
    with Image.open(png) as image:
        image.verify()
    poster = Image.open(png).convert("RGB")
    assert poster.size == SIZE
    assert ImageChops.difference(poster, renderer.render(0, freeze=True)).getbbox() is None, "PNG content mismatch"
    assert gif.stat().st_size <= 3_500_000, "GIF exceeds approved preferred size"

    for i in range(len(NAMES)):
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
    bootstrap_box = (910,605,1060,735)
    masks = [f.crop(bootstrap_box).convert("L").point(lambda v: 255 if v > 80 else 0) for f in source]
    bootstrap_errors = [distance(a.crop(bootstrap_box),b.crop(bootstrap_box),mask)
                        for a,b,mask in zip(source,decoded,masks)]
    assert max(bootstrap_errors) < 4, "Bootstrap particle GIF color fidelity degraded"
    assert ImageChops.difference(source[0].crop(bootstrap_box),source[16].crop(bootstrap_box)).getbbox() is not None, "Bootstrap particles frozen"
    assert ImageChops.difference(decoded[0].crop(bootstrap_box),decoded[16].crop(bootstrap_box)).getbbox() is not None, "Decoded Bootstrap particles frozen"
    for width in (375,320):
        small = poster.resize((width,round(SIZE[1]*width/SIZE[0])),Image.Resampling.LANCZOS)
        for node in renderer.nodes:
            _,name,_,_,_,x,y,_ = node
            box = ImageDraw.Draw(poster).textbbox((x,y+LABEL_OFFSET),name,font=renderer.font(LABEL_SIZE,True),anchor="mm")
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
            "bootstrap_particle_quantization_mean_abs_rgb_max": max(bootstrap_errors),
            "bootstrap_source_and_decoded_animated": True,
            "sha256": {p.name: sha256(p) for p in (png,gif)}}


def verify_protected():
    actual = {p: blob_sha(ROOT/p) for p in PROTECTED_BLOBS}
    assert actual == PROTECTED_BLOBS, "Frozen Languages/Tools bytes changed"
    return actual


def verify_negative_controls(renderer):
    """Fail closed for inventory, fixture drift, empty contours and missing masks."""
    import framework_orbits as orbits
    rejected = []

    def reject(name, operation):
        try:
            operation()
        except (AssertionError, ValueError):
            rejected.append(name)
        else:
            raise AssertionError(f"Negative control accepted: {name}")

    bad = copy.copy(renderer)
    bad.nodes = [*renderer.nodes[:-1]]
    reject("missing technology", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.nodes = list(renderer.nodes)
    n = list(bad.nodes[9]); n[1] = "FramerNotion"; bad.nodes[9] = tuple(n)
    reject("incorrect technology identity", lambda: verify_structure(bad))
    for index, name in ((5,"WebAssembly"),(11,"Rust crate"),(11,"SpringBoot")):
        bad = copy.copy(renderer)
        bad.nodes = list(renderer.nodes)
        n = list(bad.nodes[index]); n[1] = name; bad.nodes[index] = tuple(n)
        reject("removed technology restored: "+name, lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.nodes = list(renderer.nodes)
    n = list(bad.nodes[6]); n[-1] = []; bad.nodes[6] = tuple(n)
    reject("empty added contour", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.keep = Image.new("L", SIZE, 255)
    reject("disabled protection mask", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.sample_colors = {**renderer.sample_colors, "react": ["#ffffff"]*1000}
    reject("preserved source RGB recolored", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.polish_styles = copy.deepcopy(renderer.polish_styles)
    bad.polish_styles["googleappsscript"]["radius"] = .2
    reject("unreviewed GAS particle radius", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.nodes = list(renderer.nodes)
    n = list(bad.nodes[9])
    retained = [p for p in n[-1] if p[0] < 45]
    n[-1] = [retained[i % len(retained)] for i in range(1000)]
    bad.nodes[9] = tuple(n)
    reject("Motion dot component removed", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.nodes = list(renderer.nodes)
    n = list(bad.nodes[8]); n[-1] = list(n[-1]); n[-1][0] = (0,0)
    bad.nodes[8] = tuple(n)
    reject("Bootstrap contour changed", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.bootstrap_mode = "historical-particles"
    reject("previous particle B restored", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.bootstrap_mode = "official-svg-raster"
    reject("solid official Bootstrap raster restored", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    bad.bootstrap_image = renderer.bootstrap_image.copy()
    bad.bootstrap_image.putpixel((64,51),(0,255,0,255))
    reject("archived official Bootstrap reference recolored", lambda: verify_bootstrap_outline(bad))
    bad = copy.copy(renderer)
    bad.background = renderer.background.copy()
    bad.background.putpixel((50,50),(255,255,255))
    reject("unexpected distant-star/background change", lambda: verify_structure(bad))
    bad = copy.copy(renderer)
    def footer_restored(image, phase, freeze=False):
        image = renderer.foreground(image, phase, freeze)
        ImageDraw.Draw(image).line((43, SIZE[1]-39, 1158, SIZE[1]-39), fill=(29,67,93))
        return image
    bad.foreground = footer_restored
    reject("Frameworks footer restored", lambda: verify_structure(bad))
    with tempfile.TemporaryDirectory(prefix="contour-negative-") as directory:
        for attr, source in (("FIXTURE", FIXTURE), ("EXPANSION_FIXTURE", EXPANSION_FIXTURE),
                             ("REFINEMENT_FIXTURE", REFINEMENT_FIXTURE),
                             ("POLISH_FIXTURE", POLISH_FIXTURE)):
            tampered = Path(directory)/source.name
            data = json.loads(source.read_text())
            key = next(iter(data["points"]))
            data["points"][key][0][0] += .5
            tampered.write_text(json.dumps(data))
            with patch.object(orbits, attr, tampered):
                reject(attr+" coordinate drift", load_renderer)
        for name, content in (
            ("modified official SVG", BOOTSTRAP_SVG.read_bytes().replace(b"#9013fe",b"#ff0000")),
            ("wrong Bootstrap asset", b'<svg xmlns="http://www.w3.org/2000/svg"><text>B</text></svg>'),
        ):
            tampered = Path(directory)/"bootstrap.svg"
            tampered.write_bytes(content)
            with patch.object(orbits,"BOOTSTRAP_SVG",tampered):
                reject(name,orbits.official_bootstrap)
        tampered = Path(directory)/"bootstrap.png"
        tampered.write_bytes(BOOTSTRAP_PNG.read_bytes()+b"modified")
        with patch.object(orbits,"BOOTSTRAP_PNG",tampered):
            reject("modified official lossless raster",orbits.official_bootstrap)
        tampered = Path(directory)/"bootstrap-outline.json"
        data = json.loads(BOOTSTRAP_OUTLINE.read_text())
        data["points"][0][0] += .5
        tampered.write_text(json.dumps(data))
        with patch.object(orbits,"BOOTSTRAP_OUTLINE",tampered):
            reject("Bootstrap outline fixture drift",load_renderer)
        protected_root = Path(directory)/"protected"
        for path in PROTECTED_BLOBS:
            target = protected_root/path
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/path).read_bytes())
        target.write_bytes(target.read_bytes()+b"modified")
        with patch.object(sys.modules[__name__],"ROOT",protected_root):
            reject("modified protected Languages/Tools asset",verify_protected)
    return {"rejected": rejected, "count": len(rejected)}


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
    result = {"structure":verify_structure(renderer),"animation":verify_assets(renderer,args.assets),
              "palette": verify_palette_tables(args.assets/"constellation-frameworks.gif"),
              "negative_controls": verify_negative_controls(renderer)}
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
