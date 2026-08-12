#!/usr/bin/env python3
"""Regenerate _src/svg/contextmap.svg (Sleeswijk Visser / Stappers depth model).

    python3 tools/make-contextmap.py

Why this exists rather than the deck's svgContextmap(): in the deck version the
band labels sit INSIDE the triangles, and near the apex the shape is far
narrower than the words. Measured against the deck geometry (apex y=78, base
y=374, half-base 66):

    label            space inside   needed
    dizem / pensam       25.0px     ~46.2px    overflow
    explícito            16.9px     ~56.9px    overflow
    observável           49.9px     ~63.3px    overflow

Widening cannot fix it — for "explícito" to fit at its height the triangle
would need a half-base of ~218 instead of 66. So the labels move outside, into
a column beside each shape, tied back with a hairline tick. The triangles keep
their job (showing the widening) and the words keep theirs (being readable).

Muted text uses #757169, not the brand's #8A857B: the latter measures 3.43:1 on
paper and fails AA for small text.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "_src" / "svg" / "contextmap.svg"

GREEN, GREEN_T = "#007F33", "#D6EBDD"
GOLD,  GOLD_T  = "#E0A500", "#FBEFCB"
ORANGE, ORANGE_T = "#E85D04", "#FBE3D2"
INK, INK_SOFT, MUTED = "#1A1A1A", "#3D3D3D", "#757169"
RULE = "#C9C3B8"

TOP, BOT = 86, 386          # vertical extent of every shape
HALF = 46                   # half-width at the wide end
W, H = 780, 470

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def mids(cuts):
    """Band mid-heights from the cut positions."""
    edges = [TOP] + cuts + [BOT]
    return [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]

def tri_up(cx):
    return f'<polygon points="{cx},{TOP} {cx-HALF},{BOT} {cx+HALF},{BOT}"'

def edge_up(cx, y):
    return cx + HALF * (y - TOP) / (BOT - TOP)

def edge_down(cx, y):
    return cx + HALF * (BOT - y) / (BOT - TOP)

def band_lines(cx, cuts, colour, down=False):
    out = ""
    for y in cuts:
        e = (edge_down if down else edge_up)(cx, y)
        half = e - cx
        out += (f'<line x1="{cx-half:.1f}" y1="{y}" x2="{cx+half:.1f}" y2="{y}" '
                f'stroke="{colour}" stroke-width="1.2" opacity="0.5"/>')
    return out

def label(x, y, lines, size=11.5, weight=700, fill=INK):
    """Left-aligned label, vertically centred on y."""
    dy0 = -(len(lines) - 1) * (size + 2) / 2
    spans = "".join(
        f'<tspan x="{x}" dy="{(size + 2) if i else dy0:.1f}">{esc(t)}</tspan>'
        for i, t in enumerate(lines))
    return (f'<text x="{x}" y="{y + size * 0.36:.1f}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{spans}</text>')

def tick(x1, x2, y):
    return (f'<line x1="{x1:.1f}" y1="{y}" x2="{x2:.1f}" y2="{y}" '
            f'stroke="{RULE}" stroke-width="1.2"/>')

def build():
    p = []
    p.append(f'<svg viewBox="0 0 {W} {H}" font-family="Space Grotesk, sans-serif" '
             f'role="img" aria-label="Mapeamento de contexto: quanto mais fundo o '
             f'conhecimento, menos as entrevistas alcancam; as sessoes gerativas '
             f'chegam ao tacito e ao latente">')

    # depth axis
    p.append(f'<line x1="26" y1="{TOP}" x2="26" y2="{BOT+8}" stroke="{MUTED}" stroke-width="2"/>')
    p.append(f'<polygon points="26,{BOT+16} 21,{BOT+2} 31,{BOT+2}" fill="{MUTED}"/>')
    p.append(f'<text x="14" y="{TOP+2}" transform="rotate(-90 14 {TOP+2})" '
             f'font-size="10.5" font-weight="700" fill="{MUTED}" letter-spacing="1">SUPERFÍCIE</text>')
    p.append(f'<text x="14" y="{BOT}" transform="rotate(-90 14 {BOT})" text-anchor="end" '
             f'font-size="10.5" font-weight="700" fill="{MUTED}" letter-spacing="1">PROFUNDO</text>')

    groups = [
        # cx, tint, stroke, cuts, header, header_x, label_x, labels, inverted
        (118, GREEN_T, GREEN, [190, 280], "o que as pessoas:", 72, 178,
         [["dizem", "pensam"], ["fazem", "usam"], ["sabem · sentem", "· sonham"]], False),
        (314, GOLD_T, GOLD, [190, 280], "técnicas:", 268, 374,
         [["entrevistas"], ["observações"], None], True),
        (560, ORANGE_T, ORANGE, [161, 236, 311], "conhecimento:", 514, 620,
         [["explícito"], ["observável"], ["tácito"], ["latente"]], False),
    ]

    for cx, tint, stroke, cuts, head, hx, lx, labels, down in groups:
        p.append(f'<text x="{hx}" y="64" font-size="12.5" font-weight="700" fill="{INK}">{esc(head)}</text>')
        if down:
            p.append(f'<polygon points="{cx-HALF},{TOP} {cx+HALF},{TOP} {cx},{BOT}" '
                     f'fill="{tint}" stroke="{stroke}" stroke-width="2.2"/>')
        else:
            p.append(tri_up(cx) + f' fill="{tint}" stroke="{stroke}" stroke-width="2.2"/>')
        p.append(band_lines(cx, cuts, stroke, down))

        for y, text in zip(mids(cuts), labels):
            e = (edge_down if down else edge_up)(cx, y)
            if text is None:      # the highlighted generative-sessions chip
                p.append(tick(e + 4, lx - 8, y))
                p.append(f'<rect x="{lx}" y="{y-15:.1f}" width="132" height="30" rx="7" fill="{GOLD}"/>')
                p.append(f'<text x="{lx+66}" text-anchor="middle" font-size="11" font-weight="700" '
                         f'fill="{INK}"><tspan x="{lx+66}" y="{y-1:.1f}">SESSÕES</tspan>'
                         f'<tspan x="{lx+66}" dy="13">GERATIVAS</tspan></text>')
            else:
                p.append(tick(e + 4, lx - 8, y))
                p.append(label(lx, y, text))

    # the Ponte hook: theatre powers the generative sessions
    chip_cx = 374 + 66
    p.append(f'<line x1="{chip_cx}" y1="410" x2="{chip_cx}" y2="356" stroke="{ORANGE}" stroke-width="3"/>')
    p.append(f'<polygon points="{chip_cx},350 {chip_cx-6},362 {chip_cx+6},362" fill="{ORANGE}"/>')
    p.append(f'<rect x="72" y="414" width="{W-72-8}" height="30" rx="15" fill="{INK}"/>')
    p.append(f'<text x="{(72 + W-8)/2:.0f}" y="433" text-anchor="middle" font-size="11.5" '
             f'font-weight="600" fill="#FFFFFF">Motor gerativo → TEATRO (Boal): Jornal · Imagem · Fórum</text>')

    p.append('</svg>')
    return "".join(p)

if __name__ == "__main__":
    OUT.write_text(build() + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parents[2])} ({OUT.stat().st_size} bytes)")
