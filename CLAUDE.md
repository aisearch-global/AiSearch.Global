# AISearch Global — Project Instructions

---

## ⛔ STOP — READ THIS BEFORE TOUCHING ANYTHING

These rules are absolute. No exceptions. No "I thought it would be better". No silent changes.

### NEVER USE .html EXTENSIONS IN INTERNAL LINKS OR SCHEMA URLS

**Rule:** Every internal link (`href`) and every URL in JSON-LD schema must use the clean URL — no `.html` extension, ever.

| ❌ Wrong | ✅ Correct |
|---|---|
| `href="/aeo-score-calculator.html"` | `href="/aeo-score-calculator"` |
| `href="/services/aeo-audit.html"` | `href="/services/aeo-audit"` |
| `href="/insights/aeo-traction-stack.html"` | `href="/insights/aeo-traction-stack"` |
| `"url": "https://aisearch.global/services/aeo-audit.html"` | `"url": "https://aisearch.global/services/aeo-audit"` |

**Why:** Cloudflare Pages strips `.html` and redirects to the clean URL (301). If the `_redirects` file also has a 200 rewrite rule mapping that clean URL back to `.html`, a redirect loop results (`ERR_TOO_MANY_REDIRECTS`). Even without a loop, `.html` links add an unnecessary redirect on every click. Clean URLs are what Cloudflare serves natively — always link to those.

**Applies to:** `href` attributes, `src` attributes for pages, all `url`, `item`, and `@id` fields in JSON-LD schema, canonical tags, OG tags, sitemap entries.

### LOCKED ASSETS — NEVER MODIFY WITHOUT VIV EXPLICITLY SAYING SO IN THIS CONVERSATION

**LOGOS**

- **Nav/header (dark backgrounds only):**
  `/assets/images/logos/header-logo.svg`
  ⚠️ WHITE TEXT ON TRANSPARENT BACKGROUND. COMPLETELY INVISIBLE ON WHITE OR LIGHT SURFACES. Only ever used inside the dark site header. Never in documents, PDFs, slides, or any white-background context. Never replaced with text.

- **Print/PDF/documents (white/light backgrounds only):**
  `/assets/images/logos/aisearch-logo-primary-dark.png`
  The ONLY logo for any `@media print`, PDF download, or white-background document. No other logo file is acceptable here.

**FAVICON**
```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="shortcut icon" href="/favicon.svg">
```
Both lines. Exact paths. On every page. Do not change the file, the paths, or the tags.

**GOOGLE ANALYTICS**
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XBZMSCBXBZ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-XBZMSCBXBZ');</script>
```
Every page must have this. Property ID `G-XBZMSCBXBZ` is fixed. Never alter or omit.

**BRAND COLOURS — NEVER ALTER**
| Token | Value |
|---|---|
| Teal (primary accent) | `#0ABAB5` / `#0ABFBC` |
| Dark background | `#0D0E10` |
| Body text | `#E3E8EE` |
| Muted text | `#95A0AD` |

**`assets/js/main.js` — DO NOT RESTRUCTURE**
The shared header/footer injector. Do not change:
- The `var H = ...` header HTML block (logo img tag, nav links, CTA link)
- The footer social media URLs
- The GA event tracking logic

### WHAT TO DO IF YOU THINK A LOCKED ITEM NEEDS CHANGING

Stop. Do not make the change. Tell Viv what you want to change and why. Wait for explicit confirmation in this conversation before proceeding. "I assumed" is not acceptable.

### WHY THESE RULES EXIST

A previous AI session silently replaced the header logo SVG with plain text, breaking the brand across every page of the live website. These rules exist because silent "improvements" to brand assets cause real damage.

---

## About

**AISearch Global** — `www.aisearch.global`
**Founder:** Viveka (Viv) — vivi.mdas@gmail.com
**Location:** Sydney, Australia
**Stage:** Pre-revenue. Launched May 2026.

AEO (Answer Engine Optimisation) consultancy. Helps Australian businesses get found, cited, and recommended in AI-generated answers — ChatGPT, Gemini, Perplexity, Google AI Overviews, Claude.

