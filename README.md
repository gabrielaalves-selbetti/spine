# Spine

A shared delivery workflow for coding agents and the teams that work with them.

Spine is a reusable set of instructions — rules, a memory bank, and slash commands — that gives every agent
and every teammate the same way of planning, building, and handing off work. One Python script installs it
into a project as real, committable files: no Bash, no PowerShell, no symlinks, no admin rights, no network.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Extending your project](#extending-your-project)
- [Updating](#updating)
- [Health checks](#health-checks)
- [Troubleshooting](#troubleshooting)
- [Migrating from the shell installers](#migrating-from-the-shell-installers)
- [Uninstalling](#uninstalling)
- [Contributing](#contributing)
- [Credits](#credits)

## Features

- **Delivery workflow** — plan, execute with tests, harvest, Pull Request.
- **Memory bank** (`docs/memory/`) — context, decisions, progress, and tasks, shared through git.
- **Rules** — three short files every agent reads, reached from the project's `AGENTS.md`.
- **Commands** — `/spine-bootstrap`, `/spine-plan`, `/spine-execute`, `/spine-harvest`, `/spine-commit`.
- **Skills** — nine workflow skills loaded on demand.
- **One-file installer** — `spine.py` installs, updates, and checks a project; running it twice changes nothing.

## Requirements

- Python 3.9 or newer, standard library only (`python --version`; `py -3` also works on Windows).
- A local copy of this repository (git clone or unpacked `.zip`).
- Nothing else: no admin rights, no Developer Mode, no package installs.

## Quick start

1. Get a local copy of Spine, outside your project:

   ```
   git clone https://github.com/gabrielaalves-selbetti/spine C:\tools\spine
   ```

2. Preview what would be written to your project (nothing is changed):

   ```
   python C:\tools\spine\spine.py install C:\dev\my-project --ides claude,cursor --dry-run
   ```

3. Install:

   ```
   python C:\tools\spine\spine.py install C:\dev\my-project --ides claude,cursor
   ```

4. Commit everything that was created, then run `/spine-bootstrap` in the IDE.

From the first install to day-to-day use and updates:

```mermaid
flowchart TD
    clone["Clone Spine outside the project"] --> dry["spine.py install --dry-run"]
    dry --> install["spine.py install --ides ..."]
    install --> commit["Commit the generated files"]
    commit --> bootstrap["/spine-bootstrap fills the memory bank"]
    bootstrap --> work["Daily work: plan, execute, harvest, Pull Request"]
    work --> newer{"Newer Spine available?"}
    newer -- no --> work
    newer -- yes --> pull["Update the Spine clone"]
    pull --> reinstall["spine.py install (reuses --ides)"]
    reinstall --> doctor["python .spine/spine.py doctor"]
    doctor --> recommit["Commit the update"]
    recommit --> work
```

The same commands work on macOS and Linux with POSIX paths, for example
`python3 ~/tools/spine/spine.py install ~/dev/my-project --ides claude`.

## Installation

`install` runs from the Spine clone and points at the project root. It copies files into the project, never
touches the network, and never writes outside the project.

```
python C:\tools\spine\spine.py install [TARGET] --ides <list> [--dry-run] [--force]
```

### Options

| Option | Meaning |
|---|---|
| `TARGET` | Project root. Default: current directory. |
| `--ides` | Comma-separated: `claude`, `cursor`, `antigravity`, `windsurf`. Required on the first install; later runs reuse the previous selection. |
| `--dry-run` | Show `CREATE` / `UPDATE` / `REMOVE` / `SKIP` and write nothing. |
| `--force` | Overwrite command pointers you edited by hand. Never applies to `AGENTS.md`, `CLAUDE.md`, or `docs/`. |

### What gets created

```text
my-project/
├── AGENTS.md                     created once; the hub every agent reads
├── CLAUDE.md                     created once (Claude Code): "@AGENTS.md"
├── .spine/                       single source of truth, managed by spine.py
│   ├── spine.py                  doctor
│   ├── manifest.json             what was generated (hashes, no timestamp)
│   ├── .gitattributes            keeps .spine/ on LF line endings
│   ├── commands/                 full command instructions
│   ├── rules/                    01-core-protocol, 02-memory-bank, 03-code-quality
│   └── skills/                   workflow skills
├── docs/                         created once; never overwritten
│   ├── memory/                   global/, ledger/, active_tasks/, completed_tasks/
│   ├── governance/  quality/  workflow/
├── .claude/commands/spine-*.md   thin pointers to .spine/commands/
└── .cursor/commands/spine-*.md   thin pointers to .spine/commands/
```

The installer never touches `.gitignore`. Everything it creates is meant to be committed, so teammates get
Spine with `git pull`.

### File classes

Three kinds of files, three rules:

| Kind | Paths | Behavior on every run |
|---|---|---|
| Mirror | `.spine/**` | Made equal to the Spine clone. Do not edit by hand. |
| Pointer | per-IDE command files | Rewritten when missing or untouched; your edits are kept unless `--force`. |
| Seed | `AGENTS.md`, `CLAUDE.md`, `docs/**` | Created only when missing. Never overwritten. |

How `install` decides what to do with each file:

```mermaid
flowchart TD
    file["File in the install plan"] --> kind{"Which class?"}
    kind -- Mirror --> mirror{"Same as the Spine clone?"}
    mirror -- yes --> keep["KEEP"]
    mirror -- no --> write["CREATE or UPDATE"]
    kind -- Pointer --> pointer{"On disk?"}
    pointer -- missing --> create["CREATE"]
    pointer -- "up to date" --> keep
    pointer -- outdated --> edited{"Edited by hand?"}
    edited -- no --> update["UPDATE"]
    edited -- "yes, with --force" --> update
    edited -- "yes, without --force" --> skip["SKIP (your edit is kept)"]
    kind -- Seed --> seed{"Already exists?"}
    seed -- yes --> keep
    seed -- no --> create
```

Files that a previous install generated and the Spine clone no longer has are removed (`REMOVE`): always
under `.spine/`, and for pointers only when they were not edited by hand (or with `--force`).

### Existing `AGENTS.md`

If the project already has an `AGENTS.md`, it is left alone: the Spine hub is written to
`.spine/AGENTS.snippet.md` for you to merge by hand, and `doctor` warns until `AGENTS.md` references
`.spine/rules`.

### Supported IDEs

| `--ides` | Rules | Command pointers | Status |
|---|---|---|---|
| `claude` | `CLAUDE.md` → `@AGENTS.md` | `.claude/commands/` | Known layout |
| `cursor` | `AGENTS.md` at the root | `.cursor/commands/` | **A VERIFICAR** |
| `antigravity` | `AGENTS.md` at the root | `.agents/workflows/` (or `.agent/workflows/`) | **A VERIFICAR** |
| `windsurf` | `AGENTS.md` at the root | `.windsurf/workflows/` | **A VERIFICAR** |

Rows marked **A VERIFICAR** have not been checked by hand against the IDE yet; `install` and `doctor` print
a note for them. The paths live in one table (`IDE_LAYOUTS` in `spine.py`).

## Usage

### Commands

| Command | Purpose |
|---|---|
| `/spine-bootstrap` | Assess the project and fill the memory bank |
| `/spine-plan` | Turn a tracker ticket into a task plan |
| `/spine-execute` | Implement an active task with tests |
| `/spine-harvest` | Close the task, update the memory bank, hand off to a Pull Request |
| `/spine-commit` | Commit with branch safety checks |

Each IDE gets one thin pointer file per command; the full instructions live in `.spine/commands/`. If the IDE
does not show a command, open its instructions file there and follow it.

### Team workflow

1. **Ticket** — every task starts from a ticket in your tracker. Its ID (for example `PROJ-123`) is the task ID.
2. **`/spine-plan PROJ-123 <goal>`** — writes `docs/memory/active_tasks/PROJ-123-<name>.md` with an `owner`,
   acceptance criteria, and a test strategy, then validates it.
3. **`/spine-execute <task file>`** — syncs `develop`, creates the branch `<type>/<task-id>`, implements test-first.
4. **`/spine-harvest <task file>`** — updates the memory bank, moves the task to `completed_tasks/`, commits,
   pushes, and stops.
5. **Pull Request** — the branch reaches `develop` only through a reviewed Pull Request.

Branches: `main`, `develop`, `staging`, `production`, and work branches `<type>/<task-id>` where `<type>` is one of
`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `hotfix`, `release`. Promotion goes
`develop` → `staging` → `production` → `main`. Details: `docs/workflow/gitflow-operacional.md` in the project.

Delivery of one task, with the task file status at each step:

```mermaid
flowchart TD
    ticket["Tracker ticket PROJ-123"] --> plan["/spine-plan PROJ-123 goal"]
    plan --> planned["Task file in active_tasks/ (status PLANNING)"]
    planned --> execute["/spine-execute task-file"]
    execute --> branch["Branch type/PROJ-123 from develop (status IN_PROGRESS)"]
    branch --> tests["Implement test-first and validate (status REVIEW)"]
    tests --> harvest["/spine-harvest task-file"]
    harvest --> done["Memory bank updated, task moved to completed_tasks/ (status DONE)"]
    done --> push["Commit and git push"]
    push --> pr["Pull Request reviewed and merged into develop"]
```

Promotion between environments:

```mermaid
flowchart LR
    develop["develop"] --> staging["staging"]
    staging --> production["production"]
    production --> main["main"]
```

### Memory Bank v2.1

Operational source of truth: `docs/memory/` (Markdown in git). Canonical spec: `rules/02-memory-bank.md`
(`.spine/rules/02-memory-bank.md` in an installed project).

```text
docs/memory/
  global/              # Stable context (brief, glossary, patterns, decisions)
  ledger/
    roadmap.md         # Milestones maintained by the team
    progress.md        # Team blockers and next steps + append-only delivery log
    learnings.md       # Recurrence registry (LEARN-NNN)
  active_tasks/        # Open work; each file has an owner and a status
  completed_tasks/     # DONE tasks (moved at harvest via git mv)
```

**Tiered SYNC:**

| Tier | When | Read |
|------|------|------|
| Core | Every session | global 1–6, progress Current state, open `active_tasks/` |
| Extended | Plan, harvest, ambiguous scope | `roadmap.md`, full delivery log |
| On demand | Debugging, recurrence | `learnings.md`, `completed_tasks/` |

## Extending your project

`.spine/` belongs to Spine: it is replaced on every `install`, so nothing of your own goes there. Your
project's skills, subagents, commands, and rules live in the IDE's own directories and in `AGENTS.md`. The
installer writes only `.spine/`, its `spine-*.md` command pointers, and missing seed files; everything else
in `.claude/`, `.cursor/`, and the other IDE directories is never touched.

```mermaid
flowchart TD
    start["I want to add or change something"] --> own{"Is it part of Spine itself?"}
    own -- yes --> clone["Change it in the Spine clone, then run install again"]
    own -- no --> what{"What is it?"}
    what -- Skill --> skill["IDE skills directory"]
    skill --> policy["List it in docs/governance/skills-policy.md"]
    what -- Subagent --> agent["IDE agents directory"]
    what -- Command --> command["IDE commands directory, no spine- prefix"]
    what -- Rule --> rule["AGENTS.md, Project-specific instructions"]
    what -- "Hooks, MCP, settings" --> config["IDE configuration files"]
```

| Extension | Where it lives | What Spine needs |
|---|---|---|
| Project skill | The IDE's skills directory, e.g. `.claude/skills/<name>/SKILL.md` | An entry in `docs/governance/skills-policy.md` with the path to its `SKILL.md` |
| Subagent | The IDE's agents directory, e.g. `.claude/agents/<name>.md` | Nothing; mention it in `AGENTS.md` if the team is expected to use it |
| Project command | The IDE's commands directory, without the `spine-` prefix | Nothing |
| Project rule | `AGENTS.md`, under "Project-specific instructions" | Nothing; it takes precedence over `.spine/rules/` |
| Hooks, MCP servers, settings | The IDE's configuration, e.g. `.claude/settings.json` | Nothing |

The paths above are the Claude Code ones. For another IDE, use its equivalent directory. Commit these files
like the rest, so teammates get them with `git pull`.

### Adding a skill

1. Create the skill where the IDE expects it, for example `.claude/skills/<name>/SKILL.md`.
2. List it in `docs/governance/skills-policy.md`, under the section for the project's additional skills, with
   the path to its `SKILL.md`. That file also holds the criteria for adding and removing skills.
3. Use it. To make it the skill a task is executed with, set `execution_skill: <name>` in the task file's
   frontmatter. `/spine-execute` does not use a skill the policy does not list.

The nine Spine skills are not registered as native IDE skills. Agents read them from
`.spine/skills/<name>/SKILL.md` when a command or the policy calls for them.

### Adding a subagent

Create it in the IDE's agents directory, for example `.claude/agents/<name>.md`. Spine neither installs nor
validates subagents. A subagent that does delivery work should follow the same rules as everyone else: point
it at `AGENTS.md` (which leads to `.spine/rules/` and the memory bank) instead of copying instructions into it.

### Adding commands and rules

- **Commands** — add them to the IDE's commands directory under any name that does not start with `spine-`.
  That prefix belongs to the installer, which rewrites and removes `spine-*.md` pointers.
- **Rules** — write them in `AGENTS.md`, under "Project-specific instructions". When instructions conflict,
  the order is: the user's request, then `AGENTS.md`, then `.spine/rules/`.

### Changing Spine itself

To change a Spine rule, command, or skill, change it in the Spine clone and run `install` again (see
[Contributing](#contributing)). An edit made directly under `.spine/` is overwritten by the next `install`,
and until then `doctor` fails with `content differs from the installed version`.

## Updating

Update your Spine clone, then run `install` again. Without `--ides` it reuses the previous selection:

```
python C:\tools\spine\spine.py install C:\dev\my-project
```

Running it twice in a row changes nothing. Files that left the Spine clone are removed from `.spine/`, and
dropping an IDE from `--ides` removes its untouched pointers. Commit the result so teammates get the update.

## Health checks

From the project root:

```
python .spine/spine.py doctor
python .spine/spine.py doctor --task docs/memory/active_tasks/PROJ-123-social-login.md
```

`doctor` checks that `.spine/` is a real directory that matches its manifest, that files are UTF-8 without BOM,
that every selected IDE has one pointer per command, that the memory bank seed files exist, that `AGENTS.md`
references `.spine/rules`, and that no two tasks share a `task_id`. `--task` validates one task file against
the task contract.

Exit code 0 means OK (warnings allowed); 1 means at least one error. `OK:` lines go to stdout;
`ERROR:`, `WARNING:`, and `NOTE:` lines go to stderr.

## Troubleshooting

| Message | Cause | Fix |
|---|---|---|
| `--ides is required on the first install` | The project has no `.spine/manifest.json` yet. | Pass `--ides`, for example `--ides claude,cursor`. |
| `unknown IDE(s): ...` | A key in `--ides` is not supported. | Use `claude`, `cursor`, `antigravity`, or `windsurf`. |
| `install must run from the Spine clone` | `install` was run from the copy at `.spine/spine.py`. | Run `install` from your Spine clone; the copy in the project is for `doctor`. |
| `.spine is a link or a file (legacy install?)` | `.spine` was left by an old installer. | Remove it and install again. See [Migrating](#migrating-from-the-shell-installers). |
| `refusing to write through a link` | A managed path is a symlink or junction. | Replace the link with a real directory, or remove it, and install again. |
| `... was edited locally; not overwritten (use --force)` | A command pointer was changed by hand (`SKIP`). | Keep your edit, or pass `--force` to restore the generated pointer. |
| `AGENTS.md exists and does not reference .spine/rules` | The project had its own `AGENTS.md`. | Merge `.spine/AGENTS.snippet.md` into it by hand. |
| `content differs from the installed version` | A file under `.spine/` was edited. | Run `install` again; change Spine in the clone, not in the project. |
| `unreadable manifest` | `.spine/manifest.json` is damaged. | Delete it and run `install` again with `--ides`. |
| `generated file(s) have CRLF line endings` | Git converts line endings on checkout. | Add `* text=auto eol=lf` to the project's `.gitattributes`. |
| `.gitignore ignores a path Spine expects to be committed` | `.spine` or an IDE directory is ignored. | Remove that line from `.gitignore` and commit the files. |
| `duplicate task_id ...` | Two task files share one tracker ID. | Keep one file per task; delete or rename the other. |

## Migrating from the shell installers

Earlier versions of Spine were installed with `install.sh` / `install.ps1` and relied on symlinks. `spine.py`
replaces them and writes real files only. To move a project over:

1. Remove the old `.spine` from the project, whether it is a link or a directory. `install` refuses a linked
   `.spine`, and files left in an old directory are not in the manifest, so they would never be cleaned up.
2. Remove the Spine symlinks left in the IDE directories (`.claude/`, `.cursor/`, ...). `install` refuses to
   write through a link.
3. Run `install` with `--ides` as in [Quick start](#quick-start). Your existing `AGENTS.md` and `docs/` are
   kept as they are.
4. Run `python .spine/spine.py doctor`. It warns about leftovers from the old installers (`.spine-vendor`,
   `opencode.json`, `.opencode`); delete the ones your project does not use for anything else.

## Uninstalling

There is no uninstall command. Remove the generated files by hand:

1. Delete `.spine/`.
2. Delete the `spine-*.md` pointers from each IDE directory (`.claude/commands/`, `.cursor/commands/`,
   `.agents/workflows/`, `.windsurf/workflows/`).

`AGENTS.md`, `CLAUDE.md`, and `docs/` belong to the project. Keep them, or remove the Spine references from
them, as the team prefers.

## Contributing

Run the tests from the Spine repo root:

```
pytest tests/
```

Try the installer against a scratch directory before changing it:

```
python spine.py install /path/to/scratch --ides claude,cursor --dry-run
python spine.py install /path/to/scratch --ides claude,cursor
python spine.py doctor /path/to/scratch
```

See [`AGENTS.md`](AGENTS.md) for the repository layout, the code style, and the contract `spine.py` must keep.

## Credits

This repository is a fork of [SPINE](https://github.com/fjuste/spine) by Fernando Juste, adapted for
teams working on locked-down Windows machines.

SPINE was inspired by practical community work, especially:

- [antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills)
- [Cursor Memory Bank (gist)](https://gist.github.com/ipenywis/1bdb541c3a612dbac4a14e1e3f4341ab)
