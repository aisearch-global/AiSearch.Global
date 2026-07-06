#!/usr/bin/env python3
"""
AI News Automation — Step 2: turn today's candidate stories into a published
brief.

Reads data/pending/<date>.json (written by fetch_pipeline.py) and produces:
  - news/<date>.html            a real, indexable archived page (no ticker-only JS)
  - news/index.html             regenerated list of recent briefs + ticker markup
  - news/latest.json            small JSON file the ticker's client-side JS polls
  - data/pending/<date>.brief.json   the generated copy, kept for the LinkedIn step
  - sitemap.xml (repo root)     updated in place: /news hub entry refreshed and a
    <url> entry added for every dated brief page (clean URLs, no .html)

Summarisation: if ANTHROPIC_API_KEY is set, each story gets a ~200-word brief
written by Claude in AISearch Global's voice. If it isn't set, falls back to a
naive truncation of the source's own summary — good enough to keep the
pipeline runnable end-to-end before that key is wired up, but the AI-written
version is what should ship in production.

Usage:
    python generate_brief.py               # today (UTC date)
    python generate_brief.py --date 2026-07-05
"""
from __future__ import annotations

import argparse
import json
import os
import re
import textwrap
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent  # automation/ai-news -> repo root
DATA_DIR = ROOT / "data"
PENDING_DIR = DATA_DIR / "pending"
NEWS_DIR = REPO_ROOT / "news"
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"

SITE_URL = "https://aisearch.global"

# Cache-busting versions for shared assets. These MUST match the ?v= values the
# committed site pages use (check index.html). Cloudflare caches the unversioned
# URLs, so a page emitted without the current ?v= loads a stale main.js/styles.css
# — this is how the news pages ended up with the pre-News nav (2026-07-07).
STYLES_CSS_HREF = "/assets/css/styles.css?v=4"
MAIN_JS_SRC = "/assets/js/main.js?v=news-nav1"
MAX_INDEX_DAYS = 60      # how many days of briefs stay listed on /news
MAX_TICKER_ITEMS = 15

CATEGORY_LABELS = {
    "ai_news": "AI News",
    "ai_law_regulation": "AI Law & Regulation",
    "human_ai_research": "Human-AI Research",
    "aeo_relevance": "AEO Relevance",
    "australia_focus": "Australia",
}

