#!/usr/bin/env python3
"""Inspect Station Grid content, historical pixels, real GIF frames and guards."""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageChops, ImageDraw, ImageStat

import render_sections as sections
import tools_observatory as tools

ROOT = Path(__file__).resolve().parents[1]
KEYS = ('postgresql', 'docker', 'git', 'cloudflare', 'linux', 'vscode',
        'blender', 'chatgpt', 'claude')
NAMES = ('PostgreSQL', 'Docker', 'Git', 'Cloudflare', 'Linux', 'VS Code',
         'Blender', 'ChatGPT', 'Claude')
COLORS = ('#a8d4ff', '#8dd9ff', '#ffaf8f', '#ffd49a', '#eed4b5', '#a2c8ff',
          '#fbc392', '#aeefd8', '#ffbfa4')
POSITIONS = tuple((x, y) for y in (222, 444, 666) for x in (215, 600, 985))
PROTECTED_BLOBS = {
    'assets/constellation-languages.gif': '9f5a84ddae394f44992215c59a4271e37a932fb4',
    'assets/constellation-languages.png': '50ae288464fd4e9de3db5bc69d3b479ebf88b385',
    'assets/constellation-frameworks.gif': '4a0008388dd93fe6c9d510c4a4769ccdcc4c9f55',
    'assets/constellation-frameworks.png': '94318a7f67ba7211c04b5605922fe8ab1590fb06',
}
ORIGINAL_BLOB = 'b71675893426c6e1797b25c985e4c584ef87528c'
REFERENCE = ROOT / 'scripts/tools_station_reference.png'
REFERENCE_SHA256 = '7618734c27cee4d87602eb3505c15f88fd3ddc00b6f8f5db67cb72a451527eec'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_sha(path):
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def load_renderer():
    return tools.StationGrid(sections.SECTIONS['tools'])


def distance(a, b, mask=None):
    return sum(ImageStat.Stat(ImageChops.difference(a, b), mask=mask).mean) / 3


def verify_protected(root=ROOT):
    actual = {p: blob_sha(root / p) for p in PROTECTED_BLOBS}
    assert actual == PROTECTED_BLOBS, 'Protected Languages/Frameworks assets changed'
    return actual


def historical_pixels(renderer):
    """Re-extract literal source pixels from an independently hashed Git object."""
    data = subprocess.check_output(['git', 'cat-file', 'blob', ORIGINAL_BLOB], cwd=ROOT)
    assert hashlib.sha256(data).hexdigest() == renderer.fixture['original_asset_sha256']
    source = Image.open(io.BytesIO(data)).convert('RGB')
    originals = json.loads((ROOT / 'data/icon-paths.json').read_text())
    extras = json.loads((ROOT / 'data/supplemental-icons.json').read_text())['paths']
    counts = {}
    for node in renderer.nodes:
        key = node['key']
        assert hashlib.sha256(sections.glyph_svg(key, originals, extras).encode()).hexdigest() == node['source_svg_sha256']
        x, y = node['historical_anchor']
        rgb = tuple(round(int(node['color'][j:j + 2], 16) * .96) for j in (1, 3, 5))
        literal = [[px, py, *rgb] for py in range(-62, 63) for px in range(-82, 83)
                   if source.getpixel((x + px, y + py)) == rgb]
        assert literal == node['pixels'], f'{key}: frozen geometry differs from committed pixels'
        assert hashlib.sha256(json.dumps(literal, separators=(',', ':')).encode()).hexdigest() == node['raster_sha256']
        assert len(literal) > 200, f'{key}: empty/incomplete symbol'
        counts[key] = len(literal)
    return counts


