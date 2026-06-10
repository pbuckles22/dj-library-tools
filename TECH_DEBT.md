# Technical debt — DJ Library Tools

Ranked backlog. Promote "Do first" items from handoff notes here.

| Priority | Category | What | Suggested fix |
|----------|----------|------|---------------|
| 1 | Feature | Cut dedupe apply not run | `cuts dedupe --dry-run` → user review → `--apply` |
| 2 | Tests | No Tier 2 integration tests for pipeline/sync | Add `@pytest.mark.integration` tests with `tmp_path` fixtures |
| 3 | Packaging | Flat layout with `sys.path` hack | Add `lib/__init__.py`; optional `pip install -e .` |
| 4 | Lint | No ruff/format gate | Add ruff to dev deps and merge-ready command |
| 5 | Platform | `tag_compare_delete.sh` is bash-only | Add PowerShell delete helper for Windows |
| 6 | Config | Shallow merge (top-level keys only) | Deep merge if nested config grows |
| 7 | Feature | `dj.py shazam import` (CSV) | Backlog in TODO.md |

**Resolved (handoff 0003):** `dj.py tag` (#5 former), NewMusic auto-clear, ingest hash_lib fast path.