# Every other page on the site carries its own copy of this block in <head>
# (see e.g. insights/what-is-aeo-answer-engine-optimisation.html) rather than
# relying solely on /assets/css/styles.css — that external sheet is only a thin
# supplementary layer. Without this block, and without real <header></header>/
# <footer></footer> tags for main.js to inject the nav/footer into, a page
# renders as unstyled default HTML even though the CSS link is present. This
# was missed in the first build — pages were live but looked broken.
SHARED_STYLE = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--tiffany:#0ABFBC;--tiffany-dim:rgba(10,191,188,0.10);--silver:#C0C0C0;--silver-dim:#888888;--charcoal:#2B2B2B;--charcoal-mid:#1E1E1E;--black:#0D0D0D;--white:#FFFFFF;--font-head:'Space Grotesk',system-ui,sans-serif;--font-body:'DM Sans',system-ui,sans-serif}
html{background:var(--black);color:var(--white);font-family:var(--font-body);font-size:16px;line-height:1.75;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}a:hover{color:var(--tiffany)}
.container{max-width:1120px;margin:0 auto;padding:0 1rem}
header{position:sticky;top:0;z-index:100;background:rgba(13,14,16,.92);backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,255,255,.12)}
.nav{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1rem 0}
.brand img{height:34px;width:auto;max-width:260px;display:block}
.nav-toggle{display:none;background:none;border:1px solid rgba(255,255,255,.12);color:var(--white);padding:.45rem .65rem;border-radius:0}
.nav-links{display:flex;gap:1rem;list-style:none;padding:0;margin:0}
.nav-links a{text-decoration:none;color:var(--silver);font-family:var(--font-body);font-weight:500;font-size:1rem;line-height:1}
.nav-links a:hover,.nav-links a:focus{color:var(--tiffany)}
.cta-link{padding:.55rem .9rem;border:1px solid var(--tiffany);border-radius:0;color:var(--tiffany)!important}
main{max-width:720px;margin:0 auto;padding:4rem 2rem 6rem}
h1{font-family:var(--font-head);font-size:clamp(1.9rem,4vw,2.75rem);font-weight:500;line-height:1.2;color:var(--white);margin-bottom:1.5rem;letter-spacing:-.015em}
h2{font-family:var(--font-head);font-size:1.35rem;font-weight:500;color:var(--tiffany);margin:2.75rem 0 .9rem}
p{color:var(--silver);margin-bottom:1.35rem;font-size:.975rem;line-height:1.75}
footer{border-top:1px solid var(--charcoal);padding:1.2rem 0;color:var(--silver-dim);font-size:.9rem}
.footer-links{display:flex;gap:1rem;flex-wrap:wrap;margin-top:.5rem}
.footer-links a{font-size:12px;color:var(--silver-dim);text-decoration:none}
.footer-links a:hover{color:var(--tiffany)}
.social-links{display:flex;gap:.75rem;flex-wrap:wrap;margin-top:.75rem}
.social-links a{font-size:1.1rem;color:var(--silver-dim);text-decoration:none}
.social-links a:hover{color:var(--tiffany)}
@media(max-width:720px){.nav-toggle{display:block}.nav-links{display:none;position:absolute;left:1rem;right:1rem;top:4.2rem;flex-direction:column;background:#111317;border:1px solid rgba(255,255,255,.12);padding:.8rem;border-radius:0}.nav-links.open{display:flex}}
@media(max-width:640px){main{padding:2.5rem 1.25rem 4rem}}
.back-link{display:inline-flex;align-items:center;gap:.4rem;font-size:12px;color:var(--silver-dim);margin-bottom:2.25rem}
.news-brief-intro{font-size:1.05rem;color:var(--silver);margin-bottom:2.5rem;padding-bottom:2rem;border-bottom:1px solid var(--charcoal)}
.news-story{margin:0 0 2.25rem;padding-bottom:2rem;border-bottom:1px solid var(--charcoal)}
.news-story-meta{color:var(--tiffany);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.6rem;display:block}
.news-story h2{margin-top:0}
.ai-news-ticker{display:flex;align-items:center;gap:.75rem;overflow:hidden;white-space:nowrap;background:var(--charcoal-mid);border:1px solid var(--charcoal);border-radius:0;padding:.85rem 1.1rem;margin:1.75rem 0 2.5rem}
.ai-news-ticker-label{color:var(--tiffany);font-weight:600;flex-shrink:0;font-size:.85rem;text-transform:uppercase;letter-spacing:.05em}
.ai-news-ticker-track{overflow:hidden;text-overflow:ellipsis;font-size:.9rem}
.ai-news-ticker-track a{color:var(--silver)}
.ai-news-ticker-track a:hover{color:var(--tiffany)}
.news-index-list{list-style:none;padding:0;margin-top:1.5rem}
.news-index-list li{border-bottom:1px solid var(--charcoal);font-size:.95rem}
.news-index-list li a{display:block;padding:.9rem 0;color:var(--white);font-weight:500}
.news-index-list li a:hover{color:var(--tiffany)}
.news-index-list li a .story-count{color:var(--silver);font-weight:400}
.news-index-list li a:hover .story-count{color:var(--tiffany)}
"""


def log(msg: str) -> None:
    print(f"[generate_brief] {msg}", flush=True)


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:80]


def naive_summary(raw: str, max_words: int = 200) -> str:
    words = raw.split()
    if len(words) <= max_words:
        return raw.strip()
    return " ".join(words[:max_words]).rstrip(",.;: ") + "..."


def summarise_with_claude(story: dict) -> tuple[str, str]:
    """Returns (headline, ~200 word brief). Falls back to naive summary on any error."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return story["title"], naive_summary(story["summary_raw"])

    try:
        import anthropic  # imported lazily so the script still runs without the package

        client = anthropic.Anthropic(api_key=api_key)
        prompt = textwrap.dedent(f"""
            You are writing one entry in AISearch Global's daily AI news brief.
            AISearch Global is a Sydney-based Answer Engine Optimisation (AEO) and
            Generative Engine Optimisation (GEO) consultancy. The voice is direct,
            plain-English, no hype, no filler — written for a busy Australian small
            business owner who has five minutes.

            Source: {story['source']}
            Original headline: {story['title']}
            Original summary: {story['summary_raw']}

            Write:
            1. A clear headline (rewrite only if the original is unclear or clickbait-y,
               otherwise keep it close to the original).
            2. A summary of approximately 200 words, in plain English, that explains
               what happened and why it matters — flag the AEO/GEO angle explicitly if
               there is one. Do not invent facts not in the source summary.

            Reply in this exact format, nothing else:
            HEADLINE: <headline>
            SUMMARY: <summary>
        """).strip()

        resp = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        headline_match = re.search(r"HEADLINE:\s*(.+)", text)
        summary_match = re.search(r"SUMMARY:\s*(.+)", text, re.DOTALL)
        headline = headline_match.group(1).strip() if headline_match else story["title"]
        summary = summary_match.group(1).strip() if summary_match else naive_summary(story["summary_raw"])
        return headline, summary
    except Exception as exc:  # noqa: BLE001
        log(f"  Claude summarisation failed ({exc}), falling back to naive summary")
        return story["title"], naive_summary(story["summary_raw"])


def render_story_block(headline: str, summary: str, story: dict) -> str:
    cats = ", ".join(CATEGORY_LABELS.get(c, c) for c in story["categories"])
    return f"""
      <article class="news-story">
        <p class="news-story-meta">{cats} &middot; Source: {story['source']}</p>
        <h2>{headline}</h2>
        <p>{summary}</p>
        <p><a href="{story['link']}" target="_blank" rel="noopener">Read the original at {story['source']} &rarr;</a></p>
      </article>
    """.strip()


def render_page(date_str: str, human_date: str, story_blocks: list[str]) -> str:
    body = "\n".join(story_blocks) if story_blocks else "<p>No qualifying stories today.</p>"
    canonical = f"{SITE_URL}/news/{date_str}"
    news_article_schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": f"AI News Brief — {human_date}",
        "datePublished": f"{date_str}T00:00:00+10:00",
        "author": {"@type": "Organization", "name": "AISearch Global", "url": SITE_URL},
        "publisher": {"@type": "Organization", "name": "AISearch Global", "url": SITE_URL},
        "mainEntityOfPage": canonical,
        "url": canonical,
    }
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI News Brief — {human_date} | AISearch Global</title>
  <meta name="description" content="Daily AI news brief for {human_date}: AI news, AI law and regulation, human-AI research, and AEO-relevant developments, with an Australian focus.">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="author" content="AISearch Global">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="shortcut icon" href="/favicon.svg">
  <link rel="apple-touch-icon" href="/assets/images/aisearch_social_graphic_plumber.png">
  <style>{SHARED_STYLE}</style>

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="AISearch Global">
  <meta property="og:locale" content="en_AU">
  <meta property="og:url" content="{canonical}">
  <meta property="og:title" content="AI News Brief — {human_date} | AISearch Global">
  <meta property="og:description" content="Daily AI news brief for {human_date}, curated by AISearch Global.">
  <meta property="og:image" content="{SITE_URL}/assets/images/aisearch_social_graphic_plumber.png">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="AI News Brief — {human_date} | AISearch Global">
  <meta name="twitter:description" content="Daily AI news brief for {human_date}, curated by AISearch Global.">
  <meta name="twitter:image" content="{SITE_URL}/assets/images/aisearch_social_graphic_plumber.png">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XBZMSCBXBZ"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-XBZMSCBXBZ');
  </script>
  <script defer src="/assets/js/consent.js"></script>
  <link rel="stylesheet" href="{STYLES_CSS_HREF}">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <script defer src="{MAIN_JS_SRC}"></script>

  <script type="application/ld+json">{json.dumps(news_article_schema)}</script>
</head>
<body>
<header></header>
<main class="news-brief-page">
  <a href="/news" class="back-link">&larr; All AI news briefs</a>
  <h1>AI News Brief — {human_date}</h1>
  <p class="news-brief-intro">Curated daily by AISearch Global. Every story links back to its original source — we don't republish, we round up.</p>
  {body}
</main>
<footer></footer>
</body>
</html>
"""


def render_index(entries: list[dict]) -> str:
    """entries: list of {date, human_date, headline_count} newest first."""
    items = "\n".join(
        f'      <li><a href="/news/{e["date"]}">{e["human_date"]} '
        f'<span class="story-count">&mdash; {e["headline_count"]} stories</span></a></li>'
        for e in entries
    )
    canonical = f"{SITE_URL}/news"
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI News | AISearch Global</title>
  <meta name="description" content="Daily curated AI news: AI news, AI law and regulation, human-AI research, and AEO-relevant developments, with an Australian focus.">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="author" content="AISearch Global">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="shortcut icon" href="/favicon.svg">
  <link rel="apple-touch-icon" href="/assets/images/aisearch_social_graphic_plumber.png">
  <style>{SHARED_STYLE}</style>
  <link rel="stylesheet" href="{STYLES_CSS_HREF}">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <script defer src="{MAIN_JS_SRC}"></script>

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="AISearch Global">
  <meta property="og:locale" content="en_AU">
  <meta property="og:url" content="{canonical}">
  <meta property="og:title" content="AI News | AISearch Global">
  <meta property="og:description" content="Daily curated AI news, AEO-relevant developments, and an Australian focus.">
  <meta property="og:image" content="{SITE_URL}/assets/images/aisearch_social_graphic_plumber.png">

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XBZMSCBXBZ"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-XBZMSCBXBZ');
  </script>
  <script defer src="/assets/js/consent.js"></script>
</head>
<body>
<header></header>
<main class="news-index-page">
  <h1>AI News</h1>
  <p>A running ticker of the latest headlines AISearch Global is tracking, plus the full daily brief archive below.</p>

  <div id="ai-news-ticker" class="ai-news-ticker" aria-live="polite">
    <span class="ai-news-ticker-label">Latest:</span>
    <div class="ai-news-ticker-track"><!-- populated by /news/latest.json --></div>
  </div>

  <h2>Recent briefs</h2>
  <ul class="news-index-list">
{items}
  </ul>
</main>
<footer></footer>

  <script>
    (function () {{
      var track = document.querySelector('.ai-news-ticker-track');
      if (!track) return;
      fetch('/news/latest.json', {{ cache: 'no-store' }})
        .then(function (r) {{ return r.ok ? r.json() : []; }})
        .then(function (items) {{
          track.innerHTML = items.map(function (item) {{
            return '<a href="' + item.link + '" target="_blank" rel="noopener">' + item.headline + '</a>';
          }}).join(' &nbsp;&middot;&nbsp; ');
        }})
        .catch(function () {{ /* fail quietly — ticker just stays empty, page still works */ }});
    }})();
  </script>
</body>
</html>
"""


def sitemap_url_block(loc: str, lastmod: str, changefreq: str, priority: str) -> str:
    return (
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        f"  </url>\n"
    )


def update_sitemap(date_str: str) -> None:
    """Keep sitemap.xml in sync with the news section: refresh the /news hub
    entry's lastmod and add a <url> entry for every dated brief page on disk.

    Per Viv's direction (News-nav brief, 2026-07-06) every dated page is listed
    individually and stays in the sitemap permanently. Entries use clean URLs
    (no .html) — see CLAUDE.md. Edits the existing file in place with string
    surgery rather than an XML parser so the hand-maintained entries and their
    formatting are left untouched.
    """
    if not SITEMAP_PATH.exists():
        log(f"sitemap.xml not found at {SITEMAP_PATH} — skipping sitemap update")
        return

    xml = SITEMAP_PATH.read_text(encoding="utf-8")
    if "</urlset>" not in xml:
        log("sitemap.xml has no closing </urlset> tag — skipping sitemap update")
        return

    hub_loc = f"{SITE_URL}/news"
    if f"<loc>{hub_loc}</loc>" in xml:
        xml = re.sub(
            rf"(<loc>{re.escape(hub_loc)}</loc>\s*<lastmod>)[^<]*(</lastmod>)",
            rf"\g<1>{date_str}\g<2>",
            xml,
        )
        log(f"sitemap.xml: refreshed /news lastmod to {date_str}")
    else:
        xml = xml.replace("</urlset>", sitemap_url_block(hub_loc, date_str, "daily", "0.8") + "</urlset>")
        log("sitemap.xml: added /news hub entry")

    added = 0
    for page in sorted(NEWS_DIR.glob("????-??-??.html")):
        page_date = page.stem
        loc = f"{SITE_URL}/news/{page_date}"
        if f"<loc>{loc}</loc>" in xml:
            continue
        # Dated briefs are write-once archives: lastmod is the brief's own date.
        xml = xml.replace("</urlset>", sitemap_url_block(loc, page_date, "monthly", "0.6") + "</urlset>")
        added += 1

    SITEMAP_PATH.write_text(xml, encoding="utf-8")
    log(f"sitemap.xml: {added} dated news entr{'y' if added == 1 else 'ies'} added")


def collect_index_entries() -> list[dict]:
    entries = []
    if NEWS_DIR.exists():
        for f in sorted(NEWS_DIR.glob("*.brief-meta.json"), reverse=True)[:MAX_INDEX_DAYS]:
            entries.append(json.loads(f.read_text(encoding="utf-8")))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD, defaults to today (UTC)")
    args = parser.parse_args()

    date_str = args.date or datetime.now(timezone.utc).date().isoformat()
    human_date = datetime.fromisoformat(date_str).strftime("%-d %B %Y")

    pending_path = PENDING_DIR / f"{date_str}.json"
    if not pending_path.exists():
        log(f"No pending file for {date_str} ({pending_path}) — nothing to do. "
            f"Run fetch_pipeline.py first.")
        return 0

    stories = json.loads(pending_path.read_text(encoding="utf-8"))
    if not stories:
        log(f"{date_str}: pending file is empty (no stories cleared the pipeline) — skipping publish.")
        return 0

    briefed = []
    for story in stories:
        headline, summary = summarise_with_claude(story)
        briefed.append({**story, "headline": headline, "summary": summary})

    NEWS_DIR.mkdir(parents=True, exist_ok=True)

    story_blocks = [render_story_block(s["headline"], s["summary"], s) for s in briefed]
    page_html = render_page(date_str, human_date, story_blocks)
    (NEWS_DIR / f"{date_str}.html").write_text(page_html, encoding="utf-8")
    log(f"Wrote news/{date_str}.html ({len(briefed)} stories)")

    # Small metadata file per day, used to rebuild the index without re-parsing every HTML file.
    meta = {"date": date_str, "human_date": human_date, "headline_count": len(briefed)}
    (NEWS_DIR / f"{date_str}.brief-meta.json").write_text(json.dumps(meta), encoding="utf-8")

    # Save the generated (headline, summary) copy for the LinkedIn draft step.
    (PENDING_DIR / f"{date_str}.brief.json").write_text(json.dumps(briefed, indent=2), encoding="utf-8")

    # Rebuild /news/index.html from all known days.
    entries = collect_index_entries()
    (NEWS_DIR / "index.html").write_text(render_index(entries), encoding="utf-8")
    log(f"Rebuilt news/index.html ({len(entries)} days listed)")

    # Rebuild the ticker feed from the most recent days' stories, newest first.
    ticker_items = []
    for e in entries[:5]:
        brief_path = PENDING_DIR / f"{e['date']}.brief.json"
        if not brief_path.exists():
            continue
        for s in json.loads(brief_path.read_text(encoding="utf-8")):
            ticker_items.append({"headline": s["headline"], "link": s["link"], "date": e["date"]})
    ticker_items = ticker_items[:MAX_TICKER_ITEMS]
    (NEWS_DIR / "latest.json").write_text(json.dumps(ticker_items, indent=2), encoding="utf-8")
    log(f"Wrote news/latest.json ({len(ticker_items)} items)")

    # Keep sitemap.xml in step with the pages just written.
    update_sitemap(date_str)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
