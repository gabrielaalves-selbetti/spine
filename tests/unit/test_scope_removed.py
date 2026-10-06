"""Invariants for what is out of scope in the shipped trees."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import REPO_ROOT

SHIPPED_DIRS = ("commands", "rules", "skills", "templates")
# Maintainer-only promotion cascade; never installed into consumer projects.
INTERNAL_FILES = {"commands/spine-promote.md"}

OUT_OF_SCOPE_TERMS = ("graphify", "mkdocs", "opencode", "symlink", "install.sh", "install.ps1", "spine_validate")
SOLO_MODEL_TERMS = ("Solo", "feature/", "sequential", "roadmap_idea", "/spine-roadmap", "/spine-update")

REMOVED_PATHS = (
    "install.sh",
    "install.ps1",
    ".spine",
    "scripts",
    "agents",
    "commands/spine-roadmap.md",
    "commands/spine-update.md",
    "templates/opencode.json",
    "templates/dot.graphifyignore",
    "templates/docs/mkdocs",
    "templates/docs/governance/ice-scoring-guide.md",
)

KEPT_SKILLS = [
    "executing-plans",
    "gitflow",
    "grill-me",
    "handoff-protocol",
    "systematic-debugging",
    "test-driven-development",
    "testing-guidelines",
    "verification-before-completion",
    "writing-plans",
]


def _shipped_text_files() -> list[Path]:
    files: list[Path] = []
    for name in SHIPPED_DIRS:
        files.extend(path for path in (REPO_ROOT / name).rglob("*") if path.is_file())
    return [path for path in files if path.relative_to(REPO_ROOT).as_posix() not in INTERNAL_FILES]


def _offenders(term: str, ignore_case: bool) -> list[str]:
    needle = term.lower() if ignore_case else term
    offenders = []
    for path in _shipped_text_files():
        text = path.read_text(encoding="utf-8")
        if needle in (text.lower() if ignore_case else text):
            offenders.append(path.relative_to(REPO_ROOT).as_posix())
    return offenders


@pytest.mark.parametrize("term", OUT_OF_SCOPE_TERMS)
def test_out_of_scope_tooling_is_not_mentioned(term: str) -> None:
    assert _offenders(term, ignore_case=True) == []


@pytest.mark.parametrize("term", SOLO_MODEL_TERMS)
def test_solo_model_wording_is_gone(term: str) -> None:
    assert _offenders(term, ignore_case=False) == []


@pytest.mark.parametrize("relative", REMOVED_PATHS)
def test_removed_paths_do_not_exist(relative: str) -> None:
    assert not (REPO_ROOT / relative).exists()


def test_skill_catalog_is_the_workflow_set() -> None:
    assert sorted(path.name for path in (REPO_ROOT / "skills").iterdir()) == KEPT_SKILLS


def test_promotion_cascade_branches_are_still_documented() -> None:
    text = (REPO_ROOT / "templates/docs/workflow/gitflow-operacional.md").read_text(encoding="utf-8")
    for branch in ("`main`", "`develop`", "`staging`", "`production`"):
        assert branch in text
