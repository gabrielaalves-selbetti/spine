"""Memory Bank v2.1 contract tests (stdlib path reads)."""

from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_memory_bank_rule_v21_structure() -> None:
    text = _read("rules/02-memory-bank.md")
    assert "MEMORY BANK V2.1" in text
    assert "completed_tasks/" in text
    assert "learnings.md" in text
    assert "tiered SYNC" in text.lower() or "Tiered SYNC" in text
    assert "memory-tags-policy.md" in text
    assert "task_id:" in text
    assert "owner:" in text


def test_progress_template_has_delivery_log() -> None:
    text = _read("templates/docs/memory/ledger/progress.md")
    assert "## Current state" in text
    assert "## Delivery log" in text
    assert "**Tags:**" in text
    assert "In flight" not in text


def test_learnings_template_has_learn_entry() -> None:
    text = _read("templates/docs/memory/ledger/learnings.md")
    assert "LEARN-001" in text
    assert "**Tags:**" in text
    assert "**Recurrences:**" in text


def test_task_template_obsidian_frontmatter() -> None:
    text = _read("templates/docs/memory/active_tasks/_task-template.md").replace("\r\n", "\n")
    assert text.startswith("---\n")
    assert "tags:" in text
    assert "status:" in text
    assert "goal:" in text
    assert "owner:" in text
    assert "branch:" in text
    assert "base:" in text
    assert "roadmap_idea" not in text
    assert "## Implementation Plan" in text


def test_writing_plans_skill_no_superpowers_header() -> None:
    text = _read("skills/writing-plans/SKILL.md")
    assert "_task-template" in text
    assert "superpowers:executing-plans" not in text


def test_memory_tags_policy() -> None:
    text = _read("templates/docs/governance/memory-tags-policy.md")
    assert "1–5 tags" in text or "1-5 tags" in text
    assert "area/" in text
    assert "type/" in text


def test_spine_harvest_v21_contract() -> None:
    text = _read("commands/spine-harvest.md").lower()
    assert "delivery log" in text
    assert "learnings.md" in text
    assert "git mv" in text
    assert "completed_tasks/" in text
    assert "memory-tags-policy" in text


def test_spine_harvest_hands_off_to_pull_request() -> None:
    text = _read("commands/spine-harvest.md")
    assert "git push -u origin <branch>" in text
    assert "Pull Request" in text
    assert "**do not** delete the branch" in text


def test_spine_plan_v21_contract() -> None:
    text = _read("commands/spine-plan.md").lower()
    assert "completed_tasks/" in text
    assert "frontmatter" in text
    assert "_task-template.md" in text
    assert "native plan" in text
    assert "implementation plan" in text


def test_spine_plan_requires_tracker_id_and_owner() -> None:
    text = _read("commands/spine-plan.md")
    assert "Never invent an ID" in text
    assert "`owner:`" in text
    assert "<type>/<task-id>" in text


def test_readme_memory_bank_v21_section() -> None:
    text = _read("README.md")
    assert "Memory Bank v2.1" in text
    assert "completed_tasks/" in text
    assert "learnings.md" in text


def test_agents_memory_bank_v21() -> None:
    text = _read("AGENTS.md")
    assert "Memory Bank v2.1" in text
    assert "completed_tasks/" in text or "active_tasks/" in text
