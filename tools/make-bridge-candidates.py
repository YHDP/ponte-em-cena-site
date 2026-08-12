#!/usr/bin/env python3
"""Five logo-inspired treatments of the bridge-of-methods diagram.

    python3 tools/make-bridge-candidates.py     # -> _src/svg/bridge-c1..c5.svg

Brief: one layer more beautiful, not a redesign. The current diagram works, so
legibility is the gate — a candidate that looks better and reads worse loses.

The language is logo104: a Warren truss of seven tessellated triangles running
BR-green → gold *encontro* → NL-orange, on an ink deck with two piers. Measured
off brand/logo/ponte-logo-color.svg: apexes alternate top and bottom every 20
units across x 20–180, y 24–56, coloured
    #007F33 #4FA873 #007F33 #E0A500 #E85D04 #F2934F #E85D04

Anchored spread, so the safe end is always available:
    c1, c2  conservative — current structure, truss detailing
    c3, c4  medium       — truss geometry replaces the plain boxes
    c5      ambitious    — the whole diagram IS one truss, oficinas as bays

CHOSEN 2026-08-11: **d4** — full triangle geometry, PLAIN rails. Round 1 put c1
and c3 through; round 2 walked the space between them as a matrix, and d4 won
by removing the truss rails c1 had added. The read: the converging triangles
carry the meaning on their own, and patterning the rails as well made the frame
compete with the content. Copied to _src/svg/bridge.svg; regenerate with this
script and re-copy if it changes. The other candidates stay for the record and
because the lab inlines them.
"""

from pathlib import Path

SVG = Path(__file__).resolve().parent.parent / "_src" / "svg"

GR, GRl, GRd = "#007F33", "#4FA873", "#005A24"
OR, ORl, ORd = "#E85D04", "#F2934F", "#B8460A"
GO, GOd = "#E0A500", "#9E7400"
GRt, ORt, GOt = "#D6EBDD", "#FBE3D2", "#FBEFCB"
INK, SOFT, MUTED, WHITE = "#1A1A1A", "#3D3D3D", "#757169", "#FFFFFF"
FONT = "Space Grotesk, sans-serif"

W, H = 1000, 430
COLS = [
    # Titled by MOVEMENT, not by theme. The signed proposal says workshop themes
    # are "identified in consultation with" the Consulate and names three
    # candidates (Cultural Communication, Water & Resilience, 200 Years
    # Forward); naming the diagram after any one of them would publish a choice
    # that has not been made. The movement is what the oficina does regardless
    # of which theme lands on it.
    ("01", "Diagnosticar", "ler o outro", "Teatro-Jornal", "Context Mapping + Kleurendenken"),
    ("02", "Gerar", "encenar o impasse", "Teatro Fórum", "Frame Creation"),
    ("03", "Decidir", "propor", "Teatro Legislativo", "camada holandesa — em co-desenho"),
]
CX = [167, 500, 833]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size=11, weight=700, fill=INK, anchor="middle", ls=None):
    sp = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}"{sp}>{esc(s)}</text>')


def lines(x, y, rows, size=11, weight=700, fill=INK, lh=None):
    lh = lh or size + 2
    sp = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else lh}">{esc(r)}</tspan>'
                 for i, r in enumerate(rows))
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{sp}</text>')


def box(x, y, w, h, fill, stroke, rx=9, sw=1.4):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def truss(x0, x1, ytop, ybot, cols, opacity=1.0, sw=0):
    """Warren truss: alternating up/down triangles tessellated across a band."""
    n = len(cols)
    step = (x1 - x0) / (n + 1)
    out = []
    for i, c in enumerate(cols):
        a, b = x0 + i * step, x0 + (i + 2) * step
        apex = (a + b) / 2
        if i % 2 == 0:
            pts = f"{a},{ybot} {b},{ybot} {apex},{ytop}"
        else:
            pts = f"{a},{ytop} {b},{ytop} {apex},{ybot}"
        st = f' stroke="{INK}" stroke-width="{sw}"' if sw else ""
        out.append(f'<polygon points="{pts}" fill="{c}" opacity="{opacity}"{st}/>')
    return "".join(out)


