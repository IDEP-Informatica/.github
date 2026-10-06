"""Genera profile/assets/banner.svg con el logo y las tipografías embebidas.

GitHub muestra el SVG como <img>, así que no puede cargar fuentes ni imágenes
externas: todo va embebido en base64. Las tipografías son las del sitio oficial
(idepba.com.ar): Roboto, Roboto Slab y Roboto Mono, licencia Apache 2.0.

Uso:  pip install fonttools brotli pillow && python build_banner.py
"""
import base64
import io
import urllib.request
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from PIL import Image

HERE = Path(__file__).parent
OUT = HERE.parent / "banner.svg"

# Paleta tomada de los colores globales de idepba.com.ar
C = dict(
    bg0="#013220", bg1="#004225", bg2="#00693E",
    green="#289548", neon="#61CE70", white="#FFFFFF",
    dim="#A7C4B2", panel="#0B1F16", border="#1E6343", amber="#F7DD3F",
)

# Todo el texto sale del manifiesto (github.com/IDEP-Informatica/manifiesto)
TERM = [
    ("idep@informatica:~$", " ./manifiesto --lo-que-queremos"),
    ("›", " Un Estado con soberanía informática"),
    ("›", " Software libre como política pública"),
    ("›", " Carrera para el trabajo informático"),
    ("›", " IA con los trabajadores adentro"),
    ("›", " Tecnología que dura, industria nacional"),
    ("idep@informatica:~$", " ./manifiesto --llamado"),
    ("", "Queremos escribirlo nosotros."),
]
FOOT_L = "IDEP · ATE Provincia de Buenos Aires · CTA Autónoma"
FOOT_R = "La tecnología no es neutral."
TITLE_BAR = "manifiesto — idep@informatica"

GF = "https://fonts.gstatic.com/s/"
FONTS = {
    "Roboto": GF + "roboto/v51/KFOMCnqEu92Fr1ME7kSn66aGLdTylUAMQXC89YmC2DPNWuYjammQ.woff",  # 700
    "Roboto Slab": GF + "robotoslab/v36/BngbUXZYTXPIvIBgJJSb6s3BzlRRfKOFbvjoa4OWaw.woff",  # 700
    "Roboto Mono": GF + "robotomono/v31/L0xuDF4xlVMF-BfR8bXMIhJHg45mwgGEFl0_3vqPQA.woff",  # 400
}


def font_face(family, url, text):
    raw = urllib.request.urlopen(url).read()
    font = TTFont(io.BytesIO(raw))
    opts = Options()
    opts.flavor = "woff2"
    sub = Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff2;base64,{b64}) format('woff2');}}"


def logo_data(width):
    im = Image.open(HERE / "idep-informatica-logo.png").convert("RGBA")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=88, method=6)
    return im.size, base64.b64encode(buf.getvalue()).decode()


def main():
    mono_text = "".join(a + b for a, b in TERM) + TITLE_BAR + "█"
    faces = "".join([
        font_face("Roboto", FONTS["Roboto"], FOOT_L),
        font_face("Roboto Slab", FONTS["Roboto Slab"], FOOT_R),
        font_face("Roboto Mono", FONTS["Roboto Mono"], mono_text),
    ])
    # el logo se muestra a 470 px; se embebe al doble para pantallas de alta densidad
    (lw, lh), logo = logo_data(940)
    lw, lh = lw // 2, lh // 2

    lines = []
    ys = [62, 90, 112, 134, 156, 178, 210, 234]
    for i, ((a, b), y) in enumerate(zip(TERM, ys), start=1):
        if a.startswith("idep@"):
            user, path = a.split(":", 1)
            body = (f'<tspan fill="{C["neon"]}">{user}</tspan><tspan fill="{C["dim"]}">:{path}</tspan>'
                    f'<tspan fill="{C["white"]}">{b}</tspan>')
        elif a:
            body = f'<tspan fill="{C["amber"]}">{a}</tspan><tspan fill="{C["white"]}">{b}</tspan>'
        else:
            body = f'<tspan fill="{C["neon"]}">{b}</tspan>'
        lines.append(f'<text x="22" y="{y}" class="l" style="animation-delay:{0.4 + 0.5 * (i - 1):.1f}s">{body}</text>')

    # pistas de circuito decorativas, en eco del logo
    traces = [
        "M0 70 H120 l30 30 H300", "M0 330 H90 l40 -40 H260", "M1200 30 H1100 l-30 30 H980",
        "M1200 372 H1120 l-24 -24 H900", "M560 0 V40 l20 20 V120", "M590 400 V350 l-20 -20 V300",
    ]
    trace_svg = "".join(
        f'<path d="{d}" class="t"/><path d="{d}" class="p" style="animation-delay:{i * 0.9:.1f}s"/>'
        for i, d in enumerate(traces)
    )
    nodes = [(300, 100), (260, 290), (980, 60), (900, 348), (580, 120), (570, 300)]
    node_svg = "".join(f'<circle cx="{x}" cy="{y}" r="4"/>' for x, y in nodes)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="400" viewBox="0 0 1200 400" role="img" aria-label="IDEP Informática · ATE Provincia de Buenos Aires · CTA Autónoma">
