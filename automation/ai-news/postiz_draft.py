#!/usr/bin/env python3
"""
AI News Automation — Step 3: queue a LinkedIn draft in Postiz.

Reads data/pending/<date>.brief.json (written by generate_brief.py), writes a
short LinkedIn post covering the top 1-3 stories + a link to the day's brief
page, and pushes it to Postiz as a DRAFT (never auto-posted — Viv reviews and
sends it from inside Postiz).

Requires two secrets to actually reach Postiz:
    POSTIZ_API_KEY
    POSTIZ_LINKEDIN_INTEGRATION_ID   (the integration/channel ID for the
                                       already-connected "ai-search-global"
                                       LinkedIn Page in Postiz)

If either is missing, the script falls back to writing the draft text to
data/pending/<date>.linkedin-draft.txt so the pipeline still runs end-to-end
and the post can be pasted in manually. This is the expected mode until Viv
adds the two secrets to the repo.

Postiz public API reference: https://docs.postiz.com/public-api/posts/create
POST https://api.postiz.com/public/v1/posts
  { "type": "draft", "posts": [{ "integration": "<id>", "content": "<text>" }] }

NOTE: the exact payload shape should be re-checked against Postiz's current
docs before first real run — third-party API surfaces change. Treat this as
a first draft of the integration, not a guaranteed-correct final version.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
PENDING_DIR = DATA_DIR / "pending"

SITE_URL = "https://aisearch.global"
POSTIZ_API_URL = "https://api.postiz.com/public/v1/posts"
MAX_STORIES_IN_POST = 3


def log(msg: str) -> None:
    print(f"[postiz_draft] {msg}", flush=True)


def build_post_text(date_str: str, human_date: str, stories: list[dict]) -> str:
    lines = [f"AI news brief — {human_date}", ""]
    for s in stories[:MAX_STORIES_IN_POST]:
        lines.append(f"→ {s['headline']}")
    lines.append("")
    lines.append("Full roundup, with sources linked:")
    lines.append(f"{SITE_URL}/news/{date_str}")
    lines.append("")
    lines.append("#AEO #AnswerEngineOptimisation #AI")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD, defaults to today")
    args = parser.parse_args()

    date_str = args.date or datetime.utcnow().date().isoformat()
    human_date = datetime.fromisoformat(date_str).strftime("%-d %B %Y")

    brief_path = PENDING_DIR / f"{date_str}.brief.json"
    if not brief_path.exists():
        log(f"No brief file for {date_str} — nothing to queue. Run generate_brief.py first.")
        return 0

    stories = json.loads(brief_path.read_text(encoding="utf-8"))
    if not stories:
        log(f"{date_str}: brief file is empty — nothing to post.")
        return 0

    post_text = build_post_text(date_str, human_date, stories)

    api_key = os.environ.get("POSTIZ_API_KEY")
    integration_id = os.environ.get("POSTIZ_LINKEDIN_INTEGRATION_ID")

    if not api_key or not integration_id:
        fallback_path = PENDING_DIR / f"{date_str}.linkedin-draft.txt"
        fallback_path.write_text(post_text, encoding="utf-8")
        log("POSTIZ_API_KEY / POSTIZ_LINKEDIN_INTEGRATION_ID not set — "
            f"wrote draft text to {fallback_path} instead. Paste it into "
            "Postiz manually, or add the secrets so this step can do it "
            "automatically.")
        return 0

    payload = {
        "type": "draft",
        "posts": [
            {"integration": integration_id, "content": post_text}
        ],
    }
    try:
        resp = requests.post(
            POSTIZ_API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=20,
        )
        resp.raise_for_status()
        log(f"Draft queued in Postiz for {human_date} (LinkedIn, awaiting your review).")
    except requests.RequestException as exc:
        log(f"FAILED to queue Postiz draft: {exc}")
        fallback_path = PENDING_DIR / f"{date_str}.linkedin-draft.txt"
        fallback_path.write_text(post_text, encoding="utf-8")
        log(f"Wrote fallback draft text to {fallback_path} so nothing is lost.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
