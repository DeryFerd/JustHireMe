# JustHireMe

**Local-first job intelligence for finding better roles, ranking fit, and generating tailored application material.**

JustHireMe is an open-source desktop workbench for job seekers and builders who want a transparent, hackable alternative to noisy job boards and opaque "AI apply" tools. It helps you collect leads from configurable sources, rank them against your profile, explain why each job was shown, and generate tailored resume, cover letter, and outreach drafts.

The project is intentionally **local-first**. Your profile, lead history, generated documents, graph data, vector data, and settings live on your machine by default.

```text
Import profile -> Scrape sources -> Quality gate -> Rank fit -> Match with vectors -> Customize documents/outreach
```

## Status

JustHireMe is in early alpha and being prepared for a public OSS community. Expect active refactoring, rough edges, and incomplete release tooling. The core direction is stable:

- scraper
- ranker
- vector-backed matching
- customization package generation
- local-first desktop workflow

Browser automation and auto-apply code exists in the repository, but it is **experimental, unsupported, and not part of the core product promise**.

## What JustHireMe Does

### 1. Scrape Job Leads

JustHireMe can collect jobs and opportunity signals from configured sources such as:

- ATS/company boards
- Greenhouse, Lever, Ashby, Workable-style targets
- RSS feeds
- Hacker News hiring threads
- GitHub issue/search-style sources
- Reddit/community sources
- Remote job APIs and user-provided targets

The preferred contribution path is direct source adapters for company and ATS boards. Broad search scraping is supported as a fallback, but treated as lower-confidence data.

### 2. Filter Bad Leads Before They Pollute the Pipeline

Scraped data is messy. JustHireMe includes a deterministic lead quality gate that can reject or down-rank:

- missing source/apply URLs
- thin scraped rows
- stale jobs
- senior-only roles in beginner-focused feeds
- unpaid, spammy, or low-trust postings
- postings with missing company/context signals

Saved leads carry quality metadata so users and contributors can inspect why a lead was shown.

### 3. Rank Candidate Fit

The backend evaluates each lead against the candidate profile using:

- deterministic rubric scoring
- seniority caps
- stack and project evidence
- red-flag checks
- source signal
- optional LLM-assisted evaluation
- semantic matching when vectors are available

The score is designed to be explainable. A low score should say what is missing; a high score should point to actual evidence.

### 4. Use Graph And Vector Data

The profile system stores structured candidate context:

- skills
- projects
- experience
- certifications
- education
- achievements
- summary/profile text

Kuzu is used for graph-style local profile data. LanceDB stores profile vectors for semantic matching. The intended data flow is:

```text
Resume/profile ingestion -> structured profile graph -> skill/project embeddings -> semantic fit during job evaluation
```

If vector search or embeddings are unavailable, the app falls back to deterministic scoring and makes that fallback visible.

### 5. Generate A Customization Package

For a promising lead, JustHireMe can generate:

- tailored resume PDF
- tailored cover letter PDF
- founder message
- LinkedIn note
- cold email
- keyword coverage summary
- selected project rationale

The app does not need auto-apply to be useful. The supported workflow is: find better jobs, understand fit, generate better materials, then apply through the channel you trust.

## Product Principles

- **Local-first:** user data should stay on the user's machine by default.
- **Explainable:** every ranking and filtering decision should be inspectable.
- **Contributor-friendly:** adding a job source should be straightforward and well-tested.
- **No fake confidence:** if vectors, models, or source data are unavailable, the app should say so.
- **Human-controlled:** generated materials are drafts for review, not magic submissions.
- **Automation is experimental:** browser automation is a lab area, not the core OSS product.

## Tech Stack

| Area | Technology |
| --- | --- |
| Desktop shell | Tauri 2 |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Backend API | Python 3.13, FastAPI, WebSockets |
| Local CRM | SQLite |
| Profile graph | Kuzu |
| Vector store | LanceDB |
| Agent flow | LangGraph-style backend modules |
| Document generation | Markdown/PDF rendering |
| Browser automation lab | Playwright |
| Packaging | Tauri bundle + Python sidecar |

## Repository Layout

```text
JustHireMe/
├── src/                         # React frontend
│   ├── components/              # Shared UI components
│   ├── hooks/                   # Frontend data/websocket hooks
│   ├── settings/                # Settings sections
│   └── views/                   # Main app screens
├── backend/                     # Python API, agents, ranking, storage
│   ├── agents/                  # Scrapers, rankers, evaluator, generator
│   ├── db/                      # SQLite/Kuzu/LanceDB access
│   ├── graph/                   # Evaluation graph flow
│   └── tests/                   # Backend regression/API tests
├── src-tauri/                   # Tauri Rust shell and sidecar config
├── docs/                        # Contributor and release docs
├── scripts/                     # Build scripts
└── .github/                     # CI and issue templates
```

