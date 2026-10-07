"""Build GitHub-safe artwork from the October 2026 portfolio design.

Run: python3 tools/build_profile.py
Requires fonttools and brotli. All type is outlined and all media embedded,
so GitHub's image renderer never needs an external font, image or script.
"""
import base64
from functools import lru_cache
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
MEDIA = ROOT / "tools/profile-media"
FONT = ROOT / "tools/profile-fonts/HankenGrotesk.woff2"
# Exact paper, ink, secondary text and accent values from styles.css.
THEMES = {
    "light": dict(paper="#f3efe6", ink="#17150f", muted="#5c574c", accent="#a83c12", surface="#faf8f4", edge="#d6d2c8"),
    "dark": dict(paper="#12110e", ink="#f1ece1", muted="#a7a093", accent="#f28b63", surface="#24231f", edge="#393730"),
}


@lru_cache
def font(weight):
    return instantiateVariableFont(TTFont(FONT), {"wght": weight}, inplace=True)


def text(value, x, y, size, color, weight=400, tracking=0):
    """Outline Hanken Grotesk; fail instead of emitting missing glyphs."""
    f = font(weight)
    glyphs, cmap = f.getGlyphSet(), f.getBestCmap()
    scale = size / f["head"].unitsPerEm
    paths = []
    for char in value:
        if ord(char) not in cmap:
            raise ValueError(f"Missing glyph: {char!r}")
        glyph = glyphs[cmap[ord(char)]]
        pen = SVGPathPen(glyphs)
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
        paths.append(pen.getCommands())
        x += glyph.width * scale + tracking
    return f'<path fill="{color}" d="{" ".join(paths)}"/>'


def rect(x, y, width, height, fill, radius=20, stroke=None):
    edge = f' stroke="{stroke}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}"{edge}/>'


@lru_cache
def image_data(name):
    return "data:image/webp;base64," + base64.b64encode((MEDIA / name).read_bytes()).decode()


def image(name, x, y, width, height, key, radius=14, fit="meet"):
    return (
        f'<defs><clipPath id="{key}">{rect(x, y, width, height, "white", radius)}</clipPath></defs>'
        f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
        f'preserveAspectRatio="xMidYMid {fit}" clip-path="url(#{key})" href="{image_data(name)}"/>'
    )


def panel(width, height, title, theme):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title>',
        rect(.5, .5, width - 1, height - 1, theme["paper"], 24, theme["edge"]),
    ]


def save(name, parts):
    (ASSETS / name).write_text("".join(parts) + "</svg>\n")


def header(theme_name, mobile):
    t = THEMES[theme_name]
    w, h = (600, 560) if mobile else (1200, 430)
    s = panel(w, h, "Yousof Selim. Software Engineering student. I build and ship real apps. Two are live on the App Store. Subang Jaya, Malaysia.", t)
    if mobile:
        s += [
            text("Yousof", 32, 85, 48, t["ink"], 600, -.6),
            text("Selim", 32, 139, 48, t["ink"], 600, -.6),
            text("Software Engineering", 32, 204, 24, t["muted"]),
            text("student", 32, 236, 24, t["muted"]),
            image("yousof-portrait.webp", 382, 32, 186, 268, "portrait", 18, "slice"),
            text("I build and ship real apps.", 32, 368, 43, t["ink"], 600, -.6),
            text("Two are live on the", 32, 422, 43, t["muted"], 600, -.6),
            text("App Store.", 32, 472, 43, t["muted"], 600, -.6),
            text("Subang Jaya, Malaysia", 32, 529, 22, t["muted"]),
        ]
    else:
        s += [
            text("Yousof Selim", 48, 78, 36, t["ink"], 600, -.4),
            text("Software Engineering student", 48, 116, 24, t["muted"]),
            text("I build and ship", 48, 218, 66, t["ink"], 600, -1.2),
            text("real apps.", 48, 288, 66, t["ink"], 600, -1.2),
            text("Two are live on the App Store.", 48, 340, 31, t["muted"], 500, -.2),
            text("Subang Jaya, Malaysia", 48, 390, 22, t["muted"]),
            image("yousof-portrait.webp", 832, 28, 340, 374, "portrait", 20, "slice"),
        ]
    save(f'profile-{theme_name}{"-mobile" if mobile else ""}.svg', s)


