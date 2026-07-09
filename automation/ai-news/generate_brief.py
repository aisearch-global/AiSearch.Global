#!/usr/bin/env python3
"""
AI News Automation — Step 2: turn today's candidate stories into a published
brief, rendered as "The Answer Engine" — AISearch Global's daily newspaper
(eggshell paper, charcoal ink, Tiffany-teal accents; Playfair Display
nameplate/headlines, Source Serif 4 body, Space Grotesk kickers/bylines).
Design source of truth: the approved 8 July 2026 handoff templates
(edition-template.html / front-page-template.html).

Reads data/pending/<date>.json (written by fetch_pipeline.py) and produces:
  - news/<date>.html            a real, indexable archived edition (newspaper layout)
  - news/index.html             the front page: masthead, ticker, splash, editions list
  - news/latest.json            small JSON file of recent headlines (kept for compatibility;
                                the ticker itself is now server-rendered into index.html)
  - news/rss.xml                RSS 2.0 feed, one item per edition
  - data/pending/<date>.brief.json   the generated copy, kept for the LinkedIn step
  - sitemap.xml (repo root)     updated in place: /news hub entry refreshed and a
    <url> entry added for every dated brief page (clean URLs, no .html)

Summarisation: if ANTHROPIC_API_KEY is set, each story gets a ~200-word brief
written by Claude in AISearch Global's voice. If it isn't set, falls back to a
naive truncation of the source's own summary. If data/pending/<date>.brief.json
already exists (i.e. the edition was published before), its copy is reused
as-is so a re-render only restyles the page — archived editions never get
their text rewritten. Pass --resummarise to force fresh copy.

Usage:
    python generate_brief.py               # today (Australia/Sydney date)
    python generate_brief.py --date 2026-07-05
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path


def sydney_today() -> str:
    """Publication date: the Sydney calendar day, NOT UTC. The paper lands each
    Sydney morning (cron 20:00 UTC = 6am AEST next day); dating by UTC stamped
    every edition with yesterday's date, and a cron that fired after 00:00 UTC
    skipped a date entirely. Keep in sync with fetch_pipeline.sydney_today()."""
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("Australia/Sydney")
    except Exception:  # no tz database (bare Windows) — AEST, ignoring DST
        tz = timezone(timedelta(hours=10))
    return datetime.now(tz).date().isoformat()


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
MAIN_JS_SRC = "/assets/js/main.js?v=answer-engine2"
MAX_INDEX_DAYS = 60      # how many days of briefs stay listed on /news
MAX_TICKER_ITEMS = 15

# Publication identity (brand handles locked by Viv, design brief 8 July 2026).
# Display name is always "The Answer Engine" — never squished or hyphenated.
PUB_NAME = "The Answer Engine"
PUB_TAGLINE = "AI news, read the way machines read it. Sydney."
PUB_DOMAIN = "theanswerengine.news"
PUB_LINKEDIN = "https://www.linkedin.com/showcase/theanswerengine"
PUB_X_URL = "https://x.com/answerengine_au"
PUB_X_HANDLE = "@answerengine_au"

GOOGLE_FONTS_HREF = ("https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,500"
                     "&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400"
                     "&family=Space+Grotesk:wght@500;600;700&display=swap")

CATEGORY_LABELS = {
    "ai_news": "AI News",
    "ai_law_regulation": "AI Law & Regulation",
    "human_ai_research": "Human-AI Research",
    "aeo_relevance": "AEO Relevance",
    "australia_focus": "Australia",
}

# SHARED_STYLE — from the approved handoff templates, plus the standard site
# chrome rules (the injected header/footer carry no CSS of their own beyond
# what main.js adds — every page must style .nav/.nav-links itself, so a page
# without these rules renders the nav as an unstyled vertical list).
# The paper sits inside the site's dark chrome, which main.js injects into the
# empty <header></header>/<footer></footer> tags — do not put visible content
# in those tags.
# Palette: paper #F4F0E4 · ink #2B2B2B · tiffany #0ABFBC (rules/accents) ·
# deep teal #078F8B (link + kicker text — tiffany is too light for text on
# eggshell, deep teal keeps the same hue at readable contrast).
SHARED_STYLE = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --paper:#F4F0E4;
  --paper-deep:#ECE6D4;
  --ink:#2B2B2B;
  --ink-soft:#5C574B;
  --rule:#2B2B2B;
  --hairline:rgba(43,43,43,.22);
  --tiffany:#0ABFBC;
  --teal:#078F8B;        /* link + kicker text — WCAG-safe on eggshell */
  --teal-ink:#065F5C;    /* hover */
  --serif-display:'Playfair Display',Georgia,serif;
  --serif-body:'Source Serif 4',Georgia,serif;
  --sans:'Space Grotesk',system-ui,sans-serif;
}
html{background:#0D0D0D;font-size:16px;-webkit-font-smoothing:antialiased}
body{font-family:var(--serif-body);color:var(--ink);line-height:1.6}

/* ---- standard site chrome (header/footer injected by main.js) ----
   Same layout rules as every other page's <style> block; colour values are
   hard-coded because the newspaper :root doesn't define the site tokens. */
.container{max-width:1120px;margin:0 auto;padding:0 1rem}
header{position:sticky;top:0;z-index:100;background:rgba(13,14,16,.92);backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,255,255,.10);font-family:var(--sans);color:#E3E8EE}
.nav{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1rem 0}
.brand img{display:block;height:34px;width:auto;max-width:260px}
.nav-toggle{display:none;background:none;border:1px solid rgba(255,255,255,.10);color:#E3E8EE;padding:.45rem .65rem;border-radius:0}
.nav-links{display:flex;gap:1rem;list-style:none;padding:0;margin:0}
.nav-links a{text-decoration:none;color:#95A0AD;font-weight:500}
.nav-links a:hover,.nav-links a:focus{color:#0ABAB5}
.cta-link{padding:.55rem .9rem;border:1px solid #0ABAB5;border-radius:0;color:#0ABAB5!important}
footer{font-family:var(--sans);color:#E3E8EE}
.footer-links a{text-decoration:none;color:#95A0AD}.footer-links a:hover{color:#0ABAB5}
@media(max-width:720px){
  .nav-toggle{display:block}
  .nav-links{display:none;position:absolute;left:1rem;right:1rem;top:4.2rem;flex-direction:column;background:#111317;border:1px solid rgba(255,255,255,.10);padding:.8rem;border-radius:0}
  .nav-links.open{display:flex}
}

/* default link colours (in-paper) */
.paper a{color:var(--teal);text-decoration:none}
.paper a:hover{color:var(--teal-ink);text-decoration:underline;text-decoration-color:var(--tiffany);text-underline-offset:3px}

/* ---- the paper sheet (sits beneath the site's dark chrome) ---- */
.paper{max-width:1180px;margin:2.5rem auto 4rem;background:var(--paper);padding:clamp(1.4rem,4vw,3.5rem) clamp(1.2rem,4.5vw,4rem) clamp(2rem,4vw,3rem);box-shadow:0 30px 70px rgba(0,0,0,.55)}

/* ---- masthead ---- */
.masthead{text-align:center}
.masthead-top{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;font-family:var(--sans);font-size:.68rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-soft);border-bottom:1px solid var(--hairline);padding-bottom:.55rem}
.masthead-top a{color:var(--ink-soft)}
.masthead-top a:hover{color:var(--teal-ink)}
/* nameplate mirrors the brand lockup: THE / teal rule / ANSWER ENGINE / teal rule / subline */
.nameplate{margin:1.5rem 0 .6rem;text-transform:uppercase;color:var(--ink);line-height:1}
.nameplate a{color:var(--ink);display:inline-block}
.nameplate a:hover{color:var(--ink);text-decoration:none}
.np-the{display:block;font-family:var(--serif-display);font-weight:900;font-size:clamp(1.1rem,2.6vw,1.9rem);letter-spacing:.28em;padding-left:.28em;padding-bottom:.42em;margin-bottom:.5em;border-bottom:3px solid var(--tiffany)}
.np-main{display:block;font-family:var(--serif-display);font-weight:900;font-size:clamp(2.3rem,7.6vw,5.6rem);letter-spacing:.02em;line-height:1.04;padding-bottom:.14em;border-bottom:3px solid var(--tiffany)}
.np-sub{display:block;font-family:var(--sans);font-weight:600;font-size:clamp(.66rem,1.4vw,.92rem);letter-spacing:.42em;padding-left:.42em;color:var(--teal);margin-top:1em}
.tagline{font-family:var(--serif-body);font-style:italic;font-size:clamp(.9rem,1.6vw,1.05rem);color:var(--ink-soft);margin:.8rem 0 1.35rem}
.dateline{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;border-top:1px solid var(--rule);border-bottom:4px double var(--rule);padding:.5rem 0;font-family:var(--sans);font-size:.7rem;font-weight:600;letter-spacing:.13em;text-transform:uppercase;color:var(--ink)}
.dateline .dateline-date{font-weight:700}
.dateline a{color:var(--teal)}

/* ---- standfirst ---- */
.standfirst{text-align:center;font-style:italic;font-size:.95rem;color:var(--ink-soft);padding:1rem 1rem 1.1rem;border-bottom:1px solid var(--hairline)}

/* ==== STORY BLOCK — repeats per story; first (ranked) story uses .story--lead ==== */

/* lead story */
.story--lead{padding:2rem 0 1.8rem;border-bottom:3px double var(--rule)}
.story--lead .kicker{text-align:center}
.story--lead .headline{font-family:var(--serif-display);font-weight:900;font-size:clamp(1.7rem,4.6vw,3.3rem);line-height:1.08;letter-spacing:-.005em;text-align:center;margin:.55rem auto .7rem;max-width:22ch}
.story--lead .byline{text-align:center}
.story--lead .body{columns:2;column-gap:2.6rem;column-rule:1px solid var(--hairline);margin-top:1.3rem;text-align:justify;hyphens:auto}
.story--lead .body p{font-size:1.02rem;line-height:1.68;margin-bottom:1rem}
.story--lead .body p:first-of-type::first-letter{font-family:var(--serif-display);font-weight:700;font-size:3.6em;line-height:.82;float:left;padding:.06em .12em 0 0;color:var(--teal)}
.story--lead .read-link{display:block;text-align:center;margin-top:.9rem}

/* standard stories flow into newspaper columns */
.stories{columns:3;column-gap:2.6rem;column-rule:1px solid var(--hairline);padding-top:.4rem}
.story{break-inside:avoid;padding:1.35rem 0 1.5rem;border-bottom:1px solid var(--hairline)}
.story .headline{font-family:var(--serif-display);font-weight:700;font-size:1.32rem;line-height:1.18;margin:.4rem 0 .55rem}
.story .body p{font-size:.92rem;line-height:1.62;margin-bottom:.75rem;text-align:justify;hyphens:auto}

/* shared story parts */
.kicker{font-family:var(--sans);font-size:.66rem;font-weight:700;letter-spacing:.17em;text-transform:uppercase;color:var(--teal)}
.headline a{color:var(--ink)}
.headline a:hover{color:var(--teal-ink);text-decoration:none}
.byline{font-family:var(--sans);font-size:.66rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft);margin-bottom:.55rem}
.read-link{font-family:var(--sans);font-size:.74rem;font-weight:600;letter-spacing:.04em}
.read-link a{color:var(--teal)}

/* ---- ticker (front page) ---- */
.ticker{display:flex;align-items:center;gap:1rem;border-bottom:1px solid var(--rule);background:var(--paper-deep);margin-top:0;padding:.55rem .9rem;overflow:hidden}
.ticker-label{font-family:var(--sans);font-size:.66rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--teal);flex-shrink:0;border-right:1px solid var(--hairline);padding-right:1rem}
.ticker-viewport{overflow:hidden;flex:1;min-width:0}
.ticker-track{display:inline-block;white-space:nowrap;font-family:var(--serif-body);font-size:.88rem;animation:ticker-scroll 80s linear infinite;padding-left:0}
.ticker:hover .ticker-track{animation-play-state:paused}
.ticker-track a{color:var(--ink)}
.ticker-track a:hover{color:var(--teal-ink)}
.ticker-sep{color:var(--tiffany);padding:0 .8rem;font-weight:700}
@keyframes ticker-scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media (prefers-reduced-motion:reduce){.ticker-track{animation:none}.ticker-viewport{overflow-x:auto}}

/* ---- front-page splash + archive ---- */
.splash{padding:2rem 0 1.9rem;border-bottom:3px double var(--rule);text-align:center}
.splash .headline{font-family:var(--serif-display);font-weight:900;font-size:clamp(1.7rem,4.6vw,3.3rem);line-height:1.08;margin:.55rem auto .7rem;max-width:22ch}
.splash .teaser{font-size:1.05rem;line-height:1.65;max-width:56ch;margin:0 auto .9rem;color:var(--ink)}
.edition-link{font-family:var(--sans);font-size:.78rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase}
.archive{padding-top:1.8rem}
.section-flag{display:flex;align-items:center;gap:.9rem;font-family:var(--sans);font-size:.72rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--ink)}
.section-flag::before,.section-flag::after{content:"";flex:1;border-top:1px solid var(--rule)}
.archive-list{list-style:none;margin-top:.4rem}
.archive-list li{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;padding:1rem .2rem;border-bottom:1px solid var(--hairline)}
.archive-list .edition-date{font-family:var(--serif-display);font-weight:700;font-size:1.25rem}
.archive-list .edition-date a{color:var(--ink)}
.archive-list .edition-date a:hover{color:var(--teal-ink)}
.archive-list .edition-count{font-family:var(--sans);font-size:.7rem;font-weight:600;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-soft);white-space:nowrap}

/* ---- paper footer (colophon) ---- */
.colophon{margin-top:2.4rem;border-top:4px double var(--rule);padding-top:1.3rem;text-align:center}
.colophon .fleuron{color:var(--tiffany);font-size:1rem;letter-spacing:.6em;padding-left:.6em}
.colophon p{font-family:var(--sans);font-size:.7rem;font-weight:500;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-soft);margin-top:.7rem}
.colophon .colophon-links{display:flex;justify-content:center;gap:1.6rem;margin-top:.8rem;font-family:var(--sans);font-size:.7rem;font-weight:600;letter-spacing:.11em;text-transform:uppercase}
/* ---- responsive: collapse columns, keep masthead legible ---- */
@media (max-width:980px){.stories{columns:2}}
@media (max-width:660px){
  .stories{columns:1;column-rule:none}
  .story--lead .body{columns:1;column-rule:none}
  .paper{margin:1rem .6rem 2rem}
  .dateline{justify-content:center;text-align:center}
  .masthead-top{flex-wrap:wrap;justify-content:center;text-align:center}
}

/* ---- print: it actually prints like a newspaper ---- */
@media print{
  html{background:#fff}
  .paper{box-shadow:none;margin:0;max-width:none;background:#fff}
  header,footer,.ticker{display:none}
  .stories{columns:3}
  a{color:var(--ink)!important;text-decoration:none!important}
}
"""


