"""Build the GitHub profile README and its artwork from the yousofselim.com design.

Run: python3 tools/build_profile.py
Needs fonttools, brotli, uharfbuzz and Pillow (python3 -m pip install fonttools brotli uharfbuzz pillow).

Every SVG is drawn at the size GitHub shows it, so a 14px label in the source
is a 14px label on screen. Three widths cover the README column:

  phone  320  viewports up to 591px, and 768-879px (sidebar layout)
  mid    600  everything else up to 1153px
  wide   846  1154px and up (846px is the README column from 1280px)

Each width is used only where the column is at least ~85% of it, and art is
never scaled up, so type stays within 15% of its drawn size.

Backgrounds are transparent, so the art sits on GitHub's own page colour in
every theme; only media panels carry a fill. Type is Hanken Grotesk, shaped
with HarfBuzz (kerning included) and outlined to paths. Media is embedded.
Nothing loads at view time, and there are no scripts or animation.

The script also writes README.md, so copy, alt text and image names cannot drift.
"""
import base64
import io
from functools import lru_cache
from html import escape
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
MEDIA = ROOT / "tools/profile-media"
FONT = ROOT / "tools/profile-fonts/HankenGrotesk.woff2"

# Portfolio colours (styles.css and ui/css/00-tokens.css). Hairlines are ink at
# a fixed opacity, like the site's color-mix() hairlines, so they suit any ground.
THEMES = {
    "light": dict(ink="#17150f", muted="#5c574c", panel="#e4e0d7", on_ink="#f3efe6"),
    "dark": dict(ink="#f1ece1", muted="#a7a093", panel="#070705", on_ink="#12110e"),
}
HAIR, HAIR_STRONG = .12, .20
TIERS = {"phone": 320, "mid": 600, "wide": 846}
# Where each width is NOT shown. These sources must not mention the colour
# scheme: GitHub's <themed-picture> rewrites every source that does when a
# signed-in visitor has picked a theme, which would erase the width condition.
HIDE = {
    "phone": "(min-width: 592px) and (max-width: 767px), (min-width: 880px)",
    "mid": "(max-width: 591px), (min-width: 768px) and (max-width: 879px), (min-width: 1154px)",
    "wide": "(max-width: 1153px)",
}

SITE = "https://yousofselim.com"
RESUME = f"{SITE}/Yousof-Selim-Resume.pdf"

# Stroke icons from the portfolio (tools/build.mjs): 24px grid, 1.6 stroke.
ICONS = {
    "doc": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z"/><path d="M14 3v6h6M8 13h8m-8 4h5"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
    "github": '<path d="M9 19c-4 1-4-2-6-2m12 5v-4a3.5 3.5 0 0 0-1-3c3-.3 6-1.5 6-6a4.5 4.5 0 0 0-1.3-3.1A4 4 0 0 0 18.6 2S17.4 1.6 15 3a13 13 0 0 0-6 0C6.6 1.6 5.4 2 5.4 2a4 4 0 0 0-.1 3.9A4.5 4.5 0 0 0 4 9c0 4.5 3 5.7 6 6a3.5 3.5 0 0 0-1 3v4"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7 10v7m0-10v.1M11 17v-7m0 3a3 3 0 0 1 6 0v4"/>',
    "play": '<path d="m5 3 15 9L5 21Z"/><path d="m5 3 10 12m-10 6 10-12"/>',
    "appstore": '<rect x="3" y="3" width="18" height="18" rx="5"/><path d="m10 7 7 12M14 7 7 19M6 15h12"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m3 7 9 6 9-6"/>',
    "download": '<path d="M12 4v11m-4.5-4.5L12 15l4.5-4.5M5 20h14"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>',
}

