import os
import yzlib as Y
from yzlib import (INK, PANEL, PANEL2, BONE, BONE2, MUT, FAINT, GRN, GRN_D,
                   LINE, LINE2, GRNL, GRNL2, esc, measure, fam, css)

# Paths resolve relative to this script's repo so the pipeline is portable.
HERE  = os.path.dirname(os.path.abspath(__file__))
ROOT  = os.path.dirname(HERE)
OUT   = os.environ.get("YZ_OUT", os.path.join(ROOT, "assets"))
FONTS = os.environ.get("YZ_FONTS", os.path.join(HERE, "fonts"))
NICHE = os.environ.get("YZ_NICHE", os.path.join(HERE, "yousof-niche.png"))
os.makedirs(OUT, exist_ok=True)
F = lambda name: os.path.join(FONTS, name)

print("subsetting fonts...")
Y.load_font("ax", F("Archivo.ttf"), "AX", axes={"wght":830,"wdth":120}, feats=())
Y.load_font("axm",F("Archivo.ttf"), "AXM", axes={"wght":680,"wdth":112}, feats=())
Y.load_font("jm", F("JBMono.ttf"), "JM", axes={"wght":500}, feats=())
Y.load_font("jmb",F("JBMono.ttf"), "JMB", axes={"wght":700}, feats=())
Y.load_font("sg", F("SpaceGrotesk.ttf"),"SG", axes={"wght":450}, feats=())
Y.load_font("ar", F("Amiri.ttf"), "AR", text="يوسف سليم ", feats=("*",))
for k in ("ax","axm","jm","jmb","sg","ar"):
    print("  %-4s %5d bytes" % (k, Y.bytesize(k)))

def T(x, y, s, size, key, fill=BONE, anchor="start", tracking=0.0, opacity=None):
    op = '' if opacity is None else f' opacity="{opacity}"'
    ls = '' if not tracking else f' letter-spacing="{tracking}"'
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam(key)}" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}"{ls}{op}>{esc(s)}</text>')

def figure_svg(fx, fy, target_h, dot=BONE, ncols=24):
    dots, w, h = Y.halftone(NICHE, ncols=ncols)
    sc = target_h / h
    W = w * sc
    parts = [f'<g>']
    for (cx, cy, r) in dots:
        parts.append(f'<circle cx="{fx+cx*sc:.1f}" cy="{fy+cy*sc:.1f}" r="{r*sc:.2f}" fill="{dot}"/>')
    parts.append('</g>')
    return "".join(parts), W, target_h