def log(msg: str) -> None:
    print(f"[generate_brief] {msg}", flush=True)


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def clean_text(text: str) -> str:
    """Decode source HTML entities to real characters BEFORE they are esc()'d.

    Feeds serve entity-encoded copy (e.g. ``just&#160;don&#8217;t``). Passing that
    straight to esc() double-encodes the ampersand (``&amp;#160;``), so the browser
    prints the literal ``&#160;`` — the double-encoding bug that shipped on the
    2026-07-09 edition. Unescaping first turns ``&#160;`` into a real non-breaking
    space and ``&#8217;`` into a real apostrophe; esc() then re-encodes cleanly, so
    the round-trip is idempotent for plain text (Claude-written copy is unaffected).

    Apply this ONLY to free-text fields (headline, summary, source) — never to URLs.
    html.unescape() would corrupt a link like ``?a=1&copy=2`` into ``?a=1©=2``."""
    return html.unescape(str(text))


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:80]


# Date display helpers — built without strftime's %-d (GNU-only; explodes on
# Windows), so the generator runs identically on CI and a local machine.
def date_full(date_str: str) -> str:
    """'Sunday, 5 July 2026' — dateline + archive rows."""
    dt = datetime.fromisoformat(date_str)
    return f"{dt.strftime('%A')}, {dt.day} {dt.strftime('%B')} {dt.year}"


