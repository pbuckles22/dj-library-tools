# PM_PLAN — DJ Library Tools

**Epics and user stories:** [doc/requirements/product.md](doc/requirements/product.md)

## Current phase

**Phase 3 — Metadata & cut policy** (June 2026)

- [x] `dj.py tag` (AcoustID); pipeline tag step — US-TAG-01
- [x] NewMusic ingest + validated clear in pipeline — US-PIPE-01
- [x] Quality tiers (`audit bitrates --tier-cleanup`) — US-QUAL-01
- [x] Master ~5,205 club tracks; NewMusic cleared
- [ ] **Cut standardize** — intro aliases → `Intro Clean` — **US-CUT-01**
- [ ] **Cut dedupe narrow** — dry-run then user-approved apply — **US-CUT-02**
- [ ] Rekordbox sync after cuts — **US-SYNC-01**
- [ ] Shazam manual queue — **US-SHAZ-01**; legacy folder review — **US-CLEAN-02** ([TODO.md](TODO.md))

**Phase 2 — Operational cleanup** — **complete**

- [x] Delete confirmed dupes from old NAS folders (16,798) — US-OLD-02
- [x] Pipeline + Rekordbox sync
- [x] Relocate / cleanup helpers

## Engineering (ongoing)

- [x] Windows UTF-8 fixes (0477a62)
- [x] Tier 1 tests: **66** passing — US-ENG-06
- [ ] Tier 2 pipeline integration tests — US-ENG-01
- [ ] ruff/format gate — US-ENG-03

## Next

See [doc/requirements/product.md](doc/requirements/product.md) (Now: US-CUT-01 → US-CUT-02 → US-SYNC-01), [AGENT_HANDOFF.md](AGENT_HANDOFF.md), and [doc/handoff/0003-HANDOFF-2026-06-10_1800.md](doc/handoff/0003-HANDOFF-2026-06-10_1800.md).