# ---------------- HERO ----------------
def build_hero():
    VW, VH = 1200, 600
    fig, FW, FH = figure_svg(0, 0, 372, ncols=23)  # build at origin, place via <g>
    FX = VW - 40 - FW + 18
    FY = 150
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {VW} {VH}" '
             f'role="img" aria-label="Yousof Selim — Flutter and full-stack engineer, open to internships">')
    s.append(f'<title>Yousof Selim — @yeegz</title>')
    s.append('<defs>')
    s.append(f'<style>{css("ax","jm","jmb","sg","ar")}</style>')
    s.append('<clipPath id="hp"><rect x="6" y="6" width="1188" height="588" rx="22"/></clipPath>')
    s.append('<pattern id="dg" width="22" height="22" patternUnits="userSpaceOnUse">'
             f'<circle cx="1.4" cy="1.4" r="1.4" fill="{BONE}" fill-opacity="0.045"/></pattern>')
    s.append('<linearGradient id="scan" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{GRN}" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="{GRN}" stop-opacity="0.85"/>'
             f'<stop offset="1" stop-color="{GRN}" stop-opacity="0"/></linearGradient>')
    s.append('</defs>')
    # panel
    s.append(f'<rect x="6" y="6" width="1188" height="588" rx="22" fill="{PANEL}" stroke="{GRNL}" stroke-width="1"/>')
    s.append('<g clip-path="url(#hp)">')
    s.append(f'<rect x="6" y="6" width="1188" height="588" fill="url(#dg)"/>')
    # the halftone figure
    s.append(f'<g transform="translate({FX:.1f},{FY})">{fig}')
    s.append(f'<rect x="-26" y="-8" width="20" height="{FH+16}" fill="url(#scan)" opacity="0.3">'
             f'<animate attributeName="x" values="-26;{FW:.0f}" dur="6.5s" '
             f'repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.2 1"/></rect>')
    s.append('</g>')
    s.append('</g>')
    # corner ticks (specimen sheet)
    for (tx, ty, dx, dy) in [(18,18,1,1),(1182,18,-1,1),(18,582,1,-1),(1182,582,-1,-1)]:
        s.append(f'<path d="M{tx} {ty+12*dy}L{tx} {ty}L{tx+12*dx} {ty}" fill="none" stroke="{GRNL2}" stroke-width="1"/>')
    # top row: @yeegz
    s.append(f'<circle cx="46" cy="56" r="4" fill="{GRN}"/>')
    s.append(f'<circle cx="46" cy="56" r="4" fill="none" stroke="{GRN}" stroke-width="1.4">'
             f'<animate attributeName="r" values="4;13" dur="2.6s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0.7;0" dur="2.6s" repeatCount="indefinite"/></circle>')
    s.append(T(62, 61, "@yeegz", 17, "jmb", BONE))
    s.append(T(150, 61, "/ github profile", 13, "jm", MUT))
    # top-right arabic + locale
    s.append(T(1154, 60, "يوسف سليم", 33, "ar", BONE, anchor="end"))
    s.append(T(1154, 86, "KUALA LUMPUR · MY", 12, "jm", MUT, anchor="end", tracking=2))
    # kicker
    s.append(T(48, 150, "FLUTTER", 14, "jmb", GRN, tracking=5)
             + T(150, 150, "·  FULL-STACK  ·  PRODUCT", 14, "jm", MUT, tracking=5))
    # name lockup — SELIM justified to YOUSOF width (solid block, the "step" set wide)
    NSIZE = 104
    yw = measure("ax", "YOUSOF", NSIZE)
    selim_tr = (yw - measure("ax", "SELIM", NSIZE)) / (len("SELIM") - 1)
    s.append(T(44, 252, "YOUSOF", NSIZE, "ax", BONE))
    s.append(T(46, 350, "SELIM", NSIZE, "ax", BONE, tracking=selim_tr))
    # dimension line under name, spanning the full block width
    dlx, dlw = 46, yw
    dy = 384
    s.append(f'<line x1="{dlx}" y1="{dy}" x2="{dlx+dlw:.0f}" y2="{dy}" stroke="{LINE2}" stroke-width="1"/>')
    s.append(f'<line x1="{dlx}" y1="{dy-5}" x2="{dlx}" y2="{dy+5}" stroke="{LINE2}" stroke-width="1"/>')
    s.append(f'<line x1="{dlx+dlw:.0f}" y1="{dy-5}" x2="{dlx+dlw:.0f}" y2="{dy+5}" stroke="{LINE2}" stroke-width="1"/>')
    lab = "FIG. 00 — IDENTITY"
    lw = measure("jm", lab, 11, tracking=2)
    lcx = dlx + dlw/2
    s.append(f'<rect x="{lcx-lw/2-8:.0f}" y="{dy-9}" width="{lw+16:.0f}" height="18" fill="{PANEL}"/>')
    s.append(T(lcx, dy+4, lab, 11, "jm", MUT, anchor="middle", tracking=2))
    # tagline
    s.append(T(48, 442, "I design, build & ship real products —", 23, "sg", BONE2))
    s.append(T(48, 474, "end to end, since 2023.", 23, "sg", BONE2))
    # availability pill
    pill_txt = "Open to SWE / Technical PM internships"
    pw = measure("jm", pill_txt, 14) + 64
    py = 506
    s.append(f'<rect x="48" y="{py}" width="{pw:.0f}" height="40" rx="20" fill="rgba(155,207,165,0.07)" stroke="{GRNL2}" stroke-width="1"/>')
    s.append(f'<circle cx="76" cy="{py+20}" r="4.5" fill="{GRN}"/>')
    s.append(f'<circle cx="76" cy="{py+20}" r="4.5" fill="none" stroke="{GRN}" stroke-width="1.3">'
             f'<animate attributeName="r" values="4.5;12" dur="2.2s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0.8;0" dur="2.2s" repeatCount="indefinite"/></circle>')
    s.append(T(94, py+25, pill_txt, 14, "jm", BONE, ))
    # degree line
    s.append(T(48+pw+22, py+25, "·  BSc (Hons) Software Engineering · Sunway × Lancaster · 2027", 13, "jm", MUT))
    s.append('</svg>')
    open(f"{OUT}/hero.svg","w").write("".join(s))
    print("hero.svg", os.path.getsize(f"{OUT}/hero.svg"), "bytes")

