---
description: "Defines structure and practical use of the Memory Bank as the operational source of truth."
globs: 
alwaysApply: true
---

# MEMORY BANK V2.1 - State API

The `docs/memory/` directory is the **operational source of truth**. It is shared by the whole team through git.

Tag conventions: see `docs/governance/memory-tags-policy.md`.

## Structure

```
docs/memory/
  global/                    # Stable base (changes with explicit justification)
    project-brief.md         # Scope, goals, project boundaries
    product-context.md       # Why the project exists, problems it solves, UX goals; § Known Opportunities (unplanned)
    domain-glossary.md       # Ubiquitous language: canonical domain terms (language only)
    system-patterns.md       # Stack, architecture, design patterns; § Project-Specific Alterations
    tech-context.md          # Dev setup, constraints, infra; § Known Risks
    decision-log.md          # Record of architectural decisions with WHY
  ledger/                    # Current state (updated on each task)
    roadmap.md               # Milestones maintained by the team (not filled at bootstrap)
    progress.md              # Current state + delivery log (append-only)
    learnings.md             # Recurrence registry (incidents, root causes — harvest only)
  active_tasks/              # Open work only (PLANNING | IN_PROGRESS | REVIEW)
    <task-id>-<descriptive-name>.md
  completed_tasks/           # DONE tasks moved on harvest
    <task-id>-<descriptive-name>.md
```

`<task-id>` is the ID of the ticket in the team's tracker (for example `PROJ-123`). It is never invented or numbered locally.

### Global file semantics (agent-oriented)

| File | Bootstrap fills | Notes |
|------|-----------------|-------|
| `project-brief.md` | Yes | Scope, goals, boundaries |
| `product-context.md` | Yes | Product behavior; § **Known Opportunities (unplanned)** for improvements not yet scheduled |
| `domain-glossary.md` | Yes | Terms + code location hints |
| `system-patterns.md` | Yes | Architecture; § **Project-Specific Alterations** (custom payment, auth, etc.) — agents must not revert |
| `tech-context.md` | Yes | Dev commands, env; § **Known Risks** |
| `decision-log.md` | Yes | WHY for major alterations and bootstrap baseline |
| `roadmap.md` | **No** | Plain milestone list maintained by the team |
| `learnings.md` | Rarely at bootstrap | Incidents at `/spine-harvest` only |

`/spine-bootstrap` runs after `python spine.py install` and fills placeholders in `global/` plus `progress.md` Current state. It does **not** create `active_tasks/` files — use `/spine-plan`.

## Access Rules (pragmatic)

| Layer | Author | When it changes |
|---|---|---|
| `global/` | Human or agent with explicit approval | Scope/architecture changes |
| `ledger/` | Executing agent | Every delivery cycle |
| `active_tasks/` | Executing agent (task `owner`) | Created in PLAN; updated until harvest |
| `completed_tasks/` | Executing agent | Written only at harvest (`git mv` from `active_tasks/`) |
| `ledger/learnings.md` | Executing agent | At harvest when root cause / incident / rework recorded |

Every change to the memory bank travels in the task branch and reaches the base branch through the Pull Request.

## Tiered SYNC (reading rules)

If a file does not exist, create it only if it is part of the current task flow.

### Core (every session)

1. `global/project-brief.md` (scope)
2. `global/product-context.md` (product context)
3. `global/domain-glossary.md` (domain language — create lazily during discovery or `/spine-bootstrap` if missing)
4. `global/system-patterns.md` (how to build)
5. `global/tech-context.md` (constraints)
6. `global/decision-log.md` (previous decisions)
7. `ledger/progress.md` — **Current state** section only
8. `active_tasks/` — every `.md` except `_task-template.md`; frontmatter `owner` and `status` tell who is working on what

### Extended (planning, harvest, ambiguous scope)

- `ledger/roadmap.md`
- `ledger/progress.md` — full **Delivery log**

### On demand (debugging, recurrence, audits)

- `ledger/learnings.md`
- `completed_tasks/`
- Grep task frontmatter (`tags:`) and ledger `**Tags:**` per `memory-tags-policy.md`