<style>{faces}
.mono{{font-family:'Roboto Mono',ui-monospace,monospace;font-size:15px}}
.l{{opacity:0;animation:show .01s forwards}}
.t{{fill:none;stroke:{C["green"]};stroke-width:2;opacity:.35}}
.p{{fill:none;stroke:{C["neon"]};stroke-width:2;stroke-dasharray:24 600;stroke-dashoffset:24;animation:pulse 5s linear infinite}}
.cursor{{animation:blink 1s steps(1) infinite}}
@keyframes show{{to{{opacity:1}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes pulse{{to{{stroke-dashoffset:-600}}}}
@media (prefers-reduced-motion:reduce){{.l{{opacity:1;animation:none}}.p,.cursor{{animation:none}}.p{{display:none}}}}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{C["bg0"]}"/><stop offset=".55" stop-color="{C["bg1"]}"/><stop offset="1" stop-color="{C["bg2"]}"/>
  </linearGradient>
  <radialGradient id="glow" cx=".25" cy=".45" r=".45"><stop offset="0" stop-color="{C["neon"]}" stop-opacity=".22"/><stop offset="1" stop-color="{C["neon"]}" stop-opacity="0"/></radialGradient>
  <clipPath id="r"><rect width="1200" height="400" rx="18"/></clipPath>
</defs>
<g clip-path="url(#r)">
  <rect width="1200" height="400" fill="url(#bg)"/>
  <rect width="1200" height="400" fill="url(#glow)"/>
  {trace_svg}
  <g fill="{C["green"]}" opacity=".7">{node_svg}</g>
</g>
<image x="50" y="{(340 - lh) // 2 + 6}" width="{lw}" height="{lh}" href="data:image/webp;base64,{logo}"/>
<g transform="translate(620 40)">
  <rect width="530" height="290" rx="10" fill="{C["panel"]}" fill-opacity=".92" stroke="{C["border"]}"/>
  <path d="M0 10a10 10 0 0 1 10-10h510a10 10 0 0 1 10 10v22H0z" fill="{C["border"]}" opacity=".6"/>
  <circle cx="20" cy="16" r="5.5" fill="#ff5f57"/><circle cx="38" cy="16" r="5.5" fill="#febc2e"/><circle cx="56" cy="16" r="5.5" fill="#28c840"/>
  <text x="265" y="21" text-anchor="middle" class="mono" font-size="12" fill="{C["dim"]}">{TITLE_BAR}</text>
  <g class="mono">
    {"".join(lines)}
    <g class="l" style="animation-delay:{0.4 + 0.5 * len(TERM):.1f}s"><text x="22" y="264"><tspan fill="{C["neon"]}">idep@informatica</tspan><tspan fill="{C["dim"]}">:~$</tspan></text>
    <rect x="{22 + 19 * 9 + 6}" y="250" width="9" height="18" fill="{C["neon"]}" class="cursor"/></g>
  </g>
</g>
<text x="52" y="372" font-family="Roboto,sans-serif" font-weight="700" font-size="15" letter-spacing=".6" fill="{C["white"]}" opacity=".9">{FOOT_L}</text>
<text x="1150" y="372" text-anchor="end" font-family="'Roboto Slab',serif" font-weight="700" font-size="16" fill="{C["neon"]}">{FOOT_R}</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"{OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