# ---------------- CONTACT PILLS ----------------
def pill(name, label, icon, accent=False):
    H = 60
    tw = measure("jmb", label, 14, tracking=1)
    W = 34 + 22 + tw + 24
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H}" viewBox="0 0 {W:.0f} {H}" '
         f'role="img" aria-label="{label}">']
    s.append(f'<style>{css("jmb")}</style>')
    stroke = GRNL2 if accent else LINE2
    s.append(f'<rect x="1" y="1" width="{W-2:.0f}" height="{H-2}" rx="11" fill="{PANEL}" stroke="{stroke}" stroke-width="1"/>')
    ic = GRN if accent else BONE2
    cx, cy = 26, H/2
    if icon == "arrow":
        s.append(f'<path d="M{cx-7} {cy+7}L{cx+7} {cy-7}M{cx-3} {cy-7}H{cx+7}V{cy+3}" fill="none" stroke="{ic}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    elif icon == "in":
        s.append(f'<rect x="{cx-9}" y="{cy-9}" width="18" height="18" rx="3" fill="none" stroke="{ic}" stroke-width="1.6"/>')
        s.append(f'<circle cx="{cx-4.5}" cy="{cy-4}" r="1.4" fill="{ic}"/>')
        s.append(f'<path d="M{cx-4.5} {cy-1}V{cy+5}M{cx+1} {cy+5}V{cy+1}q0-2 2-2t2 2v{4}" fill="none" stroke="{ic}" stroke-width="1.5" stroke-linecap="round"/>')
    elif icon == "mail":
        s.append(f'<rect x="{cx-9}" y="{cy-7}" width="18" height="14" rx="2.5" fill="none" stroke="{ic}" stroke-width="1.6"/>')
        s.append(f'<path d="M{cx-8} {cy-5}L{cx} {cy+1.5}L{cx+8} {cy-5}" fill="none" stroke="{ic}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')
    elif icon == "doc":
        s.append(f'<path d="M{cx-7} {cy-9}H{cx+3}L{cx+7} {cy-5}V{cy+9}H{cx-7}Z" fill="none" stroke="{ic}" stroke-width="1.6" stroke-linejoin="round"/>')
        s.append(f'<path d="M{cx-4} {cy-1}H{cx+4}M{cx-4} {cy+3}H{cx+4}" stroke="{ic}" stroke-width="1.5" stroke-linecap="round"/>')
    s.append(T(48, H/2+5, label, 14, "jmb", BONE if not accent else GRN, tracking=1))
    s.append('</svg>')
    open(f"{OUT}/btn-{name}.svg","w").write("".join(s))
    return W

def build_pills():
    pill("portfolio","PORTFOLIO","arrow", accent=True)
    pill("linkedin","LINKEDIN","in")
    pill("email","EMAIL","mail")
    pill("resume","RÉSUMÉ","doc")
    print("pills written")

# ---------------- shared section helpers ----------------
def write(name, s):
    open(f"{OUT}/{name}", "w").write("".join(s))
    print("  %-26s %6d bytes" % (name, os.path.getsize(f"{OUT}/{name}")))

def open_svg(vw, vh, fonts, label):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {vw} {vh}" '
         f'role="img" aria-label="{esc(label)}">']
    s.append(f'<title>{esc(label)}</title>')
    s.append(f'<defs><style>{css(*fonts)}</style></defs>')
    return s

