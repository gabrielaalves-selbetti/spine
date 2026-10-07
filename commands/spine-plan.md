---
description: Plan a task, create memory-bank artifact, and prepare test strategy
---

# Slash Command: /spine-plan

Act as a Senior Software Architect. Follow the instructions provided in the user arguments (the text passed with the command).

**Native Plan input:** If the user arguments contain a native Plan draft (from an IDE Plan mode or similar), treat it as input to normalize into the active task artifact. Native Plan = draft; `/spine-plan` = versioned contract in `docs/memory/active_tasks/`. Discovery and GitFlow rules below still apply.

**Precondition:** `python spine.py install` completed for this project. The contract validator is `.spine/spine.py` (standard library only, Python 3.9+; if `python` is unavailable, use `py -3`). Skills live in `.spine/skills/<name>/SKILL.md`: read the file when a step below names a skill.

1. **Task ID (mandatory):**
   - Every plan belongs to one ticket in the team's tracker. Take the ID from the user arguments (for example `PROJ-123` or `48213`).
   - If no ID was given, ask for it and stop until answered. Never invent an ID and never number tasks locally.
   - The ID may contain only letters, digits, and hyphens.
   - Run `git fetch origin`, then look for the ID in `docs/memory/active_tasks/` and `docs/memory/completed_tasks/` (working tree and `origin/<base_branch>`). If a task file with this ID already exists, update that file or stop and ask — never create a second one.

2. **Discovery (conditional — `grill-me` skill):**
   Run `.spine/skills/grill-me/SKILL.md` **before** `writing-plans` when **any** of the following applies. Otherwise skip discovery and proceed to step 3.

   **Trigger precedence (first match wins):**

   1. **Explicit opt-out:** if the user arguments contain (case-insensitive) `skip discovery`, `no grill`, or `direct plan`, skip discovery regardless of scope clarity.
   2. **Explicit opt-in:** if the user arguments contain (case-insensitive) `grill me`, `grill:`, `grill -`, `grill with docs`, `grill:docs`, `stress-test`, or `challenge this`, run discovery even when scope appears clear. Strip the trigger phrase; use the remainder as the task briefing. When `grill with docs` or `grill:docs` is used, expect inline updates to `domain-glossary.md` and `decision-log.md` per the skill.
   3. **Implicit:** run discovery when scope is ambiguous, broad, multi-domain, or when major architectural/security/auth/schema/infrastructure decisions are unresolved.

   **When discovery is active:**

   - Follow the `grill-me` skill: one question at a time; provide a recommended answer; explore the codebase when the answer is discoverable there.
   - Read memory bank global files (`domain-glossary.md`, `product-context.md`, `system-patterns.md`, `decision-log.md`); promote canonical terms and architectural decisions per the skill's knowledge-promotion rules.
   - Do **not** write the full plan until discovery is complete.
   - Record outcomes in `## Discovery notes` on the task file (create the file early with frontmatter `status: PLANNING` if needed to capture notes incrementally). Note any updates made to `domain-glossary.md` or `decision-log.md`.

   **Retroactive opt-in:** if the user asks to be grilled mid-session before the plan is written, switch to discovery and resume planning after it completes.

   **Shared context rule (always applies):** if the user arguments contain a project briefing, incorporate it into scope without contradicting facts already present in memory bank files.

3. **Planning Skill (mandatory):**
   - Follow `.spine/skills/writing-plans/SKILL.md` to structure content into the Memory Bank task contract (`docs/memory/active_tasks/_task-template.md`).
   - `writing-plans` **fills** template sections; it does not replace frontmatter or rename body headings.
   - Bite-sized Task/Step detail belongs under optional `## Implementation Plan` (omit when ≤3 acceptance criteria).
   - Run only after discovery is complete or skipped.
   - If there is a conflict between a skill and this command, **this command takes precedence** to preserve the project workflow.

**Native Plan normalization:** When the user arguments are a native Plan draft with `**Goal:**`, `**Architecture:**`, `**Tech Stack:**`, or root-level `### Task N:` blocks:
   - Map `goal` → frontmatter `goal`; expand architecture/stack in `## Objective`
   - Move root-level Task/Step blocks → `## Implementation Plan`
   - Generate full frontmatter + `tags` (1–5) before saving
   - Remove legacy inline Status/Branch/Goal headers and `superpowers:*` references

4. **Execution Skill Selection:**
   - Default: `executing-plans` (generic implementation workflow).
   - Use another skill only when `docs/governance/skills-policy.md` lists it.
   - Record in frontmatter as `execution_skill: <skill-name>` (without `@` prefix).

