# AGENTS.md — Spine Agent Operating Guide

This file provides instructions for agentic coding agents working **on the Spine repository** itself.

**Scope:**
- **This file** — operating guide for the Spine repo and framework maintenance.
- **Consumer projects** — get their own `AGENTS.md` from [`templates/AGENTS.md`](templates/AGENTS.md). Do **not** copy this file into consumer repos.
- **Public setup guide** — [`README.md`](README.md).

Spine is a workflow framework for coding agents working in teams: Markdown rules, commands, and skills, plus one Python script (`spine.py`) that installs them into a project.

---

## 1. Repository Layout

```
spine/
├── spine.py                # The only installer: `install` and `doctor` (stdlib only, Python 3.9+)
├── templates/
│   ├── AGENTS.md           # Hub seeded once into consumer projects
│   └── docs/               # Seeded once into consumer `docs/` (never overwritten)
│       ├── memory/         # global/, ledger/, active_tasks/, completed_tasks/
│       ├── governance/     # skills-policy, memory-tags-policy
│       ├── quality/        # guardrails
│       └── workflow/       # GitFlow and delivery cycle guides
├── commands/               # Command sources (/spine-plan, /spine-bootstrap, ...)
├── rules/                  # Source-of-truth rules (01-core-protocol, 02-memory-bank, 03-code-quality)
├── skills/                 # Workflow skills (each has a SKILL.md)
├── docs/                   # Memory bank of the Spine repository itself (not shipped)
└── tests/                  # pytest (conftest.py + unit/)
```

`.gitignore` excludes local agent configs at the root: `.cursor/`, `.claude/`, `.agents/`, `.windsurf/`, `CLAUDE.md`.

---

## 2. Build / Lint / Test Commands

Spine has no compiled artifact. Run tests from the Spine repo root:

```bash
pytest tests/
pytest -v -x tests/unit/test_<module>.py::test_<function_name>
```

Try the installer against a scratch directory:

```bash
python spine.py install /path/to/scratch --ides claude,cursor --dry-run
python spine.py install /path/to/scratch --ides claude,cursor
python spine.py doctor /path/to/scratch
```

---

## 3. Code Style Guidelines

### Language and Encoding
- All code, comments, docstrings, commit messages, and generated file content must be in **English**.
- Exception: preserve user-provided literals (translations, UI copy) exactly as given.
- All files are UTF-8 with LF line endings (`.gitattributes` enforces LF).

### Imports
Order enforced by **isort**:
1. Standard library
2. Third-party packages
3. Local application imports

Never mix groups; use a blank line between each group.

### Type Annotations
- **Strict by default**: annotate all function parameters and return types.
- Avoid bare `Any`, `object`, or unparameterized `dict`; justify exceptions in a comment.
- Prefer `dict[str, int]` over `Dict[str, int]`.
- Local variables may rely on inference; public API boundaries must be explicit.

### Naming Conventions
- Functions / methods: `snake_case`
- Variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Test functions: behavior sentence (e.g., `test_second_install_is_byte_identical_noop`)

### Docstrings
- Google style, mandatory on all **public** functions, methods, and classes.
- Include `Args:`, `Returns:`, and `Raises:` sections where applicable.

### Formatting
- Prefer short, cohesive functions; one logical concern per function.
- No magic numbers — define named constants.

---

## 4. `spine.py` contract

Changes to the installer must keep all of these true (the tests in `tests/unit/test_spine_install.py` and `test_spine_doctor.py` enforce them):

- **Single file, standard library only, Python 3.9+.** No syntax or stdlib API newer than 3.9.
- **No network, no subprocess, no writes outside the target project.** Every write goes through `safe_path`, which refuses paths that leave the target or pass through a symlink/junction.
- **Real files only.** No symlinks are created anywhere.
- **UTF-8, LF, no BOM** for every generated file, whatever the line endings of the source checkout.
- **Idempotent.** Running `install` twice changes no byte. The manifest has sorted keys and no timestamp.
- **`--dry-run`** computes the same plan and writes nothing.
- **Three file classes:**

| Class | Paths in the target | Rule |
|---|---|---|
| Mirror | `.spine/**` | Always equals the source; stale files listed in the previous manifest are removed |
| Pointer | per-IDE command files | Rewritten when missing or untouched; a local edit is kept (`SKIP`) unless `--force` |
| Seed | `AGENTS.md`, `CLAUDE.md`, `docs/**` | Created only when missing; never overwritten, not even with `--force` |

- **IDE paths** live in one table, `IDE_LAYOUTS`. An entry stays `verified=False` (reported as `A VERIFICAR`) until its paths were checked by hand against the IDE.
- `commands/spine-promote.md` is maintainer-only and listed in `INTERNAL_COMMANDS`; it must never be installed into a consumer project.

---

## 5. What ships to a consumer project

```
PROJECT_ROOT/
├── AGENTS.md                  seed — hub that points to .spine/rules/
├── CLAUDE.md                  seed (Claude Code only) — "@AGENTS.md"
├── .spine/                    mirror — single source of truth
│   ├── spine.py               doctor / doctor --task
│   ├── manifest.json
│   ├── commands/  rules/  skills/
├── docs/                      seed — memory bank, governance, quality, workflow
└── <ide dir>/                 pointers — one thin file per command
```

Updating a consumer project = running `python spine.py install <project>` again from the Spine clone.

---

## 6. Delivery model the rules and commands implement

- **Team workflow** (4+ people): work reaches `develop` only through a Pull Request; `/spine-harvest` stops at `git push`.
- **Task ID** is the tracker ID (`PROJ-123`); file `docs/memory/active_tasks/<task-id>-<name>.md`; mandatory `owner`.
- **Branches:** `main`, `develop`, `staging`, `production`; work branches `<type>/<task-id>` with `<type>` in `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `hotfix`, `release`.
- **Memory Bank v2.1:** canonical spec in `rules/02-memory-bank.md`; tags in `templates/docs/governance/memory-tags-policy.md`.

When a rule, command, skill, or template changes one of these, change the others and `validate_task` in `spine.py` in the same delivery.

### Commands

- `/spine-bootstrap` — initial assessment and memory bank fill
- `/spine-plan` — task plan in the memory bank (tracker ID required; conditional `grill-me` discovery)
- `/spine-execute` — implement the active task with validation
- `/spine-harvest` — consolidate learnings, close the task, hand off to a Pull Request
- `/spine-commit` — commit with branch safety checks
- `/spine-promote` — maintainer-only promotion cascade for this repository (not installed)

## headroom (Context Compression)

Token budget is a constrained resource. Use Headroom MCP tools proactively to manage it.

Rules:
- Before reasoning over any tool output, file content, or search result larger than ~2000 tokens, call `headroom_compress` to shrink it and keep only the compressed form plus its hash
- When you need the original details later, call `headroom_retrieve` with the hash (optionally filtered by `query`)
- Prefer compressing large `read`, `grep`, `glob`, `bash`, and web fetch results rather than keeping the full text in context
- Do NOT compress small outputs (< ~2000 tokens) or content you will reference immediately in the next turn — the compression overhead is not worth it
