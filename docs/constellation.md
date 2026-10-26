# Skill Constellation — sectioned README artwork

This profile embeds generated GIFs, since GitHub README markdown cannot run React/TSX/WebGL. Output is explicitly **non-interactive**.

## Layout and editorial choices

The previous 20-node poster was difficult to read on phones, especially the bottom two rows. The three sections now contain **31 nodes** into three independently generated star maps:

- **Languages & Markup (10):** HTML, CSS, JavaScript, TypeScript, VBScript, Python, Java, MoonBit, C++, Rust (ordered from frontend/web through scripting toward backend/systems)
- **Frameworks & Runtimes (12):** React, Next.js, Node.js, R3F, Three.js, Vue.js, Google Apps Script, TailwindCSS, Bootstrap, Framer Motion, jQuery, Prisma
- **Tools & Platforms (9):** PostgreSQL, Docker, Git, Cloudflare, Linux, VS Code, Blender, ChatGPT, Claude

Frameworks now uses **Quiet Orbits / Structure**, with two shared elliptical paths behind **twelve outline-particle symbols**. Tools retains its original three-column layout and awaits its Space Station / Observatory design phase. The completed Languages image is a distinct 5-column × 2-row, 1600×780 layout, arranged for left-to-right frontend → backend reading. It displays only particle icons and language names, without secondary status labels or connector lines. Brightness is intentionally high across all groups and conveys **no proficiency ranking**. Internal activity metadata is retained: MoonBit is used in [Web Interactive Flow](https://github.com/YT-TechDev/web-interactive-flow), based on the public MoonBit/WebAssembly runtime implementation; C++ and Rust remain Exploring. ChatGPT/Claude are explicitly AI tools, not programming languages.

## Sources

- Frozen portfolio outline dataset: `data/icon-paths.json` from `YT-TechDev/yt-techdev-portfolio` at `6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27`.
- Repaired TypeScript, PostgreSQL, Docker and Git outlines and other supplemental marks: `data/supplemental-icons.json` from Simple Icons pinned at `90646e4bf7f3b89df6c37e65baf3e7bc759a517c`.
- MoonBit is extracted as **outline and interior-edge particle samples** from the official `moonbitlang/moonbit-docs` `next/_static/logo.png`, pinned to commit `50bbd2f59ba80ed046b6ecad57c7e8507ca06e9e` (repository copy `assets/moonbit-official.png`). The earlier illustrative crescent/M is no longer used for the Languages renderer.
- React / Next.js / R3F and VS Code / ChatGPT have illustrative symbols. Other normalized logo outlines come from the pinned sources.

Neither RAOS nor Assembly are listed. The portfolio source is referenced, not mutated.

## Regeneration

```bash
python -m pip install -r scripts/requirements.txt
python scripts/render_sections.py --only frameworks
python scripts/verify_frameworks.py --determinism --protected
python scripts/verify_languages.py
```

The canonical Frameworks command defaults to **64 frames × 100ms = 6.4 seconds** at 1200×1110. Its PNG is a neutral, undrifted/unpulsed pose with orbital lights at phase zero; it is a lossless RGB poster, not a decoded GIF frame. `--frames` remains available for disposable experiments, but the production verifier requires 64 frames. Languages still supports `--only languages` (36×150ms), and Tools still supports `--only tools` (18 frames, original encoding). Section selection writes only the chosen pair of images. The old combined assets were removed as obsolete.

Frozen Languages verification uses CairoSVG and system fonts/FreeType in addition to the pinned Python requirements. The approved CI-compatible environment uses system FreeType 2.14.3; a machine with a different SVG rasterizer can reject the frozen Languages PNG. Do not regenerate or replace Languages to make a Frameworks change pass. Frameworks' audited contour fixture removes this source of silhouette variation from its production rendering.

## Review gate

- [ ] Exact final content passes the section-aware workflow and both verifiers
- [ ] Inspect Quiet Orbits PNG/GIF, all twelve identities, protected arcs and loop transition
- [ ] Preview all three GIFs at phone width via the draft PR
- [ ] Confirm labels, clipping, the official MoonBit contour and color contrast

Do not merge before visual approval. No changes to public profile main until the PR is merged.

## Bootstrap outline-particle revision

The user's subsequent design instruction replaces the solid official Bootstrap
mark with an **unofficial outline-particle adaptation of the same shape**. All
twelve technology symbols now use particles. The official reference SVG and its
lossless PNG remain unchanged as provenance and historical evidence; the PNG
is no longer composited into the active artwork.

`build_bootstrap_outline.py` extracts the two exact SVG path geometries into
neutral contour masks: the brace-shaped outer silhouette and the B, including
both counters. It freezes 1,000 ordered samples in `bootstrap_outline_contours.json`.
The outer contour uses light violet `#c9a4ff`; B uses pale violet `#ede4ff` for
contrast on navy. There is no solid fill, gradient or shadow in this adaptation.
The 128×102 design region and anchor (985,671) are preserved. It uses the same
3× antialiased particle radii as Motion/Apps Script and the existing shared
floating/pulse functions, including Bootstrap's original index-eight phase.
Orbital protection contains its full animation and antialiasing support.
The deterministic GIF palette retains 224 composition colors and reserves 32
colors from Bootstrap's actual five-phase particle samples to preserve sparse
violet edges. All frames still share one 256-color table without dithering;
the existing foreground error limit and stricter Bootstrap error check remain.

All eleven other symbols retain their exact contours, colors and animation.
The frozen RGB preservation fixtures and all historical contour fixtures stay
unchanged. Verification now checks the derived Bootstrap fixture, actual particle
layer, absence of solid fill, floating animation, GIF fidelity and rejection of
both the solid raster and old standalone particle B. Timing, subtitle, labels,
background, orbits, Languages and Tools retain their previous contracts.

This requested adaptation is not an unchanged official logo. The upstream
guidance prohibits logo modification; no brand-owner approval or guideline
compliance is claimed for the particle adaptation. Provenance and prior usage
assessment remain recorded below, applying to their respective historical output.

## Historical official Bootstrap integration (October 26, 2026)

The solid-logo rendering contract below is superseded by the outline-particle revision above.

Bootstrap is the sole exception to the particle rendering contract. The unchanged
primary SVG referenced by the [official Bootstrap 5.3 brand documentation](https://getbootstrap.com/docs/5.3/about/brand/)
is pinned to **v5.3.8**, commit `25aa8cc0b32f0d1a54be575347e6d84b70b1acd7`.
Its SHA-256 is `df11d37a123e36a768f2a6064973c4c6ab17d1e3c6501c8bf434ca5c0134c9a2`.
Full provenance, rasterization commands, checksums, license and usage assessment
are in [the brand-source notes](../scripts/framework_brand_sources/bootstrap-README.md).

The official 512×408 canvas is proportionally rasterized at **128×102**, centered
on the existing **(985,671)** anchor. The logo stays static, retaining the official
outer shape, B, purple and white gradients, stroke and built-in shadow. There is
no particle sampling, pulse, added glow, recoloring or component animation.
The existing Bootstrap label and all twelve anchors remain fixed. A 12px local
clear-space allowance excludes orbital curves and moving lights. This allowance
is a conservative layout choice, not a published Bootstrap spacing rule.

Inkscape 1.2.2 produces the faithful lossless RGBA raster, including the SVG's
original filter. The existing CairoSVG dependency does not implement every
primitive in that shadow filter. Production therefore composites the verified
SVG-derived PNG rather than substituting an incomplete runtime conversion. Both
source and raster bytes and decoded RGBA pixels are pinned; no new runtime
package is introduced. The canonical renderer remains deterministic and offline.

All eleven other contours, multicolor samples, floating offsets, pulses and
labels are preserved. `framework_bootstrap_preserved_rgb.json` records five
unquantized foreground phases for each from baseline `fc6240cc1e43401c4ae3801186b96bc78802becb`.
The previous Bootstrap contour stays in the immutable expansion fixture and is
still exercised by the historical RGB checks. It cannot pass as active artwork.
All earlier contour/RGB fixtures remain unchanged. The background/star hash,
two orbital paths, subtitle, footer-free layout, 1200×1110 canvas and 64×100ms
infinite animation retain their existing contracts.

Verification separately checks SVG identity/provenance, lossless raster identity,
all decoded GIF frames and Bootstrap color error. GIF quantization is lossy;
decoded pixels are not claimed to be binary-identical to the vector or PNG.
Negative controls reject modified/wrong SVGs, modified PNGs, recoloring, restored
particle B, missing technology, protected-asset drift and all earlier failures.
The full existing validation, Languages checks and Tools guards stay enabled.

This is a referential technology listing with the adjacent name **Bootstrap**,
not use of Bootstrap as the developer's own project brand. No endorsement or
affiliation is claimed. This interpretation follows the documentation's request
to use its mark when referencing Bootstrap; it is not brand-owner approval.
PR #2 stays Draft and unmerged pending human design review.

## Historical Frameworks visual polish (October 26, 2026)

The Bootstrap hold described below is superseded by the official-asset exception above.

The subtitle is now **FROM UI LIBRARIES TO APPLICATION SYSTEMS**, at the same position, font, size and color. The section title, twelve labels, 1200×1110 canvas and all twelve anchors are unchanged.

**Bootstrap is held unchanged.** Its [official guidance](https://getbootstrap.com/docs/5.3/about/brand/) asks users to reference the official mark and forbids modifying the logos. The [Bootstrap 5 announcement](https://blog.getbootstrap.com/2021/05/05/bootstrap-5/) explains the CSS-curly-brace origin. The official SVG is 512×408 with purple `#9013fe` → `#6610f2` and white-to-lilac B fills. A brace-accented original illustration and a refined standalone B were compared locally at native, 375px and 320px sizes. Neither has confirmed brand clearance; neither is production input. Retaining the existing particle B is a scope-preserving hold, not a claim that the existing illustration is approved official artwork. A new particle adaptation requires clarification from the brand owner; an unchanged official asset would require an explicit visual exception to this section's particle treatment.

**Framer Motion keeps its visible historical name and uses the verified current Motion identity.** [Motion became independent in November 2024](https://motion.dev/magazine/framer-motion-is-now-independent-introducing-motion). The maintainer supplies [the three diagonal forms and circular dot](https://github.com/motiondivision/motion/discussions/3326), including curved ends and the original spacing, and permits the requester's logo use and color cleanup. Current [Motion Studio artwork](https://github.com/motiondivision/motion-vscode/blob/main/images/logo.png), blob `365221b61a343781d08fcac6c426886f74ad0b70`, independently corroborates that geometry; its pink product tile is not the library's yellow identity. The outline uses library yellow `#fef62a`, drawn from the maintainer's library SVG, instead of the prior muted `#f3df83`. The original black foreground path is stored in `motion-symbol.svg`; converting its fill into yellow particle contours is explicitly an **unofficial illustrative adaptation**, not unaltered official artwork or an endorsement. No Framer website-builder symbol is substituted.

Motion candidate A used the verified geometry with the historical point rasterizer. Candidate B keeps the same 1,000 coordinates and geometry but applies local 3× antialiasing. Candidate B was selected for clearer small-size contours and the dot. Its three differently terminated slanted forms and dot replace the inaccurate two parallelograms and triangular wedge. The visible label remains `Framer Motion`.

**Google Apps Script keeps its exact existing 1,000 ordered coordinates, four source colors, five white circular rims, center and label.** Only its local rasterization changes: 3× supersampling, 0.78px primary particle radius, 1.25px accents every eighth sample, and a single Lanczos downsample. The same bounded treatment is used for Motion. There is no blur/glow, fill container or inter-arm reconstruction. Native and actual 375px/320px comparisons show stronger circle rims without merged red/yellow/green/blue contours. Source brightness and periodic pulse formulas are unchanged.

`framework_polish_contours.json` and `build_framework_polish.py` hold the separate active Motion contour, its exact source hash, provenance, yellow interpretation and the two reviewed local raster styles. The four historical contour/RGB fixtures and `build_framework_refinement.py` remain byte-identical. `framework_polish_preserved_rgb.json` is independently captured from starting commit `652f79a761bf714f6a3553e8cd2667a086b31abc`: it adds ordered-coordinate hashes and 50 source RGB checks for the nine strictly preserved marks plus held Bootstrap. The older 45 source RGB checks, including archived Motion, still run separately. Vue and historical Prisma are now explicitly included in the current preservation checks.

The particle AA support is conservatively bounded by 5px only for Motion and Apps Script. Their fixed orbital protection cores and continuous animation envelopes are recomputed; the two ellipses and illumination trajectories are unchanged. Static star attenuation uses the frozen pre-polish protection geometry so changing an orbital mask cannot brighten or dim distant stars. The complete background RGB hash is independently checked against the starting renderer. Negative controls additionally reject Motion-dot removal, unreviewed GAS radii, Bootstrap changes, active-fixture drift and unexpected star changes. Existing GIF decoding, palette fidelity, size, seam, clipping, timing, canonical determinism, Languages verification and Tools protection remain enabled.

The technical output is for human design review. Bootstrap's requested identity improvement remains blocked by brand guidance, so the whole four-part request must not be reported as an unconditional design-ready PASS.

During local generation, complete-image checks rejected two directly saved PNGs with incomplete IDAT chunks. Isolated full in-memory encodings were valid. The Frameworks PNG path therefore now validates a complete encoded buffer, writes a temporary file and atomically replaces the PNG, then checks that its bytes remain unchanged during GIF generation. The encoding options and pixel content are unchanged. The original direct-write truncation cause was not conclusively identified; both canonical regenerations must still match the verified PNG/GIF hashes before any push.

## Prior Frameworks refinement baseline (October 26, 2026)

The following paragraphs record the pre-polish baseline at `652f79a`. Quiet Orbits retained its navy space, sparse stars, two shared cyan/violet orbits, restrained illumination and slow floating motion. Its obsolete WASM subtitle is superseded by the visual-polish wording above.

### Final layout

Canvas **1200×1110**; columns **X=215,600,985**; rows **Y=191,431,671,911**. Names remain **38px DejaVu Sans Bold**, centered **96px** below the marks. No global font reduction was needed for Google Apps Script: its full name fits with clear separation from TailwindCSS. Framer Motion and jQuery move to the new column centers; their contour-local ordered samples and colors remain unchanged.

| Row | X=215 | X=600 | X=985 |
| :-- | :-- | :-- | :-- |
| Y=191 | React | Next.js | Node.js |
| Y=431 | R3F | Three.js | Vue.js |
| Y=671 | Google Apps Script | TailwindCSS | Bootstrap |
| Y=911 | Framer Motion | jQuery | Prisma |

The Frameworks-only foreground has exactly three header/subtitle text calls and twelve names. Both footer captions and its horizontal rule are removed without replacement. Canvas height, two orbital paths and top header remain unchanged. The lowest name ends around Y=1022, with calm lower padding and the existing continuous orbital arc. Languages and Tools footer paths are untouched.

At 375px the canvas becomes 375×347 and the labels have an effective 11.875px font size. At 320px it becomes 320×296, with effective 10.13px labels. These simulated previews support design review; real mobile-device playback is **UNVERIFIED**.

### Official identity references and interpretations

All three new/redesigned marks are **unofficial particle adaptations**, not official downloadable logo assets or endorsements.

- **Vue.js:** the two filled paths of the actual [Vue homepage logo](https://vuejs.org/) provide the nested V contours. The outer green `#42b883` is retained; the official inner `#35495e` is lifted to teal `#80c7c6` for dark-background contrast. Proportions and separated inner/outer edges are preserved; it is not a single V letter.
- **Google Apps Script:** [Google Workspace's extension documentation](https://developers.google.com/workspace/extend) explicitly labels and links the [Apps Script v10 product icon](https://www.gstatic.com/images/branding/productlogos/apps_script/v10/192px.svg). Its four overlapping red/yellow/green/blue rounded arms and five white circles replace the historical generic code document. Sampling occurs after SVG occlusion, retaining visible component relationships without exposing hidden arm edges. Exact source fill colors are retained before the existing 0.96 activity brightness and pulse. White circular areas become particle rims, not solid white discs. [Apps Script overview](https://developers.google.com/apps-script) corroborates product identity. This symbol requires special human design approval.
- **Prisma ORM:** the requested angular, faceted prism is the **historic** official mark. The supplied [presskit](https://github.com/prisma/presskit) changed to a new banded mark in August 2026 (`664e85e9950fa431d2e025202aeda758ff28d5ef`, merged August 26); that is not the faceted silhouette requested here. The source is therefore pinned to [Prisma-LightSymbol.svg at 13ee1c5](https://github.com/prisma/presskit/blob/13ee1c557d3dad9c036cdb1e2607c33ea90c2544/Assets/Prisma-LightSymbol.svg). The asymmetrical outer quadrilateral and inset slanted triangular cutout retain their official aspect ratio. Near-white `#edf3ff` particles replace the white fill. This intentionally represents Prisma ORM's recognizable legacy identity; it must not be described as the current official mark. The presskit permits standalone symbols alongside other brand symbols. No enclosing badge or generic equilateral triangle is added.

The three exact vector references are stored in `scripts/framework_brand_sources/`. Their byte hashes, URLs, palette interpretation and fixed coordinates are recorded in `framework_refinement_contours.json`. `build_framework_refinement.py` derives only these three contours offline; it never rewrites historical contours or the shared sampler. It samples visible vector color boundaries at 2×, rounds to half-pixel coordinates and uses a fixed per-key shuffle. Production reads 1,000 frozen ordered samples per mark.

### Immutable historical evidence and source RGB

`framework_contours.json` remains byte-identical (SHA-256 `03f39f7807a8a7ec3d496d167eaaeacdbdd81b74da63cfaf8f44e528cf418745`), as does `framework_expansion_contours.json` (SHA-256 `b2e27c86ba99bb4c0946c4e1d7d3c522b00774d19faeaada8b25291969b99670`). The historical fixtures retain inactive WebAssembly, SpringBoot, Rust crate and the former code-document Apps Script samples solely for reproducibility. They do not define active inventory. The active renderer selects exactly twelve entries; the refined Apps Script fixture overrides its archived version.

React, Next.js, Node.js, R3F, Three.js, TailwindCSS, Bootstrap, Framer Motion and jQuery retain all ordered local coordinates, colors and activity brightness. Five original active masks still match the independent historical binary silhouette hashes. `framework_preserved_rgb.json` additionally captures actual pre-change foreground crops from baseline `5cd6048516b6016789bb87267926a9abbb37e6a8`: nine marks × neutral plus four animated phases = **45 source RGB layer comparisons**. Both old and new renders use the same local anchor, avoiding palette changes or half-pixel rounding after a canvas translation being mistaken for a contour redesign.

### Orbits, encoding and validation

The two shared ellipses remain center (600,558), radii (560,430), rotation −8°, and center (606,570), radii (600,490), rotation 9°. Static protection masks are recomputed from actual new contours, complete continuous drift, dot radius, rounding allowance, glow/antialias support, label boxes and the header. No removed footer core remains. Orbital and moving-light alpha are exactly zero in each protected core after glow/antialiasing. No moving masks, per-logo rings or arc redesign are introduced.

Timing remains **64×100ms = 6.4 seconds**, infinite loop, with one deterministic 256-color palette, no dithering and disposal 1. All real GIF frames must exactly match their intended palette-quantized RGB sources. The palette may change for multicolor Apps Script, so old GIF index equality is not an identity test. Source contours and the 45 unquantized RGB layers are checked separately. Existing gates remain: **3,500,000 bytes** maximum, **<8** foreground RGB error, **≥8px** logo/name clearance, seam **≤1.25×** the largest interior step and **>500,000** static pixels.

The verifier checks exact inventory/order/colors/anchors; immutable fixtures and reference hashes; offline contour derivation; all collision and clipping bounds; header and footer absence; full floating/label protection; all periodic endpoints; native/mobile contrast; all decoded frames/durations/palette tables; actual seam continuity; RGB and decoded background stability; and two complete deterministic canonical regenerations. Negative controls reject missing/incorrect/restored technologies, empty/drifting contours, disabled protection, recolored preserved source layers and a restored footer. CI adds only these Frameworks sources/fixtures to section selection, preserving Languages checks, Tools guards, concurrency and guarded non-force bot writes.

## Historical six-item Quiet Orbits baseline (October 25, 2026)

Languages tells the Cosmic Dust / Origin Layer story; Frameworks expresses the emergence of structure with two shared orbits. The decorative paths do not indicate dependencies, proficiency or a central technology. No hub, per-logo rings, arrows or new badges are present.

- Geometry is fixed at center (600,281), radii (574,138), rotation −7°, and center (606,282), radii (657,217), rotation 9°. Three-times-resolution curves are downsampled once; a restrained blur adds depth. Broad arc breaks and fixed exclusion regions keep the curves subordinate to the logos.
- Six original anchors remain X=(187,600,1013), Y=(177,385). Particle motion uses horizontal ±1.2px and vertical ±5px integer-harmonic functions; pulse is `.96 + .04*sin(phase + sample*.19 + index)`. Light points travel short sinusoidal arcs. Background and orbital curves are built once per renderer instance.
- Names are 36px bold, anchored 88px below each logo center. Header/footer fonts and positions are preserved from the committed Frameworks baseline, including its original right footer anchor at X=1158 (the study image placed it one pixel left).
- Masks contain each full floating envelope, emphasized-dot radius and rounded pixel centers, every name, header and footer. An outer fixed falloff softens line ends. Alpha is forced to zero inside the protected core **after** glow and antialiasing; masks never follow instantaneous logo positions.
- A single deterministic 256-color palette is derived from five fixed animation phases. Dithering is disabled. All frames use this color table; source RGB and decoded GIF backgrounds must both remain exactly static outside the continuous animation envelope.

### Baseline reconciliation and frozen contours

The historical Frameworks PNG was last generated in asset commit `08eb31353501607086cd206bbd4de43d87ac60c4`, using renderer source `6624f5dc94588a4c7ea6c1391bdb53ddcda6b10a`. Its SHA-256 is `aec3d751231c5f75f5b8212a0888ffc354570b13d9055dad3224f4e66a8c5925`.

The 7,483-pixel mismatch at the pre-implementation HEAD was reproduced exactly with Python 3.12.14, Pillow 12.3.0, CairoSVG 2.8.2, Cairo 1.18.0 and system FreeType 2.13.2. It contains 6,470 changed logo pixels and 1,013 changed footer pixels, with zero background, star, name or header changes. Two historical code changes account for the source mismatch: a six-pixel transparent border added to the shared contour sampler in `d080d91` changes edge candidates/shuffle results, and the right footer anchor changed from 1158 to 1157 in `755d294`. The old asset had deliberately remained frozen.

Restoring the historical source leaves 600 differing WebAssembly pixels under system FreeType 2.13.2. Changing only system FreeType to 2.14.3 eliminates that residual: **zero changed pixels and byte-identical PNG SHA-256**. Changing Cairo 1.18.0 to 1.18.4 alone does not eliminate it. The old Actions log identifies Ubuntu 26.04.1 and Python 3.12.15 but did not record system FreeType; this controlled reproduction establishes a matching environment without inventing the missing historical version record.

`scripts/framework_contours.json` preserves the exact original 1,000 ordered samples per logo from that matching reproduction. This additional production input is necessary to keep the original particle silhouette stable across FreeType changes. It records provenance, SVG hashes, seed, environment and six independently extracted committed-logo mask hashes. `prepared_contours` rejects fixture or SVG changes. `render_constellation.py`, the pinned icon datasets, Languages and Tools samplers remain untouched. No NumPy or new runtime package is needed.

To reconstruct the fixture provenance independently, extract the historical commit with `git archive`, import its `prepared_nodes('frameworks', ...)`, and render its frozen phase-zero poster with the pinned Python dependencies, Cairo 1.18.0 and system FreeType 2.14.3. The DejaVu Sans Bold source font SHA-256 is `5c1247acef7f2b8522a31742c76d6adcb5569bacc0be7ceaa4dc39dd252ce895`. Compare the poster to the historical PNG before retaining samples. Production rendering uses the frozen samples directly, so this historical environment is not required for the canonical Frameworks command.

### Verification and CI isolation

`verify_frameworks.py` checks actual PNG pixels, all 64 fully decoded GIF frames against their intended quantized RGB renders, every duration, total time and loop flag. It checks the six original binary logo masks, identities/colors/anchors, typography bounds, continuous floating envelopes, zero orbital alpha in protected regions, mathematical endpoints, decoded seam versus normal adjacent-frame changes, palette fidelity, static background pixels and 320/375px label contrast. `--determinism` runs the canonical CLI twice in a disposable checkout and compares both output hashes to the validated images. `--protected` additionally asserts the frozen Languages/Tools Git Blob SHAs for this phase.

The workflow keeps the Languages render/verification pipeline and adds Frameworks rendering/verification. Dedicated Frameworks changes select Frameworks; dedicated Languages changes select Languages; explicit mixed changes select both. A generic shared-renderer-only push retains the Languages generation path, while both content verifiers still run, so ambiguous cross-section changes fail rather than being silently accepted. Manual dispatch provides explicit `frameworks`, `languages` and `both` choices. Frameworks-only runs verify the existing Languages PNG/GIF without rewriting them; Languages-only runs preserve the Frameworks pair. Tools is never a generated write target in this workflow.

Every unselected tracked file is hashed before generation and checked afterward. Only selected GIF/PNG pairs may change or be staged. Per-branch concurrency serializes bot writers; a fresh remote-HEAD check precedes a non-force bot push. Failed verification prevents commits. The bot uses GITHUB_TOKEN, whose pushes do not trigger another workflow run; only the selected image pairs can be committed. The bot write step is restricted to the existing feature branch; main has no write step. CI uploads verification metrics and its actual dependency/font inventory for final-tree reconciliation.

Native-size images, decoded phases, loop transition, original-logo comparison, orbit masks and 320/375px previews require visual inspection in addition to numerical checks. Resized previews do not verify a physical device or GitHub's image proxy. PR #2 remains Draft and unmerged until Tools is completed and final approval is given.

## Earlier Languages phases

### Language-only visual refinement

- HTML5 and CSS3 shields now use complete vector paths from Devicon pinned at `6a37858047b0e8d9c9c0e68f4a071fc410652e89`; the original portfolio SVG paths remain available in the frozen snapshot. This fixes incomplete internal numerals.
- TypeScript uses an optically enlarged, softly rounded **illustrative TS monogram**; the pinned upstream SVG still remains in the supplemental dataset for provenance.
- VBScript uses a neutral, explicitly labeled VBS outline rather than reusing an IDE trademark. Its original portfolio paths remain stored.
- No visual changes to the Frameworks or Tools generated assets in this phase.

### Languages CSS outline and orbital motion refinement (October 25, 2026)

- CSS3's upper horizontal shield seam is explicitly restored in the CairoSVG shape at original 128×128 geometry, so the contour sampler retains it rather than relying on antialiasing thresholds.
- The Languages renderer uses **36 frames × 150ms = 5.4 seconds** for a gentle, vertical-dominant weightless loop, with small horizontal drift and per-node phase offsets.
- The motion and particle pulse use integer-harmonic periodic functions so the GIF wraps without a discontinuity at the loop seam; GitHub Actions checks the seam numerically.
- Only `Languages & Markup` artwork is regenerated. Frameworks & Tools images and animation remain untouched.

### Minimal Languages presentation (October 25, 2026)

- Secondary status labels and horizontal/vertical constellation connectors are hidden **only for Languages**. Internal activity/tag data, the nebula, background stars, headings and footer remain intact.
- All ten names use the same 40px bold font and baseline offset, 120px below their icon centers. This improves phone-width readability and clears the official MoonBit contour throughout the float.
- Icon samples, TypeScript scale/corners, the CSS top seam, MoonBit source artwork, particle pulse and the 36-frame / 5.4s motion are unchanged.
- `scripts/verify_languages.py` checks rendered text/lines, actual PNG content, continuous-motion label clearance, all 36 decoded GIF frames, timing, exact periodic render endpoints and the encoded last-to-first frame delta. Visual inspection at desktop and phone widths remains required.
- Actions checks preserved artwork checksums and stages only the Languages GIF/PNG. If local and CI rendering match, the already-committed assets need no extra bot commit.

### Cosmic Dust / Origin Layer (October 25, 2026)

- Languages has a dedicated deep-navy background: an asymmetric, warped blue/violet cloud bank with a faint cyan-blue veil, dark pockets and low-opacity dust following the cloud density. Seeded, multiscale value noise creates the haze at quarter resolution, then Pillow upsamples it once. No external textures or new dependencies are used.
- Three static star depths combine many faint distant pinpoints, fewer uneven mid-field stars and nine softly glowing foreground stars. Brighter stars avoid icons, names, headings and footer; the nebula is attenuated behind the existing icon centers. No grids, connectors or secondary labels are introduced.
- The background is cached for the entire render. All Languages GIF frames share one palette with dithering disabled, keeping exposed background pixels exactly static and reducing palette shimmer and GIF size. Frameworks/Tools use their original background and encoding paths.
- The ten-node data, point samples, icon geometry/colors, text positions, particle pulse and floating offsets are unchanged. Against baseline `9733f251609e8a3c0231f13ceaef6854f39b1de5`, all 36 Languages foreground renders and all 18 Frameworks/Tools phases match pixel for pixel when supplied the same background.
- Verification also checks repeatable background pixels, dark backgrounds behind all ten icons and exact exposed-background stability across every decoded GIF frame. The 36-frame, 1600×780, 150ms/frame, 5.4s infinite loop and 18.7px minimum moving-icon/name clearance remain intact.
- Local assets: GIF **3,841,553 bytes** (previously 6,277,441; approximately 39% smaller), PNG **162,994 bytes**. Encoded last-to-first mean RGB delta **2.2938**, below the interior maximum **2.8928**; rendered endpoints at 0 and 2π match exactly.
- Visual review covers the PNG, decoded GIF frames 0/1/9/18/27/34/35, and 320px/375px previews. Physical-device playback and final aesthetic approval remain separate user review items.
