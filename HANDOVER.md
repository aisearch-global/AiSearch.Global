# Handover Brief — AISearch Global Website

**Project:** `C:\Users\dasku\OneDrive\Documents\Aisearch.global` (git repo, Cloudflare Pages static site)
**Last updated:** 2026-06-25
**Live site:** https://aisearch.global
**Repo:** github.com/aisearch-global/AiSearch.Global (auto-deploy on push to `main`)

---

## Critical constraints — NEVER touch without explicit confirmation in chat

- `assets/js/main.js` — the `var H = ...` header block, footer social URLs, GA event logic, Bootstrap Icons classes
- `insights/aisearch-global-client-zero.html` — locked article, edit only on explicit request
- `insights/client-zero-visibility-dashboard.html` — locked dashboard, edit only on explicit request
- See `CLAUDE.md` for full locked-asset rules: logos, GA ID `G-XBZMSCBXBZ`, favicon, brand colours, Formspree form ID, `.html` extension rule, Bootstrap Icons rule

---

## Current live state (as of 2026-06-25)

### Visibility Dashboard
`insights/client-zero-visibility-dashboard.html` — **completely replaced** this session.

The old DC design component (used `support.js` / `<x-dc>` / `<sc-for>` template syntax — was broken) and all previous cockpit/accordion/bento iterations are **gone**. The file is now a fully working, standalone vanilla JS implementation.

**What it is:**
- Self-contained page — no `main.js`, no framework, no Chart.js or external chart library
- Own header with `/assets/images/logos/header-logo.svg` logo, GA4, Bootstrap Icons CDN, Google Fonts
- 11 metrics: AEO Score · Brand Recognition · Share of Voice · Sentiment · Presence Quality · GEO Visibility · Analysis Summary · Narrative Themes · Source Analysis · Site Performance · Technical Foundation
- Left rail: clickable metric cards + archetype dial + overall engine score bars + 3 verify tool links
- Right panel: dynamically built per metric — provider rings, SVG donuts (SoV), radar chart, vertical bars, lollipop, heatmap, strength/gap chips, step journey, narrative theme cards, timeline
- Bottom strip: "Back to Zero" → `/insights/aisearch-global-client-zero` · "Get your own visibility audit" → `/services/aeo-audit`
- CSS transition animations via `data-dash` / `data-w` / `data-h` / `data-left` attributes, triggered via double `requestAnimationFrame`
- Live at: https://aisearch.global/insights/client-zero-visibility-dashboard

### Client Zero Article
`insights/aisearch-global-client-zero.html` — updated this session.

Added **timing gap timeline + headline callout** between the green training-cutoff context box and the 36/30/41 score grid:
- Visual timeline: AI training datasets bar (teal) · AI's blind spot (orange hatched) · 22 May 2026 launch marker (teal dot) · 20 Jun 2026 graded dot
- Callout: *"This is the headline: the AI models were trained before we existed — yet even with zero training-data history, all three engines still found and rated the brand. That is a strong starting position, not a weak one."*
- Live at: https://aisearch.global/insights/aisearch-global-client-zero

Both changes committed and pushed to `main`. Cloudflare Pages deployed.

### insights/index.html
Already had Client Zero as the featured top article with both the article and dashboard links. JSON-LD schema already included. No changes needed this session.

### sitemap.xml
Already had both `aisearch-global-client-zero` and `client-zero-visibility-dashboard` entries. No changes needed this session.

---

## Architecture — Calculator end-to-end flow

```
User fills form → clicks "Check My AI Visibility"
  ↓
assets/js/calculator.js: trackAndRun() → runAssessment()
  ↓
fetch POST → https://aeo-score.aisearchglobal.workers.dev
  ↓
Cloudflare Worker (cloudflare/aeo-score-worker.js):
  - scores 20 signals (17 AEO + 3 Princeton GEO)
  - ctx.waitUntil(logToSheets()) → aisearchglobal@gmail.com Google Sheet
  - returns JSON
  ↓
calculator.js: renderResult() + renderGeo() → results displayed
```

### Key files
| File | Purpose |
|---|---|
| `aeo-score-calculator.html` | Page HTML + CSS only — zero inline JS |
| `assets/js/calculator.js` | ALL calculator JS — single source of truth |
| `cloudflare/aeo-score-worker.js` | Scoring + Sheets logging — deploy via wrangler |
| `cloudflare/google-sheets-logger.gs` | Apps Script webhook for Google Sheets |
| `assets/js/main.js` | Shared header/footer injector — LOCKED |
| `_headers` | Cloudflare Pages HTTP headers inc. CSP |
| `_redirects` | Directory rewrites + legacy URL redirects |
| `llms.txt` / `llms-full.txt` | AI crawler reference files |

### Worker deploy (NOT triggered by git push — must run manually)
```bash
cd "C:\Users\dasku\OneDrive\Documents\Aisearch.global\cloudflare"
npx wrangler deploy aeo-score-worker.js
```

### CSP (live via `_headers`)
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://static.cloudflareinsights.com https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; img-src 'self' data: https://www.googletagmanager.com https://www.google-analytics.com; connect-src 'self' https://aeo-score.aisearchglobal.workers.dev https://formspree.io https://www.google-analytics.com https://www.googletagmanager.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self' https://formspree.io; upgrade-insecure-requests;
```
Note: `https://cdnjs.cloudflare.com` added for Bootstrap Icons CDN used by the dashboard.

---

## Infrastructure

- **Cloudflare Pages** project: `aisearch-global`
  - Account ID: `bcb5adf500b41a01598037b13bc5d4d2`
  - Zone ID: `f3136e5207849686f6b1a258140d253d`
  - Auto-deploy: push to `main`
- **Scoring Worker:** `aeo-score.aisearchglobal.workers.dev`
- **Google Sheets logging:** aisearchglobal@gmail.com Drive, sheet "AEO Score Scans" — 90-day auto-delete via Apps Script trigger
- **Naming conventions:** Service = "AI Visibility Audit" · Calculator = "AEO Score Calculator"
- **Cloudflare dashboard CSP rule:** DELETED (2026-06-21). CSP comes from `_headers` only.

---

## Page pattern

Every standard site page = own embedded `<style>` block + `main.js` injects header/footer into empty `<header></header>` / `<footer></footer>` tags.

Dashboard (`client-zero-visibility-dashboard.html`) is a **standalone exception** — no `main.js`, own logo/header, own full-page layout.

Required CSS per standard page: `.container{max-width:1120px}`, sticky header, nav, nav-toggle, cta-link, `@media(max-width:720px)` mobile breakpoint.

---

## Still TODO

1. **`insights/aeo-geo-results-timeline.html`** — exists locally, content-complete, not committed, not in sitemap or insights index. Held deliberately — needs a push decision.
2. **Layout consistency audit** — "the layout is all over the place." Each page has its own `<style>` block. Not done.
3. **Fresh screenshots** post-deploy with hard-refreshed browser.
