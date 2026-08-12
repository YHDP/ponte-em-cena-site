#!/usr/bin/env python3
"""Compose the Ponte em Cena site from _src/ into servable HTML at the repo root.

    python3 tools/build.py            # build everything
    python3 tools/build.py --check    # build to memory, fail if disk differs

Why a builder at all: the site is six pages in three languages. Keeping the
head block, nav and funder co-brand band in sync across eighteen hand-authored
files is a drift guarantee, and the funder band in particular carries a brand
rule we verified geometrically. One shell, one stylesheet, one strings file per
language. Same shape as regenstudio-website/build.ts, which generates its blog
pages and sitemap while the rest of that site is hand-authored.

Standard library only. No build step is required to *view* the site — the
output is plain static HTML committed to the repo and served by GitHub Pages.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"

IG_RE = re.compile(r"<!-- IG:START -->.*?<!-- IG:END -->", re.S)

# Months for the human-readable "last updated" stamp, per language.
MONTHS = {
    "pt": "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split(),
    "en": "January February March April May June July August September October November December".split(),
    "nl": "januari februari maart april mei juni juli augustus september oktober november december".split(),
}


def esc(s: str) -> str:
    """Escape for an HTML attribute value."""
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def page_by_slug(cfg: dict, slug: str) -> dict:
    return next(p for p in cfg["pages"] if p["slug"] == slug)


def page_url(cfg: dict, lang: str, slug: str) -> str:
    """Absolute URL for a page, derived from its output path.

    Deriving from `out` rather than from the slug keeps root-level files honest:
    404.html is served at /404.html, not at /404/. Directory pages drop the
    index.html and keep the trailing slash.
    """
    prefix = cfg["languages"][lang]["prefix"]
    tail = page_by_slug(cfg, slug)["out"]
    if tail.endswith("index.html"):
        tail = tail[: -len("index.html")]
    return f"{cfg['base']}/{prefix}{tail}"


def page_href(cfg: dict, lang: str, slug: str) -> str:
    """Root-relative link for in-site navigation.

    NOT page_url(): that returns the absolute production URL, which is correct
    for canonical / hreflang / og:url but wrong for an <a href>. Building the
    nav from it meant every link on a locally served copy jumped straight to
    ponte-em-cena.com.br, so the local site looked like it had no subpages at
    all. Root-relative works on localhost and in production alike.
    """
    return page_url(cfg, lang, slug)[len(cfg["base"]):]


def out_path(cfg: dict, lang: str, page: dict) -> Path:
    prefix = cfg["languages"][lang]["prefix"]
    return ROOT / f"{prefix}{page['out']}"


def rel_prefix(cfg: dict, lang: str, page: dict) -> str:
    """Relative path from a built page back to the repo root, for asset hrefs.

    Counted from the real output path plus the language prefix, so a root-level
    file such as 404.html gets "" while metodologia/index.html gets "../".
    """
    depth = (1 if cfg["languages"][lang]["prefix"] else 0) + page["out"].count("/")
    return "../" * depth if depth else ""


def build_nav(cfg: dict, strings: dict, lang: str, current: str) -> str:
    items = []
    for slug in cfg["nav"]:
        label = strings["nav"][slug]
        href = page_href(cfg, lang, slug)
        aria = ' aria-current="page"' if slug == current else ""
        items.append(f'<li><a href="{href}"{aria}>{esc(label)}</a></li>')
    return "".join(items)


def build_footer_links(cfg: dict, strings: dict, lang: str) -> str:
    out = []
    for slug in ("sobre", "contato", "privacidade"):
        out.append(f'<a href="{page_href(cfg, lang, slug)}">{esc(strings["nav"][slug])}</a>')
    return "".join(out)


GLOBE = ('<svg class="lang-switcher__globe" viewBox="0 0 24 24" fill="none" '
         'stroke="currentColor" stroke-width="1.9" stroke-linecap="round" '
         'aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
         '<path d="M3 12h18M12 3c2.5 2.7 2.5 15.3 0 18M12 3c-2.5 2.7-2.5 15.3 0 18"/></svg>')

SOON = {"pt": "Em breve", "nl": "Binnenkort", "en": "Coming soon"}
SWITCH_LABEL = {"pt": "Idioma", "nl": "Taal", "en": "Language"}


def build_switcher(cfg: dict, lang: str, slug: str, built: set) -> str:
    """Emit the language switcher at BUILD time, not at runtime.

    assets/js/i18n.js can inject this, and did — but injecting a bordered
    control after load shifted the header and cost 0.171 CLS on the home page,
    dropping Lighthouse performance to 92. The builder knows the page's slug and
    language, so it can write the correct hrefs directly. That removes the shift
    and, as a bonus, makes the switcher work with JavaScript disabled. i18n.js
    still contains the injector and no-ops when a switcher is already present.
    """
    langs = [l for l in cfg["languages"] if (l, slug) in built]
    planned = [l for l in cfg.get("planned_languages", []) if (l, slug) not in built]
    if len(langs) < 2 and not planned:
        return ""

    parts, first = [], True
    for l in langs:
        if not first:
            parts.append('<span class="lang-switcher__sep">|</span>')
        first = False
        active = " lang-switcher__link--active" if l == lang else ""
        cur = ' aria-current="true"' if l == lang else ""
        parts.append(
            f'<a href="{page_href(cfg, l, slug)}" class="lang-switcher__link{active}"'
            f' data-lang="{l}"{cur} hreflang="{cfg["languages"][l]["hreflang"]}">{l.upper()}</a>')
    for l in planned:
        if not first:
            parts.append('<span class="lang-switcher__sep">|</span>')
        first = False
        # A span, not a disabled anchor: there is no href to point it at.
        parts.append(
            f'<span class="lang-switcher__link lang-switcher__link--planned" data-lang="{l}"'
            f' aria-disabled="true" title="{esc(SOON[lang])}">{l.upper()}</span>')
    return (f'<div class="lang-switcher" role="group" aria-label="{esc(SWITCH_LABEL[lang])}">'
            + GLOBE + "".join(parts) + "</div>")


def build_hreflang(cfg: dict, slug: str, built: set[tuple[str, str]]) -> str:
    """Alternates for the languages this page actually exists in, plus x-default.

    Claiming an alternate that 404s is worse than omitting it, so EN and NL are
    only advertised once those fragments are written.

    x-default points at PT: it is this site's default language and lives at the
    root. regenstudio-website's rule that x-default is always English is
    specific to that site, not a general one.
    """
    lines = []
    for lang, meta in cfg["languages"].items():
        if (lang, slug) in built:
            lines.append(f'<link rel="alternate" hreflang="{meta["hreflang"]}" href="{page_url(cfg, lang, slug)}">')
    if (cfg["default_lang"], slug) in built:
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{page_url(cfg, cfg["default_lang"], slug)}">')
    return "\n".join(lines)


def build_jsonld(cfg: dict, strings: dict, lang: str, slug: str, page_meta: dict) -> str:
    """One canonical @id per entity, reused across pages, so crawlers and answer
    engines resolve a single graph rather than a per-page island."""
    base, org = cfg["base"], cfg["organization"]
    org_id, site_id = f"{base}/#organization", f"{base}/#website"

    graph = [
        {
            "@type": "Organization",
            "@id": org_id,
            "name": org["name"],
            "url": base + "/",
            "description": org["description"],
            "foundingDate": org["foundingDate"],
            "areaServed": org["areaServed"],
            "sameAs": org["sameAs"],
            "member": [{"@type": "Organization", "name": m["name"], "url": m["url"]}
                       for m in org["member"]],
            "funder": {"@type": "Organization", "name": org["funder"]["name"],
                       "alternateName": org["funder"]["alternateName"]},
        },
        {
            "@type": "WebSite",
            "@id": site_id,
            "url": base + "/",
            "name": org["name"],
            "inLanguage": cfg["languages"][lang]["hreflang"],
            "publisher": {"@id": org_id},
        },
        {
            "@type": "WebPage",
            "@id": page_url(cfg, lang, slug) + "#webpage",
            "url": page_url(cfg, lang, slug),
            "name": page_meta["title"],
            "description": page_meta["description"],
            "inLanguage": cfg["languages"][lang]["hreflang"],
            "isPartOf": {"@id": site_id},
            "about": {"@id": org_id},
            "dateModified": page_meta["updated_iso"],
            "speakable": {"@type": "SpeakableSpecification",
                          "cssSelector": [".hero .lede", ".page-head .lede"]},
        },
    ]

    people = strings.get("people", [])
    if people:
        graph += [{"@type": "Person", "@id": f"{base}/#{p['id']}", "name": p["name"],
                   "jobTitle": p["jobTitle"], "affiliation": {"@type": "Organization",
                   "name": p["affiliation"]}} for p in people]

    # The glossary is the highest-value AI-readability payload here: a
    # methodology project wants its vocabulary quotable and attributable.
    if slug == "metodologia" and strings.get("glossary"):
        terms = []
        for key in cfg["glossary"]:
            t = strings["glossary"].get(key)
            if not t:
                continue
            terms.append({"@type": "DefinedTerm", "@id": f"{base}/metodologia/#{key}",
                          "name": t["name"], "description": t["description"],
                          "inDefinedTermSet": f"{base}/metodologia/#glossary"})
        if terms:
            graph.append({"@type": "DefinedTermSet", "@id": f"{base}/metodologia/#glossary",
                          "name": strings["ui"]["glossaryName"], "hasDefinedTerm": terms})

    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=None, separators=(",", ":"))


def preserve_ig(rendered: str, existing: Path) -> str:
    """Keep whatever scripts/fetch-instagram.mjs last wrote between the markers.

    That script rewrites the built index.html in place, so a naive rebuild would
    silently revert the live gallery to the fragment's empty placeholder. If the
    page on disk has a non-empty IG region, it wins.
    """
    if not existing.exists():
        return rendered
    prev = IG_RE.search(existing.read_text(encoding="utf-8"))
    cur = IG_RE.search(rendered)
    if not prev or not cur:
        return rendered
    body = prev.group(0)
    # "Non-empty" means it carries real markup, not just the comment placeholder.
    if "<section" not in body:
        return rendered
    # Never preserve the fixture gallery. assets/instagram/sample-*.svg are the
    # tiles stamped AMOSTRA that ship until an IG_TOKEN exists, and publishing
    # them to a funder-facing domain is the thing this whole region is careful
    # about. Only a real fetch result earns preservation.
    if "assets/instagram/sample-" in body:
        return rendered
    return rendered[:cur.start()] + body + rendered[cur.end():]


def fragment_for(lang: str, slug: str) -> Path:
    return SRC / "pages" / lang / f"{slug or 'home'}.html"


def render_page(cfg: dict, shell: str, strings: dict, lang: str, page: dict,
                built: set[tuple[str, str]]) -> tuple[Path, str]:
    slug = page["slug"]
    frag_path = fragment_for(lang, slug)

    content = frag_path.read_text(encoding="utf-8").rstrip()
    meta = dict(strings["pages"][slug])

    stamp = dt.datetime.fromtimestamp(frag_path.stat().st_mtime)
    meta["updated_iso"] = stamp.strftime("%Y-%m-%d")
    human = f"{MONTHS[lang][stamp.month - 1]} {stamp.year}"

    p = rel_prefix(cfg, lang, page)
    analytics = cfg.get("analytics") or {}
    endpoint = analytics.get("endpoint", "")
    origin = re.match(r"https://[^/]+", endpoint).group(0) if endpoint else ""

    repl = {
        "{{HTML_LANG}}": cfg["languages"][lang]["htmlLang"],
        # The switcher must only offer languages this page exists in, otherwise
        # a PT-only launch hands visitors two 404s. i18n.js reads this.
        "{{AVAILABLE_LANGS}}": " ".join(l for l in cfg["languages"] if (l, slug) in built),
        # Declared but unwritten languages. Rendered inert in the switcher so
        # the multilingual intent is visible before the translations exist,
        # without ever offering a link that 404s.
        "{{PLANNED_LANGS}}": " ".join(
            l for l in cfg.get("planned_languages", []) if (l, slug) not in built),
        "{{OG_LOCALE}}": cfg["languages"][lang]["ogLocale"],
        "{{BASE}}": cfg["base"],
        "{{P}}": p,
        # {{L}} is the LANGUAGE root; {{P}} is the SITE root. An in-body link
        # written as {{P}}metodologia/ resolves to the Portuguese page from
        # every language, which is exactly how /nl/ and /en/ ended up sending
        # readers to PT. In-body page links use {{L}}. {{P}} stays right for
        # assets, for /mapa-agua/ (one shared, untranslated page) and for the
        # deliberate cross-language link to the PT-only Teatro do Oprimido text.
        "{{L}}": p + cfg["languages"][lang]["prefix"],
        "{{HOME}}": page_href(cfg, lang, ""),
        "{{CANONICAL}}": page_url(cfg, lang, slug),
        # A noindex page (the 404) advertises neither a canonical nor
        # alternates: it is not a destination and must not look like one.
        "{{CANONICAL_TAG}}": "" if meta.get("noindex") else
            f'<link rel="canonical" href="{page_url(cfg, lang, slug)}">\n',
        "{{HREFLANG}}": "" if meta.get("noindex") else build_hreflang(cfg, slug, built),
        "{{TITLE}}": esc(meta["title"]),
        "{{DESCRIPTION}}": esc(meta["description"]),
        # og:title is the punchy brand line; <title> is the descriptive one.
        "{{OG_TITLE}}": esc(meta.get("ogTitle", meta["title"])),
        "{{OG_DESCRIPTION}}": esc(meta.get("ogDescription", meta["description"])),
        "{{OG_IMAGE_ALT}}": esc(strings["ui"]["ogImageAlt"]),
        "{{ROBOTS}}": '<meta name="robots" content="noindex">' if meta.get("noindex") else "",
        "{{JSONLD}}": build_jsonld(cfg, strings, lang, slug, meta),
        "{{NAV}}": build_nav(cfg, strings, lang, slug),
        "{{SWITCHER}}": build_switcher(cfg, lang, slug, built),
        "{{FOOTER_LINKS}}": build_footer_links(cfg, strings, lang),
        "{{CONTENT}}": content,
        "{{CSP_CONNECT}}": f" {origin}" if origin else "",
        "{{TRACKER}}": f'<script src="{p}assets/js/tracker.js" defer></script>' if endpoint else "",
        "{{UPDATED_ISO}}": meta["updated_iso"],
        "{{UPDATED_HUMAN}}": human,
    }
    for key, val in strings["ui"].items():
        repl["{{S_" + re.sub(r"(?<!^)(?=[A-Z])", "_", key).upper() + "}}"] = esc(val)

    # {{SVG:name}} inlines _src/svg/<name>.svg. Inline rather than <img src>
    # because these diagrams are text-heavy and an externally referenced SVG
    # cannot use the page's Space Grotesk — the labels would silently fall back
    # to a system sans. Sourced from brand/templates/ponte-deck-3-oficinas.html
    # by rendering the deck and lifting the generated markup, so the site and
    # the deck show the same artwork rather than two hand-kept copies.
    # Diagrams are translated: tools/translate-svgs.py writes _src/svg/<lang>/.
    # Prefer the current language, fall back to the PT original. The labels do
    # real work in these figures, so a diagram left in Portuguese on an English
    # page is a content bug, not a cosmetic one.
    def inline_svg(m):
        name = m.group(1)
        for cand in (SRC / "svg" / lang / f"{name}.svg", SRC / "svg" / f"{name}.svg"):
            if cand.exists():
                return cand.read_text(encoding="utf-8").strip()
        raise SystemExit(f"missing svg: {name}.svg (looked in svg/{lang}/ and svg/)")
    content = re.sub(r"\{\{SVG:([a-z0-9_-]+)\}\}", inline_svg, content)

    # Content goes in FIRST so that fragments may use {{P}} for asset paths and
    # still get depth-correct hrefs from the substitution pass below.
    html = shell.replace("{{CONTENT}}", content)
    for needle, val in repl.items():
        if needle == "{{CONTENT}}":
            continue
        html = html.replace(needle, val)

    leftover = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", html)))
    if leftover:
        raise SystemExit(f"unfilled placeholders in {lang}/{slug or 'home'}: {', '.join(leftover)}")

    dest = out_path(cfg, lang, page)
    return dest, preserve_ig(html + "\n", dest)


def build_sitemap(cfg: dict, built: set[tuple[str, str]]) -> str:
    """Only list (lang, slug) pairs that were actually generated this run.

    Deriving from the config instead would advertise the full 6x3 matrix while
    EN and NL are still unwritten, i.e. hand search engines 404s. Alternates are
    filtered the same way, so a page that exists only in PT does not claim to
    have EN and NL versions.
    """
    rows = []
    today = dt.date.today().isoformat()
    for lang, slug in sorted(built, key=lambda x: (page_by_slug(cfg, x[1])["out"], x[0])):
        page = page_by_slug(cfg, slug)
        if cfg["strings_by_lang"][lang]["pages"][slug].get("noindex"):
            continue
        langs_with_page = [l for l in cfg["languages"] if (l, slug) in built]
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{cfg["languages"][l]["hreflang"]}" '
            f'href="{page_url(cfg, l, slug)}"/>' for l in langs_with_page)
        if (cfg["default_lang"], slug) in built:
            alts += (f'\n    <xhtml:link rel="alternate" hreflang="x-default" '
                     f'href="{page_url(cfg, cfg["default_lang"], slug)}"/>')
        rows.append(
            f"  <url>\n    <loc>{page_url(cfg, lang, slug)}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{page['changefreq']}</changefreq>\n"
            f"    <priority>{page['priority']}</priority>{alts}\n  </url>")
    # llms.txt is a first-class destination for answer engines, not an
    # afterthought, so it is listed like any other page.
    rows.append(
        f"  <url>\n    <loc>{cfg['base']}/llms.txt</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n"
        f"    <priority>0.9</priority>\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="do not write; exit 1 if any output differs from disk")
    args = ap.parse_args()

    cfg = load_json(SRC / "site.json")
    shell = (SRC / "shell.html").read_text(encoding="utf-8")

    # Pass 1 — discover which (lang, slug) pairs exist, so hreflang and the
    # sitemap only ever point at pages that will actually be on disk.
    cfg["strings_by_lang"] = {}
    built: set[tuple[str, str]] = set()
    missing: list[str] = []
    for lang in cfg["languages"]:
        sp = SRC / "strings" / f"{lang}.json"
        if not sp.exists():
            print(f"  skip {lang}: no strings file yet")
            continue
        cfg["strings_by_lang"][lang] = load_json(sp)
        for page in cfg["pages"]:
            slug = page["slug"]
            if slug not in cfg["strings_by_lang"][lang].get("pages", {}):
                continue
            if fragment_for(lang, slug).exists():
                built.add((lang, slug))
            else:
                missing.append(f"_src/pages/{lang}/{slug or 'home'}.html")

    # Pass 2 — render.
    outputs: dict[Path, str] = {}
    for lang, slug in built:
        page = page_by_slug(cfg, slug)
        dest, html = render_page(cfg, shell, cfg["strings_by_lang"][lang], lang, page, built)
        outputs[dest] = html

    outputs[ROOT / "styles.css"] = (SRC / "styles.css").read_text(encoding="utf-8")
    outputs[ROOT / "sitemap.xml"] = build_sitemap(cfg, built)

    if args.check:
        stale = [p for p, c in outputs.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != c]
        for p in stale:
            print(f"  STALE {p.relative_to(ROOT)}")
        print(f"{len(stale)} stale of {len(outputs)}")
        return 1 if stale else 0

    for path, content in sorted(outputs.items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        changed = not path.exists() or path.read_text(encoding="utf-8") != content
        path.write_text(content, encoding="utf-8")
        print(f"  {'wrote' if changed else 'same '} {path.relative_to(ROOT)}")
    print(f"{len(outputs)} files")
    for m in missing:
        print(f"  MISSING fragment (page skipped): {m}")
    if missing:
        print(f"{len(missing)} page(s) declared in strings but not yet written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
