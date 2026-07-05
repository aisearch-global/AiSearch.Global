# AI News Automation — how it works

Three scripts, run in order, wired together by `.github/workflows/ai-news-daily.yml`:

1. **`fetch_pipeline.py`** — pulls every feed in `sources.yaml`, drops anything already
   published before (`data/seen.json`), drops anything that doesn't match the AI
   keyword filter (for sources that need it), verifies every remaining link actually
   resolves, caps stories per category, writes `data/pending/<date>.json`.
2. **`generate_brief.py`** — turns that JSON into a real, indexable page at
   `/news/<date>`, rebuilds `/news/index.html`, and rewrites `/news/latest.json`
   (the small file the ticker on `/news` polls client-side).
3. **`postiz_draft.py`** — builds a short LinkedIn post from the day's brief and
   queues it in Postiz as a **draft** — it will not auto-post. You review and send
   it from inside Postiz.

Every run appends a line to `data/run-log.jsonl` (source-by-source: found /
error) so failures are visible instead of silent. GitHub also emails repo
watchers automatically when a scheduled workflow run fails.

## Why no Cloudflare Worker

The original requirements draft suggested a Worker + KV for the live ticker.
On reflection that's unnecessary complexity: the daily GitHub Action already
commits new files and pushes to `main`, which triggers the existing
`deploy.yml` Cloudflare Pages deploy automatically. A plain static
`/news/latest.json`, fetched by a few lines of client-side JS, does the same
job with one less moving part, no new Cloudflare secrets, and no separate
`wrangler deploy` step to remember. Flagging this since it's a change from
what the original requirements doc recommended.

## Setup checklist

- [ ] **Secrets to add in GitHub repo settings → Secrets and variables → Actions:**
  - `ANTHROPIC_API_KEY` — powers the ~200-word AI-written summaries. Without it,
    the pipeline still runs and publishes, just with a plainer truncated summary
    of the source's own text instead of a written brief.
  - `POSTIZ_API_KEY` and `POSTIZ_LINKEDIN_INTEGRATION_ID` — needed for the LinkedIn
    draft step to actually reach Postiz. Without them, the script writes the draft
    text to a `.txt` file in the run instead, for manual copy-paste.
- [ ] **Confirm the thin sources** — `sources.yaml` marks confidence per feed.
  Anything tagged `unconfirmed` (OAIC, DISR, ACCC, InnovationAus) needs a real
  browser check before go-live: open the URL, see if it's actual RSS/Atom XML.
  If a government source has no native feed, the practical fallback is a small
  scraper against their media-releases listing page — tell me if you want that
  built once you've confirmed which ones are missing a feed.
- [ ] **Postiz integration ID** — find this in the Postiz dashboard for the
  already-connected `ai-search-global` LinkedIn Page channel, or ask Postiz
  support/docs for how to list integration IDs via their API.
- [ ] **First run** — trigger manually via the Actions tab (`workflow_dispatch`)
  before trusting the schedule, and check `/news` + the LinkedIn draft in Postiz
  look right.

## Run time

Defaults to 6:00am AEST (`cron: '0 20 * * *'` UTC). No daylight-saving
adjustment is built in — see the comment at the top of the workflow file if
that hour drift during AEDT (Oct-Apr) matters enough to fix properly.

## Testing locally

The scripts need open internet (RSS feeds, Anthropic API, Postiz API) — they
won't run inside a restricted sandbox. On your own machine or in the GitHub
Action:

```bash
cd automation/ai-news
pip install -r requirements.txt
python fetch_pipeline.py --dry-run     # prints what it would publish, writes nothing
python fetch_pipeline.py               # writes data/pending/<today>.json + updates seen.json
python generate_brief.py               # builds news/<today>.html, index.html, latest.json
python postiz_draft.py                 # queues (or falls back to a .txt draft)
```

## Files this creates/updates on every run

```
news/<date>.html                 archived daily brief (real page, NewsArticle schema)
news/<date>.brief-meta.json      small metadata used to rebuild the index fast
news/index.html                  regenerated list of recent briefs + ticker markup
news/latest.json                 ticker feed (last ~5 days, ~15 headlines)
automation/ai-news/data/seen.json          dedupe history (trimmed to 120 days)
automation/ai-news/data/run-log.jsonl      append-only reliability log
automation/ai-news/data/pending/<date>.json         raw candidates for the day
automation/ai-news/data/pending/<date>.brief.json   generated copy (headline+summary)
automation/ai-news/data/pending/<date>.linkedin-draft.txt   fallback if Postiz secrets aren't set
```