After SYNC, before any code change, state:
- Key assumptions about the task derived from the memory bank.
- Any ambiguities, gaps, or conflicts found in the context — present them; do not pick silently.
- The simplest approach that satisfies the requirements. If a simpler alternative exists, name it and push back.

## Template: active_tasks/_task-template.md

Reference file (not a task). Tasks use Obsidian-style YAML frontmatter. See `docs/memory/active_tasks/_task-template.md`.

```yaml
---
task_id: PROJ-123
title: Social login adjustment
goal: One-line outcome the task must achieve
status: PLANNING
owner: maria.silva
tags:
  - area/auth
  - type/feature
branch: feat/PROJ-123
base: develop
execution_skill: executing-plans
created_at: 2026-06-05
updated_at: 2026-06-05
completed_at:
related_learnings: []
---
```

| Property | Required | Notes |
|---|---|---|
| `task_id` | yes | Tracker ID (letters, digits, hyphens); equals the file name prefix and the branch suffix |
| `title` | yes | Human-readable title |
| `goal` | yes | Single outcome sentence |
| `status` | yes | `PLANNING` \| `IN_PROGRESS` \| `REVIEW` \| `DONE` |
| `owner` | yes | Person responsible for the task (name or handle) |
| `tags` | yes | YAML list; 1–5 tags per `memory-tags-policy.md` |
| `branch` | yes | `<type>/<task_id>`; type is one of `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `hotfix`, `release` |
| `base` | yes | `base_branch` from `docs/governance/integrations.md` (default `develop`; `production` for `hotfix`) |
| `execution_skill` | recommended | Without `@` prefix |
| `created_at` / `updated_at` | yes | ISO date `YYYY-MM-DD` |
| `completed_at` | on DONE | Set at harvest |
| `related_learnings` | optional | List of `LEARN-NNN` refs |

Body sections (no duplicate metadata — no `## Branch`, `## Base`, or body `## Status`):

```markdown
# PROJ-123-social-login-adjustment

## Discovery notes
...

## Objective
[Expanded goal]

## Inputs
- [Input files/data]

## Expected Outputs
- [Files/artifacts that must be generated]

## Acceptance Criteria (verifiable, TDD-ready)
- [ ] [Criterion 1]
  - Test: [specific test that proves this criterion]

## Test Strategy
...
```

Optional body section (use when bite-sized execution steps are needed):

```markdown
## Implementation Plan

### Task 1: [Component]
**Files:** ...
**Step 1:** ...
```

**Anti-patterns (do not use in task files):**

- Inline legacy metadata blocks (`**Status:**`, `**Branch:**`, `**Goal:**` at document top)
- `superpowers:*` skill headers instead of frontmatter `execution_skill`
- A `task_id` that is not a tracker ID, or two task files with the same `task_id`
- A branch that is not `<type>/<task_id>`

Validate a task file: `python .spine/spine.py doctor --task docs/memory/active_tasks/<file>.md`.

## Template: ledger/progress.md

```markdown
## Current state
- Blocked: ...
- Next: ...

## Delivery log (newest first)
### YYYY-MM-DD — Title
**Task:** PROJ-123-slug | **Branch:** feat/PROJ-123
**Tags:** area/example, type/feature
**Description:** ...
```

**Current state** holds team-level blockers and next steps only. Work in progress is not listed there: it is whatever sits in `active_tasks/`, with its `owner` and `status`.

**Delivery log** is append-only: add one entry at the top and never rewrite history. When two Pull Requests conflict here, keep both entries, newest first.

## Template: ledger/learnings.md

```markdown
## LEARN-001 — Short slug title
**First seen:** YYYY-MM-DD | **Task:** PROJ-123-slug
**Tags:** area/example, type/incident

**Symptoms:** ...
**Root cause:** ...
**Detect early:** ...
**Prevention:** ...
**Regression test:** ...

**Recurrences:**
- YYYY-MM-DD — task PROJ-456-slug (brief)
```

## Template: completed_tasks/

Same file as `active_tasks/` after harvest: frontmatter `status: DONE`, `completed_at` set, file moved via `git mv`.
