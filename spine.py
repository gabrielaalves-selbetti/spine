#!/usr/bin/env python3
"""Spine installer and doctor (single file, standard library only, Python 3.9+).

Usage (on Windows use ``python``; ``py -3`` also works):

    python spine.py install [TARGET] --ides claude,cursor,antigravity,windsurf
    python spine.py install [TARGET] --dry-run
    python spine.py doctor [TARGET]
    python spine.py doctor --task docs/memory/active_tasks/PROJ-123-foo.md

``install`` runs from the Spine clone. It copies real files (no symlinks) into
TARGET, never touches the network, and never writes outside TARGET. Running it
again is the update path. ``doctor`` also works from the copy that ``install``
places at ``.spine/spine.py`` in the target project.

Exit code 0 means OK (warnings allowed), 1 means at least one error.
``ERROR:``/``WARNING:``/``NOTE:`` go to stderr and ``OK:`` lines go to stdout;
agents and slash commands rely on these prefixes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import TextIO

SPINE_DIR = ".spine"
MANIFEST_REL = f"{SPINE_DIR}/manifest.json"
SNIPPET_REL = f"{SPINE_DIR}/AGENTS.snippet.md"
GITATTRIBUTES_REL = f"{SPINE_DIR}/.gitattributes"
GITATTRIBUTES_CONTENT = "* text eol=lf\n"
MANIFEST_SCHEMA = 1

AGENTS_FILE = "AGENTS.md"
AGENTS_REFERENCE = f"{SPINE_DIR}/rules"
SOURCE_DIRS = ("commands", "rules", "skills", "templates")
CORE_RULES = ("01-core-protocol.md", "02-memory-bank.md", "03-code-quality.md")
# Maintainer-only commands that must never reach a consumer project.
INTERNAL_COMMANDS = ("spine-promote.md",)
IGNORED_DIR_NAMES = (".git", "__pycache__", "node_modules")

POINTER_MARKER = "<!-- spine:pointer"
GENERIC_ARGUMENTS_LINE = "User arguments: any text typed after the command name."

UNVERIFIED_TAG = "A VERIFICAR"
UTF8_BOM = b"\xef\xbb\xbf"

TASK_REQUIRED_KEYS = (
    "task_id",
    "title",
    "goal",
    "status",
    "owner",
    "tags",
    "branch",
    "base",
    "created_at",
    "updated_at",
)
TASK_BRANCH_TYPES = ("feat", "fix", "docs", "refactor", "test", "chore", "hotfix", "release")
TASK_DEFAULT_BASE = "develop"
TASK_BASE_BY_TYPE = {"hotfix": "production"}
TASK_ID_RE = re.compile(r"^[A-Za-z0-9]+(-[A-Za-z0-9]+)*$")
TASK_MIN_TAGS = 1
TASK_MAX_TAGS = 5
TASK_LEGACY_PATTERNS = (r"^\*\*Status:\*\*", r"^\*\*Branch:\*\*")
TASK_REQUIRED_SECTIONS = ("## Objective", "## Acceptance Criteria")
TASK_TEMPLATE_NAME = "_task-template.md"
TASK_DIRS = ("docs/memory/active_tasks", "docs/memory/completed_tasks")

LEGACY_ARTIFACTS = (".spine-vendor", "opencode.json", ".opencode")

# Windows reparse tags that redirect a path elsewhere (symlink, junction).
LINK_REPARSE_TAGS = (
    getattr(stat, "IO_REPARSE_TAG_SYMLINK", 0xA000000C),
    getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003),
)


@dataclass(frozen=True)
class IdeLayout:
    """Where one IDE expects command pointers and how it loads AGENTS.md.

    Attributes:
        label: Human-readable IDE name.
        commands_dir: Project-relative directory for command pointer files.
        arguments_line: Last line of each pointer (how arguments reach the agent).
        verified: False until the paths were checked by hand against the IDE.
        seed_files: ``(relative path, content)`` files created once, never overwritten.
    """

    label: str
    commands_dir: str
    arguments_line: str
    verified: bool
    seed_files: tuple[tuple[str, str], ...] = ()


# Single place to correct once each IDE has been checked by hand.
IDE_LAYOUTS = {
    "claude": IdeLayout(
        label="Claude Code",
        commands_dir=".claude/commands",
        arguments_line="User arguments: $ARGUMENTS",
        verified=True,
        seed_files=(("CLAUDE.md", "@AGENTS.md\n"),),
    ),
    "cursor": IdeLayout(
        label="Cursor",
        commands_dir=".cursor/commands",
        arguments_line=GENERIC_ARGUMENTS_LINE,
        verified=False,
    ),
    "antigravity": IdeLayout(
        label="Antigravity",
        commands_dir=".agents/workflows",  # or .agent/workflows
        arguments_line=GENERIC_ARGUMENTS_LINE,
        verified=False,
    ),
    "windsurf": IdeLayout(
        label="Windsurf",
        commands_dir=".windsurf/workflows",
        arguments_line=GENERIC_ARGUMENTS_LINE,
        verified=False,
    ),
}


class SpineError(Exception):
    """A condition that stops the command with a message for the user."""


class Report:
    """Collects validation errors and warnings and prints them as they occur."""

    def __init__(self) -> None:
        self.errors = 0
        self.warnings = 0
        self.lines: list[str] = []

    def fail(self, message: str) -> None:
        """Record an error."""
        self.errors += 1
        self._emit(f"ERROR: {message}", sys.stderr)

    def warn(self, message: str) -> None:
        """Record a warning."""
        self.warnings += 1
        self._emit(f"WARNING: {message}", sys.stderr)

    def note(self, message: str) -> None:
        """Print information that is neither an error nor a warning."""
        self._emit(f"NOTE: {message}", sys.stderr)

    def _emit(self, line: str, stream: TextIO) -> None:
        self.lines.append(line)
        print(line, file=stream)

    @property
    def passed(self) -> bool:
        """True when no errors were recorded."""
        return self.errors == 0


@dataclass(frozen=True)
class Action:
    """One planned change to the target project.

    Attributes:
        kind: CREATE, UPDATE, REMOVE, SKIP (protected local edit), or KEEP.
        path: Project-relative POSIX path.
        content: Bytes to write for CREATE/UPDATE.
    """

    kind: str
    path: str
    content: bytes | None = None


@dataclass
class InstallResult:
    """Outcome of planning (and optionally applying) an install."""

    ides: list[str] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class Manifest:
    """What install generated: selected IDEs, content hashes, and seed paths."""

    ides: list[str] = field(default_factory=list)
    mirror: dict[str, str] = field(default_factory=dict)
    pointers: dict[str, str] = field(default_factory=dict)
    seeds: list[str] = field(default_factory=list)

    def to_bytes(self) -> bytes:
        """Serialize deterministically (sorted keys, no timestamp)."""
        payload = {
            "schema": MANIFEST_SCHEMA,
            "ides": self.ides,
            "mirror": self.mirror,
            "pointers": self.pointers,
            "seeds": sorted(self.seeds),
        }
        return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


# =============================================================================
# Filesystem helpers
# =============================================================================


def normalize_newlines(text: str) -> str:
    """Return text using LF line endings only."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_source(path: Path) -> bytes:
    """Read a source file as UTF-8 (BOM tolerated) and return LF-only UTF-8 bytes.

    Args:
        path: File inside the Spine clone.

    Returns:
        Normalized content, ready to be written to the target.

    Raises:
        SpineError: If the file is not valid UTF-8.
    """
    try:
        text = path.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise SpineError(f"source file is not UTF-8: {path}") from exc
    return normalize_newlines(text).encode("utf-8")


