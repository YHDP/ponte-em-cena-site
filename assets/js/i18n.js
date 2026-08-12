/**
 * i18n.js — language switching for Ponte em Cena.
 *
 * Ported from regenstudio-website/assets/js/i18n.js, with two deliberate
 * differences.
 *
 * 1. PT is the default and lives at the site root, so the prefixes are /en/
 *    and /nl/ and DEFAULT_LANG is "pt". On Regen the default is English.
 *
 * 2. Ponte's pages are composed by tools/build.py, which writes each language's
 *    nav, footer and metadata straight into the HTML. There is therefore
 *    nothing for the runtime to swap on a normal page, and no locale file is
 *    fetched unless a page actually carries [data-i18n] nodes. The swapping
 *    path is kept for strings that only exist at runtime, and so this file
 *    stays recognisably the same engine as Regen's.
 *
 * What it always does: injects the language switcher, which cannot be
 * generated at build time because it has to point at the current path.
 *
 * Privacy: self-hosted, no external services, no cookies, no storage.
 */
(function () {
  "use strict";

  var SUPPORTED = ["pt", "nl", "en"];
  var DEFAULT_LANG = "pt";
  /* PT is served as pt-BR; the others match their bare code. */
  var HREFLANG = { pt: "pt-BR", nl: "nl", en: "en" };
  var SOON = { pt: "Em breve", nl: "Binnenkort", en: "Coming soon" };
  /* Suggestion-bar copy, in the language being offered — the point is that a
     visitor who does not read the current page can still read the offer. */
  var OFFER = {
    en: { text: "This page is also available in English.", cta: "Read in English", close: "Dismiss" },
    nl: { text: "Deze pagina is ook in het Nederlands beschikbaar.", cta: "Lees in het Nederlands", close: "Sluiten" },
    pt: { text: "Esta página também está disponível em português.", cta: "Ler em português", close: "Fechar" }
  };
  var DISMISS_KEY = "_ponte_lang_bar";

  function detectLang() {
    var path = window.location.pathname;
    for (var i = 0; i < SUPPORTED.length; i++) {
      var l = SUPPORTED[i];
      if (l === DEFAULT_LANG) continue;
      if (path.indexOf("/" + l + "/") === 0 || path === "/" + l) return l;
    }
    return DEFAULT_LANG;
  }

  var LANG = detectLang();

  var _strings = {};
  var _ready = false;
  var _callbacks = [];

  function markReady(strings) {
    _strings = strings || {};
    _ready = true;
    window.__i18n.strings = _strings;
    window.__i18n.ready = true;
    for (var i = 0; i < _callbacks.length; i++) {
      try { _callbacks[i](); } catch (e) { /* a bad callback must not stop the rest */ }
    }
    _callbacks = [];
    if (typeof CustomEvent === "function") {
      document.dispatchEvent(new CustomEvent("i18nReady"));
    }
  }

  /* --- Locale loading (only when a page has runtime strings) --- */

  function loadLocale(callback) {
    if (LANG === DEFAULT_LANG || !document.querySelector("[data-i18n],[data-i18n-placeholder],[data-i18n-aria],[data-i18n-html]")) {
      callback({});
      return;
    }
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/locales/" + LANG + ".json", true);
    xhr.onreadystatechange = function () {
      if (xhr.readyState !== 4) return;
      var parsed = {};
      if (xhr.status === 200) {
        try { parsed = JSON.parse(xhr.responseText); } catch (e) { parsed = {}; }
      }
      callback(parsed);
    };
    xhr.send();
  }

  function applyTranslations(strings) {
    if (!strings || !Object.keys(strings).length) return;
    var map = [
      ["[data-i18n]", "data-i18n", function (el, v) { el.textContent = v; }],
      ["[data-i18n-placeholder]", "data-i18n-placeholder", function (el, v) { el.setAttribute("placeholder", v); }],
      ["[data-i18n-aria]", "data-i18n-aria", function (el, v) { el.setAttribute("aria-label", v); }],
      ["[data-i18n-html]", "data-i18n-html", function (el, v) { el.innerHTML = v; }]
    ];
    for (var m = 0; m < map.length; m++) {
      var els = document.querySelectorAll(map[m][0]);
      for (var i = 0; i < els.length; i++) {
        var v = strings[els[i].getAttribute(map[m][1])];
        if (v) map[m][2](els[i], v);
      }
    }
  }

  /* --- Language switcher --- */

  /* Strips the current prefix and re-adds the target one, so the switcher
     always lands on the SAME page in the other language. This is why every
     language shares one set of slugs (see _src/site.json). */
  function buildSwitcherUrl(targetLang) {
    var path = window.location.pathname;
    for (var i = 0; i < SUPPORTED.length; i++) {
      var l = SUPPORTED[i];
      if (l === DEFAULT_LANG) continue;
      if (path.indexOf("/" + l + "/") === 0 || path === "/" + l) {
        path = path.substring(l.length + 1) || "/";
        break;
      }
    }
    if (path.charAt(0) !== "/") path = "/" + path;
    return targetLang === DEFAULT_LANG ? path : "/" + targetLang + path;
  }

  /* Languages this page actually exists in. tools/build.py stamps them on
     <html data-langs>, because offering a link to a translation that has not
     been written yet just hands the visitor a 404. Falls back to all supported
     languages if the attribute is absent. */
  function langsFrom(attrName, fallback) {
    var attr = (document.documentElement.getAttribute(attrName) || "").trim();
    if (!attr) return fallback || [];
    var listed = attr.split(/\s+/), out = [];
    for (var i = 0; i < SUPPORTED.length; i++) {
      if (listed.indexOf(SUPPORTED[i]) !== -1) out.push(SUPPORTED[i]);
    }
    return out;
  }

  function availableLangs() {
    var built = langsFrom("data-langs", SUPPORTED);
    return built.length ? built : SUPPORTED;
  }

  /* Declared but not yet written. Rendered visibly and inertly so the
     multilingual intent is legible before the translations exist. */
  function plannedLangs() {
    var built = availableLangs(), planned = langsFrom("data-langs-planned"), out = [];
    for (var i = 0; i < planned.length; i++) {
      if (built.indexOf(planned[i]) === -1) out.push(planned[i]);
    }
    return out;
  }

  function buildSwitcherHTML() {
    var built = availableLangs(), planned = plannedLangs();
    /* Nothing to switch to and nothing on the way: render nothing at all. */
    if (built.length < 2 && !planned.length) return "";

    var html = "", first = true, i, lang;
    for (i = 0; i < built.length; i++) {
      lang = built[i];
      if (!first) html += '<span class="lang-switcher__sep">|</span>';
      first = false;
      html += '<a href="' + buildSwitcherUrl(lang) + '" class="lang-switcher__link' +
              (lang === LANG ? " lang-switcher__link--active" : "") + '"' +
              ' data-lang="' + lang + '"' + (lang === LANG ? ' aria-current="true"' : "") +
              ' hreflang="' + HREFLANG[lang] + '">' + lang.toUpperCase() + "</a>";
    }
    for (i = 0; i < planned.length; i++) {
      lang = planned[i];
      if (!first) html += '<span class="lang-switcher__sep">|</span>';
      first = false;
      /* A span, not a disabled anchor: there is no href to give it. */
      html += '<span class="lang-switcher__link lang-switcher__link--planned"' +
              ' data-lang="' + lang + '" aria-disabled="true" title="' +
              SOON[LANG] + '">' + lang.toUpperCase() + "</span>";
    }
    return html;
  }

  /* Inline SVG, not an image request and not an emoji: emoji render
     differently on every platform and some not at all. */
  var GLOBE =
    '<svg class="lang-switcher__globe" viewBox="0 0 24 24" fill="none" ' +
    'stroke="currentColor" stroke-width="1.9" stroke-linecap="round" ' +
    'aria-hidden="true"><circle cx="12" cy="12" r="9"/>' +
    '<path d="M3 12h18M12 3c2.5 2.7 2.5 15.3 0 18M12 3c-2.5 2.7-2.5 15.3 0 18"/></svg>';

  function injectSwitcher() {
    var host = document.querySelector(".nav__actions");
    if (!host || host.querySelector(".lang-switcher")) return;
    var markup = buildSwitcherHTML();
    if (!markup) return;   /* only one language available — render nothing */
    markup = GLOBE + markup;
    var box = document.createElement("div");
    box.className = "lang-switcher";
    box.setAttribute("role", "group");
    box.setAttribute("aria-label", { pt: "Idioma", nl: "Taal", en: "Language" }[LANG]);
    box.innerHTML = markup;
    host.appendChild(box);
  }

  /* --- Public API — same surface as the Regen engine --- */

  window.__i18n = {
    lang: LANG,
    supported: SUPPORTED,
    ready: false,
    strings: {},
    t: function (key, fallback) {
      return (_ready && _strings[key]) || fallback || key;
    },
    onReady: function (cb) {
      if (_ready) { cb(); } else { _callbacks.push(cb); }
    },
    buildSwitcherUrl: buildSwitcherUrl
  };

  /* Offer the visitor's own language without ever taking them there.
     A client-side redirect on static hosting means a flash of the wrong page,
     it breaks the hreflang model, and Googlebot crawls from the US so it would
     only ever see English. Serving the requested URL and offering the other is
     what Google's own guidance recommends instead. */
  function suggestLanguage() {
    try {
      if (window.sessionStorage && sessionStorage.getItem(DISMISS_KEY)) return;
    } catch (e) { /* storage blocked — just show it */ }

    var pref = (navigator.language || "").slice(0, 2).toLowerCase();
    if (!pref || pref === LANG) return;
    if (availableLangs().indexOf(pref) === -1) return;   /* not built yet */

    var copy = OFFER[pref];
    if (!copy) return;

    var bar = document.createElement("div");
    bar.className = "langbar";
    bar.setAttribute("lang", HREFLANG[pref]);
    var inner = document.createElement("div");
    inner.className = "wrap langbar__in";
    var span = document.createElement("span");
    span.textContent = copy.text;
    var link = document.createElement("a");
    link.href = buildSwitcherUrl(pref);
    link.textContent = copy.cta;
    link.setAttribute("hreflang", HREFLANG[pref]);
    var close = document.createElement("button");
    close.type = "button";
    close.textContent = copy.close;
    close.addEventListener("click", function () {
      bar.parentNode.removeChild(bar);
      try { sessionStorage.setItem(DISMISS_KEY, "1"); } catch (e) {}
    });
    inner.appendChild(span); inner.appendChild(link); inner.appendChild(close);
    bar.appendChild(inner);
    document.body.insertBefore(bar, document.body.firstChild);
  }

  function init() {
    document.documentElement.lang = HREFLANG[LANG];
    injectSwitcher();
    suggestLanguage();
    loadLocale(function (strings) {
      applyTranslations(strings);
      markReady(strings);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