PROJECTS = [
    dict(key="bupples", name="Bupples", status="Live on the App Store and Google Play",
         blurb="Split the bill, skip the awkward follow-up. Scan a receipt, tap who had what, and Bupples works out who owes whom.",
         chips=["Flutter", "Firebase", "Vertex AI"],
         phones=["bupples-profile.webp", "bupples-accent.webp", "bupples-settings.webp"],
         alt="the profile, accent editor and settings screens",
         links=[("case-study", f"{SITE}/work/bupples/"),
                ("app-store", "https://apps.apple.com/my/app/bupples/id6777620291"),
                ("google-play", "https://play.google.com/store/apps/details?id=com.bupples.bupples"),
                ("showcase", "https://github.com/yeegz/Bupples-showcase")]),
    dict(key="adelante", name="Adelante", status="Live on the App Store",
         blurb="A daily quote on your Home Screen, Lock Screen and Apple Watch, for the days you don\u2019t feel like opening an app.",
         chips=["Flutter", "Swift/SwiftUI", "Kotlin"],
         phones=["adelante-widgets.webp", "adelante-today.webp", "adelante-discover.webp"],
         alt="the widget gallery, Today and Discover screens",
         links=[("case-study", f"{SITE}/work/adelante/"),
                ("app-store", "https://apps.apple.com/us/app/adelante-daily-quotes/id6816598027"),
                ("showcase", "https://github.com/yeegz/adelante-showcase")]),
    dict(key="wayclub", name="WayClub", status="Guided demo with sample data",
         blurb="Student clubs plan events, get them approved and run sign-ups in one place, "
               "not across group chats, forms and spreadsheets.",
         chips=["Next.js", "NestJS", "PostgreSQL"],
         shot="wayclub-workspace.webp",
         alt="a club workspace with events, proposals and committee members, using fictional data",
         links=[("case-study", f"{SITE}/work/wayclub/"),
                ("demo", "https://wayclub-live-demo.web.app/home?tour=1"),
                ("showcase", "https://github.com/yeegz/WayClub-showcase")]),
    dict(key="photoshoot", name="Photoshoot", status="Live in your browser · Windows 1.0.1",
         blurb="Strike a pose, pick from 17 live effects, keep the strip. Nothing from your camera ever leaves your device.",
         chips=["TypeScript", "Electron", "MediaPipe"],
         shot="photoshoot-landing.webp",
         alt="the red photobooth landing page",
         links=[("case-study", f"{SITE}/work/photoshoot/"),
                ("open-app", "https://photoshoot-yeegz.web.app/app/"),
                ("windows", "https://github.com/yeegz/photoshoot/releases/tag/v1.0.1"),
                ("source", "https://github.com/yeegz/photoshoot")]),
    dict(key="codeatlas", name="CodeAtlas", status="Runs locally · source on GitHub",
         blurb="Green tests don\u2019t always mean nothing broke. CodeAtlas finds the tests a change really reaches, runs the code before and after, and signs what it saw.",
         chips=["TypeScript", "Node.js", "Vitest"],
         shot="codeatlas-workspace.webp",
         alt="the evidence workspace on a fixture repository",
         links=[("case-study", f"{SITE}/work/codeatlas/"),
                ("source", "https://github.com/yeegz/CodeAtlas")]),
]

# Text links under each project: (label, icon, primary, alt with NAME placeholder).
LINKS = {
    "case-study": ("Case study", "doc", True, "Read the NAME case study"),
    "app-store": ("App Store", "appstore", False, "Get NAME on the App Store"),
    "google-play": ("Google Play", "play", False, "Get NAME on Google Play"),
    "showcase": ("Showcase", "github", False, "Browse the NAME showcase on GitHub"),
    "demo": ("Try the demo", "globe", False, "Try the NAME demo"),
    "open-app": ("Open the app", "globe", False, "Open NAME in your browser"),
    "windows": ("Windows", "download", False, "Download NAME 1.0.1 for Windows"),
    "source": ("Source", "github", False, "Browse the NAME source on GitHub"),
}

# Pill buttons: (label, icon or None, primary).
BUTTONS = {
    "resume": ("Résumé", None, True),
    "recruiters": ("For recruiters", "doc", False),
    "portfolio": ("Portfolio", "globe", False),
    "email": ("Email me", "mail", True),
    "linkedin": ("LinkedIn", "linkedin", False),
}

