# Agent handoff — DJ Library Tools

**Read this first.** Then continue from [Mission](#mission-read-this) and [Recommended next steps](#recommended-next-steps-priority-order).

**Repo:** https://github.com/pbuckles22/dj-library-tools  
**GitHub account:** `pbuckles22`  
**Primary machine:** Mac (`~/dev/dj-library-tools`)  
**Branch:** `main` = `origin/main` (latest handoff commit on GitHub)

**Start prompt for a fresh agent:**

> Read AGENT_HANDOFF.md and continue from recommended next steps. Treat the system as a blackbox. Priority is 100% requirement coverage, then ≥80% code coverage.

---

## Mission (read this)

**This whole system is a blackbox.**

Do not optimize for internal elegance, drive-by refactors, or “understanding every module.” Optimize for **observable behavior that matches requirements**.

| Priority | Goal | Definition of done |
|----------|------|--------------------|
| **1** | **100% requirement coverage** | Every user story / acceptance criterion in [doc/requirements/product.md](doc/requirements/product.md) is either **Done** with evidence, or has an **automated test** (or explicit Tier-2/manual checklist entry) that proves the behavior. No orphan requirements. |
| **2** | **≥80% code coverage** | After requirements are fully covered, raise line/branch coverage of `lib/` + `dj.py` to **at least 80%** (pytest-cov). Coverage without requirement mapping is not the goal. |

**How to work (blackbox):**

1. Read requirements in `doc/requirements/product.md` (and promote anything still in `doc/inbox-from-meowdoku/` into requirements first).
2. For each open acceptance criterion: write a test that fails, implement or wire behavior until it passes — **outside-in**.
3. Prefer tests that assert CLI outcomes, file-system effects, and config-resolved paths — not private helpers unless they are the only seam.
4. Map tests → requirement IDs (e.g. `US-CUT-01`) in test names or docstrings.
5. Only after requirement matrix is green: fill gaps to hit **≥80%** code coverage.

**Not the mission:** rewriting Serato/NAS ops for fun, expanding scope beyond requirements, or committing without the user asking.

---

## Purpose (product)

Python CLI to manage the **Master** DJ music library on NAS (`buckles`) and sync to **Serato** (primary). Rekordbox is sunset.

- **Source of truth:** `Master/` on NAS — flat DJ tracks
- **This repo:** scripts, config, docs, tests (not the music files)
- **Runtime state on NAS:** `Master/_meta/` — hash library, freeze manifest, dedup reports

**Business rule:** Files already in Master (frozen / published) are sacred. New imports never alter them. On clash, **delete the incoming NewMusic file**, not Master.

---

## Current state (Mac, July 2026)

### Git / platform

| Item | Status |
|------|--------|
| `main` on GitHub | ✅ Serato-first + Phase 2 merged and pushed (`17fea01` handoff; merge `7bd5c14`) |
| pytest Tier 1 | ✅ `python -m pytest -q` (65 passed, 1 skipped last run) |
| GitHub Actions CI | ✅ 3.10 / 3.12 / 3.13 |
| AgenticTemplate skill pod + SDD (no PRs) | ✅ |
| Caveman skill | Global only: `~/.cursor/skills/caveman/` (not in repo) |

### Serato-first (Mac) — implemented

| Item | Status |
|------|--------|
| Freeze lock | **5060 tracks** (`Master/_meta/frozen.json` + macOS xattr) |
| Stable NAS path | `~/Music/DJ_Master_Link` → `/Volumes/buckles*` via `scripts/update-nas-link.sh` |
| launchd auto-heal | `local.dj.nas-link` watches `/Volumes` (installed on this Mac) |
| Clash policy | Incoming NewMusic deleted on filename / frozen tag / MD5 clash (`lib/staging.py`) |
| Pipeline skips frozen | organize / rename / dedup never touch frozen tracks |
| Rename | mutagen closed before rename; `mark_done` after rename |
| Dedup priority | frozen > hash_lib > bitrate; never delete frozen |
| Gig USB | **exFAT**, volume **`DJ_USB`** → `/Volumes/DJ_USB` |
| Serato local mirror | **5059** tracks in `~/Music/_Serato_/Imported/Latest Import` |
| `refresh` default | `--target serato` (rekordbox opt-in) |
| Serato setup doc | [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) |

### Library state (Windows/NAS, June 2026)

| Item | Status |
|------|--------|
| Master | **~5,205** club-grade tracks (≥256 kbps after tier cleanup) |
| NewMusic | **0** |
| LowQuality / Shazam | ~921 / ~2k |
| AcoustID | Keys in `config.local.json`; `python dj.py tag` built |

### Phase 2 ops — mostly done

- [x] Tag compare + delete old-folder dupes (16,798)
- [x] NewMusic pipeline (ingest → … → clear)
- [x] Quality tier cleanup; tag full; relocate / cleanup
- [ ] **US-CUT-01 / US-CUT-02** — built CLI; NAS run / user-approved apply pending
- [ ] Shazam queue + legacy folder review

### User progress (Serato)

- Serato was pointed at NAS/USB → yellow triangles. Fix: **only** `Latest Import` as a Serato drive (local files).
- Local sync done; analyze may still be pending after drive cleanup.

### Gaps that block 100% requirement coverage

| Gap | Why it matters |
|-----|----------------|
| `doc/inbox-from-meowdoku/` not in `doc/requirements/` | Freeze, NAS symlink, Serato/USB, Lexicon behaviors exist in code/docs but are **not formal requirements** → cannot claim 100% coverage |
| product.md still Rekordbox-first / Serato-paused in places | Requirements lag Serato-first architecture |
| Many acceptance criteria unchecked | Cuts, sync, Shazam, hygiene stories still open |
| Few/no tests for freeze, staging clash, refresh, NAS link, cuts apply paths | Behavior exists; blackbox proof missing |
| Code coverage not measured / below 80% | Secondary goal after requirements |

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

### A. Requirement coverage → 100% (primary)

1. **Inventory requirements** — walk every epic/US in [doc/requirements/product.md](doc/requirements/product.md); build a coverage matrix (US ID → test or manual evidence → status).
2. **Promote inbox** — move `doc/inbox-from-meowdoku/` into `doc/requirements/` (freeze, stable-nas-path, serato-usb, lexicon); delete inbox when done. Update product.md to **Serato-first** (Rekordbox sunset).
3. **Blackbox tests for shipped behavior** — freeze, staging clash policy, pipeline flags, `refresh`/`sync serato`, config NAS link resolution, cuts standardize/dedupe dry-run. Tag each test with US IDs.
4. **Close open acceptance criteria** — US-CUT-01/02 (dry-run then user-approved apply), US-SYNC-*, Shazam/hygiene stories per product.md. Operational NAS steps need user approval for deletes.
5. **Mark Done only with evidence** — checkbox + test name or handoff note with command output.

### B. Code coverage → ≥80% (secondary)

6. Enable `pytest-cov` on `lib/` + `dj.py`; publish baseline in [TEST_PLAN.md](TEST_PLAN.md).
7. Fill gaps **only where requirements already have tests** or where uncovered lines are required for safety (deletes, path resolution).
8. Stop at ≥80% once requirement matrix is complete — do not chase 100% line coverage.

### C. User / ops (parallel, not instead of A)

9. **Serato drive cleanup (user):** only `Latest Import`; remove missing; analyze all.
10. Gig USB export after analyze; optional NAS ghost-file re-download.

Plan reference: `~/.cursor/plans/serato-first_dj_pipeline_0989f77e.plan.md`

---

## Commands (Mac)

```bash
cd ~/dev/dj-library-tools

# Tests (merge-ready)
python -m pytest -q
# After cov is wired:
# python -m pytest -q --cov=lib --cov=dj --cov-report=term-missing

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

**Coverage targets (agent must track):**

| Layer | Target |
|-------|--------|
| Requirements (product.md + promoted inbox) | **100%** |
| Code (`lib/`, `dj.py`) | **≥80%** after requirements |

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

- **Blackbox first.** Requirements → tests → behavior. Code coverage second.
- **Master is sacred.** Never delete Master tracks without explicit user approval.
- **Frozen tracks:** never rename, organize, or delete via dedup.
- **Clash policy:** incoming loses — delete from NewMusic, log to `Master/_meta/rejected_imports.log`.
- **Do not commit:** `config.local.json`, `backup/`, `tag_compare_*`, `master_compare_*`, `.agents/`
- **Do not commit unless user asks.**

---

## Docs index

| File | Contents |
|------|----------|
| [doc/requirements/product.md](doc/requirements/product.md) | **Source of truth for requirement coverage** |
| [TEST_PLAN.md](TEST_PLAN.md) | Tier 1 / Tier 2 |
| [PM_PLAN.md](PM_PLAN.md) | Phase scope |
| [TODO.md](TODO.md) | Operational checklist |
| [TECH_DEBT.md](TECH_DEBT.md) | Engineering debt |
| [RISKS.md](RISKS.md) | Operational risks |
| [notes/WORKFLOW.md](notes/WORKFLOW.md) | Day-to-day pipeline |
| [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) | Local-first Serato + DJ_USB |
| [doc/inbox-from-meowdoku/](doc/inbox-from-meowdoku/) | **Promote into requirements** (freeze, NAS, Serato/USB) |
| [README.md](README.md) | CLI reference (partially outdated) |
