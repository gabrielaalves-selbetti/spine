---
description: Open the task's Pull Request as a draft linked to the tracker item, or publish it
---

# Slash Command: /spine-pr [publish]
Act as a Senior Software Engineer handing a finished delivery to team review.

**Modes (user arguments — the text passed with the command):**
- Empty: **open** — create the Pull Request as a draft.
- `publish`: **publish** — take the draft out of draft and move the tracker item to the configured state.
- Anything else: stop and show these two modes.

**Requirement:** an MCP server for GitHub, Azure DevOps, or GitLab (and one for the tracker when it is a different
product), or the matching CLI as a fallback. Without either, this command only prints text ready to paste.
See `docs/governance/integrations.md`.

1. **Configuration:**
   - Read the frontmatter of `docs/governance/integrations.md`. If the file is missing, or `tracker` or `repository`
     is `none`, stop: explain that the integration is not configured and point to that file.
   - Never read credentials from files and never ask the user to paste a token into the chat.

2. **Task and branch checks (both modes):**
   - Current branch: `git rev-parse --abbrev-ref HEAD`. It must be `<type>/<task-id>`; otherwise stop.
   - Find the task file for `<task-id>` in `docs/memory/completed_tasks/` (after `/spine-harvest`) or
     `docs/memory/active_tasks/`, and read `task_id`, `title`, `branch`, and `base` from its frontmatter.
     If `branch` differs from the current branch, stop.
   - **Target branch** is the task's `base`. If it is listed in `forbidden_targets`, refuse: never open or publish a
     Pull Request into a forbidden branch, even when asked.
   - The branch must be pushed and up to date with `origin` (`git status --short --branch`). If not, stop and point to
     `/spine-commit push` or `/spine-harvest`.
   - If the task is still in `active_tasks/`, warn that `/spine-harvest` has not run yet and ask whether to continue.

3. **Access path (follow `.spine/rules/01-core-protocol.md`, External tools):**
   1. MCP: `tracker_mcp_server`/`tracker_tools` and `repository_mcp_server`/`repository_tools`.
   2. CLI fallback (`cli_fallback`) only when the MCP server is not configured, not reachable, or lacks the operation.
      Print one line before using it: `Using CLI fallback (<cli>): <reason>.`
   3. Manual: when neither works, print the title and description ready to paste, plus the source and target branches,
      and stop.
   - A refusal by the user, a permission rule, or a guard is **not** a reason to fall back. Stop, explain what was
     blocked, and ask how to proceed.

4. **Mode open:**
   - Read the tracker item `<task-id>`: title and current state. If the item does not exist, stop.
   - If a Pull Request from `<branch>` into `<base>` already exists, report its URL and stop.
   - Build the Pull Request:
     - **Source → target:** `<type>/<task-id>` → `<base>`.
     - **Title:** the tracker item title, prefixed with the task ID when the team convention asks for it.
     - **Link to the item:** Azure DevOps — the Pull Request's work item link; GitHub or GitLab — `Refs #<task-id>` in
       the description (or the Jira key when the tracker is Jira). Never use closing keywords such as `Closes`,
       `Fixes`, or `Resolves`: they change the item state on merge.
     - **Description:** objective, delivery summary, and validation (tests and checks run), taken from the task file.
     - **Draft:** always.
   - Show the full payload and ask for confirmation. Create it only after an explicit yes.

5. **Mode publish:**
   - Find the open Pull Request from `<branch>` into `<base>`. If there is none, stop and suggest `/spine-pr`.
     If it is not a draft, report it and skip the draft step.
   - If `publish_state` is empty, only the draft step runs. If `publish_state` is listed in `forbidden_states`, stop:
     the configuration is inconsistent.
   - Show the two writes (Pull Request ready for review; item `<current state>` → `publish_state`) and ask for
     confirmation. Run them only after an explicit yes.
   - Moving the item to `publish_state` is the only state change this command makes.

6. **Never:**
   - Approve, vote, complete or merge, abandon or close a Pull Request; never enable auto-complete.
   - Bypass, override, or disable branch policies or required reviewers.
   - Set a state listed in `forbidden_states`, or any state other than `publish_state`.
   - Put personal data (names, e-mail addresses, phone numbers, customer data) or credentials in the title,
     description, or comments.

7. **Final report:**
   - Pull Request URL (or the paste-ready text), source and target branches, draft or published.
   - Tracker item ID and state before and after.
   - Path used: MCP, CLI fallback, or manual.
   - **Next step:** after `open`, `/spine-pr publish` when the team is ready to review; after `publish`, the team
     reviews and merges in the repository host.
