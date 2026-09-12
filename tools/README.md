# Profile artwork

The current profile uses custom navigation buttons, a halftone portrait header, six linked project panels and matching practice/contact panels. Light and dark header variants follow the visitor’s theme. A short introduction and expandable project details preserve readable text. The project graphics use the portfolio’s Archivo, Space Grotesk and Instrument Serif typefaces. The restored original header retains its Archivo, Space Grotesk and technical-label treatment. Latin lettering is converted to vector paths; the original embedded Amiri font preserves the Arabic name without external font requests. Every image has a descriptive text alternative in the README.

## Rebuild

Requires Python 3 and FontTools:

```sh
python3 -m pip install fonttools
python3 tools/build_profile.py
```

The three source fonts and their SIL Open Font Licenses are in `profile-fonts/`. Output includes `assets/profile-dark.svg`, `assets/profile-light.svg`, `assets/nav-*.svg`, `assets/selected-*.svg`, `assets/profile-practice.svg` and `assets/profile-contact.svg`. The header adapts the original composition from `assets/hero.svg`, including the vector portrait, Arabic name, dotted texture, wide name lockup and corner details. The artwork has no scripts, external resources or continuous animation.

`build.py`, `yzlib.py` and the other SVGs belong to the previous profile treatment. They are retained as editable historical assets and are not used by the current README.

## Product cards and icons

Project artwork now uses current portfolio images, with separate icon-led action links in the README. At viewport widths up to 600px, a stacked SVG composition preserves readable project copy. Desktop compositions place product evidence beside the title and summary.

`profile-media/` contains unmodified source media copied from the portfolio and the WayClub public showcase. Bupples uses only the September 2026 profile, settings and accent captures supplied by the owner. Photoshoot uses the existing portfolio product illustration and is labeled as artwork. CodeAtlas is an architecture diagram, not a claim of a released web UI.

`profile-icons/` contains Bootstrap Icons from https://github.com/twbs/icons, with its MIT license. The generator embeds icon paths directly; image-button links remain native HTML anchors with project-specific alternative labels. No external badge service is used.