## Requirements

Install these before running the app locally:

- Node.js 20+
- Rust stable
- Python 3.13+
- uv
- Git

Optional:

- Ollama, for local model experiments
- Playwright browser dependencies, only if working on experimental automation

## Quick Start

Clone the repository:

```bash
git clone https://github.com/vasu-devs/JustHireMe.git
cd JustHireMe
```

Install frontend dependencies:

```bash
npm install
```

Install backend dependencies:

```bash
cd backend
uv sync --dev
cd ..
```

Run the desktop app in development:

```bash
npm run tauri dev
```

The Tauri shell starts the frontend and launches the Python backend sidecar/dev process.

## Development Commands

Frontend typecheck:

```bash
npm run typecheck
```

Frontend tests:

```bash
npm test
```

Production frontend build:

```bash
npm run build
```

Backend tests on Windows:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/tests
```

Backend tests on macOS/Linux:

```bash
backend/.venv/bin/python -m pytest backend/tests
```

Rust/Tauri check:

```bash
cd src-tauri
cargo check
```

## Configuration

Settings are configured inside the desktop app. For v1, API keys are stored in local app settings.

Supported provider areas include:

- global LLM provider
- evaluator model/provider
- generator model/provider
- ingestor model/provider
- scraper/source settings
- source quality thresholds
- experimental automation settings

Do not share screenshots, logs, local app data, or issue reports that contain API keys, cookies, private resumes, or local database contents.

## Data And Privacy

JustHireMe stores local data under the user's local app data directory. It may include:

- profile graph
- vector tables
- SQLite CRM database
- generated PDFs
- settings
- activity history
- lead metadata

This is useful for privacy and hackability, but it also means your local app data directory is sensitive. Treat it like a private workspace.

Planned improvement:

- OS keychain-backed API key storage

## Core Backend Concepts

### Scraper Sources

Scraper modules collect raw leads and normalize them into a shared lead shape. See:

- `backend/agents/free_scout.py`
- `backend/agents/scout.py`
- `docs/source-adapters.md`

### Lead Quality Gate

The quality gate lives in:

- `backend/agents/quality_gate.py`

It evaluates whether a scraped lead is worth saving. It attaches quality score and explanation metadata for UI/debugging.

### Ranking And Evaluation

Ranking and scoring logic lives around:

- `backend/agents/lead_intel.py`
- `backend/agents/feedback_ranker.py`
- `backend/agents/scoring_engine.py`
- `backend/agents/evaluator.py`

### Vector Matching

Semantic matching is handled through:

- `backend/agents/ingestor.py`
- `backend/agents/semantic.py`
- `backend/db/client.py`

### Customizer

Document and outreach generation lives in:

- `backend/agents/generator.py`

The customizer produces the user-facing package: resume PDF, cover letter PDF, and outreach drafts.

## Windows Release Build

The first public packaging target is Windows.

Build the Python sidecar:

```powershell
.\scripts\build-sidecar.ps1
```

Build the Tauri bundle:

```powershell
npm run tauri build
```

See [docs/windows-release.md](docs/windows-release.md) for the smoke test checklist.

## Contributing

Contributions are welcome. The best first contribution path is improving sources and ranking quality.

Start here:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/source-adapters.md](docs/source-adapters.md)
- [ROADMAP.md](ROADMAP.md)
- `.github/ISSUE_TEMPLATE/`

Good first contribution areas:

- add a source adapter
- add scraper fixtures
- improve lead quality rules
- improve ranker tests
- document local Ollama setup
- improve Windows installer instructions
- improve UI copy around fit explanations

Please do not open public issues with API keys, resumes, cookies, bearer tokens, or database files.

## Issue Types

Use the provided issue templates:

- bug report
- scraper source request
- ranker/scoring improvement
- docs task
- good first issue

When reporting ranking issues, include sanitized job snippets and expected behavior. The most useful reports explain why a lead should have been shown, hidden, scored higher, or scored lower.

## Experimental Automation

The repository contains browser automation and auto-apply code. This exists for experimentation and future plugin work, but it is not the supported core workflow.

Current stance:

- not marketed as a core feature
- not required for useful job search
- disabled by default
- should be treated carefully by contributors
- may become an optional plugin later

## Roadmap

See [ROADMAP.md](ROADMAP.md).

Near-term priorities:

- more high-quality ATS/company source adapters
- stronger quality gate tests
- clearer vector matching state in the UI
- Windows installer polish
- contributor-friendly source plugin boundaries
- OS keychain support for API keys

## License

JustHireMe is released under the [MIT License](LICENSE).

## Maintainer Note

This project is being built in the open because one person cannot cover every job source, every market, every ranking edge case, and every packaging path alone. The goal is to make a useful local tool and a welcoming codebase where contributors can add sources, improve ranking, and help job seekers get better signal with less noise.
