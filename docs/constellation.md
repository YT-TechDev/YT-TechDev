# Skill Constellation — sectioned README artwork

This profile embeds generated GIFs, since GitHub README markdown cannot run React/TSX/WebGL. Output is explicitly **non-interactive**.

## Layout and editorial choices

The previous 20-node poster was difficult to read on phones, especially the bottom two rows. This iteration splits **21 nodes** into three independently generated star maps:

- **Languages (6):** TypeScript, JavaScript, Python, MoonBit, C++, Rust
- **Frameworks & Runtimes (6):** React, Next.js, Node.js, R3F, Three.js, WebAssembly
- **Tools & Platforms (9):** PostgreSQL, Docker, Git, Cloudflare, Linux, VS Code, Blender, ChatGPT, Claude

The 3-column layout makes each icon and caption larger in the rendered README. Brightness is intentionally high across all groups, including `Exploring`, and conveys **no proficiency ranking**. MoonBit is marked as used in [Web Interactive Flow](https://github.com/YT-TechDev/web-interactive-flow) based on the public MoonBit/WebAssembly runtime implementation. C++ and Rust remain Exploring. ChatGPT/Claude are explicitly AI tools, not programming languages.

## Sources

- Frozen portfolio outline dataset: `data/icon-paths.json` from `YT-TechDev/yt-techdev-portfolio` at `6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27`.
- Repaired TypeScript, PostgreSQL, Docker and Git outlines and other supplemental marks: `data/supplemental-icons.json` from Simple Icons pinned at `90646e4bf7f3b89df6c37e65baf3e7bc759a517c`.
- MoonBit has an **illustrative moon/M symbol**, not its official brand logo.
- React / Next.js / R3F / WebAssembly and VS Code / ChatGPT have illustrative symbols. Other normalized logo outlines come from the pinned sources.

Neither RAOS nor Assembly are listed. The portfolio source is referenced, not mutated.

## Regeneration

```bash
python -m pip install -r scripts/requirements.txt
python scripts/render_sections.py
```

The renderer emits PNG and 18-frame GIFs for each section (six files). GitHub Actions verifies dimensions (1200×560, 1200×560, 1200×810) and frame counts, then commits the generated assets. The old combined `assets/constellation.gif` and `assets/constellation.png` are removed as obsolete.

## Review gate

- [ ] Render workflows PASS on the latest branch HEAD
- [ ] Inspect the actual updated PNGs, not only automated assertions
- [ ] Preview all three GIFs at phone width via the draft PR
- [ ] Confirm labels, clipping, MoonBit illustrative mark and color contrast

Do not merge before visual approval. No changes to public profile main until the PR is merged.
