# Technical debt — DJ Library Tools

Ranked backlog. Promote "Do first" items from handoff notes here.

| Priority | Category | What | Suggested fix |
|----------|----------|------|---------------|
| 1 | Tests | No Tier 2 integration tests for pipeline/sync | Add `@pytest.mark.integration` tests with `tmp_path` fixtures |
| 2 | Packaging | Flat layout with `sys.path` hack | Add `lib/__init__.py`; optional `pip install -e .` |
| 3 | Lint | No ruff/format gate | Add ruff to dev deps and merge-ready command |
| 4 | Platform | `tag_compare_delete.sh` is bash-only | Add PowerShell delete helper for Windows |
| 5 | Feature | No `dj.py tag` (AcoustID/MusicBrainz) | Add `lib/tag.py`; pyacoustid in requirements |
| 6 | Config | Shallow merge (top-level keys only) | Deep merge if nested config grows |
