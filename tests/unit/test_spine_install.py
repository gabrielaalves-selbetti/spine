"""Behavioral tests for `spine.py install`."""

from __future__ import annotations

import ast
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

from conftest import REPO_ROOT, SCRIPT, snapshot

FORBIDDEN_IMPORTS = {"urllib", "http", "socket", "subprocess", "ftplib", "ssl", "requests"}
CHANGING_KINDS = {"CREATE", "UPDATE", "REMOVE"}


def _kinds(result: object) -> dict[str, str]:
    return {action.path: action.kind for action in result.actions}  # type: ignore[attr-defined]


def test_dry_run_writes_nothing(spine: ModuleType, fake_source: Path, target: Path) -> None:
    result = spine.install(fake_source, target, ["claude"], dry_run=True)

    assert snapshot(target) == {}
    assert "CREATE" in set(_kinds(result).values())


def test_install_creates_single_source_and_pointers(spine: ModuleType, fake_source: Path, target: Path) -> None:
    spine.install(fake_source, target, ["claude", "cursor"])

    files = snapshot(target)
    assert ".spine/commands/spine-plan.md" in files
    assert ".spine/rules/01-core-protocol.md" in files
    assert ".spine/skills/writing-plans/SKILL.md" in files
    assert ".spine/skills/writing-plans/extra/notes.md" in files
    assert ".spine/spine.py" in files
    assert ".spine/manifest.json" in files
    assert ".spine/.gitattributes" in files
    assert "AGENTS.md" in files
    assert "CLAUDE.md" in files
    assert "docs/memory/global/project-brief.md" in files
    assert "docs/memory/completed_tasks/.gitkeep" in files
    assert ".claude/commands/spine-plan.md" in files
    assert ".cursor/commands/spine-execute.md" in files
    assert not any(path.startswith((".windsurf/", ".agents/", ".agent/")) for path in files)


def test_pointer_is_thin_and_references_spine_commands(spine: ModuleType, fake_source: Path, target: Path) -> None:
    spine.install(fake_source, target, ["claude"])

    pointer = (target / ".claude" / "commands" / "spine-plan.md").read_text(encoding="utf-8")
    assert pointer.startswith("---\ndescription: Plan a task\n---\n")
    assert "spine:pointer" in pointer
    assert "`.spine/commands/spine-plan.md`" in pointer
    assert "$ARGUMENTS" in pointer
    assert "# Slash Command" not in pointer


def test_internal_command_is_not_installed(spine: ModuleType, fake_source: Path, target: Path) -> None:
    spine.install(fake_source, target, ["claude"])

    assert not [path for path in snapshot(target) if "spine-promote" in path]


def test_second_install_is_byte_identical_noop(spine: ModuleType, fake_source: Path, target: Path) -> None:
    spine.install(fake_source, target, ["claude", "windsurf"])
    before = snapshot(target)

    result = spine.install(fake_source, target, ["claude", "windsurf"])

    assert snapshot(target) == before
    assert not CHANGING_KINDS & set(_kinds(result).values())


def test_generated_files_are_utf8_lf_without_bom(spine: ModuleType, fake_source: Path, target: Path) -> None:
    spine.install(fake_source, target, ["claude", "cursor", "antigravity", "windsurf"])

    for path, data in snapshot(target).items():
        assert b"\r" not in data, path
        assert not data.startswith(b"\xef\xbb\xbf"), path
        data.decode("utf-8")


def test_existing_agents_and_memory_are_never_overwritten(spine: ModuleType, fake_source: Path, target: Path) -> None:
    (target / "AGENTS.md").write_bytes(b"# My own rules\n")
    brief = target / "docs" / "memory" / "global" / "project-brief.md"
    brief.parent.mkdir(parents=True)
    brief.write_bytes(b"# Real project brief\n")

    result = spine.install(fake_source, target, ["claude"], force=True)

    assert (target / "AGENTS.md").read_bytes() == b"# My own rules\n"
    assert brief.read_bytes() == b"# Real project brief\n"
    assert (target / ".spine" / "AGENTS.snippet.md").is_file()
    assert any("AGENTS.md" in warning for warning in result.warnings)


def test_snippet_is_removed_once_agents_references_spine(spine: ModuleType, fake_source: Path, target: Path) -> None:
    (target / "AGENTS.md").write_bytes(b"# My own rules\n")
    spine.install(fake_source, target, ["claude"])
    (target / "AGENTS.md").write_bytes(b"# My own rules\n\nSee .spine/rules/.\n")

    spine.install(fake_source, target, ["claude"])

    assert not (target / ".spine" / "AGENTS.snippet.md").exists()


def test_edited_pointer_is_skipped_unless_forced(spine: ModuleType, fake_source: Path, target: Path) -> None:
    spine.install(fake_source, target, ["claude"])
    pointer = target / ".claude" / "commands" / "spine-plan.md"
    pointer.write_bytes(b"my custom command\n")

    skipped = spine.install(fake_source, target, ["claude"])

    assert _kinds(skipped)[".claude/commands/spine-plan.md"] == "SKIP"
    assert pointer.read_bytes() == b"my custom command\n"
    assert skipped.warnings

    spine.install(fake_source, target, ["claude"], force=True)

    assert b"spine:pointer" in pointer.read_bytes()


