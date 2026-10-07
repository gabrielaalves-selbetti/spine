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
6. **Harvest:** append delivery log in `progress.md`; update `learnings.md` when applicable; update `decision-log.md` and `domain-glossary.md` when applicable; move task to `completed_tasks/` via `git mv`; push the branch and hand off to a Pull Request with `/spine-pr`.

## 2. Definition of Done
- [ ] Isolated branch `<type>/<task-id>` created from the base branch (`base_branch` in `docs/governance/integrations.md`, default `develop`; `production` for `hotfix`)
- [ ] `docs/memory/active_tasks/<task-id>-<descriptive-name>.md` with frontmatter (including `owner`), scope, and acceptance criteria
- [ ] Tests executed and passing
- [ ] `docs/memory/ledger/progress.md` updated (delivery log entry; Current state when team blockers or next steps changed)
- [ ] `docs/memory/ledger/learnings.md` updated (if incident, root cause, or rework recorded)
- [ ] Task file in `docs/memory/completed_tasks/` with `status: DONE`
- [ ] `docs/memory/global/decision-log.md` updated (if there was an architectural decision)
- [ ] `docs/memory/global/domain-glossary.md` updated (if canonical domain terms were promoted during discovery)
- [ ] Branch pushed and Pull Request to `base` opened as a draft with `/spine-pr` (or requested from the team)

## 3. Guard rails
- Never use `git push --force`.
- Never commit directly to `main`, `production`, `staging`, `develop`, or the configured `base_branch`; never merge into them locally. Integration happens through Pull Requests.
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

## 5. External tools (tracker and repository)
Project settings live in `docs/governance/integrations.md`.
- **MCP first, CLI as fallback.** Use the configured MCP server. Use the CLI in `cli_fallback` only when the MCP server is not configured, not reachable, or lacks the operation, and say so in one line first: `Using CLI fallback (<cli>): <reason>.`
- **No workaround.** A refusal by the user, a permission rule, or a guard that blocks one path is never worked around through the other path. Stop, explain what was blocked, and ask how to proceed.
- **Every write asks first.** Creating or updating a Pull Request, changing a tracker item, or posting a comment requires an explicit confirmation after showing what will be written.
- **Never** approve, vote on, complete, merge, or abandon a Pull Request; never enable auto-complete; never bypass, override, or disable branch policies.
- **Never** set a tracker state other than the configured `publish_state`, and never one listed in `forbidden_states`.
- **No personal data or credentials** in Pull Request titles, descriptions, or comments.
