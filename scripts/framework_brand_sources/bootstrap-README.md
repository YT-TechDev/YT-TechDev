# Official Bootstrap mark — immutable source and faithful raster

This mark identifies Bootstrap in the developer's technology inventory. It is
not the developer's own brand and does not imply affiliation or endorsement.

## Provenance

- Guidelines: https://getbootstrap.com/docs/5.3/about/brand/
- Guidelines source: https://github.com/twbs/bootstrap/blob/25aa8cc0b32f0d1a54be575347e6d84b70b1acd7/site/src/content/docs/about/brand.mdx
- Version: **v5.3.8**
- Commit: `25aa8cc0b32f0d1a54be575347e6d84b70b1acd7`
- Original path: `site/static/docs/[version]/assets/brand/bootstrap-logo.svg`
- Pinned SVG: https://raw.githubusercontent.com/twbs/bootstrap/25aa8cc0b32f0d1a54be575347e6d84b70b1acd7/site/static/docs/%5Bversion%5D/assets/brand/bootstrap-logo.svg
- Published mark linked by the guidelines: https://getbootstrap.com/docs/5.3/assets/brand/bootstrap-logo.svg
- Upstream Git Blob SHA: `f0189652b88bf6148676918156723948862578a8`
- SVG SHA-256: `df11d37a123e36a768f2a6064973c4c6ab17d1e3c6501c8bf434ca5c0134c9a2`
- PNG SHA-256: `72cc867688c2a915ad0b720fa63718cde4237a931f74e43458801f87b5974fef`
- Decoded RGBA SHA-256: `1168ac356ead386fceaf7a1ad5578cd4c1e89029a15e7e2348ccdd19636e3ecc`

`bootstrap-logo.svg` is byte-identical to the upstream blob, including its final
newline. The outer shape and B are the original two paths. Both original
user-space gradients remain: purple `#9013fe` → `#6610f2`, and white `#fff` →
`#f1e5fc`. The white stroke and original drop-shadow filter are retained. The
intrinsic 512×408 aspect ratio is exactly preserved at 128×102 (1/4 scale).
No Bootstrap Icons glyph or redrawn B is used.

## Lossless raster derivation

Export environment: Inkscape **1.2.2 (b0a8486541, 2022-12-01)**, then Pillow
**12.3.0** to normalize the PNG container without changing RGBA pixels:

```bash
inkscape scripts/framework_brand_sources/bootstrap-logo.svg \
  --export-type=png --export-filename=/tmp/bootstrap-official-128.png \
  --export-width=128 --export-height=102
python - <<'PY'
from PIL import Image
source = Image.open('/tmp/bootstrap-official-128.png').convert('RGBA')
source.save('scripts/framework_brand_sources/bootstrap-logo-128.png', optimize=True)
PY
```

The SVG is not rewritten by this operation. Inkscape handles the source filter;
CairoSVG 2.8.2 supports only part of its primitives, so it is not used to produce
this mark. Production verifies and composites the pinned lossless raster without
requiring Inkscape or another runtime package. A changed SVG or raster fails
closed; deliberate asset upgrades need an independent visual and checksum review.
Do not update pins merely to accept new bytes.

The PNG is unpulsed, unwarped and stationary at (985,671). There are no added
effects, particles or individual-component animations. A 12px exclusion region
keeps the orbits and lights separate. This is a local design allowance; the
referenced guidelines do not specify a numeric minimum size or clear space.

## Usage assessment and attribution

The official guidelines request the logo when referencing Bootstrap, prohibit
modification, prohibit using Bootstrap branding for one's own projects, and
require the name Bootstrap. This profile uses the unchanged mark alongside that
name solely to identify a technology. It does not brand the profile or another
project with Bootstrap. That is the basis for proceeding; no official approval
or legal clearance is claimed.

Copyright (c) 2011-2025 The Bootstrap Authors. The upstream MIT license is retained
unchanged in `bootstrap-LICENSE.txt`; it does not override the brand guidance.

The final GIF is a lossy palette encoding. Source SVG integrity, lossless PNG
integrity and decoded GIF color fidelity are separate checks, with no claim of
binary identity between formats. Real mobile playback and GitHub image-proxy
behavior require separate human observation.
