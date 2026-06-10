# PM_PLAN — DJ Library Tools

## Current phase

**Phase 3 — Metadata & cut policy** (June 2026)

- [x] `dj.py tag` (AcoustID); pipeline tag step
- [x] NewMusic ingest + validated clear in pipeline
- [x] Quality tiers (`audit bitrates --tier-cleanup`)
- [x] Master ~5,205 club tracks; NewMusic cleared
- [ ] **Cut standardize** — intro aliases → `Intro Clean`
- [ ] **Cut dedupe narrow** — dry-run then user-approved apply
- [ ] Shazam manual queue; legacy folder review (`TODO.md`)

**Phase 2 — Operational cleanup** — **complete**

- [x] Delete confirmed dupes from old NAS folders (16,798)
- [x] Pipeline + Rekordbox sync
- [x] Relocate / cleanup helpers

## Engineering (ongoing)

- [x] Windows UTF-8 fixes (0477a62)
- [x] Tier 1 tests: 57 passing
- [ ] Tier 2 pipeline integration tests
- [ ] ruff/format gate

## Next

See [AGENT_HANDOFF.md](AGENT_HANDOFF.md) and [doc/handoff/0003-HANDOFF-2026-06-10_1800.md](doc/handoff/0003-HANDOFF-2026-06-10_1800.md).
