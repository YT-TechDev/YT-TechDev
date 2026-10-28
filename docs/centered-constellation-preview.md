# Centered constellation headings — visual review

This Draft PR experiment displays three full-width GIFs in a **single README paragraph**, eliminating Markdown block margins between images. Each GIF draws a larger (40 px vs previous 25 px) centered heading, along with a centered eyebrow and subtitle. Each original source GIF is immutable.

The output is produced by `scripts/render_centered_constellation.py`. The renderer reuses exactly the per-frame RGB colors already present in each approved source GIF, preserving **all pixels below y=120** and the original frame count, duration and looping. New headings occupy the original header region. The generator rejects color loss, particle differences, heading shimmer or timing changes.

Because GitHub sanitizes inline CSS, this preview relies on contiguous `<img width="100%" align="top" />` elements inside a single paragraph instead of `margin:0`. **True zero CSS line-box spacing is not guaranteed**; inspect the rendered README on desktop and 320/375px mobile before merging. No original images, particle physics, or original generators are modified.