SKILLS = [
    ("Mobile", ["Flutter", "Dart", "Riverpod", "Swift/SwiftUI", "Kotlin"]),
    ("Backend and data", ["TypeScript", "NestJS", "PostgreSQL", "Firebase", "REST APIs"]),
    ("Web", ["React", "Next.js", "JavaScript", "HTML/CSS", "WebGL2", "Electron"]),
    ("Testing and delivery", ["Flutter tests", "Vitest", "Playwright", "Firebase Emulator Suite",
                              "GitHub Actions", "App Store and Google Play releases"]),
    ("Also", ["Python", "Java (working knowledge)", "Vertex AI and Gemini", "MediaPipe", "Git"]),
]


# --- Type -----------------------------------------------------------------

@lru_cache
def hb_face():
    font = TTFont(FONT)
    font.flavor = None  # HarfBuzz reads TrueType, not WOFF2
    data = io.BytesIO()
    font.save(data)
    return hb.Face(hb.Blob(data.getvalue()))


@lru_cache
def hb_font(weight):
    font = hb.Font(hb_face())
    font.set_variations({"wght": weight})
    return font


UPEM = 1000
CAP = .697  # cap height / em, from OS/2


def shape(value, weight):
    font = hb_font(weight)
    buf = hb.Buffer()
    buf.add_str(value)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    for info in buf.glyph_infos:
        if info.codepoint == 0:
            raise ValueError(f"Missing glyph in {value!r}")
    return font, buf.glyph_infos, buf.glyph_positions


def measure(value, size, weight=400, track=0.0):
    _, infos, pos = shape(value, weight)
    return sum(p.x_advance for p in pos) * size / UPEM + track * size * len(infos)


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


GLYPHS = {}  # (weight, glyph id) -> path id, for the SVG being built
RIGHT = [0.0]  # rightmost text edge in the SVG being built


@lru_cache(maxsize=None)
def outline(weight, gid):
    pen = SVGPathPen(None, ntos=lambda v: num(round(v, 1)))
    hb_font(weight).draw_glyph_with_pen(gid, pen)
    return pen.getCommands()


def text(value, x, y, size, color, weight=400, track=0.0):
    """Shaped, kerned and outlined. Each glyph is defined once per SVG in font
    units and placed with <use>, which keeps files small. `track` is in em."""
    _, infos, pos = shape(value, weight)
    uses, ux = [], 0
    for info, p in zip(infos, pos):
        if outline(weight, info.codepoint):
            ref = GLYPHS.setdefault((weight, info.codepoint), f"g{len(GLYPHS):x}")
            dy = f' y="{p.y_offset}"' if p.y_offset else ""  # font units, y-up inside the flip
            uses.append(f'<use href="#{ref}" x="{num(ux + p.x_offset)}"{dy}/>')
        ux += p.x_advance + track * UPEM
    s = f"{size / UPEM:.5f}".rstrip("0")
    RIGHT[0] = max(RIGHT[0], x + ux * size / UPEM)
    return f'<g fill="{color}" transform="translate({num(x)} {num(y)}) scale({s} -{s})">{"".join(uses)}</g>'


def lines_for(tokens, joiner, size, weight, width, track):
    lines, current = [], []
    for token in tokens:
        if current and measure(joiner.join(current + [token]), size, weight, track) > width:
            lines.append(current)
            current = [token]
        else:
            current.append(token)
    return [joiner.join(line) for line in lines + [current]]


def wrap(value, size, weight, width, track=0.0, joiner=" "):
    """Greedy wrap, then balanced like CSS text-wrap: balance: the narrowest
    width that keeps the same number of lines. A list wraps between items."""
    tokens = value if isinstance(value, list) else value.split(" ")
    lines = lines_for(tokens, joiner, size, weight, width, track)
    if len(lines) > 1:
        lo, hi = width / 2, width
        for _ in range(14):
            mid = (lo + hi) / 2
            if len(lines_for(tokens, joiner, size, weight, mid, track)) > len(lines):
                lo = mid
            else:
                hi = mid
        lines = lines_for(tokens, joiner, size, weight, hi, track)
    return lines


