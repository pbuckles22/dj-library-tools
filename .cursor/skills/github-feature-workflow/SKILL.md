---
name: github-feature-workflow
description: >-
  Short-lived feature branches; TDD + lint + merge-ready command as exit criteria before
  commit; push and merge to main (or user-directed flow). Do not default to
  asking the user to open a PR. Use when implementing a feature or non-trivial
  fix, when the user asks for branch/git workflow, or after substantial edits
  that should not stay uncommitted.
---

# Git / GitHub feature branch workflow

**Policy in this template:** [AGENT_HANDOFF.md](../../AGENT_HANDOFF.md) — `main` is the integration branch; the **merge-ready command** is the quality bar. This skill defines **how work is finished**: tests (TDD where the tier applies), lint, format, merge-ready green, then **commit** (and **push** per AGENT_HANDOFF). **Pull requests are not part of the default exit** for this template unless the user explicitly asks for a PR or GitHub-based review.

## Do not prompt for PRs (agents)

- **Do not** tell the user to "open a PR," paste `github.com/.../pull/new/...` links, or treat opening a PR as the normal end-of-task step.
- **Do** treat **green merge-ready command** plus project test discipline ([tester](../tester/SKILL.md), [TEST_TDD.md](../TEST_TDD.md), [code-quality-gate](../code-quality-gate/SKILL.md) when relevant) as **merge-ready / commit-ready**.
- **If** the user says they want a PR, GitHub review, or external reviewers: then describe or open the PR as they asked.

**Completion mental model:** one branch ≈ one purpose → merge-ready green → **commit** → **push** → merge to `main` (locally or via GitHub **only if the user uses that path**) → delete the feature branch. No roundabout "please open a PR" unless they chose that path.

## When to apply

- User asks for a **feature branch**, **commit**, **push**, or **merge** (or explicitly **PR**).
- A **coherent slice** of work is done (e.g. one epic story, one bugfix) and should be **recorded in git** before the session ends.
- **Do not** create branches for one-line typo fixes unless the user wants it.

## Branch naming

- Prefer: `feature/<short-kebab-topic>` (e.g. `feature/epic-10-3-pause-keys`) or `fix/<issue-or-topic>`.
- Avoid ultra-long names; include epic/story id if it helps **PM_PLAN** / roadmap traceability.

## Branch-first rule (agents)

- **Do not** stack substantial implementation on **`main`** and only then create a feature branch to "check in." That bypasses a proper branch history and the CI-before-commit discipline.
- **Do** start each non-trivial slice on a **new branch**: `git fetch origin`, `git checkout main`, `git pull`, `git checkout -b feature/<topic>`, then implement, run merge-ready, commit, push, merge to `main` per [Standard sequence](#standard-sequence) (no default PR step).
- If work already landed on **`main`** without a branch, recover discipline going forward; optionally **`git checkout -b feature/<topic>`** from **`main`** before the _next_ slice so new commits are branch-first.

## Exit criteria before commit (ship bar)

Treat these as satisfied **before** `git commit` on anything beyond trivial doc typos (adjust if the user narrows scope):

1. **TDD / tests** — [TEST_TDD.md](../TEST_TDD.md) + [tester](../tester/SKILL.md): failing test first when the changed surface is covered by Tier 1 or Tier 2; suite green for what you touched.
2. **Lint + format** — covered by your merge-ready command (linter, Prettier/formatter check).
3. **Full merge-ready** — your project's merge-ready command green (tests, build, E2E if applicable).
4. **Quality** — For non-trivial edits, use [code-quality-gate](../code-quality-gate/SKILL.md) as appropriate (readability, complexity, obvious foot-guns).

When 1–4 are green: **commit** (and **push** when integrating to `main` per AGENT_HANDOFF). That is the **done** state — not "waiting for the user to open a PR."

## Pre-checkin and pre-next-feature checks

- **Before commits** that change behavior or tests (not one-line doc typos): run your **merge-ready command** — same gate as [AGENT_HANDOFF.md](../../AGENT_HANDOFF.md) for **`main`**.
- **Before merging** to **`main`**: merge-ready green on the feature branch.
- **Before starting the next feature** after a merged story: run merge-ready on updated **`main`** (`git checkout main && git pull`) so Tier 1 + Tier 2 still pass against **origin/main** before new work begins (catches drift if the final gate was skipped).

## Standard sequence

1. **Start from current `main` (or agreed base):** `git fetch origin` when remote exists; `git status` (clean or intentional WIP).
2. **Create branch:** `git checkout -b <name>` — **before** writing production code for the slice.
3. **Implement** with tests as required by [tester skill](../tester/SKILL.md) and [TEST_TDD.md](../TEST_TDD.md) (**red → green** when that tier applies).
4. **Gate before commit:** meet **[Exit criteria before commit](#exit-criteria-before-commit-ship-bar)**; your merge-ready command is the all-in-one gate here.
5. **Commit:** clear, imperative subject line; body only if context helps (what/why, not noise). One logical commit per slice is fine; multiple small commits are fine if they tell a story.
6. **Push:** `git push -u origin <branch>` (first time); later `git push` on that branch.
7. **Integrate to `main`:** Prefer what the user asked for: **local merge** (`git checkout main && git pull && git merge <branch> && [merge-ready] && git push origin main`) when they want work on `main` without a PR, or **they** handle GitHub merge if they use the web UI. **Do not** nudge them toward opening a PR by default.
8. **After merge to `main`:** checkout `main`, `git pull`, **delete the local feature branch** (`git branch -d <branch>`). Delete remote: `git push origin --delete <branch>` when the user wants the remote branch removed.
9. **Update product state** if scope shipped: [PM_PLAN.md](../../PM_PLAN.md) and your product plan — not only git history.

**PR (explicit opt-in only):** If and only if the user asked for a PR or GitHub review, add a PR with a short title and note merge-ready green. Otherwise skip PR language entirely.

## What this skill does _not_ do

- Replace **code review** or **handoff** — see [AGENT_HANDOFF.md](../../AGENT_HANDOFF.md) and `.cursor/rules/handoff-checklist.mdc` when the user wants a handoff.
- **Invent a PR step** — PRs are not the default completion signal; **merge-ready + commit (+ push/merge per user)** is.
