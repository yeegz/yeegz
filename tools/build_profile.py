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
FONT = ROOT / "tools/profile-fonts/SchibstedGrotesk.woff2"  # the portfolio's typeface

# Portfolio colours (styles.css and ui/css/00-tokens.css). Hairlines are ink at
# a fixed opacity, like the site's color-mix() hairlines, so they suit any ground.
THEMES = {
    "light": dict(ink="#111114", muted="#5d5d66", panel="#e8e8eb", on_ink="#f5f5f7"),
    "dark": dict(ink="#f2f2f4", muted="#a1a1aa", panel="#1c1c1f", on_ink="#111113"),
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
    dict(key="bupples", name="Bupples", status="App Store and Google Play · 1.5.0",
         blurb="Split the bill, skip the awkward follow-up. Scan a receipt, tap who had what, and Bupples works out who owes whom, to the cent.",
         chips=["Flutter", "Firebase", "Vertex AI"],
         phones=["bupples-receipt-2026-11.webp", "bupples-home-2026-11.webp", "bupples-bubbles-2026-11.webp"],
         alt="the receipt claim, Home and hangout balance screens",
         links=[("case-study", f"{SITE}/work/bupples/"),
                ("app-store", "https://apps.apple.com/my/app/bupples/id6777620291"),
                ("google-play", "https://play.google.com/store/apps/details?id=com.bupples.bupples"),
                ("showcase", "https://github.com/yeegz/Bupples-showcase")]),
    dict(key="pulse", name="Pulse", status="In development · team project",
         blurb="A city of about 150 residents that lives on its own. Ask anyone why they did something, change the city in plain English, and replay the day.",
         chips=["TypeScript", "three.js", "Fastify"],
         shot="pulse-city.webp",
         alt="the simulated city from above, with its districts and streets",
         links=[("case-study", f"{SITE}/work/pulse/"),
                ("demo", "https://pulse-ihzwsnnyfa-as.a.run.app")]),
    dict(key="keepwell", name="Keepwell", status="Live demo · pre-pilot",
         blurb="Maintenance for estates, factories, campuses and hotels. The technician\u2019s app keeps working in a plant room with no signal, and two people can never be promised the same spare part.",
         chips=["Java", "Spring Boot", "PostgreSQL", "Angular"],
         shot="keepwell-overview.webp",
         alt="the manager\u2019s overview with the jobs that need a decision, on sample data",
         links=[("case-study", f"{SITE}/work/keepwell/"),
                ("demo", "https://keepwell-951434273932.asia-southeast1.run.app"),
                ("showcase", "https://github.com/yeegz/keepwell-showcase")]),
    dict(key="hostmortem", name="Hostmortem", status="Replay live · v0.1",
         blurb="It was fine, then it wasn\u2019t, then someone rebooted it. Hostmortem keeps the minutes before on a Linux box and says what it knows, suspects and could not see.",
         chips=["C++20", "Linux", "SQLite"],
         shot="hostmortem-replay.webp",
         alt="the replay of a real upstream DNS outage on a five-lane tape, with the verdict underneath",
         links=[("case-study", f"{SITE}/work/hostmortem/"),
                ("demo", f"{SITE}/hostmortem-showcase/"),
                ("showcase", "https://github.com/yeegz/hostmortem-showcase")]),
    dict(key="planket", name="Planket", status="App Store · web app live",
         blurb="See when your friends are free and send a plan in three taps. Your calendar stays private: friends see busy time, never what you are doing.",
         chips=["Next.js", "Capacitor", "Supabase"],
         phones=["planket-plan.webp", "planket-calendar.webp", "planket-friends.webp"],
         alt="the plan, shared calendar and friends screens",
         links=[("case-study", f"{SITE}/work/planket/"),
                ("app-store", "https://apps.apple.com/my/app/planket/id6825034126"),
                ("open-app", "https://planket-yeegz.web.app"),
                ("showcase", "https://github.com/yeegz/planket-showcase")]),
    dict(key="photoshoot", name="Photoshoot", status="Web app and Windows 1.5.1",
         blurb="Strike a pose, pick from 52 live effects and reactive face masks, keep the strip. Nothing from your camera leaves your device.",
         chips=["TypeScript", "Electron", "WebGL2", "MediaPipe"],
         shot="photoshoot-landing-v151.webp",
         alt="the Photoshoot product site for version 1.5.1",
         links=[("case-study", f"{SITE}/work/photoshoot/"),
                ("open-app", "https://photoshoot-yeegz.web.app/app/"),
                ("windows", "https://github.com/yeegz/photoshoot/releases/tag/v1.5.1"),
                ("source", "https://github.com/yeegz/photoshoot")]),
]

