# JustHireMe

Local-first job intelligence workbench for finding relevant roles, ranking fit, and generating tailored application material.

JustHireMe is being prepared as an open-source desktop app. The core workflow is:

```text
Import profile -> Scrape sources -> Rank leads -> Match with vectors -> Customize resume, cover letter, and outreach
```

The project is privacy-forward: profile data, generated documents, lead history, graph data, and vector stores live on your machine by default.

## Core Features

- **Scraper:** Collect jobs from ATS/company boards, RSS feeds, Hacker News, GitHub, Reddit, and configured source targets.
- **Ranker:** Score lead quality, seniority fit, freshness, source signal, and candidate match.
- **Vector-backed matching:** Store profile skills/projects in Kuzu + LanceDB and use semantic fit during evaluation.
- **Customizer:** Generate tailored resume PDF, cover letter PDF, founder message, LinkedIn note, and cold email drafts.
- **Local-first CRM:** Track leads, scores, generated assets, feedback, follow-ups, and activity locally.

## Experimental

Browser automation and auto-apply code remains in the repository for contributors, but it is not part of the core OSS product promise. Treat it as an unsupported lab area.

## Tech Stack

Tauri 2, React 19, TypeScript, Python 3.13, FastAPI, Kuzu, LanceDB, SQLite, LangGraph, Playwright.

## Getting Started

### Prerequisites

- Node 20+
- Rust stable
- Python 3.13+
- uv

### Install

```bash
npm install
cd backend
uv sync --dev
cd ..
```

### Run Desktop App

```bash
npm run tauri dev
```

### Run Checks

```bash
npm run typecheck
npm test
npm run build
backend/.venv/Scripts/python.exe -m pytest backend/tests
```

On macOS/Linux, use `backend/.venv/bin/python -m pytest backend/tests`.

## API Keys And Privacy

For v1, API keys are stored in local app settings. Do not share logs, screenshots, issues, or database files that contain your keys or private profile data. OS keychain support is planned.

## Contributing

The easiest contribution path is adding or improving scrapers. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the source adapter contract in [docs/source-adapters.md](docs/source-adapters.md).

Good first areas:

- Add a new ATS/company-board source adapter.
- Add parser tests for an existing source.
- Improve lead quality rules.
- Improve Windows installer docs.
- Improve Ollama/local model docs.

## Roadmap

See [ROADMAP.md](ROADMAP.md).
