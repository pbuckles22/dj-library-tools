# PM_PLAN — DJ Library Tools

**Epics and user stories:** [doc/requirements/product.md](doc/requirements/product.md)  
**Coverage matrix (US + code surfaces):** [doc/requirements/coverage.md](doc/requirements/coverage.md)

## Current phase

**Phase 3 — Cut policy on NAS + Serato ops** (July 2026)

CLI and Tier-1 tests are Serato-first. Remaining work is **manual NAS apply** and Serato UI cleanup.

- [x] `dj.py tag` (AcoustID); pipeline tag step — US-TAG-01
- [x] NewMusic ingest + validated clear in pipeline — US-PIPE-01
- [x] Quality tiers (`audit bitrates --tier-cleanup`) — US-QUAL-01
- [x] Freeze lock + clash policy + NAS link + gig USB — US-FREEZE-*, US-CLASH-01, US-NAS-01, US-USB-01
- [x] Serato primary sync + `refresh` default — US-SYNC-02
- [x] Relocate / cleanup helpers — US-CLEAN-01, US-CLEAN-03
- [x] Code → docs reconciliation (every public surface mapped)
- [ ] **Cut standardize** on NAS — **US-CUT-01** (CLI ready; dry-run → apply)
- [ ] **Cut dedupe narrow** on NAS — **US-CUT-02** (dry-run → user-approved `--apply`)
- [ ] Serato drive cleanup + analyze — **US-SYNC-02** manual
- [ ] Shazam manual queue — **US-SHAZ-01**; legacy folder review — **US-CLEAN-02** ([TODO.md](TODO.md))

**Phase 2 — Operational cleanup** — **complete**

- [x] Delete confirmed dupes from old NAS folders (16,798) — US-OLD-02
- [x] Pipeline + sync helpers
- [x] Relocate / cleanup / audit bitrates

## Engineering (ongoing)

- [x] Windows UTF-8 fixes
- [x] Tier 1 tests: **152** passed, 1 skipped — US-ENG-06
- [x] ≥80% code coverage (`lib/` + `dj.py`) — US-ENG-09 (**81%**)
- [x] Requirement matrix + code surface inventory — [coverage.md](doc/requirements/coverage.md)
- [ ] Tier 2 pipeline integration tests — US-ENG-01
- [ ] ruff/format gate — US-ENG-03

## Next

See [doc/requirements/product.md](doc/requirements/product.md) (Now: US-CUT-01 → US-CUT-02 → US-SYNC-02 manual), [AGENT_HANDOFF.md](AGENT_HANDOFF.md), and [TODO.md](TODO.md).
