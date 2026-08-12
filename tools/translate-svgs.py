#!/usr/bin/env python3
"""Emit per-language copies of the diagram SVGs.

    python3 tools/translate-svgs.py        # -> _src/svg/{en,nl}/*.svg

The diagrams carry a lot of meaning and were shipping with Portuguese labels on
the English and Dutch pages. Rather than making four generators language-aware,
this translates their OUTPUT: the PT files stay the single source of geometry,
and this maps every visible string. Keyed on the exact PT text, so regenerating
a diagram keeps working as long as its wording does not change.

The coverage check is the point. Any visible string without an entry is a hard
error, so a diagram can never quietly ship half-translated.

Kleurendenken colour names (Blauw, Geel, ...) stay Dutch everywhere: they are
the method's own terms. Only the parenthetical gloss is localised, and in NL it
becomes the canonical -druk term rather than a redundant repeat of the colour.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src" / "svg"
SKIP_PREFIX = "bridge-"          # lab candidates, not shipped

T = {
 # ── bridge ─────────────────────────────────────────────────────────────
 "BRASIL · TEATRO DO OPRIMIDO": ("BRAZIL · THEATRE OF THE OPPRESSED", "BRAZILIË · THEATER VAN DE ONDERDRUKTEN"),
 "HOLANDA · DESIGN HOLANDÊS": ("NETHERLANDS · DUTCH DESIGN", "NEDERLAND · NEDERLANDS ONTWERP"),
 "OFICINA 01": ("WORKSHOP 01", "WORKSHOP 01"),
 "OFICINA 02": ("WORKSHOP 02", "WORKSHOP 02"),
 "OFICINA 03": ("WORKSHOP 03", "WORKSHOP 03"),
 "Diagnosticar": ("Diagnose", "Diagnosticeren"),
 "Gerar": ("Generate", "Genereren"),
 "Decidir": ("Decide", "Beslissen"),
 "ler o outro": ("reading the other", "de ander lezen"),
 "encenar o impasse": ("staging the deadlock", "de impasse spelen"),
 "propor": ("propose", "voorstellen"),
 "Teatro-Jornal": ("Newspaper Theatre", "Krantentheater"),
 "Teatro Fórum": ("Forum Theatre", "Forumtheater"),
 "Teatro Legislativo": ("Legislative Theatre", "Wetgevend Theater"),
 "Context Mapping": ("Context Mapping", "Context Mapping"),
 "Frame Creation": ("Frame Creation", "Frame Creation"),
 "+ Kleurendenken": ("+ Kleurendenken", "+ kleurendenken"),
 "camada holandesa": ("Dutch layer", "Nederlandse laag"),
 "em co-desenho": ("in co-design", "in co-design"),
 # ── teatro-jornal ──────────────────────────────────────────────────────
 "A NOTÍCIA": ("THE NEWS", "HET BERICHT"),
 "LEITURA": ("READING", "LEZING"),
 "CRUZADA": ("CROSSED", "GEKRUIST"),
 "CENA": ("SCENE", "SCÈNE"),
 "jornal NL": ("Dutch paper", "NL-krant"),
 "jornal BR": ("Brazilian paper", "BR-krant"),
 "o mesmo tema, lado a lado": ("the same subject, side by side", "hetzelfde onderwerp, naast elkaar"),
 "o que omite,": ("what it leaves out,", "wat het weglaat,"),
 "quem não foi ouvido,": ("who was not heard,", "wie niet gehoord is,"),
 "que interesses": ("which interests", "welke belangen"),
 "e cenas a partir": ("and scenes out of", "en scènes uit"),
 "do material": ("the material", "het materiaal"),
 "investigada": ("investigated", "onderzocht"),
 "A informação deixa de ser recebida como algo neutro": ("Information stops being received as neutral", "Informatie wordt niet langer als neutraal ontvangen"),
 "técnicas:": ("techniques:", "technieken:"),
 "imagens": ("images", "beelden"),
 # ── teatro-forum ───────────────────────────────────────────────────────
 "A CENA MODELO": ("THE MODEL SCENE", "DE MODELSCÈNE"),
 "A PLATEIA": ("THE AUDIENCE", "HET PUBLIEK"),
 "A CENA": ("THE SCENE", "DE SCÈNE"),
 "protagonista": ("protagonist", "protagonist"),
 "antagonista": ("antagonist", "tegenspeler"),
 "quer algo e não consegue": ("wants something and cannot get it", "wil iets en krijgt het niet"),
 "o que o impede": ("what stops them", "wat het tegenhoudt"),
 "o espect-ator entra": ("the spect-actor steps in", "de toeschouw-speler stapt in"),
 "testa uma atitude": ("tries an attitude", "beproeft een houding"),
 "percebe seus efeitos": ("sees its effects", "ziet het effect"),
 "encontra resistências": ("meets resistance", "stuit op weerstand"),
 "reformula a estratégia": ("reformulates the strategy", "stelt de strategie bij"),
 "outra pessoa, outro caminho": ("another person, another route", "een ander, een andere weg"),
 "alternativas testadas": ("alternatives tested", "beproefde alternatieven"),
 # ── teatro-legislativo ─────────────────────────────────────────────────
 "PROPOSTA": ("PROPOSAL", "VOORSTEL"),
 "DEBATE PÚBLICO": ("PUBLIC DEBATE", "PUBLIEK DEBAT"),
 "POLÍTICA PÚBLICA": ("PUBLIC POLICY", "PUBLIEK BELEID"),
 "situações vividas": ("situations lived", "geleefde situaties"),
 "coletivamente": ("collectively", "collectief"),
 "formulação coletiva": ("collective drafting", "gezamenlijk formuleren"),
 "recomendações": ("recommendations", "aanbevelingen"),
 "o cidadão como destinatário": ("the citizen as recipient", "de burger als ontvanger"),
 "o cidadão como autor": ("the citizen as author", "de burger als auteur"),
 "O grupo compara escolhas e consequências": ("The group compares choices and consequences", "De groep vergelijkt keuzes en gevolgen"),
 "Boal como vereador no Rio de Janeiro, 1993–1996": ("Boal as a city councillor in Rio de Janeiro, 1993–1996", "Boal als gemeenteraadslid in Rio de Janeiro, 1993–1996"),
 # ── contextmap ─────────────────────────────────────────────────────────
 "SUPERFÍCIE": ("SURFACE", "OPPERVLAK"),
 "PROFUNDO": ("DEEP", "DIEP"),
 "SESSÕES": ("GENERATIVE", "GENERATIEVE"),
 "GERATIVAS": ("SESSIONS", "SESSIES"),
 "o que as pessoas:": ("what people:", "wat mensen:"),
 "dizem": ("say", "zeggen"),
 "pensam": ("think", "denken"),
 "usam": ("use", "gebruiken"),
 "fazem": ("do", "doen"),
 "sabem · sentem": ("know · feel", "weten · voelen"),
 "· sonham": ("· dream", "· dromen"),
 "explícito": ("explicit", "expliciet"),
 "observável": ("observable", "waarneembaar"),
 "tácito": ("tacit", "tacit"),
 "latente": ("latent", "latent"),
 "entrevistas": ("interviews", "interviews"),
 "observações": ("observation", "observatie"),
 "conhecimento:": ("knowledge:", "kennis:"),
 "Motor gerativo → TEATRO (Boal): Jornal · Imagem · Fórum": ("Generative engine → THEATRE (Boal): Newspaper · Image · Forum", "Generatieve motor → THEATER (Boal): Krant · Beeld · Forum"),
 "internamente": ("internally", "intern"),
 "temas que emergem": ("themes that emerge", "thema's die opkomen"),
 # ── kleuren ────────────────────────────────────────────────────────────
 "Geel": ("Geel", "Geel"), "Blauw": ("Blauw", "Blauw"), "Rood": ("Rood", "Rood"),
 "Groen": ("Groen", "Groen"), "Wit": ("Wit", "Wit"),
 "Oranje": ("Oranje", "Oranje"), "Paars": ("Paars", "Paars"),
 "(amarelo)": ("(yellow)", "(geeldruk)"), "(azul)": ("(blue)", "(blauwdruk)"),
 "(vermelho)": ("(red)", "(rooddruk)"), "(verde)": ("(green)", "(groendruk)"),
 "(branco)": ("(white)", "(witdruk)"), "(laranja)": ("(orange)", "(oranjedruk)"),
 "(roxo)": ("(purple)", "(paarsdruk)"),
 "Poder": ("Power", "Macht"),
 "Planejada": ("Planned", "Gepland"),
 "Recompensa": ("Reward", "Beloning"),
 "Aprendizagem": ("Learning", "Leren"),
 "Transformação": ("Emergence", "Zelforganisatie"),
 "Negociação": ("Negotiation", "Onderhandeling"),
 "Desenvolvimento": ("Development", "Ontwikkeling"),
 "interesses,": ("interests,", "belangen,"),
 "coalizões,": ("coalitions,", "coalities,"),
 "poder,": ("power,", "macht,"),
 "negociar": ("negotiate", "onderhandelen"),
 "do topo; metas;": ("from the top; targets;", "van bovenaf; doelen;"),
 "racional; KPIs": ("rational; KPIs", "rationeel; KPI's"),
 "planejamento": ("planning", "planning"),
 "alavancas de RH": ("HR levers", "HR-hefbomen"),
 "motivar;": ("motivate;", "motiveren;"),
 "reconhecimento;": ("recognition;", "erkenning;"),
 "vender": ("sell", "verkopen"),
 "aprender;": ("learn;", "leren;"),
 "refletir;": ("reflect;", "reflecteren;"),
 "diálogo e": ("dialogue and", "dialoog en"),
 "mudar estratégias e práticas": ("change strategy and practice", "strategie en praktijk veranderen"),
 "auto-organização;": ("self-organisation;", "zelforganisatie;"),
 "bottom-up;": ("bottom-up;", "bottom-up;"),
 "espaço;": ("space;", "ruimte;"),
 "sentido": ("meaning", "betekenis"),
 "confiança": ("trust", "vertrouwen"),
 "por projeto;": ("by project;", "per project;"),
 "co-criação": ("co-creation", "co-creatie"),
 "conjunto": ("joint", "gezamenlijk"),
 "muda através de": ("changes through", "verandert door"),
 "forçar a partir": ("forcing from", "forceren van"),
 "5 canônicas — De Caluwé &amp; Vermaak, 1999": ("5 canonical — De Caluwé &amp; Vermaak, 1999", "5 canonieke — De Caluwé &amp; Vermaak, 1999"),
 "+ 2 de enriquecimento — Koeleman, 2013": ("+ 2 enrichment — Koeleman, 2013", "+ 2 verrijkend — Koeleman, 2013"),
 "De Caluwé &amp; Vermaak ’99": ("De Caluwé &amp; Vermaak ’99", "De Caluwé &amp; Vermaak ’99"),
 "+ Koeleman ’13": ("+ Koeleman ’13", "+ Koeleman ’13"),
 # ── frame ──────────────────────────────────────────────────────────────
 "ABRIR · expandir (1–5)": ("OPEN UP · expand (1–5)", "OPENEN · verbreden (1–5)"),
 "REENQUADRAR · pivô": ("REFRAME · pivot", "HERKADEREN · scharnier"),
 "APLICAR · convergir (7–9)": ("APPLY · converge (7–9)", "TOEPASSEN · convergeren (7–9)"),
 "Arqueologia": ("Archaeology", "Archeologie"),
 "Paradoxo": ("Paradox", "Paradox"),
 "Contexto": ("Context", "Context"),
 "Campo": ("Field", "Veld"),
 "Temas": ("Themes", "Thema's"),
 "Quadros": ("Frames", "Kaders"),
 "(Frames)": ("(Frames)", "(Frames)"),
 "Futuros": ("Futures", "Toekomsten"),
 "Integração": ("Integration", "Integratie"),
 "história do problema": ("history of the problem", "geschiedenis van het probleem"),
 "o que torna isto difícil?": ("what makes this hard?", "wat maakt dit lastig?"),
 "círculo interno de atores": ("inner circle of actors", "binnenste kring van actoren"),
 "explorar o campo amplo": ("explore the wider field", "het brede veld verkennen"),
 "lições &amp; oportunidades na rede": ("lessons &amp; opportunities in the network", "lessen &amp; kansen in het netwerk"),
 "resultados &amp; propostas de valor": ("outcomes &amp; value propositions", "uitkomsten &amp; waardeproposities"),
 "▶ Teatro Fórum ao vivo": ("▶ Forum Theatre, live", "▶ Forumtheater, live"),
}

NUMERIC = re.compile(r'^[\d\s.,%°/+—→⇄·–-]*$')

def main():
    files = [f for f in sorted(SRC.glob("*.svg")) if not f.name.startswith(SKIP_PREFIX)]
    missing, written = set(), 0
    for idx, lang in enumerate(("en", "nl")):
        out_dir = SRC / lang
        out_dir.mkdir(exist_ok=True)
        for f in files:
            s = f.read_text(encoding="utf-8")
            def sub(m):
                txt = m.group(1)
                key = txt.strip()
                if not key or NUMERIC.match(key):
                    return m.group(0)
                if key not in T:
                    missing.add(key)
                    return m.group(0)
                return m.group(0).replace(txt, T[key][idx])
            s = re.sub(r'>([^<>]{1,80})<', sub, s)
            (out_dir / f.name).write_text(s, encoding="utf-8")
            written += 1
    if missing:
        print(f"translate-svgs: {len(missing)} untranslated string(s):", file=sys.stderr)
        for k in sorted(missing):
            print(f"  {k!r}", file=sys.stderr)
        raise SystemExit(1)
    print(f"  wrote {written} file(s) across en, nl")

if __name__ == "__main__":
    main()