def rail(y, colour, label, h=26):
    return (f'<rect x="60" y="{y}" width="880" height="{h}" rx="{h/2}" fill="{colour}"/>'
            + t(500, y + h / 2 + 4.5, label, 12, 700, WHITE, ls="1.2"))


def arrows(y):
    out = []
    for a, b in ((261, 399), (594, 732)):
        out.append(f'<line x1="{a}" y1="{y}" x2="{b-7}" y2="{y}" stroke="{GO}" stroke-width="2.5"/>'
                   f'<polygon points="{b},{y} {b-9},{y-5} {b-9},{y+5}" fill="{GO}"/>')
    return "".join(out)


def wrap(body, label, h=H):
    return (f'<svg viewBox="0 0 {W} {h}" font-family="{FONT}" role="img" '
            f'aria-label="{esc(label)}">' + body + "</svg>\n")


LABEL = ("Ponte de metodos: o Teatro do Oprimido no trilho brasileiro e o design "
         "holandes no trilho neerlandes encontram-se em tres oficinas, do "
         "diagnosticar ao decidir")


# ── c1 · truss rails ────────────────────────────────────────────────────────
def c1():
    """Conservative. Structure untouched; the two rails become truss bands."""
    p = []
    p.append(truss(60, 940, 16, 42, [GR, GRl, GR, GRl, GR, GRl, GR, GRl, GR], 0.9))
    p.append(f'<rect x="60" y="16" width="880" height="26" rx="13" fill="none" stroke="{GRd}" stroke-width="1.2"/>')
    p.append(t(500, 34, "BRASIL · TEATRO DO OPRIMIDO", 12, 700, WHITE, ls="1.2"))
    p.append(truss(60, 940, 414, 388, [OR, ORl, OR, ORl, OR, ORl, OR, ORl, OR], 0.9))
    p.append(f'<rect x="60" y="388" width="880" height="26" rx="13" fill="none" stroke="{ORd}" stroke-width="1.2"/>')
    p.append(t(500, 406, "HOLANDA · DESIGN HOLANDÊS", 12, 700, WHITE, ls="1.2"))
    p.append(arrows(225))
    for i, (num, name, mov, br, nl) in enumerate(COLS):
        cx = CX[i]
        p.append(f'<line x1="{cx}" y1="42" x2="{cx}" y2="68" stroke="{GR}" stroke-opacity="0.45" stroke-width="2"/>')
        p.append(box(cx - 86, 68, 172, 44, GRt, GR))
        p.append(lines(cx, 93, [br], 10.5, 700, GRd))
        p.append(f'<line x1="{cx}" y1="112" x2="{cx}" y2="186" stroke="{GR}" stroke-width="2.5"/>'
                 f'<polygon points="{cx},190 {cx-5},180 {cx+5},180" fill="{GR}"/>')
        # encontro carries a small gold apex, the logo's centre triangle
        p.append(f'<polygon points="{cx},182 {cx-11},199 {cx+11},199" fill="{GO}" stroke="{GOd}" stroke-width="1.2"/>')
        p.append(box(cx - 90, 199, 180, 62, GO, GOd, rx=11, sw=1.5))
        p.append(f'<text x="{cx}" text-anchor="middle" fill="{INK}">'
                 f'<tspan x="{cx}" y="218" font-size="8.5" font-weight="700" letter-spacing="0.6">OFICINA {num}</tspan>'
                 f'<tspan x="{cx}" dy="17" font-size="12.5" font-weight="700">{esc(name)}</tspan>'
                 f'<tspan x="{cx}" dy="14" font-size="9.5">{esc(mov)}</tspan></text>')
        p.append(f'<line x1="{cx}" y1="261" x2="{cx}" y2="312" stroke="{OR}" stroke-width="2.5"/>'
                 f'<polygon points="{cx},261 {cx-5},271 {cx+5},271" fill="{OR}"/>')
        p.append(box(cx - 86, 312, 172, 44, ORt, OR))
        p.append(lines(cx, 330 if len(nl_rows(nl)) > 1 else 337, nl_rows(nl), 10.5, 700, ORd, lh=12))
        p.append(f'<line x1="{cx}" y1="356" x2="{cx}" y2="388" stroke="{OR}" stroke-opacity="0.45" stroke-width="2"/>')
    return wrap("".join(p), LABEL)


