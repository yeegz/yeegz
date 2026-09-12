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
def panel(width, height, title, theme='dark'):
    bg, ink, accent, muted = ('#0a0a0b','#f2efe9','#9bcfa5','#a7a59e') if theme=='dark' else ('#ece8dd','#121b14','#3f6748','#596354')
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title><rect width="{width}" height="{height}" rx="12" fill="{bg}"/>'], ink, accent, muted
# Icon-led navigation and product presentations. Source images are embedded
# unchanged; all interactivity is provided by separate README anchors.
import base64

def measure(f, value, size):
    cmap=f.getBestCmap(); glyphs=f.getGlyphSet()
    return sum(glyphs[cmap.get(ord(c),'.notdef')].width for c in value)*size/f['head'].unitsPerEm

def icon(name,x,y,size,color):
    root=ET.parse(ROOT/'tools/profile-icons'/f'{name}.svg').getroot()
    paths=''.join(ET.tostring(child,encoding='unicode') for child in root)
    return f'<g transform="translate({x} {y}) scale({size/16})" fill="{color}">{paths}</g>'

def button(key,label,mark,primary=False):
    w=round(24+24+12+measure(BODY,label,21)+24);h=58
    bg,fg=('#9bcfa5','#0a0a0b') if primary else ('#111413','#f2efe9')
    s,_,_,_=panel(w,h,label)
    s += [f'<rect x="1" y="1" width="{w-2}" height="56" rx="12" fill="{bg}" stroke="#9bcfa5" stroke-opacity=".55"/>',icon(mark,24,17,24,fg),text(BODY,label,60,37,21,fg),'</svg>']
    (ROOT/'assets'/f'{key}.svg').write_text(''.join(s))

for key,label,mark in [('portfolio','Portfolio','globe2'),('linkedin','LinkedIn','linkedin'),('email','Email','envelope'),('resume','Résumé','file-earmark-text')]:
    button('nav-'+key,label,mark,key=='portfolio')
for key,label,mark in [('app-store','App Store','apple'),('google-play','Google Play','google-play'),('product-site','Product site','globe2'),('case-study','Case study','journal-text'),('showcase','Showcase','github'),('live-app','Open app','globe2'),('source','Source','github'),('demo','Try demo','play-circle'),('implementation','Implementation','code-slash'),('play','Play game','play-circle')]:
    button('action-'+key,label,mark,key in ['app-store','live-app','demo','play'])