def date_short(date_str: str) -> str:
    """'5 July 2026' — titles, bylines, schema headlines."""
    dt = datetime.fromisoformat(date_str)
    return f"{dt.day} {dt.strftime('%B')} {dt.year}"


def date_day_month(date_str: str) -> str:
    """'5 July' — the splash's 'Read the 5 July edition' link."""
    dt = datetime.fromisoformat(date_str)
    return f"{dt.day} {dt.strftime('%B')}"


def story_count_label(n: int) -> str:
    return "1 story" if n == 1 else f"{n} stories"


def edition_number(date_str: str) -> int:
    """Ordinal of this edition (Vol. 1 · No. n): count of editions on disk up
    to and including this date. Stable across re-renders in any order."""
    dates = {p.stem for p in NEWS_DIR.glob("????-??-??.brief-meta.json")} if NEWS_DIR.exists() else set()
    dates.add(date_str)
    return sum(1 for d in dates if d <= date_str)


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


# --------------------------------------------------------------------------
# Shared page furniture
# --------------------------------------------------------------------------

def render_masthead(top_left: str, dateline_mid: str, edition_no: int) -> str:
    """The nameplate block both pages share. top_left is the left slot of the
    hairline row above the nameplate (back link on editions, domain on the
    front page); dateline_mid is the bold centre of the dateline row."""
    return f"""  <div class="masthead">
    <div class="masthead-top">
      {top_left}
      <span>Curated by AISearch Global &middot; Sydney</span>
      <a href="/news/rss.xml">Subscribe (RSS)</a>
    </div>
    <h1 class="nameplate"><a href="/news"><span class="np-the">The</span><span class="np-main">Answer Engine</span><span class="np-sub">AI News &middot; Sydney</span></a></h1>
    <p class="tagline">{PUB_TAGLINE}</p>
    <div class="dateline">
      <span>Vol.&nbsp;1 &middot; No.&nbsp;{edition_no}</span>
      <span class="dateline-date">{dateline_mid}</span>
      <span>Free &middot; Always</span>
    </div>
  </div>"""