5. **Task Plan in the Memory Bank:**
   - **GitFlow is mandatory (not optional):** every plan must follow the branch conventions in `docs/workflow/gitflow.md`.
   - **Mandatory branch policy:** `<type>/<task-id>` as execution branch, where `<type>` is one of `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `hotfix`, `release` — pick the one that matches the nature of the work (same vocabulary as Conventional Commits). Base is the project base branch: `base_branch` in `docs/governance/integrations.md` (default `develop`); for `hotfix` it is `production`. Never create the branch during planning.
   - Ensure `docs/memory/active_tasks/` exists.
   - Create: `docs/memory/active_tasks/<task-id>-<descriptive-name>.md`
   - Example: `docs/memory/active_tasks/PROJ-123-social-login-adjustment.md`
   - Create the task file with **Obsidian-style YAML frontmatter** per `.spine/rules/02-memory-bank.md` and `docs/governance/memory-tags-policy.md`:
     - `task_id` (the tracker ID), `title`, `goal`, `status: PLANNING`
     - `owner:` the person responsible for the task — take it from the user arguments; otherwise propose the output of `git config user.name` and confirm with the user
     - `tags:` YAML list (1–5 tags; grep `learnings.md` and recent progress for related tags before inventing new ones)
     - `branch`, `base`, `execution_skill`
     - `created_at`, `updated_at` (today, `YYYY-MM-DD`)
     - `completed_at:` (empty), `related_learnings: []`
   - Body sections (no inline `## Branch`, `## Base`, or `## Status`; no top-level `**Status:**` / `**Branch:**` blocks):
     - `## Discovery notes` (when discovery ran)
     - `## Objective`, `## Inputs`, `## Expected Outputs`, `## Acceptance Criteria (verifiable, TDD-ready)`, `## Test Strategy`
     - `## Implementation Plan` (optional — when scope needs bite-sized Task/Step execution detail)

6. **Plan contract checklist (before approval gate):**
   - [ ] Frontmatter complete (`task_id`, `title`, `goal`, `status`, `owner`, `tags`, `branch`, `base`, dates)
   - [ ] `task_id` is the tracker ID and the file name starts with `<task-id>-`
   - [ ] `tags` present (1–5 per `memory-tags-policy.md`)
   - [ ] `branch` is `<type>/<task-id>` and `base` is the project base branch (`base_branch` in `docs/governance/integrations.md`, default `develop`; `production` for `hotfix`)
   - [ ] No legacy inline Status/Branch/Goal block; no `superpowers:*` headers
   - [ ] Task/Step blocks only under `## Implementation Plan` (if present)

7. **Scope Validation:** After writing the plan, evaluate whether it is well-scoped before presenting it for approval:
   - **More than 2 execution skills needed?** → Suggest splitting into separate plans, each with a single primary skill.
   - **More than 7 acceptance criteria?** → Suggest splitting into smaller plans with tighter scope.
   - **Domains mixed** (e.g., infrastructure + UI + backend in the same plan)? → Suggest splitting along domain boundaries.
   - Present your evaluation to the user: "This plan covers [X domains / Y acceptance criteria]. I recommend splitting into [N] smaller plans. Proceed as-is or split?"
   - If the user chooses to split: keep this plan for the current ticket and list the remaining pieces so the team can open one tracker ticket for each. Do not create task files for work that has no tracker ID yet.

8. **Test Strategy:** Define which tests will be created/updated in `tests/` and the execution command.

9. **Contract validation (mandatory — structure only):**
   - **Always execute** the validator from project root:

     ```bash
     python .spine/spine.py doctor --task docs/memory/active_tasks/<task-id>-<descriptive-name>.md
     ```

   - **On success:** proceed to the approval gate. Include any `WARNING:` lines in your summary (e.g. unexpected `base`) — user may accept or request fixes.
   - **On failure (contract errors):** fix the task file to match `_task-template.md`, re-run until exit code 0. Do not open the approval gate while validation fails.
   - **On failure (script missing):** stop planning; ask the user to run `python spine.py install <project-root>` from their Spine clone, then retry `/spine-plan`.
   - **On failure (Python missing):** ask the user to make Python 3.9+ available, then re-run the validator. Do not skip validation.
   - **What the script checks:** frontmatter keys, `owner`, tracker ID format, file name prefix, `<type>/<task-id>` branch, tag count (1–5), required sections (`## Objective`, `## Acceptance Criteria`), legacy `**Status:**` / `**Branch:**` blocks, promotional `superpowers:` lines, Task/Step blocks only under `## Implementation Plan`.
   - **What it does not check:** scope quality, test design, or completeness of acceptance criteria — step 6 checklist and human review still apply.

10. **Approval Gate:** Stop and ask for confirmation:
    - "Plan created at docs/memory/active_tasks/<task-id>-<descriptive-name>.md. Can I execute?"
