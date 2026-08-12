#!/usr/bin/env python3
"""Generate the three Boal-technique diagrams for /metodologia/.

    python3 tools/make-teatros.py

The Dutch methods arrived with diagrams from the deck; the Brazilian ones had
none, so the three teatro panels were walls of text next to three illustrated
ones. These even that up, in the same visual grammar as the deck diagrams:
brand palette, Space Grotesk, rounded rects, labels OUTSIDE any shape too
narrow to hold them (the lesson from make-contextmap.py).

Muted text is #757169, not the brand's #8A857B, which measures 3.43:1 on paper
and fails AA at these sizes.
"""

from pathlib import Path

SVG = Path(__file__).resolve().parent.parent / "_src" / "svg"

GREEN, GREEN_T, GREEN_D = "#007F33", "#D6EBDD", "#005A24"
GOLD,  GOLD_T,  GOLD_D  = "#E0A500", "#FBEFCB", "#9E7400"
ORANGE, ORANGE_T, ORANGE_D = "#E85D04", "#FBE3D2", "#B8460A"
INK, INK_SOFT, MUTED, RULE, WHITE = "#1A1A1A", "#3D3D3D", "#757169", "#C9C3B8", "#FFFFFF"
FONT = "Space Grotesk, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=12, weight=700, fill=INK, anchor="middle", italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}"{st}>{esc(s)}</text>')


def lines(x, y, rows, size=11, weight=700, fill=INK, anchor="middle", lh=None):
    lh = lh or size + 3
    sp = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else lh}">{esc(r)}</tspan>'
                 for i, r in enumerate(rows))
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{sp}</text>')


def box(x, y, w, h, fill, stroke, rx=10, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def arrow(x1, y1, x2, y2, colour, sw=2.5):
    """Straight arrow, head at (x2,y2). Horizontal or vertical only."""
    if y1 == y2:
        d = 1 if x2 > x1 else -1
        head = f'<polygon points="{x2},{y2} {x2-7*d},{y2-5} {x2-7*d},{y2+5}" fill="{colour}"/>'
        x2b = x2 - 6 * d
        body = f'<line x1="{x1}" y1="{y1}" x2="{x2b}" y2="{y2}" stroke="{colour}" stroke-width="{sw}"/>'
    else:
        d = 1 if y2 > y1 else -1
        head = f'<polygon points="{x2},{y2} {x2-5},{y2-7*d} {x2+5},{y2-7*d}" fill="{colour}"/>'
        y2b = y2 - 6 * d
        body = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2b}" stroke="{colour}" stroke-width="{sw}"/>'
    return body + head


def band(w, y, label, width=None):
    width = width or w - 40
    return (f'<rect x="20" y="{y}" width="{width}" height="30" rx="15" fill="{INK}"/>'
            + txt(20 + width / 2, y + 19, label, 11.5, 600, WHITE))


def wrap(svg, w, h, label):
    return (f'<svg viewBox="0 0 {w} {h}" font-family="{FONT}" role="img" '
            f'aria-label="{esc(label)}">' + svg + "</svg>\n")


# ── 1. Teatro-Jornal: from a news item to a scene ───────────────────────────
def jornal():
    W, H = 760, 330
    p = []
    p.append(txt(120, 30, "A NOTÍCIA", 11, 700, MUTED))
    p.append(box(40, 44, 160, 122, WHITE, RULE, sw=1.4))
    for i, wd in enumerate((124, 108, 118, 92, 112)):
        p.append(f'<rect x="58" y="{62+i*20}" width="{wd}" height="7" rx="3.5" fill="#E4DFD6"/>')
    # the layer the framing hides
    p.append(box(40, 182, 160, 74, "none", MUTED, rx=10, sw=1.4, dash="5 4"))
    p.append(lines(120, 208, ["o que omite,", "quem não foi ouvido,", "que interesses"],
                   9.5, 400, MUTED))

    p.append(arrow(210, 105, 268, 105, GOLD_D))
    p.append(arrow(210, 219, 262, 140, GOLD_D) if False else "")
    p.append(f'<path d="M210 219 H240 V128" fill="none" stroke="{GOLD_D}" stroke-width="2.5"/>')
    p.append(f'<polygon points="240,118 235,130 245,130" fill="{GOLD_D}"/>')

    # crossed reading
    p.append(box(270, 62, 200, 132, GOLD_T, GOLD))
    p.append(lines(370, 88, ["LEITURA", "CRUZADA"], 12.5, 700, INK))
    p.append(box(288, 124, 76, 26, WHITE, ORANGE, rx=13, sw=1.4))
    p.append(txt(326, 141, "jornal NL", 9.5, 700, ORANGE_D))
    p.append(box(376, 124, 76, 26, WHITE, GREEN, rx=13, sw=1.4))
    p.append(txt(414, 141, "jornal BR", 9.5, 700, GREEN_D))
    p.append(txt(370, 172, "o mesmo tema, lado a lado", 9.5, 400, INK_SOFT))

    p.append(arrow(480, 128, 538, 128, GOLD_D))

    # the scene
    p.append(txt(640, 30, "A CENA", 11, 700, MUTED))
    p.append(box(548, 44, 172, 150, GREEN_T, GREEN))
    p.append(lines(634, 84, ["imagens", "e cenas a partir", "do material"], 12, 700, INK))
    p.append(box(566, 138, 136, 34, WHITE, GREEN, rx=8, sw=1.4))
    p.append(lines(634, 152, ["investigada", "coletivamente"], 9.5, 700, GREEN_D, lh=11))

    p.append(band(W, 274, "A informação deixa de ser recebida como algo neutro"))
    return wrap("".join(p), W, H,
                "Teatro-Jornal: a noticia e a leitura cruzada de um jornal holandes e um "
                "brasileiro viram imagens e cenas, e a informacao deixa de ser neutra")