def render_colophon() -> str:
    # NOT a <footer> element: main.js injects the dark site footer into the
    # FIRST <footer> in the DOM (document.querySelector("footer")), which would
    # wipe the colophon and drop the dark footer inside the paper. The only
    # <footer> tag on these pages must be the empty body-level one.
    return f"""  <div class="colophon">
    <div class="fleuron">&#10070;&#10070;&#10070;</div>
    <p>{PUB_NAME} is published daily by AISearch Global &middot; Sydney, Australia &middot; {PUB_DOMAIN}</p>
    <div class="colophon-links">
      <a href="{PUB_LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
      <a href="{PUB_X_URL}" target="_blank" rel="noopener">X {PUB_X_HANDLE}</a>
      <a href="/news/rss.xml">RSS</a>
    </div>
  </div>"""


def kicker_text(story: dict) -> str:
    return " &middot; ".join(esc(CATEGORY_LABELS.get(c, c)) for c in story["categories"])


def summary_body(summary: str, indent: str) -> str:
    """{{summary}} → .body. Splits on blank lines/newlines so multi-paragraph
    copy keeps its paragraphs; returns '' for an empty summary — the caller
    omits the .body div entirely (per the handoff README)."""
    paras = [p.strip() for p in re.split(r"\n+", summary or "") if p.strip()]
    if not paras:
        return ""
    inner = f"\n".join(f"{indent}  <p>{esc(clean_text(p))}</p>" for p in paras)
    return f"{indent}<div class=\"body\">\n{inner}\n{indent}</div>\n"


