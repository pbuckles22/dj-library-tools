# Agent handoff — DJ Library Tools

**Read this first.** Then continue from [Mission](#mission-read-this) and [Recommended next steps](#recommended-next-steps-priority-order).

**Repo:** https://github.com/pbuckles22/dj-library-tools  
**GitHub account:** `pbuckles22`  
**Primary machine:** Mac (`~/dev/dj-library-tools`)  
**Branch:** `main` = `origin/main` (latest handoff commit on GitHub)

**Start prompt for a fresh agent:**

> `/caveman full`
>
> Blackbox testing. TDD (TEST_TDD.md + tester skill: red → green before production changes).
>
> Read AGENT_HANDOFF.md and continue from recommended next steps. Walk all code (`lib/`, `dj.py`, `scripts/`) and reconcile into plan + requirements so the repo has a clean starting point — no behavior that exists only in code.

**Handoff procedure always includes:** (1) **caveman** (`/caveman full`), (2) **TDD** (blackbox, test-first). See [.cursor/rules/handoff-checklist.mdc](.cursor/rules/handoff-checklist.mdc).

---

## Mission (read this)

**Reconcile code → plan / requirements (clean starting point).**

Prior session finished requirement-matrix coverage and ≥80% line coverage. Next work is the **inverse audit**: every public behavior in code must appear in durable docs (product requirements, PM_PLAN, TEST_PLAN, coverage matrix). No “secret” CLI flags, policies, or scripts that only live in source.

| Priority | Goal | Definition of done |
|----------|------|--------------------|
| **1** | **Code → docs inventory** | Walk `dj.py` subcommands, `lib/*.py` public entry points, and `scripts/`. For each behavior: linked US ID in [doc/requirements/product.md](doc/requirements/product.md) **or** new story added **or** explicit “internal/no product surface” note. |
| **2** | **Plans match reality** | [PM_PLAN.md](PM_PLAN.md), [TODO.md](TODO.md), [TEST_PLAN.md](TEST_PLAN.md), [README.md](README.md) Serato-first and consistent with product.md. No Rekordbox-primary leftovers. |
| **3** | **Coverage matrix stays truthful** | [doc/requirements/coverage.md](doc/requirements/coverage.md) lists every US; tests still map to US IDs. Add stories/tests only via **TDD** (failing test first). |

**How to work:**

1. `/caveman full` — stay in caveman unless user says stop.
2. **TDD** — blackbox, outside-in; Tier 1 red → green before production edits ([TEST_TDD.md](.cursor/skills/TEST_TDD.md)).
3. Inventory code first (CLI + lib public APIs + scripts), then patch requirements/plans — not the other way around this session.
4. Prefer doc fixes over refactors. Do not expand product scope.
5. Merge-ready: `python -m pytest -q` (coverage optional: `--cov=lib --cov=dj`).

**Not the mission:** NAS cut apply, Serato UI cleanup, drive-by refactors, or committing without the user asking.

---

## Purpose (product)

Python CLI to manage the **Master** DJ music library on NAS (`buckles`) and sync to **Serato** (primary). Rekordbox is sunset / opt-in.

- **Source of truth:** `Master/` on NAS — flat DJ tracks
- **This repo:** scripts, config, docs, tests (not the music files)
- **Runtime state on NAS:** `Master/_meta/` — hash library, freeze manifest, dedup reports

**Business rule:** Files already in Master (frozen / published) are sacred. New imports never alter them. On clash, **delete the incoming NewMusic file**, not Master.

---

## Current state (Mac, July 2026)

### Git / platform

| Item | Status |
|------|--------|
| `main` on GitHub | ✅ Blackbox requirements + coverage mission shipped |
| pytest Tier 1 | ✅ `python -m pytest -q` (152 passed, 1 skipped) |
| Code coverage | ✅ **81%** `lib/` + `dj.py` |
| Requirement matrix | ✅ [doc/requirements/coverage.md](doc/requirements/coverage.md) — every US mapped auto/manual/backlog |
| GitHub Actions CI | ✅ 3.10 / 3.12 / 3.13 |
| AgenticTemplate skill pod + SDD (no PRs) | ✅ |

### Serato-first (Mac) — implemented

| Item | Status |
|------|--------|
| Freeze lock | **5060 tracks** (`Master/_meta/frozen.json` + macOS xattr) |
| Stable NAS path | `~/Music/DJ_Master_Link` → `/Volumes/buckles*` via `scripts/update-nas-link.sh` |
| launchd auto-heal | `local.dj.nas-link` watches `/Volumes` |
| Clash policy | Incoming NewMusic deleted on filename / frozen tag / MD5 clash |
| Pipeline skips frozen | organize / rename / dedup never touch frozen tracks |
| Gig USB | **exFAT**, volume **`DJ_USB`** → `/Volumes/DJ_USB` |
| Serato local mirror | **~5059** tracks in `~/Music/_Serato_/Imported/Latest Import` |
| `refresh` default | `--target serato` |
| Serato setup doc | [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) |

### Prior mission (done — do not re-do)

- Inbox promoted → E09–E12 in product.md
- Blackbox tests for freeze, clash, sync/refresh, pipeline flags, NAS/USB config, cuts, CLI cmds
- US IDs in test names/docstrings
- pytest-cov in requirements-dev.txt

### Gaps for next agent (code → docs)

| Gap | Why it matters |
|-----|----------------|
| Not every `lib/` / `dj.py` surface audited against product.md | Behavior may exist only in code (relocate, audit flags, pull, compare outputs, etc.) |
| PM_PLAN / TODO / README may still lag Serato-first | Clean starting point needs one story |
| Manual NAS ops still open | US-CUT-01/02 apply, Serato drive cleanup — user, not agent-only |

---

## Architecture (do not break)

```text
NewMusic (NAS)
    │  clash? → delete incoming, keep Master
    ▼
Master (NAS) ── freeze lock on published tracks
   │
   ├── python dj.py sync serato / refresh
   ▼
~/Music/_Serato_/Imported/Latest Import   ← Serato library root ONLY
   │
   ├── Serato analyze / prep
   ▼
/Volumes/DJ_USB   ← Serato export for CDJs (never library source)

Stable NAS access: ~/Music/DJ_Master_Link → /Volumes/buckles*
```

**Never** point Serato or Lexicon at `/Volumes/buckles` or the gig USB as the music library source.

---

## Recommended next steps (priority order)

### A. Code → requirements / plan reconciliation (primary)

1. **Inventory CLI** — list every `dj.py` subcommand and flag from `build_parser()` / help text.
2. **Inventory lib** — public functions used by CLI (and scripts under `scripts/`).
3. **Diff vs product.md** — for each behavior: existing US ID, or add story, or mark internal-only in coverage.md.
4. **Align plans** — update PM_PLAN.md, TODO.md, README.md, TEST_PLAN.md so Serato-first and stories match code.
5. **TDD only if behavior missing** — if docs claim behavior code lacks, write failing blackbox test first, then implement.

### B. User / ops (parallel, not instead of A)

6. **US-CUT-01/02 on NAS** — dry-run → review → user-approved apply.
7. **Serato drive cleanup (user):** only `Latest Import`; remove missing; analyze all.
8. Gig USB export after analyze.

---

## Commands (Mac)

```bash
cd ~/dev/dj-library-tools

# Tests (merge-ready)
python -m pytest -q
python -m pytest -q --cov=lib --cov=dj --cov-report=term-missing

# Stable NAS link (also auto-run by require_master / launchd)
bash scripts/update-nas-link.sh

# Freeze
python dj.py freeze status

# Daily after NewMusic drops
python dj.py pipeline --no-rekordbox

# Before Serato session
python dj.py refresh
python dj.py sync serato
```

**macOS:** GNU rsync for accented filenames: `brew install rsync`.

---

## Config paths (`config.json`)

| Key | Mac path |
|-----|----------|
| `nas_volume` | `buckles` |
| `master` | `~/Music/DJ_Master_Link/My.Documents/My Music/Master` |
| `newmusic` | `~/Music/DJ_Master_Link/My.Documents/My Music/NewMusic` |
| `serato_latest_import` | `~/Music/_Serato_/Imported/Latest Import` |
| `gig_usb` | `/Volumes/DJ_USB` |
| `lexicon_root` | same as Master via `DJ_Master_Link` |
| `rekordbox_music` | `~/Music/RekordboxMusic` (legacy) |

Overrides: `config.local.json` (gitignored). AcoustID keys live there on Windows.

---

## Serato setup checklist (user)

See [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md).

1. `python dj.py sync serato` or `refresh`
2. Serato drives: **only** `~/Music/_Serato_/Imported/Latest Import`
3. Remove missing entries
4. Analyze all (local — no mass yellow triangles)
5. Export to `/Volumes/DJ_USB` for CDJs

Yellow triangles = Serato reading NAS/USB paths. Fix drives; do not re-analyze over SMB.

---

## Run and test

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

See [TEST_PLAN.md](TEST_PLAN.md) and [.cursor/skills/TEST_TDD.md](.cursor/skills/TEST_TDD.md).

**Coverage targets:**

| Layer | Target | Status |
|-------|--------|--------|
| Requirements (product.md + matrix) | **100% mapped** | Done |
| Code (`lib/`, `dj.py`) | **≥80%** | Done (81%) |
| Code → docs reconciliation | **100% of public surfaces** | **Next** |

---

## Pre-commit review (SDD — no PRs)

PRs are **not** used. Agent pod is the pre-commit gate.

Before non-trivial commits (when user asks to commit):

1. **tester** — merge-ready green
2. **code-reviewer**
3. **code-quality-gate**
4. **tech-debt-evaluator**
5. **security-reviewer** — paths, subprocess, deletes, secrets

Any **FAIL** blocks commit. See [.cursor/rules/pre-commit-gate.mdc](.cursor/rules/pre-commit-gate.mdc).

After push to `main`:

```bash
run=$(gh run list --repo pbuckles22/dj-library-tools --limit 1 --json databaseId -q '.[0].databaseId')
gh run watch "$run" --exit-status
```

---

## Agent notes

- **Caveman + TDD on every session** (handoff procedure requires both).
- **Blackbox first.** Observable behavior; map to US IDs.
- **Master is sacred.** Never delete Master tracks without explicit user approval.
- **Frozen tracks:** never rename, organize, or delete via dedup.
- **Clash policy:** incoming loses — delete from NewMusic, log to `Master/_meta/rejected_imports.log`.
- **Do not commit:** `config.local.json`, `backup/`, `tag_compare_*`, `master_compare_*`, `.agents/`, `.coverage`
- **Do not commit unless user asks.**

---

## Docs index

| File | Contents |
|------|----------|
| [doc/requirements/product.md](doc/requirements/product.md) | **Source of truth for requirement coverage** |
| [doc/requirements/coverage.md](doc/requirements/coverage.md) | US ID → test / manual / backlog |
| [TEST_PLAN.md](TEST_PLAN.md) | Tier 1 / Tier 2 |
| [PM_PLAN.md](PM_PLAN.md) | Phase scope (may lag — reconcile) |
| [TODO.md](TODO.md) | Operational checklist (may lag — reconcile) |
| [TECH_DEBT.md](TECH_DEBT.md) | Engineering debt |
| [RISKS.md](RISKS.md) | Operational risks |
| [notes/WORKFLOW.md](notes/WORKFLOW.md) | Day-to-day pipeline |
| [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) | Local-first Serato + DJ_USB |
| [doc/inbox-from-meowdoku/](doc/inbox-from-meowdoku/) | Historical pointer only (promoted) |
| [README.md](README.md) | CLI reference (may lag — reconcile) |
