---
name: handoff-protocol
description: "Handoff protocol — when a task changes hands between teammates or agents, or planning and execution are separated"
risk: low
source: spine
date_added: "2026-04-29"
---

# Handoff Protocol

## When to Use
- When a task passes from one teammate (or their agent) to another
- When separating Planner and Executor roles
- When handing off context between agents

## Default
The active task file (`<task-id>-<name>.md`) is the execution contract and the only handoff artifact.
Its frontmatter `owner` says who is responsible right now; `status` says where the work stands.
Mandatory updates at harvest: `progress.md` (delivery log append), `learnings.md` (when applicable), `decision-log.md` (when applicable); task moved to `completed_tasks/`.

## Changing owner
- Update `owner` and bump `updated_at` in the task frontmatter
- Leave a short note in the task body: what is done, what is next, open questions
- Commit and push the task branch so the new owner starts from the same state
- Never work on a task whose `owner` is someone else without confirming with them

## Planner / Executor split (optional)
- Separate Planner/Executor only when it provides real value
- Not mandatory to use `docs/discovery/` or `docs/contracts/` in every task
- Minimum: clear active task + tests + ledger update

## Handoff Flow
```
Scope → <task-id>-<name>.md → Execution → Tests → Harvest → Pull Request
```

## Rules
1. Every execution needs `docs/memory/active_tasks/<task-id>-<name>.md`
2. Structural changes to `global/` must be explicit and justified
3. Decision conflicts are escalated to the human
4. Set frontmatter `status: DONE` and `git mv` task to `completed_tasks/` when finished
5. Skill selection must respect `docs/governance/skills-policy.md`

## Reference
Core execution protocol: rule `01-core-protocol.md`
