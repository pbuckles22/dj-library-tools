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
> Read AGENT_HANDOFF.md and continue from recommended next steps. Prefer Serato UI cleanup (US-SYNC-02) or backlog stories (US-SHAZ-02, US-QUAL-03, US-ENG-*). Do not re-do code→docs inventory or re-apply cuts unless policy changes.

**Handoff procedure always includes:** (1) **caveman** (`/caveman full`), (2) **TDD** (blackbox, test-first). See [.cursor/rules/handoff-checklist.mdc](.cursor/rules/handoff-checklist.mdc).

---

## Mission (read this)

**Cut policy on NAS is done.** US-CUT-01/02 applied; narrow policy is **Intro Clean exists → delete plain Clean only** (Dirty/Acap/etc. kept). Next is Serato UI cleanup.

| Priority | Goal | Definition of done |
|----------|------|--------------------|
| **1** | **User / ops (manual)** | Serato drives: only `Latest Import`; remove missing; analyze all (US-SYNC-02) |
| **2** | **Backlog only if asked** | US-SHAZ-02, US-QUAL-03, US-ENG-* — TDD first |
| **3** | **Keep docs truthful** | Any new public surface gets a US (or internal note) in the same change |

**How to work:**

1. `/caveman full` — stay in caveman unless user says stop.
2. **TDD** — blackbox, outside-in; Tier 1 red → green before production edits ([TEST_TDD.md](.cursor/skills/TEST_TDD.md)).
3. Prefer doc fixes over refactors. Do not expand product scope without a story.
4. Merge-ready: `python -m pytest -q` (coverage optional: `--cov=lib --cov=dj`).

**Not the mission:** Drive-by refactors, committing without the user asking, re-auditing coverage.md, or re-running cuts apply.

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
| `main` on GitHub | ✅ Cut policy (Clean-only narrow) + docs reconcile |
| pytest Tier 1 | ✅ `python -m pytest -q` (153 passed, 1 skipped) |
| Code coverage | ✅ **81%** `lib/` + `dj.py` |
| Requirement matrix | ✅ [doc/requirements/coverage.md](doc/requirements/coverage.md) — every US + every public surface |
| Plans / README | ✅ Serato-first; aligned with product.md |
| GitHub Actions CI | ✅ 3.10 / 3.12 / 3.13 |
| AgenticTemplate skill pod + SDD (no PRs) | ✅ |

### Serato-first (Mac) — implemented

| Item | Status |
|------|--------|
| Freeze lock | Manifest may lag after cuts (~4718 reported; re-freeze if lock count must match live files) |
| Stable NAS path | `~/Music/DJ_Master_Link` → `/Volumes/buckles*` via `scripts/update-nas-link.sh` |
| launchd auto-heal | `local.dj.nas-link` watches `/Volumes` |
| Clash policy | Incoming NewMusic deleted on filename / frozen tag / MD5 clash |
| Pipeline skips frozen | organize / rename / dedup never touch frozen tracks |
| Gig USB | **exFAT**, volume **`DJ_USB`** → `/Volumes/DJ_USB` |
| Serato local mirror | **~4717** tracks in `~/Music/_Serato_/Imported/Latest Import` |
| `refresh` default | `--target serato` |
| Cut policy | US-CUT-01/02 applied; narrow = Intro Clean → delete Clean only |
| Serato setup doc | [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) |

### Prior missions (done — do not re-do)

- Inbox promoted → E09–E12 in product.md
- Blackbox tests for freeze, clash, sync/refresh, pipeline flags, NAS/USB config, cuts, CLI cmds
- US IDs in test names/docstrings; pytest-cov
- **Code → docs inventory:** CLI, lib entry points, scripts mapped in coverage.md
- **US-CUT-01/02 on NAS:** 522 renames; 342 Clean-only deletes; policy narrowed per user (not all cut variants)

### Gaps for next agent

| Gap | Why it matters |
|-----|----------------|
| Serato drive cleanup | Manual UI: only Latest Import; remove missing; analyze |
| ~6 NAS unicode ghosts | Unreadable paths (NFC/NFD); refresh warns; fix by re-copy if needed |
| Freeze manifest lag | Optional: re-freeze after cuts for accurate lock count |
| Backlog stories | Only if user prioritizes (SHAZ-02, QUAL-03, ENG-*) |

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

### A. User / ops (primary)

1. **US-SYNC-02** — Serato drives: only `Latest Import`; remove missing; analyze all; optional gig USB export. Restart Serato after last sync.

### B. Backlog (only if user asks)

2. US-SHAZ-02 (`shazam import`), US-QUAL-03 (`audit transcodes`), US-ENG-* — **TDD first**.
3. If adding a new CLI flag or script: update product.md + coverage.md in the same change.
4. Optional: re-freeze Master if freeze counts must match live files; fix unicode ghost paths on NAS.

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
| Code → docs reconciliation | **100% of public surfaces** | **Done** |

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
- **cuts `--mode strict`:** internal/experimental — not product policy.
- **Do not commit:** `config.local.json`, `backup/`, `tag_compare_*`, `master_compare_*`, `.agents/`, `.coverage`
- **Do not commit unless user asks.**

---

## Docs index

| File | Contents |
|------|----------|
| [doc/requirements/product.md](doc/requirements/product.md) | **Source of truth for requirement coverage** |
| [doc/requirements/coverage.md](doc/requirements/coverage.md) | US ID → test / manual / backlog **+ code surface inventory** |
| [TEST_PLAN.md](TEST_PLAN.md) | Tier 1 / Tier 2 |
| [PM_PLAN.md](PM_PLAN.md) | Phase scope |
| [TODO.md](TODO.md) | Operational checklist (Serato-first) |
| [TECH_DEBT.md](TECH_DEBT.md) | Engineering debt |
| [RISKS.md](RISKS.md) | Operational risks |
| [notes/WORKFLOW.md](notes/WORKFLOW.md) | Day-to-day pipeline |
| [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) | Local-first Serato + DJ_USB |
| [doc/inbox-from-meowdoku/](doc/inbox-from-meowdoku/) | Historical pointer only (promoted) |
| [README.md](README.md) | CLI reference (Serato-first) |

## Epic close (automatic)

When an epic's in-scope work is done, **do not wait for the user to ask**. Run [.cursor/rules/epic-close.mdc](.cursor/rules/epic-close.mdc) / pm-governance *Epic close*: **handoff checklist first**, then mark the epic complete in plan/status docs, close note, commit/push, summarize. See [.cursor/skills/pm-governance/SKILL.md](.cursor/skills/pm-governance/SKILL.md).
