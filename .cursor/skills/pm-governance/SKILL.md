---
name: pm-governance
description: >-
  Project management and governance. Use when planning sprints, making scope
  decisions, enforcing quality gates, identifying risks, or closing an epic.
  Epic close runs automatically when an epic is done — do not wait for the user to ask.
---

# PM governance — Project

Use this skill when doing sprint planning, scope tradeoffs, quality gates, risk mitigation, or **epic close**. Keep in sync with doc/requirements/ if present.

---

## Tactical oversight

- **Risk mitigation:** Identify blocking dependencies or risks early.
- **Scope management:** Focus on MVP first; when adding scope, note whether it's MVP or later.
- **Quality gates:** Define what "done" means (e.g. tests green, coverage, no known blockers).

## Communication

- **Developer sync:** Flag performance or architecture risks (e.g. UI thread load).
- **UX/requirements:** Point to doc/requirements/ or DESIGN_SYSTEM when UX is in scope.

## When to apply

- User asks for sprint planning, scope review, or "what's MVP."
- Deciding whether a feature belongs in current vs next sprint.
- Before marking a build or feature "done."
- **Whenever an epic’s in-scope acceptance is met** — run [Epic close](#epic-close-automatic) without waiting to be asked.

## Output

- **Scope:** Clear MVP vs later; which sprint a change belongs to.
- **Risks:** Listed with mitigation.
- **Quality:** Gates stated; link to PM_PLAN.md and doc/requirements/.
- **Epic close:** Status docs updated + short close summary for the user.

---

## Epic close (automatic)

**Policy:** When the last in-scope story of an epic is done (acceptance met, cuts recorded, Tier 1 green, applicable Tier 2 smoke done), **run this procedure in the same session**. Do not wait for “please close the epic.” See [.cursor/rules/epic-close.mdc](../../rules/epic-close.mdc).

### Done means

- In-scope features in `PM_PLAN.md` / product plan / epics docs are checked or explicitly **cut**.
- Merge-ready gate from `AGENT_HANDOFF.md` was green for the closing work.
- Applicable Tier 2 checklist items for that epic are checked (or N/A / cut).

### Procedure (do all)

1. **Handoff-checklist gates** — Run [.cursor/rules/handoff-checklist.mdc](../../rules/handoff-checklist.mdc) for the epic’s shipped surface: code review, tech debt, tests/coverage, security when relevant, Tier 2 if needed. Record PASS/WARN/FAIL and results in the close note. **Do not skip.**
2. **PM_PLAN** — Mark the phase/epic **Status: complete** (date). Move leftover non-epic items to the next phase or backlog.
3. **Product / epics doc** — One-line epic status (`**Status:** complete — YYYY-MM-DD`) when you maintain that file.
4. **doc/PROJECT_STATUS.md** + **AGENT_HANDOFF.md** ? *Current state* — epic closed; **Next** = next phase only (do not invent work).
5. **TEST_PLAN / TECH_DEBT / RISKS** — Align with closed scope; promote persistent debt into `TECH_DEBT.md`.
6. **README** — One-line product state if the public blurb is stale.
7. **Local handoff / close note** — required; include review, debt, tests, close results (same sections as handoff).
8. **Commit + push** per github-feature-workflow / `AGENT_HANDOFF.md`.
9. **Summarize for the user** — dual-audience close results. Do **not** start the next epic’s implementation unless the user already asked.

### Do not auto-do on close

- Start next-epic code unless directed.
- Retire deferred prototypes / dual trees unless the user or plan **Next** says so.
- Re-open cut features.