**Positioning:** Pure-play AEO specialist. Every Australian competitor is a generalist agency with AEO bolted on. AISearch Global is the focused specialist.

---

## Current Priority

**ONE job: land paying client #1.**

Sequence:
1. Foundation & proof ✅
2. AI Visibility Audit offer live (~$1,500–$2,500 AUD) ✅
3. First paying client ← WE ARE HERE
4. Convert to case study
5. Use case study to justify SRSC digital-marketing role move

---

## Offers

All six services are detailed at `/services/` (the services hub page).

- **AI Visibility Audit** — $1,500–$2,500 AUD (productised, primary offer — always start here)
- **Content Restructuring** — from $1,500 AUD
- **Schema Implementation** — $750–$1,500 AUD
- **AI Brand Presence** — $1,200–$1,800 AUD
- **Structured Content Systems** — $1,500–$2,500 AUD
- **AI Visibility Strategy** — $2,000–$3,500 AUD

---

## Proprietary Framework

**AEO Traction Stack** — 4 layers:
1. Entity Clarity
2. Schema Markup
3. Answer-Format Content
4. Citation Consistency

Layers 1 & 2 account for ~80% of improvement.

---

## Website (Cloudflare Pages, static HTML)

- Home, 6 × Services, Insights (4 articles), About, FAQ (51 Qs), Privacy, Terms
- AEO Score Calculator: `/aeo-score-calculator.html` — 13-signal automated live URL analyzer, instant grade A–F, no email required
- AI Visibility Audit: `/#contact`
- Schema: Organization + ProfessionalService + FAQPage JSON-LD, sitemap.xml, robots.txt, llms.txt
- Deployed via Cloudflare Pages on git push to main

---

## Published Insights (live)

1. *What Is AEO* — 24 May 2026
2. *How AI Decides Which Businesses to Recommend* — 30 May 2026
3. *The AEO Traction Stack* — 7 Jun 2026

---

## Content System

- **Tool:** Postiz (batch + schedule, API connected)
- **Rotation:** Week 1 Guide → Week 2 Insight → Week 3 Framework → Week 4 Case Study
- **LinkedIn:** 1 substantial post/week → links to full article
- **Facebook:** 1 short post/week → auto-distributes to Instagram + Threads
- **Other channels:** YouTube, TikTok, Pinterest, Google (live for entity signals, not fed weekly yet)
- **Workflow:** Batch-write all four in one weekend, schedule via Postiz, repeat monthly

---

## Capacity

AISearch work happens **weekends and evenings only.** Zero paid-acquisition budget. Content-led authority building.

---

## Credentials

~50 certifications: AI, generative AI, AI ethics, psychology, mental health, human-centred AI, leadership.

First client: Dr Sid Mohandas (brother) — AEO-compliant website built for testimonial + case study.

---

## SEO / AEO Audit Protocol — MANDATORY

**Every time Viv asks for an audit, SEO check, AEO check, or "what needs updating":**

1. **Search first.** Before auditing the site, run a web search for what's changed in AEO/SEO since the last audit. Search for: "AEO best practices 2026", "Google schema markup updates", "AI search ranking signals", "answer engine optimisation latest". Check docs.anthropic.com, Google Search Central, schema.org changelog, and AEO-specific sources (Frase.io, Moz, Search Engine Journal).

2. **Then audit the site** against BOTH:
   - The current site state (read actual files)
   - The latest standards found in step 1

3. **Report gaps** in priority order: Critical (broken/missing) → High (ranking impact) → Medium (best practice) → Low (nice-to-have).

4. **Always include a "What's changed since last audit" section** — new schema types, new AI crawler signals, Google algorithm updates, new AEO signals AI platforms have started weighting.

**Why:** AISearch Global is an AEO agency. Its own site must model best practice. If the site is behind on any AEO/SEO signal, that undermines the business. The audit must reflect current standards, not just known standards.

---

## How to Work With Viv

**Do:**
- Direct answers, no fluff
- Clear headings, short paragraphs, bullet points
- Frameworks and checklists over walls of text
- ONE recommendation when overwhelmed — not a list of options
- Real numbers and evidence only

