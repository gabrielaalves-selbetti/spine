---
name: writing-plans
description: "Use when you have a spec or requirements for a multi-step task, before touching code"
risk: critical
source: community
date_added: "2026-02-27"
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase. Document files to touch, tests, and bite-sized steps. DRY. YAGNI. TDD. Frequent commits.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `docs/memory/active_tasks/<task-id>-<descriptive-name>.md`

**Conflict rule:** When used from `/spine-plan`, that command and `docs/memory/active_tasks/_task-template.md` **take precedence**. This skill fills content; it does not redefine structure.

## Before writing

1. Read `docs/memory/active_tasks/_task-template.md`.
2. Grep `docs/memory/ledger/learnings.md` and recent progress delivery log for related **tags** per `docs/governance/memory-tags-policy.md`.
3. Get the tracker ID of the task (`/spine-plan` step 1). Never invent one and never number tasks locally. Make sure no file in `active_tasks/` or `completed_tasks/` already uses it.

## Document structure (mandatory)

Every plan **must** start with YAML frontmatter, then body sections in this order:

```yaml
---
task_id: PROJ-123
title: Human-readable title
goal: One-line outcome
status: PLANNING
owner: person-responsible
tags:
  - area/example
  - type/feature
branch: feat/PROJ-123
base: develop
execution_skill: executing-plans
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
completed_at:
related_learnings: []
---
```

```markdown
# PROJ-123-descriptive-name

## Discovery notes
(When discovery ran — otherwise omit or leave brief.)

## Objective
[Expanded goal — architecture and approach belong here, not in a legacy header block.]

## Inputs
- [Files, configs, dependencies]

## Expected Outputs
- [Artifacts that must exist when done]

## Acceptance Criteria (verifiable, TDD-ready)
- [ ] [Criterion 1]
  - Test: [specific test]

## Test Strategy
- Positive / Negative / Regression
- Command: `pytest ...`

## Implementation Plan
(Optional — omit when ≤3 acceptance criteria; required when execution needs step-by-step detail.)
```

**Do not use:** inline `**Status:**`, `**Branch:**`, `**Goal:**` blocks at the top, or `superpowers:*` headers. Metadata lives in frontmatter only.

## Bite-sized task granularity

When `## Implementation Plan` is present, use this structure **only inside that section**:

```markdown
### Task N: [Component name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1:** Write the failing test (include code when helpful).

**Step 2:** Run test — expect FAIL with [message].

**Step 3:** Implement minimal code to pass.

**Step 4:** Run test — expect PASS.

**Step 5:** Commit with semantic message.
```

Each step is one action (2–5 minutes). Exact file paths always. Complete code in plan when it removes ambiguity.

## When to include Implementation Plan

| Scope | Implementation Plan |
|-------|---------------------|
| ≤3 acceptance criteria, single domain | Omit — execute from Acceptance Criteria |
| >3 criteria or multi-file refactor | Include Task/Step blocks |
| Native Plan draft with Task/Step content | Normalize into Implementation Plan section |

## Normalizing native Plan drafts

If input is an IDE-native Plan draft with `**Goal:**`, `**Architecture:**`, or root-level `### Task N:`:

- `goal` → frontmatter `goal`; details → `## Objective`
- Architecture / tech stack → `## Objective` (subsections if needed)
- Root-level Task/Step blocks → move under `## Implementation Plan`
- Generate frontmatter + tags before saving

## GitFlow (Spine default)

- `branch: <type>/<task-id>` — `<type>` is one of `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `hotfix`, `release`
- `base: develop` (`production` for `hotfix`)
- `owner:` the person responsible for the task
- Do not create the branch during planning.

## Execution handoff

When invoked from `/spine-plan`, after saving the task file:

1. Complete the plan contract checklist (command step 6).
2. Run contract validation (command step 9) — **execute** from project root:

   ```bash
   python .spine/spine.py doctor --task docs/memory/active_tasks/<file>.md
   ```

   If `python` is unavailable, use `py -3`.

   Fix structural errors and re-run until the script exits 0. If the script is missing, ask the user to run `python spine.py install` from their Spine clone. This checks format consistency, not plan quality.

3. Stop at the `/spine-plan` approval gate (command step 10):

   > Plan created at `docs/memory/active_tasks/<file>.md`. Can I execute?

Do **not** offer superpowers subagent/parallel-session handoffs. Execution starts with `/spine-execute <plan_file_path>` using `execution_skill` from frontmatter.

## Remember

- Record `execution_skill` in frontmatter (no `@` prefix)
- `/spine-plan` and `_task-template.md` override this skill on structure conflicts

## When to Use

Use when `/spine-plan` step 3 invokes planning, or when you have requirements for a multi-step task before touching code.
