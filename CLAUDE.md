# AISearch Global — Project Instructions

---

## ⛔ STOP — READ THIS BEFORE TOUCHING ANYTHING

These rules are absolute. No exceptions. No "I thought it would be better". No silent changes.

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