def screenshot(name,x,y,w,h,clip=None):
    f=ROOT/'tools/profile-media'/name
    mime='image/png' if f.suffix=='.png' else 'image/webp'
    uri=f'data:{mime};base64,'+base64.b64encode(f.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="{uri}"'+(f' clip-path="url(#{clip})"' if clip else '')+'/>'

def phone(name,x,y,w,h):
    return f'<rect x="{x-4}" y="{y-4}" width="{w+8}" height="{h+8}" rx="22" fill="#080909" stroke="#686f64" stroke-width="1.5"/>'+screenshot(name,x,y,w,h)

projects=[
('bupples','Bupples','Live on iOS + Android','Money, made social.',['Shared hangouts, scanned receipts','and clear settlement history.'],'Sole developer · design through release','Flutter / Firebase / Native widgets','Current device captures'),
('adelante','Adelante','In development','A little forward, every day.',['Motivation made for your home screen,','with native widgets and offline content.'],'Sole developer · native integration','Flutter / SwiftUI / Kotlin','Current app + widget screens'),
('photoshoot','Photoshoot','Live web app','A photobooth, all yours.',['Capture photos, strips and video','with effects that run on your device.'],'Solo · concept through deployment','TypeScript / Electron / WebGL2','Portfolio product artwork'),
('wayclub','WayClub','Guided demo','A home for your club.',['Events, members and committee','handovers in one workspace.'],'Product design + full-stack development','Next.js / NestJS / PostgreSQL','Demo capture · fictional sample data'),
('codeatlas','CodeAtlas','In development','Follow the evidence.',['Map a code change, explain its impact','and select the tests that matter.'],'Architecture + implementation','TypeScript / Static analysis / Test selection','Evidence flow · architecture diagram'),
('asteri','Fallen Asteri','Playable team project','Build the world. Feel the fight.',['A Godot platformer built with a team.','My work spans movement and combat.'],'Gameplay · transitions · repository structure','Godot / GDScript','Gameplay capture')]

for key,name,status,tag,lines,role,stack,caption in projects:
    s,ink,accent,muted=panel(1200,510,name+' — '+status)
    s += ['<defs><pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#9bcfa5" opacity=".12"/></pattern><clipPath id="visual"><rect x="644" y="48" width="514" height="365" rx="14"/></clipPath></defs>',
          '<rect x="1" y="1" width="1198" height="508" rx="16" fill="#111413" stroke="#9bcfa5" stroke-opacity=".25"/>',
          '<rect x="618" y="20" width="562" height="390" fill="url(#dots)"/>',
          f'<circle cx="48" cy="48" r="4" fill="{accent}"/>',text(BODY,status,63,55,22,accent),text(DISPLAY,name,44,146,65 if key=='asteri' else 70,ink),text(SERIF,tag,48,202,38,ink)]
    s += [text(BODY,line,48,267+i*37,28,muted) for i,line in enumerate(lines)]
    s += [text(BODY,role,48,380,21,muted),'<path d="M48 433H1152" stroke="#9bcfa5" stroke-opacity=".25"/>',text(BODY,stack,48,478,24,ink)]
    if key=='bupples':
        s += [phone('bupples-settings.webp',652,85,138,299),phone('bupples-accent.webp',1000,85,138,299),phone('bupples-profile.webp',811,39,164,356)]
    elif key=='adelante':
        s += [phone('adelante-today.webp',735,58,153,332),phone('adelante-widgets.webp',931,58,153,332)]
    elif key=='photoshoot':
        s += [screenshot('photoshoot-artwork.webp',644,48,514,365,'visual')]
    elif key=='wayclub':
        s += [screenshot('wayclub-workspace.png',644,48,514,365,'visual')]
    elif key=='asteri':
        s += [screenshot('fallenasteri.webp',644,48,514,365,'visual')]
    else:
        for y,label,small in [(55,'Code change','Base + head'),(164,'Evidence map','Symbols + paths'),(273,'Test selection','Explainable coverage')]:
            s += [f'<rect x="718" y="{y}" width="383" height="86" rx="12" fill="#151b17" stroke="#9bcfa5" stroke-opacity=".4"/>',icon('code-slash' if y==55 else 'journal-text',738,y+26,27,accent),text(BODY,label,788,y+37,28,ink),text(BODY,small,788,y+66,20,muted)]
            if y<273:s += [f'<path d="M912 {y+86}v23m-5-6 5 6 5-6" stroke="#9bcfa5" fill="none"/>']
    # Caption is tied to the visible evidence, not a claim of a released UI.
    capw=measure(BODY,caption,18)
    s += [text(BODY,caption,901-capw/2,421,18,muted),'</svg>']
    (ROOT/'assets'/f'selected-{key}.svg').write_text(''.join(s))
print('Built icon buttons and six project presentations with separate destinations.')

# Mobile artwork uses a stacked composition instead of shrinking desktop text.
for key,name,status,tag,lines,role,stack,caption in projects:
    s,ink,accent,muted=panel(600,710,name+' — '+status)
    s += ['<rect x="1" y="1" width="598" height="708" rx="16" fill="#111413" stroke="#9bcfa5" stroke-opacity=".3"/>',f'<circle cx="29" cy="34" r="3" fill="{accent}"/>',text(BODY,status,42,41,19,accent),text(DISPLAY,name,25,111,52 if key=='asteri' else 60,ink),text(SERIF,tag,28,160,31,ink)]
    s += [text(BODY,line,28,210+i*33,25,muted) for i,line in enumerate(lines)]
    if key=='bupples':
        s += [phone('bupples-settings.webp',55,308,116,251),phone('bupples-accent.webp',429,308,116,251),phone('bupples-profile.webp',230,277,140,303)]
    elif key=='adelante':
        s += [phone('adelante-today.webp',132,277,138,299),phone('adelante-widgets.webp',330,277,138,299)]
    elif key in ['photoshoot','wayclub','asteri']:
        f={'photoshoot':'photoshoot-artwork.webp','wayclub':'wayclub-workspace.png','asteri':'fallenasteri.webp'}[key]
        s += [screenshot(f,28,270,544,305)]
    else:
        for y,label,small in [(277,'Code change','Base + head'),(382,'Evidence map','Symbols + paths'),(487,'Test selection','Explainable coverage')]:
            s += [f'<rect x="72" y="{y}" width="456" height="84" rx="12" fill="#151b17" stroke="#9bcfa5" stroke-opacity=".4"/>',icon('code-slash' if y==277 else 'journal-text',94,y+28,27,accent),text(BODY,label,146,y+35,27,ink),text(BODY,small,146,y+63,19,muted)]
            if y<487:s += [f'<path d="M300 {y+84}v21m-5-6 5 6 5-6" stroke="#9bcfa5" fill="none"/>']
    capw=measure(BODY,caption,18)
    mobile_stack=stack.replace('Static analysis / Test selection','Analysis / Tests')
    s += [text(BODY,caption,300-capw/2,608,18,muted),'<path d="M28 630H572" stroke="#9bcfa5" stroke-opacity=".25"/>',text(BODY,mobile_stack,28,667,22,ink),'</svg>']
    (ROOT/'assets'/f'selected-{key}-mobile.svg').write_text(''.join(s))

# Preserve the original header's identity, composition and Arabic name.
# Convert its Latin lettering to paths; retain the original embedded Arabic font.
import re, io, copy
original=ET.parse(ROOT/'assets/hero.svg').getroot()
style=original.find('.//s:style',NS).text
embedded={name:TTFont(io.BytesIO(base64.b64decode(data))) for name,data in re.findall(r"font-family:'([^']+)'.*?base64,([A-Za-z0-9+/=]+)",style)}
# Restore a designed skills section with concrete, current technologies.
skills=[('apple','Mobile + native',['Flutter / Dart','SwiftUI / WidgetKit / Kotlin']),('globe2','Web + desktop',['TypeScript / React / Next.js','Electron / WebGL2']),('code-slash','Backend + data',['Firebase / NestJS','PostgreSQL / Testing'])]
s,ink,accent,muted=panel(1200,270,'Tools I build with — mobile, web, desktop and backend')
s += [text(SERIF,'Tools I build with.',40,64,40,ink)]
for i,(mark,title,lines) in enumerate(skills):
    x=40+i*394
    s += [icon(mark,x,105,30,accent),text(BODY,title,x+44,130,28,ink),text(BODY,lines[0],x,186,24,muted),text(BODY,lines[1],x,224,23,muted)]
    if i<2:s += [f'<path d="M{x+369} 102v138" stroke="#9bcfa5" stroke-opacity=".2"/>']
s += ['</svg>'];(ROOT/'assets/profile-practice.svg').write_text(''.join(s))
s,ink,accent,muted=panel(600,480,'Tools I build with — mobile, web, desktop and backend')
s += [text(SERIF,'Tools I build with.',28,63,38,ink)]
for i,(mark,title,lines) in enumerate(skills):
    y=102+i*123
    s += [icon(mark,30,y,28,accent),text(BODY,title,74,y+25,27,ink),text(BODY,' / '.join(lines),30,y+67,19,muted)]
    if i<2:s += [f'<path d="M28 {y+93}H572" stroke="#9bcfa5" stroke-opacity=".2"/>']
s += ['</svg>'];(ROOT/'assets/profile-practice-mobile.svg').write_text(''.join(s))

# A closing invitation in the same visual language as the portfolio footer.
for mobile,w,h in [(False,1200,350),(True,600,360)]:
    s,ink,accent,muted=panel(w,h,'Let’s build something memorable. Tell me what you’re building.')
    s += [f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="#111413" stroke="#9bcfa5" stroke-opacity=".35"/>']
    for x,y,dx,dy in [(16,16,1,1),(w-16,16,-1,1),(16,h-16,1,-1),(w-16,h-16,-1,-1)]:
        s += [f'<path d="M{x} {y+12*dy}V{y}H{x+12*dx}" fill="none" stroke="#9bcfa5" stroke-opacity=".4"/>']
    for value,font,size,y,color in [('Have a project in mind?',BODY,21 if mobile else 23,55,muted),('Let’s build',DISPLAY,68 if mobile else 88,147,ink),('something memorable.',SERIF,59 if mobile else 92,233 if mobile else 249,accent),('Tell me what you’re building.',BODY,26 if mobile else 28,309,ink)]:
        s += [text(font,value,(w-measure(font,value,size))/2,y,size,color)]
    s += ['</svg>'];(ROOT/'assets'/('profile-contact-mobile.svg' if mobile else 'profile-contact.svg')).write_text(''.join(s))

# Refined header: preserve identity/content while separating the crowded footer.
portrait=next(g for g in original.findall('.//s:g',NS) if len(g.findall('s:circle',NS))>100)
arabic=next(t for t in original.findall('.//s:text',NS) if t.attrib.get('font-family')=='AR')
arabic_css=''.join(re.findall(r"@font-face\{font-family:'AR'.*?\}",style))

def header(theme,mobile=False):
    w,h=(600,700) if mobile else (1200,646)
    bg,ink,accent,muted=('#0d0d0f','#f2efe9','#9bcfa5','#a7a59e') if theme=='dark' else ('#ece8dd','#172019','#3f6748','#596354')
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>Yousof Selim — product engineer and founder of Bupples, Subang Jaya</title>',
       '<defs><style>'+arabic_css+'@keyframes portrait-enter{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:translateY(0)}}.portrait-enter{animation:portrait-enter .85s cubic-bezier(.16,1,.3,1) both}@media(prefers-reduced-motion:reduce){.portrait-enter{animation:none}}</style>'+f'<pattern id="texture" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.15" fill="{ink}" opacity=".035"/></pattern></defs>',
       f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="20" fill="{bg}" stroke="{accent}" stroke-opacity=".25"/>',f'<rect x="12" y="12" width="{w-24}" height="{h-24}" fill="url(#texture)"/>']
    for x,y,dx,dy in [(16,16,1,1),(w-16,16,-1,1),(16,h-16,1,-1),(w-16,h-16,-1,-1)]:s += [f'<path d="M{x} {y+10*dy}V{y}H{x+10*dx}" stroke="{accent}" stroke-opacity=".4" fill="none"/>']
    x=32 if mobile else 48
    s += [f'<circle cx="{x}" cy="{40 if mobile else 54}" r="4" fill="{accent}"/>',text(BODY,'@yeegz',x+14,48 if mobile else 62,22 if mobile else 24,ink)]
    if not mobile:s += [text(BODY,'/ github profile',175,62,18,muted)]
    a=copy.deepcopy(arabic);a.attrib.update({'x':str(w-x),'y':'49' if mobile else '65','font-size':'35' if mobile else '40','fill':ink});s += [ET.tostring(a,encoding='unicode'),text(BODY,'SUBANG JAYA · MY',w-x-measure(BODY,'SUBANG JAYA · MY',14 if mobile else 18),76 if mobile else 98,14 if mobile else 18,muted)]
    s += [text(BODY,'FLUTTER  /  FULL-STACK  /  PRODUCT',x,108 if mobile else 160,18 if mobile else 21,accent)]
    size=88 if mobile else 112;namefont=embedded['AX'];namew=measure(namefont,'YOUSOF',size)
    s += [text(namefont,'YOUSOF',x-4,197 if mobile else 279,size,ink)]
    spacing=(namew-measure(namefont,'SELIM',size))/4;penx=x-4
    for c in 'SELIM':s += [text(namefont,c,penx,282 if mobile else 390,size,ink)];penx+=measure(namefont,c,size)+spacing
    px,py,sc=(359,322,.40) if mobile else (748,189,.82)
    s += [f'<g transform="translate({px} {py}) scale({sc})"><g class="portrait-enter">']
    for c in portrait.findall('s:circle',NS):s += [f'<circle cx="{c.attrib["cx"]}" cy="{c.attrib["cy"]}" r="{c.attrib["r"]}" fill="{ink}"/>']
    s += ['</g></g>']
    copylines=[('Product engineer.',334),('Founder of Bupples.',369),('Mobile, web and',415),('the details in between.',450)] if mobile else [('Product engineer. Founder of Bupples.',446),('Mobile, web and the details in between.',483)]
    for value,y in copylines:s += [text(BODY,value,x,y,23 if mobile else 26,ink if y in [334,369,446] else muted)]
    liney=492 if mobile else 531
    s += [f'<path d="M{x} {liney}H{w-x}" stroke="{accent}" stroke-opacity=".25"/>']
    s += [text(BODY,'Selected freelance projects',x,534 if mobile else 577,23 if mobile else 25,accent),text(BODY,'Internships / Jan–Apr 2027',x,570 if mobile else 612,23 if mobile else 24,ink)]
    dx=x if mobile else 640
    s += [text(BODY,'BSc (Hons) Software Engineering',dx,627 if mobile else 577,21 if mobile else 24,ink),text(BODY,'Sunway × Lancaster / August 2027',dx,659 if mobile else 612,21 if mobile else 23,muted),'</svg>']
    (ROOT/'assets'/f'profile-{theme}{"-mobile" if mobile else ""}.svg').write_text(''.join(s))
for theme in ['dark','light']:
    header(theme);header(theme,True)