# --- Drawing ----------------------------------------------------------------

def attrs(**kw):
    return "".join(f' {k.replace("_", "-")}="{num(v) if isinstance(v, float) else v}"' for k, v in kw.items() if v is not None)


def rect(x, y, w, h, r, **kw):
    return f"<rect{attrs(x=float(x), y=float(y), width=float(w), height=float(h), rx=float(r))}{attrs(**kw)}/>"


def rule(y, w, color):
    return f'<path d="M0 {num(y)}H{num(w)}" stroke="{color}" stroke-opacity="{HAIR}"/>'


def icon(name, x, y, size, color):
    return (f'<g transform="translate({num(x)} {num(y)}) scale({num(size / 24)})" fill="none" stroke="{color}" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


@lru_cache
def media(name, width):
    """Embed a source image at 2x its drawn width (never larger than the source)."""
    img = Image.open(MEDIA / name)
    if img.width > width * 2:
        img = img.resize((round(width * 2), round(img.height * width * 2 / img.width)), Image.LANCZOS)
    data = io.BytesIO()
    img.save(data, "WEBP", quality=82, method=6)
    return "data:image/webp;base64," + base64.b64encode(data.getvalue()).decode()


CLIPS = [0]


def clip_id():
    CLIPS[0] += 1
    return f"c{CLIPS[0]}"


def image(name, x, y, w, h, r, align="xMidYMid slice"):
    cid = clip_id()
    return (f'<clipPath id="{cid}">{rect(x, y, w, h, r)}</clipPath>'
            f'<image{attrs(x=float(x), y=float(y), width=float(w), height=float(h))} preserveAspectRatio="{align}" '
            f'clip-path="url(#{cid})" href="{media(name, round(w))}"/>')


def svg(name, w, h, title, body):
    defs = "".join(f'<path id="{ref}" d="{outline(*key)}"/>' for key, ref in GLYPHS.items())
    if RIGHT[0] > w + .5:
        raise ValueError(f"{name}: text runs to {RIGHT[0]:.1f}px, past the {w}px edge")
    CLIPS[0], RIGHT[0] = 0, 0.0
    GLYPHS.clear()
    h = round(h)
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
           f'<defs>{defs}</defs>{"".join(body)}</svg>\n')
    (ASSETS / name).write_text(out)


# --- Components -------------------------------------------------------------

def pill(y, h, parts, t, size, pad):
    """The availability pill: runs of (text, colour key, weight) on a hairline."""
    gap = size * .45
    width = pad * 2 + sum(measure(v, size, wt) for v, _, wt in parts) + gap * (len(parts) - 1)
    body = [rect(.5, y + .5, width - 1, h - 1, (h - 1) / 2, fill="none", stroke=t["ink"], stroke_opacity=HAIR_STRONG)]
    x, base = pad, y + h / 2 + size * CAP / 2
    for v, colour, wt in parts:
        body.append(text(v, x, base, size, t[colour], wt))
        x += measure(v, size, wt) + gap
    return body, width


