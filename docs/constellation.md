# Skill Constellation — GitHub profile artwork

A GitHub profile README **cannot execute React/TSX, WebGL or an interactive Canvas**. This repository renders a static SVG fallback directly in the README, and provides a separate reproducible animated GIF export.

## Provenance

- Technology SVG paths are a frozen subset of `YT-TechDev/yt-techdev-portfolio` at commit `6e4ea4fdbea13d57e7eb4f0f120452a2baf63a27`.
- Upstream path source: `components/home/Skills/particle/svgPaths.ts`.
- Rust icon is from [Simple Icons](https://github.com/simple-icons/simple-icons), CC0.
- React / Next.js / R3F small compositions are redrawn as simple outline primitives rather than claiming to be upstream SVG shapes.
- No connection to GitHub contribution statistics; visual activity categories are manually curated.

## Export

```bash
python -m pip install -r scripts/requirements.txt
python scripts/render_constellation.py --out assets/constellation.gif
python scripts/render_constellation.py --static --out assets/constellation.png
```

The GitHub Actions workflow renders the images and pushes generated GIF/PNG binaries when permitted by repository workflow settings. The committed `assets/constellation.svg` remains the README's always-visible lightweight default until the animation is reviewed. Switching the README to GIF is a separate visual approval step.

## Editorial safety

- `building`: linked to current public work.
- `used`: used in engineering workflows; not a proficiency assessment.
- `exploring`: interest without competence claims (Rust).
- No assembly listing; RAOS is intentionally not listed prior to public release.
- Do not use these labels as live automated telemetry.
- Profile repository and source portfolio are independent: no portfolio edits are required.

## Testing

The PR should not be merged without validating successful rendering and GitHub Markdown preview. In a local environment, test GIF frame count (28), PNG/GIF geometry (1200×620) and text readability on mobile. Generated visuals are non-interactive.