def phones(key, theme_name, mobile):
    t = THEMES[theme_name]
    w, h = ((600, 600) if mobile else (1200, 460)) if key == "bupples" else ((600, 520) if mobile else (1200, 380))
    names = {
        "bupples": ["bupples-profile.webp", "bupples-accent.webp", "bupples-settings.webp"],
        "adelante": ["adelante-widgets.webp", "adelante-today.webp", "adelante-discover.webp"],
    }[key]
    title = "Bupples: profile, accent editor and settings" if key == "bupples" else "Adelante: native widgets, Today and Discover"
    s = panel(w, h, title, t)
    name = "Bupples" if key == "bupples" else "Adelante"
    lines = ["Shared expenses.", "Clear settlements."] if key == "bupples" else ["A daily quote,", "right on your home screen."]
    stack = "Flutter / Firebase / Vertex AI" if key == "bupples" else "Flutter / SwiftUI / Kotlin"
    x = 32 if mobile else 48
    s += [text(name, x, 72 if mobile else 110, 48 if mobile else 58, t["ink"], 600, -.7)]
    if mobile:
        line = "Shared expenses. Clear settlements." if key == "bupples" else "A daily quote, right on your home screen."
        s += [text(line, x, 116, 25, t["muted"])]
    else:
        s += [text(line, x, 180 + i * 40, 32, t["muted"], 400, -.2) for i, line in enumerate(lines)]
    s += [text(stack, x, h - 28 if mobile else h - 46, 21, t["muted"])]
    # Complete screenshots, arranged around the product instead of repeating a gallery strip.
    if key == "bupples":
        placements = [(34, 198, 150), (416, 198, 150), (211, 156, 178)] if mobile else [(635, 106, 135), (1010, 106, 135), (806, 62, 164)]
        screens = [names[0], names[2], names[1]]
    else:
        placements = [(130, 149, 142), (328, 149, 142)] if mobile else [(694, 38, 139), (916, 38, 139)]
        screens = [names[0], names[1]]
    for (x, y, width), name in zip(placements, screens):
        height = width * (2796 / 1290 if key == "bupples" else 1955 / 900)
        s += [rect(x - 3, y - 3, width + 6, height + 6, t["surface"], 18, t["edge"]),
              image(name, x, y, width, height, f"screen-{x}", 15)]
    save(f'selected-{key}-{theme_name}{"-mobile" if mobile else ""}.svg', s)


def workspace(key, theme_name, mobile):
    t = THEMES[theme_name]
    w = 600 if mobile else 1200
    # Preserve entire screenshots and their aspect ratios inside the paper frame.
    source, ratio, title = {
        "photoshoot": ("photoshoot-landing.webp", 1.6, "Photoshoot photobooth landing page"),
        "wayclub": ("wayclub-workspace.webp", 1600 / 1100, "WayClub guided interface demo with fictional club data"),
        "codeatlas": ("codeatlas-workspace.webp", 1.6, "CodeAtlas evidence workspace on a fixture repository"),
    }[key]
    image_w = 552 if mobile else (560 if key == "photoshoot" else 800)
    image_h = image_w / ratio
    padding = 24 if mobile else 28
    h = (552 if mobile else 420) if key == "photoshoot" else round(image_h + padding * 2)
    s = panel(w, h, title, t)
    x = (w - image_w) / 2
    if key == "photoshoot":
        x = 24 if mobile else 592
        padding = 150 if mobile else 35
        s += [text("Photoshoot", 32 if mobile else 48, 72 if mobile else 110, 48 if mobile else 58, t["ink"], 600, -.7)]
        if mobile:
            s += [text("Your camera. Your device. Your photos.", 32, 116, 25, t["muted"])]
        else:
            s += [text("Your camera. Your device.", 48, 180, 32, t["muted"]), text("Your photos.", 48, 220, 32, t["muted"])]
        s += [text("TypeScript / Electron / WebGL2", 32 if mobile else 48, h - 24 if mobile else 374, 21, t["muted"])]
    s += [rect(x - 1, padding - 1, image_w + 2, image_h + 2, t["surface"], 15, t["edge"]),
          image(source, x, padding, image_w, image_h, "workspace", 14)]
    save(f'selected-{key}-{theme_name}{"-mobile" if mobile else ""}.svg', s)


def button(key, label, mark, theme_name, primary=False):
    t = THEMES[theme_name]
    bg, fg = (t["ink"], t["paper"]) if primary else (t["paper"], t["ink"])
    f = font(500)
    glyphs, cmap = f.getGlyphSet(), f.getBestCmap()
    label_width = sum(glyphs[cmap[ord(c)]].width for c in label) * 20 / f["head"].unitsPerEm
    width = round(label_width + 76)
    icon_root = ET.parse(ROOT / "tools/profile-icons" / f"{mark}.svg").getroot()
    paths = "".join(ET.tostring(child, encoding="unicode") for child in icon_root)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="48" viewBox="0 0 {width} 48" role="img"><title>{label}</title>',
         rect(1, 1, width - 2, 46, bg, 23, t["ink"] if primary else t["edge"]),
         f'<g transform="translate(19 14) scale(1.25)" fill="{fg}">{paths}</g>',
         text(label, 50, 31, 20, fg, 500)]
    save(f"link-{key}-{theme_name}.svg", s)


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        for key, label, mark, primary in [
            ("resume", "Résumé", "file-earmark-text", True),
            ("portfolio", "Portfolio", "globe2", False),
            ("recruiters", "For recruiters", "journal-text", False),
            ("app-store", "App Store", "apple", True),
            ("google-play", "Google Play", "google-play", False),
            ("case-study", "Case study", "journal-text", False),
            ("showcase", "Showcase", "github", False),
            ("open-app", "Open app", "play-circle", True),
            ("source", "Source", "github", False),
            ("download", "Windows", "download", False),
            ("email", "Email me", "envelope", True),
            ("linkedin", "LinkedIn", "linkedin", False),
        ]:
            button(key, label, mark, theme, primary)
        for mobile in (False, True):
            header(theme, mobile)
            for key in ("bupples", "adelante"):
                phones(key, theme, mobile)
            for key in ("photoshoot", "wayclub", "codeatlas"):
                workspace(key, theme, mobile)
    print("Built 48 self-contained SVGs: 24 panels and 24 action buttons.")


if __name__ == "__main__":
    main()
