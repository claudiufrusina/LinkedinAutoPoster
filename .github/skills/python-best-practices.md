# Skill: Python Best Practices

Use this skill when writing or reviewing Python code in this project.

## Type Annotations
- Always annotate function parameters and return types
- Use `Optional[X]` or `X | None` (Python 3.10+) for nullable values
- Prefer `list[str]` over `List[str]` (Python 3.9+ built-in generics)

```python
# ✅ Good
def get_post(post_id: int) -> Post | None:
    ...

# ❌ Avoid
def get_post(post_id):
    ...
```

## Data Classes
Prefer `@dataclass` for plain data containers:

```python
from dataclasses import dataclass, field

@dataclass
class Post:
    id: int
    content: str
    hashtags: list[str] = field(default_factory=list)
    published: bool = False
```

## Dependency Injection
Pass dependencies via `__init__`, never import global singletons inside functions:

```python
# ✅ Good
class PostService:
    def __init__(self, repo: IPostRepository, client: ISocialClient) -> None:
        self._repo = repo
        self._client = client
```

## Error Handling
- Raise specific exceptions; catch narrow exception types
- Log errors with `logging` module, not `print()`
- Never swallow exceptions silently

```python
import logging
logger = logging.getLogger(__name__)

try:
    result = self._client.publish(post)
except LinkedInAPIError as exc:
    logger.error("Failed to publish post %d: %s", post.id, exc)
    raise
```

## Environment Variables
Always read secrets from environment, never hardcode:

```python
import os
TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]  # raises KeyError if missing — good!
```

## Imports Order (isort convention)
1. Standard library
2. Third-party packages
3. Local application imports

Separate each group with a blank line.
