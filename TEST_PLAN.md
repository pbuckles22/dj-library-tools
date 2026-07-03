# Test plan (TEST_PLAN.md)

Two-tier test strategy for the DJ Library Tools Python CLI.

**Requirement matrix:** [doc/requirements/coverage.md](doc/requirements/coverage.md) — every US mapped (auto / manual / backlog) **and** every public code surface (`dj.py`, `lib/` CLI entry points, `scripts/`) linked to a US or marked internal.

---

## Tier 1: Fast feedback

Blackbox tests for public behavior in `lib/` + CLI (`dj.py`) — freeze, clash policy, cuts, sync/refresh/pull, config paths, pipeline flags, cleanup, relocate, audit.

```bash
python -m pytest -q
```

Install dev deps once:

```bash
pip install -r requirements-dev.txt
```

### Code coverage

Target: **≥80%** line coverage on `lib/` + `dj.py`.

```bash
python -m pytest -q --cov=lib --cov=dj --cov-report=term-missing
```

Current (2026-07-03): **81%** total. Do not chase 100% line coverage.

### Code → docs

Public surfaces are inventoried in [coverage.md](doc/requirements/coverage.md). Prefer doc fixes when behavior already exists; use TDD only when implementing a documented gap.

---

## Tier 2: Integration

Use when behavior spans real filesystem I/O, subprocess calls (robocopy/rsync), or mutagen tag reads on sample audio.

```bash
python -m pytest -q -m integration
```

(No integration tests yet — add under `tests/` with `@pytest.mark.integration` when needed.)

---

**Handoff:** Merge-ready command is Tier 1 only for now. Document any new Tier 2 commands here and in AGENT_HANDOFF.md.