def read_lenient(path: Path) -> str:
    """Read a file the user owns; undecodable bytes are replaced."""
    return normalize_newlines(path.read_bytes().decode("utf-8-sig", errors="replace"))


def sha256(data: bytes) -> str:
    """Hex SHA-256 of data."""
    return hashlib.sha256(data).hexdigest()


def normalized_hash(data: bytes) -> str:
    """Hash of data as it would be stored by install (no BOM, LF only)."""
    return sha256(normalize_newlines(data.decode("utf-8-sig", errors="replace")).encode("utf-8"))


def is_link(path: Path) -> bool:
    """True for symlinks and Windows junctions, including broken ones."""
    try:
        info = os.lstat(path)
    except OSError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    return getattr(info, "st_reparse_tag", 0) in LINK_REPARSE_TAGS


def safe_path(target: Path, relative: str) -> Path:
    """Resolve a project-relative path, refusing anything that leaves the target.

    Args:
        target: Resolved target project root.
        relative: POSIX path relative to the target.

    Returns:
        The absolute destination path.

    Raises:
        SpineError: If the path is absolute, contains ``..``, or passes through a link.
    """
    parts = PurePosixPath(relative).parts
    if not parts or PurePosixPath(relative).is_absolute() or ".." in parts or ":" in parts[0]:
        raise SpineError(f"refusing path outside the target project: {relative}")
    current = target
    for part in parts:
        current = current / part
        if is_link(current):
            raise SpineError(f"refusing to write through a link: {current}")
    return current


