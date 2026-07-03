# Handoff (optional)

Session handoff narratives often live in **`NNNN-HANDOFF-YYYY-MM-DD_HHmm.md`** files here (legacy: `HANDOFF-*.md`) or under **`.cursor/handoff/`** as **`NNNN-handoff-YYYY-MM-DD_HHmm.md`**. Those patterns are **gitignored** by default (see root `.gitignore`) so local session notes are not pushed.

If you need a **tracked** file in this folder (e.g. contributor setup), add it and use a `.gitignore` exception so it is not matched by `HANDOFF-*.md` / `*-HANDOFF-*.md`.

Product state belongs in **PM_PLAN.md** and your product plan under **`doc/plan/`** (or equivalent), not only in handoff notes.
