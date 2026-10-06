---
task_id: PROJ-000
title: Task title (human-readable)
goal: One-line outcome the task must achieve
status: PLANNING
owner: person-responsible
tags:
  - type/feature
branch: feat/PROJ-000
base: develop
execution_skill: executing-plans
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
completed_at:
related_learnings: []
---

# PROJ-000-descriptive-name

> Reference template only — not a task. Copy structure when creating tasks via `/spine-plan`.
> `task_id` is the tracker ID; the file name is `<task_id>-<descriptive-name>.md` and the branch is `<type>/<task_id>`.
> Do not use inline `**Status:**`, `**Branch:**`, or `superpowers:*` headers — metadata lives in frontmatter only.

## Discovery notes

(When discovery ran: resolved decisions, MVP, out-of-scope, glossary/decision-log promotions.)

## Objective

(Expanded goal — may elaborate frontmatter `goal`.)

## Inputs

- [Input files/data]

## Expected Outputs

- [Files/artifacts that must be generated]

## Acceptance Criteria (verifiable, TDD-ready)

- [ ] [Criterion 1]
  - Test: [specific test that proves this criterion]
- [ ] [Criterion 2]
  - Test: [specific test that proves this criterion]

## Test Strategy

- Positive:
- Negative:
- Regression:
- Command: `pytest ...`

## Implementation Plan

(Optional — use when the task needs bite-sized execution steps. Omit for small tasks with ≤3 acceptance criteria.)

### Task 1: [Component name]

**Files:**
- Create: `path/to/file`
- Modify: `path/to/existing:line-range`
- Test: `tests/path/to/test.py`

**Step 1:** [One action — write failing test, run command, etc.]

**Step 2:** [Next action]

**Step 3:** Commit with semantic message.