# Text links under each project: (label, icon, primary, alt with NAME placeholder).
LINKS = {
    "case-study": ("Case study", "doc", True, "Read the NAME case study"),
    "app-store": ("App Store", "appstore", False, "Get NAME on the App Store"),
    "google-play": ("Google Play", "play", False, "Get NAME on Google Play"),
    "showcase": ("Showcase", "github", False, "Browse the NAME showcase on GitHub"),
    "demo": ("Live demo", "globe", False, "Try the NAME live demo, an interactive preview with sample data"),
    "open-app": ("Open the app", "globe", False, "Open NAME in your browser"),
    "windows": ("Windows", "download", False, "Download NAME 1.5.1 for Windows"),
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
    ("Mobile", ["Flutter", "Dart", "Riverpod", "Swift/SwiftUI", "Kotlin", "Capacitor"]),
    ("Backend and data", ["TypeScript", "Java", "Spring Boot", "NestJS", "PostgreSQL", "Supabase", "Firebase", "SQLite"]),
    ("Systems", ["C++20", "Linux", "CMake", "Docker"]),
    ("Web", ["React", "Next.js", "Angular", "JavaScript", "HTML/CSS", "WebGL2", "Electron"]),
    ("Testing and delivery", ["Flutter tests", "Vitest", "Playwright", "JUnit", "Fuzzing and sanitizers",
                              "GitHub Actions", "App Store and Google Play releases"]),
    ("Also", ["Python", "Vertex AI and Gemini", "MediaPipe", "Git"]),
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


UPEM = TTFont(FONT)["head"].unitsPerEm
CAP = TTFont(FONT)["OS/2"].sCapHeight / UPEM  # cap height / em, from OS/2


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
    title = ("Yousof Selim, Software Engineering student. I build and ship real apps. Three are live on the "
             "App Store. Available for an internship, 25 January to 23 April 2027. Subang Jaya, Malaysia.")
    lines = [("I build and", "ink"), ("ship real apps.", "ink"), ("Three are live on", "muted"), ("the App Store.", "muted")]
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
        body += [rect(x, y, w, h, h / 2, fill=t["ink"], fill_opacity=.06),
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
        # One block, centred on the media: name, status, the line, the stack.
        blurb = wrap(p["blurb"], 16, 400, col)
        name_h, status_gap, blurb_gap, chip_gap, ch = 24 * CAP, 26, 30, 18, 28
        block_h = name_h + status_gap + blurb_gap + (len(blurb) - 1) * 24 + chip_gap + ch
        y0 = top + (mh - block_h) / 2 + name_h
        body.append(text(p["name"], 0, y0, 24, t["ink"], 600, -.015))
        body.append(text(p["status"], 0, y0 + status_gap, 13, t["muted"]))
        base = y0 + status_gap + blurb_gap
        body += [text(v, 0, base + i * 24, 16, t["ink"]) for i, v in enumerate(blurb)]
        chip_body, _ = chips(p["chips"], base + (len(blurb) - 1) * 24 + chip_gap, t, 13)
        body += chip_body
    else:
        mid = tier == "mid"
        mx, mw, mh, top = 0, W, (300 if mid else 180), (26 if mid else 22)
        title_size, blurb_size, lh, chip_size, status = (23, 16, 24, 13, 13) if mid else (20, 15, 22, 12.5, 12.5)
        base = top + mh + 22 + title_size * CAP
        body.append(text(p["name"], 0, base, title_size, t["ink"], 600, -.015))
        base += status + 10
        body.append(text(p["status"], 0, base, status, t["muted"]))
        base += 4
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
    lead = "Flutter for the apps, TypeScript and Java for the servers, and C++ close to the system."
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


REPORT_ROWS = [
    ("119\u00d7", "shorter waits behind slow requests after one lock fix", "Testing PostgreSQL Tenant Isolation", "WayClub"),
    ("97%", "of float-based ledgers ended up not adding up", "Cent-Exact Ledger", "Bupples"),
    ("8 bugs", "around clock changes that the existing tests missed", "One Rule, Three Runtimes", "Adelante"),
    ("4\u00d7", "lower frame rate once face tracking switches on", "Sixteen Milliseconds", "Photoshoot"),
]
BUILDING_ROWS = [
    ("Adelante", "App Store \u00b7 1.1.0", "A daily quote on your Home Screen, Lock Screen and Apple Watch, with one rotation rule in Dart, Swift and Kotlin."),
    ("TrustTrail", "Web app live \u00b7 beta", "Lays out a secondhand deal\u2019s evidence and shows the exact words behind each warning sign, privately in your browser."),
    ("LetMeKnow", "Web app live", "Turns messages, bills and promises into open loops, with a plan to close each one."),
    ("WayClub", "Preview live \u00b7 paused", "Events, tickets and committee work for teams, clubs and communities, isolated per group in the database."),
]


def reports(theme, tier):
    """Engineering reports: the headline figure, what it measures, then the report and its product."""
    t, W = THEMES[theme], TIERS[tier]
    lead = "Measurements from my own products, each with its data and scripts."
    body, y = section_head("Engineering reports", lead, t, tier)
    y += 20
    big = 30 if tier != "phone" else 26
    num_w = {"wide": 150, "mid": 130, "phone": 0}[tier]
    for value, label, title, product in REPORT_ROWS:
        body.append(rule(y + .5, W, t["ink"]))
        if tier == "phone":
            y += 18 + big * CAP
            body.append(text(value, 0, y, big, t["ink"], 600, -.02))
            for v in wrap(label, 14, 400, W):
                y += 21
                body.append(text(v, 0, y, 14, t["muted"]))
            y += 22
            body.append(text(f"{title} \u00b7 {product}", 0, y, 14, t["ink"], 500))
            y += 16
        else:
            base = y + 22 + big * CAP
            body.append(text(value, 0, base, big, t["ink"], 600, -.02))
            body.append(text(title, num_w, base - big * CAP + 15 * CAP, 15, t["ink"], 600))
            body.append(text(f"{label} \u00b7 {product}", num_w, base - big * CAP + 15 * CAP + 22, 14, t["muted"]))
            y = base + 18
    body.append(rule(y + .5, W, t["ink"]))
    title = "Engineering reports. " + lead + " " + " ".join(f"{v} {l}: {ti} ({p})." for v, l, ti, p in REPORT_ROWS)
    svg(f"reports-{theme}-{tier}.svg", W, y + 1, title, body)
    return title


def building(theme, tier):
    """Still being built: name, status and one line each, on the skills table's rows."""
    t, W = THEMES[theme], TIERS[tier]
    lead = "Four more. Each status says exactly how far along it is."
    body, y = section_head("More work", lead, t, tier)
    y += 20
    name_w = {"wide": 210, "mid": 180, "phone": 0}[tier]
    for name, status, line in BUILDING_ROWS:
        body.append(rule(y + .5, W, t["ink"]))
        if tier == "phone":
            y += 16 + 16 * CAP
            body.append(text(name, 0, y, 16, t["ink"], 600))
            y += 20
            body.append(text(status, 0, y, 13, t["muted"]))
            for v in wrap(line, 14, 400, W):
                y += 21
                body.append(text(v, 0, y, 14, t["ink"]))
            y += 16
        else:
            base = y + 18 + 16 * CAP
            body.append(text(name, 0, base, 16, t["ink"], 600))
            body.append(text(status, 0, base + 20, 13, t["muted"]))
            rows = wrap(line, 15, 400, W - name_w)
            body += [text(v, name_w, base + i * 23, 15, t["ink"]) for i, v in enumerate(rows)]
            y = max(base + 20, base + (len(rows) - 1) * 23) + 18
    body.append(rule(y + .5, W, t["ink"]))
    title = "More work. " + lead + " " + " ".join(f"{n}: {s}. {l}" for n, s, l in BUILDING_ROWS)
    svg(f"building-{theme}-{tier}.svg", W, y + 1, title, body)
    return title


def button(key, theme):
    """The site's small button: 36px pill, 14px label, 18px icon, 14px padding."""
    label, mark, primary = BUTTONS[key]
    t = THEMES[theme]
    h, size, pad, isz, gap = 36, 14, 14, 18, 8
    w = pad * 2 + measure(label, size, 500, -.005) + (isz + gap if mark else 0)
    fg = t["on_ink"] if primary else t["ink"]
    # Secondary actions rest on a soft filled pill, as on the site (never an empty outline).
    body = [rect(0, 0, w, h, h / 2, fill=t["ink"], fill_opacity=1 if primary else .07)]
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
    pad = 12
    w = pad * 2 + isz + gap + measure(label, size, 500)
    fg = t["on_ink"] if primary else t["ink"]
    body = [rect(0, 0, w, h, h / 2, fill=t["ink"], fill_opacity=1 if primary else .07),
            icon(mark, pad, (h - isz) / 2, isz, fg), text(label, pad + isz + gap, h / 2 + size * CAP / 2, size, fg, 500)]
    # 4px of air after the pill; with the space between links that makes an 8px gap.
    svg(f"go-{key}-{theme}.svg", round(w + 4), h, label, body)


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

A owes B, and B owes C. The simplified plan says A should just pay C, which is neat until A actually pays and the app looks for a direct A → C debt to reduce. There isn’t one, so the payment reduced nothing. I changed settlement to pay down the original debts along the chain. Money is kept in whole minor units, so nothing drifts by a cent; [the ledger report](https://yousofselim.com/research/cent-exact-ledger/) measures it over four million simulated bills.

#### Adelante: widgets that agree without talking

The Flutter app, the iOS widgets and the Android widgets run in separate processes and can’t talk to each other. So they don’t need to: they all follow the same clock-based rotation rule and land on the same quote, offline. Running the three versions side by side then found eight clock-change cases where they disagree; [the report](https://yousofselim.com/research/one-rule-three-runtimes/) has the details.

#### WayClub: one database, no peeking

Every club shares one database, so the bug that matters is one club seeing another’s data. Each request runs in a transaction that carries the caller’s verified claims, and PostgreSQL row-level security decides what they can see, under a role that can’t bypass it. Forget a filter and you still only see your own club. [The isolation report](https://yousofselim.com/research/catalogue-driven-rls/)

#### CodeAtlas: the 500 hiding behind a green suite

A test suite can pass while a changed branch goes untested. On its authentication fixture, CodeAtlas spots an uncovered expired-session path, generates a test for it, and catches the response quietly changing from HTTP 401 to HTTP 500. [What works today](https://github.com/yeegz/CodeAtlas#current-implementation-status)

Bupples, Adelante, WayClub, Keepwell and Hostmortem are closed source, but each has a public showcase repo.

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
    work_lead = "Six products in depth. I built each alone, end to end, except Pulse, a team project."
    contact_title, contact_lead = "Hiring interns for January 2027?", "I\u2019m available full-time from 25 January to 23 April 2027. Email is the quickest way to reach me."
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
            alts["reports"] = reports(theme, tier)
            alts["building"] = building(theme, tier)
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
    report_links = " \u00b7 ".join(f"[{ti}]({SITE}/research/{slug}/)" for (_, _, ti, _), slug in zip(
        REPORT_ROWS, ["catalogue-driven-rls", "cent-exact-ledger", "one-rule-three-runtimes", "frame-budget"]))
    building_links = " \u00b7 ".join(f"[{n}]({SITE}/work/{n.lower()}/)" for n, _, _ in BUILDING_ROWS)
    sections += [
        block(responsive("building", alts["building"], f"{SITE}/#work")),
        f"<sub>Case studies: {building_links}</sub>",
        block(responsive("reports", alts["reports"], f"{SITE}/research/")),
        f"<sub>Read: {report_links} \u00b7 [all eight reports]({SITE}/research/)</sub>",
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
