"""Behavioral tests for `spine.py doctor` and `spine.py doctor --task`."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from conftest import REPO_ROOT, SCRIPT

VALID_TASK = """---
task_id: PROJ-123
title: Example task
goal: Prove the validator works
status: PLANNING
owner: maria.silva
tags:
  - type/feature
  - area/tooling
branch: feat/PROJ-123
base: develop
execution_skill: executing-plans
created_at: 2026-10-06
updated_at: 2026-10-06
completed_at:
related_learnings: []
---

# PROJ-123-example

## Objective

Do the thing.

## Acceptance Criteria (verifiable, TDD-ready)

- [ ] It works

## Implementation Plan

### Task 1: First step
"""


@pytest.fixture
def installed(spine: ModuleType, fake_source: Path, target: Path) -> Path:
    spine.install(fake_source, target, ["claude", "cursor"])
    return target


def _text(report: object) -> str:
    return "\n".join(report.lines)  # type: ignore[attr-defined]


def _task(tmp_path: Path, content: str, name: str = "PROJ-123-example.md") -> Path:
    path = tmp_path / name
    path.write_bytes(content.encode("utf-8"))
    return path


# --- structure ---------------------------------------------------------------


def test_healthy_install_passes(spine: ModuleType, installed: Path) -> None:
    report = spine.doctor(installed)

    assert report.passed, _text(report)
    assert report.warnings == 0, _text(report)


def test_unverified_ide_is_flagged(spine: ModuleType, installed: Path) -> None:
    report = spine.doctor(installed)

    assert "A VERIFICAR" in _text(report)
    assert "Cursor" in _text(report)


def test_missing_spine_directory_fails(spine: ModuleType, target: Path) -> None:
    report = spine.doctor(target)

    assert not report.passed
    assert ".spine" in _text(report)


def test_missing_mirror_file_fails(spine: ModuleType, installed: Path) -> None:
    (installed / ".spine" / "rules" / "02-memory-bank.md").unlink()

    report = spine.doctor(installed)

    assert not report.passed
    assert "02-memory-bank.md" in _text(report)


def test_modified_mirror_file_fails(spine: ModuleType, installed: Path) -> None:
    (installed / ".spine" / "commands" / "spine-plan.md").write_bytes(b"tampered\n")

    report = spine.doctor(installed)

    assert not report.passed
    assert "spine-plan.md" in _text(report)


def test_crlf_on_disk_is_a_warning_not_an_error(spine: ModuleType, installed: Path) -> None:
    rule = installed / ".spine" / "rules" / "01-core-protocol.md"
    rule.write_bytes(rule.read_bytes().replace(b"\n", b"\r\n"))

    report = spine.doctor(installed)

    assert report.passed, _text(report)
    assert report.warnings == 1
    assert "CRLF" in _text(report)


def test_bom_is_an_error(spine: ModuleType, installed: Path) -> None:
    rule = installed / ".spine" / "rules" / "01-core-protocol.md"
    rule.write_bytes(b"\xef\xbb\xbf" + rule.read_bytes())

    report = spine.doctor(installed)

    assert not report.passed
    assert "BOM" in _text(report)


def test_missing_pointer_fails(spine: ModuleType, installed: Path) -> None:
    (installed / ".cursor" / "commands" / "spine-plan.md").unlink()

    report = spine.doctor(installed)

    assert not report.passed
    assert ".cursor/commands/spine-plan.md" in _text(report)


def test_edited_pointer_is_a_warning(spine: ModuleType, installed: Path) -> None:
    (installed / ".claude" / "commands" / "spine-plan.md").write_bytes(b"custom\n")

    report = spine.doctor(installed)

    assert report.passed
    assert report.warnings >= 1


def test_missing_seed_file_fails(spine: ModuleType, installed: Path) -> None:
    (installed / "docs" / "memory" / "ledger" / "progress.md").unlink()

    report = spine.doctor(installed)

    assert not report.passed
    assert "docs/memory/ledger/progress.md" in _text(report)


def test_agents_without_spine_reference_is_a_warning(spine: ModuleType, installed: Path) -> None:
    (installed / "AGENTS.md").write_bytes(b"# Unrelated\n")

    report = spine.doctor(installed)

    assert report.passed
    assert "AGENTS.md" in _text(report)
    assert report.warnings >= 1


def test_claude_md_without_agents_reference_is_a_warning(spine: ModuleType, installed: Path) -> None:
    (installed / "CLAUDE.md").write_bytes(b"# Unrelated\n")

    report = spine.doctor(installed)

    assert report.passed
    assert "CLAUDE.md" in _text(report)


def test_legacy_artifacts_are_warnings(spine: ModuleType, installed: Path) -> None:
    (installed / "opencode.json").write_bytes(b"{}\n")
    (installed / ".spine-vendor").write_bytes(b"mode=vendor\n")

    report = spine.doctor(installed)

    assert report.passed
    assert "opencode.json" in _text(report)
    assert ".spine-vendor" in _text(report)


def test_gitignore_hiding_managed_paths_is_a_warning(spine: ModuleType, installed: Path) -> None:
    (installed / ".gitignore").write_bytes(b"node_modules/\n.spine\n/.claude/\n")

    report = spine.doctor(installed)

    assert report.passed
    assert ".gitignore" in _text(report)
    assert report.warnings == 2


def test_duplicate_task_id_fails(spine: ModuleType, installed: Path) -> None:
    memory = installed / "docs" / "memory"
    (memory / "active_tasks" / "PROJ-123-example.md").write_bytes(VALID_TASK.encode("utf-8"))
    (memory / "completed_tasks" / "PROJ-123-other.md").write_bytes(VALID_TASK.encode("utf-8"))

    report = spine.doctor(installed)

    assert not report.passed
    assert "PROJ-123" in _text(report)


def test_real_repository_install_is_healthy(spine: ModuleType, target: Path) -> None:
    spine.install(REPO_ROOT, target, ["claude", "cursor", "antigravity", "windsurf"])

    report = spine.doctor(target)

    assert report.passed, _text(report)
    assert report.warnings == 0, _text(report)


def test_installed_copy_runs_doctor_from_project_root(spine: ModuleType, target: Path) -> None:
    spine.install(REPO_ROOT, target, ["claude"])

    result = subprocess.run(
        [sys.executable, ".spine/spine.py", "doctor"],
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "OK:" in result.stdout


# --- task contract -----------------------------------------------------------


def test_valid_task_passes(spine: ModuleType, tmp_path: Path) -> None:
    report = spine.validate_task(_task(tmp_path, VALID_TASK))

    assert report.passed, _text(report)
    assert report.warnings == 0


def test_numeric_tracker_id_is_accepted(spine: ModuleType, tmp_path: Path) -> None:
    content = VALID_TASK.replace("PROJ-123", "48213")

    report = spine.validate_task(_task(tmp_path, content, "48213-example.md"))

    assert report.passed, _text(report)


def test_task_without_owner_fails(spine: ModuleType, tmp_path: Path) -> None:
    report = spine.validate_task(_task(tmp_path, VALID_TASK.replace("owner: maria.silva\n", "")))

    assert not report.passed
    assert "owner" in _text(report)


def test_task_with_empty_owner_fails(spine: ModuleType, tmp_path: Path) -> None:
    report = spine.validate_task(_task(tmp_path, VALID_TASK.replace("owner: maria.silva", "owner:")))

    assert not report.passed
    assert "owner" in _text(report)


@pytest.mark.parametrize("branch", ["feature/PROJ-123", "PROJ-123", "feat/another-thing", "feat/PROJ-123-extra"])
def test_branch_outside_type_task_id_pattern_fails(spine: ModuleType, tmp_path: Path, branch: str) -> None:
    report = spine.validate_task(_task(tmp_path, VALID_TASK.replace("feat/PROJ-123", branch)))

    assert not report.passed
    assert "branch" in _text(report)


@pytest.mark.parametrize("kind", ["feat", "fix", "docs", "refactor", "test", "chore", "release"])
def test_every_branch_type_is_accepted(spine: ModuleType, tmp_path: Path, kind: str) -> None:
    report = spine.validate_task(_task(tmp_path, VALID_TASK.replace("feat/PROJ-123", f"{kind}/PROJ-123")))

    assert report.passed, _text(report)


def test_hotfix_expects_production_base(spine: ModuleType, tmp_path: Path) -> None:
    hotfix = VALID_TASK.replace("feat/PROJ-123", "hotfix/PROJ-123")

    from_develop = spine.validate_task(_task(tmp_path, hotfix))
    from_production = spine.validate_task(_task(tmp_path, hotfix.replace("base: develop", "base: production")))

    assert from_develop.passed and from_develop.warnings == 1
    assert from_production.passed and from_production.warnings == 0


def test_unexpected_base_is_a_warning(spine: ModuleType, tmp_path: Path) -> None:
    report = spine.validate_task(_task(tmp_path, VALID_TASK.replace("base: develop", "base: main")))

    assert report.passed
    assert report.warnings == 1


def test_file_name_must_start_with_task_id(spine: ModuleType, tmp_path: Path) -> None:
    report = spine.validate_task(_task(tmp_path, VALID_TASK, "007-example.md"))

    assert not report.passed
    assert "file name" in _text(report)


def test_invalid_task_id_fails(spine: ModuleType, tmp_path: Path) -> None:
    content = VALID_TASK.replace("PROJ-123", "PROJ 123")

    report = spine.validate_task(_task(tmp_path, content, "PROJ 123-example.md"))

    assert not report.passed
    assert "task_id" in _text(report)


def test_tag_count_ignores_other_lists(spine: ModuleType, tmp_path: Path) -> None:
    six = VALID_TASK.replace("  - area/tooling\n", "  - a\n  - b\n  - c\n  - d\n  - e\n")
    none = VALID_TASK.replace("  - type/feature\n  - area/tooling\n", "")
    other_list = VALID_TASK.replace("related_learnings: []", "related_learnings:\n  - LEARN-001\n  - LEARN-002")

    assert not spine.validate_task(_task(tmp_path, six)).passed
    assert not spine.validate_task(_task(tmp_path, none)).passed
    assert spine.validate_task(_task(tmp_path, other_list)).passed


BLOCK_TAGS = "tags:\n  - type/feature\n  - area/tooling\n"


def _with_tags(tags: str) -> str:
    return VALID_TASK.replace(BLOCK_TAGS, tags)


def test_inline_tags_are_counted(spine: ModuleType, tmp_path: Path) -> None:
    assert spine.validate_task(_task(tmp_path, _with_tags("tags: [infra, mdm]\n"))).passed
    assert spine.validate_task(_task(tmp_path, _with_tags('tags: ["a, b", c] # note\n'))).passed
    assert spine.validate_task(_task(tmp_path, _with_tags("tags: [a,\n  b]\n"))).passed
    assert not spine.validate_task(_task(tmp_path, _with_tags("tags: []\n"))).passed
    assert not spine.validate_task(_task(tmp_path, _with_tags("tags: [a, b, c, d, e, f]\n"))).passed


def test_block_tags_accept_zero_indent_and_comments(spine: ModuleType, tmp_path: Path) -> None:
    assert spine.validate_task(_task(tmp_path, _with_tags("tags:\n- a\n- b # note\n"))).passed
    assert not spine.validate_task(_task(tmp_path, _with_tags("tags:\n"))).passed


def test_trailing_comment_is_not_part_of_the_value(spine: ModuleType, tmp_path: Path) -> None:
    commented = VALID_TASK.replace("base: develop", "base: develop # why").replace(
        "owner: maria.silva", "owner: maria.silva # lead"
    )
    empty_owner = VALID_TASK.replace("owner: maria.silva", "owner: # nobody")

    report = spine.validate_task(_task(tmp_path, commented))

    assert report.passed, _text(report)
    assert report.warnings == 0
    assert not spine.validate_task(_task(tmp_path, empty_owner)).passed


def test_multiline_scalar_values(spine: ModuleType, tmp_path: Path) -> None:
    folded = VALID_TASK.replace("goal: Prove the validator works", "goal: >\n  Prove the validator\n  works\n")
    quoted = VALID_TASK.replace("title: Example task", 'title: "Example\n  task"')
    plain = VALID_TASK.replace("title: Example task", "title: Example\n  task")
    owner_block = VALID_TASK.replace("owner: maria.silva", "owner: |\n  maria.silva")
    empty_block = VALID_TASK.replace("owner: maria.silva", "owner: >\n")

    for content in (folded, quoted, plain, owner_block):
        report = spine.validate_task(_task(tmp_path, content))
        assert report.passed, _text(report)
    assert not spine.validate_task(_task(tmp_path, empty_block)).passed
    assert spine._frontmatter_value("goal: >\n  a\n  b\nx: 1", "goal") == "a b"
    assert spine._frontmatter_value('t: "a\n  b"\nx: 1', "t") == "a b"


def test_missing_frontmatter_and_sections_fail(spine: ModuleType, tmp_path: Path) -> None:
    report = spine.validate_task(_task(tmp_path, "# PROJ-123-example\n\nNo contract here.\n"))

    assert not report.passed
    assert "frontmatter" in _text(report)
    assert "## Objective" in _text(report)


def test_legacy_blocks_fail(spine: ModuleType, tmp_path: Path) -> None:
    legacy = VALID_TASK + "\n**Status:** PLANNING\n"
    stray_task = VALID_TASK.replace("## Implementation Plan\n\n", "")

    assert not spine.validate_task(_task(tmp_path, legacy)).passed
    assert not spine.validate_task(_task(tmp_path, stray_task)).passed


def test_cli_task_exit_codes(tmp_path: Path) -> None:
    good = _task(tmp_path, VALID_TASK)
    bad = _task(tmp_path, VALID_TASK.replace("feat/PROJ-123", "feature/PROJ-123"), "PROJ-123-bad.md")

    ok = subprocess.run(
        [sys.executable, str(SCRIPT), "doctor", "--task", str(good)], capture_output=True, text=True, check=False
    )
    failed = subprocess.run(
        [sys.executable, str(SCRIPT), "doctor", "--task", str(bad)], capture_output=True, text=True, check=False
    )
    missing = subprocess.run(
        [sys.executable, str(SCRIPT), "doctor", "--task", str(tmp_path / "nope.md")],
        capture_output=True,
        text=True,
        check=False,
    )

    assert ok.returncode == 0 and ok.stdout.startswith("OK:")
    assert failed.returncode == 1 and "ERROR:" in failed.stderr
    assert missing.returncode == 1 and "ERROR:" in missing.stderr