**Don't:**
- Vague or ambiguous advice
- Add options when direction is needed
- Use unnecessary jargon

**If stuck or uncertain:** narrow it down. Give ONE clear next step.

---

## Brand Assets — Logos & Favicon

### Favicon
- **File:** `/favicon.svg` (root)
- **Fallback PNG:** `/assets/images/logos/favicon-transparent.png`
- **Always use both lines in `<head>`:**
  ```html
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="shortcut icon" href="/favicon.svg">
  ```

### Logo Variants — Use the Right One

| Variant | File | Use when |
|---|---|---|
| **Header / Nav (dark bg)** | `/assets/images/logos/header-logo.svg` | Site header, dark backgrounds, emails on dark |
| **Print / PDF (white bg)** | `/assets/images/logos/aisearch-logo-primary-dark.png` | Any print output, PDF downloads, white-background documents |
| **Light colour (dark bg documents)** | `/assets/images/logos/aisearch-logo-primary-light.png` | Presentations, slide decks, documents with dark backgrounds |
| **Inverse black** | `/assets/images/logos/aisearch-logo-inverse-black.png` | Single-colour black print |
| **Inverse transparent** | `/assets/images/logos/aisearch-logo-inverse-transparent.png` | Overlays, watermarks, transparent-bg contexts |

### Rules
- **Web nav header** → always `header-logo.svg`
- **`@media print` / PDF output** → always `aisearch-logo-primary-dark.png`
- **Never use the nav SVG on a white/light background** — it won't be visible
- **OG/social image:** `/assets/images/aisearch_social_graphic_plumber.png` (used for all `og:image` and `twitter:image` tags)

---

## Tech Stack

- Cloudflare Pages (static HTML/CSS, git-deployed from main branch)
- Cloudflare Workers (AEO Score Calculator scoring function — `aeo-score.aisearchglobal.workers.dev`)
- Postiz (social scheduling)
- Blogger (Mindful Machines Journal — separate project)
- GitHub (version control)

---

## Site File Map — URL → File Path

Every live URL and its source file. Edit the correct file.

| Live URL | File path |
|---|---|
| `https://aisearch.global/` | `index.html` |
| `https://aisearch.global/services/` | `services/index.html` |
| `https://aisearch.global/services/aeo-audit` | `services/aeo-audit.html` |
| `https://aisearch.global/services/content-restructuring` | `services/content-restructuring.html` |
| `https://aisearch.global/services/ai-visibility-strategy` | `services/ai-visibility-strategy.html` |
| `https://aisearch.global/services/ai-brand-presence` | `services/ai-brand-presence.html` |
| `https://aisearch.global/services/schema-implementation` | `services/schema-implementation.html` |
| `https://aisearch.global/services/structured-content-systems` | `services/structured-content-systems.html` |
| `https://aisearch.global/insights/` | `insights/index.html` |
| `https://aisearch.global/insights/what-is-aeo-answer-engine-optimisation` | `insights/what-is-aeo-answer-engine-optimisation.html` |
| `https://aisearch.global/insights/how-ai-decides-which-businesses-to-recommend` | `insights/how-ai-decides-which-businesses-to-recommend.html` |
| `https://aisearch.global/insights/aeo-traction-stack` | `insights/aeo-traction-stack.html` |
| `https://aisearch.global/about/` | `about/index.html` |
| `https://aisearch.global/faq.html` | `faq.html` |
| `https://aisearch.global/aeo-score-calculator.html` | `aeo-score-calculator.html` |
| `https://aisearch.global/privacy/` | `privacy/index.html` |
| `https://aisearch.global/terms/` | `terms/index.html` |

**Not-live files** (do not edit or deploy): `privacy.html`, `terms.html` (root-level legacy copies), `local-private/` (all files), `content-archive/` (all files), `brand-assets/social-graphics/` (all files).

---

## How `main.js` Works — CRITICAL

Every page has empty `<header></header>` and `<footer></footer>` tags in the HTML. **This is intentional.** They are not broken.