def verify_structure(renderer):
    nodes = renderer.nodes
    assert tuple(n['key'] for n in nodes) == KEYS, 'Nine identities/order changed'
    assert tuple(n['label'] for n in nodes) == NAMES, 'Labels changed'
    assert tuple(n['color'] for n in nodes) == COLORS, 'Colors changed'
    assert tuple(n['anchor'] for n in nodes) == POSITIONS, '3x3 anchors changed'
    assert tuple(n['annotation'] for n in nodes) == (None,) * 7 + ('AI TOOL', 'AI TOOL')
    assert renderer.cfg['height'] == 900 and renderer.cfg['columns'] == (215, 600, 985)
    assert renderer.cfg['rows'] == (222, 444, 666)
    assert tools.SUPPORTS == (407, 793) and len(tools.SIGNALS) == 4
    expected_text = [((43, 27), 'YT-TECHDEV   /   SKILL CONSTELLATION', 20, True, None),
                     ((43, 59), '03  /  TOOLS & PLATFORMS', 25, True, None),
                     ((43, 99), 'INSTRUMENTS, INFRASTRUCTURE & AI ASSISTANTS', 14, False, None),
                     ((43, 854), 'DUST  →  ORBITS  →  OBSERVATORY', 17, False, None),
                     ((1157, 854), 'YT-TECHDEV', 17, False, 'ra')]
    for i, name in enumerate(NAMES):
        x, y = POSITIONS[i]
        expected_text.append(((x, y + 95), name, 38, True, 'mm'))
        if i >= 7:
            expected_text.append(((x, y + 130), 'AI TOOL', 20, True, 'mm'))
    assert [t[:5] for t in renderer.texts] == expected_text, 'Header/labels/annotations/footer changed'
    d = ImageDraw.Draw(Image.new('L', tools.SIZE))
    text_boxes = []
    gaps = []
    for xy, text, size, bold, anchor, _ in renderer.texts:
        box = d.textbbox(xy, text, font=renderer.font(size, bold), anchor=anchor)
        l, t, r, b = box
        assert 0 <= l < r < 1200 and 0 <= t < b < 900, f'Text clipped: {text}'
        text_boxes.append(box)
    for i, a in enumerate(text_boxes):
        for b in text_boxes[i + 1:]:
            assert a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1], 'Text collision'
    for n in nodes:
        x, y = n['anchor']
        xs, ys = [p[0] for p in n['pixels']], [p[1] for p in n['pixels']]
        logo_box = (x + min(xs), y + min(ys), x + max(xs), y + max(ys))
        name_box = d.textbbox((x, y + 95), n['label'], font=renderer.font(38, True), anchor='mm')
        assert x - 170 <= name_box[0] < name_box[2] <= x + 170, 'Name leaves its column'
        gap = name_box[1] - logo_box[3]
        assert gap >= 19, f'Approved 19px logo/name clearance lost: {n["key"]}'
        gaps.append(gap)
        assert 43 < logo_box[0] < logo_box[2] < 1157 and 141 < logo_box[1] < logo_box[3] < 823
        for b in text_boxes:
            assert logo_box[2] < b[0] or b[2] < logo_box[0] or logo_box[3] < b[1] or b[3] < logo_box[1], 'Logo/text collision'
    return {'inventory': list(NAMES), 'positions': POSITIONS, 'minimum_logo_name_gap': min(gaps),
            'historical_pixel_counts': historical_pixels(renderer)}


def verify_symbols(poster, renderer):
    for n in renderer.nodes:
        x, y = n['anchor']
        actual = [[px, py, *poster.getpixel((x + px, y + py))]
                  for py in range(-62, 63) for px in range(-82, 83)
                  if max(poster.getpixel((x + px, y + py))) > 100]
        assert actual == n['pixels'], f'{n["key"]}: actual silhouette/RGB changed'


def verify_masks(renderer):
    expected = Image.new('L', tools.SIZE)
    d = ImageDraw.Draw(expected)
    for b in renderer.boxes:
        d.rectangle(b, fill=255)
    assert ImageChops.difference(expected, renderer.protected).getbbox() is None, 'Fixed mask changed'
    assert ImageChops.multiply(renderer.structure.getchannel('A'), expected).getbbox() is None, 'Station enters protected core'
    probe = Image.new('RGBA', tools.SIZE, (150, 120, 90, 180))
    assert ImageChops.multiply(renderer.protect(probe).getchannel('A'), expected).getbbox() is None, 'Protection disabled'
    for n in range(48):
        signal = renderer.signal_layer(math.tau * n / 48)
        assert ImageChops.multiply(signal.getchannel('A'), expected).getbbox() is None, 'Signal enters protected core'
    # Structure is subordinate in actual final RGB, including its antialiasing.
    assert renderer.structure.getchannel('A').getextrema()[1] <= 140
    for carrier in range(4):
        for n in range(8):
            assert renderer.signal_layer(math.tau * n / 8, only=carrier).getchannel('A').getextrema()[1] > 0, f'Carrier {carrier} fully occluded'


