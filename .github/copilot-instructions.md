# GitHub Copilot Instructions — LinkedIn Auto Poster

## Project Overview
LinkedIn Auto Poster is an automated Python application that schedules and publishes LinkedIn posts with dynamic content composition. It combines a Flask web GUI for managing posts with a background scheduler that handles LinkedIn API publishing.

## Repository Layout
```
LinkedinAutoPoster/
├── src/
│   ├── core/           # Domain logic (PostService, scheduler)
│   ├── interfaces/     # Abstractions: IContentProvider, IPostRepository, ISocialClient
│   ├── infrastructure/ # Implementations: SQLite repos, LinkedIn API client
│   └── utils/          # Shared helpers
├── templates/          # Jinja2 HTML templates (dark glassmorphism theme)
├── static/             # CSS, JS, images
├── data/               # posts.db (SQLite) — shared by scheduler and web GUI
├── tests/              # Pytest test suite
├── main.py             # Entry point: background scheduler
├── web.py              # Entry point: Flask web GUI
└── docker-compose.yml  # Docker support
```

## Architecture & Design Principles
- **Clean/SOLID** — Always program to the interfaces in `src/interfaces/`:
  - `IContentProvider` — supplies post content
  - `IPostRepository` — persists and retrieves posts
  - `ISocialClient` — publishes to social platforms
- **PostService** — orchestrates the publish pipeline; do NOT add side-effects directly to entry points
- Both `main.py` and `web.py` share the same `data/posts.db`; migrations must be backwards-compatible

## Tech Stack
- **Language**: Python 3.11+
- **Web**: Flask (Jinja2 templates)
- **Database**: SQLite via `sqlite3` (no ORM)
- **API**: LinkedIn API v2 (OAuth 2.0)
- **Infra**: Docker & Docker Compose

## Coding Standards
- Follow PEP 8; use type hints on all function signatures
- Prefer dependency injection — pass dependencies via constructors, not globals
- Use `dataclasses` or `TypedDict` for data transfer objects
- All external I/O (API calls, DB writes) must be behind the interface abstractions
- No secrets or tokens in source code — use `.env` / environment variables

## Template Placeholders
Post templates use these placeholders — keep them consistent between web preview and scheduler rendering:
- `{title}`, `{body}`, `{link}`, `{hashtags}`, `@{Company}`

## Image Uploads
Always follow the secure LinkedIn API three-step handshake:
1. Register upload → get `uploadUrl` + `asset`
2. PUT binary to `uploadUrl`
3. Attach `asset` URN to the post payload

## Testing Guidelines
- Locate tests in `tests/` mirroring the `src/` structure
- Mock all external I/O (LinkedIn API, file system) with `unittest.mock`
- Run with: `pytest tests/ -v`
- Aim for ≥ 80 % coverage on `src/core/` and `src/infrastructure/`

## Dry-Run Mode
When `DRY_RUN=true` in env, the scheduler must skip actual API calls and log what it _would_ publish.

## PR & Commit Conventions
- Branch naming: `feat/<short-desc>`, `fix/<short-desc>`, `chore/<short-desc>`
- Commits: Conventional Commits format (`feat:`, `fix:`, `docs:`, `test:`, `chore:`)
- Every PR must include: description of change, testing done, and any env-var changes
