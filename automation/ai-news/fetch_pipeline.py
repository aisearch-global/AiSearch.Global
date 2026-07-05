#!/usr/bin/env python3
"""
AI News Automation — Step 1: fetch, dedupe, verify, rank.

Reads sources.yaml, pulls each RSS feed, drops anything already published
(data/seen.json), drops anything that doesn't look AI-relevant (when the
source requires that filter), verifies each remaining link actually resolves,
caps how many stories survive per category, and writes the result to
data/pending/<date>.json for generate_brief.py to turn into copy.

Every run appends one line to data/run-log.jsonl so failures are visible
instead of silent. Designed to run inside GitHub Actions (needs open internet
— will not work from a network-restricted sandbox).

Usage:
    python fetch_pipeline.py                # normal run
    python fetch_pipeline.py --dry-run       # fetch + print, don't write seen.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import feedparser
import requests
import yaml

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
PENDING_DIR = DATA_DIR / "pending"
SEEN_FILE = DATA_DIR / "seen.json"
LOG_FILE = DATA_DIR / "run-log.jsonl"

SEEN_RETENTION_DAYS = 120        # how long a story is remembered so it isn't republished
MAX_ENTRIES_PER_FEED = 25        # how far into each feed we look
MAX_STORIES_PER_CATEGORY = 3     # cap so one noisy category doesn't crowd out the rest
MAX_STORIES_TOTAL = 12
FETCH_TIMEOUT = 15
FETCH_RETRIES = 3
FETCH_BACKOFF_SECONDS = 4
VERIFY_TIMEOUT = 8

USER_AGENT = (
    "Mozilla/5.0 (compatible; AISearchGlobalNewsBot/1.0; "
    "+https://aisearch.global/news)"
)

# Tracking params etc. stripped before a link is used as a dedupe key or archived.
STRIP_QUERY_PREFIXES = ("utm_", "ref", "fbclid", "gclid", "mc_cid", "mc_eid")


def log(msg: str) -> None:
    print(f"[fetch_pipeline] {msg}", flush=True)


def load_sources() -> tuple[list[dict], list[str]]:
    with open(ROOT / "sources.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config["sources"], [k.lower() for k in config.get("ai_keywords", [])]


def load_seen() -> dict:
    if not SEEN_FILE.exists():
        return {}
    try:
        return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        log("WARNING: seen.json unreadable, starting fresh")
        return {}


def save_seen(seen: dict) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=SEEN_RETENTION_DAYS)
    trimmed = {
        k: v for k, v in seen.items()
        if datetime.fromisoformat(v) > cutoff
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(trimmed, indent=2, sort_keys=True), encoding="utf-8")


def canonical_link(link: str) -> str:
    """Strip tracking params so the same story from two feeds dedupes cleanly."""
    parts = urlsplit(link.strip())
    q = [(k, v) for k, v in parse_qsl(parts.query) if not k.lower().startswith(STRIP_QUERY_PREFIXES)]
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), urlencode(q), ""))


def normalize_title(title: str) -> str:
    t = re.sub(r"[^a-z0-9 ]", "", title.lower())
    return re.sub(r"\s+", " ", t).strip()


def story_key(title: str, link: str) -> str:
    basis = normalize_title(title) + "|" + canonical_link(link)
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:24]


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def matches_keywords(text: str, keywords: list[str]) -> bool:
    haystack = f" {text.lower()} "
    return any(kw in haystack for kw in keywords)


def fetch_source(source: dict, keywords: list[str], seen: dict) -> tuple[list[dict], str | None]:
    url = source["url"]
    last_error = None
    feed = None
    for attempt in range(1, FETCH_RETRIES + 1):
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=FETCH_TIMEOUT)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            if feed.bozo and not feed.entries:
                raise ValueError(f"unparseable feed (bozo): {feed.bozo_exception}")
            break
        except Exception as exc:  # noqa: BLE001 — we want to catch and log everything here
            last_error = str(exc)
            log(f"  attempt {attempt}/{FETCH_RETRIES} failed for {source['name']}: {last_error}")
            if attempt < FETCH_RETRIES:
                time.sleep(FETCH_BACKOFF_SECONDS * attempt)

    if feed is None:
        return [], last_error or "unknown fetch failure"

    candidates = []
    for entry in feed.entries[:MAX_ENTRIES_PER_FEED]:
        title = strip_html(entry.get("title", ""))
        link = entry.get("link", "").strip()
        if not title or not link:
            continue

        key = story_key(title, link)
        if key in seen:
            continue

        summary = strip_html(entry.get("summary", "") or entry.get("description", ""))

        if source.get("ai_filter", True) and not matches_keywords(f"{title} {summary}", keywords):
            continue

        published = entry.get("published", entry.get("updated", ""))

        candidates.append({
            "key": key,
            "title": title,
            "link": canonical_link(link),
            "summary_raw": summary[:1200],
            "published": published,
            "source": source["name"],
            "categories": source["categories"],
        })

    return candidates, None


def verify_url(url: str) -> bool:
    try:
        resp = requests.head(url, headers={"User-Agent": USER_AGENT}, timeout=VERIFY_TIMEOUT, allow_redirects=True)
        if resp.status_code >= 400 or resp.status_code == 405:
            # Some servers don't support HEAD properly — confirm with a light GET before giving up.
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=VERIFY_TIMEOUT, stream=True)
        return resp.status_code < 400
    except requests.RequestException:
        return False


def dedupe_across_sources(candidates: list[dict]) -> list[dict]:
    seen_keys = set()
    result = []
    for c in candidates:
        if c["key"] in seen_keys:
            continue
        seen_keys.add(c["key"])
        result.append(c)
    return result


def rank_and_cap(candidates: list[dict]) -> list[dict]:
    """Cap per category so no single noisy feed crowds out the rest of the brief."""
    per_category_count: dict[str, int] = {}
    kept = []
    for c in candidates:
        cats = c["categories"]
        if any(per_category_count.get(cat, 0) >= MAX_STORIES_PER_CATEGORY for cat in cats):
            # still allow it if at least one of its categories has room
            if all(per_category_count.get(cat, 0) >= MAX_STORIES_PER_CATEGORY for cat in cats):
                continue
        for cat in cats:
            per_category_count[cat] = per_category_count.get(cat, 0) + 1
        kept.append(c)
        if len(kept) >= MAX_STORIES_TOTAL:
            break
    return kept


def append_run_log(entry: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="fetch and print, don't persist state")
    args = parser.parse_args()

    today = datetime.now(timezone.utc).date().isoformat()
    run_started = datetime.now(timezone.utc).isoformat()

    sources, keywords = load_sources()
    seen = load_seen()

    all_candidates = []
    source_results = []
    for source in sources:
        log(f"Fetching {source['name']} ({source['url']})")
        candidates, error = fetch_source(source, keywords, seen)
        source_results.append({
            "name": source["name"],
            "confidence": source.get("confidence", "unknown"),
            "found": len(candidates),
            "error": error,
        })
        if error:
            log(f"  SOURCE FAILED: {source['name']}: {error}")
        else:
            log(f"  kept {len(candidates)} candidate(s) after keyword filter + dedupe-against-seen")
        all_candidates.extend(candidates)

    deduped = dedupe_across_sources(all_candidates)
    log(f"{len(deduped)} unique candidates across all sources before URL verification")

    verified = []
    dropped_broken = 0
    for c in deduped:
        if verify_url(c["link"]):
            verified.append(c)
        else:
            dropped_broken += 1
            log(f"  DROPPED (broken link): {c['title']} -> {c['link']}")

    ranked = rank_and_cap(verified)
    log(f"{len(ranked)} stories selected for today's brief (after per-category cap)")

    if not args.dry_run:
        for c in ranked:
            seen[c["key"]] = run_started
        save_seen(seen)

        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        out_path = PENDING_DIR / f"{today}.json"
        out_path.write_text(json.dumps(ranked, indent=2), encoding="utf-8")
        log(f"Wrote {out_path}")

        append_run_log({
            "run_at": run_started,
            "date": today,
            "sources": source_results,
            "candidates_before_verify": len(deduped),
            "dropped_broken_links": dropped_broken,
            "stories_selected": len(ranked),
        })
    else:
        log("Dry run — nothing written to disk")
        print(json.dumps(ranked, indent=2))

    if len(ranked) == 0:
        log("No stories cleared the pipeline today — this is not necessarily an error "
            "(quality over quota), but check run-log.jsonl if it happens repeatedly.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
