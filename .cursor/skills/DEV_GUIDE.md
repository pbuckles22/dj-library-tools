# DEV_GUIDE — DJ Library Tools

## Stack

- **Python 3.10+** — stdlib CLI (`argparse`), no web framework
- **mutagen** — audio tag reading and bitrate detection
- **pytest** — Tier 1 unit tests

## Repo layout

```
dj.py              CLI entry point (argparse subcommands)
lib/
  config.py        Config load/merge, path resolution
  organize.py      Move non-audio files to _meta
  rename.py        Rename to "Artist - Title.ext"
  dedup.py         MD5 dedup, hash library cache
  sync.py          rsync (mac) / robocopy (windows)
  compare.py       Tag-based or MD5 compare vs Master
config.json        Committed defaults (mac/windows paths)
config.local.json  Gitignored machine overrides
tests/             Tier 1 unit tests
notes/             Operational docs (workflow, setup)
```

Imports: `dj.py` adds repo root to `sys.path`; pytest uses `pythonpath = ["."]` in `pyproject.toml`.

## Conventions

- Prefer **pure functions** in `lib/` for logic that can be unit-tested without NAS paths.
- **Config:** never commit `config.local.json`; runtime state lives on NAS in `Master/_meta/`.
- **Platform:** use `{mac, windows}` dicts in config; `_resolve()` picks the active key.
- **I/O boundaries:** organize, sync, and full dedup/compare scan real directories — mock or use `tmp_path` in tests.
- **Safety:** Master is source of truth; destructive ops require explicit user approval.

## Commands

```powershell
pip install -r requirements.txt          # runtime
pip install -r requirements-dev.txt      # + pytest
python dj.py pipeline                    # daily workflow
python -m pytest -q                      # Tier 1 tests
```

See AGENT_HANDOFF.md for Windows NAS paths and operational workflow.
