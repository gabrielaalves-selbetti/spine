---
description: Create a high-quality commit for current changes with safe branch checks
---

# Slash Command: /spine-commit
Act as a Senior Software Engineer focused on clean history and safe Git flow decisions.

Goal: commit the latest local changes with a clear message that explains why and impact.

**Optional context (user arguments — the text passed with the command):**
- If the arguments are empty, run in `commit-only` mode.
- If the arguments include words like `push`, `commit and push`, or `commit+push`, run in `commit-and-push` mode.
- If the arguments are ambiguous, ask for confirmation before pushing.

1. **Pre-flight Context:**
   - Run:
     - `git status --short --branch`
     - `git diff --staged`
     - `git diff`
     - `git log --oneline -n 10`
   - If there are no staged or unstaged changes, STOP and report:
     - "No local changes to commit."

2. **Branch Safety and Decision Gate:**
   - Detect current branch and whether `develop` exists:
     - `git rev-parse --abbrev-ref HEAD`
     - `git branch --list develop`
   - If current branch is `main`, `master`, `production`, `staging`, or `develop` (no direct commits on shared branches):
     - Ask for the tracker ID of the work, then:
     - If `develop` exists:
       - Ask confirmation to create `<type>/<task-id>` from `develop` and move work there before commit.
     - If `develop` does not exist:
       - Ask confirmation and present options:
         - Option A: create `<type>/<task-id>` from current branch and commit there.
         - Option B: initialize `develop` from current branch, then create `<type>/<task-id>` from `develop`.
   - If current branch starts with `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, `chore/`, `hotfix/`, or `release/`, continue.

3. **Commit Scope Discipline:**
   - Stage only files relevant to this delivery.
   - Do not include unrelated noise.
   - If there are unrelated changes, list them and ask whether to exclude.

4. **Commit Message Quality (mandatory):**
   - Use Conventional Commits:
     - `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
   - The prefix normally matches the branch type.
   - Subject line must be concise and meaningful.
   - Body must be explicit and useful for future audits:
     - `Why:` problem or intent
     - `What changed:` key files and behavior impact
     - `Validation:` tests/checks executed
     - `Notes:` risks, follow-ups, or migration notes (if any)
   - Prefer message quality over shortness.

5. **Commit Execution:**
   - Create the commit.
   - Show:
     - `git show --name-only --oneline HEAD`
     - `git status --short --branch`

6. **Optional Push (when requested via the arguments):**
   - If mode is `commit-and-push`:
     - Ensure upstream exists for current branch; if not, push with `-u`.
     - Push current branch to `origin`.
     - Show:
       - `git status --short --branch`
       - tracking branch (`branch -vv` or equivalent)
   - If mode is `commit-only`, skip push.

7. **Team workflow (default for SPINE):**
   - Work reaches `develop` (or `production` for a `hotfix`) **only through a Pull Request** reviewed by the team.
   - **Never** merge a work branch into `develop`, `staging`, `production`, or `main` locally, and never push directly to them.
   - After `git push`, the next step is the Pull Request from the current branch into its base. If the remote prints a `.../pull/new/...` URL, show it to the user.
   - Do not open the Pull Request with a tool unless the user asks for it.
   - A task is closed with `/spine-harvest` (memory bank update + task move) **before** the Pull Request, so the review covers the memory bank changes too.

8. **Mandatory Final Report:**
   - Final branch used.
   - Commit hash + full commit message.
   - Files included in the commit.
   - Push result (performed or skipped).
   - **Next step:** `/spine-harvest` if the task is still open; otherwise open the Pull Request into the base branch.