def hero(theme, tier):
    t, W = THEMES[theme], TIERS[tier]
    title = ("Yousof Selim, Software Engineering student. I build and ship real apps. Two are live on the "
             "App Store. Available for an internship, 25 January to 23 April 2027. Subang Jaya, Malaysia.")
    lines = [("I build and", "ink"), ("ship real apps.", "ink"), ("Two are live on", "muted"), ("the App Store.", "muted")]
    if tier == "phone":
        # No portrait: on narrow screens GitHub shows the avatar just above the README.
        body = [text("Yousof Selim", 0, 18, 15, t["ink"], 500), text("Software Engineering student", 0, 39, 15, t["muted"])]
        size, lh = 32, 35
        first = 39 + 22 + size * CAP
        pill_size, pill_h, pad = 12.5, 30, 11
    else:
        name = 17 if tier == "wide" else 16
        body = [text("Yousof Selim", 0, 20, name, t["ink"], 500),
                text(" · Software Engineering student", measure("Yousof Selim", name, 500), 20, name, t["muted"])]
        size, lh = (46, 50) if tier == "wide" else (38, 42)
        first = 20 + 26 + size * CAP
        pill_size, pill_h, pad = 13, 32, 12
    for i, (value, colour) in enumerate(lines):
        body.append(text(value, 0, first + i * lh, size, t[colour], 600, -.025))
    pill_y = first + 3 * lh + size * .26 + 22
    parts = [("Available for an internship", "muted", 400), ("25 January to 23 April 2027", "ink", 500)]
    if pad * 2 + sum(measure(v, pill_size, wt) for v, _, wt in parts) + pill_size * .45 > W:
        parts = [("Internship", "muted", 400), ("25 January to 23 April 2027", "ink", 500)]
    pill_body, _ = pill(pill_y, pill_h, parts, t, pill_size, pad)
    body += pill_body
    loc = 13 if tier == "phone" else 13.5
    loc_base = pill_y + pill_h + 24 + loc * CAP
    if tier != "phone":
        # Portrait: a hairline frame, a ring of page colour, then the photo, as on the site.
        iw, frame_r, img_r = (250, 22, 15) if tier == "wide" else (196, 19, 13)
        ih, pad = iw / .8, 7
        fw, fh = iw + pad * 2, ih + pad * 2
        body += [rect(W - fw + .5, .5, fw - 1, fh - 1, frame_r, fill="none", stroke=t["ink"], stroke_opacity=HAIR_STRONG),
                 image("yousof-portrait.webp", W - fw + pad, pad, iw, ih, img_r)]
        loc_base = max(loc_base, fh - 3)
    body += [icon("pin", -1, loc_base - loc * CAP / 2 - 8, 16, t["muted"]),
             text("Subang Jaya, Malaysia", 21, loc_base, loc, t["muted"])]
    svg(f"hero-{theme}-{tier}.svg", W, loc_base + 4, title, body)
    return title


def section_head(title, lead, t, tier):
    W = TIERS[tier]
    size, lead_size = {"wide": (30, 17), "mid": (28, 16), "phone": (24, 15)}[tier]
    base, body = 30 + size * CAP, []
    for i, value in enumerate(wrap(title, size, 600, W, -.02)):
        body.append(text(value, 0, base + i * size * 1.15, size, t["ink"], 600, -.02))
    base += i * size * 1.15 + 14
    for value in wrap(lead, lead_size, 400, W):
        base += lead_size * 1.55
        body.append(text(value, 0, base, lead_size, t["muted"]))
    return body, base + 6


def heading(key, title, lead, theme, tier):
    body, h = section_head(title, lead, THEMES[theme], tier)
    svg(f"head-{key}-{theme}-{tier}.svg", TIERS[tier], h, f"{title} {lead}", body)


def chips(values, y, t, size):
    h, pad, gap = (28, 10, 8) if size >= 13 else (26, 9, 7)
    body, x = [], 0
    for value in values:
        w = measure(value, size, 500) + pad * 2
        body += [rect(x + .5, y + .5, w - 1, h - 1, 6, fill="none", stroke=t["ink"], stroke_opacity=HAIR_STRONG),
                 text(value, x + pad, y + h / 2 + size * CAP / 2, size, t["ink"], 500)]
        x += w + gap
    return body, h