def tab(s, num, title, x=40, y=6):
    txt = f"{num} / {title}"
    w = measure("jmb", txt, 13, tracking=2) + 36
    s.append(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="30" rx="6" fill="{GRN}"/>')
    s.append(T(x+18, y+20, txt, 13, "jmb", INK, tracking=2))
    return x + w

def panel(s, y, h, fill=PANEL2, stroke=LINE):
    s.append(f'<rect x="6" y="{y}" width="1188" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')

def arrow(s, x, y, c, sz=6):
    s.append(f'<path d="M{x-sz} {y+sz}L{x+sz} {y-sz}M{x-sz+3.5} {y-sz}H{x+sz}V{y+sz-3.5}" '
             f'fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>')

# ---------------- 01 / PROFILE ----------------
def build_about():
    VW = 1200; top = 34; padx = 40
    rows = [
        ("ROLE",   "Flutter & full-stack engineer  ·  freelance since 2023"),
        ("BASED",  "Kuala Lumpur / Subang Jaya, Malaysia"),
        ("BUILDS", "cross-platform apps  ·  real-time backends  ·  design-led UX"),
        ("SHIPPED","4 client products across iOS · Android · Web"),
        ("STACK",  "Dart / Flutter  ·  Node.js  ·  Supabase / Postgres  ·  Firebase"),
        ("EDU",    "BSc (Hons) Software Engineering — Sunway × Lancaster · 2027"),
        ("NOW",    "open to SWE / Technical PM internships"),
    ]
    rowH = 34
    H = top + 150 + rowH*len(rows) + 18
    s = open_svg(VW, H, ("jm","jmb","sg"), "Profile — Yousof Selim, software engineer")
    tab(s, "01", "PROFILE")
    panel(s, top, H - top - 6)
    s.append(T(padx, top+56, "Software-engineering undergrad who ships real products end to end —", 21, "sg", BONE))
    s.append(T(padx, top+86, "front end, backend, and the design in between.", 21, "sg", BONE))
    s.append(f'<line x1="{padx}" y1="{top+116}" x2="{VW-padx}" y2="{top+116}" stroke="{LINE}" stroke-width="1"/>')
    y = top + 150
    for k, v in rows:
        s.append(T(padx, y, k, 12, "jmb", GRN, tracking=2))
        s.append(T(padx+150, y, v, 14, "jm", BONE2))
        if (k, v) != rows[-1]:
            s.append(f'<line x1="{padx}" y1="{y+13}" x2="{VW-padx}" y2="{y+13}" stroke="{LINE}" stroke-width="0.6" stroke-opacity="0.5"/>')
        y += rowH
    s.append('</svg>'); write("about.svg", s)

# ---------------- 02 / STACK ----------------
def chip(s, x, y, text):
    w = measure("jm", text, 13) + 32
    s.append(f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="28" rx="8" fill="rgba(242,239,233,0.018)" stroke="{LINE2}" stroke-width="1"/>')
    s.append(f'<circle cx="{x+14:.0f}" cy="{y+14}" r="2.4" fill="{GRN}"/>')
    s.append(T(x+24, y+19, text, 13, "jm", BONE2))
    return w

def build_stack():
    VW = 1200; top = 34; padx = 40
    groups = [
        ("LANGUAGES",     ["Dart","TypeScript","JavaScript","Python","SQL","GDScript"]),
        ("FRONTEND",      ["Flutter","React Native","Tailwind CSS","WebGL / GLSL"]),
        ("BACKEND · DATA",["Node.js","REST APIs","Supabase / Postgres","Firebase / Firestore"]),
        ("AI WORKFLOW",   ["Claude Code","Cursor","GitHub Copilot","Gemini"]),
        ("TOOLS",         ["Git","Xcode","Figma","Godot","Canva"]),
    ]
    rowH = 48
    H = top + 50 + rowH*len(groups) + 8
    s = open_svg(VW, H, ("jm","jmb"), "Stack — languages, frontend, backend, AI tools")
    tab(s, "02", "STACK")
    panel(s, top, H - top - 6)
    y = top + 50
    for label, items in groups:
        s.append(T(padx, y+19, label, 12, "jmb", GRN, tracking=1.5))
        cx = padx + 196
        for it in items:
            cx += chip(s, cx, y+1, it) + 10
        if label != groups[-1][0]:
            s.append(f'<line x1="{padx}" y1="{y+rowH-7}" x2="{VW-padx}" y2="{y+rowH-7}" stroke="{LINE}" stroke-width="0.6" stroke-opacity="0.5"/>')
        y += rowH
    s.append('</svg>'); write("stack.svg", s)

# ---------------- 03 / SHIPPED header ----------------
def build_sec_shipped():
    VW = 1200; H = 64
    s = open_svg(VW, H, ("jm","jmb"), "Shipped — selected work")
    endx = tab(s, "03", "SHIPPED")
    s.append(T(endx+18, 26, "selected work · concept to deployment", 12, "jm", MUT))
    s.append(f'<line x1="6" y1="54" x2="1194" y2="54" stroke="{LINE2}" stroke-width="1"/>')
    s.append(f'<line x1="6" y1="54" x2="6" y2="48" stroke="{LINE2}" stroke-width="1"/>')
    s.append(f'<line x1="1194" y1="54" x2="1194" y2="48" stroke="{LINE2}" stroke-width="1"/>')
    s.append('</svg>'); write("sec-shipped.svg", s)

# ---------------- project cards ----------------
def spec_seg(s, x, y, label, value):
    s.append(T(x, y, label, 10, "jmb", FAINT, tracking=1.5))
    lw = measure("jmb", label, 10, tracking=1.5)
    s.append(T(x+lw+9, y, value, 12, "jm", MUT))

def project(name, fig, idx, title, status, active, line, stack, role, platform, host):
    VW = 1200; H = 184
    s = open_svg(VW, H, ("ax","jmb","jm","sg"), f"{title} — {status}")
    panel(s, 6, H-12)
    s.append(T(VW-46, 158, idx, 150, "ax", BONE, anchor="end", opacity=0.045))
    s.append(T(40, 52, f"FIG. {fig}", 12, "jmb", GRN, tracking=2))
    s.append(T(40, 96, title, 33, "ax", BONE))
    tw = measure("ax", title, 33)
    col = GRN if active else MUT
    stw = measure("jmb", status, 11, tracking=1) + 26
    s.append(f'<rect x="{40+tw+22:.0f}" y="74" width="{stw:.0f}" height="26" rx="6" fill="none" '
             f'stroke="{col}" stroke-opacity="0.55" stroke-width="1"/>')
    s.append(T(40+tw+22+13, 91, status, 11, "jmb", col, tracking=1))
    s.append(T(40, 130, line, 16, "sg", BONE2))
    spec_seg(s, 40,  160, "STACK", stack)
    spec_seg(s, 470, 160, "ROLE", role)
    spec_seg(s, 720, 160, "PLATFORM", platform)
    hw = measure("jm", host, 12)
    s.append(T(VW-40, 160, host, 12, "jm", GRN, anchor="end"))
    arrow(s, VW-40-hw-14, 156, GRN, 5)
    s.append('</svg>'); write(f"project-{name}.svg", s)

def build_projects():
    project("bupples","01","01","Bupples","TESTFLIGHT", True,
            "Group expense-splitter: snap a receipt, AI scans it, the group settles up in real time.",
            "Flutter · Firebase · Gemini", "solo, end-to-end", "iOS / Android",
            "github.com/yeegz/Bupples-showcase")
    project("photoshoot","02","02","Photoshoot","LIVE", True,
            "Joyful webcam photobooth — live WebGL2 effects + MediaPipe face-mesh, secure Electron, community themes.",
            "Electron · TypeScript · WebGL2", "solo, clean-room", "Desktop / Web",
            "photoshoot-yeegz.web.app")
    project("portfolio","03","03","Portfolio","LIVE", True,
            "Award-style personal site: a living halftone identity, WebGL shaders, and a hidden platformer easter-egg.",
            "Vanilla JS · GSAP · WebGL", "design + build", "Web",
            "yeegz.github.io")
    project("tajweed","04","04","Tajweed","IN PROGRESS", True,
            "Quranic-recitation learning platform — rebuilt information architecture, navigation and core lesson flows.",
            "Frontend · UI/UX", "design lead", "Web",
            "yeegz.github.io")
    project("taskboard","05","05","Task Board","ARCHIVE", False,
            "ClickUp-style task manager: drag-and-drop, category tags, priority sorting, state-driven UI.",
            "HTML · CSS · JavaScript", "solo", "Web",
            "github.com/yeegz/To-Do-List-Board")
    project("asteri","06","06","Fallen Asteri","PLAYABLE", True,
            "2D souls-like platformer — player movement, combat and scene transitions, built with a team Git workflow.",
            "Godot · GDScript", "gameplay programming", "itch.io",
            "yeegz.itch.io/fallenasteri")

# ---------------- 04 / PROOF ----------------
def build_proof():
    VW = 1200; top = 34; padx = 40
    metrics = [
        ("4",          "products shipped",   "concept to deployment"),
        ("3+ yrs",     "freelance",          "real, paying clients"),
        ("3",          "platforms",          "iOS · Android · Web"),
        ("150+",       "tests green",        "on Bupples alone"),
        ("real-time",  "multi-device sync",  "Supabase · Firebase"),
        ("WebGL2 + AI","under the hood",     "effects · receipt-scan"),
    ]
    cellW = (1188 - 2*34) / 3
    rowH = 100
    H = top + 50 + rowH*2 + 12
    s = open_svg(VW, H, ("ax","jmb","jm"), "Proof — why it matters")
    tab(s, "04", "PROOF")
    panel(s, top, H - top - 6)
    y0 = top + 50
    for i, (val, lab, sub) in enumerate(metrics):
        r, c = divmod(i, 3)
        cx = padx + c*cellW
        cy = y0 + r*rowH
        s.append(T(cx, cy+38, val, 34, "ax", GRN))
        s.append(T(cx, cy+66, lab, 13, "jmb", BONE))
        s.append(T(cx, cy+88, sub, 12, "jm", MUT))
        if c < 2:
            s.append(f'<line x1="{cx+cellW-22:.0f}" y1="{cy+6}" x2="{cx+cellW-22:.0f}" y2="{cy+rowH-22}" stroke="{LINE}" stroke-width="0.6" stroke-opacity="0.5"/>')
    s.append(f'<line x1="{padx}" y1="{y0+rowH-14}" x2="{VW-padx}" y2="{y0+rowH-14}" stroke="{LINE}" stroke-width="0.6" stroke-opacity="0.5"/>')
    s.append('</svg>'); write("proof.svg", s)

# ---------------- 05 / CONTACT ----------------
def build_cta():
    VW = 1200; H = 210
    s = open_svg(VW, H, ("ax","jm","jmb"), "Contact — let's build something people remember")
    panel(s, 6, H-12, fill=PANEL, stroke=GRNL)
    for (tx, ty, dx, dy) in [(24,24,1,1),(1176,24,-1,1),(24,186,1,-1),(1176,186,-1,-1)]:
        s.append(f'<path d="M{tx} {ty+11*dy}L{tx} {ty}L{tx+11*dx} {ty}" fill="none" stroke="{GRNL2}" stroke-width="1"/>')
    s.append(T(VW/2, 88, "Let's build something people remember.", 33, "ax", BONE, anchor="middle"))
    s.append(T(VW/2, 130, "yousofselim2@gmail.com    ·    yeegz.github.io    ·    linkedin.com/in/ysf-slm",
              14, "jm", MUT, anchor="middle"))
    txt = "AVAILABLE FOR 2027 INTERNSHIPS"
    pw = measure("jmb", txt, 12, tracking=2) + 56
    px = VW/2 - pw/2
    s.append(f'<rect x="{px:.0f}" y="156" width="{pw:.0f}" height="34" rx="17" fill="rgba(155,207,165,0.06)" stroke="{GRNL2}" stroke-width="1"/>')
    s.append(f'<circle cx="{px+24:.0f}" cy="173" r="4" fill="{GRN}"/>')
    s.append(f'<circle cx="{px+24:.0f}" cy="173" r="4" fill="none" stroke="{GRN}" stroke-width="1.2">'
             f'<animate attributeName="r" values="4;11" dur="2.4s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0.8;0" dur="2.4s" repeatCount="indefinite"/></circle>')
    s.append(T(px+40, 178, txt, 12, "jmb", GRN, tracking=2))
    s.append('</svg>'); write("cta.svg", s)

print("building assets...")
build_hero()
build_pills()
build_about()
build_stack()
build_sec_shipped()
build_projects()
build_proof()
build_cta()
print("done")