def verify_reference(renderer):
    """Exact approved A, except the removed study stamp and one carrier fix."""
    assert sha256(REFERENCE) == REFERENCE_SHA256, 'Approved A reference changed'
    reference = Image.open(REFERENCE).convert('RGB')
    production = renderer.render(0)
    allowed = Image.new('L', tools.SIZE)
    draw = ImageDraw.Draw(allowed)
    draw.rectangle((1020, 24, 1165, 52), fill=255)  # DESIGN STUDY / A only.
    draw.rectangle((303, 126, 427, 166), fill=255)  # Relocated masked top signal.
    diff = ImageChops.difference(reference, production)
    assert ImageChops.multiply(diff, ImageChops.invert(allowed).convert('RGB')).getbbox() is None, 'Production deviates from approved A outside bounded exceptions'
    return {'reference_sha256': REFERENCE_SHA256, 'outside_allowed_regions_changed_pixels': 0,
            'exceptions': ['remove DESIGN STUDY / A stamp', 'move fully occluded top-deck carrier from x=165 to x=365']}


def verify_palette(path):
    data = path.read_bytes()
    assert data[:6] in (b'GIF89a', b'GIF87a') and data[10] & 128
    length = 3 * 2 ** ((data[10] & 7) + 1)
    table = data[13:13 + length]
    position, count = 13 + length, 0

    def skip_blocks(p):
        while data[p]:
            p += data[p] + 1
        return p + 1

    while data[position] != 59:
        if data[position] == 33:
            position = skip_blocks(position + 2)
        else:
            assert data[position] == 44, 'Invalid GIF block'
            flags = data[position + 9]
            position += 10
            frame_table = table
            if flags & 128:
                size = 3 * 2 ** ((flags & 7) + 1)
                frame_table = data[position:position + size]
                position += size
            assert frame_table == table, 'GIF palette shimmer'
            position = skip_blocks(position + 1)
            count += 1
    assert count == 48
    return {'image_blocks': count, 'common_palette': True, 'sha256': hashlib.sha256(table).hexdigest()}


def decode_gif(path):
    frames, durations = [], []
    with Image.open(path) as gif:
        assert gif.size == (1200, 900) and gif.n_frames == 48, 'GIF geometry/count'
        assert gif.info.get('loop') == 0, 'Infinite loop metadata missing'
        for i in range(48):
            gif.seek(i)
            assert gif.info.get('duration') == 160, 'Wrong frame timing'
            frame = gif.convert('RGB')
            frame.load()
            frames.append(frame)
            durations.append(gif.info['duration'])
    assert sum(durations) == 7680
    return frames


def verify_poster(poster, renderer):
    verify_symbols(poster, renderer)
    assert ImageChops.difference(poster, renderer.render(0)).getbbox() is None, 'PNG text/composition mismatch'


