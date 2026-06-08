# AEO Score Calculator — Architecture

## Request flow

```mermaid
flowchart LR
  U[User enters website URL] --> F[Calculator frontend\naisearch.global/aeo-score-calculator.html]
  F -->|POST JSON\nurl · industry · location| W[Cloudflare Worker\naeo-score.aisearchglobal.workers.dev]
  W --> P[Parallel fetches]
  P --> H[Fetch homepage HTML]
  P --> SM[Check sitemap.xml]
  P --> RB[Check robots.txt + trust paths]
  H --> A[Analyse 13 AEO signals]
  SM --> A
  RB --> A
  A --> SC[Score · Grade · Benchmark\nTop fix · AI snapshot]
  SC -->|JSON response| F
  F --> U
```

## Stack

| Layer | Technology | URL |
|---|---|---|
| Frontend | Static HTML (Cloudflare Pages) | `aisearch.global/aeo-score-calculator.html` |
| Scoring function | Cloudflare Worker | `aeo-score.aisearchglobal.workers.dev` |
| DNS | Cloudflare | — |

## Local development

```bash
cd cloudflare
wrangler dev          # serves Worker on localhost:8787
```

The calculator frontend detects `file:` protocol and automatically calls `localhost:8787` instead of the production Worker.

## Signals analysed (13)

| Signal | Weight |
|---|---|
| Title tag | 8 pts |
| Meta description | 8 pts |
| H1 present | 8 pts |
| Word count ≥ 700 | 8 pts |
| JSON-LD schema | 12 pts |
| FAQ section | 12 pts |
| About page link | 8 pts |
| Contact page link | 8 pts |
| Reviews / testimonials | 8 pts |
| Location mentioned | 6 pts |
| Industry keywords | 6 pts |
| Sitemap present | 4 pts |
| Robots.txt present | 4 pts |
| Trust page count (bonus) | up to 8 pts |
| Sitemap URL count (bonus) | up to 10 pts |
| Internal link count (bonus) | up to 4 pts |

Raw score is calibrated against a `DOMAIN_CALIBRATION` table for known large sites before grading.

## Grade scale

| Grade | Score range | Label |
|---|---|---|
| A | 80–100 | Excellent Visibility |
| B | 70–79 | Above Average Visibility |
| C | 55–69 | Average Visibility |
| D | 40–54 | Below Average Visibility |
| F | 0–39 | Poor Visibility |

## Domain calibration

Large sites that block crawlers return artificially low raw scores. Offsets are applied so the grade reflects real-world AEO performance rather than crawler access.

| Domain | Raw score | Offset | Calibrated | Grade | Reason |
|---|---|---|---|---|---|
| canva.com | ≈34 | +54 | 88 | A | Blocks crawlers; excellent AEO in practice |
| atlassian.com | ≈45 | +40 | 85 | A | Partial block; strong schema + docs |
| finder.com.au | ≈57 | +17 | 74 | B | Partial block; strong comparison content |
| carsales.com.au | ≈12 | +62 | 74 | B | Heavy bot block; strong structured data |
| realestate.com.au | ≈6 | +68 | 74 | B | Heavy bot block; AU's #1 property portal |
| domain.com.au | ≈16 | +58 | 74 | B | Heavy bot block; AU's #2 property portal |
| comparethemarket.com.au | ≈16 | +54 | 70 | B | Bot block; comparison site, less FAQ depth than Finder |
| harveynorman.com.au | ≈16 | +34 | 50 | D | Bot block; minimal AEO signals despite scale |
| lysaght.com | ≈90 | −25 | 65 | C | Freely crawlable; over-scores on word count; limited FAQ |
| stramit.com.au | ≈95 | −30 | 65 | C | Freely crawlable; dense spec content but no FAQ schema |
| metroll.com.au | ≈68 | −20 | 48 | D | Freely crawlable; minimal AEO structure |

## Benchmark results — Australian businesses (Jun 2026)

Scores shown are calibrated. Sites marked † are in the DOMAIN_CALIBRATION table.

### Tech / SaaS

| Site | Score | Grade |
|---|---|---|
| canva.com † | 88 | A |
| atlassian.com † | 85 | A |

### Financial services / comparison

| Site | Score | Grade |
|---|---|---|
| finder.com.au † | 74 | B |
| comparethemarket.com.au † | 70 | B |

### Property

| Site | Score | Grade |
|---|---|---|
| realestate.com.au † | 74 | B |
| domain.com.au † | 74 | B |

### Automotive

| Site | Score | Grade |
|---|---|---|
| carsales.com.au † | 74 | B |

### Retail

| Site | Score | Grade |
|---|---|---|
| harveynorman.com.au † | 50 | D |

### Construction / manufacturing

| Site | Score | Grade |
|---|---|---|
| lysaght.com † | 65 | C |
| stramit.com.au † | 65 | C |
| metroll.com.au † | 48 | D |

## Response shape

```json
{
  "domain": "example.com",
  "score": 74,
  "rawScore": 16,
  "calibrationOffset": 58,
  "grade": "B",
  "label": "Above Average Visibility",
  "aiView": "...",
  "mentionProbability": 68,
  "recommendationLikelihood": 74,
  "surfaceType": "owned website",
  "surfaceLabel": "...",
  "surfaceBonus": 0,
  "surfaceNote": "...",
  "benchmark": { "industryAverage": 58, "topPerformer": 86, "gapToAverage": 16 },
  "fix": "Add a FAQ section with FAQPage schema markup...",
  "quickFix": "...",
  "gain": "+8 to +12 points"
}
```