# ── 2. Teatro Fórum: the intervention loop ──────────────────────────────────
def forum():
    W, H = 760, 352
    p = []
    p.append(txt(232, 30, "A CENA MODELO", 11, 700, MUTED))
    p.append(box(40, 44, 384, 128, GOLD_T, GOLD))
    p.append(box(70, 74, 150, 68, WHITE, GOLD_D, rx=8, sw=1.4))
    p.append(lines(145, 102, ["protagonista"], 11.5, 700, INK))
    p.append(txt(145, 124, "quer algo e não consegue", 9, 400, INK_SOFT))
    p.append(box(244, 74, 150, 68, WHITE, GOLD_D, rx=8, sw=1.4))
    p.append(lines(319, 102, ["antagonista"], 11.5, 700, INK))
    p.append(txt(319, 124, "o que o impede", 9, 400, INK_SOFT))

    # the audience steps in
    p.append(txt(232, 284, "A PLATEIA", 11, 700, MUTED))
    for i in range(9):
        cx = 72 + i * 42
        on = i == 4
        p.append(f'<circle cx="{cx}" cy="248" r="12" fill="{ORANGE if on else "#E4DFD6"}"/>')
        if on:
            p.append(f'<circle cx="{cx}" cy="248" r="17" fill="none" stroke="{ORANGE}" stroke-width="2"/>')
    p.append(arrow(240, 226, 240, 178, ORANGE))
    p.append(box(268, 200, 168, 30, WHITE, ORANGE, rx=15, sw=1.6))
    p.append(txt(352, 220, "o espect-ator entra", 10.5, 700, ORANGE_D))

    # what happens once inside
    p.append(arrow(432, 108, 486, 108, GOLD_D))
    steps = [("testa uma atitude", 52), ("percebe seus efeitos", 100),
             ("encontra resistências", 148), ("reformula a estratégia", 196)]
    for label, y in steps:
        p.append(box(496, y, 224, 34, WHITE, RULE, rx=8, sw=1.4))
        p.append(txt(608, y + 22, label, 11, 700, INK))
    for y in (86, 134, 182):
        p.append(arrow(608, y, 608, y + 8, RULE, sw=2))
    # loop back for the next attempt
    p.append(f'<path d="M496 213 H466 V69 H496" fill="none" stroke="{ORANGE}" '
             f'stroke-width="2" stroke-dasharray="5 4"/>')
    p.append(f'<polygon points="502,69 490,64 490,74" fill="{ORANGE}"/>')
    p.append(txt(455, 145, "outra pessoa, outro caminho", 9, 700, ORANGE_D,
                 anchor="middle") .replace('<text ', '<text transform="rotate(-90 455 145)" '))

    p.append(band(W, 306, "O grupo compara escolhas e consequências"))
    return wrap("".join(p), W, H,
                "Teatro Forum: um espect-ator da plateia entra na cena modelo, testa uma "
                "atitude, encontra resistencias e reformula; outra pessoa tenta outro caminho")


# ── 3. Teatro Legislativo: from scene to public policy ──────────────────────
def legislativo():
    W, H = 760, 300
    p = []
    steps = [("CENA", "situações vividas", GREEN_T, GREEN, GREEN_D),
             ("PROPOSTA", "alternativas testadas", GOLD_T, GOLD, GOLD_D),
             ("DEBATE PÚBLICO", "recomendações", ORANGE_T, ORANGE, ORANGE_D),
             ("POLÍTICA PÚBLICA", "formulação coletiva", "#FFFFFF", INK, INK)]
    x, w, gap = 40, 158, 20
    base, rise = 196, 26
    for i, (head, sub, fill, stroke, tc) in enumerate(steps):
        bx = x + i * (w + gap)
        h = 72 + i * rise
        by = base - h
        p.append(box(bx, by, w, h, fill, stroke))
        p.append(txt(bx + w / 2, by + 30, head, 11.5, 700, tc))
        p.append(txt(bx + w / 2, by + 50, sub, 9.5, 400, INK_SOFT))
        if i < 3:
            p.append(arrow(bx + w + 3, base - 30, bx + w + gap - 3, base - 30, GOLD_D, sw=2))

    # the citizen's role shifts underneath
    p.append(f'<defs><linearGradient id="roleGrad" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{GREEN}"/><stop offset="0.5" stop-color="{GOLD}"/>'
             f'<stop offset="1" stop-color="{ORANGE}"/></linearGradient></defs>')
    p.append(f'<rect x="40" y="216" width="{W-80}" height="8" rx="4" fill="url(#roleGrad)"/>')
    p.append(txt(40, 246, "o cidadão como destinatário", 10.5, 700, GREEN_D, anchor="start"))
    p.append(txt(W - 40, 246, "o cidadão como autor", 10.5, 700, ORANGE_D, anchor="end"))
    p.append(txt(W / 2, 274, "Boal como vereador no Rio de Janeiro, 1993–1996",
                 9.5, 400, MUTED))
    return wrap("".join(p), W, H,
                "Teatro Legislativo: da cena a proposta, ao debate publico e a politica "
                "publica; o cidadao deixa de ser destinatario e passa a autor")


if __name__ == "__main__":
    for name, fn in (("teatro-jornal", jornal), ("teatro-forum", forum),
                     ("teatro-legislativo", legislativo)):
        out = SVG / f"{name}.svg"
        out.write_text(fn(), encoding="utf-8")
        print(f"  wrote _src/svg/{name}.svg ({out.stat().st_size} bytes)")
