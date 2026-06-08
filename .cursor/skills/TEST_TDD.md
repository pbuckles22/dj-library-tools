# TEST_TDD — Project

## How to test

- **Black-box:** Assert on behavior (public API: inputs and outputs). Do not depend on implementation details. See [tester/SKILL.md](tester/SKILL.md).
- **Continuous:** Run your project’s test command after adding or changing logic or tests; keep the suite green.
- **Tiers ([TEST_PLAN.md](../../TEST_PLAN.md)):** When defined, **Tier 1** is fast feedback; **Tier 2** is integration or E2E. Validate at every tier that applies to the change.

---

## TDD when TEST_PLAN defines Tier 1 and Tier 2

**Default:** Do not merge production changes until the right tier(s) have **failing test → passing test** for the behavior you are adding or changing.

### Tier 1

Use for logic covered by your fast test command (unit, headless, mocked APIs — whatever TEST_PLAN.md says).

1. **Red** — Add or extend a test that describes the new behavior and fails with the current code.
2. **Green** — Implement until the Tier 1 command passes.

### Tier 2

Use when behavior must hold in a real runtime (browser, device, network, DB — whatever TEST_PLAN.md says).

1. **Red** — Add or extend an integration or E2E test that fails until the feature exists.
2. **Green** — Implement until the Tier 2 command passes.

**When both apply:** Usually Tier 1 first, then Tier 2. Pure integration-only changes may start at Tier 2; add Tier 1 later if you extract testable logic.

### Exceptions

- Docs-only, config-only, or comment-only changes.
- Trivial one-line fixes with no behavior change (still run your merge-ready command if the project uses one).
- Pure refactors preserving behavior: keep tests green.

Never leave failing tests on the default branch.

---

## Merge-ready

Document your **merge-ready** or **CI** command in **AGENT_HANDOFF.md** and run it before merge when your team uses that gate.
