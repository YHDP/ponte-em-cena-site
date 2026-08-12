# Ponte em Cena — vendored fonts (provenance + license)

Self-hosted woff2 for the locked Ponte brand system. Vendored 2026-05-15.
Self-hosting is mandatory per the global font rule
(`~/.claude/rules/common/dependencies.md` — no CDN font delivery).

After the typography lock (`type7`), the eight audition families were pruned
(2026-05-15). Only the two **locked** families remain. Both are
**SIL Open Font License 1.1** — clean for commercial use and redistribution
alongside PolyForm-NC code (dependency-evaluation framework, criterion 3: PASS).

| Family | Role | Files | Source |
|---|---|---|---|
| **Space Grotesk** | wordmark / display | `spacegrotesk-var.woff2` (variable, wght 300–700) | Google Fonts (SIL OFL 1.1) |
| **Gelasio** | body / running text (Georgia-metric) | `gelasio-var.woff2` (variable, wght 400–700), `gelasio-italic.woff2` (static 400) | Google Fonts (SIL OFL 1.1) |

**Consolidated 2026-08-10.** Both families were previously vendored under
per-weight filenames (`spacegrotesk-{400,500,700}-normal.woff2`,
`gelasio-{400,600}-normal.woff2`) that were byte-identical duplicates of a
single variable file each. Declaring a variable font under a single
`font-weight` value pins it to its default instance, so the locked wordmark
weight 700 rendered as the file's default 300 ("Space Grotesk Light") with
synthetic bold, and browsers fetched the same file three times. Now one file
per family, declared with a weight range. No licence change — same upstream
releases, same SIL OFL 1.1.

`ponte-fonts.css` declares the `@font-face` rules pointing at these local woff2.
The `latin` subset covers Latin-1 Supplement, so PT (ã õ ç) and NL diacritics
render natively. These two licence rows promote into the project-wide
`NOTICE.md` in Phase 2.