def source_files(directory: Path) -> list[Path]:
    """All files under directory, sorted, skipping VCS and cache directories."""
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and not set(path.relative_to(directory).parts) & set(IGNORED_DIR_NAMES)
    )


def is_spine_source(root: Path) -> bool:
    """True when root looks like the Spine clone (not an installed .spine copy)."""
    return all((root / name).is_dir() for name in SOURCE_DIRS)


def load_manifest(target: Path) -> Manifest | None:
    """Read ``.spine/manifest.json`` from the target.

    Args:
        target: Target project root.

    Returns:
        The manifest, or None when the project has none.

    Raises:
        SpineError: If the file exists but is not a valid manifest.
    """
    path = target / SPINE_DIR / "manifest.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        manifest = Manifest(
            ides=[str(item) for item in payload["ides"]],
            mirror={str(key): str(value) for key, value in payload["mirror"].items()},
            pointers={str(key): str(value) for key, value in payload["pointers"].items()},
            seeds=[str(item) for item in payload["seeds"]],
        )
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise SpineError(f"unreadable manifest: {path} (delete it and re-run install with --ides)") from exc
    return manifest


# =============================================================================
# install
# =============================================================================


def command_names(source: Path) -> list[str]:
    """Command files that are installed into consumer projects."""
    return sorted(
        path.name for path in (source / "commands").glob("*.md") if path.name not in INTERNAL_COMMANDS
    )


def render_pointer(command_name: str, command_text: str, layout: IdeLayout) -> str:
    """Build the thin per-IDE file that points at ``.spine/commands/``.

    Args:
        command_name: Command file name, e.g. ``spine-plan.md``.
        command_text: Content of the source command (its description is reused).
        layout: Target IDE layout.

    Returns:
        Pointer file content.
    """
    match = re.search(r"^description:[ \t]*(.+)$", command_text.split("\n---", 1)[0], flags=re.MULTILINE)
    description = match.group(1).strip() if match else f"Spine command {Path(command_name).stem}"
    return (
        "---\n"
        f"description: {description}\n"
        "---\n"
        f"{POINTER_MARKER} - generated by spine.py; edit {SPINE_DIR}/commands/{command_name} instead -->\n"
        f"Read `{SPINE_DIR}/commands/{command_name}` and follow it exactly.\n"
        "\n"
        f"{layout.arguments_line}\n"
    )


def collect_mirror(source: Path) -> dict[str, bytes]:
    """Files that make up the managed ``.spine/`` tree, keyed by target path."""
    files: dict[str, bytes] = {}
    for name in command_names(source):
        files[f"{SPINE_DIR}/commands/{name}"] = read_source(source / "commands" / name)
    for path in sorted((source / "rules").glob("*.md")):
        files[f"{SPINE_DIR}/rules/{path.name}"] = read_source(path)
    for path in source_files(source / "skills"):
        files[f"{SPINE_DIR}/{path.relative_to(source).as_posix()}"] = read_source(path)
    files[f"{SPINE_DIR}/{Path(__file__).name}"] = read_source(Path(__file__).resolve())
    files[GITATTRIBUTES_REL] = GITATTRIBUTES_CONTENT.encode("utf-8")
    return files


def collect_pointers(source: Path, ides: list[str]) -> dict[str, bytes]:
    """Per-IDE command pointer files, keyed by target path."""
    files: dict[str, bytes] = {}
    for name in command_names(source):
        command_text = read_source(source / "commands" / name).decode("utf-8")
        for ide in ides:
            layout = IDE_LAYOUTS[ide]
            files[f"{layout.commands_dir}/{name}"] = render_pointer(name, command_text, layout).encode("utf-8")
    return files


def collect_seeds(source: Path, ides: list[str]) -> dict[str, bytes]:
    """Files created once and never overwritten, keyed by target path."""
    files = {AGENTS_FILE: read_source(source / "templates" / AGENTS_FILE)}
    docs = source / "templates" / "docs"
    for path in source_files(docs):
        files[f"docs/{path.relative_to(docs).as_posix()}"] = read_source(path)
    for ide in ides:
        for relative, content in IDE_LAYOUTS[ide].seed_files:
            files[relative] = content.encode("utf-8")
    return files


