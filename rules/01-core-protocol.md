---
description: "Core protocol for team delivery: focus on delivery, testing, and memory."
globs: 
alwaysApply: true
---

# CORE PROTOCOL

## 1. Mandatory minimum flow
1. **Sync & clarify:** Follow `02-memory-bank.md` — tiered SYNC, then post-SYNC assumptions, ambiguities, and simplest approach.
2. **Plan:** create/update `docs/memory/active_tasks/<task-id>-<descriptive-name>.md` matching `_task-template.md` (Obsidian frontmatter + body sections; optional `## Implementation Plan` for bite-sized steps). `<task-id>` is the tracker ID and `owner` is mandatory. Do not create the branch during planning.
3. **Branch:** at execution time, create or switch to `branch` from task frontmatter (`<type>/<task-id>`), based on `base`.
4. **Test (TDD):**
   a. Write a failing test for the first acceptance criterion.
   b. Implement the minimum code to make it pass.
   c. Refactor if needed while keeping tests green.
   d. Repeat for each acceptance criterion.
5. **Execute:** implement atomically and validate all tests pass.
6. **Harvest:** append delivery log in `progress.md`; update `learnings.md` when applicable; update `decision-log.md` and `domain-glossary.md` when applicable; move task to `completed_tasks/` via `git mv`; push the branch and hand off to a Pull Request.

## 2. Definition of Done
- [ ] Isolated branch `<type>/<task-id>` created from `develop` (`production` for `hotfix`)
- [ ] `docs/memory/active_tasks/<task-id>-<descriptive-name>.md` with frontmatter (including `owner`), scope, and acceptance criteria
- [ ] Tests executed and passing
- [ ] `docs/memory/ledger/progress.md` updated (delivery log entry; Current state when team blockers or next steps changed)
- [ ] `docs/memory/ledger/learnings.md` updated (if incident, root cause, or rework recorded)
- [ ] Task file in `docs/memory/completed_tasks/` with `status: DONE`
- [ ] `docs/memory/global/decision-log.md` updated (if there was an architectural decision)
- [ ] `docs/memory/global/domain-glossary.md` updated (if canonical domain terms were promoted during discovery)
- [ ] Branch pushed and Pull Request to `base` requested

## 3. Guard rails
- Never use `git push --force`.
- Never commit directly to `main`, `production`, `staging`, or `develop`; never merge into them locally. Integration happens through Pull Requests.
- Never assume an ambiguous requirement without confirmation. Surface assumptions and tradeoffs first.
- No silent decisions: architectural decisions require a recorded "why".
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If an implementation exceeds 3x the minimum viable lines, justify why.

## 4. Commits
Prefer Conventional Commits:
- `feat:`
- `fix:`
- `refactor:`
- `test:`
- `docs:`
- `chore:`

The commit prefix normally matches the branch type (`feat/PROJ-123` → `feat:`).
