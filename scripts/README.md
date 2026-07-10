# Instagram feed — how it works & how to go live

The lander shows the latest posts from **@in.pulsobr** as a **static, self-hosted
gallery**. Thumbnails are downloaded at build time and served from
`assets/instagram/`, so a visitor's browser **never contacts Meta** — no Meta
JavaScript, no cookies, no trackers. The page stays **zero-JS**: the gallery is
plain HTML baked into `index.html` between the `<!-- IG:START -->` / `<!-- IG:END -->`
markers.

## Pieces

| File | Role |
|---|---|
| `scripts/fetch-instagram.mjs` | Fetches posts (Graph API), downloads thumbnails, writes `posts.json`, injects the static `<section class="ig">` into `index.html`. Zero npm deps (Node 18+). |
| `assets/instagram/posts.json` | Generated manifest (do not hand-edit). |
| `assets/instagram/posts.sample.json` + `sample-*.svg` | Placeholder fixture used when no token is set — lets the section render for review before go-live. |
| `.github/workflows/instagram-refresh.yml` | Weekly cron + manual run: refresh token → fetch → download → commit → Pages redeploys. |

## Modes

- **Fixture (no `IG_TOKEN`)** — renders the placeholder posts. `node scripts/fetch-instagram.mjs`.
- **Live (`IG_TOKEN` set)** — refreshes the token, fetches @in.pulsobr's real posts, downloads thumbs.

Config lives at the top of `fetch-instagram.mjs`: `POST_COUNT` (6),
`HASHTAG_FILTER` (`null`; set to `'#ponteemcena'` to show only tagged project
posts), `HANDLE`.

## Go-live — one-time setup (needs the (in)PULSO account)

Because the account is the partner's, **(in)PULSO** does steps 1–4 once:

1. **Convert @in.pulsobr to a Business or Creator account** (free, ~30s in
   Instagram → Settings → Account type).
2. Create a **Meta Developer app** at developers.facebook.com (keep it in
   *Development* mode — **Standard Access** is enough for one's own account; no
   App Review needed).
3. Add the Instagram product and authorise @in.pulsobr.
4. Generate a **long-lived access token** (60-day, refreshable) and note the
   **Instagram user id**.
   - Default here uses the **Instagram-Login flow** (`graph.instagram.com`,
     refresh via `ig_refresh_token`) — no Facebook Page required.
   - If you use the **Facebook-Login Graph API** instead, link a Facebook Page
     and set `GRAPH_BASE=https://graph.facebook.com/v21.0`.

Then **Yvo** wires the secrets (GitHub → repo → Settings → Secrets and variables
→ Actions):

- `IG_TOKEN` — the long-lived token (**required**).
- `IG_USER_ID` — the user id (optional; omit to use `/me`).
- `GRAPH_BASE` — only if not using the default `graph.instagram.com`.
- `GH_PAT` — optional fine-grained PAT with **Secrets: write** on this repo, so
  the workflow can rotate `IG_TOKEN` automatically each week. Without it, re-paste
  a fresh token roughly every 50 days.

Finally, run the workflow once: **Actions → Refresh Instagram feed → Run workflow**.
The first run downloads real thumbnails, rewrites the gallery, and commits.

## Local run

```bash
cp .env.example .env      # fill IG_TOKEN (+ IG_USER_ID); .env is gitignored
node scripts/fetch-instagram.mjs
```

## Privacy note

The Instagram Graph API is a **build-time** dependency: the only call to Meta
happens in CI (or on your machine), using the project's own token. No visitor
data ever reaches Meta, so no visitor-facing sub-processor disclosure is
triggered. Never commit a token — it lives only in GitHub Secrets or a local
`.env`.
