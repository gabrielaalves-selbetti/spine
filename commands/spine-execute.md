---
description: Execute the active task with implementation, validation, and status updates in the memory-bank
---

# Slash Command: /spine-execute <plan_file_path>
Act as a Software Engineer focused on rigorous implementation.

1. **Active Task Selection:** Use the provided `<plan_file_path>` argument.
   - Validate if the file exists and has a `.md` extension.
   - File must be under `docs/memory/active_tasks/` (open tasks only; completed tasks live in `completed_tasks/`).
   - Read `owner` from frontmatter. If the task belongs to someone else, confirm with the user before changing anything.
2. **Branch Setup:** Read `task_id`, `branch`, and `base` from task YAML frontmatter.
   - **GitFlow is mandatory (not optional) during execution.**
   - `branch` must be `<type>/<task-id>` with `<type>` in `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `hotfix`, `release`. `base` must be `develop` (`production` for `hotfix`).
   - If `branch` or `base` are missing or do not comply, stop and request a plan correction before implementation.
   - **Sync base before any work (shared repository):**
     1. `git fetch origin`
     2. `git checkout <base>`
     3. `git pull --ff-only origin <base>`
        - If `--ff-only` fails (local `<base>` diverged), **STOP** and ask the user to reconcile before continuing.
        - If checkout/pull is blocked by a dirty working tree, **STOP** and ask to commit or stash first.
   - If the specified `branch` does not exist yet (locally or on `origin`): `git checkout -b <branch>` (from the updated `<base>`).
   - If the `branch` already exists:
     1. `git checkout <branch>` (and `git pull --ff-only origin <branch>` when it exists on `origin`)
     2. Integrate latest base: `git merge origin/<base>` (or rebase onto `origin/<base>` if the team prefers rebase).
     3. If merge/rebase conflicts, **STOP** and ask the user to resolve before implementation.
3. **Context Reading:** Read the selected active task mandatorily:
   - YAML frontmatter (`goal`, `tags`, `execution_skill`, …)
   - `## Acceptance Criteria`, `## Test Strategy`
   - `## Implementation Plan` when present — use Task/Step blocks as the execution checklist (batch via the `executing-plans` skill)
   - If Implementation Plan is **missing** and there are **>3** acceptance criteria, stop and ask to extend the plan or proceed criterion-by-criterion
4. **Execution Skill Selection:**
   - Use the skill specified in frontmatter `execution_skill`: read `.spine/skills/<execution_skill>/SKILL.md` (for a project skill, the path listed in `docs/governance/skills-policy.md`).
   - If no skill is specified, default to `executing-plans`.
   - Do not use a skill that `docs/governance/skills-policy.md` does not list.
5. **Atomic Implementation:** Implement the required code by following `docs/memory/global/system-patterns.md` and the active task guidelines.
6. **Validation Cycle:**
   - Run the test command defined in the active task.
   - If it fails, analyze the error and fix the code (not the test, unless the test is logically wrong).
   - Repeat until all tests pass.
7. **Execution Status:** Update frontmatter at start and end:
   - At beginning: `status: IN_PROGRESS`, bump `updated_at`.
   - When complete: `status: REVIEW`, bump `updated_at`.
   - When marking `REVIEW`, record a minimal checklist with tests executed and test results in the task body.
8. **Restriction:** Do not perform refactors outside the active task scope. If you find a necessary improvement, record it in "Notes" in the task itself.
9. **Completion Gate (mandatory):**
   - Before sending the final execution response, verify frontmatter `status` is `REVIEW`.
   - If status is not `REVIEW`, stop and update it before completion.
   - `REVIEW` is valid only if evidence is present: `Tests executed` list and `Test results` summary.
   - If test evidence is missing, stop and update the active task file before completion.
   - Do not merge and do not open the Pull Request here: `/spine-harvest` closes the delivery.
