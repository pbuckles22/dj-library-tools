---
name: context-bootstrapper
description: Receiving-agent protocol. Boots a new agent into the minimum correct context (select + isolate) and produces a clear next-step plan without guessing.
---

# Context Bootstrapper — Receiving Agent Protocol

Use this skill when starting work on this repo, resuming after a break, switching to a new “feature-agent”, or when context feels bloated/confusing.

Goal: reach a **confident, bounded next step** using **minimal context**.

---

## Bootstrap order (read in this order)

1. **Project baseline (always-on context)**  
   - `.cursor/rules/always.mdc`
   - `AGENT_HANDOFF.md`

2. **Current phase / feature truth** (choose the one that matches the user’s goal)  
   - `PM_PLAN.md` (phase/scope)
   - `TEST_PLAN.md` (Tier 1 / Tier 2 validation gates)

3. **Most recent session handoff note** (if present)  
   - `.cursor/handoff/NNNN-handoff-YYYY-MM-DD_HHmm.md` (**highest `NNNN`**, tie-break by timestamp)  
   - and/or `doc/handoff/NNNN-HANDOFF-YYYY-MM-DD_HHmm.md` (same rule)

4. **If the task is code-touching:** read the smallest set of files necessary to act safely.

---

## Produce the “Receiver Brief” (what you must write next)

After reading, produce a short brief with:

- **Objective**: one sentence; restate the user goal precisely.
- **Scope**:
  - **In scope**:
  - **Out of scope**:
- **Constraints**: branch policy, “no guessing”, validation tier.
- **Acceptance criteria**: 2–5 verifiable checks.
- **Next steps**: 3–7 bite-sized steps, each with a validation hook.
- **Open questions**: only if something blocks safe progress.

If any required inputs are missing, stop and ask before acting.

---

## Token budget guidance (cheap but effective)

Preferred context payload for a new session:

- **Tracked truth**: `AGENT_HANDOFF.md` + the relevant plan doc(s) (project state)
- **One handoff note**: latest only (session delta)
- **Only the files you’re editing** (and their direct dependencies)

Avoid:
- Full transcript dumps
- Large logs unless they directly change decisions
- Repeating old execution details already captured in tracked docs
