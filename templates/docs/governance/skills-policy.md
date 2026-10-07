# Skills Policy

Tag policy for tasks, progress, and learnings: `docs/governance/memory-tags-policy.md`.

## Goal
Keep only skills that bring recurring value to the team workflow.

## Installed skills

`python spine.py install` copies every Spine skill into `.spine/skills/`. The agent reads `.spine/skills/<name>/SKILL.md` when a command or this policy points to the skill.

### Core (always in use)
- `writing-plans`
- `executing-plans`
- `test-driven-development`
- `systematic-debugging`
- `verification-before-completion`

### Workflow and Quality
- `gitflow`
- `testing-guidelines`
- `handoff-protocol`
- `grill-me` (conditional discovery — see Operating Guideline: Planning)

## Additional project skills
- Project-specific skills live outside `.spine/` (that folder is managed by `spine.py`) and must be listed here, with the path to their `SKILL.md`, to be usable as `execution_skill`.
- Entry criteria: recurring use in real work, measurable reduction of rework, risk, or time, and alignment with the project's main stack.
- Removal criteria: no recurring use in the last 30 days, overlap with an already active skill, or pushing simple tasks toward overengineering.

## Operating Guideline: Planning

Use this rule to avoid ambiguity between discovery and plan structuring:

- **Fixed pipeline:** `grill-me` (discovery, conditional) → `writing-plans` (fills `_task-template.md`, mandatory) → `/spine-plan` gate.
- **Task contract:** YAML frontmatter + fixed sections; optional Task/Step detail in `## Implementation Plan` (omit when there are ≤3 acceptance criteria).
- **Simple default:** clear, single-domain scope → skip `grill-me`, go straight to `writing-plans`.
- **Escalate discovery:** use `grill-me` when the scope is ambiguous, multi-domain, or has open architecture/security/schema/infra decisions.

### When to use `grill-me`
- Ambiguous or broad scope (e.g. "improve performance").
- Multiple domains in the same delivery (e.g. backend + infra + UI).
- Unresolved architecture or security decisions.
- Explicit opt-in in `/spine-plan`: `grill me`, `grill:`, `grill -`, `grill with docs`, `grill:docs`, `stress-test`, `challenge this`.
- Opt-in with domain documentation: `grill with docs` or `grill:docs` — same skill, expecting inline updates to `domain-glossary.md` and `decision-log.md`.

### When to skip `grill-me`
- Clear scope, single deliverable, single domain.
- Explicit opt-out: `skip discovery`, `no grill`, `direct plan`.

### Tie-breaker (anti-overengineering)
- If the scope already defines MVP, out-of-scope, and main domain, do not use `grill-me`.
- `grill-me` asks one question at a time; do not write the full plan until discovery ends.
- Record decisions in `## Discovery notes` in the active task file before `writing-plans`.
- **Knowledge promotion:** task scope decisions → `## Discovery notes`; canonical domain terms → `domain-glossary.md`; architecture decisions (triple criterion: hard to reverse, surprising without context, real trade-off) → `decision-log.md`.

### Relation to other workflow skills
- **`writing-plans`:** always after discovery (or after skipping it). Fills `_task-template.md` (frontmatter + sections); Task/Step only in `## Implementation Plan`.
- **`executing-plans`:** reads the frontmatter and Implementation Plan; stops at `REVIEW` — `/spine-harvest` closes the delivery.
- **`handoff-protocol`:** applies when the task changes owner or agent; does not replace scope discovery.

## Syncing in Consumer Projects

This file is seeded into `docs/governance/skills-policy.md` by `python spine.py install` and is never overwritten afterwards. When updating Spine, manually review the differences against `templates/docs/governance/skills-policy.md` in the Spine clone and adopt what is relevant.
