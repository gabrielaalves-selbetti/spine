"""Cross-file invariants for Memory Bank task contract alignment."""

from pathlib import Path
from types import ModuleType


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_task_template_has_implementation_plan_section() -> None:
    text = _read("templates/docs/memory/active_tasks/_task-template.md")
    assert "## Implementation Plan" in text
    assert "do not use inline" in text.lower() or "metadata lives in frontmatter" in text.lower()


def test_task_template_satisfies_the_validator(spine: ModuleType, tmp_path: Path) -> None:
    task = tmp_path / "PROJ-000-descriptive-name.md"
    task.write_bytes(Path("templates/docs/memory/active_tasks/_task-template.md").read_bytes())

    report = spine.validate_task(task)

    assert report.passed, report.lines
    assert report.warnings == 0


def test_only_the_template_lives_in_template_active_tasks() -> None:
    active = Path("templates/docs/memory/active_tasks")
    assert sorted(p.name for p in active.glob("*.md")) == ["_task-template.md"]


def test_writing_plans_aligns_with_template() -> None:
    text = _read("skills/writing-plans/SKILL.md").lower()
    assert "_task-template" in text
    assert "implementation plan" in text
    assert "superpowers:executing-plans" not in text
    assert "docs/memory/active_tasks/" in text
    assert "python .spine/spine.py doctor --task" in text


def test_executing_plans_reads_frontmatter_and_impl_plan() -> None:
    text = _read("skills/executing-plans/SKILL.md").lower()
    assert "frontmatter" in text
    assert "implementation plan" in text
    assert "docs/memory/active_tasks/" in text
    super_lines = [
        line for line in text.splitlines() if "superpowers:" in line
    ]
    assert super_lines, "expected explicit rejection of superpowers handoff"
    assert all("do not" in line for line in super_lines)


def test_spine_plan_lists_implementation_plan() -> None:
    text = _read("commands/spine-plan.md")
    assert "## Implementation Plan" in text
    assert "Plan contract checklist" in text
    assert "Contract validation" in text
    assert "python .spine/spine.py doctor --task" in text
    assert "py -3" in text


def test_spine_execute_reads_implementation_plan() -> None:
    text = _read("commands/spine-execute.md")
    assert "## Implementation Plan" in text


def test_spine_harvest_and_execute_share_frontmatter_fields() -> None:
    execute = _read("commands/spine-execute.md").lower()
    harvest = _read("commands/spine-harvest.md").lower()
    for field in ("frontmatter", "task_id", "branch", "base", "tags"):
        assert field in execute, f"spine-execute missing {field}"
        assert field in harvest, f"spine-harvest missing {field}"


def test_memory_bank_rule_documents_implementation_plan() -> None:
    text = _read("rules/02-memory-bank.md")
    assert "## Implementation Plan" in text
    assert "Anti-patterns" in text


def test_branch_types_match_everywhere(spine: ModuleType) -> None:
    listed = ", ".join(f"`{kind}`" for kind in spine.TASK_BRANCH_TYPES)
    for path in (
        "rules/02-memory-bank.md",
        "commands/spine-plan.md",
        "commands/spine-execute.md",
        "skills/writing-plans/SKILL.md",
    ):
        assert listed in _read(path), path
