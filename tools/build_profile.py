"""Build the profile's static, theme-aware header with outlined portfolio type.

Usage: python3 tools/build_profile.py /path/to/fonts
Requires fonttools. Font files and their OFL licenses live in tools/profile-fonts.
"""
from pathlib import Path
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from html import escape
ROOT = Path(__file__).resolve().parents[1]
FONTS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'tools/profile-fonts'
def font(name, axes=None):
    f = TTFont(FONTS / name)
    return instantiateVariableFont(f, axes, inplace=True) if axes else f
DISPLAY = font('Archivo.ttf', {'wght':900, 'wdth':115})
BODY = font('SpaceGrotesk.ttf', {'wght':500})
SERIF = font('InstrumentSerif-Italic.ttf')
def text(f, value, x, y, size, color):
    glyphs = f.getGlyphSet(); cmap = f.getBestCmap(); scale = size / f['head'].unitsPerEm
    paths = []
    for char in value:
        name = cmap.get(ord(char), '.notdef'); glyph = glyphs[name]
        pen = SVGPathPen(glyphs)
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
        paths.append(pen.getCommands())
        x += glyph.width * scale
    return f'<path fill="{color}" d="{" ".join(paths)}"/>'
def build(theme):
    bg, ink, accent, muted = ('#0a0a0b','#f2efe9','#9bcfa5','#a7a59e') if theme == 'dark' else ('#ece8dd','#121b14','#3f6748','#596354')
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420" role="img" aria-labelledby="title desc"><title id="title">Yousof Selim — Product engineer</title><desc id="desc">Founder of Bupples. Design, build, ship.</desc><rect width="1200" height="420" fill="{bg}"/>']
    s += [text(DISPLAY,'YOUSOF',48,154,118,ink), text(DISPLAY,'SELIM',48,278,118,ink)]
    s += [text(BODY,'Product engineer',710,112,31,ink),text(BODY,'Founder of Bupples',710,155,24,muted)]
    s += [text(SERIF,'Design. Build. Ship.',710,274,40,accent)]
    s += [f'<path d="M48 324H1152" stroke="{muted}" stroke-opacity=".35"/>',text(BODY,'Mobile, web and the details in between.',48,374,25,ink),text(BODY,'yeegz.github.io',937,374,24,accent)]
    s += ['</svg>']
    (ROOT/'assets'/f'profile-{theme}.svg').write_text(''.join(s))
for theme in ['dark','light']: build(theme)
print('Built both profile headers with outlined type; no external resources or motion.')
