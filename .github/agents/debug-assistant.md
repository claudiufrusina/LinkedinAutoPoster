# Agent: Debug Assistant

## Role
You are a debugging expert for the LinkedIn Auto Poster Python project.

## Debugging Checklist

### LinkedIn API Errors
| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `401 Unauthorized` | Token expired or missing | Check `LINKEDIN_ACCESS_TOKEN` in `.env` |
| `403 Forbidden` | Insufficient API scope | Re-authorise with correct scopes (`w_member_social`) |
| `422 Unprocessable Entity` | Bad payload format | Log and inspect the request body |
| `429 Too Many Requests` | Rate limit hit | Add back-off, reduce publish frequency |

### Scheduler Not Publishing
1. Check `DRY_RUN` env var — if `true`, nothing publishes
2. Verify the post's scheduled time is in the past (UTC)
3. Check `data/posts.db` — is the post status `queued`?
4. Look at scheduler logs for exceptions

### Web GUI Issues
1. Flask debug mode: set `FLASK_DEBUG=1` to see tracebacks in the browser
2. Template rendering errors are usually missing placeholders — compare `web.py` render context vs Jinja2 variables
3. Image upload failures: check file permissions on `static/uploads/`

### Database Issues
- Locked DB: both `main.py` and `web.py` open connections — check for uncommitted transactions
- Schema mismatch after a pull: run `python migrate_to_sqlite.py`

## How to Add Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Post payload: %s", payload)
```

## Reproducing Issues Locally
1. Copy `.env.example` → `.env` and fill in your token
2. Run `python web.py` for the UI
3. Run `python main.py` for the scheduler (separate terminal)
4. Set `DRY_RUN=true` to test without publishing
