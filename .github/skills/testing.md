# Skill: Testing Conventions

Use this skill when writing, fixing, or reviewing tests.

## Framework
- **pytest** is the test runner: `pytest tests/ -v --cov=src`
- Tests mirror the `src/` folder structure under `tests/`

## Test File Layout
```
tests/
├── conftest.py           # shared fixtures
├── core/
│   └── test_post_service.py
├── infrastructure/
│   ├── test_sqlite_repo.py
│   └── test_linkedin_client.py
└── utils/
    └── test_template_renderer.py
```

## Fixtures (conftest.py)
Define reusable fixtures for database connections, mock clients, and sample posts:

```python
import pytest
from unittest.mock import MagicMock
from src.interfaces.post_repository import IPostRepository

@pytest.fixture
def mock_repo() -> IPostRepository:
    return MagicMock(spec=IPostRepository)

@pytest.fixture
def sample_post():
    return Post(id=1, content="Hello {title}", hashtags=["#test"])
```

## Mocking External I/O
Always mock LinkedIn API calls and file-system access:

```python
from unittest.mock import patch, MagicMock

def test_publish_calls_api(mock_repo, mock_client):
    service = PostService(repo=mock_repo, client=mock_client)
    service.publish(post_id=1)
    mock_client.publish.assert_called_once()
```

## Coverage Target
- `src/core/` — ≥ 80 %
- `src/infrastructure/` — ≥ 70 % (integration paths may be excluded)
- `src/interfaces/` — skip (abstract only)

## Naming Conventions
- File: `test_<module>.py`
- Function: `test_<action>_<expected_outcome>`  
  e.g. `test_publish_raises_on_api_error`

## Do NOT
- Write tests that hit the real LinkedIn API
- Write tests that mutate `data/posts.db` on disk without a temp fixture
- Use `time.sleep()` — use `freezegun` or mock `datetime.now()`
