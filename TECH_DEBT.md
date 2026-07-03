# Technical debt — DJ Library Tools

Ranked backlog. Promote "Do first" items from handoff notes here.

**Story IDs:** Engineering items are also tracked as `US-ENG-*` in [doc/requirements/product.md](doc/requirements/product.md). This file stays the ranked engineering-only view.

| Priority | Category | What | Suggested fix | Story |
|----------|----------|------|---------------|-------|
| 1 | Feature | Cut dedupe apply not run | `cuts dedupe --dry-run` → user review → `--apply` | US-CUT-02 |
| 2 | Tests | No Tier 2 integration tests for pipeline/sync | Add `@pytest.mark.integration` tests with `tmp_path` fixtures | US-ENG-01 |
| 3 | Packaging | Flat layout with `sys.path` hack | Add `lib/__init__.py`; optional `pip install -e .` | US-ENG-02 |
| 4 | Lint | No ruff/format gate | Add ruff to dev deps and merge-ready command | US-ENG-03 |
| 5 | Platform | `tag_compare_delete.sh` is bash-only | Add PowerShell delete helper for Windows | US-ENG-04 |
| 6 | Config | Shallow merge (top-level keys only) | Deep merge if nested config grows | US-ENG-05 |
| 7 | Feature | `dj.py shazam import` (CSV) | Backlog in TODO.md | US-ENG-07 |

**Resolved (handoff 0003):** `dj.py tag` (#5 former), NewMusic auto-clear, ingest hash_lib fast path.
