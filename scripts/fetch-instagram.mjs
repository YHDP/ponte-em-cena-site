#!/usr/bin/env node
// Ponte em Cena — Instagram → static gallery builder.
//
// Pulls @ponteemcena's latest posts via the Instagram Graph API (server-side,
// at BUILD time), downloads each thumbnail into assets/instagram/ (self-hosted),
// writes assets/instagram/posts.json, and injects a static <section class="ig">
// into index.html between the IG:START / IG:END markers.
//
// The visitor's browser only ever loads local images — zero Meta requests, zero
// JS. The only Meta contact is this script talking to the Graph API with the
// project's own token.
//
// Zero npm dependencies (Node 18+ built-ins only).
//
// Modes:
//   • No IG_TOKEN in env  → FIXTURE mode: render from assets/instagram/posts.sample.json
//                           (no network, no downloads). For look/copy review pre-token.
//   • IG_TOKEN present     → LIVE mode: refresh token, fetch media, download, render.
//
// Env:
//   IG_TOKEN       long-lived Instagram access token (LIVE mode)
//   IG_USER_ID     optional; if unset, uses /me/media
//   GRAPH_BASE     default https://graph.instagram.com (Instagram-Login flow)
//   IG_TOKEN_OUT   optional path to write the refreshed token (CI → gh secret set)
//   A local .env file (KEY=VALUE lines) is read if present.

import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, unlinkSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

// ── Config ─────────────────────────────────────────────────────────────
const POST_COUNT     = 6;
const HASHTAG_FILTER = null;          // e.g. '#ponteemcena' to show only tagged project posts
const HANDLE         = 'ponteemcena';
const CAPTION_MAX    = 110;

const ROOT     = join(dirname(fileURLToPath(import.meta.url)), '..');
const IG_DIR   = join(ROOT, 'assets', 'instagram');
const HTML     = join(ROOT, 'index.html');
const DATA     = join(IG_DIR, 'posts.json');
const SAMPLE   = join(IG_DIR, 'posts.sample.json');
const MARK_A   = '<!-- IG:START -->';
const MARK_B   = '<!-- IG:END -->';

