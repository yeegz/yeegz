# Profile artwork

The profile follows the October 2026 portfolio redesign: Hanken Grotesk, warm paper and charcoal, a single natural portrait, rounded media frames and real product screenshots. The README keeps ownership, status, availability and skills as native text, with descriptive alternatives for artwork and button links so they remain searchable and readable without images.

## Rebuild

Requires Python 3, FontTools and Brotli:

```sh
python3 -m pip install fonttools brotli
python3 tools/build_profile.py
```

The generator builds 48 SVGs: the header and five project panels in light/dark and desktop/mobile variants, plus twelve custom icon buttons in both themes. `README.md` selects them with `<picture>`, following [GitHub’s documented theme-aware image pattern](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github#adding-an-image-to-suit-your-visitors). At viewport widths up to 600px, artwork switches to a dedicated mobile composition.

Hanken Grotesk and its SIL Open Font License are in `profile-fonts/`. Lettering is converted to paths; source media is embedded. The SVGs have no scripts, external requests or animation. Accessible descriptions live in the README and each SVG title. Links are native HTML or Markdown anchors, outside the artwork.

The generator uses the portfolio’s exact paper, ink and muted colors. Screenshots retain their product colors in both themes. Header text and project status are maintained separately in `build_profile.py` and `README.md`; update both when the introduction changes.

## Research and content

- Design source: [portfolio](https://yousofselim.com/), including its `docs/design-system.md`, `styles.css` and `ui/css/00-tokens.css` at portfolio commit `244383f`.
- Content source: the portfolio’s [recruiter page](https://yousofselim.com/simple/) and five linked case studies, reviewed 7 October 2026.
- Availability uses the portfolio’s exact dates and qualified university-placement wording. It does not repeat the previous unsupported sponsorship claim.
- Photoshoot uses the actual red photobooth landing page. CodeAtlas uses the fixture-repository evidence workspace and is described as local tooling. WayClub is explicitly a guided interface demo with fictional data.

## Validation

Rebuild, then check the README at desktop and phone widths in light and dark modes. Verify all 48 SVGs parse, all referenced assets exist, images load, links remain readable, and the document has no horizontal overflow. Check the rendered GitHub preview before publishing because GitHub controls the Markdown styling.

Older unreferenced artwork, font files and build scripts remain in the repository as historical sources. `build_profile.py` is the sole generator for the current README.

## Custom buttons

The action buttons use Hanken Grotesk, portfolio ink/paper fills, 48px pill geometry and recognizable destination icons. Primary actions are filled; secondary actions are outlined. Bootstrap icon sources and their MIT license live in `profile-icons/`; `download.svg` is an original geometric download icon. Buttons remain real links and each has a project-specific accessible label.

See [design research](design-research.md) for the compared profiles and the choices made for this one.