`assets/js/main.js` runs on page load and injects the full nav and footer HTML into those empty tags. This is how every page gets the same header logo, nav links, CTA button, and footer without copy-pasting HTML into every file.

**Rules:**
- Never write content directly into `<header>` or `<footer>` tags in any page file — `main.js` will overwrite it.
- Never restructure or rewrite the `var H = ...` block or footer block in `main.js` — those are LOCKED (see top of this file).
- If the nav or footer looks wrong, the fix is in `assets/js/main.js`, not in individual page files.
- The `<script defer src="/assets/js/main.js"></script>` tag must be in `<head>` of every page.

---

## AEO Score Calculator — Worker Deploys Separately

The scoring logic lives in `cloudflare/aeo-score-worker.js` and runs as a **Cloudflare Worker** at `aeo-score.aisearchglobal.workers.dev`.

**Git push to main does NOT deploy the Worker.** The Worker must be deployed separately:
```
npx wrangler deploy cloudflare/aeo-score-worker.js
```

The page `aeo-score-calculator.html` is deployed via git push like everything else. The Worker is a separate service. Editing `cloudflare/aeo-score-worker.js` and pushing will NOT update the live scoring logic until `wrangler deploy` is run.

---

## Standard `<head>` Template — Required on Every Page

Every new page must include all of the following, in this order:

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PAGE TITLE | AISearch Global</title>
  <meta name="description" content="PAGE DESCRIPTION">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="author" content="AISearch Global">
  <link rel="canonical" href="https://aisearch.global/PAGE-URL">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="shortcut icon" href="/favicon.svg">
  <link rel="apple-touch-icon" href="/assets/images/aisearch_social_graphic_plumber.png">
  <link rel="stylesheet" href="/assets/css/styles.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <script defer src="/assets/js/main.js"></script>

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="AISearch Global">
  <meta property="og:locale" content="en_AU">
  <meta property="og:url" content="https://aisearch.global/PAGE-URL">
  <meta property="og:title" content="PAGE TITLE | AISearch Global">
  <meta property="og:description" content="PAGE DESCRIPTION">
  <meta property="og:image" content="https://aisearch.global/assets/images/aisearch_social_graphic_plumber.png">
  <meta property="og:image:alt" content="AISearch Global social graphic showing a plumber search query and warning that your business is not here">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="PAGE TITLE | AISearch Global">
  <meta name="twitter:description" content="PAGE DESCRIPTION">
  <meta name="twitter:image" content="https://aisearch.global/assets/images/aisearch_social_graphic_plumber.png">
  <meta name="twitter:image:alt" content="AISearch Global social graphic showing a plumber search query and warning that your business is not here">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XBZMSCBXBZ"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XBZMSCBXBZ');
  </script>
</head>
```

The OG image and twitter:image are always `aisearch_social_graphic_plumber.png` unless Viv explicitly specifies otherwise.

---

## Formspree — Contact Form

**Form ID:** `xqejbpqj`
**Endpoint:** `https://formspree.io/f/xqejbpqj`

Used in `index.html` (home `#contact` section) and `about/index.html`. Any new contact or lead form must use this same endpoint — do NOT create a new Formspree form. Creating a new form would silently drop submissions from the existing form.

---

## Fixes Applied — Regression Protection

These bugs were found and fixed. Do not revert them.

| What was fixed | File(s) | Before (broken) | After (correct) |
|---|---|---|---|
| Nav logo was plain text | `assets/js/main.js` | `<span>AISearch Global</span>` text in header | `<img src="/assets/images/logos/header-logo.svg" ...>` |
| Signal 9 label wrong | `aeo-score-calculator.html` | Incorrect label text | Correct signal 9 label |
| GA missing | `faq.html`, all 4 insights pages | No GA snippet | GA snippet `G-XBZMSCBXBZ` added |
| Print logo wrong | `insights/aeo-traction-stack.html` | Used header SVG (invisible on white) in `@media print` | Uses `aisearch-logo-primary-dark.png` |

If you see any of these files without the correct content, the state has regressed — restore from git history or reapply the fix.