// ── Tiny .env loader (no dep) ──────────────────────────────────────────
function loadEnv() {
  const p = join(ROOT, '.env');
  if (!existsSync(p)) return;
  for (const line of readFileSync(p, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/i);
    if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
}
loadEnv();

const TOKEN     = process.env.IG_TOKEN || '';
const USER_ID   = process.env.IG_USER_ID || 'me';
const BASE      = (process.env.GRAPH_BASE || 'https://graph.instagram.com').replace(/\/+$/, '');
const TOKEN_OUT = process.env.IG_TOKEN_OUT || '';

// ── Helpers ────────────────────────────────────────────────────────────
const esc = (s = '') => String(s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');

function excerpt(caption = '') {
  const one = caption.replace(/\s+/g, ' ').trim();
  return one.length > CAPTION_MAX ? one.slice(0, CAPTION_MAX - 1).trimEnd() + '…' : one;
}

async function getJSON(url) {
  const r = await fetch(url);
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(`Graph API ${r.status}: ${JSON.stringify(j.error || j)}`);
  return j;
}

// ── Token refresh (LIVE only) ──────────────────────────────────────────
async function refreshToken() {
  try {
    const j = await getJSON(`${BASE}/refresh_access_token?grant_type=ig_refresh_token&access_token=${encodeURIComponent(TOKEN)}`);
    if (j.access_token && j.access_token !== TOKEN) {
      console.log(`↻ token refreshed (expires in ~${Math.round((j.expires_in || 0) / 86400)}d)`);
      if (TOKEN_OUT) writeFileSync(TOKEN_OUT, j.access_token);   // consumed by CI `gh secret set`
      console.log('::add-mask::' + j.access_token);
      return j.access_token;
    }
  } catch (e) {
    console.warn('⚠ token refresh skipped:', e.message);   // non-fatal; current token still valid
  }
  return TOKEN;
}

// ── Fetch + download (LIVE) ────────────────────────────────────────────
async function fetchLive() {
  const token = await refreshToken();
  const fields = 'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp';
  const j = await getJSON(`${BASE}/${encodeURIComponent(USER_ID)}/media?fields=${fields}&limit=30&access_token=${encodeURIComponent(token)}`);
  let items = (j.data || []);

  if (HASHTAG_FILTER) {
    const tag = HASHTAG_FILTER.toLowerCase();
    items = items.filter(p => (p.caption || '').toLowerCase().includes(tag));
  }
  items = items.slice(0, POST_COUNT);

  const posts = [];
  const keep = new Set();
  for (const p of items) {
    const src = p.media_type === 'VIDEO' ? (p.thumbnail_url || p.media_url) : p.media_url;
    if (!src) continue;
    const file = `${p.id}.jpg`;
    const buf = Buffer.from(await (await fetch(src)).arrayBuffer());
    writeFileSync(join(IG_DIR, file), buf);
    keep.add(file);
    const cap = excerpt(p.caption);
    posts.push({
      id: p.id,
      image: `assets/instagram/${file}`,
      permalink: p.permalink,
      caption: cap,
      alt: `Post de @${HANDLE} no Instagram${cap ? ': ' + cap : ''}`,
      timestamp: p.timestamp,
      type: p.media_type,
    });
  }
  pruneImages(keep);
  return { source: 'graph-api', posts };
}

// Remove stale downloaded thumbs (numeric-id .jpg) no longer in the set.
function pruneImages(keep) {
  for (const f of readdirSync(IG_DIR)) {
    if (/^\d+\.jpg$/.test(f) && !keep.has(f)) unlinkSync(join(IG_DIR, f));
  }
}

// ── Fixture (no token) ─────────────────────────────────────────────────
function fetchFixture() {
  if (!existsSync(SAMPLE)) throw new Error(`No IG_TOKEN and no fixture at ${SAMPLE}`);
  const j = JSON.parse(readFileSync(SAMPLE, 'utf8'));
  return { source: 'sample', posts: (j.posts || []).slice(0, POST_COUNT) };
}

// ── Render the static section ──────────────────────────────────────────
function renderSection(posts) {
  const profile = `https://www.instagram.com/${HANDLE}/`;
  const glyph = `<svg class="ig-glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/></svg>`;

  const cards = posts.map(p => {
    const badge = p.type === 'VIDEO' ? `<span class="ig-badge" aria-hidden="true">▶</span>`
      : p.type === 'CAROUSEL_ALBUM' ? `<span class="ig-badge" aria-hidden="true">▤</span>` : '';
    return `      <a class="ig-card" href="${esc(p.permalink)}" target="_blank" rel="noopener noreferrer" aria-label="${esc(p.alt)}">
        <img loading="lazy" src="${esc(p.image)}" alt="${esc(p.alt)}">${badge}
      </a>`;
  }).join('\n');

  return `${MARK_A}
<!-- Instagram gallery — static, self-hosted, generated by scripts/fetch-instagram.mjs. Do not hand-edit. -->
<section class="ig">
  <div class="wrap">
    <div class="eyebrow">Nas redes</div>
    <div class="prose" style="margin-bottom: clamp(22px,3.5vw,34px)">
      <p>Acompanhe os bastidores e os encontros do projeto pelo Instagram
      do <strong>Ponte em Cena</strong>.</p>
    </div>
    <div class="ig-grid">
${cards}
    </div>
    <a class="ig-follow" href="${profile}" target="_blank" rel="noopener noreferrer">
      ${glyph}<span>Segue <strong>@${esc(HANDLE)}</strong></span>
      <span class="ig-ext" aria-hidden="true">↗</span>
    </a>
  </div>
</section>
${MARK_B}`;
}

function inject(html, block) {
  const a = html.indexOf(MARK_A), b = html.indexOf(MARK_B);
  if (a !== -1 && b !== -1) {
    return html.slice(0, a) + block + html.slice(b + MARK_B.length);
  }
  // First run: insert before the partners section.
  const anchor = '<section class="partners">';
  const i = html.indexOf(anchor);
  if (i === -1) throw new Error('Cannot find IG markers or <section class="partners"> anchor in index.html');
  return html.slice(0, i) + block + '\n\n' + html.slice(i);
}

// ── Main ───────────────────────────────────────────────────────────────
(async () => {
  if (!existsSync(IG_DIR)) mkdirSync(IG_DIR, { recursive: true });

  const { source, posts } = TOKEN ? await fetchLive() : fetchFixture();
  if (!posts.length) { console.error('No posts to render — aborting (index.html untouched).'); process.exit(1); }

  writeFileSync(DATA, JSON.stringify({ handle: HANDLE, source, count: posts.length, posts }, null, 2) + '\n');

  const html = readFileSync(HTML, 'utf8');
  writeFileSync(HTML, inject(html, renderSection(posts)));

  console.log(`✓ ${source}: ${posts.length} posts → posts.json + index.html`);
})().catch(e => { console.error('✗', e.message); process.exit(1); });
