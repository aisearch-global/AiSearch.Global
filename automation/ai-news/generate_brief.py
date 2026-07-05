#!/usr/bin/env python3
"""
AI News Automation — Step 2: turn today's candidate stories into a published
brief.

Reads data/pending/<date>.json (written by fetch_pipeline.py) and produces:
  - news/<date>.html            a real, indexable archived page (no ticker-only JS)
  - news/index.html             regenerated list of recent briefs + ticker markup
  - news/latest.json            small JSON file the ticker's client-side JS polls
  - data/pending/<date>.brief.json   the generated copy, kept for the LinkedIn step

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

SITE_URL = "https://aisearch.global"
MAX_INDEX_DAYS = 60      # how many days of briefs stay listed on /news
MAX_TICKER_ITEMS = 15

CATEGORY_LABELS = {
    "ai_news": "AI News",
    "ai_law_regulation": "AI Law & Regulation",
    "human_ai_research": "Human-AI Research",
    "aeo_relevance": "AEO Relevance",
    "australia_focus": "Australia",
}


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
  <link rel="stylesheet" href="/assets/css/styles.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <script defer src="/assets/js/main.js"></script>

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

  <script type="application/ld+json">{json.dumps(news_article_schema)}</script>
</head>
<body>
  <main class="container news-brief-page" style="padding-top: 6rem; padding-bottom: 4rem;">
    <p><a href="/news">&larr; All AI news briefs</a></p>
    <h1>AI News Brief — {human_date}</h1>
    <p class="news-brief-intro">Curated daily by AISearch Global. Every story links back to its original source — we don't republish, we round up.</p>
    {body}
  </main>
</body>
</html>
"""


def render_index(entries: list[dict]) -> str:
    """entries: list of {date, human_date, headline_count} newest first."""
    items = "\n".join(
        f'      <li><a href="/news/{e["date"]}">{e["human_date"]}</a> — {e["headline_count"]} stories</li>'
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
  <link rel="stylesheet" href="/assets/css/styles.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <script defer src="/assets/js/main.js"></script>

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
  <main class="container news-index-page" style="padding-top: 6rem; padding-bottom: 4rem;">
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
