---
description: Consolidate final delivery, update memory-bank, and close the active task with learnings
---

# Slash Command: /spine-harvest <plan_file_path>
Act as a Tech Lead and Knowledge Manager.

1. **Plan File Selection:** Use the provided `<plan_file_path>` argument.
   - Validate if the file exists and has a `.md` extension.
   - File must be under `docs/memory/active_tasks/` (open tasks only).

2. **GitFlow Compliance Check (mandatory):**
   - GitFlow is mandatory (not optional) for harvest.
   - Read `task_id`, `branch`, and `base` from task frontmatter.
   - The implementation branch must be `<type>/<task-id>` and must be the current branch.
   - The base integration branch must be the project base branch (`base_branch` in `docs/governance/integrations.md`, default `develop`; `production` for `hotfix`).
   - If branch naming does not comply, stop and request correction before any consolidation steps.

3. **Integrate the latest base (shared repository):**
   - `git fetch origin`, then `git merge origin/<base>` (or rebase if the team prefers rebase).
   - If there are conflicts, **STOP** and ask the user to resolve them. Doing this before step 5 keeps ledger conflicts out of the Pull Request.

4. **Final Verification:** Run the full test suite to ensure there are no regressions.

5. **Memory Bank Update:**

   **5a. `docs/memory/ledger/progress.md`**
   - Refresh **Current state** only when team-level blockers or next steps changed (it does not list work in progress).
   - **Append** one delivery log block at the top of **Delivery log (newest first)** — do not rewrite history:
     - `### YYYY-MM-DD — Title` (from frontmatter `title` or task slug)
     - `**Task:** <task-id>-slug | **Branch:**` from frontmatter
     - `**Tags:**` — flatten frontmatter `tags` list to comma-separated (per `docs/governance/memory-tags-policy.md`)
     - `**Description:**` — concise delivery summary

   **5b. `docs/memory/ledger/learnings.md`** (when task recorded root cause, incident, or rework)
   - Before new `LEARN-NNN`, grep existing entries by **tags** + symptoms per `memory-tags-policy.md`.
   - Add new `LEARN-NNN` or append to **Recurrences** on matching entry.
   - **Tags** required on new entries; copy from task frontmatter, refine if needed.
   - Mirror one-line pointer in task Delivery summary body.

   **5c. Unchanged when not applicable:**
   - `docs/memory/global/decision-log.md` — architectural decisions only.
   - `docs/memory/global/domain-glossary.md` — canonical terms promoted during discovery or delivery.
   - `docs/memory/global/system-patterns.md` — new patterns established.
   - `## Implementation Plan` in the task body is not copied to the delivery log (summary uses frontmatter `title`, `tags`, and delivery description only).

6. **Active Task Closure:**
   - Update frontmatter: `status: DONE`, `completed_at: YYYY-MM-DD`, `updated_at: YYYY-MM-DD`.
   - Set `related_learnings:` when linked to `LEARN-NNN` entries.
   - Add final **Delivery summary** block in task body.
   - Record learning: root cause + prevention + regression test.
   - **`git mv`** `docs/memory/active_tasks/<task-id>-name.md` → `docs/memory/completed_tasks/<task-id>-name.md` (create dir if missing).
   - Include the move in the final commit.

7. **Git Consolidation (Pull Request):**
   - Make the final commit with a semantic message (prefix matching the branch type).
   - Push the branch: `git push -u origin <branch>`.
   - **Do not** merge into `<base>` locally and **do not** delete the branch. The delivery, including the memory bank changes, reaches `<base>` through a Pull Request reviewed by the team.
   - Do not open the Pull Request here; the next step is `/spine-pr`, which opens it as a draft linked to the tracker item.

8. **Summary:** Present a concise summary of what was learned and improved in the project, then state the handoff: "Branch `<branch>` pushed. Next: `/spine-pr` to open a draft Pull Request into `<base>`."
