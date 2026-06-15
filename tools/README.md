# Build pipeline — @yeegz profile README

Every visual in the profile `README.md` is a **hand-built, self-contained SVG**.
Nothing loads from a third-party badge or stats service. This is deliberate:
GitHub renders README SVGs inside a sandboxed `<img>`, which strips JavaScript and
blocks external fonts/images. So the build inlines everything —

- **Fonts** (Archivo / JetBrains Mono / Space Grotesk / Amiri) are subsetted to the
  exact glyphs used and embedded as base64 `woff2` via `@font-face` data-URIs.
- **The halftone portrait** in the hero is sampled from a photo into vector dots
  (`yzlib.halftone`) — not an embedded raster.
- **Motion** (the pulse dots, the green scan sweep) is SMIL, which the sandbox plays.

The result is one cohesive "specimen archive" identity that matches yeegz.github.io
and renders identically for every viewer, on GitHub light **and** dark.

## Regenerate

Requires Python 3 with `pillow`, `fonttools`, and `brotli`:

```bash
pip install pillow fonttools brotli
./fetch-fonts.sh            # downloads the 4 source fonts into ./fonts
python3 build.py            # writes all SVGs into ../assets
```

- `yzlib.py` — design tokens, font subsetting/embedding, text measurement, halftone.
- `build.py` — composes every asset (hero, profile, stack, project cards, proof, CTA).
- Override paths with env vars `YZ_OUT`, `YZ_FONTS`, `YZ_NICHE` if needed.
