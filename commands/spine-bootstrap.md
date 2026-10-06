---
description: Deep project assessment and agent-optimized memory bank fill after spine.py install
---

# Slash Command: /spine-bootstrap

Act as the project's Initial Assessment Architect.

**Goal:** Build a complete, **agent-ready** project context layer. Deep assessment of the source code, then fill memory bank documents with maximal detail for **agent consumption** (tiered SYNC), not human storytelling.

**Bootstrap is not planning.** Do not create active tasks, plans, or modify `roadmap.md`. Delivery starts with `/spine-plan`.

**Optional context (user arguments):** Non-empty free text passed with the command = project briefing (domain, stack, constraints, stakeholders, links). Highest priority when filling files; do not contradict existing valid content.

**Precondition:** `python spine.py install` completed for this project (`.spine/`, seeded `docs/`, `AGENTS.md`, command pointers).

---

## Step 0 — Setup boundary and readiness

Run from project root:

```bash
python .spine/spine.py doctor
```

Standard library only, Python 3.9+ (if `python` is unavailable, use `py -3`).

**On success:** proceed to Step 1. Report any `WARNING:` and `NOTE:` lines in the final summary.

**On failure:**

1. Stop assessment.
2. List the `ERROR:` lines from the output.
3. Ask the user to run `python spine.py install <project-root>` from their Spine clone in a terminal, reload the IDE, and retry.

**Forbidden (agent must never):**

- Copy/seed `docs/` (downloads, creating missing template files)
- Edit anything under `.spine/` (managed by `spine.py`)
- Modify `docs/memory/ledger/roadmap.md`
- Create or modify task files in `docs/memory/active_tasks/`

**Re-bootstrap:** Safe to re-run. Idempotent enrichment — replace placeholders, append non-conflicting detail, preserve valid existing content.

---

## Step 1 — Deep assessment (mandatory, before any writes)

Goal: **complete project understanding**. Do not write memory bank files until assessment is sufficient.

**Discovery order:**

1. User arguments (if non-empty)
2. **Source and configs:** README, manifests, CI, infra, entry points, layer structure, tests, env patterns
3. Existing memory bank (re-bootstrap) — conflicts → **Gaps**, do not silently overwrite

**Assessment must cover:**

| Area | Feeds |
|------|--------|
| Stack (languages, frameworks, DB, queue, infra, deploy) | `system-patterns.md`, `tech-context.md` |
| Architecture (layers, data flow, external APIs) | `system-patterns.md` |
| Domain terms and bounded contexts | `domain-glossary.md` |
| Dev workflow (install, run, test commands) | `tech-context.md` |
| **Alterations** (custom payment, auth, webhooks vs platform default) | `system-patterns.md` § Project-Specific Alterations + `decision-log.md` |
| **Risks** (fragile integrations, missing tests, deprecated deps) | `tech-context.md` § Known Risks |
| **Opportunities** (unplanned improvements, not scheduled work) | `product-context.md` § Known Opportunities (unplanned) |
| Scope, goals, boundaries | `project-brief.md`, `product-context.md` |
| Git branches vs Spine GitFlow (`develop`, `staging`, `production`, `main` + `<type>/<task-id>`) | `tech-context.md`, summary **Gaps** if mismatch |
| Task tracker in use and its ID format | `tech-context.md` |

**Hunt signals:** grep `TODO|FIXME|HACK|override|custom`; payment/checkout/auth/shipping directories; user arguments.

**Depth bar:** If any global section would still read like `[Fill in]` after Step 2, assessment was insufficient — explore deeper.

**No discovery interview:** Unresolved domain ambiguity → **Gaps** + recommend `/spine-plan` with discovery triggers when delivery starts.

---

## Step 2 — Memory Bank bootstrap (global) — agent-optimized

**Primary audience: agents.** Structure for SYNC, grep, and navigation.

