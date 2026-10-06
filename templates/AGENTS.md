# AGENTS.md

This project uses **Spine**: a shared workflow for coding agents (rules, memory bank, commands).
This file is the entry point for every agent and every teammate's IDE. It belongs to the project:
`spine.py` creates it once and never overwrites it.

## Rules (read before any work)

Read these files in order and follow them. They are the source of truth for how work is done here.

1. `.spine/rules/01-core-protocol.md` — delivery cycle, definition of done, guard rails, commits
2. `.spine/rules/02-memory-bank.md` — structure and reading order of `docs/memory/`
3. `.spine/rules/03-code-quality.md` — style, architecture, error handling, security (when changing code)

Always:

- `docs/memory/` is the operational source of truth. Run the tiered SYNC from rule 02 at the start of every session.
- Every task has a tracker ID, an `owner`, and a branch `<type>/<task-id>`. Work reaches `develop` only through a Pull Request.
- Never edit anything under `.spine/`. It is managed by `spine.py` and replaced on every update.
- When instructions conflict: the user's request first, then this file, then `.spine/rules/`.

## Commands

Each IDE has thin command files that point here. The full instructions live in `.spine/commands/`.

| Command | Instructions | Purpose |
|---|---|---|
| `/spine-bootstrap` | `.spine/commands/spine-bootstrap.md` | Assess the project and fill the memory bank |
| `/spine-plan` | `.spine/commands/spine-plan.md` | Turn a tracker ticket into a task plan |
| `/spine-execute` | `.spine/commands/spine-execute.md` | Implement an active task with tests |
| `/spine-harvest` | `.spine/commands/spine-harvest.md` | Close the task, update the memory bank, hand off to a Pull Request |
| `/spine-commit` | `.spine/commands/spine-commit.md` | Commit with branch safety checks |

If the IDE does not show a command, read its instructions file directly and follow it.

## Skills

Load a skill only when a command or the task calls for it: read `.spine/skills/<name>/SKILL.md`.
Which skills may be used is governed by `docs/governance/skills-policy.md`.

## Project documents

- `docs/memory/` — memory bank (context, decisions, progress, tasks)
- `docs/workflow/` — branch flow and delivery cycle
- `docs/quality/guardrails.md` — test and merge guard rails
- `docs/governance/` — skills policy and memory tags policy

## Checks

```bash
python .spine/spine.py doctor
python .spine/spine.py doctor --task docs/memory/active_tasks/<task-id>-<name>.md
```

## Project-specific instructions

<!-- Add this project's own rules below. They take precedence over .spine/rules/. -->
