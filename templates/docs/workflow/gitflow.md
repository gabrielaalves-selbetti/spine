# Operational GitFlow

## Goal
Standardize a simple, safe, and repeatable cycle for team development, without overengineering.

## Official Branches
- `main`: canonical code branch.
- `develop`: continuous integration of finished deliveries.
- `staging`: pre-production validation.
- `production`: mirror of what is in production.

## Temporary Branches
Every work branch follows `<type>/<task-id>`, where `<task-id>` is the ticket ID in the team tracker.

- `feat/<task-id>`: new feature.
- `fix/<task-id>`: non-urgent fix.
- `docs/<task-id>`, `refactor/<task-id>`, `test/<task-id>`, `chore/<task-id>`: other kinds of work (same vocabulary as Conventional Commits).
- `hotfix/<task-id>`: urgent production fix.
- `release/<task-id>`: stabilization for delivery.

## Standard Delivery Flow
1. Create `<type>/<task-id>` from `develop`.
2. Implement with a test (or test plan) before the Pull Request.
3. Update memory bank v2.1 on the branch itself (`progress.md` delivery log, `learnings.md`, `decision-log.md`; task in `completed_tasks/` after harvest).
4. Open a Pull Request from `<type>/<task-id>` to `develop`; the merge happens after team review.
5. Promote `develop` to `staging`.
6. Run the release checklist.
7. Promote `staging` to `production`.
8. Sync `production` with `main`.

## Hotfix Flow
1. Create `hotfix/<task-id>` from `production` (or `main` if it mirrors production).
2. Fix + add a regression test.
3. Merge into `production` and `main`.
4. Reapply on `develop` to avoid divergence.

## Safety Rules
- No direct commits to `main`/`production`/`staging`/`develop`.
- No local merge of a work branch into `develop`: integration goes through a Pull Request.
- Every delivery needs test evidence.
- Every delivery must update the memory bank.
- Without clear acceptance criteria, the task does not start.
- Every task has an `owner` and a tracker ID.

## Naming Conventions
- Feature: `feat/PROJ-123`
- Fix: `fix/PROJ-456`
- Hotfix: `hotfix/PROJ-789`
- Release: `release/PROJ-800`

## Promotion Checklist (staging -> production)
- Scope tests executed.
- Minimum regression executed.
- Memory bank updated.
- Cycle learnings recorded.
