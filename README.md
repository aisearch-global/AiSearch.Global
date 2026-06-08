# AISearch Global Website

Static HTML/CSS site for `https://aisearch.global`. Deployed via Cloudflare Pages on git push.

## Site structure

```
index.html                        # Home
about/index.html                  # About
faq.html                          # FAQ (51 questions)
privacy/index.html                # Privacy policy
terms/index.html                  # Terms

services/
  aeo-audit.html                  # AI Visibility Audit (flagship)
  content-restructuring.html      # Content Restructuring
  schema-implementation.html      # Schema Implementation
  ai-brand-presence.html          # AI Brand Presence
  structured-content-systems.html # Structured Content Systems
  ai-visibility-strategy.html     # AI Visibility Strategy

insights/
  index.html                      # Insights index
  what-is-aeo-answer-engine-optimisation.html   # 24 May 2026
  how-ai-decides-which-businesses-to-recommend.html  # 30 May 2026
  aeo-glossary.html               # AEO Help Guide  — 3 Jun 2026
  aeo-traction-stack.html         # AEO Traction Stack framework — 7 Jun 2026

aeo-calculator.html               # AISearch Global AEO Calculator (free tool, 13 signals, instant score)
ai-visibility-assessment.html     # Client intake / assessment form

assets/css/styles.css
assets/js/main.js
assets/images/

llms.txt                          # AI crawler context
robots.txt
sitemap.xml
```

## Deployment

Hosted on **Cloudflare Pages** (`aisearch-global` project). Deploys automatically on push to `main`.

AEO Calculator scoring runs on **Cloudflare Workers**: `aeo-score.aisearchglobal.workers.dev`
- Local dev: `cd cloudflare && wrangler dev` (serves on `localhost:8787`)
- Architecture: see [`cloudflare/ARCHITECTURE.md`](cloudflare/ARCHITECTURE.md)

```
cloudflare/
  aeo-score-worker.js   # Worker source (ES Module, export default fetch)
  wrangler.toml         # Worker deployment config
  ARCHITECTURE.md       # Request flow diagram and signal reference
```

## Schema implemented

- `Organization` — home page
- `ProfessionalService` — home page
- `WebSite` — home page
- `FAQPage` — home page and FAQ page
- `Article` — insights articles
- `BreadcrumbList` — insights articles

## Analytics

Google Analytics 4: `G-XBZMSCBXBZ`

## Key external accounts

- **Google Search Console:** submitted, verified
- **Formspree:** lead form `xqejbpqj`
- **Postiz:** social scheduling (9 channels)

## Local private files

`local-private/` is gitignored. Contains:
- `tmp-live-snapshots/` — snapshots of live pages (last synced: 8 Jun 2026)
- `brand-style-guide-local.html`
- `social-media-plan-*.html`
- `credentials.md`
