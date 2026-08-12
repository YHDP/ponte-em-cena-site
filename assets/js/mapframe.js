/* mapframe.js — size the embedded map frame to its own content.
 *
 * The map page reflows hard: measured at 1000px wide it needs 1127px of
 * height, but at 900px the .ferramenta grid drops to one column and it needs
 * 1606px. A CSS aspect-ratio can only ever approximate that, and approximating
 * it means either an inner scrollbar or a slab of dead space. The frame is
 * same-origin, so it can just read the real height instead of guessing.
 *
 * The CSS aspect-ratio stays as the pre-JS default: without this file the
 * frame is still usable, it just scrolls internally on narrow screens.
 */
(function () {
  "use strict";

  var frames = document.querySelectorAll(".mapa-embed iframe");
  if (!frames.length) return;

  function measure(doc) {
    var de = doc.documentElement;
    var b = doc.body;
    return Math.max(
      de ? de.scrollHeight : 0,
      de ? de.offsetHeight : 0,
      b ? b.scrollHeight : 0,
      b ? b.offsetHeight : 0
    );
  }

  function fit(frame) {
    var doc;
    try {
      doc = frame.contentDocument;
    } catch (e) {
      return; // cross-origin; nothing to do but leave the CSS ratio in place
    }
    if (!doc || !doc.body) return;
    var h = measure(doc);
    if (h > 0) {
      frame.style.height = h + "px";
      // Height now drives the box, so the ratio must stop competing with it.
      frame.style.aspectRatio = "auto";
    }
  }

  function watch(frame) {
    fit(frame);
    var doc;
    try {
      doc = frame.contentDocument;
    } catch (e) {
      return;
    }
    if (!doc || !doc.body || typeof ResizeObserver !== "function") return;
    // Selecting a municipality expands the detail panel, which changes the
    // document height after load. Re-fit when it does.
    new ResizeObserver(function () {
      fit(frame);
    }).observe(doc.body);
  }

  Array.prototype.forEach.call(frames, function (frame) {
    frame.addEventListener("load", function () {
      watch(frame);
    });
    // A lazy frame that is already complete when this runs fires no load event.
    try {
      if (frame.contentDocument && frame.contentDocument.readyState === "complete") {
        watch(frame);
      }
    } catch (e) {
      /* cross-origin */
    }
  });

  var t;
  window.addEventListener("resize", function () {
    clearTimeout(t);
    t = setTimeout(function () {
      Array.prototype.forEach.call(frames, function (frame) {
        // Clear first: a frame stuck at the old tall height would report that
        // height back and never shrink.
        frame.style.height = "";
        fit(frame);
      });
    }, 180);
  });
})();
