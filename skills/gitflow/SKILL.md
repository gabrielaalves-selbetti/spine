---
name: gitflow
description: "Reference for Git branching strategy — branch structure, naming, and promotion flow"
risk: low
source: spine
date_added: "2026-04-29"
---

# GitFlow Reference

## When to Use
- When creating or managing branches
- When promoting code through staging/production
- When unsure about branch naming or merge strategy

## Branch Structure

| Branch | Purpose | Origin | Merges to |
|---|---|---|---|
| `production` | Live code | `staging` | — |
| `main` | Canonical branch; stable mirror of `production` | `production` | — |
| `staging` | QA and pre-production | `develop` | `production` |
| `develop` | Integration branch | `main`/`production` | `staging` |
| `feat/*`, `fix/*`, `docs/*`, `refactor/*`, `test/*`, `chore/*` | Task work | `develop` | `develop` |
| `release/*` | Release stabilization | `develop` | `develop` |
| `hotfix/*` | Urgent fixes | `production` | `production`, `main`, `develop` |

## Rules
1. Every change starts with: `git checkout develop && git pull && git checkout -b <type>/<task-id>`
2. Atomic commits — one logical change per commit
3. Never push directly to `production`, `main`, `staging`, or `develop`
4. Never `git push --force`
5. Merge to `develop` requires a Pull Request reviewed by the team
6. Memory bank must be updated in the task branch, before the Pull Request

## Naming
- Work branches: `<type>/<task-id>`, where `<task-id>` is the tracker ID (e.g., `feat/PROJ-123`, `fix/PROJ-456`)
- `<type>` follows Conventional Commits: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Hotfixes: `hotfix/<task-id>` (e.g., `hotfix/PROJ-789`)
- Releases: `release/<task-id>` (the tracker ID of the release ticket)

## Promotion Flow
`<type>/<task-id>` → `develop` → `staging` → `production` → `main`

## Reference
Full operational guide: `docs/workflow/gitflow.md`