# ── c2 · encontro as a truss node ───────────────────────────────────────────
def c2():
    """Conservative. Rails stay plain; each encontro becomes a little bridge."""
    p = [rail(16, GR, "BRASIL · TEATRO DO OPRIMIDO"), rail(388, OR, "HOLANDA · DESIGN HOLANDÊS")]
    p.append(arrows(225))
    for i, (num, name, mov, br, nl) in enumerate(COLS):
        cx = CX[i]
        p.append(f'<line x1="{cx}" y1="42" x2="{cx}" y2="66" stroke="{GR}" stroke-opacity="0.45" stroke-width="2"/>')
        p.append(box(cx - 86, 66, 172, 42, GRt, GR))
        p.append(lines(cx, 90, [br], 10.5, 700, GRd))
        # a five-triangle truss standing in for the connector
        p.append(truss(cx - 74, cx + 74, 122, 158, [GR, GRl, GO, ORl, OR], 1.0))
        p.append(f'<rect x="{cx-78}" y="158" width="156" height="7" rx="3.5" fill="{INK}"/>')
        p.append(f'<rect x="{cx-64}" y="165" width="9" height="14" fill="{INK}"/>')
        p.append(f'<rect x="{cx+55}" y="165" width="9" height="14" fill="{INK}"/>')
        p.append(f'<text x="{cx}" text-anchor="middle" fill="{INK}">'
                 f'<tspan x="{cx}" y="205" font-size="8.5" font-weight="700" letter-spacing="0.6">OFICINA {num}</tspan>'
                 f'<tspan x="{cx}" dy="19" font-size="14" font-weight="700">{esc(name)}</tspan>'
                 f'<tspan x="{cx}" dy="15" font-size="9.5" font-weight="500" fill="{SOFT}">{esc(mov)}</tspan></text>')
        p.append(box(cx - 86, 314, 172, 42, ORt, OR))
        p.append(lines(cx, 332 if len(nl_rows(nl)) > 1 else 339, nl_rows(nl), 10.5, 700, ORd, lh=12))
        p.append(f'<line x1="{cx}" y1="356" x2="{cx}" y2="388" stroke="{OR}" stroke-opacity="0.45" stroke-width="2"/>')
    return wrap("".join(p), LABEL)


# ── c3 · triangles carry the flow ───────────────────────────────────────────
def c3():
    """Medium. Method boxes become triangles converging on the gold encontro."""
    p = [rail(16, GR, "BRASIL · TEATRO DO OPRIMIDO"), rail(388, OR, "HOLANDA · DESIGN HOLANDÊS")]
    p.append(arrows(215))
    for i, (num, name, mov, br, nl) in enumerate(COLS):
        cx = CX[i]
        # green wedge descending from the Brazilian rail
        p.append(f'<polygon points="{cx-92},58 {cx+92},58 {cx},170" fill="{GRt}" stroke="{GR}" stroke-width="1.8"/>')
        p.append(lines(cx, 84, [br], 11.5, 700, GRd))
        # orange wedge rising from the Dutch rail
        p.append(f'<polygon points="{cx-92},372 {cx+92},372 {cx},262" fill="{ORt}" stroke="{OR}" stroke-width="1.8"/>')
        p.append(lines(cx, 340 if len(nl_rows(nl)) > 1 else 348, nl_rows(nl), 11, 700, ORd, lh=12))
        # the gold meeting between them
        p.append(f'<polygon points="{cx},170 {cx+96},216 {cx},262 {cx-96},216" fill="{GO}" stroke="{GOd}" stroke-width="1.8"/>')
        p.append(f'<text x="{cx}" text-anchor="middle" fill="{INK}">'
                 f'<tspan x="{cx}" y="203" font-size="8.5" font-weight="700" letter-spacing="0.6">OFICINA {num}</tspan>'
                 f'<tspan x="{cx}" dy="16" font-size="12" font-weight="700">{esc(name)}</tspan>'
                 f'<tspan x="{cx}" dy="14" font-size="9" font-weight="500">{esc(mov)}</tspan></text>')
    return wrap("".join(p), LABEL)