def test_deselected_ide_pointers_are_removed(spine: ModuleType, fake_source: Path, target: Path) -> None:
    spine.install(fake_source, target, ["claude", "cursor"])

    spine.install(fake_source, target, ["claude"])

    assert not (target / ".cursor").exists()
    assert (target / ".claude" / "commands" / "spine-plan.md").is_file()


def test_stale_mirror_file_is_removed_but_foreign_file_is_kept(
    spine: ModuleType, fake_source: Path, target: Path
) -> None:
    spine.install(fake_source, target, ["claude"])
    (fake_source / "commands" / "spine-execute.md").unlink()
    foreign = target / ".spine" / "local-notes.md"
    foreign.write_bytes(b"mine\n")

    spine.install(fake_source, target, ["claude"])

    assert not (target / ".spine" / "commands" / "spine-execute.md").exists()
    assert not (target / ".claude" / "commands" / "spine-execute.md").exists()
    assert foreign.read_bytes() == b"mine\n"


def test_tampered_manifest_cannot_remove_memory(spine: ModuleType, fake_source: Path, target: Path) -> None:
    spine.install(fake_source, target, ["claude"])
    manifest = target / ".spine" / "manifest.json"
    text = manifest.read_text(encoding="utf-8")
    tampered = text.replace('"mirror": {', '"mirror": {\n    "docs/memory/ledger/progress.md": "0",')
    manifest.write_bytes(tampered.encode("utf-8"))

    spine.install(fake_source, target, ["claude"])

    assert (target / "docs" / "memory" / "ledger" / "progress.md").is_file()


def test_first_install_requires_ides_and_rerun_reuses_them(spine: ModuleType, fake_source: Path, target: Path) -> None:
    with pytest.raises(spine.SpineError, match="--ides"):
        spine.install(fake_source, target, None)

    spine.install(fake_source, target, ["windsurf"])
    result = spine.install(fake_source, target, None)

    assert result.ides == ["windsurf"]


def test_unknown_ide_is_rejected(spine: ModuleType, fake_source: Path, target: Path) -> None:
    with pytest.raises(spine.SpineError, match="opencode"):
        spine.install(fake_source, target, ["opencode"])


def test_target_equal_to_source_is_refused(spine: ModuleType, fake_source: Path) -> None:
    with pytest.raises(spine.SpineError):
        spine.install(fake_source, fake_source, ["claude"])


def test_installed_copy_cannot_install(spine: ModuleType, fake_source: Path, target: Path, tmp_path: Path) -> None:
    spine.install(fake_source, target, ["claude"])
    other = tmp_path / "other"
    other.mkdir()

    with pytest.raises(spine.SpineError, match="Spine clone"):
        spine.install(target / ".spine", other, ["claude"])


def test_spine_dir_as_link_is_refused(
    spine: ModuleType,
    fake_source: Path,
    target: Path,
    tmp_path: Path,
    make_dir_link: Callable[[Path, Path], None],
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    make_dir_link(target / ".spine", outside)

    with pytest.raises(spine.SpineError):
        spine.install(fake_source, target, ["claude"])

    assert snapshot(outside) == {}


def test_linked_ide_directory_is_refused_before_any_write(
    spine: ModuleType,
    fake_source: Path,
    target: Path,
    tmp_path: Path,
    make_dir_link: Callable[[Path, Path], None],
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    make_dir_link(target / ".claude", outside)

    with pytest.raises(spine.SpineError, match="link"):
        spine.install(fake_source, target, ["claude"])

    assert snapshot(outside) == {}
    assert not (target / ".spine").exists()


def test_non_utf8_source_aborts_before_any_write(spine: ModuleType, fake_source: Path, target: Path) -> None:
    (fake_source / "skills" / "writing-plans" / "bad.md").write_bytes(b"\xff\xfe\x00bad")

    with pytest.raises(spine.SpineError, match="UTF-8"):
        spine.install(fake_source, target, ["claude"])

    assert snapshot(target) == {}


def test_cli_dry_run_exit_code_and_output(
    spine: ModuleType, target: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = spine.main(["install", str(target), "--ides", "claude,cursor", "--dry-run"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "CREATE" in captured.out
    assert "A VERIFICAR" in captured.err
    assert snapshot(target) == {}


def test_cli_reports_errors_with_exit_code_1(
    spine: ModuleType, target: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = spine.main(["install", str(target)])

    assert exit_code == 1
    assert "ERROR:" in capsys.readouterr().err


def test_script_parses_as_python_39() -> None:
    ast.parse(SCRIPT.read_text(encoding="utf-8"), feature_version=(3, 9))


def test_script_imports_no_network_or_process_modules() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])

    assert not imported & FORBIDDEN_IMPORTS


def test_real_repository_installs_expected_commands(spine: ModuleType, target: Path) -> None:
    spine.install(REPO_ROOT, target, ["claude", "cursor", "antigravity", "windsurf"])

    commands = sorted(path.name for path in (target / ".spine" / "commands").iterdir())
    assert commands == [
        "spine-bootstrap.md",
        "spine-commit.md",
        "spine-execute.md",
        "spine-harvest.md",
        "spine-plan.md",
    ]
    for ide_dir in (".claude/commands", ".cursor/commands", ".agents/workflows", ".windsurf/workflows"):
        assert sorted(path.name for path in (target / ide_dir).iterdir()) == commands
