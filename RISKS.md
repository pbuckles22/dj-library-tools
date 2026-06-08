# Risks — DJ Library Tools

Top operational risks (impact / trigger / mitigation).

| Risk | Impact | Trigger | Mitigation |
|------|--------|---------|------------|
| Accidental Master deletion | High | Running delete scripts without review | Never delete from Master without explicit user approval; review `tag_compare_not_in_master.txt` |
| Stale DJ app mirrors | Medium | Sync skipped after pipeline | Run `python dj.py sync all`; restart Serato/Rekordbox |
| NAS unreachable | Medium | Drive letter unmapped on Windows | Verify with `python dj.py dedup --days 1`; use `config.local.json` |
| Tag compare false negatives | Medium | Missing or bad ID3 tags | Review no-tags report; prefer tag compare over MD5 for re-tagged files |
| Hash library corruption | Low | Interrupted dedup write | Backup `Master/_meta/hash_library.json` to `backup/` after full dedup |
