# AISearch Global — Project Instructions

---

## ⛔ PROTECTED — DO NOT MODIFY WITHOUT EXPLICIT INSTRUCTION FROM VIV

The following are locked. Do not change, replace, move, or rewrite any of these without Viv explicitly asking you to:

| Asset | Locked value |
|---|---|
| Nav / header logo | `/assets/images/logos/header-logo.svg` — **dark backgrounds only**. This SVG has white/light text on a transparent background. It is INVISIBLE on white or light backgrounds. Never use it in documents, PDFs, or any white-background context. |
| Print / PDF logo | `/assets/images/logos/aisearch-logo-primary-dark.png` — **white/light backgrounds only** (documents, PDFs, print). The only logo used in `@media print`. |
| Favicon | `/favicon.svg` — do not change the file or the `<link>` tags pointing to it |
| Brand colours | Teal `#0ABAB5` / `#0ABFBC` · Dark bg `#0D0E10` · Text `#E3E8EE` — never alter |
| Footer social links | URLs in `assets/js/main.js` — do not add, remove, or change any social handle or URL |
| GA property ID | `G-XBZMSCBXBZ` — never alter or remove from any page |
| `main.js` header HTML | The `var H = ...` block — do not restructure without explicit approval |

**Why these are locked:** A previous AI session changed the nav logo from the SVG image to plain text, breaking the brand. These rules exist to prevent that class of error from recurring.

**If you think a change to a locked item is needed:** stop, describe what you want to change and why, and wait for Viv to confirm before touching it.

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
