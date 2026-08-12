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
        select(btn.getAttribute("aria-expanded") === "true" ? -1 : i);
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
    select(0);
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
