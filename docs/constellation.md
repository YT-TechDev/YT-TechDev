# Skill Constellation — sectioned README artwork

This profile embeds generated GIFs, since GitHub README markdown cannot run React/TSX/WebGL. Output is explicitly **non-interactive**.

## Layout and editorial choices

The previous 20-node poster was difficult to read on phones, especially the bottom two rows. The three sections now contain **25 nodes** into three independently generated star maps:

- **Languages & Markup (10):** HTML, CSS, JavaScript, TypeScript, VBScript, Python, Java, MoonBit, C++, Rust (ordered from frontend/web through scripting toward backend/systems)
- **Frameworks & Runtimes (6):** React, Next.js, Node.js, R3F, Three.js, WebAssembly
- **Tools & Platforms (9):** PostgreSQL, Docker, Git, Cloudflare, Linux, VS Code, Blender, ChatGPT, Claude

Frameworks and tools retain their validated 3-column layouts, without any new edits this phase. The Languages image is a distinct 5-column × 2-row, 1600×780 layout, arranged for left-to-right frontend → backend reading. Brightness is intentionally high across all groups, including `Exploring`, and conveys **no proficiency ranking**. MoonBit is marked as used in [Web Interactive Flow](https://github.com/YT-TechDev/web-interactive-flow) based on the public MoonBit/WebAssembly runtime implementation. C++ and Rust remain Exploring. ChatGPT/Claude are explicitly AI tools, not programming languages.

## Sources

- Frozen portfolio outline dataset: `data/icon-paths.json` from `YT-TechDev/yt-techdev-portfolio` at `6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27`.
- Repaired TypeScript, PostgreSQL, Docker and Git outlines and other supplemental marks: `data/supplemental-icons.json` from Simple Icons pinned at `90646e4bf7f3b89df6c37e65baf3e7bc759a517c`.
- MoonBit is extracted as **outline and interior-edge particle samples** from the official `moonbitlang/moonbit-docs` `next/_static/logo.png`, pinned to commit `50bbd2f59ba80ed046b6ecad57c7e8507ca06e9e` (repository copy `assets/moonbit-official.png`). The earlier illustrative crescent/M is no longer used for the Languages renderer.
- React / Next.js / R3F / WebAssembly and VS Code / ChatGPT have illustrative symbols. Other normalized logo outlines come from the pinned sources.

Neither RAOS nor Assembly are listed. The portfolio source is referenced, not mutated.

## Regeneration

```bash
python -m pip install -r scripts/requirements.txt
python scripts/render_sections.py
```

The renderer supports all three sections, but this phase runs **`python scripts/render_sections.py --only languages`** and verifies only the language PNG and 18-frame GIF at 1600×780. Frameworks and Tools binaries remain unchanged. The old combined `assets/constellation.gif` and `assets/constellation.png` are removed as obsolete.

## Review gate

- [ ] Language-only workflow PASS on the latest branch HEAD
- [ ] Inspect the updated Languages PNG; specifically TypeScript corners/scale and official MoonBit rabbit silhouette, plus HTML, CSS, Java, VBScript.
- [ ] Preview all three GIFs at phone width via the draft PR
- [ ] Confirm labels, clipping, MoonBit illustrative mark and color contrast

Do not merge before visual approval. No changes to public profile main until the PR is merged.

### Language-only visual refinement

- HTML5 and CSS3 shields now use complete vector paths from Devicon pinned at `6a37858047b0e8d9c9c0e68f4a071fc410652e89`; the original portfolio SVG paths remain available in the frozen snapshot. This fixes incomplete internal numerals.
- TypeScript uses an optically enlarged, softly rounded **illustrative TS monogram**; the pinned upstream SVG still remains in the supplemental dataset for provenance.
- VBScript uses a neutral, explicitly labeled VBS outline rather than reusing an IDE trademark. Its original portfolio paths remain stored.
- No visual changes to the Frameworks or Tools generated assets in this phase.