def _sync_action(target: Path, relative: str, content: bytes) -> Action:
    destination = safe_path(target, relative)
    if not destination.is_file():
        return Action("CREATE", relative, content)
    if destination.read_bytes() == content:
        return Action("KEEP", relative)
    return Action("UPDATE", relative, content)


def _is_pointer_path(relative: str) -> bool:
    return any(relative.startswith(f"{layout.commands_dir}/") for layout in IDE_LAYOUTS.values())


def _plan_pointers(
    target: Path, pointers: dict[str, bytes], previous: dict[str, str], force: bool, result: InstallResult
) -> None:
    for relative, content in sorted(pointers.items()):
        action = _sync_action(target, relative, content)
        if action.kind == "UPDATE" and not force:
            on_disk = normalized_hash(safe_path(target, relative).read_bytes())
            if on_disk != previous.get(relative):
                action = Action("SKIP", relative)
                result.warnings.append(f"{relative} was edited locally; not overwritten (use --force)")
        result.actions.append(action)

    for relative in sorted(set(previous) - set(pointers)):
        if not _is_pointer_path(relative):
            continue
        destination = safe_path(target, relative)
        if not destination.is_file():
            continue
        if force or normalized_hash(destination.read_bytes()) == previous[relative]:
            result.actions.append(Action("REMOVE", relative))
        else:
            result.actions.append(Action("SKIP", relative))
            result.warnings.append(f"{relative} was edited locally; not removed (use --force)")


def plan_install(source: Path, target: Path, ides: list[str], force: bool) -> InstallResult:
    """Compute every change install would make, without touching the target.

    Args:
        source: Resolved Spine clone root.
        target: Resolved target project root.
        ides: Selected IDE keys, in canonical order.
        force: Overwrite or remove command pointers that were edited locally.

    Returns:
        Planned actions (the manifest is always last), warnings, and notes.

    Raises:
        SpineError: If a source file is not UTF-8 or a path would leave the target.
    """
    previous = load_manifest(target) or Manifest()
    result = InstallResult(ides=ides)
    mirror = collect_mirror(source)
    pointers = collect_pointers(source, ides)
    seeds = collect_seeds(source, ides)

    agents = safe_path(target, AGENTS_FILE)
    if agents.is_file() and AGENTS_REFERENCE not in read_lenient(agents):
        mirror[SNIPPET_REL] = seeds[AGENTS_FILE]
        result.warnings.append(
            f"{AGENTS_FILE} exists and does not reference {AGENTS_REFERENCE}; "
            f"it was not modified - merge {SNIPPET_REL} into it by hand"
        )

    for relative, content in sorted(mirror.items()):
        result.actions.append(_sync_action(target, relative, content))
    for relative in sorted(set(previous.mirror) - set(mirror)):
        if relative.startswith(f"{SPINE_DIR}/") and safe_path(target, relative).is_file():
            result.actions.append(Action("REMOVE", relative))

    _plan_pointers(target, pointers, previous.pointers, force, result)

    for relative, content in sorted(seeds.items()):
        kind = "KEEP" if safe_path(target, relative).exists() else "CREATE"
        result.actions.append(Action(kind, relative, content if kind == "CREATE" else None))

    manifest = Manifest(
        ides=ides,
        mirror={relative: sha256(content) for relative, content in mirror.items()},
        pointers={relative: sha256(content) for relative, content in pointers.items()},
        seeds=list(seeds),
    )
    result.actions.append(_sync_action(target, MANIFEST_REL, manifest.to_bytes()))

    for ide in ides:
        layout = IDE_LAYOUTS[ide]
        if not layout.verified:
            result.notes.append(f"[{UNVERIFIED_TAG}] {layout.label}: path not confirmed yet ({layout.commands_dir}/)")
    return result


def _prune_empty_parents(target: Path, directory: Path) -> None:
    while directory != target and directory.is_dir() and not any(directory.iterdir()):
        directory.rmdir()
        directory = directory.parent