---

## `_redirects` — Adding New Pages

`_redirects` (root) controls Cloudflare Pages URL rewriting. **Every page with a clean URL needs an entry here.**

Format: `SOURCE DESTINATION STATUS_CODE`

Current rules:
```
/services  /services/index.html  200
/services/ /services/index.html  200
/insights  /insights/index.html  200
/insights/ /insights/index.html  200
/privacy   /privacy/index.html   200
/privacy/  /privacy/index.html   200
/terms     /terms/index.html     200
/terms/    /terms/index.html     200
/aeo-calculator.html /aeo-score-calculator.html 301
/aeo-calculator      /aeo-score-calculator.html 301
/insights/aeo-glossary.html /insights/ 301
```

When adding a new page at a directory URL (e.g. `/new-page/index.html`), add both:
```
/new-page  /new-page/index.html  200
/new-page/ /new-page/index.html  200
```
Without these entries, `/new-page/` will return a 404.

---

## Social Media Profiles

All social links are injected by `main.js` footer — to update a URL, change it in `main.js` only (not in individual pages).

| Platform | URL | Handle |
|---|---|---|
| LinkedIn | `https://www.linkedin.com/company/ai-search-global/` | `ai-search-global` |
| Facebook | `https://www.facebook.com/aisearch.global` | `aisearch.global` |
| Instagram | `https://www.instagram.com/aisearch.global/` | `@aisearch.global` |
| Threads | `https://www.threads.net/@aisearch.global` | `@aisearch.global` |
| X (Twitter) | `https://x.com/aisearch_global` | `@aisearch_global` (underscore, not dot) |
| YouTube | `https://www.youtube.com/@aisearch.global` | `@aisearch.global` |
| Pinterest | `https://au.pinterest.com/aisearch_global/` | `aisearch_global` (underscore) |
| TikTok | `https://www.tiktok.com/@aisearch.global` | `@aisearch.global` |
| Google Maps | Long URL in `main.js` | Listed as AISearch Global, Currans Hill Sydney |

Note the handle inconsistency: X and Pinterest use underscore (`aisearch_global`); all others use dot (`aisearch.global`).

**Contact email:** `hello@aisearch.global` — the public business address used on the website, in schema markup, and on all social profiles.

---

## GA Event Tracking — `data-track` and `data-track-form`

`main.js` wires up two types of GA4 event tracking automatically — no extra JS needed, just add the attribute.

**Click events** (`data-track`):
```html
<a href="..." data-track="your_label">Click me</a>
```
Fires: `gtag('event', 'click', { event_category: 'engagement', event_label: 'your_label' })`

**Form submit events** (`data-track-form`):
```html
<form ... data-track-form="audit_request">...</form>
```
Fires: `gtag('event', 'generate_lead', { event_category: 'conversion', event_label: 'audit_request' })`

Existing labels in use (don't duplicate): `audit_request`, `about_hero_cta`, `about_calculator_cta`, `about_cta_click`, `email_click`, `calculator-cta`, `audit_services_hero`, `calculator_services_hero`, `article-cta-traction-stack`, and per-service CTAs.

---

## Known Anomalies — Do Not "Fix"

These are intentional or pre-existing states that look wrong but should not be changed without Viv's direction.

**`insights/index.html` uses relative asset paths**
Lines 14–15 load CSS and JS as `../assets/css/styles.css` and `../assets/js/main.js` instead of the absolute `/assets/...` pattern used everywhere else. The page works correctly — Cloudflare resolves it. Do not change to absolute paths without testing; the page predates the current pattern and has not caused issues.

**Pinterest domain verification only on 2 pages**
`<meta name="p:domain_verify" content="c18ed316c67e3a4c44602269f5997354">` appears only in `index.html` and `about/index.html`. This is intentional — Pinterest verification only requires one page. Do not add it to other pages.

**`faq.html` and `terms/index.html` have no JSON-LD schema**
17 of 19 live pages have `<script type="application/ld+json">` blocks. `faq.html` and `terms/index.html` do not. This is an existing gap, not a regression.
