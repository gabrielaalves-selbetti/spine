# Quality Guardrails

## Goal
Keep deliveries under control with tests and regression prevention.

## Base Rule
Every task must include:
1. Execution plan.
2. Test plan.
3. Evidence that the tests ran.

## Minimum Test Plan per Task
- **Positive case**: the expected path works.
- **Negative case**: invalid input / controlled error.
- **Regression**: confirms critical existing behavior did not break.

## Test Types (apply according to scope)
- Unit: business rules and critical functions.
- Integration: services, database, and contracts.
- E2E/functional: critical user flows (when applicable).
- Post-release smoke: sanity check in production/staging.

## Merge Gate
- Acceptance criteria met.
- Test plan executed.
- No open critical failures.
- Memory bank updated with learnings.

## Mandatory Learning Record
For incidents, bugs, and rework, record in `docs/memory/ledger/learnings.md` (a `LEARN-NNN` entry with **Tags** per `docs/governance/memory-tags-policy.md`):
- Root cause.
- How to detect it early.
- Test that prevents recurrence.
- Operating rule added/adjusted.