def phones(names, x, y, w, h, t):
    """Three screens, the middle one in front, bleeding off the panel's lower edge (the site's media panel)."""
    cid = clip_id()
    body = [rect(x, y, w, h, 14, fill=t["panel"]),
            f'<clipPath id="{cid}">{rect(x, y, w, h, 14)}</clipPath><g clip-path="url(#{cid})">']
    cw, sw = h * .55, h * .49
    cx = x + (w - cw) / 2
    spots = [(cx - sw * .64, y + h * .24, sw, names[0]), (cx + cw - sw * .36, y + h * .24, sw, names[2]),
             (cx, y + h * .087, cw, names[1])]
    for px, py, pw, name in spots:
        ph, bezel = pw * 1300 / 600, pw * .028
        body += [rect(px - bezel, py - bezel, pw + bezel * 2, ph + bezel * 2, pw * .16, fill="#050505",
                      stroke="#ffffff", stroke_opacity=.14),
                 image(name, px, py, pw, ph, pw * .13)]
    body += ["</g>", rect(x + .5, y + .5, w - 1, h - 1, 13.5, fill="none", stroke=t["ink"], stroke_opacity=HAIR)]
    return body


def shot(name, x, y, w, h, t):
    return [image(name, x, y, w, h, 14, "xMidYMin slice"),
            rect(x + .5, y + .5, w - 1, h - 1, 13.5, fill="none", stroke=t["ink"], stroke_opacity=HAIR)]


def project(p, theme, tier):
    t, W = THEMES[theme], TIERS[tier]
    stack = f"{', '.join(p['chips'][:-1])} and {p['chips'][-1]}"
    title = f"{p['name']}. {p['status']}. {p['blurb']} Built with {stack}. The screenshot shows {p['alt']}."
    body = [rule(.5, W, t["ink"])]
    if tier == "wide":
        # Media on the right; the text column sits on the baseline so the links continue it.
        mw, mh, top = 470, 294, 28
        mx, col = W - mw, W - mw - 40
        h = top + mh
        body.append(text(p["status"], 0, top + 10, 13, t["muted"]))
        chip_body, ch = chips(p["chips"], h - 28, t, 13)
        blurb = wrap(p["blurb"], 16, 400, col)
        base = h - ch - 20 - (len(blurb) - 1) * 24
        body.append(text(p["name"], 0, base - 36, 24, t["ink"], 600, -.015))
        body += [text(v, 0, base + i * 24, 16, t["ink"]) for i, v in enumerate(blurb)]
        body += chip_body
    else:
        mid = tier == "mid"
        mx, mw, mh, top = 0, W, (300 if mid else 180), (26 if mid else 22)
        title_size, blurb_size, lh, chip_size, status = (23, 16, 24, 13, 13) if mid else (20, 15, 22, 12.5, 12.5)
        base = top + mh + 30
        body.append(text(p["status"], 0, base, status, t["muted"]))
        base += 12 + title_size * CAP + 8
        body.append(text(p["name"], 0, base, title_size, t["ink"], 600, -.015))
        base += 10
        for v in wrap(p["blurb"], blurb_size, 400, W):
            base += lh
            body.append(text(v, 0, base, blurb_size, t["ink"]))
        chip_body, ch = chips(p["chips"], base + 16, t, chip_size)
        body += chip_body
        h = base + 16 + ch
    if "phones" in p:
        body += phones(p["phones"], mx, top, mw, mh, t)
    else:
        body += shot(p["shot"], mx, top, mw, mh, t)
    svg(f"work-{p['key']}-{theme}-{tier}.svg", W, h, title, body)
    return title


def skills(theme, tier):
    t, W = THEMES[theme], TIERS[tier]
    lead = "Mostly Flutter and Firebase for the apps, and TypeScript for the web and the servers."
    body, y = section_head("Skills", lead, t, tier)
    y += 20
    size = 14 if tier == "phone" else 15
    label_w = {"wide": 210, "mid": 180, "phone": 0}[tier]
    for label, values in SKILLS:
        body.append(rule(y + .5, W, t["ink"]))
        if tier == "phone":
            y += 14 + 13 * CAP
            body.append(text(label, 0, y, 13, t["muted"]))
            y += 6
            for v in wrap(values, size, 400, W, joiner=" · "):
                y += size * 1.5
                body.append(text(v, 0, y, size, t["ink"]))
            y += 15
        else:
            rows = wrap(values, size, 400, W - label_w, joiner=" · ")
            base = y + 15 + size * CAP
            body.append(text(label, 0, base, size, t["muted"]))
            body += [text(v, label_w, base + i * size * 1.55, size, t["ink"]) for i, v in enumerate(rows)]
            y = base + (len(rows) - 1) * size * 1.55 + 16
    body.append(rule(y + .5, W, t["ink"]))
    title = "Skills. " + lead + " " + ". ".join(f"{label}: {', '.join(values)}" for label, values in SKILLS) + "."
    svg(f"skills-{theme}-{tier}.svg", W, y + 1, title, body)
    return title


