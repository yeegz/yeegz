"""Build custom profile artwork with outlined portfolio type.

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
# Custom profile panels preserve the portfolio's visual identity throughout.
import xml.etree.ElementTree as ET
NS = {'s':'http://www.w3.org/2000/svg'}
old = ET.parse(ROOT/'assets/hero.svg').getroot()
portrait = next(g for g in old.findall('.//s:g',NS) if len(g.findall('s:circle',NS)) > 100)
def panel(width, height, title, theme='dark'):
    bg, ink, accent, muted = ('#0a0a0b','#f2efe9','#9bcfa5','#a7a59e') if theme=='dark' else ('#ece8dd','#121b14','#3f6748','#596354')
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title><rect width="{width}" height="{height}" rx="12" fill="{bg}"/>'], ink, accent, muted
for theme in ['dark','light']:
    s,ink,accent,muted=panel(1200,540,'Yousof Selim — product engineer and founder of Bupples',theme)
    s += [text(BODY,'@yeegz',48,56,22,accent),text(BODY,'Product engineer / Founder of Bupples',48,103,25,muted),text(DISPLAY,'YOUSOF',42,242,120,ink),text(DISPLAY,'SELIM',44,365,120,ink)]
    s += ['<g transform="translate(780 105) scale(.75)">']
    for c in portrait.findall('s:circle',NS):s.append(f'<circle cx="{c.attrib["cx"]}" cy="{c.attrib["cy"]}" r="{c.attrib["r"]}" fill="{ink}"/>')
    s += ['</g>',text(SERIF,'Design. Build. Ship.',50,431,48,accent),f'<path d="M48 468H1152" stroke="{muted}" stroke-opacity=".3"/>',text(BODY,'Selected freelance projects',48,511,24,ink),text(BODY,'Internships / Jan–Apr 2027',785,511,24,muted),'</svg>']
    (ROOT/'assets'/f'profile-{theme}.svg').write_text(''.join(s))
for key,label,width in [('portfolio','Portfolio',170),('linkedin','LinkedIn',164),('email','Email',136),('resume','Résumé',156)]:
    s,ink,accent,muted=panel(width,58,label)
    fill=accent if key=='portfolio' else '#101012';color='#0a0a0b' if key=='portfolio' else ink
    s.append(f'<rect x="1" y="1" width="{width-2}" height="56" rx="10" fill="{fill}" stroke="{accent}" stroke-opacity=".55"/>')
    s.append(text(BODY,label,19,36,20,color));s.append(f'<path d="M{width-37} 36l13-13m-12 0h12v12" fill="none" stroke="{color}" stroke-width="1.5"/>');s.append('</svg>')
    (ROOT/'assets'/f'nav-{key}.svg').write_text(''.join(s))
projects=[
('bupples','Bupples','Shared expenses. Clear balances.','Flutter / Firebase / Native widgets','Live','iOS + Android'),
('photoshoot','Photoshoot','A photobooth that stays on your device.','TypeScript / Electron / WebGL2','Live','Web app'),
('wayclub','WayClub','One workspace for your club.','Next.js / NestJS / PostgreSQL','Guided demo','Sample data'),
('codeatlas','CodeAtlas','Evidence for what a code change does.','TypeScript / Test selection / Signed evidence','In development','Developer tools'),
('adelante','Adelante','Encouragement, right on your Home Screen.','Flutter / SwiftUI / Kotlin','In development','Native widgets'),
('asteri','Fallen Asteri','Movement, combat and a world built together.','Godot / GDScript / Team project','Playable','Desktop')]
for key,name,tag,stack,status,platform in projects:
    s,ink,accent,muted=panel(1200,290,name+' — '+tag+' '+status)
    s.append(f'<path d="M24 24v242M48 222h1104" stroke="{accent}" stroke-opacity=".28"/>')
    s += [text(DISPLAY,name,52,112,72,ink),text(BODY,tag,55,169,29,muted),text(BODY,stack,55,261,23,muted),text(BODY,status,906,71,23,accent),text(BODY,platform,906,108,21,muted)]
    s += [f'<path d="M1092 167l42-42m-36 0h36v36" fill="none" stroke="{accent}" stroke-width="2"/>','</svg>']
    (ROOT/'assets'/f'selected-{key}.svg').write_text(''.join(s))
s,ink,accent,muted=panel(1200,252,'How I work — product design, implementation and release')
s += [text(SERIF,'From the first flow to the final release.',48,80,48,accent),text(BODY,'Product design, mobile and web development, native integration,',48,137,28,ink),text(BODY,'backend systems and tests tied to real behaviour.',48,181,28,ink),text(BODY,'Flutter / Dart / Firebase / TypeScript / SwiftUI / Kotlin / Electron / WebGL2',48,227,23,muted),'</svg>']
(ROOT/'assets/profile-practice.svg').write_text(''.join(s))
s,ink,accent,muted=panel(1200,216,'Start a conversation — project enquiries and January–April 2027 internships')
s += [text(DISPLAY,'Let’s make it happen.',48,89,60,ink),text(BODY,'A product to build, improve or introduce? Send me a short brief.',50,143,28,muted),text(BODY,'yousofselim2@gmail.com',50,188,26,accent),'<path d="M1070 136l58-58m-48 0h48v48" stroke="'+accent+'" stroke-width="3" fill="none"/>','</svg>']
(ROOT/'assets/profile-contact.svg').write_text(''.join(s))
print('Built custom navigation, portrait headers, six project panels, practice and contact.')
