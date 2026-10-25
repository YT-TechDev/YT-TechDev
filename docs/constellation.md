# Skill Constellation — GitHub profile artwork

This repository's profile README embeds a generated **animated GIF**; GitHub README pages do not execute React/TSX, WebGL or interactive canvases.

## Provenance and repairs

- The original portfolio paths remain pinned in `data/icon-paths.json` from `YT-TechDev/yt-techdev-portfolio` commit `6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27` (`components/home/Skills/particle/svgPaths.ts`).
- **TypeScript, PostgreSQL, Docker and Git** were distorted by a heuristic SVG viewBox in the first iteration. These are now rendered using explicitly normalized 24×24 paths.
- Repaired icon paths and additional C++, Linux, WebAssembly, Three.js, Blender, Claude paths are from [Simple Icons](https://github.com/simple-icons/simple-icons) pinned at commit `90646e4bf7f3b89df6c37e65baf3e7bc759a517c`; stored as `data/supplemental-icons.json`.
- JavaScript, Node.js, Python and Cloudflare continue to use the pinned portfolio paths.
- React/Next.js/R3F are locally drawn particle motifs. VS Code is an **illustrative code symbol**, ChatGPT is an **abstract particle knot**, not their official marks.

## Editorial semantics

- **Building**: represented in active public development.
- **Used**: appears in projects or tooling workflows, not an expertise rating.
- **Exploring**: learning or interest, not professional proficiency (C++ and Rust).
- **AI tool**: ChatGPT and Claude are tools, not programming-language competencies.

No GitHub stats are queried; brightness is a curated activity visualization. Assembly and RAOS are deliberately not listed.

## Rendering

```bash
python -m pip install -r scripts/requirements.txt
python scripts/render_constellation.py --out assets/constellation.gif
python scripts/render_constellation.py --static --out assets/constellation.png
```

Generated images are committed by GitHub Actions when permitted. The README uses GIF and PNG is the static fallback. The older 12-icon SVG has been removed rather than retained as an inconsistent fallback.

## Review before merging

- [ ] TypeScript, PostgreSQL, Docker and Git display complete recognizable outlines.
- [ ] 20 nodes display, in 4 columns by 5 rows; verify phone-scale text.
- [ ] GIF is animated with 24 frames at 1200×960.
- [ ] Make a final GitHub PR visual check before merge.

The portfolio repository remains untouched.
