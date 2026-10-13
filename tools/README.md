# Profile artwork

The profile follows yousofselim.com: Hanken Grotesk, the portfolio's ink and muted colours, its 36px buttons, 28px chips, availability pill, framed portrait and media panels, and the same copy as the homepage.

## Rebuild

```sh
python3 -m pip install fonttools brotli uharfbuzz pillow
python3 tools/build_profile.py
```

The script writes `README.md` and every file in `assets/`, so copy, alt text and file names cannot drift apart. Edit the content in `build_profile.py` (`PROJECTS`, `SKILLS`, `NOTES`, the hero and headings), never in `README.md` directly.

## How it fits GitHub

- **Drawn at display size.** Each piece of art exists at three widths: phone (320), mid (600) and wide (846, the README column from 1280px). A width is only used where the column is at least about 85% of it, and images have no `width` attribute, so they are never scaled up. A 14px label in the source is a 14px label on screen, give or take 15%.
- **Transparent.** Only media panels have a fill. Text, hairlines and frames sit directly on GitHub's own background, so nothing looks pasted on in light, dark or dimmed themes.
- **Width and theme are chosen separately.** A signed-in visitor who has picked a theme in GitHub settings gets every `<source>` that mentions `prefers-color-scheme` rewritten by GitHub's `<themed-picture>` script, which erases any width condition in that same query. So each width is its own `<picture>`. Its first source hides it outside its range (a 0 × 0 `blank.svg`), and its remaining sources choose only the theme. Exactly one of the three is visible at a time.
- **One description per artwork.** The three pictures share one link, which carries the description as `aria-label`. The images have empty alt text, so screen readers don't read it three times.
- **Self-contained.** Type is shaped with HarfBuzz (with kerning) and outlined. Each glyph is defined once per SVG and placed with `<use>`. Media is embedded at 2× its drawn size. No scripts, fonts or network requests are needed at view time.

Icons are the portfolio's own stroke icons (`tools/build.mjs` in the portfolio repository), copied into `ICONS`. Hanken Grotesk and its SIL Open Font License are in `profile-fonts/`. The portfolio's revision 5 (in progress, uncommitted, 14 October) switches to Schibsted Grotesk; if that ships, point `FONT` at the new woff2 and rebuild.

## Checking a change

Render the README with GitHub's own Markdown API and look at it at phone, mid and wide widths, in light and dark, and with an explicit GitHub theme:

```sh
gh api -X POST markdown -F text=@README.md -f mode=gfm -f context=yeegz/yeegz > preview.html
```

The README column is 846px from a 1280px viewport, `viewport − 434` from 1012 to 1279, `viewport − 370` from 768 to 1011, and `viewport − 82` below 768.

Older generators (`build.py`, `yzlib.py`, `fetch-fonts.sh`) and their fonts and icons are historical. `build_profile.py` is the only one used by the current README. See [design research](design-research.md) for the profiles compared in October.
