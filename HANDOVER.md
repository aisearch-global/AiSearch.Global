# Handover Brief — AISearch Global Website

**Project:** `C:\Users\dasku\OneDrive\Documents\Aisearch.global` (git repo, Cloudflare Pages static site)
**Last updated:** 2026-06-21, end of session
**Live site:** https://aisearch.global

---

## Critical constraint — NEVER touch without explicit confirmation in chat

- `insights/aisearch-global-client-zero.html`
- `insights/client-zero-visibility-dashboard.html`
- Any `client-zero-*` named file
- `assets/js/main.js` — the `var H = ...` header block, footer social URLs, GA event logic
- See full locked-asset rules in repo-root `CLAUDE.md` (logos, GA ID, favicon, brand colours, Formspree form ID) — read it before any further changes.

---

## What was done this session (all pushed live)

### 1. Social media icons restored + permanently locked
A parallel session had replaced Bootstrap Icons with inline SVGs in `assets/js/main.js`. Reverted all 8 icons back to `<i class="bi bi-...">` classes. Added permanent lock rule to `CLAUDE.md`: "Social icons MUST remain Bootstrap Icons classes — NEVER replace with inline SVGs."

### 2. Phone number format fixed site-wide
`main.js` footer NAP was showing `02 4019 2419` (local format). Changed to `+61 2 4019 2419` (international). `tel:` hrefs and schema were already correct. Applied `+61` format consistently across `index.html` and `about/index.html` contact sections.

### 3. "Prefer direct contact?" line added to index.html + about/index.html
Both pages now show phone + email inline in the contact/CTA section with `tel:` and `mailto:` links styled in accent colour.

### 4. AEO Score Calculator — fully fixed, never-fail architecture

Multiple layers fixed in sequence:

- **Stray `h` character** in `<head>` of `aeo-score-calculator.html` — removed (caused HTML parse corruption).
- **`disabled` attribute** on submit button — removed. Was silently blocking all clicks.
- **Consent validation UX** — replaced dead-end form-hiding with inline error + scroll-to + 5s auto-dismiss.
- **`resetToForm()` bug** — button stayed `disabled` after first scan. Fixed.
- **`showError()` bug** — button now re-enabled on error.
- **ROOT CAUSE — CSP blocking all inline JS:** A `Content-Security-Policy` header set in the **Cloudflare dashboard** had no `'unsafe-inline'` for `script-src`. This silently prevented ALL `<script>` blocks from executing. `trackAndRun()` was in the HTML source but the browser never ran it. Button appeared normal, did nothing on click. Confirmed via `typeof trackAndRun === 'undefined'` in browser console.

**Permanent fix:** All calculator JS extracted from the HTML into **`/assets/js/calculator.js`** — an external file served from `'self'`, always CSP-safe regardless of any dashboard policy. The HTML page now has zero inline JS. One `<script src="/assets/js/calculator.js">` tag at the bottom of `<body>`.

**`_headers` file** created and committed with correct CSP (was never previously committed — Cloudflare Pages never saw it).

**⚠️ One action still required:** The Cloudflare dashboard CSP rule must be deleted — see section below.

### 5. Google Sheets logging added to Worker
Every scan now logs to Google Sheets (aisearchglobal@gmail.com Drive, sheet "AEO Score Scans"):
- `cloudflare/aeo-score-worker.js` — `logToSheets(env, payload)` + `ctx.waitUntil()` (fire-and-forget, never blocks response)
- `cloudflare/google-sheets-logger.gs` — Apps Script Web App deployed at aisearchglobal@gmail.com
- `SHEETS_WEBHOOK_URL` Cloudflare Worker secret set
- Worker redeployed
- Columns: Timestamp / URL / Domain / Industry / Location / AEO Score / Grade / Marketing Consent / Delete After (90 days)
- Daily trigger at 2am UTC auto-deletes expired rows

### 6. Privacy policy + consent text updated
- `privacy/index.html` — research and tool-integrity/misuse-protection added as stated purposes. Date updated to 21 June 2026.
- Calculator consent checkbox — "…storing this scan for 90 days for research and tool integrity purposes."

---

## ✅ RESOLVED — Cloudflare Dashboard CSP (2026-06-21)

The Cloudflare Transform Rule that was injecting a second `Content-Security-Policy` header has been deleted. CSP is now set by a single source (`_headers` in the repo). The Worker URL `https://aeo-score.aisearchglobal.workers.dev` is confirmed present in `connect-src`. Inline `onclick` handlers were also removed from the HTML and replaced with event listeners in `calculator.js` so button clicks are CSP-safe regardless of any future dashboard policy.

### The correct CSP (already live via `_headers`)
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; img-src 'self' data: https://www.googletagmanager.com https://www.google-analytics.com; connect-src 'self' https://aeo-score.aisearchglobal.workers.dev https://formspree.io https://www.google-analytics.com https://www.googletagmanager.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self' https://formspree.io; upgrade-insecure-requests;
```

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

### Worker deploy (NOT triggered by git push — must run manually)
```bash
cd "C:\Users\dasku\OneDrive\Documents\Aisearch.global\cloudflare"
npx wrangler deploy aeo-score-worker.js
```

---

## Still uncommitted locally — Viv's WIP, DO NOT commit/push without asking

- `_redirects` — adds `/insights/client-zero-visibility-dashboard` redirect
- `sitemap.xml` — adds two Client Zero URLs
- `insights/index.html` — adds Client Zero as position-1 listing
- `insights/client-zero-visibility-dashboard.html` — new file, untracked
- `insights/aeo-geo-results-timeline.html` — content-complete article, not yet in sitemap or insights index

**Confirm with Viv before pushing any of these.**

---

## Still TODO

1. **Layout consistency audit** — "the layout is all over the place." Each page has its own `<style>` block. Not done.
2. **Client Zero publish decision** — files exist locally only.
3. **`insights/aeo-geo-results-timeline.html`** — not wired into sitemap or insights index.
4. **Fresh visual screenshots** post-deploy with hard-refreshed browser.

---

## Reference: page pattern + locked assets

Every live page = own embedded `<style>` block + `main.js` injects header/footer into empty `<header></header>`/`<footer></footer>` tags. Required CSS per page: `.container{max-width:1120px}`, sticky header, nav, nav-toggle, cta-link, `@media(max-width:720px)` mobile breakpoint.

Full locked-asset rules, file map, social URLs, Formspree ID: see `CLAUDE.md` — read before any changes, never modify locked items without Viv's explicit confirmation.
