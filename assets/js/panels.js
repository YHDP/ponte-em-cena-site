/**
 * panels.js — turns a list of methods into a single-open disclosure set.
 *
 * Progressive enhancement, deliberately. Without JavaScript every panel is
 * simply visible and the section reads as a plain sequence of headed sections:
 * nothing is hidden behind a script. This file only ADDS the open/close
 * behaviour, so a failed or blocked load costs interactivity, never content.
 * It also means crawlers and answer engines see all explanations regardless.
 *
 * Why disclosure and not tabs. This was an ARIA tablist until the cards were
 * grouped by oficina. A `tablist` may only contain `tab` children, so the
 * three real <h3> group headings would either be invalid or have to be hidden
 * from assistive tech with role="presentation" — which throws away exactly the
 * grouping a screen-reader user needs most. Buttons with aria-expanded carry
 * the same behaviour, stay valid with headings interleaved, and are natively
 * keyboard-operable without a roving tabindex.
 *
 * Markup contract (see _src/pages/<lang>/metodologia.html):
 *   <div class="methods" data-panels>
 *     <div class="methods__tabs">
 *       <h3 class="methods__head">…</h3>          ← any number, anywhere
 *       <button class="m-tab" data-target="ID">…</button> × N
 *     </div>
 *     <div class="m-panel" id="ID">…</div> × N
 *   </div>
 *
 * Single-open: opening one closes the rest, so the explanation always appears
 * directly under the card grid rather than pushing it around.
 *
 * Self-hosted, no dependencies, no storage, no network.
 */
(function () {
  "use strict";

  function setup(root) {
    var buttons = [].slice.call(root.querySelectorAll(".m-tab"));
    var panels = buttons
      .map(function (b) { return document.getElementById(b.getAttribute("data-target")); })
      .filter(Boolean);
    if (buttons.length !== panels.length || !buttons.length) return;

    buttons.forEach(function (btn, i) {
      var panel = panels[i];
      if (!btn.id) btn.id = panel.id + "-btn";
      btn.setAttribute("aria-controls", panel.id);
      panel.setAttribute("role", "region");
      panel.setAttribute("aria-labelledby", btn.id);
      btn.addEventListener("click", function () {
        /* Clicking the open one closes it, so the grid can return to rest. */
        var opening = btn.getAttribute("aria-expanded") !== "true";
        select(opening ? i : -1);
        /* The panel renders BELOW the whole card grid. With seven cards that
           is far enough down that on a laptop the answer opens off-screen and
           the click reads as doing nothing. Bring it into view, but only when
           it actually is out of view, so a click on a panel you can already
           see does not yank the page. */
        if (!opening) return;
        var panel = panels[i];
        var r = panel.getBoundingClientRect();
        var headroom = 90;                      /* the sticky header */
        if (r.top < headroom || r.top > window.innerHeight - 80) {
          var reduce = window.matchMedia
            && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
          var y = window.pageYOffset + r.top - headroom;
          if (window.scrollTo && !reduce) {
            window.scrollTo({ top: y, behavior: "smooth" });
          } else {
            window.scrollTo(0, y);
          }
        }
      });
    });

    function select(idx) {
      buttons.forEach(function (btn, i) {
        var on = i === idx;
        btn.setAttribute("aria-expanded", on ? "true" : "false");
        panels[i].hidden = !on;
      });
    }

    root.classList.add("is-enhanced");

    /* Deep links. A link to #m-jornal used to land on a panel that select(0)
       had just hidden, so the browser jumped to a display:none element and
       nothing moved — on a page full of diagrams and cards that reads as a
       broken link rather than a closed panel. Open the panel named in the
       hash instead, and scroll it into view ourselves, because the jump has
       already happened by the time we un-hide it. */
    function openFromHash() {
      var id = (location.hash || "").slice(1);
      if (!id) return false;
      for (var i = 0; i < panels.length; i++) {
        if (panels[i].id === id) {
          select(i);
          panels[i].scrollIntoView({ block: "start" });
          buttons[i].focus({ preventScroll: true });
          return true;
        }
      }
      return false;
    }

    if (!openFromHash()) select(0);
    window.addEventListener("hashchange", openFromHash);
  }

  function init() {
    [].slice.call(document.querySelectorAll("[data-panels]")).forEach(setup);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
