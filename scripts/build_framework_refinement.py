#!/usr/bin/env python3
"""Freeze only the three reviewed vector-derived particle contours, offline.

Historical fixtures and the shared sampler are never rewritten. Visible color
boundaries are extracted AFTER SVG occlusion; hidden overlapping arms do not
produce invented lines. Production reads the resulting fixed coordinates.
"""
from __future__ import annotations

import hashlib
import io
import json
import random
from pathlib import Path

import cairosvg
from PIL import Image, ImageChops, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
DESTINATION = ROOT / "framework_refinement_contours.json"
SPECS = {
    "vue": ("vue.svg", (140, 121), ("#42b883", "#35495e"),
            {"#35495e": "#80c7c6"}, "https://vuejs.org/"),
    "googleappsscript": ("googleappsscript.svg", (150, 120),
            ("#ea4335", "#fbbc04", "#34a853", "#4285f4", "#ffffff"), {},
            "https://developers.google.com/workspace/extend"),
    "prisma": ("prisma-legacy.svg", (98, 120), ("#ffffff",),
            {"#ffffff": "#edf3ff"},
            "https://github.com/prisma/presskit/blob/13ee1c557d3dad9c036cdb1e2607c33ea90c2544/Assets/Prisma-LightSymbol.svg"),
}


def rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))


def build():
    data = {"version": 1, "provenance": {
        "date": "2026-10-26", "samples_per_icon": 1000, "seed": 847491,
        "method": "Visible vector color-boundary sampling at 2x; half-pixel coordinates; fixed shuffle; no shared sampler changes.",
        "interpretation": "Unofficial particle adaptations. Vue inner navy is lifted to teal for contrast. Apps Script retains the actual four arms and five white circular components. Prisma uses the requested historic faceted mark, not the August 2026 rebrand.",
        "prisma_current_presskit_commit": "664e85e9950fa431d2e025202aeda758ff28d5ef",
        "prisma_legacy_presskit_commit": "13ee1c557d3dad9c036cdb1e2607c33ea90c2544",
    }, "sources": {}, "points": {}, "colors": {}}
    for key, (name, size, colors, substitutions, reference) in SPECS.items():
        source = ROOT / "framework_brand_sources" / name
        svg = source.read_bytes()
        image = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg,
                            output_width=768, output_height=768))).convert("RGBA")
        image = image.crop(image.getchannel("A").getbbox())
        image.thumbnail((size[0]*2, size[1]*2), Image.Resampling.LANCZOS)
        image = ImageOps.expand(image, border=8, fill=(0, 0, 0, 0))
        w, h = image.size
        # Classify against actual source fills, excluding antialiased fringe.
        masks = {c: Image.new("L", image.size) for c in colors}
        for y in range(h):
            for x in range(w):
                r, g, b, a = image.getpixel((x, y))
                if a > 160:
                    c = min(colors, key=lambda c: sum((v-t)**2 for v,t in zip((r,g,b), rgb(c))))
                    masks[c].putpixel((x, y), 255)
        choices = []
        for c, mask in masks.items():
            edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(3)))
            for y in range(h):
                for x in range(w):
                    if edge.getpixel((x, y)):
                        choices.append(((x-w/2)/2, (y-h/2)/2, substitutions.get(c,c)))
        random.Random(847491 + sum(map(ord,key))).shuffle(choices)
        selected = [choices[i % len(choices)] for i in range(1000)]
        data["points"][key] = [[x,y] for x,y,_ in selected]
        data["colors"][key] = [c for _,_,c in selected]
        data["sources"][key] = {"file": source.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(svg).hexdigest(), "reference": reference,
            "source_colors": list(colors), "color_substitutions": substitutions,
            "max_size": list(size), "unique_boundary_points": len(choices)}
    return (json.dumps(data, separators=(",", ":")) + "\n").encode()


if __name__ == "__main__":
    DESTINATION.write_bytes(build())
    print(DESTINATION.name, hashlib.sha256(DESTINATION.read_bytes()).hexdigest())
