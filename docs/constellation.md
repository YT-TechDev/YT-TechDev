# Skill Constellation — sectioned README artwork

This profile embeds generated GIFs, since GitHub README markdown cannot run React/TSX/WebGL. Output is explicitly **non-interactive**.

## Layout and editorial choices

The previous 20-node poster was difficult to read on phones, especially the bottom two rows. The three sections now contain **25 nodes** into three independently generated star maps:

- **Languages & Markup (10):** HTML, CSS, JavaScript, TypeScript, VBScript, Python, Java, MoonBit, C++, Rust (ordered from frontend/web through scripting toward backend/systems)
- **Frameworks & Runtimes (6):** React, Next.js, Node.js, R3F, Three.js, WebAssembly
- **Tools & Platforms (9):** PostgreSQL, Docker, Git, Cloudflare, Linux, VS Code, Blender, ChatGPT, Claude

Frameworks now uses **Quiet Orbits / Structure**, with two shared elliptical paths behind the original six particle logos. Tools retains its original three-column layout and awaits its Space Station / Observatory design phase. The completed Languages image is a distinct 5-column × 2-row, 1600×780 layout, arranged for left-to-right frontend → backend reading. It displays only particle icons and language names, without secondary status labels or connector lines. Brightness is intentionally high across all groups and conveys **no proficiency ranking**. Internal activity metadata is retained: MoonBit is used in [Web Interactive Flow](https://github.com/YT-TechDev/web-interactive-flow), based on the public MoonBit/WebAssembly runtime implementation; C++ and Rust remain Exploring. ChatGPT/Claude are explicitly AI tools, not programming languages.

## Sources

- Frozen portfolio outline dataset: `data/icon-paths.json` from `YT-TechDev/yt-techdev-portfolio` at `6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27`.
- Repaired TypeScript, PostgreSQL, Docker and Git outlines and other supplemental marks: `data/supplemental-icons.json` from Simple Icons pinned at `90646e4bf7f3b89df6c37e65baf3e7bc759a517c`.
- MoonBit is extracted as **outline and interior-edge particle samples** from the official `moonbitlang/moonbit-docs` `next/_static/logo.png`, pinned to commit `50bbd2f59ba80ed046b6ecad57c7e8507ca06e9e` (repository copy `assets/moonbit-official.png`). The earlier illustrative crescent/M is no longer used for the Languages renderer.
- React / Next.js / R3F / WebAssembly and VS Code / ChatGPT have illustrative symbols. Other normalized logo outlines come from the pinned sources.

Neither RAOS nor Assembly are listed. The portfolio source is referenced, not mutated.

## Regeneration

```bash
python -m pip install -r scripts/requirements.txt
python scripts/render_sections.py --only frameworks
python scripts/verify_frameworks.py --determinism --protected
python scripts/verify_languages.py
```

The canonical Frameworks command defaults to **64 frames × 100ms = 6.4 seconds** at 1200×560. Its PNG is a neutral, undrifted/unpulsed pose with orbital lights at phase zero; it is a lossless RGB poster, not a decoded GIF frame. `--frames` remains available for disposable experiments, but the production verifier requires 64 frames. Languages still supports `--only languages` (36×150ms), and Tools still supports `--only tools` (18 frames, original encoding). Section selection writes only the chosen pair of images. The old combined assets were removed as obsolete.

Frozen Languages verification uses CairoSVG and system fonts/FreeType in addition to the pinned Python requirements. The approved CI-compatible environment uses system FreeType 2.14.3; a machine with a different SVG rasterizer can reject the frozen Languages PNG. Do not regenerate or replace Languages to make a Frameworks change pass. Frameworks' audited contour fixture removes this source of silhouette variation from its production rendering.

## Review gate

- [ ] Exact final content passes the section-aware workflow and both verifiers
- [ ] Inspect Quiet Orbits PNG/GIF, all six identities, protected arcs and loop transition
- [ ] Preview all three GIFs at phone width via the draft PR
- [ ] Confirm labels, clipping, the official MoonBit contour and color contrast

Do not merge before visual approval. No changes to public profile main until the PR is merged.

## Quiet Orbits / Structure (October 25, 2026)

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
