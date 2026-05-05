# Contributing to JustHireMe

Thanks for helping make JustHireMe useful for real job seekers.

## Project Direction

The OSS core is a local-first job intelligence workbench:

- scrape job sources
- rank lead quality and candidate fit
- use profile graph/vector data
- customize resume, cover letter, and outreach drafts

Browser automation and auto-apply are experimental lab areas, not the main contribution path.

## Local Setup

```bash
npm install
cd backend
uv sync --dev
cd ..
npm run tauri dev
```

## Checks Before a PR

```bash
npm run typecheck
npm test
npm run build
backend/.venv/Scripts/python.exe -m pytest backend/tests
```

On macOS/Linux, use `backend/.venv/bin/python -m pytest backend/tests`.

## Adding a Scraper Source

Start with `docs/source-adapters.md`.

A source contribution should include:

- a parser or adapter that returns normalized lead dictionaries
- source-specific freshness and URL handling
- quality gate metadata where useful
- tests for at least one good lead and one rejected/noisy lead
- docs showing how users configure the source

Prefer ATS/company-board adapters over broad search scraping. Search scraping is useful, but should be treated as lower-confidence fallback data.

## Coding Expectations

- Keep changes scoped.
- Avoid committing local data, keys, generated app data, or databases.
- Add deterministic tests for ranking, parsing, and quality rules.
- Keep user-facing copy honest about what is core vs experimental.

## PR Checklist

- [ ] I ran the relevant frontend/backend checks.
- [ ] I added or updated tests for behavior changes.
- [ ] I updated docs for user-visible or contributor-visible changes.
- [ ] I did not include private data, API keys, local database files, or generated artifacts.
