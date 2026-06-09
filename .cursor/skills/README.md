# Project skills

All agent skills and source-of-truth docs live here.

| Item | Path | When to use |
|------|------|-------------|
| **DEV_GUIDE** | [DEV_GUIDE.md](DEV_GUIDE.md) | Tech stack, architecture, repo layout, conventions. |
| **TEST_TDD** | [TEST_TDD.md](TEST_TDD.md) | What to test; TDD. |
| **DESIGN_SYSTEM** | [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) | Visuals, motion, haptics (N/A for CLI; placeholder). |
| **techwriter** | [techwriter/SKILL.md](techwriter/SKILL.md) | Editing README, AGENT_HANDOFF, or internal docs. |
| **tester** | [tester/SKILL.md](tester/SKILL.md) | Adding or changing tests; run pytest; black-box only. |
| **green-and-clean** | [green-and-clean/SKILL.md](green-and-clean/SKILL.md) | Operating model: no guessing, bounded scope, verifiable steps. |
| **context-bootstrapper** | [context-bootstrapper/SKILL.md](context-bootstrapper/SKILL.md) | Receiving-agent bootstrap: minimal read order + receiver brief. |
| **session-summarizer** | [session-summarizer/SKILL.md](session-summarizer/SKILL.md) | Leaving-agent compression: decisions-first handoffs. |
| **tech-debt-evaluator** | [tech-debt-evaluator/SKILL.md](tech-debt-evaluator/SKILL.md) | Assessing tech debt; refactor/sprint planning. |
| **code-reviewer** | [code-reviewer/SKILL.md](code-reviewer/SKILL.md) | Pre-commit review: correctness, conventions, tests. |
| **code-quality-gate** | [code-quality-gate/SKILL.md](code-quality-gate/SKILL.md) | Pre-commit: diff-scoped maintainability and anti-spaghetti. |
| **tech-lead** | [tech-lead/SKILL.md](tech-lead/SKILL.md) | Sequencing work, definition of done, risks. |
| **eval-engineer** | [eval-engineer/SKILL.md](eval-engineer/SKILL.md) | Acceptance criteria (make “green” objective). |
| **risk-manager** | [risk-manager/SKILL.md](risk-manager/SKILL.md) | Risk register; see [RISKS.md](../../RISKS.md). |
| **release-manager** | [release-manager/SKILL.md](release-manager/SKILL.md) | Merge-ready/release discipline; see [RELEASE.md](../../RELEASE.md). |
| **security-reviewer** | [security-reviewer/SKILL.md](security-reviewer/SKILL.md) | Pre-commit when paths, subprocess, deletes, or secrets touched. |
| **incident-triager** | [incident-triager/SKILL.md](incident-triager/SKILL.md) | Evidence-driven incident/debug workflow. |
| **pm-governance** | [pm-governance/SKILL.md](pm-governance/SKILL.md) | Sprint planning, scope, quality gates. |
| **ui-ux** | [ui-ux/SKILL.md](ui-ux/SKILL.md) | N/A for CLI (placeholder from upstream). |
| **game-readiness** | [game-readiness/SKILL.md](game-readiness/SKILL.md) | N/A for CLI (placeholder from upstream). |
| **visual-match** | [visual-match/SKILL.md](visual-match/SKILL.md) | N/A for CLI (placeholder from upstream). |
| **github-feature-workflow** | [github-feature-workflow/SKILL.md](github-feature-workflow/SKILL.md) | Feature branch → pod consensus → commit → push to `main` (**no PRs**). |

**Pre-commit pod:** [.cursor/rules/pre-commit-gate.mdc](../rules/pre-commit-gate.mdc) — run tester, code-reviewer, code-quality-gate, tech-debt-evaluator (and security-reviewer when relevant) before commit.

Scope/sprints: [PM_PLAN.md](../../PM_PLAN.md). Session handoffs: [.cursor/handoff/README.md](../handoff/README.md).