def apply_actions(target: Path, actions: list[Action]) -> None:
    """Write and remove files as planned. Every path is re-checked before use."""
    for action in actions:
        if action.kind in ("CREATE", "UPDATE") and action.content is not None:
            destination = safe_path(target, action.path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(action.content)
        elif action.kind == "REMOVE":
            destination = safe_path(target, action.path)
            destination.unlink()
            _prune_empty_parents(target, destination.parent)


def resolve_ides(requested: list[str] | None, target: Path) -> list[str]:
    """Validate the IDE selection, falling back to the previous install.

    Args:
        requested: IDE keys from the command line, or None when omitted.
        target: Target project root.

    Returns:
        Selected IDE keys in canonical order, without duplicates.

    Raises:
        SpineError: If nothing was selected or a key is unknown.
    """
    valid = ", ".join(IDE_LAYOUTS)
    if requested is None:
        previous = load_manifest(target)
        if previous is None:
            raise SpineError(f"--ides is required on the first install (valid: {valid})")
        requested = previous.ides
    unknown = [ide for ide in requested if ide not in IDE_LAYOUTS]
    if unknown:
        raise SpineError(f"unknown IDE(s): {', '.join(unknown)} (valid: {valid})")
    selected = [ide for ide in IDE_LAYOUTS if ide in requested]
    if not selected:
        raise SpineError(f"select at least one IDE with --ides (valid: {valid})")
    return selected


def install(
    source: Path, target: Path, ides: list[str] | None, dry_run: bool = False, force: bool = False
) -> InstallResult:
    """Install or update Spine in a target project.

    Args:
        source: Spine clone root.
        target: Target project root (must exist).
        ides: IDE keys to wire, or None to reuse the previous selection.
        dry_run: Plan only; write nothing.
        force: Overwrite or remove command pointers that were edited locally.

    Returns:
        The planned (and, unless dry_run, applied) actions.

    Raises:
        SpineError: On invalid source/target, unknown IDE, or unsafe paths.
    """
    source = source.resolve()
    target = target.resolve()
    if not is_spine_source(source):
        raise SpineError(f"install must run from the Spine clone; not a Spine source: {source}")
    if not target.is_dir():
        raise SpineError(f"target directory not found: {target}")
    if target == source:
        raise SpineError("target must differ from the Spine clone")
    spine_dir = target / SPINE_DIR
    if is_link(spine_dir) or (spine_dir.exists() and not spine_dir.is_dir()):
        raise SpineError(f"{spine_dir} is a link or a file (legacy install?); remove it first")

    result = plan_install(source, target, resolve_ides(ides, target), force)
    if not dry_run:
        apply_actions(target, result.actions)
    return result


# =============================================================================
# doctor
# =============================================================================


def _frontmatter(content: str) -> str | None:
    if not content.startswith("---"):
        return None
    return content[3:].split("\n---", 1)[0]


BLOCK_SCALAR_RE = re.compile(r"([|>])[+-]?[0-9]?[+-]?(?:[ \t]+#.*)?")


def _continuation_lines(lines: list[str], start: int, plain: bool) -> list[str]:
    collected: list[str] = []
    for line in lines[start:]:
        text = line.strip()
        if line[:1] not in (" ", "\t") and text:
            break
        if plain and (not text or text.startswith(("#", "- "))):
            break
        if text:
            collected.append(text)
    return collected


def _frontmatter_value(frontmatter: str, key: str) -> str | None:
    lines = frontmatter.split("\n")
    prefix = f"{key}:"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        rest = line[len(prefix):].strip()
        block = BLOCK_SCALAR_RE.fullmatch(rest)
        if block:
            parts = _continuation_lines(lines, index + 1, plain=False)
            return ("\n" if block.group(1) == "|" else " ").join(parts)
        if rest[:1] in ("'", '"') and rest.count(rest[0]) == 1:
            parts = [rest]
            for extra in lines[index + 1:]:
                parts.append(extra.strip())
                if rest[0] in extra:
                    break
            return _strip_comment(" ".join(parts)).strip("\"'")
        value = _strip_comment(rest)
        if value and rest[0] not in ("'", '"'):
            value = " ".join([value] + _continuation_lines(lines, index + 1, plain=True))
        return value.strip("\"'")
    return None


def _strip_comment(text: str) -> str:
    quote = ""
    for index, char in enumerate(text):
        if quote:
            if char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
        elif char == "#" and (index == 0 or text[index - 1] in " \t"):
            return text[:index].rstrip()
    return text.rstrip()


def _split_flow_items(text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    quote = ""
    for char in text:
        if quote:
            quote = "" if char == quote else quote
        elif char in "\"'":
            quote = char
        elif char == ",":
            items.append("".join(current))
            current = []
            continue
        current.append(char)
    items.append("".join(current))
    return [item.strip().strip("\"'").strip() for item in items if item.strip().strip("\"'").strip()]


def _count_tags(frontmatter: str) -> int:
    match = re.search(r"^tags:[ \t]*(.*)$", frontmatter, flags=re.MULTILINE)
    if not match:
        return 0
    inline = _strip_comment(match.group(1))
    if inline.startswith("["):
        flow = inline
        if "]" not in flow:
            tail = frontmatter[match.end():]
            flow += " " + _strip_comment(tail.split("]", 1)[0].replace("\n", " ")) + "]"
        return len(_split_flow_items(flow[1:].split("]", 1)[0]))
    if inline:
        return 0
    block = re.match(r"((?:[ \t]*-(?:[ \t].*)?\n?|[ \t]+.*\n?|[ \t]*#.*\n?)*)", frontmatter[match.end() + 1:])
    lines = block.group(1).split("\n") if block else []
    items = (_strip_comment(line) for line in lines if re.match(r"^[ \t]*-[ \t]", line + " "))
    return sum(1 for item in items if item.lstrip()[1:].strip())


def _validate_task_frontmatter(task_file: Path, frontmatter: str, report: Report) -> None:
    values = {key: _frontmatter_value(frontmatter, key) for key in TASK_REQUIRED_KEYS}
    for key, value in values.items():
        if value is None:
            report.fail(f"frontmatter missing key: {key}")
    if values["owner"] == "":
        report.fail("owner is empty (set the person responsible for the task)")

    task_id = values["task_id"]
    if task_id is not None:
        if not TASK_ID_RE.match(task_id):
            report.fail(f"task_id must be the tracker ID (letters, digits, hyphens): {task_id!r}")
        elif not task_file.name.startswith(f"{task_id}-"):
            report.fail(f"file name must start with '{task_id}-': {task_file.name}")

    branch = values["branch"]
    if branch is not None:
        kind, _, suffix = branch.partition("/")
        if kind not in TASK_BRANCH_TYPES or suffix != task_id:
            report.fail(f"branch must be <type>/<task_id> with type in {', '.join(TASK_BRANCH_TYPES)}: {branch!r}")
        expected_base = TASK_BASE_BY_TYPE.get(kind, TASK_DEFAULT_BASE)
        if values["base"] is not None and values["base"] != expected_base:
            report.warn(f"base is not {expected_base}: {values['base']!r}")

    tag_count = _count_tags(frontmatter)
    if tag_count < TASK_MIN_TAGS:
        report.fail(f"tags list empty (need {TASK_MIN_TAGS}-{TASK_MAX_TAGS} tags)")
    elif tag_count > TASK_MAX_TAGS:
        report.fail(f"too many tags ({tag_count}; max {TASK_MAX_TAGS})")


def validate_task(task_file: Path, report: Report | None = None) -> Report:
    """Validate a memory bank task file against the Spine task contract.

    Args:
        task_file: Path to the task markdown file (must exist).
        report: Optional report to append to.

    Returns:
        The report with recorded errors and warnings.
    """
    report = report or Report()
    content = read_lenient(task_file)

    frontmatter = _frontmatter(content)
    if frontmatter is None:
        report.fail("missing YAML frontmatter (file must start with ---)")
    else:
        _validate_task_frontmatter(task_file, frontmatter, report)

    for pattern in TASK_LEGACY_PATTERNS:
        if re.search(pattern, content, flags=re.MULTILINE):
            report.fail(f"legacy pattern found: {pattern}")

    for line in content.split("\n"):
        lowered = line.lower()
        if "superpowers:" in lowered and not re.search(r"do not|never use|`superpowers", lowered):
            report.fail("promotional superpowers: reference found (use execution_skill in frontmatter)")
            break

    for section in TASK_REQUIRED_SECTIONS:
        if section not in content:
            report.fail(f"missing required section: {section}")

    if re.search(r"^### Task [0-9]+:", content, flags=re.MULTILINE) and "## Implementation Plan" not in content:
        report.fail("Task N blocks found outside ## Implementation Plan section")

    return report


def _check_generated_files(target: Path, manifest: Manifest, report: Report) -> None:
    crlf: list[str] = []
    generated = [(relative, digest, True) for relative, digest in manifest.mirror.items()]
    generated += [(relative, digest, False) for relative, digest in manifest.pointers.items()]
    for relative, digest, is_mirror in sorted(generated):
        path = target.joinpath(*PurePosixPath(relative).parts)
        if not path.is_file():
            report.fail(f"missing file: {relative} (re-run install)")
            continue
        data = path.read_bytes()
        if data.startswith(UTF8_BOM):
            report.fail(f"file has a UTF-8 BOM: {relative} (re-run install)")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            report.fail(f"file is not UTF-8: {relative} (re-run install)")
            continue
        if b"\r" in data:
            crlf.append(relative)
        if normalized_hash(data) == digest:
            continue
        if is_mirror:
            report.fail(f"content differs from the installed version: {relative} (re-run install)")
        else:
            report.warn(f"command pointer was edited locally: {relative}")
    if crlf:
        report.warn(
            f"{len(crlf)} generated file(s) have CRLF line endings, e.g. {crlf[0]} "
            "(git autocrlf? add '* text=auto eol=lf' to .gitattributes)"
        )


def _check_layout(target: Path, manifest: Manifest, report: Report) -> None:
    spine_dir = target / SPINE_DIR
    for rule in CORE_RULES:
        if f"{SPINE_DIR}/rules/{rule}" not in manifest.mirror:
            report.fail(f"core rule not installed: {SPINE_DIR}/rules/{rule}")
    commands = sorted(path.name for path in (spine_dir / "commands").glob("*.md"))
    if not commands:
        report.fail(f"no commands found in {SPINE_DIR}/commands/")
    for skill in sorted(path for path in (spine_dir / "skills").glob("*") if path.is_dir()):
        if not (skill / "SKILL.md").is_file():
            report.fail(f"skill without SKILL.md: {SPINE_DIR}/skills/{skill.name}")

    for ide in manifest.ides:
        layout = IDE_LAYOUTS.get(ide)
        if layout is None:
            report.fail(f"manifest lists an unknown IDE: {ide}")
            continue
        if not layout.verified:
            report.note(f"[{UNVERIFIED_TAG}] {layout.label}: path not confirmed yet ({layout.commands_dir}/)")
        for name in commands:
            relative = f"{layout.commands_dir}/{name}"
            pointer = target.joinpath(*PurePosixPath(relative).parts)
            if not pointer.is_file():
                report.fail(f"missing command pointer: {relative} (re-run install)")
            elif f"{SPINE_DIR}/commands/{name}" not in read_lenient(pointer):
                report.warn(f"{relative} does not reference {SPINE_DIR}/commands/{name}")
        for relative, content in layout.seed_files:
            seed = target / relative
            if seed.is_file() and AGENTS_FILE not in read_lenient(seed):
                report.warn(f"{relative} does not reference {AGENTS_FILE} (add a line: {content.strip()})")


def _check_seeds(target: Path, manifest: Manifest, report: Report) -> None:
    for relative in manifest.seeds:
        if not target.joinpath(*PurePosixPath(relative).parts).exists():
            report.fail(f"missing seed file: {relative} (re-run install)")
    agents = target / AGENTS_FILE
    if agents.is_file() and AGENTS_REFERENCE not in read_lenient(agents):
        report.warn(f"{AGENTS_FILE} does not reference {AGENTS_REFERENCE} (merge {SNIPPET_REL} into it)")


def _check_links(target: Path, manifest: Manifest, report: Report) -> None:
    seen: set[Path] = set()
    for relative in [*manifest.mirror, *manifest.pointers, *manifest.seeds]:
        current = target
        for part in PurePosixPath(relative).parts:
            current = current / part
            if current not in seen and is_link(current):
                report.fail(f"managed path is a symlink or junction: {current.relative_to(target).as_posix()}")
            seen.add(current)


def _check_surroundings(target: Path, manifest: Manifest, report: Report) -> None:
    for name in LEGACY_ARTIFACTS:
        if (target / name).exists():
            report.warn(f"legacy Spine artifact found: {name} (left over from the old installers)")

    gitignore = target / ".gitignore"
    if gitignore.is_file():
        managed = {SPINE_DIR}
        managed.update(
            PurePosixPath(IDE_LAYOUTS[ide].commands_dir).parts[0] for ide in manifest.ides if ide in IDE_LAYOUTS
        )
        for line in read_lenient(gitignore).split("\n"):
            if line.strip().strip("/") in managed:
                report.warn(f".gitignore ignores a path Spine expects to be committed: {line.strip()}")

    owners: dict[str, list[str]] = {}
    for directory in TASK_DIRS:
        for path in sorted(target.joinpath(*PurePosixPath(directory).parts).glob("*.md")):
            if path.name == TASK_TEMPLATE_NAME:
                continue
            task_id = _frontmatter_value(_frontmatter(read_lenient(path)) or "", "task_id")
            if task_id:
                owners.setdefault(task_id, []).append(f"{directory}/{path.name}")
    for task_id, paths in sorted(owners.items()):
        if len(paths) > 1:
            report.fail(f"duplicate task_id {task_id}: {', '.join(paths)}")


def doctor(target: Path, report: Report | None = None) -> Report:
    """Validate the Spine structure installed in a target project.

    Args:
        target: Target project root.
        report: Optional report to append to.

    Returns:
        The report with recorded errors and warnings.
    """
    report = report or Report()
    target = target.resolve()
    spine_dir = target / SPINE_DIR
    if is_link(spine_dir) or not spine_dir.is_dir():
        report.fail(f"{SPINE_DIR}/ is missing or is not a real directory (run: python spine.py install)")
        return report
    try:
        manifest = load_manifest(target)
    except SpineError as exc:
        report.fail(str(exc))
        return report
    if manifest is None:
        report.fail(f"missing {MANIFEST_REL} (run: python spine.py install)")
        return report

    _check_links(target, manifest, report)
    _check_generated_files(target, manifest, report)
    _check_layout(target, manifest, report)
    _check_seeds(target, manifest, report)
    _check_surroundings(target, manifest, report)
    return report


# =============================================================================
# CLI
# =============================================================================


def run_install(args: argparse.Namespace) -> int:
    """CLI handler for ``install``."""
    source = Path(__file__).resolve().parent
    target = Path(args.target)
    ides = [part.strip() for part in args.ides.split(",") if part.strip()] if args.ides is not None else None
    result = install(source, target, ides, dry_run=args.dry_run, force=args.force)

    print(f"Spine install{' (dry-run)' if args.dry_run else ''}")
    print(f"  Source: {source}")
    print(f"  Target: {target.resolve()}")
    print(f"  IDEs:   {', '.join(result.ides)}")
    counts: dict[str, int] = {}
    for action in result.actions:
        counts[action.kind] = counts.get(action.kind, 0) + 1
        if action.kind != "KEEP":
            print(f"  {action.kind:<6} {action.path}")
    for note in result.notes:
        print(f"NOTE: {note}", file=sys.stderr)
    for warning in result.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    summary = ", ".join(f"{counts.get(kind, 0)} {kind}" for kind in ("CREATE", "UPDATE", "REMOVE", "SKIP", "KEEP"))
    if args.dry_run:
        print(f"OK: dry-run, nothing written ({summary}).")
    else:
        print(f"OK: {summary}.")
        print("Next: commit the generated files, then run /spine-bootstrap in the IDE.")
    return 0


def run_doctor(args: argparse.Namespace) -> int:
    """CLI handler for ``doctor``."""
    if args.task:
        task_file = Path(args.task)
        if not task_file.is_file():
            print(f"ERROR: file not found: {args.task}", file=sys.stderr)
            return 1
        report = validate_task(task_file)
        if not report.passed:
            print(f"Validation failed with {report.errors} error(s).", file=sys.stderr)
            return 1
        print(f"OK: {args.task} matches the Spine task contract.")
        return 0

    report = doctor(Path(args.target))
    if not report.passed:
        print(f"Doctor found {report.errors} error(s), {report.warnings} warning(s).", file=sys.stderr)
        return 1
    print(f"OK: Spine structure is valid ({report.warnings} warning(s)).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with the ``install`` and ``doctor`` subcommands."""
    parser = argparse.ArgumentParser(prog="spine.py", description="Spine installer and doctor.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install", help="Install or update Spine in a project (idempotent).")
    install_parser.add_argument("target", nargs="?", default=".", help="Project root (default: current directory)")
    install_parser.add_argument(
        "--ides",
        help=f"Comma-separated: {','.join(IDE_LAYOUTS)} (required on first install; reused afterwards)",
    )
    install_parser.add_argument("--dry-run", action="store_true", help="Show the plan without writing anything")
    install_parser.add_argument(
        "--force",
        action="store_true",
        help=f"Overwrite command pointers edited locally (never {AGENTS_FILE}, CLAUDE.md, or docs/)",
    )
    install_parser.set_defaults(handler=run_install)

    doctor_parser = subparsers.add_parser("doctor", help="Validate the installed structure or a task file.")
    doctor_parser.add_argument("target", nargs="?", default=".", help="Project root (default: current directory)")
    doctor_parser.add_argument("--task", metavar="FILE", help="Validate one task file against the task contract")
    doctor_parser.set_defaults(handler=run_doctor)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Arguments without the program name (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    # Keep stdout/stderr ordered when piped, and never crash on a legacy console code page.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(line_buffering=True, errors="replace")
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except SpineError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