def render_story_block(story: dict, *, lead: bool, date_str: str) -> str:
    """STORY BLOCK — repeats per story; the first ranked story renders as the
    lead (.story--lead, h2, dated byline), the rest as .story (h3)."""
    link = esc(story["link"])  # URL — never clean_text()'d (would corrupt &-params)
    headline = esc(clean_text(story["headline"]))
    source = esc(clean_text(story["source"]))
    if lead:
        body = summary_body(story.get("summary", ""), "    ")
        return f"""  <article class="story--lead">
    <p class="kicker">{kicker_text(story)}</p>
    <h2 class="headline"><a href="{link}" target="_blank" rel="noopener">{headline}</a></h2>
    <p class="byline">Source: {source} &middot; {date_short(date_str)}</p>
{body}    <p class="read-link"><a href="{link}" target="_blank" rel="noopener">Read the original at {source}&nbsp;&rarr;</a></p>
  </article>"""
    body = summary_body(story.get("summary", ""), "      ")
    return f"""    <article class="story">
      <p class="kicker">{kicker_text(story)}</p>
      <h3 class="headline"><a href="{link}" target="_blank" rel="noopener">{headline}</a></h3>
      <p class="byline">Source: {source}</p>
{body}      <p class="read-link"><a href="{link}" target="_blank" rel="noopener">Read the original at {source}&nbsp;&rarr;</a></p>
    </article>"""


# --------------------------------------------------------------------------
# Daily edition — /news/<date>
# --------------------------------------------------------------------------

