"""Shared test fixtures."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "spine.py"

FAKE_COMMAND = (
    "---\r\n"
    "description: Plan a task\r\n"
    "---\r\n"
    "\r\n"
    "# Slash Command: /spine-plan\r\n"
)


@pytest.fixture(scope="session")
def spine() -> ModuleType:
    """Load spine.py as a module without requiring it to be a package."""
    spec = importlib.util.spec_from_file_location("spine", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolve string annotations through sys.modules.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


@pytest.fixture
def fake_source(tmp_path: Path) -> Path:
    """A minimal Spine source tree stored with CRLF line endings and one BOM."""
    source = tmp_path / "spine-source"
    _write(source / "commands" / "spine-plan.md", FAKE_COMMAND.encode("utf-8"))
    _write(source / "commands" / "spine-execute.md", b"# Slash Command: /spine-execute\r\n")
    _write(source / "commands" / "spine-promote.md", b"# internal\r\n")
    for rule in ("01-core-protocol.md", "02-memory-bank.md", "03-code-quality.md"):
        _write(source / "rules" / rule, b"\xef\xbb\xbf# Rule\r\n")
    _write(source / "skills" / "writing-plans" / "SKILL.md", b"# Writing Plans\r\n")
    _write(source / "skills" / "writing-plans" / "extra" / "notes.md", "# Não ASCII\r\n".encode("utf-8"))
    _write(source / "templates" / "AGENTS.md", b"# AGENTS.md\r\n\r\nRead `.spine/rules/01-core-protocol.md`.\r\n")
    docs = source / "templates" / "docs"
    _write(docs / "memory" / "global" / "project-brief.md", b"# Project Brief\r\n")
    _write(docs / "memory" / "ledger" / "progress.md", b"# Progress\r\n")
    _write(docs / "memory" / "active_tasks" / ".gitkeep", b"")
    _write(docs / "memory" / "completed_tasks" / ".gitkeep", b"")
    return source


@pytest.fixture
def target(tmp_path: Path) -> Path:
    """An empty consumer project directory."""
    project = tmp_path / "project"
    project.mkdir()
    return project


@pytest.fixture
def make_dir_link() -> Callable[[Path, Path], None]:
    """Create a directory symlink, or a junction on Windows without privilege."""

    def _make(link: Path, destination: Path) -> None:
        try:
            os.symlink(destination, link, target_is_directory=True)
            return
        except OSError:
            if os.name != "nt":
                pytest.skip("cannot create links on this platform")
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(destination)],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            pytest.skip("cannot create a junction on this machine")

    return _make


def snapshot(root: Path) -> dict[str, bytes]:
    """Map every file under root to its bytes."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
