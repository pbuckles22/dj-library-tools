# `doc/gemini/` — transient Gemini exchange folder

**Purpose:** a scratch drop-zone for handing files to an external LLM (Gemini) and bringing its
output back. **Not canonical** — the repo source and tracked docs are the source of truth.

**Conventions** (see [`.cursor/rules/gemini-handoff.mdc`](../../.cursor/rules/gemini-handoff.mdc)):

- **Flat** — no subdirectories.
- **≤ 10 files total** (this `README.md` included). Copy only what's needed.
- **Transient** — wiped and reloaded on each reuse; only this `README.md` persists.
- On "hand off to Gemini", the agent creates this folder if missing and fills it with a context
  Markdown (e.g. `CONTEXT.md`) plus the relevant code files (flattened by base name).

Anything Gemini returns should be folded into canonical code/docs, not left here.
