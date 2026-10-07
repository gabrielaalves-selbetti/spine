---
tracker: none
tracker_mcp_server: ""
tracker_tools: []
repository: none
repository_url: ""
repository_mcp_server: ""
repository_tools: []
cli_fallback: ""
base_branch: develop
forbidden_targets: [main]
publish_state: ""
forbidden_states: []
---

# Integrations

Per-project settings for the tracker and the repository host. `/spine-pr` reads this file to open and publish
Pull Requests, and `.spine/spine.py doctor --task` reads `base_branch` to check the `base` of every task.
This file belongs to the project: `spine.py` creates it once and never overwrites it.

## Requirements

`/spine-pr` talks to the tracker and the repository host. It needs, in this order of preference:

1. **An MCP server** configured in the IDE for the repository host: GitHub, Azure DevOps, or GitLab. When the
   tracker is a different product (for example Jira with GitHub), add an MCP server for the tracker too.
2. **A CLI fallback** installed and logged in: `gh` (GitHub), `az` with the `azure-devops` extension
   (Azure DevOps), or `glab` (GitLab).
3. **Without either**, `/spine-pr` only prints a title and description ready to paste into the web UI.

Credentials live in the MCP server or CLI configuration. Never write tokens, passwords, or personal data in this
file: it is committed with the project.

## Settings

| Key | Meaning |
|---|---|
| `tracker` | Where the task IDs live: `azure-devops`, `github`, `gitlab`, `jira`, or `none` (disables `/spine-pr`). |
| `tracker_mcp_server` | Name of the tracker's MCP server, as configured in the IDE. |
| `tracker_tools` | MCP tools used to read an item and change its state. |
| `repository` | Repository host: `azure-devops`, `github`, `gitlab`, or `none` (disables `/spine-pr`). |
| `repository_url` | Web URL of the repository. |
| `repository_mcp_server` | Name of the repository host's MCP server (often the same as `tracker_mcp_server`). |
| `repository_tools` | MCP tools used to create, find, and publish a Pull Request. |
| `cli_fallback` | CLI used when the MCP server is unavailable: `gh`, `az`, or `glab`. Empty: no CLI fallback. |
| `base_branch` | Branch that work branches start from and merge into (`hotfix` keeps `production`). |
| `forbidden_targets` | Branches `/spine-pr` never opens a Pull Request into. |
| `publish_state` | The only tracker state `/spine-pr publish` may set. Empty: publish does not change the item. |
| `forbidden_states` | States the agent never sets, whatever is asked. |

<!--
Example: Azure DevOps for both tracker and repository. Replace the placeholders and copy the keys
into the frontmatter above.

tracker: azure-devops
tracker_mcp_server: azure-devops
tracker_tools: [wit_get_work_item, wit_update_work_item]
repository: azure-devops
repository_url: https://dev.azure.com/<org>/<project>/_git/<repo>
repository_mcp_server: azure-devops
repository_tools: [repo_create_pull_request, repo_list_pull_requests_by_repo_or_project, repo_update_pull_request]
cli_fallback: az
base_branch: dev
forbidden_targets: [main]
publish_state: Waiting
forbidden_states: [Homologate, Done]
-->
