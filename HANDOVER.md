# Handover Brief — AISearch Global Website

**Project:** `C:\Users\dasku\OneDrive\Documents\Aisearch.global` (git repo, Cloudflare Pages static site)
**Last updated:** 2026-06-22, dashboard card click fix
**Live site:** https://aisearch.global

---

## Critical constraint — NEVER touch without explicit confirmation in chat

- `insights/aisearch-global-client-zero.html`
- `insights/client-zero-visibility-dashboard.html`
- Any `client-zero-*` named file
- `assets/js/main.js` — the `var H = ...` header block, footer social URLs, GA event logic
- See full locked-asset rules in repo-root `CLAUDE.md` (logos, GA ID, favicon, brand colours, Formspree form ID) — read it before any further changes.

---

## Latest session addendum (2026-06-22, dashboard card click fix)

Dashboard cockpit cards were not expanding on click on the live site. Root cause: identical pattern to the calculator CSP incident.

**Root cause:** `_headers` CSP `script-src` did not include `https://cdnjs.cloudflare.com`. The dashboard loads Chart.js from that CDN. When CSP blocks it, `Chart` is undefined when the inline script runs — `Chart.defaults.color = ...` throws immediately, crashing the entire `<script>` block. The IIFE at the bottom of that block (which wires up `click` listeners on every `.cockpit-card`) never executes, so cards silently do nothing on click.

**Fix:** Added `https://cdnjs.cloudflare.com` to `script-src` in `_headers`. No other files changed.

This must be committed and pushed to take effect (Cloudflare Pages serves `_headers` only from the deployed build).

---

## Previous session addendum (2026-06-21, congruence/explainer/sitemap-flow session) — pushed by Viv

More work on `insights/client-zero-visibility-dashboard.html` and `sitemap.xml` (Viv gave explicit in-chat instruction to edit the locked dashboard file):

1. **Cockpit ↔ expanded-panel numeric congruence audit** — Checked all 10 cockpit-card summary stats against their expanded detail panels for mismatches ("otherwise incongruent and can decay trust"). Found and fixed 2:
   - `panel-recognition`: cockpit blurb said "12/100 avg," dial/true average of the 3 sub-scores (12, 5, 12) is 10. Fixed blurb to "10/100 avg."
   - `panel-crawler`: cockpit ("5 AI bots") and expanded Key Signal stat ("5"/"AI platforms crawling") agreed with each other but not with the actual itemized crawler list, which has 6 distinct AI-bot rows. Fixed both to "6."
   - Other 8 pairs checked, already consistent, no changes.
2. **Second "HubSpot" leak found + fixed** — `dash-subtitle` line (~348) still said "Tools: HubSpot AEO Grader + ..." — renamed to "AI Brand Perception Audit," matching the project-wide rule to never expose that third-party tool name publicly. Confirmed via grep: zero "HubSpot" matches remain in the file.
3. **Explainer paragraphs added** to 4 expanded panels that jumped straight into data without explaining the visual encoding: `panel-platform` (what the gauge dial + meta tags mean), `panel-sentiment` (defines all 4 sentiment dimensions + clarifies Polarization is a risk score where *lower* is better, fixing a contradiction in the old copy), `panel-crawler` (colour-coded AI vs. traditional crawler rows), `panel-performance` (defines TTFB/LCP/Cache Rate). Other 6 panels already had adequate framing, left as-is.
4. **Sitemap flow decision** — Removed `/insights/client-zero-visibility-dashboard` from `sitemap.xml`. Agreed with Viv: the dashboard has no narrative framing on its own and shouldn't rank as an independent search destination — the case-study article (`aisearch-global-client-zero`) is the canonical AEO/SEO entry point. Dashboard stays reachable via direct URL or the article's CTA button; `robots` meta on the dashboard page left as `index,follow` (not noindex), since it's fine for it to be discovered via the article's link, just not promoted as its own priority page.

No locked assets (header/footer/main.js/GA/favicon/brand colours) touched. Not yet committed.

---

## Previous session addendum (2026-06-21, dashboard styling fix session) — pushed by Viv

Dashboard styling fixes applied to `insights/client-zero-visibility-dashboard.html` (Viv gave explicit in-chat instruction to edit this locked file):