def verify_assets(renderer, assets):
    png, gif = assets / 'constellation-tools.png', assets / 'constellation-tools.gif'
    with Image.open(png) as poster:
        poster.load()
        assert poster.size == (1200, 900) and poster.mode == 'RGB'
        poster = poster.copy()
    verify_poster(poster, renderer)
    verify_masks(renderer)
    assert ImageChops.difference(renderer.render(0), renderer.render(math.tau)).getbbox() is None, 'Rendered period does not close'
    for i in range(4):
        assert tools.signal_state(i, 0) == tools.signal_state(i, math.tau)
        assert tools.navigation_strength(i, 0) == tools.navigation_strength(i, math.tau)
    decoded = decode_gif(gif)
    palette = tools.global_palette(renderer)
    static_mask = ImageChops.invert(renderer.motion_mask())
    assert static_mask.histogram()[255] > 1_000_000
    max_error = 0
    for i, frame in enumerate(decoded):
        source = renderer.render(math.tau * i / 48)
        expected = source.quantize(palette=palette, dither=Image.Dither.NONE).convert('RGB')
        assert ImageChops.difference(frame, expected).getbbox() is None, f'GIF frame {i} content mismatch'
        verify_symbols(frame, renderer)
        delta = ImageChops.difference(frame, decoded[0])
        assert ImageChops.multiply(delta, static_mask.convert('RGB')).getbbox() is None, 'GIF background variation'
        max_error = max(max_error, distance(source, frame))
    steps = [distance(decoded[i], decoded[(i + 1) % 48]) for i in range(48)]
    assert min(steps) > 0, 'Frozen transition'
    assert steps[-1] <= max(steps[:-1]) * 1.25, 'Encoded loop jumps'
    assert max_error < 2, 'GIF color fidelity degraded'
    assert gif.stat().st_size <= 2_500_000, 'Preferred GIF budget exceeded; review required'
    # Real downsampled content: quantify each name and symbol, then inspect previews.
    for width in (375, 320):
        small = poster.resize((width, round(900 * width / 1200)), Image.Resampling.LANCZOS)
        scale = width / 1200
        for n in renderer.nodes:
            x, y = n['anchor']
            label = tuple(round(v * scale) for v in (x - 170, y + 75, x + 170, y + 118))
            logo = tuple(round(v * scale) for v in (x - 82, y - 62, x + 83, y + 63))
            for kind, box in (('name', label), ('symbol', logo)):
                crop = small.crop(box).convert('L')
                assert crop.getextrema()[1] > 90 and sum(crop.histogram()[60:]) > 10, f'{width}px {n["key"]} {kind} disappears'
    return {'size': [1200, 900], 'frames': 48, 'duration_ms': 160, 'total_ms': 7680,
            'loop': 0, 'gif_bytes': gif.stat().st_size, 'static_pixels': static_mask.histogram()[255],
            'seam_rgb_delta': steps[-1], 'interior_max_rgb_delta': max(steps[:-1]),
            'max_whole_frame_rgb_error': max_error, 'protected_symbol_rgb_error': 0,
            'png_sha256': sha256(png), 'gif_sha256': sha256(gif),
            'resized_previews': [375, 320], 'real_device_playback': 'UNVERIFIED'}


