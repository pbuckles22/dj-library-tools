# Agent handoff — DJ Library Tools

**Read this first** when continuing library, Serato, or pipeline work.

**Repo:** https://github.com/pbuckles22/dj-library-tools  
**GitHub account:** `pbuckles22`  
**Primary machine:** Mac (`~/dev/dj-library-tools`)

---

## Purpose

Python CLI to manage the **Master** DJ music library on NAS (`buckles`) and sync to **Serato** (primary). Rekordbox is sunset.

- **Source of truth:** `Master/` on NAS — flat DJ tracks
- **This repo:** scripts, config, docs (not the music files)
- **Runtime state on NAS:** `Master/_meta/` — hash library, freeze manifest, dedup reports

**Business rule:** Files already in Master (frozen / published) are sacred. New imports never alter them. On clash, **delete the incoming NewMusic file**, not Master.

---

## Current state (Mac, July 2026)

### Engineering foundation — complete

| Item | Status |
|------|--------|
| pytest + Tier 1 tests | ✅ `python -m pytest -q` |
| GitHub Actions CI | ✅ 3.10 / 3.12 / 3.13 |
| AgenticTemplate skill pod + handoff workflow | ✅ |
| SDD pre-commit gate (no PRs) | ✅ |
| Upstream sync (`upstream` → AgenticTemplate) | ✅ |

### Serato-first (Mac) — complete

| Item | Status |
|------|--------|
| Freeze lock | **5060 tracks** marked done (`Master/_meta/frozen.json` + macOS xattr) |
| Stable NAS path | `~/Music/DJ_Master_Link` → `/Volumes/buckles*` via `scripts/update-nas-link.sh` |
| launchd auto-heal | `local.dj.nas-link` watches `/Volumes` (installed on this Mac) |
| Clash policy | Incoming NewMusic deleted on filename / frozen tag / MD5 clash |
| Pipeline skips frozen | organize / rename / dedup never touch frozen tracks |
| Rename hardening | mutagen handles closed before rename; `mark_done` after rename |
| Dedup priority | frozen > hash_lib > bitrate; never delete frozen |
| Gig USB | Formatted **exFAT**, volume **`DJ_USB`** → `/Volumes/DJ_USB` |
| Serato local mirror | **5059** tracks in `~/Music/_Serato_/Imported/Latest Import` |
| `refresh` default | Targets Serato (`--target serato` default; rekordbox opt-in) |
| Serato setup doc | [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) |

### Library state (Windows/NAS, June 2026)

