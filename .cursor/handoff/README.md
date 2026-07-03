# Handoff notes

**Committed in this repo:** `_template.md` and this README — no secrets.

**Session narratives (usually gitignored):**

- **`doc/handoff/NNNN-HANDOFF-YYYY-MM-DD_HHmm.md`** — optional naming for dated session notes (monotonic `NNNN`).
- **`.cursor/handoff/NNNN-handoff-YYYY-MM-DD_HHmm.md`** — alternative location (monotonic `NNNN`).

**Naming rules (do not overwrite history):**

- **`NNNN`**: zero-padded monotonic serial (**0001**, **0002**, …) that always increases.
- **`YYYY-MM-DD_HHmm`**: local timestamp in 24h time.
- **Never reuse** an `NNNN` and **never edit** a previous handoff file in place—append a new file.

**Pick the next serial (PowerShell) — `.cursor/handoff/`:**

```powershell
$dir = Join-Path $PSScriptRoot '.'
$next = 1
Get-ChildItem -LiteralPath $dir -Filter '*-handoff-*.md' -File -ErrorAction SilentlyContinue |
  ForEach-Object {
    if ($_.Name -match '^(\d{4})-handoff-\d{4}-\d{2}-\d{2}_\d{4}\.md$') {
      [int]$n = $matches[1]
      if ($n -ge $next) { $next = $n + 1 }
    }
  }
'{0:0000}-handoff-YYYY-MM-DD_HHmm.md' -f $next
```

See [`.gitignore`](../.gitignore). If you need a **tracked** contributor guide under `doc/handoff/`, add the file and use a `.gitignore` exception (`!doc/handoff/YourFile.md`) so it is not ignored by the `HANDOFF-*` pattern.

**Product state on `main`:** [PM_PLAN.md](../../PM_PLAN.md) and your product plan doc (e.g. under `doc/plan/`) if you use one. **Process and commands:** this file and [AGENT_HANDOFF.md](../../AGENT_HANDOFF.md).

Run the handoff checklist (`.cursor/rules/handoff-checklist.mdc`) before writing a handoff note.
