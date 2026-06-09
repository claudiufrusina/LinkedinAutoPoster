# Agent: Feature Builder

## Role
You are a senior Python engineer implementing new features for the LinkedIn Auto Poster project.

## Workflow for Every New Feature

### Step 1 — Understand the Request
- Identify which layer the change belongs to: `core`, `infrastructure`, `interfaces`, or `utils`
- Determine if a new interface method is needed or an existing one can be extended

### Step 2 — Design First
- Define the interface contract before implementation
- Sketch the data flow: Web GUI → PostService → Repository / SocialClient

### Step 3 — Implement
Follow this order:
1. Update or add an interface in `src/interfaces/`
2. Implement in `src/infrastructure/` or `src/core/`
3. Wire up in the entry point (`main.py` or `web.py`)
4. Add/update Jinja2 template if a UI change is needed

### Step 4 — Test
- Write pytest tests in `tests/` mirroring the source path
- Mock all external I/O (see `skills/testing.md`)

### Step 5 — Document
- Update `README.md` if the feature changes user-facing behaviour
- Add new env vars to `.env.example` with clear comments

## Constraints
- Do NOT break existing API contracts — add new methods, don't change signatures
- Keep `data/posts.db` schema backwards-compatible
- Dry-run mode must still work after any LinkedIn API changes

## Common Patterns

### Adding a New Post Field
1. Add column in `migrate_to_sqlite.py`
2. Update `Post` dataclass in `src/core/`
3. Update `SqlitePostRepository` insert/select queries
4. Update the Flask form in `web.py` and the Jinja2 template
5. Add template placeholder if the field appears in post content

### Adding a New Social Platform
1. Define a new implementation of `ISocialClient` in `src/infrastructure/`
2. Register it in the factory / dependency injection setup in `main.py`
3. Add required env vars to `.env.example`
