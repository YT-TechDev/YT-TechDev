#!/usr/bin/env python3
"""Derive the reviewed Motion contour; keep all historical fixtures immutable."""
from __future__ import annotations

import hashlib
import io
import json
import random
from pathlib import Path

import cairosvg
from PIL import Image, ImageChops, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
DESTINATION = ROOT / 'framework_polish_contours.json'
SOURCE = ROOT / 'framework_brand_sources/motion-symbol.svg'
STYLES = {key: {'scale': 3, 'radius': .78, 'accent_radius': 1.25,
                'accent_stride': 8, 'support_radius': 5}
          for key in ('framermotion', 'googleappsscript')}


def build():
    svg = SOURCE.read_bytes()
    image = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg,
                       output_width=768, output_height=768))).convert('RGBA')
    image = image.crop(image.getchannel('A').getbbox())
    image.thumbnail((300, 108), Image.Resampling.LANCZOS)
    image = ImageOps.expand(image, border=8, fill=(0, 0, 0, 0))
    mask = image.getchannel('A').point(lambda v: 255 if v > 160 else 0)
    edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(3)))
    w, h = image.size
    choices = [((x-w/2)/2, (y-h/2)/2) for y in range(h) for x in range(w)
               if edge.getpixel((x, y))]
    random.Random(847491 + sum(map(ord, 'framermotion'))).shuffle(choices)
    points = [choices[i % len(choices)] for i in range(1000)]
    data = {'version': 1,
            'baseline_commit': '652f79a761bf714f6a3553e8cd2667a086b31abc',
            'interpretation': 'Unofficial particle outline of the Motion library symbol. '
              'Exact maintainer-supplied path geometry; dark source ink is mapped '
              'to library yellow #fef62a on navy. No enclosing tile. '
              'Framer Motion remains the historical visible label. '
              'Apps Script uses its unchanged four-color coordinates and five circle rims.',
            'sources': {'framermotion': {
                'file': SOURCE.relative_to(ROOT).as_posix(),
                'sha256': hashlib.sha256(svg).hexdigest(),
                'reference': 'https://github.com/motiondivision/motion/discussions/3326',
                'identity_reference': 'https://motion.dev/magazine/framer-motion-is-now-independent-introducing-motion',
                'geometry_crosscheck': 'https://github.com/motiondivision/motion-vscode/blob/main/images/logo.png',
                'crosscheck_blob': '365221b61a343781d08fcac6c426886f74ad0b70',
                'source_ink': '#0c1012', 'library_yellow': '#fef62a',
                'max_size': [150,54], 'components': 4,
                'unique_boundary_points': len(choices)}},
            'points': {'framermotion': points},
            'colors': {'framermotion': ['#fef62a']*1000},
            'styles': STYLES,
            'bootstrap': 'Unchanged: official no-modification guidance blocks publishing candidates.'}
    return (json.dumps(data, separators=(',', ':'))+'\n').encode()


if __name__ == '__main__':
    DESTINATION.write_bytes(build())
    print(DESTINATION.name, hashlib.sha256(DESTINATION.read_bytes()).hexdigest())