# ── c4 · one continuous truss, three gold apexes ────────────────────────────
def c4():
    """Medium. A single truss band spans the width; the oficinas are its apexes."""
    p = [rail(16, GR, "BRASIL · TEATRO DO OPRIMIDO"), rail(388, OR, "HOLANDA · DESIGN HOLANDÊS")]
    band = [GR, GRl, GO, GRl, GR, ORl, GO, ORl, OR, ORl, GO, ORl, OR]
    p.append(truss(40, 960, 176, 262, band, 1.0, sw=1.1))
    p.append(f'<rect x="40" y="262" width="920" height="9" rx="4.5" fill="{INK}"/>')
    for px in (108, 892):
        p.append(f'<rect x="{px}" y="271" width="12" height="20" fill="{INK}"/>')
    for i, (num, name, mov, br, nl) in enumerate(COLS):
        cx = CX[i]
        p.append(f'<line x1="{cx}" y1="42" x2="{cx}" y2="72" stroke="{GR}" stroke-opacity="0.4" stroke-width="2"/>')
        p.append(box(cx - 84, 72, 168, 40, GRt, GR))
        p.append(lines(cx, 95, [br], 10.5, 700, GRd))
        p.append(f'<line x1="{cx}" y1="112" x2="{cx}" y2="172" stroke="{GR}" stroke-opacity="0.5" stroke-width="2"/>')
        p.append(f'<text x="{cx}" text-anchor="middle" fill="{INK}">'
                 f'<tspan x="{cx}" y="312" font-size="8.5" font-weight="700" letter-spacing="0.6">OFICINA {num}</tspan>'
                 f'<tspan x="{cx}" dy="18" font-size="13.5" font-weight="700">{esc(name)}</tspan>'
                 f'<tspan x="{cx}" dy="14" font-size="9.5" font-weight="500" fill="{SOFT}">{esc(mov)}</tspan></text>')
        p.append(box(cx - 84, 352, 168, 34, ORt, OR))
        p.append(lines(cx, 366 if len(nl_rows(nl)) > 1 else 372, nl_rows(nl), 9.5, 700, ORd, lh=11))
    return wrap("".join(p), LABEL)


# ── c5 · the whole diagram is the bridge ────────────────────────────────────
def c5():
    """Ambitious. logo104 stretched into a diagram: chords, bays, deck, piers."""
    p = []
    p.append(t(500, 26, "BRASIL · TEATRO DO OPRIMIDO", 11.5, 700, GRd, ls="1.4"))
    p.append(f'<rect x="70" y="38" width="860" height="6" rx="3" fill="{GR}"/>')
    # a faint offset second layer, the logo's woven depth
    p.append(f'<g opacity="0.28" transform="translate(6,4)">'
             + truss(70, 930, 44, 250, [GR, GRl, GR, GO, OR, ORl, OR], 1.0) + "</g>")
    p.append(truss(70, 930, 44, 250, [GR, GRl, GR, GO, OR, ORl, OR], 1.0, sw=1.2))
    p.append(f'<rect x="70" y="250" width="860" height="11" rx="5.5" fill="{INK}"/>')
    for px in (150, 838):
        p.append(f'<rect x="{px}" y="261" width="14" height="26" fill="{INK}"/>')
    p.append(f'<rect x="70" y="300" width="860" height="6" rx="3" fill="{OR}"/>')
    p.append(t(500, 322, "HOLANDA · DESIGN HOLANDÊS", 11.5, 700, ORd, ls="1.4"))
    for i, (num, name, mov, br, nl) in enumerate(COLS):
        cx = CX[i]
        p.append(t(cx, 348, f"OFICINA {num} · {mov}".upper(), 8.5, 700, GOd, ls="0.7"))
        p.append(t(cx, 370, name, 14, 700, INK))
        p.append(t(cx, 390, f"{br}  ×  {nl.split(' — ')[0]}", 9.5, 500, SOFT))
    return wrap("".join(p), LABEL, h=410)