1. **Cockpit ↔ expanded-panel congruence** — The 3 AI-platform gauge cards (`#panel-platform`) used a red→amber→green rainbow gradient on the SVG arc, which clashed with the rest of the page's single-accent-colour language and duplicated the grade-badge's good/bad semantics. Replaced with a faded→solid gradient in each platform's own brand colour (ChatGPT green, Perplexity teal, Gemini purple) — now matches the needle, score text, and every other platform-coloured element on the page.
2. **Blurry "Which AI Bots Are Indexing the Site" charts** — Root cause: all Chart.js canvases (SOV donuts, crawler donut, AEO score line) are created once at page load, while every panel except the first is `display:none`. Chart.js measures a 0×0 container at creation time, so canvases render at the wrong internal resolution and look blurry/undersized once their panel opens. Fixed by dispatching a `resize` event (via `requestAnimationFrame`) inside `openPanel()` every time a card is expanded — forces Chart.js to recompute against the now-visible container. Fixes all chart panels, not just the crawler one.
3. **Priority Actions (P1/P2/P3) card alignment** — Cards are now `display:flex;flex-direction:column` with the paragraph set to `flex:1`, so the service badge + impact line anchor to the bottom of every card regardless of paragraph length. Lightly evened up the three paragraphs' length/cadence (~38–42 words each, same two-sentence structure) so the row reads as one consistent set rather than uneven blocks.

No locked assets (header/footer/main.js/GA/favicon/brand colours) touched. Not yet committed — see git status below.

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

## Push scope decision — 2026-06-22: push everything except the Timeline

Viv confirmed: push everything currently outstanding **except** `insights/aeo-geo-results-timeline.html`, which is held back for next week.

Verified actual `git status` (not just this doc's prior notes) shows these modified/untracked files:

**Push now:**
- `HANDOVER.md`, `_headers`, `_redirects`, `sitemap.xml`, `assets/js/main.js`
- `about/index.html`, `aeo-score-calculator.html`, `faq.html`, `index.html`, `privacy/index.html`, `terms/index.html`
- `insights/index.html`, `insights/aeo-traction-stack.html`, `insights/how-ai-decides-which-businesses-to-recommend.html`, `insights/princeton-geo-paper-explained.html`, `insights/what-is-aeo-answer-engine-optimisation.html`
- `services/index.html`, `services/aeo-audit.html`, `services/ai-brand-presence.html`, `services/ai-visibility-strategy.html`, `services/content-restructuring.html`, `services/schema-implementation.html`, `services/structured-content-systems.html`
- `insights/client-zero-visibility-dashboard.html` (new/untracked)

**Hold back (next week):**
- `insights/aeo-geo-results-timeline.html` — untracked, content-complete, deliberately not pushed this round.

**Also untracked, not a site file — leave out of the commit:**
- `AISEARCH GLOBAL WEBSITE AUDIT 21-06-26.docx` — a working doc, not part of the deployed site.

**`assets/js/main.js` checked against the locked-asset rules before clearing it for push:** the diff showed as binary at first glance (a line-ending change made git treat it as a binary diff), but forcing a text diff confirmed the content is byte-for-byte identical except line endings — header HTML block, footer social URLs, GA tracking logic, and Bootstrap Icons classes are all untouched. Safe to include.

**`.git/index.lock`:** still present (0-byte, timestamp 2026-06-21 13:34 UTC) and this sandboxed session still can't delete it. However, the repo's last real commit (`48f030f`, "Fix .html extensions in nav/footer links + bump main.js cache version") landed at 23:51:17 +1000 — *after* the lock's timestamp — so it isn't actually blocking commits made directly on Viv's machine. Treat it as a harmless stale OneDrive-sync artifact, not a live blocker. If a local git client ever does refuse with "unable to create '.git/index.lock': File exists," delete that one 0-byte file and retry.

**Still open, not part of this push:**
- `insights/aisearch-global-client-zero.html` exists on disk but doesn't show as changed in this `git status` — it's already committed as-is. It still needs the "Why This Matters for You" section rewrite (drafted, not applied) per the project memory — that's separate follow-up work, not blocking this push.

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
