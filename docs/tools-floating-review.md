# Tools floating motion — October 27, 2026 JST

Starting commit: `7f88216d36366c67d9837626a131ae87b5c55a7d`.
Scope: Tools only, existing Draft PR #2. This is a technical implementation for
human visual review; it does not authorize merge, publication or main changes.

## Current identity status

| Visible name | Requested refinement | Status and actual artwork |
| --- | --- | --- |
| VS Code | Recognizable ribbon silhouette in outline particles | **BLOCKED — brand constraint.** Existing illustrative code glyph retained. No ribbon refinement implemented. |
| ChatGPT | Recognizable interwoven symbol in outline particles | **BLOCKED — brand constraint.** Existing illustrative abstract knot retained. No Blossom refinement implemented. |
| Cloudflare | Recognizable company silhouette in outline particles | **BLOCKED — brand constraint.** Existing illustrative simplified cloud retained. No official contour refinement implemented. |

Authoritative references checked October 27, 2026 JST:

- [Microsoft Visual Studio Code brand guidelines](https://code.visualstudio.com/brand):
  the recognizable identity is the blue folded ribbon/fish. The guidelines
  explicitly prohibit modifying or redrawing the icon in a different style.
  Their spacing and permitted contexts also need review for a future official
  asset implementation. No permission for a particle redraw was established.
- [OpenAI design guidelines](https://openai.com/brand/): the Blossom is an
  interwoven sixfold form. The guidelines require the logo exactly as supplied,
  prohibit modification and additional colors, and disallow implied endorsement.
  A colored particle adaptation was not established as permissible.
- [Cloudflare press kit](https://www.cloudflare.com/press/press-kit/): official
  company artwork is available there. It has the distinctive orange cloud/sun
  silhouette and trailing lighter cloud, unlike the existing generic contour.
  [Cloudflare trademark guidelines](https://www.cloudflare.com/trademark/)
  require written permission for logo use outside their specified exceptions and
  prohibit modification. A press download alone is not permission to redraw it.

These are bounded implementation decisions based on the published rules, not a
legal opinion or a claim that the old illustrations are approved official logos.
All three existing illustrations remain explicitly unofficial and unrefined.
No affiliation, partnership or endorsement is asserted. Under the task's
explicit fallback, their local pixels remain unchanged and motion proceeds.
All nine original contours, including the six protected identities, retain the
entire frozen 9,968-pixel dataset, colors, source SVG hashes and provenance.
`tools_particles.json` and `tools_station_reference.png` remain immutable.

## Motion and station contract

`tools_motion_v1.json` is a separate versioned active motion fixture with a
pinned SHA-256. Each instrument uses one sinusoidal scalar with an integer
harmonic of one and a deterministic phase offset of index/9 turns. Both axes
share the scalar: the trajectory is a short reversible diagonal drift rather
than an orbit. Slopes alternate; phases differ for all nine instruments.

| Instrument | Horizontal amplitude | Vertical amplitude | Phase, turns |
| --- | ---: | ---: | ---: |
| PostgreSQL | 4px | 9px | 0/9 |
| Docker | 3px | 9px | 1/9 |
| Git | 5px | 10px | 2/9 |
| Cloudflare | 4px | 10px | 3/9 |
| Linux | 3px | 10px | 4/9 |
| VS Code | 5px | 10px | 5/9 |
| Blender | 4px | 10px | 6/9 |
| ChatGPT | 3px | 10px | 7/9 |
| Claude | 5px | 10px | 8/9 |

The renderer caches separate symbol sprites, stationary typography, background
and station structure. Only the symbol sprites translate. The preserved signal
lights retain their original formulas. Integer placement preserves every local
pixel exactly: no contour resampling, new antialiasing, glow, rotation, scaling,
stretching, random sampling or per-frame particle pulse is introduced. The
continuous underlying sine is smooth; integer raster steps are at most 2px
per 160ms frame, including the seam. Raster rounding can hold a position near
an extremum. It does not change the silhouette. The PNG is the actual phase-zero
RGB pose of this animation, while the immutable reference is checked at neutral
translation to preserve its original whole-composition comparison gate.

Continuous bounds use actual painted local extrema plus the maximum absolute
analytic displacement and 2px conservative padding. Frozen pixels already
include emphasized-dot radii, so their support is counted once. Integer GIF
quantization with dithering off does not expand support. Unioning those bounds
with the original 200x170px fixed cores leaves the cores unchanged: all travel
fits inside them. Background stars, station structure, 13px mask falloff and
signal exclusion are therefore byte/pixel stable across this change. Masks
never follow the sprites. Protected station/signal alpha is zero after filters.

The original >=19px neutral logo/name clearance gate remains. The additional
continuous motion gate requires >=10px at the full analytic extreme (>=8px
including the conservative 2px pad), plus nonintersection with every text box,
annotations, hull limits and fixed protected station regions. No sampled-frame
maximum is substituted for this continuous bound.

At 320px width, vertical travel is 4.8–5.33px peak-to-peak; at 375px it is
5.625–6.25px. These are resized production previews, not physical-device playback.
Mathematical closure, actual decoded per-logo positions, per-logo steps and
encoded final-to-first continuity are checked separately.

## Verification and review

Canonical production remains 1200x900, 48 frames, 160ms/frame, 7680ms, infinite
loop. The PNG and GIF are fully encoded and decoded before replacement.
A fixed palette reserves literal symbol colors; no dithering is used. The
historical <=2,500,000-byte GIF gate remains unchanged.

`verify_tools.py` preserves historical fixture extraction, neutral >=19px
clearance, original design-reference comparison, signal visibility, typography,
GIF/palette/timing/loop, protected assets and deterministic CLI checks. It adds:

- Nine distinct phases and real rendered foreground movement, independently of
  signals. Every actual decoded GIF frame must contain the exact translated
  literal silhouette; per-logo decoded offsets and spans are reported.
- Analytical collision/clipping bounds, fixed-mask coverage, measured maximum
  steps, periodic endpoints and actual encoded seam comparisons.
- All 48 neutral-translation RGB station/signal/text phases compared with the
  exact starting renderer loaded from its immutable Git commit. Background,
  structure, mask, exclusion and static base also compare exactly.
- The decoded static-field check excludes the new continuous logo envelopes as
  well as old signal travel. At least 75% of the canvas must remain pixel-stable.
  The old >1,000,000 static-pixel assertion described only the signal-only
  motion mask; the new classification necessarily excludes moving logos. The
  independent full historical station gate prevents that exclusion from hiding
  station changes.
- Negative controls for a static logo layer with live signals, identical phases,
  excessive displacement, noninteger harmonic/failed periodicity, invalid motion
  fixture and shifted label. Existing negative controls are retained.

`--determinism` regenerates both assets twice using the canonical Tools CLI and
requires matching hashes and unchanged unselected files. Existing Languages,
Frameworks and section guard tests still run. CI adds the two Tools-only source
paths to existing selection/triggers, without changing protected renderers or
allowing extra generated writes.

Generate the production-derived review package outside the repository:

```bash
# First preserve assets from starting commit as before.png and before.gif.
python scripts/tools_review.py --before /absolute/baseline --output /absolute/review
python scripts/verify_tools.py --protected --determinism --report /absolute/review/tools-verification.json
```

The review script produces final PNG/GIF, full before/after still and motion
comparison, all three unchanged contour comparisons, five-phase contact sheet,
analytical trajectory plots, actual 375/320px decoded previews and GIF resizes,
loop transition still/GIF, fixed-core/envelope overlay, three-section composition,
a high-contrast motion-difference diagnostic and hashes. The diagnostic is not
part of the production artwork. Contour comparison crops remove the intentional
translation and explicitly mark each identity refinement BLOCKED.

Overall design classification remains **NEEDS REFINEMENT** while those three
requested identity improvements are unimplemented, even when all motion and
technical checks pass. Stop with PR #2 Open/Draft/unmerged for human review.