# ── ROUND 2 ─────────────────────────────────────────────────────────────────
# c1 and c3 both landed. Round 2 walks the space between them as an explicit
# matrix rather than five hand-drawn guesses, so the verdicts say WHICH axis
# did the work:
#     rails    plain ─────────────── truss          (c1 brought truss rails)
#     method   box ── trapézio ───── triângulo      (c3 brought full wedges)
#     encontro caixa+ápice ───────── losango        (c3 brought the diamond)

def nl_rows(nl):
    """Wrap the Dutch label. It is the longest string in the diagram and the
    wedges taper, so a single line overhangs the shape — the same overflow the
    contextmap diagram had, and the reason its labels moved outside."""
    if " — " in nl:
        return nl.split(" — ")
    if " + " in nl:
        a, b = nl.split(" + ", 1)
        return [a, "+ " + b]
    return [nl]


def wedge(cx, ytop, ybot, half_top, half_bot, fill, stroke, sw=1.8):
    """Box, trapezoid or triangle depending on the two half-widths."""
    return (f'<polygon points="{cx-half_top},{ytop} {cx+half_top},{ytop} '
            f'{cx+half_bot},{ybot} {cx-half_bot},{ybot}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def variant(rails_truss, shape, encontro_diamond, tessellate=False):
    """shape: 'box' | 'trap' | 'tri'."""
    p = []
    if rails_truss:
        p.append(truss(60, 940, 16, 42, [GR, GRl, GR, GRl, GR, GRl, GR, GRl, GR], 0.9))
        p.append(f'<rect x="60" y="16" width="880" height="26" rx="13" fill="none" stroke="{GRd}" stroke-width="1.2"/>')
        p.append(t(500, 34, "BRASIL · TEATRO DO OPRIMIDO", 12, 700, WHITE, ls="1.2"))
        p.append(truss(60, 940, 414, 388, [OR, ORl, OR, ORl, OR, ORl, OR, ORl, OR], 0.9))
        p.append(f'<rect x="60" y="388" width="880" height="26" rx="13" fill="none" stroke="{ORd}" stroke-width="1.2"/>')
        p.append(t(500, 406, "HOLANDA · DESIGN HOLANDÊS", 12, 700, WHITE, ls="1.2"))
    else:
        p.append(rail(16, GR, "BRASIL · TEATRO DO OPRIMIDO"))
        p.append(rail(388, OR, "HOLANDA · DESIGN HOLANDÊS"))
    p.append(arrows(215))

    # how far the shape tapers toward the encontro
    # half-width at the rail end and at the encontro end. "box" keeps a shallow
    # taper so it still belongs to the same family as trap and tri.
    taper = {"box": (92, 80), "trap": (96, 46), "tri": (96, 6)}[shape]
    for i, (num, name, mov, br, nl) in enumerate(COLS):
        cx = CX[i]
        if tessellate:
            p.append(f'<clipPath id="wt{i}"><polygon points="{cx-taper[0]},60 {cx+taper[0]},60 '
                     f'{cx+taper[1]},166 {cx-taper[1]},166"/></clipPath>'
                     f'<g clip-path="url(#wt{i})">'
                     + truss(cx - taper[0], cx + taper[0], 60, 166, [GR, GRl, GR, GRl, GR], 0.55)
                     + f'</g>')
            p.append(wedge(cx, 60, 166, taper[0], taper[1], "none", GR))
        else:
            p.append(wedge(cx, 60, 166, taper[0], taper[1], GRt, GR))
        p.append(lines(cx, 96, [br], 11.5, 700, GRd))

        if tessellate:
            p.append(f'<clipPath id="wb{i}"><polygon points="{cx-taper[1]},266 {cx+taper[1]},266 '
                     f'{cx+taper[0]},370 {cx-taper[0]},370"/></clipPath>'
                     f'<g clip-path="url(#wb{i})">'
                     + truss(cx - taper[0], cx + taper[0], 266, 370, [OR, ORl, OR, ORl, OR], 0.55)
                     + f'</g>')
            p.append(wedge(cx, 266, 370, taper[1], taper[0], "none", OR))
        else:
            p.append(wedge(cx, 266, 370, taper[1], taper[0], ORt, OR))
        rows = nl_rows(nl)
        # label sits toward the wide end of the wedge, vertically centred there
        p.append(lines(cx, 330 if len(rows) > 1 else 336, rows, 11, 700, ORd, lh=13))

        if encontro_diamond:
            p.append(f'<polygon points="{cx},166 {cx+98},216 {cx},266 {cx-98},216" '
                     f'fill="{GO}" stroke="{GOd}" stroke-width="1.8"/>')
        else:
            p.append(f'<polygon points="{cx},170 {cx-11},187 {cx+11},187" fill="{GO}" stroke="{GOd}" stroke-width="1.2"/>')
            p.append(box(cx - 92, 187, 184, 60, GO, GOd, rx=11, sw=1.6))
        ty = 203 if encontro_diamond else 206
        p.append(f'<text x="{cx}" text-anchor="middle" fill="{INK}">'
                 f'<tspan x="{cx}" y="{ty}" font-size="8.5" font-weight="700" letter-spacing="0.6">OFICINA {num}</tspan>'
                 f'<tspan x="{cx}" dy="16" font-size="12.5" font-weight="700">{esc(name)}</tspan>'
                 f'<tspan x="{cx}" dy="14" font-size="9" font-weight="500">{esc(mov)}</tspan></text>')
    return wrap("".join(p), LABEL)


ROUND2 = {
    "bridge-d1": ("Trilhos em treliça + losango",
                  "Caixas retangulares como no c1, mas o encontro vira o losango do c3. "
                  "Move só o encontro.",
                  lambda: variant(True, "box", True)),
    "bridge-d2": ("Trapézios, encontro em caixa",
                  "Os métodos afunilam sem virar triângulo, e o encontro continua caixa com "
                  "ápice. O passo mais curto a partir do c1.",
                  lambda: variant(True, "trap", False)),
    "bridge-d3": ("Trapézios + losango",
                  "O ponto médio exato: afunilamento parcial e encontro em losango, sobre "
                  "trilhos de treliça.",
                  lambda: variant(True, "trap", True)),
    "bridge-d4": ("Triângulos, trilhos lisos",
                  "A geometria do c3 inteira, mas com os trilhos lisos do original. Isola "
                  "quanto os trilhos em treliça estavam contribuindo.",
                  lambda: variant(False, "tri", True)),
    "bridge-d5": ("Triângulos tessalados",
                  "O c3 empurrado para dentro do logo: cada cunha é ela própria uma treliça "
                  "de triângulos menores, em transparência.",
                  lambda: variant(True, "tri", True, tessellate=True)),
}


if __name__ == "__main__":
    rounds = [("bridge-c1", c1), ("bridge-c2", c2), ("bridge-c3", c3),
              ("bridge-c4", c4), ("bridge-c5", c5)]
    rounds += [(k, v[2]) for k, v in ROUND2.items()]
    for name, fn in rounds:
        out = SVG / f"{name}.svg"
        out.write_text(fn(), encoding="utf-8")
        print(f"  wrote _src/svg/{name}.svg ({out.stat().st_size} bytes)")
