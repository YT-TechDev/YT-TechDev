#!/usr/bin/env python3
"""Build review artifacts from actual decoded production images, outside Git."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

import render_sections as sections
import tools_observatory as tools

PHASES = (0, 12, 24, 36, 47)
INK = (207, 228, 245)


def canvas(size):
    return Image.new('RGB', size, (6, 13, 29))


def caption(image, text, xy=(16, 12), size=20):
    ImageDraw.Draw(image).text(xy, text, fill=INK, font=tools.tools_font(size, True))


def decode(path):
    with Image.open(path) as image:
        return [image.seek(i) or image.convert('RGB') for i in range(image.n_frames)]


def montage(frames, indices, width, columns, title):
    height = round(width*900/1200)
    out = canvas((width*columns, 48+(height+38)*math.ceil(len(indices)/columns)))
    caption(out, title)
    for j, index in enumerate(indices):
        x, y = j % columns*width, 48+j//columns*(height+38)
        out.paste(frames[index].resize((width, height), Image.Resampling.LANCZOS), (x, y+28))
        caption(out, f'frame {index:02d} / {index*160} ms', (x+8, y+4), 15)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', required=True, type=Path, help='Directory with before.png and before.gif from starting HEAD')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if out == tools.ROOT or tools.ROOT in out.parents:
        parser.error('Review outputs must be outside the repository')
    out.mkdir(parents=True, exist_ok=True)
    renderer = tools.StationGrid(sections.SECTIONS['tools'])
    frames = decode(tools.ROOT/'assets/constellation-tools.gif')
    before_frames = decode(args.before/'before.gif')
    before = Image.open(args.before/'before.png').convert('RGB')
    after = Image.open(tools.ROOT/'assets/constellation-tools.png').convert('RGB')
    for ext in ('png', 'gif'):
        shutil.copyfile(tools.ROOT/f'assets/constellation-tools.{ext}', out/f'final-tools.{ext}')
    comparison = canvas((2400, 952))
    caption(comparison, 'BEFORE / stationary symbols', (22, 15), 25)
    caption(comparison, 'AFTER / nine independently phased instruments', (1222, 15), 25)
    comparison.paste(before, (0, 52)); comparison.paste(after, (1200, 52))
    comparison.save(out/'before-after.png')
    comparison_frames = []
    for i in range(48):
        image = canvas((1200, 482))
        caption(image, 'BEFORE', (16, 5), 18); caption(image, 'AFTER', (616, 5), 18)
        image.paste(before_frames[i].resize((600,450), Image.Resampling.LANCZOS), (0,32))
        image.paste(frames[i].resize((600,450), Image.Resampling.LANCZOS), (600,32))
        comparison_frames.append(image)
    save_gif(comparison_frames, out/'before-after-motion.gif')
    for key in ('vscode', 'chatgpt', 'cloudflare'):
        i = next(i for i,n in enumerate(renderer.nodes) if n['key']==key)
        x,y = renderer.nodes[i]['anchor']
        dx,dy = tools.floating_offset(renderer.motion[i],0)
        image = canvas((880, 460))
        caption(image, key+' / contour UNCHANGED - brand restriction', (18,12), 21)
        for j,(source,ox,oy) in enumerate(((before,0,0),(after,dx,dy))):
            crop = source.crop((x+ox-90,y+oy-75,x+ox+90,y+oy+75))
            image.paste(crop.resize((432,360),Image.Resampling.NEAREST),(8+j*440,70))
            caption(image, ('BEFORE','AFTER / translation removed')[j], (12+j*440,46), 16)
        caption(image,'Historical illustrative artwork; no official-logo refinement claimed.', (16,434),16)
        image.save(out/f'{key}-contour-comparison.png')
    montage(frames,PHASES,600,3,'Floating phases: 0, pi/2, pi, 3pi/2, final encoded frame').save(out/'floating-contact-sheet.png')
    for width in (375,320):
        montage(frames,PHASES,width,3,f'{width}px actual decoded frame resizes / no physical-device claim').save(out/f'mobile-{width}-frames.png')
        small=[f.resize((width,round(900*width/1200)),Image.Resampling.LANCZOS) for f in frames]
        save_gif(small,out/f'mobile-{width}.gif')
    montage(frames,(46,47,0,1),375,2,'Loop seam: last two and first two decoded frames').save(out/'loop-transition.png')
    loop=[frames[i].resize((600,450),Image.Resampling.LANCZOS) for i in (44,45,46,47,0,1,2,3)]
    save_gif(loop,out/'loop-transition.gif')
    # High contrast diagnostic, deliberately separate from the artwork.
    difference=canvas((1200,952)); caption(difference,'MOTION DIFFERENCE / frame 0 vs 24 / cyan old, coral new',size=22)
    difference.paste(frames[0].point(lambda v:round(v*.32)),(0,52))
    d=ImageDraw.Draw(difference)
    for node,spec in zip(renderer.nodes,renderer.motion):
        x,y=node['anchor']; a=tools.floating_offset(spec,0); b=tools.floating_offset(spec,math.pi)
        for px,py,*_ in node['pixels']:
            d.point((x+px+a[0],y+py+a[1]+52), fill=(60,232,255))
            d.point((x+px+b[0],y+py+b[1]+52), fill=(255,109,129))
    difference.save(out/'motion-difference.png')
    mask=after.copy(); overlay=Image.new('RGBA',tools.SIZE)
    od=ImageDraw.Draw(overlay)
    for node,spec in zip(renderer.nodes,renderer.motion):
        od.rectangle(renderer.logo_envelope(node,spec,tools.ENVELOPE_PAD),fill=(240,110,45,35),outline=(255,170,60,230),width=2)
    # Cyan outlines are the existing fixed core, orange the full continuous travel.
    for box in renderer.boxes: od.rectangle(box,outline=(65,220,245,150))
    mask=Image.alpha_composite(mask.convert('RGBA'),overlay).convert('RGB')
    caption(mask,'CYAN fixed cores / ORANGE padded continuous envelopes',(20,810),19)
    mask.save(out/'fixed-protection-masks.png')
    trajectories=canvas((1080,830)); caption(trajectories,'Analytical trajectories / positions magnified 6x / no rotation',size=23)
    for i,(node,spec) in enumerate(zip(renderer.nodes,renderer.motion)):
        x=(i%3)*360+180; y=(i//3)*255+170
        d=ImageDraw.Draw(trajectories)
        d.line((x-55,y,x+55,y),fill=(40,70,100)); d.line((x,y-78,x,y+78),fill=(40,70,100))
        coords=[(x+6*tools.floating_offset(spec,math.tau*j/480,raster=False)[0],y+6*tools.floating_offset(spec,math.tau*j/480,raster=False)[1]) for j in range(481)]
        d.line(coords,fill=(92,179,218),width=2)
        for frame,color in zip(PHASES,((255,172,90),(120,255,190),(123,162,255),(255,130,190),(255,255,255))):
            dx,dy=tools.floating_offset(spec,math.tau*frame/48,raster=False)
            cx,cy=x+6*dx,y+6*dy
            d.ellipse((cx-4,cy-4,cx+4,cy+4),fill=color)
        caption(trajectories,node['label'],(x-140,y-108),20)
        caption(trajectories,f'+/-{abs(spec["ax"])}x{spec["ay"]} px / phase {i}/9 turn',(x-140,y+83),15)
    trajectories.save(out/'motion-trajectories.png')
    sections_images=[]
    for name in ('languages','frameworks','tools'):
        image=Image.open(tools.ROOT/f'assets/constellation-{name}.png').convert('RGB')
        sections_images.append(image.resize((1200,round(image.height*1200/image.width)),Image.Resampling.LANCZOS))
    composition=canvas((1200,sum(i.height for i in sections_images)))
    y=0
    for image in sections_images: composition.paste(image,(0,y)); y+=image.height
    composition.save(out/'three-section-composition.png')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
    (out/'review-manifest.json').write_text(json.dumps({'source_gif':hashes['final-tools.gif'],'frame_indices':PHASES,'physical_device':'UNVERIFIED','sha256':hashes},indent=2)+'\n')
    print(f'Review artifacts: {out}')


def save_gif(frames,path):
    palette=frames[0].quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(path,save_all=True,append_images=indexed[1:],duration=160,loop=0,optimize=False,disposal=1)


if __name__=='__main__': main()