def verify_negative_controls(renderer, assets):
    rejected = []

    def reject(name, action):
        try:
            action()
        except (AssertionError, ValueError):
            rejected.append(name)
        else:
            raise AssertionError(f'Negative control accepted: {name}')

    for name, mutate in (
        ('missing technology', lambda r: r.nodes.pop()),
        ('incorrect symbol', lambda r: r.nodes[0].update(pixels=r.nodes[1]['pixels'])),
        ('wrong label', lambda r: r.nodes[0].update(label='Postgres')),
        ('AI TOOL removed', lambda r: r.nodes[-1].update(annotation=None)),
        ('wrong footer', lambda r: r.texts.__setitem__(3, ((43, 853), 'OLD FOOTER', 17, True, None, (1, 2, 3)))),
    ):
        changed = copy.copy(renderer)
        changed.nodes = copy.deepcopy(renderer.nodes)
        changed.texts = list(renderer.texts)
        mutate(changed)
        reject(name, lambda: verify_structure(changed))
    disabled = copy.copy(renderer)
    disabled.protect = lambda layer: layer
    reject('mask disabled', lambda: verify_masks(disabled))
    hidden = list(tools.SIGNALS)
    hidden[2] = (165, 146, 42, 0)
    with patch.object(tools, 'SIGNALS', tuple(hidden)):
        reject('fully occluded signal carrier', lambda: verify_masks(renderer))
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        fixture = root / 'particles.json'
        fixture.write_bytes(tools.FIXTURE.read_bytes().replace(b'PostgreSQL', b'PostgreSQX', 1))
        reject('changed frozen fixture', lambda: tools.load_fixture(fixture))
        altered = Image.open(assets / 'constellation-tools.png').convert('RGB')
        p = renderer.nodes[0]['pixels'][0]
        altered.putpixel((215 + p[0], 222 + p[1]), (0, 0, 0))
        reject('changed actual symbol pixel', lambda: verify_symbols(altered, renderer))
        original = Image.open(assets / 'constellation-tools.png').convert('RGB')
        for name, box in (
            ('corrupted actual label', (83, 299, 346, 336)),
            ('removed actual AI TOOL', (541, 782, 660, 810)),
            ('corrupted actual footer', (43, 854, 400, 880)),
        ):
            changed = original.copy()
            changed.paste((0, 0, 0), box)
            reject(name, lambda: verify_poster(changed, renderer))
        raw = (assets / 'constellation-tools.gif').read_bytes()
        timing = root / 'timing.gif'
        timing.write_bytes(raw.replace(b'\x21\xf9\x04\x04\x10\x00', b'\x21\xf9\x04\x04\x11\x00', 1))
        assert timing.read_bytes() != raw, 'Timing control did not mutate'
        reject('wrong frame timing', lambda: decode_gif(timing))
        loop = root / 'loop.gif'
        assert b'NETSCAPE2.0' in raw
        loop.write_bytes(raw.replace(b'NETSCAPE2.0', b'NOTSCAPE2.0', 1))
        reject('missing loop metadata', lambda: decode_gif(loop))
        for p in PROTECTED_BLOBS:
            path = root / p
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / p).read_bytes())
        (root / 'assets/constellation-frameworks.png').write_bytes(b'corrupt')
        reject('modified protected asset', lambda: verify_protected(root))
    # Test the actual static-field predicate independently of render equality.
    a, b = renderer.render(0), renderer.render(0).copy()
    b.putpixel((1190, 890), (255, 255, 255))
    mask = ImageChops.invert(renderer.motion_mask()).convert('RGB')
    reject('background variation', lambda: assert_equal_masked(a, b, mask))
    return rejected


def assert_equal_masked(a, b, mask):
    assert ImageChops.multiply(ImageChops.difference(a, b), mask).getbbox() is None


def verify_determinism(assets):
    expected = {ext: sha256(assets / f'constellation-tools.{ext}') for ext in ('png', 'gif')}
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / 'checkout'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        selected = {f'assets/constellation-tools.{ext}' for ext in ('png', 'gif')}

        def unselected():
            return {str(p.relative_to(root)): sha256(p) for p in root.rglob('*')
                    if p.is_file() and str(p.relative_to(root)) not in selected}

        frozen = unselected()
        env = dict(os.environ, PYTHONPYCACHEPREFIX=str(Path(directory) / 'pycache'))
        for iteration in range(2):
            subprocess.run([sys.executable, 'scripts/render_sections.py', '--only', 'tools'],
                           cwd=root, env=env, check=True, stdout=subprocess.PIPE)
            actual = {ext: sha256(root / f'assets/constellation-tools.{ext}') for ext in ('png', 'gif')}
            assert actual == expected, f'Canonical generation {iteration + 1} differs'
            assert unselected() == frozen, 'Tools CLI modified unselected files'
    return {'canonical_runs': 2, 'sha256': expected, 'unselected_files_unchanged': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, default=ROOT / 'assets')
    parser.add_argument('--determinism', action='store_true')
    parser.add_argument('--protected', action='store_true', help='Assert the frozen Languages/Frameworks blobs for this Tools phase')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    renderer = load_renderer()
    result = {'structure': verify_structure(renderer), 'approved_reference': verify_reference(renderer),
              'animation': verify_assets(renderer, args.assets),
              'palette': verify_palette(args.assets / 'constellation-tools.gif'),
              'negative_controls': verify_negative_controls(renderer, args.assets)}
    if args.protected:
        result['protected_blobs'] = verify_protected()
    if args.determinism:
        result['determinism'] = verify_determinism(args.assets)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    print('Station Grid content, historical symbols, masks, timing and loop: PASS')


if __name__ == '__main__':
    main()