| Principle | Guidance |
|-----------|----------|
| Structure | Predictable headings per `.spine/rules/02-memory-bank.md` Core SYNC |
| Specificity | Concrete paths, modules, config files, CLI commands |
| Glossary | Term + definition + code location hint |
| Architecture | Layer map, request/job flow, key files/classes |
| Alterations | Table in `system-patterns.md`; non-obvious WHY → `decision-log.md` entry; link both ways |
| Risks | Bullet list with impact and related paths |
| Opportunities | Unplanned improvements only (not roadmap milestones) |
| Cross-links | `See tech-context.md § Known Risks` |
| Scannable | Bullets and short paragraphs; no marketing tone |
| English | All generated content |
| Depth | **Maximize detail**; completeness over brevity |

**Fill rules:**

| Signal | Action |
|--------|--------|
| Placeholder (`[Fill in]`, empty section, template boilerplate) | Replace with detailed inferred content |
| Valid project-specific content already present | Preserve; append only non-conflicting detail |
| Conflict (repo vs user arguments vs existing doc) | Do not overwrite; record in **Gaps** |
| `domain-glossary.md` | Add terms; never delete existing entries |
| `decision-log.md` | Append bootstrap baseline entry (date, baseline established, key facts + WHY) |

**Files to fill:**

- `docs/memory/global/project-brief.md`
- `docs/memory/global/product-context.md` (incl. § Known Opportunities (unplanned))
- `docs/memory/global/domain-glossary.md`
- `docs/memory/global/system-patterns.md` (incl. § Project-Specific Alterations)
- `docs/memory/global/tech-context.md` (incl. § Known Risks)
- `docs/memory/global/decision-log.md`

If a section is missing in an older seeded file, add the section during fill.

---

## Step 3 — Memory Bank bootstrap (ledger) — limited scope

**In scope:**

- `docs/memory/ledger/progress.md` — update **Current state** only: bootstrap complete, memory bank baseline ready; **never wipe Delivery log**
- `docs/memory/ledger/learnings.md` — leave empty unless repo evidence supports an incident-style entry; flag in **Gaps** if file missing after install

**Out of scope:**

- **`docs/memory/ledger/roadmap.md` — do not modify** (maintained by the team)
- **Task files in `active_tasks/` — do not create**

---

## Step 4 — Mandatory summary

Always include:

- **Assessment coverage:** key dirs and configs explored; confidence level
- **Memory bank files filled:** Each updated `global/*` and ledger file with one-line depth note
- **Counts:** alterations documented, risks listed, opportunities captured
- **Intentionally untouched:** `roadmap.md` (not bootstrap scope)
- **Created vs. updated vs. preserved**
- **Gaps:** Credentials, business rules, stakeholder intent, branch policy exceptions, unresolved domain terms
- **Setup status:** `spine.py doctor` result, including warnings and `A VERIFICAR` notes
- **GitFlow note:** existing branches vs Spine target (`develop`, `staging`, `production`, `main` + `<type>/<task-id>`)
- **Next step:** `/spine-plan <task-id> <goal>` — bootstrap does not produce plans or tasks
- **Re-bootstrap:** idempotent enrichment only

Memory bank changes made by bootstrap are regular file changes: they reach the team through a branch and a Pull Request like any other delivery.

If user asks for a plan or task: "Bootstrap builds agent context only. Use `/spine-plan` for delivery planning."

---

## Knowledge mapping (reference)

| Concept | Primary home | When |
|---------|--------------|------|
| Project-specific alteration | `system-patterns.md` § Project-Specific Alterations | Bootstrap |
| WHY of alteration | `decision-log.md` | Bootstrap |
| Known risk | `tech-context.md` § Known Risks | Bootstrap |
| Opportunity (unplanned) | `product-context.md` § Known Opportunities | Bootstrap |
| Incident / recurrence | `learnings.md` | `/spine-harvest` only |
| Scheduled milestone | `roadmap.md` | Team, by hand |

---

## Acceptance criteria (command behavior)

- [ ] Runs `python .spine/spine.py doctor` before assessment
- [ ] Deep assessment of source code before writing
- [ ] Fills `global/*` and ledger (`progress.md`, `learnings.md` if applicable) with agent-optimized detail
- [ ] Documents alterations, risks, and opportunities when evidence exists
- [ ] Does **not** modify `roadmap.md`
- [ ] No installation side effects; no active task or plan creation
- [ ] Preserves valid existing content; conflicts → **Gaps**
- [ ] Summary includes counts, untouched files, gaps, and `/spine-plan` handoff
- [ ] All generated content in English