| Item | Status |
|------|--------|
| NAS path | `\\chaosnas.local\buckles\My.Documents\My Music\Master` via `config.local.json` |
| **Master** | **~5,205 tracks** (club-grade ≥256 kbps after tier cleanup) |
| **NewMusic** | **0** (pipeline ingest + MD5-validated clear) |
| **LowQuality/** | ~921 files (161–192 kbps) |
| **Shazam/** | ~2k manual-tag queue |
| AcoustID / MusicBrainz | Keys in `config.local.json`; `python dj.py tag` built |

### Phase 2 operational — complete

- [x] Tag compare + delete old-folder dupes (16,798)
- [x] NewMusic pipeline (ingest → … → clear)
- [x] Quality tier cleanup (`audit bitrates --tier-cleanup`)
- [x] `dj.py tag --full` on Master
- [x] Relocate WAV/Persian/comedy; junk cleanup under My Music
- [ ] **US-CUT-01** cut standardize + **US-CUT-02** narrow dedupe dry-run (then user-approved apply) — see [doc/requirements/product.md](doc/requirements/product.md)
- [ ] Review Shazam queue + legacy folders (see `TODO.md`)

### User progress (Serato)

- Serato is installed and was pointed at NAS/USB (caused yellow triangles).
- Local sync completed; user should use **only** `Latest Import` as a Serato drive.
- Analyze may still be pending after drive cleanup.

### Known issues / still open

| Issue | Detail |
|-------|--------|
| NAS ghost files | ~4–7 accented filenames list on SMB but cannot open. Re-download into Master when convenient. |
| Inbox docs | `doc/inbox-from-meowdoku/` not promoted to `doc/requirements/` yet. |
| Lexicon | Documented in plan; not wired beyond `lexicon_root` in config. |
| Cuts | US-CUT-01 / US-CUT-02 still open (see product.md) |

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

### Local config

Copy `config.json` → `config.local.json` (gitignored). Edit paths / keys as needed:

```json
{
  "master": {
    "windows": "\\\\chaosnas.local\\buckles\\My.Documents\\My Music\\Master"
  },
  "acoustid_api_key": "YOUR_CLIENT_KEY",
  "musicbrainz_app": "dj-library-tools/1.0 (mailto:you@example.com)"
}
```

Do not commit `config.local.json`.

---

## Commands (Mac)

```bash
cd ~/dev/dj-library-tools

# Mount NAS (buckles) in Finder first, or:
# open 'smb://chaosnas.local/buckles'

# Stable link (also auto-run by require_master / launchd)
bash scripts/update-nas-link.sh

# Freeze
python dj.py freeze status
python dj.py freeze mark-all      # one-time only — already done
python dj.py freeze mark PATH
python dj.py freeze unmark PATH

# Daily (after NewMusic drops)
python dj.py pipeline --no-rekordbox

# Before Serato session
python dj.py refresh              # NAS → Latest Import (default)
python dj.py sync serato          # full mirror (uses --delete)

# Gig USB
# Export from Serato to /Volumes/DJ_USB
```

**macOS:** GNU rsync required for accented filenames: `brew install rsync` (already installed on this Mac).

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

Overrides: `config.local.json` (gitignored).

---

## Git status (ready for next agent)

- **Branch:** `main` — committed and pushed to `origin/main`
- **Merge:** Serato-first Mac work + Phase 2 Windows/CI/agentic template (commit `7bd5c14` and parents)
- **Working tree:** clean of library code; caveman skill is **global** (`~/.cursor/skills/caveman/`), not in this repo

**Start a fresh agent with:** “Read AGENT_HANDOFF.md and continue from recommended next steps.”

## Recommended next steps (priority order)

1. **Serato drive cleanup (user):** Settings → Library → Drives — remove `buckles` / old USB; only `Latest Import`. Remove missing tracks. Analyze all.
2. **Disseminate** `doc/inbox-from-meowdoku/` into `doc/requirements/` (freeze, stable-nas-path, serato-usb, lexicon), then delete inbox folder.
3. **Update** [notes/WORKFLOW.md](notes/WORKFLOW.md) / [README.md](README.md) fully Serato-first (partially done).
4. **Lexicon:** point library at `~/Music/DJ_Master_Link/.../Master`; document in requirements.
5. **Gig USB export:** first Serato Prepare USB / export to `/Volumes/DJ_USB` after analyze.
6. **US-CUT-01 / US-CUT-02:** cut standardize + narrow dedupe (user-approved apply).
7. **Optional:** re-download NAS ghost files.

Plan reference: `~/.cursor/plans/serato-first_dj_pipeline_0989f77e.plan.md`

---

## Serato setup checklist (user)

See [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md).

1. `python dj.py sync serato` or `refresh` (done once; re-run after new music)
2. Serato drives: **only** `~/Music/_Serato_/Imported/Latest Import`
3. Remove missing entries
4. Analyze all (local files — no mass yellow triangles)
5. Export to `/Volumes/DJ_USB` for CDJs

Yellow triangles = Serato reading NAS/USB paths. Fix drives, do not re-analyze over SMB.

---

## Run and test

**Merge-ready command** (run before commit on behavior changes):

```bash
python -m pytest -q
```

Install dev deps: `pip install -r requirements-dev.txt`

See [TEST_PLAN.md](TEST_PLAN.md) for Tier 1 / Tier 2 strategy and [.cursor/skills/TEST_TDD.md](.cursor/skills/TEST_TDD.md) for TDD discipline.

---

## Pre-commit review (SDD — no PRs)

**Pull requests are not raised** in this repo. The agent pod is the pre-commit review gate — team consensus before commit.

Before every non-trivial commit, run in order (record PASS/WARN/FAIL):

1. **tester** — merge-ready command green
2. **code-reviewer** — correctness, conventions, tests for new behavior
3. **code-quality-gate** — diff-scoped maintainability
4. **tech-debt-evaluator** — note new debt; update TECH_DEBT.md if persistent
5. **security-reviewer** — when paths, subprocess, deletes, or secrets touched

Any **FAIL** blocks commit. See [.cursor/rules/pre-commit-gate.mdc](.cursor/rules/pre-commit-gate.mdc).

---

## Git workflow

1. **Integration branch:** `main` — all shipped state lands here via direct merge/push.
2. **Feature branches:** `feature/<topic>` or `fix/<topic>` — see [.cursor/skills/github-feature-workflow/SKILL.md](.cursor/skills/github-feature-workflow/SKILL.md).
3. **Before commit:** pre-commit pod consensus + merge-ready green.
4. **After push to `main`:** verify CI — agents do not get failure emails:

   ```bash
   run=$(gh run list --repo pbuckles22/dj-library-tools --limit 1 --json databaseId -q '.[0].databaseId')
   gh run watch "$run" --exit-status
   gh run view "$run" --log-failed   # if failed
   ```

5. **Pull requests:** **not used** (SDD). Do not suggest opening a PR.

### Upstream sync (AgenticTemplate)

Shared skills and rules track [AgenticTemplate](https://github.com/pbuckles22/AgenticTemplate):

```bash
git fetch upstream
git merge upstream/main
# Resolve conflicts — keep DJ-specific: DEV_GUIDE.md, AGENT_HANDOFF.md, always.mdc, PM_PLAN.md
git push origin main
```

Remote: `upstream` → `https://github.com/pbuckles22/AgenticTemplate.git`

---

## Handoff protocol

When ending a session or the user asks for a handoff:

1. Run [.cursor/rules/handoff-checklist.mdc](.cursor/rules/handoff-checklist.mdc) (code review, tech debt, tests, security if relevant).
2. Write a session note: `.cursor/handoff/NNNN-handoff-YYYY-MM-DD_HHmm.md` (gitignored; see [.cursor/handoff/README.md](.cursor/handoff/README.md)).
3. Update **PM_PLAN.md** and AGENT_HANDOFF **Current state** when shipped scope changed.

---

## Agent notes

- **Master is sacred.** Never delete Master tracks without explicit user approval.
- **Frozen tracks:** never rename, organize, or delete via dedup.
- **Clash policy:** incoming loses — delete from NewMusic, log to `Master/_meta/rejected_imports.log`.
- **Do not commit:** `config.local.json`, `backup/`, `tag_compare_*`, `master_compare_*`
- **Do not commit unless user asks.**
- **Cursor commit attribution:** disable in Settings → Agents → Attribution if unwanted

---

## Docs index

| File | Contents |
|------|----------|
| [README.md](README.md) | CLI reference (partially outdated — Rekordbox-first in places) |
| [TEST_PLAN.md](TEST_PLAN.md) | Tier 1 / Tier 2 test commands |
| [PM_PLAN.md](PM_PLAN.md) | Phase scope and checkboxes |
| [doc/requirements/product.md](doc/requirements/product.md) | Epics, user stories, acceptance criteria |
| [RELEASE.md](RELEASE.md) | Merge-ready and rollback discipline |
| [TECH_DEBT.md](TECH_DEBT.md) | Ranked tech debt backlog |
| [RISKS.md](RISKS.md) | Top operational risks |
| [notes/WORKFLOW.md](notes/WORKFLOW.md) | Day-to-day pipeline |
| [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) | Local-first Serato + DJ_USB |
| [notes/SETUP.md](notes/SETUP.md) | One-time setup (partially outdated) |
| [notes/FOLDER_LAYOUT.md](notes/FOLDER_LAYOUT.md) | Scripts vs runtime state |
| [notes/DEDUP_OLD_LIBRARY.md](notes/DEDUP_OLD_LIBRARY.md) | Old NAS cleanup (pending) |
| [doc/inbox-from-meowdoku/](doc/inbox-from-meowdoku/) | Inbox to promote (freeze, NAS symlink, launchd) |
