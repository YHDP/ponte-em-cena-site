/**
 * PonteTracker — Privacy-preserving first-party analytics.
 * ES5-compatible IIFE. Auto-initializes on load.
 *
 * Configured for: ponte-em-cena.com.br (site: 'ponte')
 *
 * Ported unchanged from regenstudio-website/assets/js/tracker.js apart from
 * the four config points below: SITE, the dev/staging bail-out, the
 * internal-referrer list, and the global name. The backend is the SAME
 * Supabase Edge Function — it already carries a `site` discriminator, which is
 * why running a second site through it is configuration rather than new
 * infrastructure. ponte-em-cena.com.br must be present in that function's
 * ALLOWED_ORIGINS or every event is rejected server-side.
 *
 * No cookies. No localStorage. One tab-scoped sessionStorage key
 * (_rt_prev_page) for internal navigation flow. Raw IPs are never stored: the
 * function hashes them with a daily-rotating salt and deletes raw events after
 * 48 hours. Disclosed on /privacidade/ — keep the two in step.
 *
 * Features:
 * - page_view with referrer_domain + from_page (sessionStorage)
 * - scroll depth: 25/50/75/100%
 * - click tracking on [data-track] elements
 * - page_exit with time_on_page_ms
 * - Public API: window.PonteTracker.track(eventType, extra)
 */
(function () {
  'use strict';

  // ── Skip tracking on dev + staging environments ──
  var h = window.location.hostname;
  if (h === 'localhost' || h === '127.0.0.1' || h === '0.0.0.0' || h === '') return;

  var ENDPOINT = 'https://uemspezaqxmkhenimwuf.supabase.co/functions/v1/private-track-report-event';
  var SITE = 'ponte';
  var pageLoadTime = Date.now();

  // ── Bot detection — flag known crawlers (still tracked, tagged as bot) ──
  var _ua = navigator.userAgent || '';
  var _isBot = /bot|crawl|spider|slurp|bingpreview|mediapartners|facebookexternalhit|linkedinbot|twitterbot|whatsapp|telegrambot|googlebot|yandex|baidu|duckduckbot|semrush|ahrefs|mj12bot|dotbot|petalbot|bytespider|gptbot|chatgpt|claudebot|anthropic|perplexity|applebot|archive\.org|ia_archiver|wget|curl|python-requests|httpx|node-fetch|axios|postman|lighthouse|pagespeed|gtmetrix|headlesschrome/i.test(_ua);
  // Headless browser detection (catches puppeteer, playwright, selenium)
  if (!_isBot && (navigator.webdriver || !navigator.languages || navigator.languages.length === 0)) _isBot = true;

  // ── Timezone (used server-side for country mapping) ──
  var tz = '';
  try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}

  // ── Send helper ──
  function send(payload) {
    try {
      payload.site = SITE;
      if (_isBot) payload.is_bot = true;
      if (tz) payload.timezone = tz;
      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: JSON.stringify(payload),
        keepalive: true
      }).catch(function () {});
    } catch (e) {
      // Analytics must never break the page
    }
  }

  // ── Referrer domain (external only — internal navigation uses from_page) ──
  var referrerDomain = null;
  try {
    if (document.referrer) {
      var rh = new URL(document.referrer).hostname;
      if (rh !== 'ponte-em-cena.com.br' && rh !== 'www.ponte-em-cena.com.br') {
        referrerDomain = rh;
      }
    }
  } catch (e) { /* malformed referrer */ }

  // ── From-page tracking (sessionStorage, tab-scoped, no personal data) ──
  var fromPage = null;
  try {
    fromPage = sessionStorage.getItem('_rt_prev_page') || null;
  } catch (e) { /* private browsing */ }

  var currentPath = window.location.pathname;

  try {
    sessionStorage.setItem('_rt_prev_page', currentPath);
  } catch (e) { /* private browsing */ }

  // ── Public API ──
  function track(eventType, extra) {
    var payload = {
      event_type: eventType,
      pathname: currentPath,
      referrer_domain: referrerDomain
    };
    if (fromPage) payload.from_page = fromPage;
    if (extra) {
      if (extra.target) payload.target = extra.target;
      if (extra.section) payload.section = extra.section;
      if (extra.from_page) payload.from_page = extra.from_page;
      if (typeof extra.time_on_page_ms === 'number') payload.time_on_page_ms = extra.time_on_page_ms;
    }
    send(payload);
  }

  window.PonteTracker = { track: track };

  // ── Auto page_view ──
  track('page_view');

  // ── Scroll depth tracking ──
  var scrollThresholds = [25, 50, 75, 100];
  var firedThresholds = {};

  function onScroll() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    if (docHeight <= 0) return;
    var percent = Math.round((scrollTop / docHeight) * 100);
    for (var i = 0; i < scrollThresholds.length; i++) {
      var t = scrollThresholds[i];
      if (percent >= t && !firedThresholds[t]) {
        firedThresholds[t] = true;
        track('scroll_' + t);
      }
    }
  }

  if (window.addEventListener) {
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // ── Click tracking on [data-track] elements ──
  function onDocClick(e) {
    var el = e.target;
    // Walk up to find nearest [data-track]
    while (el && el !== document.body) {
      if (el.getAttribute && el.getAttribute('data-track')) {
        var targetName = el.getAttribute('data-track');
        // Find nearest [data-section] ancestor (or self)
        var sectionName = '';
        var sec = el;
        while (sec && sec !== document.body) {
          if (sec.getAttribute && sec.getAttribute('data-section')) {
            sectionName = sec.getAttribute('data-section');
            break;
          }
          sec = sec.parentElement;
        }
        track('click', { target: targetName, section: sectionName });
        return;
      }
      el = el.parentElement;
    }
  }

  if (document.addEventListener) {
    document.addEventListener('click', onDocClick, false);
  }

  // ── Page exit with time on page ──
  var exitFired = false;

  function fireExit() {
    if (exitFired) return;
    exitFired = true;
    var timeOnPage = Date.now() - pageLoadTime;
    track('page_exit', { time_on_page_ms: timeOnPage });
  }

  if (document.addEventListener) {
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') fireExit();
    }, false);
    window.addEventListener('pagehide', fireExit, false);
    window.addEventListener('beforeunload', fireExit, false);
  }

})();