def render_page(date_str: str, human_date: str, stories: list[dict]) -> str:
    canonical = f"{SITE_URL}/news/{date_str}"
    short = date_short(date_str)
    title = f"{PUB_NAME} — {short} | AISearch Global"
    description = (f"{PUB_NAME}, {short}: today's AI news, AI law & regulation, human-AI research "
                   f"and AEO-relevant developments, curated daily by AISearch Global, Sydney.")
    news_article_schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": f"{PUB_NAME} — {short}",
        "alternativeHeadline": f"Daily AI news brief for {short}",
        "datePublished": f"{date_str}T00:00:00+10:00",
        "author": {"@type": "Organization", "name": "AISearch Global", "url": SITE_URL},
        "publisher": {"@type": "Organization", "name": "AISearch Global", "url": SITE_URL},
        "isPartOf": {"@type": "Periodical", "name": PUB_NAME, "url": f"{SITE_URL}/news"},
        "mainEntityOfPage": canonical,
        "url": canonical,
        "citation": [s["link"] for s in stories],
    }
    masthead = render_masthead(
        '<a href="/news">&larr; All editions</a>',
        f"{date_full(date_str)} &middot; {story_count_label(len(stories))}",
        edition_number(date_str),
    )
    if stories:
        lead_html = render_story_block(stories[0], lead=True, date_str=date_str)
        rest = "\n\n".join(render_story_block(s, lead=False, date_str=date_str) for s in stories[1:])
        stories_html = f"{lead_html}\n\n  <section class=\"stories\">\n\n{rest}\n\n  </section>" if rest else lead_html
    else:
        stories_html = '  <p class="standfirst">No qualifying stories today.</p>'

    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="author" content="AISearch Global">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" type="application/rss+xml" title="{PUB_NAME} — AI News" href="/news/rss.xml">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="shortcut icon" href="/favicon.svg">
  <link rel="apple-touch-icon" href="/assets/images/aisearch_social_graphic_plumber.png">
  <style>{SHARED_STYLE}</style>

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="AISearch Global">
  <meta property="og:locale" content="en_AU">
  <meta property="og:url" content="{canonical}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="Daily AI news brief for {short}, curated by AISearch Global.">
  <meta property="og:image" content="{SITE_URL}/assets/images/aisearch_social_graphic_plumber.png">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="Daily AI news brief for {short}, curated by AISearch Global.">
  <meta name="twitter:image" content="{SITE_URL}/assets/images/aisearch_social_graphic_plumber.png">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{GOOGLE_FONTS_HREF}" rel="stylesheet">

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
<main class="paper">

{masthead}

  <p class="standfirst">Curated daily by AISearch Global. Every story links to its original source &mdash; we don't republish, we round up.</p>

{stories_html}

{render_colophon()}

