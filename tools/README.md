# Profile artwork

The current profile uses a static header for light and dark themes, followed by readable Markdown. The graphics use the portfolio’s Archivo, Space Grotesk and Instrument Serif typefaces; text is converted to vector paths so GitHub does not need to load fonts. Every image has a descriptive text alternative in the README.

## Rebuild

Requires Python 3 and FontTools:

```sh
python3 -m pip install fonttools
python3 tools/build_profile.py
```

The three source fonts and their SIL Open Font Licenses are in `profile-fonts/`. Output is `assets/profile-dark.svg` and `assets/profile-light.svg`. The artwork has no scripts, external resources or continuous animation.

`build.py`, `yzlib.py` and the other SVGs belong to the previous profile treatment. They are retained as editable historical assets and are not used by the current README.
