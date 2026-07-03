---
name: session-summarizer
description: Leaving-agent protocol. Produces a compressed, decision-first handoff that preserves intent and next steps while stripping execution noise.
---

# Session Summarizer — Leaving Agent Protocol

Use this skill when ending a session, reducing context, handing work to a new agent, or preparing a “feature-agent” to pause safely.

Goal: transfer **working state** (decisions, rationale, next steps) with **minimal tokens**.

---

## Progressive summarization (what to keep vs strip)

Always keep (highest value per token):
1. **Decisions** (what we chose)
2. **Rationale** (why we chose it)
3. **Next steps** (what to do next, in order)
4. **Acceptance criteria / validation** (how to know it’s done)

Keep only summary-level:
- Actions taken (headline only)
- File paths changed (key files only)

Strip unless directly decision-relevant:
- Long logs
- Step-by-step execution transcripts
- Repeated context already captured in tracked docs

---

## Handoff note budget

Default target: **≤ 500 words** (≈ 700 tokens).

If you exceed the budget, remove execution details first.

---

## Handoff note structure (required)

Write the handoff note using this structure (mirrors the repo template):

### Filename rules (mandatory)

- Prefer: `.cursor/handoff/NNNN-handoff-YYYY-MM-DD_HHmm.md`
- Optional second location: `doc/handoff/NNNN-HANDOFF-YYYY-MM-DD_HHmm.md`
- **`NNNN` must be new and monotonic** (0001, 0002, …). Never reuse a number.
- Never edit a prior handoff file to “update” it—write a new one.

### Note contents

- **TL;DR (1–2 sentences)**: current state + the one key thing the next agent must know
- **Decisions made**: bullet list (decision + rationale)
- **Done this session**: summary bullets (no logs)
- **Next steps (prioritized)**: 1–5 steps; each step should be verifiable
- **Blockers / open questions**: only items that prevent safe progress
- **Durable docs updated**: list tracked docs updated (or “none”)
- **Key files**: only the handful that matter next

---

## “Green and Clean” exit check

Before ending:
- Are acceptance criteria satisfied (or clearly not yet)?
- Were the right validation tiers run (Tier 1 minimum where defined)?
- Are durable decisions written into tracked docs (not only in the note)?
- Is the note short enough to prevent context bloat?
