# Profile artwork

The current profile uses custom navigation buttons, a halftone portrait header, six linked project panels and matching practice/contact panels. Light and dark header variants follow the visitor’s theme. A short introduction and expandable project details preserve readable text. The graphics use the portfolio’s Archivo, Space Grotesk and Instrument Serif typefaces; text is converted to vector paths so GitHub does not need to load fonts. Every image has a descriptive text alternative in the README.

## Rebuild

Requires Python 3 and FontTools:

```sh
python3 -m pip install fonttools
python3 tools/build_profile.py
```

The three source fonts and their SIL Open Font Licenses are in `profile-fonts/`. Output includes `assets/profile-dark.svg`, `assets/profile-light.svg`, `assets/nav-*.svg`, `assets/selected-*.svg`, `assets/profile-practice.svg` and `assets/profile-contact.svg`. The header reuses the existing vector portrait from `assets/hero.svg`. The artwork has no scripts, external resources or continuous animation.

`build.py`, `yzlib.py` and the other SVGs belong to the previous profile treatment. They are retained as editable historical assets and are not used by the current README.
