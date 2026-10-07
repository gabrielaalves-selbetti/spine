# Delivery Cycle (Lean)

## Goal
Run tasks predictably and with quality, keeping documentation minimal and useful.

## Standard Cycle
1. **Task intake**
   - Start from a ticket in the team tracker (the ticket ID identifies the task).
   - Define goal, scope, owner, and acceptance criteria.
2. **Quick plan**
   - Describe the approach in a few lines.
   - Define the test plan (positive, negative, regression).
3. **Execution on `<type>/<task-id>`**
   - Implement the minimum needed to deliver value.
4. **Validation**
   - Run the planned tests.
   - Check the impact on related areas.
5. **Record (harvest v2.1)**
   - Append the entry to the delivery log in `docs/memory/ledger/progress.md` (with **Tags**); update Current state when there is a blocker or a next step for the team.
   - Record recurrences in `docs/memory/ledger/learnings.md` when there was an incident or rework.
   - Record decisions in `docs/memory/global/decision-log.md`.
   - Move the finished task: `git mv active_tasks/ → completed_tasks/` (frontmatter `status: DONE`).
6. **Pull Request**
   - Push the branch and open a Pull Request to `develop`, reviewed by the team.
7. **Promotion**
   - `develop` -> `staging` -> `production` -> `main`.

## Definition of Done
- Acceptance criteria met.
- Planned tests executed.
- Memory bank updated.
- Pull Request open against the base branch.
- No undocumented critical pending item.

## Anti-Overengineering Guardrail
- Do not create a new abstraction without 2 real cases.
- Do not add a new tool unless it replaces something or reduces cost/time.
- Prefer the simple solution before the "generic" one.
