# Project Context: LinkedIn Auto Poster

## Purpose
LinkedIn Auto Poster is an automated Python application that schedules and publishes LinkedIn posts with dynamic content composition. It combines a Flask web GUI for managing posts with a background scheduler that handles LinkedIn API publishing.

## Core Features
- **Web GUI Dashboard** — Create, edit, delete, and preview LinkedIn posts with image uploads
- **Automated Scheduler** — Publishes queued posts at configured times via LinkedIn API
- **SQLite Database** — Stores post metadata, content, and publish history
- **Template System** — Dynamic post formatting with placeholders (`{title}`, `{body}`, `{link}`, `{hashtags}`, `@{Company}`)
- **Company @Mentions** — Automatically tags companies with LinkedIn URNs
- **Image Support** — Handles post images with secure LinkedIn upload workflow
- **Dry-run Mode** — Test the full pipeline without publishing

## Architecture
- **Clean/SOLID principles** — Interfaces (IContentProvider, IPostRepository, ISocialClient) with multiple implementations
- **Entry Points** — `main.py` (scheduler), `web.py` (web GUI), `migrate_to_sqlite.py` (data migration)
- **Key modules** — PostService orchestrates the pipeline; SqlitePostRepository and SqliteContentProvider handle data access
- **Templates** — Jinja2 HTML templates for the web interface with dark glassmorphism theme

## Tech Stack
- Python 3 with Flask framework
- SQLite database (no external DB required)
- LinkedIn API v2 integration
- Docker & Docker Compose support

## When Making Changes
- Preserve the interface abstractions (content_provider.py, post_repository.py, social_client.py)
- Both scheduler and web GUI share the same `data/posts.db` — maintain compatibility
- Template placeholders must be consistent between web preview and scheduler rendering
- Image uploads must follow the secure LinkedIn API handshake workflow