def button(key, theme):
    """The site's small button: 36px pill, 14px label, 18px icon, 14px padding."""
    label, mark, primary = BUTTONS[key]
    t = THEMES[theme]
    h, size, pad, isz, gap = 36, 14, 14, 18, 8
    w = pad * 2 + measure(label, size, 500, -.005) + (isz + gap if mark else 0)
    fg = t["on_ink"] if primary else t["ink"]
    body = [rect(.5, .5, w - 1, h - 1, (h - 1) / 2, fill=t["ink"] if primary else "none",
                 stroke=t["ink"], stroke_opacity=1 if primary else HAIR_STRONG)]
    x = pad
    if mark:
        body.append(icon(mark, x, (h - isz) / 2, isz, fg))
        x += isz + gap
    body.append(text(label, x, h / 2 + size * CAP / 2, size, fg, 500, -.005))
    # 4px of air after the pill; with the space between links that makes an 8px gap.
    svg(f"btn-{key}-{theme}.svg", round(w + 4), h, label, body)


def link(key, theme):
    """The site's card links: icon and label, no pill; only the first link is ink."""
    label, mark, primary, _ = LINKS[key]
    t = THEMES[theme]
    colour = t["ink"] if primary else t["muted"]
    h, size, isz, gap = 28, 14, 16, 7
    w = isz + gap + measure(label, size, 500)
    body = [icon(mark, 0, (h - isz) / 2, isz, colour), text(label, isz + gap, h / 2 + size * CAP / 2, size, colour, 500)]
    svg(f"go-{key}-{theme}.svg", round(w + 16), h, label, body)


# --- README -----------------------------------------------------------------

def responsive(stem, label, href):
    """One <picture> per width. Outside its range each resolves to a 0x0 image, so
    exactly one is visible; inside it, the theme sources pick light or dark. No
    width attribute: art is shown at its drawn size and only ever shrinks.
    The link carries the description once, instead of three identical alts."""
    pictures = "".join(
        f'<picture><source media="{HIDE[tier]}" srcset="assets/blank.svg">'
        f'<source media="(prefers-color-scheme: dark)" srcset="assets/{stem}-dark-{tier}.svg">'
        f'<img src="assets/{stem}-light-{tier}.svg" alt=""></picture>'
        for tier in TIERS)
    return f'<a href="{href}" aria-label="{escape(label)}">{pictures}</a>'


def themed(prefix, key, alt, href, height):
    return (f'<a href="{href}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/{prefix}-{key}-dark.svg">'
            f'<img src="assets/{prefix}-{key}-light.svg" height="{height}" alt="{escape(alt)}"></picture></a>')


def block(inner):
    return f"<p>\n{inner}\n</p>"


