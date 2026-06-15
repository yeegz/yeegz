"""Shared build library for Yousof Selim's GitHub README assets.
Subsets + embeds fonts as data-URI woff2, measures text, generates SVG-native halftone.
Everything self-contained so it renders inside GitHub's <img>-SVG sandbox."""
import base64, io, string
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset
from PIL import Image

# ---- design tokens ----
INK   = "#0a0a0b"   # near-black page
PANEL = "#0d0d0f"   # lifted panel
PANEL2= "#101012"
BONE  = "#f2efe9"   # primary text
BONE2 = "#cfccc3"   # secondary
MUT   = "#86847c"   # muted mono
FAINT = "#5c5b54"   # faintest
GRN   = "#9bcfa5"   # sea-glass accent
GRN_D = "#6f9e78"   # dim green
LINE  = "rgba(242,239,233,0.11)"
LINE2 = "rgba(242,239,233,0.18)"
GRNL  = "rgba(155,207,165,0.16)"
GRNL2 = "rgba(155,207,165,0.34)"

GLY = (string.ascii_letters + string.digits +
       " .,:;!?()[]{}/\\&'\"@#%+-=<>|_~*" + "—–·•×…’“”éÉ")

_FONTS = {}

def load_font(key, path, family, text=GLY, axes=None, feats=("*",)):
    f = TTFont(path)
    if axes:
        try: instantiateVariableFont(f, axes, inplace=True)
        except Exception as e: print("  inst warn", key, e)
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    adv = {}
    for ch in set(text):
        gn = cmap.get(ord(ch))
        if gn: adv[ch] = hmtx[gn][0]
    opt = subset.Options()
    opt.flavor = "woff2"
    opt.layout_features = list(feats)
    opt.name_IDs = []
    opt.notdef_outline = True
    opt.glyph_names = False
    opt.desubroutinize = True
    opt.hinting = False
    opt.recalc_timestamp = False
    opt.drop_tables = []
    s = subset.Subsetter(options=opt)
    s.populate(text=text)
    s.subset(f)
    bio = io.BytesIO(); f.save(bio); raw = bio.getvalue()
    b64 = base64.b64encode(raw).decode()
    css = ("@font-face{font-family:'%s';font-style:normal;font-display:block;"
           "src:url(data:font/woff2;base64,%s) format('woff2')}" % (family, b64))
    _FONTS[key] = dict(family=family, upm=upm, adv=adv, css=css, bytes=len(raw),
                       space=adv.get(' ', upm*0.3))
    return _FONTS[key]

def fam(key): return _FONTS[key]["family"]
def css(*keys): return "".join(_FONTS[k]["css"] for k in keys)
def bytesize(key): return _FONTS[key]["bytes"]

def measure(key, text, size, tracking=0.0):
    fd = _FONTS[key]; upm = fd["upm"]; adv = fd["adv"]; sp = fd["space"]
    total = sum(adv.get(ch, sp) for ch in text)
    w = total * size / upm
    if len(text) > 1: w += tracking * (len(text) - 1)
    return w

def esc(t):
    return (t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))

# ---- SVG-native halftone from an alpha PNG ----
def halftone(path, ncols=26, cov_min=0.40, rmin=0.26, rmax=1.04,
             lum_bias=0.55, gamma=0.85):
    """Return (list of (cx,cy,r) in a normalized box, width, height) sampled on a
    staggered hex grid. Coordinates are in source-pixel space (post alpha-trim)."""
    im = Image.open(path).convert("RGBA")
    bb = im.getbbox()
    if bb: im = im.crop(bb)
    w, h = im.size
    px = im.load()
    cell = max(3, round(w / ncols))
    half = cell / 2.0
    dots = []
    row = 0
    yy = 0
    while yy < h:
        offx = half if (row % 2) else 0
        xx = offx
        while xx < w:
            asum = 0.0; lsum = 0.0; n = 0
            y0 = int(yy); x0 = int(xx)
            for dy in range(cell):
                sy = y0 + dy
                if sy >= h: break
                for dx in range(cell):
                    sx = x0 + dx
                    if sx >= w: break
                    r, g, b, a = px[sx, sy]
                    af = a / 255.0
                    asum += af
                    lsum += (0.299*r + 0.587*g + 0.114*b) / 255.0 * af
                    n += 1
            if n:
                cov = asum / n
                if cov >= cov_min:
                    lum = (lsum / asum) if asum > 0 else 0.0
                    lum = pow(max(0.0, min(1.0, lum)), gamma)
                    # brighter source -> larger bone dot; coverage scales edge dots down
                    rr = (rmin + (rmax - rmin) * (lum_bias*lum + (1-lum_bias))) * half
                    rr *= min(1.0, 0.45 + 0.55*cov)
                    dots.append((x0 + half, y0 + half, rr))
            xx += cell
        yy += cell
        row += 1
    return dots, float(w), float(h)
