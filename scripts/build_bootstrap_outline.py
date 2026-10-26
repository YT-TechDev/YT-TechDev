#!/usr/bin/env python3
"""Freeze a particle adaptation of the pinned Bootstrap outer shape and B."""
from __future__ import annotations

import hashlib
import io
import json
import random
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg
from PIL import Image, ImageChops, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'framework_brand_sources/bootstrap-logo.svg'
DESTINATION = ROOT / 'bootstrap_outline_contours.json'
SOURCE_SHA256 = 'df11d37a123e36a768f2a6064973c4c6ab17d1e3c6501c8bf434ca5c0134c9a2'
STYLE = {'scale': 3, 'radius': .78, 'accent_radius': 1.25,
         'accent_stride': 8, 'support_radius': 5}


def build():
    source = SOURCE.read_bytes()
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError('Bootstrap reference SVG changed')
    svg = ET.fromstring(source)
    paths = svg.findall('{http://www.w3.org/2000/svg}path')
    if len(paths) != 2:
        raise ValueError('Expected the Bootstrap outer shape and B')
    choices, boundaries = [], []
    for name, path, color in zip(('outer', 'B'), paths, ('#c9a4ff', '#ede4ff')):
        # Extract exact source path geometry without mutating the original SVG.
        # Neutral fills are contour masks only, never production logo artwork.
        mask_svg = ET.Element('svg', xmlns='http://www.w3.org/2000/svg',
                              viewBox='0 0 512 408', width='512', height='408')
        attrs = {'d': path.attrib['d'], 'fill': 'white'}
        if 'stroke' in path.attrib:
            attrs['stroke'] = 'white'
        ET.SubElement(mask_svg, 'path', attrs)
        image = Image.open(io.BytesIO(cairosvg.svg2png(
            bytestring=ET.tostring(mask_svg), output_width=256,
            output_height=204))).convert('RGBA')
        image = ImageOps.expand(image, border=8, fill=(0,0,0,0))
        mask = image.getchannel('A').point(lambda v: 255 if v > 160 else 0)
        edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(3)))
        w,h = edge.size
        part = [((x-w/2)/2, (y-h/2)/2, color)
                for y in range(h) for x in range(w) if edge.getpixel((x,y))]
        boundaries.append({'name': name, 'color': color, 'boundary_points': len(part)})
        choices.extend(part)
    random.Random(847491 + sum(map(ord,'bootstrap'))).shuffle(choices)
    selected = [choices[i % len(choices)] for i in range(1000)]
    data = {'version': 1, 'baseline_commit': '47eabd78127a72cb6cf407af7ee044c8ef6ab9d8',
            'source': {'file': SOURCE.relative_to(ROOT).as_posix(),
                       'sha256': SOURCE_SHA256, 'version': 'v5.3.8',
                       'commit': '25aa8cc0b32f0d1a54be575347e6d84b70b1acd7'},
            'interpretation': 'User-requested unofficial outline-particle adaptation. '
              'Official brace-shaped outer path and B, including both counters. '
              'Light violet outer contour and pale B for navy contrast. '
              'No solid fill, gradient, shadow or official-raster compositing. '
              'Original reference SVG remains unchanged; this is not an unmodified official logo.',
            'size': [128,102], 'boundaries': boundaries, 'style': STYLE,
            'points': [[x,y] for x,y,_ in selected],
            'colors': [color for _,_,color in selected]}
    return (json.dumps(data,separators=(',',':'))+'\n').encode()


if __name__ == '__main__':
    DESTINATION.write_bytes(build())
    print(DESTINATION.name,hashlib.sha256(DESTINATION.read_bytes()).hexdigest())
