## Description
<!-- Summarise what this PR does and why -->

Closes #<!-- issue number -->

## Type of Change
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] ♻️ Refactor (no functional change)
- [ ] 📝 Documentation
- [ ] 🔧 Chore / dependency update
- [ ] 🚀 Performance improvement

## Affected Components
- [ ] Scheduler (`main.py`)
- [ ] Web GUI (`web.py` / templates)
- [ ] LinkedIn API client
- [ ] Database / migration
- [ ] Tests
- [ ] Docker / CI

## Testing Done
<!-- Describe how you tested this change -->
- [ ] Ran `pytest tests/ -v`
- [ ] Manually tested with `DRY_RUN=true`
- [ ] Manually tested the Web GUI
- [ ] Verified Docker build succeeds

## Environment Variable Changes
<!-- List any new or changed env vars, and update .env.example -->
None / see below:

```
NEW_VAR=description   # explain what it does
```

## Checklist
- [ ] Type hints on all new functions
- [ ] Docstrings on new public classes/methods
- [ ] No secrets or tokens in code
- [ ] Interface abstractions preserved
- [ ] `data/posts.db` schema is backwards-compatible (or migration script added)
- [ ] `README.md` updated if user-facing behaviour changed
