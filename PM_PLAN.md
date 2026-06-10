# PM_PLAN — DJ Library Tools

## Current phase

**Phase 2 — Operational cleanup** (June 2026) — **mostly complete**

- [x] Delete confirmed dupes from old NAS folders (16,798 deleted, user confirmed)
- [x] Import NewMusic → Master (727 files via robocopy)
- [x] Run pipeline on Master (rename, dedup, sync Rekordbox)
- [x] Re-sync RekordboxMusic
- [ ] Review 1,951 old-folder “not in Master” files
- [ ] AcoustID tag sweep (`dj.py tag` — not built yet; ~681 untagged in Master)

**Phase 3 — Metadata enrichment** (next)

- [ ] `python dj.py tag` (AcoustID → MusicBrainz → mutagen)
- [ ] Wire tag into pipeline before rename
- [ ] Rekordbox-only default (Serato paused)

## Engineering (ongoing)

- [x] Windows UTF-8 fixes for compare/dedup/rename/sync (handoff 0002)

## Next

See [AGENT_HANDOFF.md](AGENT_HANDOFF.md) → Current state and Recommended next steps.

Keep this file in sync with AGENT_HANDOFF when shipped scope changes.