</main>
<footer></footer>
</body>
</html>
"""


# --------------------------------------------------------------------------
# Front page — /news
# --------------------------------------------------------------------------

def render_ticker(ticker_items: list[dict]) -> str:
    """'Latest' ticker strip. The item set is duplicated once in the markup so
    the CSS translateX(-50%) loop is seamless; pauses on hover and degrades to
    a static scrollable row under prefers-reduced-motion (all in SHARED_STYLE)."""
    if not ticker_items:
        return ""
    one_set = "".join(
        f'<a href="{esc(i["link"])}" target="_blank" rel="noopener">{esc(clean_text(i["headline"]))}</a>'
        f'<span class="ticker-sep">&middot;</span>'
        for i in ticker_items
    )
    return f"""  <div class="ticker">
    <span class="ticker-label">Latest</span>
    <div class="ticker-viewport">
      <div class="ticker-track">{one_set}{one_set}</div>
    </div>
  </div>"""


def render_splash(latest: dict, lead: dict | None) -> str:
    """Front-page splash: the latest edition's lead story, linking to that
    edition (not the external source — the front page sells the edition)."""
    if not lead:
        return ""
    edition_url = f"/news/{latest['date']}"
    # clean_text() first so entity-glued tokens like "just&#160;don't" split into
    # real words (nbsp is Unicode whitespace) — otherwise the 40-word cut is wrong.
    teaser_words = clean_text(lead.get("summary") or "").split()
    ellipsis = "&hellip;" if len(teaser_words) > 40 else ""
    teaser_html = f'\n    <p class="teaser">{esc(" ".join(teaser_words[:40]))}{ellipsis}</p>' if teaser_words else ""
    return f"""  <section class="splash">
    <p class="kicker">In today's edition &middot; {kicker_text(lead)}</p>
    <h2 class="headline"><a href="{edition_url}">{esc(clean_text(lead["headline"]))}</a></h2>{teaser_html}
    <p class="edition-link"><a href="{edition_url}">Read the {date_day_month(latest['date'])} edition &mdash; {story_count_label(latest['headline_count'])} &rarr;</a></p>
  </section>"""


def render_index(entries: list[dict], ticker_items: list[dict], splash_lead: dict | None) -> str:
    """entries: list of {date, human_date, headline_count} newest first."""
    canonical = f"{SITE_URL}/news"
    title = f"{PUB_NAME} — Daily AI News | AISearch Global"
    description = (f"{PUB_NAME}: daily AI news read the way machines read it. AI news, AI law & regulation, "
                   f"human-AI research and AEO-relevant developments, curated by AISearch Global, Sydney.")
    collection_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"{PUB_NAME} — Daily AI News",
        "url": canonical,
        "publisher": {"@type": "Organization", "name": "AISearch Global", "url": SITE_URL},
        "hasPart": {"@type": "Periodical", "name": PUB_NAME, "url": canonical},
    }
    latest = entries[0] if entries else None
    masthead = render_masthead(
        f"<span>{PUB_DOMAIN}</span>",
        f"Latest edition: {date_full(latest['date'])}" if latest else "First edition coming soon",
        edition_number(latest["date"]) if latest else 1,
    )
    archive_rows = "\n".join(
        f"""      <li>
        <span class="edition-date"><a href="/news/{e['date']}">{date_full(e['date'])}</a></span>
        <span class="edition-count">{story_count_label(e['headline_count'])}</span>
      </li>"""
        for e in entries
    )
    splash_html = render_splash(latest, splash_lead) if latest else ""

    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="author" content="AISearch Global">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" type="application/rss+xml" title="{PUB_NAME} — AI News" href="/news/rss.xml">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="shortcut icon" href="/favicon.svg">
  <link rel="apple-touch-icon" href="/assets/images/aisearch_social_graphic_plumber.png">
  <style>{SHARED_STYLE}</style>

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="AISearch Global">
  <meta property="og:locale" content="en_AU">
  <meta property="og:url" content="{canonical}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="Daily curated AI news, AEO-relevant developments, and an Australian focus.">
  <meta property="og:image" content="{SITE_URL}/assets/images/aisearch_social_graphic_plumber.png">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="Daily curated AI news, AEO-relevant developments, and an Australian focus.">
  <meta name="twitter:image" content="{SITE_URL}/assets/images/aisearch_social_graphic_plumber.png">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{GOOGLE_FONTS_HREF}" rel="stylesheet">

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

  <script type="application/ld+json">{json.dumps(collection_schema)}</script>
</head>
<body>
<header></header>
<main class="paper paper--front">

{masthead}

{render_ticker(ticker_items)}

{splash_html}

  <section class="archive">
    <h2 class="section-flag">Recent Editions</h2>
    <ul class="archive-list">
{archive_rows}
    </ul>
  </section>

{render_colophon()}

</main>
<footer></footer>
</body>
</html>
"""


# --------------------------------------------------------------------------
# RSS — /news/rss.xml (one item per edition)
# --------------------------------------------------------------------------

def render_rss(entries: list[dict]) -> str:
    def rfc822(date_str: str) -> str:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%a, %d %b %Y 00:00:00 +1000")

    items = []
    for e in entries:
        link = f"{SITE_URL}/news/{e['date']}"
        headlines = []
        brief_path = PENDING_DIR / f"{e['date']}.brief.json"
        if brief_path.exists():
            headlines = [clean_text(s["headline"]) for s in json.loads(brief_path.read_text(encoding="utf-8"))]
        desc = f"{story_count_label(e['headline_count'])}"
        if headlines:
            desc += ": " + " · ".join(headlines)
        items.append(
            f"    <item>\n"
            f"      <title>{esc(PUB_NAME)} — {esc(date_short(e['date']))}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid isPermaLink=\"true\">{link}</guid>\n"
            f"      <pubDate>{rfc822(e['date'])}</pubDate>\n"
            f"      <description>{esc(desc)}</description>\n"
            f"    </item>\n"
        )
    last_build = rfc822(entries[0]["date"]) if entries else rfc822(datetime.now(timezone.utc).date().isoformat())
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{esc(PUB_NAME)} — AI News</title>\n"
        f"    <link>{SITE_URL}/news</link>\n"
        f"    <atom:link href=\"{SITE_URL}/news/rss.xml\" rel=\"self\" type=\"application/rss+xml\"/>\n"
        f"    <description>{esc(PUB_TAGLINE)} Curated daily by AISearch Global.</description>\n"
        "    <language>en-au</language>\n"
        f"    <lastBuildDate>{last_build}</lastBuildDate>\n"
        + "".join(items)
        + "  </channel>\n</rss>\n"
    )