NOTES = """<details>
<summary><b>Under the hood</b> · four problems and how I cracked them</summary>

#### Bupples: the payment that went nowhere

A owes B, and B owes C. The simplified plan says A should just pay C, which is neat until A actually pays and the app looks for a direct A → C debt to reduce. There isn’t one, so the payment reduced nothing. I changed settlement to pay down the original debts along the chain, so everyone’s balance still adds up. Money is kept in whole minor units, so nothing drifts by a cent. [The ledger decision](https://yousofselim.com/work/bupples/#challenges)

#### Adelante: widgets that agree without talking

The Flutter app, the iOS widgets and the Android widgets run in separate processes and can’t talk to each other. So they don’t need to: they all follow the same clock-based rotation rule and land on the same quote, offline, without waiting for the app to open. iOS also gets a precomputed timeline that fits WidgetKit’s refresh budget. [The widget architecture](https://yousofselim.com/work/adelante/#architecture)

#### WayClub: one database, no peeking

Every club shares one database, so the bug that matters is one club seeing another’s data. Instead of trusting every query to filter correctly, each request runs in a transaction that carries the caller’s verified claims, and PostgreSQL row-level security decides what they can see, under a role that can’t bypass it. Forget a filter and you still only see your own club. [The isolation decision](https://yousofselim.com/work/wayclub/)

#### CodeAtlas: the 500 hiding behind a green suite

A test suite can pass while a changed branch goes untested. On its authentication fixture, CodeAtlas spots an uncovered expired-session path, generates a test for it, and catches the response quietly changing from HTTP 401 to HTTP 500. [What works today](https://github.com/yeegz/CodeAtlas#current-implementation-status)

Bupples, Adelante and WayClub are closed source, but each has a public showcase repo.

</details>

<details>
<summary>Got a minute? Take a detour</summary>

My portfolio has [a working terminal](https://yousofselim.com/terminal/). Type `help` and see where it takes you.

Or play [Fallen Asteri](https://yeegz.itch.io/fallenasteri), a Godot platformer our team of three built. I set up our branch-and-pull-request workflow and worked on levels, animation, the HUD and combat tuning. [Source](https://github.com/yeegz/Fallen-Asteri)

</details>"""

FOOTER = "<sub>Bachelor of Software Engineering (Hons), Sunway University × Lancaster University. Graduating August 2027.</sub>"


def main():
    ASSETS.mkdir(exist_ok=True)
    alts = {}
    work_lead = "Five products, one developer on each: me."
    contact_title, contact_lead = "Hiring interns for January 2027?", "I\u2019d love to hear what your team is building. Remote or on site both work for me."
    for theme in THEMES:
        for key in BUTTONS:
            button(key, theme)
        for key in LINKS:
            link(key, theme)
        for tier in TIERS:
            alts["hero"] = hero(theme, tier)
            heading("work", "Selected work", work_lead, theme, tier)
            heading("contact", contact_title, contact_lead, theme, tier)
            alts["skills"] = skills(theme, tier)
            for p in PROJECTS:
                alts[p["key"]] = project(p, theme, tier)

    (ASSETS / "blank.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0"/>\n')

    sections = [
        block(responsive("hero", alts["hero"], f"{SITE}/")),
        block("\n".join([themed("btn", "resume", "Read my résumé (PDF)", RESUME, 36),
                         themed("btn", "recruiters", "Read the one-page recruiter overview", f"{SITE}/simple/", 36),
                         themed("btn", "portfolio", "Visit my portfolio at yousofselim.com", f"{SITE}/", 36)])),
        block(responsive("head-work", f"Selected work. {work_lead}", f"{SITE}/#work")),
    ]
    for p in PROJECTS:
        links = [themed("go", key, LINKS[key][3].replace("NAME", p["name"]), href, 28) for key, href in p["links"]]
        sections += [block(responsive("work-" + p["key"], alts[p["key"]], p["links"][0][1])),
                     block("\n".join(links))]
    sections += [
        block(responsive("skills", alts["skills"], f"{SITE}/#skills")),
        NOTES,
        block(responsive("head-contact", f"{contact_title} {contact_lead}", f"{SITE}/#contact")),
        block("\n".join([
            themed("btn", "email", "Email me at yousofselim2@gmail.com",
                   "mailto:yousofselim2@gmail.com?subject=Software%20Engineering%20internship%2C%20January%202027", 36),
            themed("btn", "linkedin", "Connect on LinkedIn", "https://www.linkedin.com/in/ysf-slm/", 36)])),
        FOOTER,
    ]
    (ROOT / "README.md").write_text("\n\n".join(sections) + "\n")
    print(f"Wrote README.md and {len(list(ASSETS.glob('*.svg')))} SVGs in assets/.")


if __name__ == "__main__":
    main()
