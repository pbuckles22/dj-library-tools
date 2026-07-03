## Release / merge discipline (SDD — no PRs)

Merges land on `main` via direct push after the **pre-commit pod** passes. Pull requests are not used.

### Merge-ready (mandatory)

Documented in `AGENT_HANDOFF.md` and `TEST_PLAN.md`:

```powershell
python -m pytest -q
```

Plus pre-commit pod consensus (see `.cursor/rules/pre-commit-gate.mdc`):

- Tier 1 green
- code-reviewer, code-quality-gate, tech-debt-evaluator PASS (security-reviewer when relevant)
- Tracked docs updated when workflow/expectations change

### Rollback

- Prefer a single revert commit per change
- Re-run pytest after revert
