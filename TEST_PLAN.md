# Test plan (TEST_PLAN.md)

Two-tier test strategy for the DJ Library Tools Python CLI.

---

## Tier 1: Fast feedback

Unit tests for pure helpers in `lib/` — config path resolution, compare normalization, rename safe filenames, dedup hashing.

```powershell
python -m pytest -q
```

Install dev deps once:

```powershell
pip install -r requirements-dev.txt
```

---

## Tier 2: Integration

Use when behavior spans real filesystem I/O, subprocess calls (robocopy/rsync), or mutagen tag reads on sample audio.

```powershell
python -m pytest -q -m integration
```

(No integration tests yet — add under `tests/` with `@pytest.mark.integration` when needed.)

---

**Handoff:** Merge-ready command is Tier 1 only for now. Document any new Tier 2 commands here and in AGENT_HANDOFF.md.