# --------------------------------------------------------------------------
# Sitemap + index metadata (unchanged pipeline)
# --------------------------------------------------------------------------

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
    parser.add_argument("--date", help="YYYY-MM-DD, defaults to today (Australia/Sydney)")
    parser.add_argument("--resummarise", action="store_true",
                        help="regenerate headline/summary copy even if <date>.brief.json already exists")
    args = parser.parse_args()

    date_str = args.date or sydney_today()
    human_date = date_short(date_str)

    pending_path = PENDING_DIR / f"{date_str}.json"
    if not pending_path.exists():
        log(f"No pending file for {date_str} ({pending_path}) — nothing to do. "
            f"Run fetch_pipeline.py first.")
        return 0

    stories = json.loads(pending_path.read_text(encoding="utf-8"))
    if not stories:
        log(f"{date_str}: pending file is empty (no stories cleared the pipeline) — skipping publish.")
        return 0

    # Reuse already-published copy when it exists: re-renders (e.g. a design
    # change) must restyle archived editions without rewriting their text.
    brief_path = PENDING_DIR / f"{date_str}.brief.json"
    if brief_path.exists() and not args.resummarise:
        briefed = json.loads(brief_path.read_text(encoding="utf-8"))
        log(f"{date_str}: reusing existing copy from {brief_path.name} ({len(briefed)} stories) — pass --resummarise to regenerate")
    else:
        briefed = []
        for story in stories:
            headline, summary = summarise_with_claude(story)
            briefed.append({**story, "headline": headline, "summary": summary})

    NEWS_DIR.mkdir(parents=True, exist_ok=True)

    page_html = render_page(date_str, human_date, briefed)
    (NEWS_DIR / f"{date_str}.html").write_text(page_html, encoding="utf-8")
    log(f"Wrote news/{date_str}.html ({len(briefed)} stories)")

    # Small metadata file per day, used to rebuild the index without re-parsing every HTML file.
    meta = {"date": date_str, "human_date": human_date, "headline_count": len(briefed)}
    (NEWS_DIR / f"{date_str}.brief-meta.json").write_text(json.dumps(meta), encoding="utf-8")

    # Save the generated (headline, summary) copy for the LinkedIn draft step.
    brief_path.write_text(json.dumps(briefed, indent=2), encoding="utf-8")

    # Build the ticker feed from the most recent days' stories, newest first.
    # Server-rendered into the front page; latest.json is still written for
    # compatibility with anything polling it.
    entries = collect_index_entries()
    ticker_items = []
    for e in entries[:5]:
        bp = PENDING_DIR / f"{e['date']}.brief.json"
        if not bp.exists():
            continue
        for s in json.loads(bp.read_text(encoding="utf-8")):
            ticker_items.append({"headline": s["headline"], "link": s["link"], "date": e["date"]})
    ticker_items = ticker_items[:MAX_TICKER_ITEMS]
    (NEWS_DIR / "latest.json").write_text(json.dumps(ticker_items, indent=2), encoding="utf-8")
    log(f"Wrote news/latest.json ({len(ticker_items)} items)")

    # The splash is the latest edition's lead story (ranked first in its brief).
    splash_lead = None
    if entries:
        latest_brief = PENDING_DIR / f"{entries[0]['date']}.brief.json"
        if latest_brief.exists():
            latest_stories = json.loads(latest_brief.read_text(encoding="utf-8"))
            splash_lead = latest_stories[0] if latest_stories else None

    # Rebuild the front page from all known days.
    (NEWS_DIR / "index.html").write_text(render_index(entries, ticker_items, splash_lead), encoding="utf-8")
    log(f"Rebuilt news/index.html ({len(entries)} days listed)")

    # RSS feed — one item per edition, newest first.
    (NEWS_DIR / "rss.xml").write_text(render_rss(entries), encoding="utf-8")
    log(f"Wrote news/rss.xml ({len(entries)} editions)")

    # Keep sitemap.xml in step with the pages just written.
    update_sitemap(date_str)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
