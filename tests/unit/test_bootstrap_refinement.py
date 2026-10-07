from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_global_templates_have_knowledge_sections() -> None:
    patterns = _read("templates/docs/memory/global/system-patterns.md")
    tech = _read("templates/docs/memory/global/tech-context.md")
    product = _read("templates/docs/memory/global/product-context.md")
    assert "## Project-Specific Alterations" in patterns
    assert "## Known Risks" in tech
    assert "## Known Opportunities (unplanned)" in product


def test_roadmap_template_is_a_plain_milestone_list() -> None:
    text = _read("templates/docs/memory/ledger/roadmap.md")
    assert "## Milestone 1" in text
    assert not text.startswith("---")
    assert "Idea Bank" not in text


def test_memory_bank_documents_bootstrap_knowledge_mapping() -> None:
    text = _read("rules/02-memory-bank.md")
    assert "Project-Specific Alterations" in text
    assert "Known Risks" in text
    assert "Known Opportunities" in text
    assert "Bootstrap fills" in text or "bootstrap fills" in text.lower()
    assert "does **not** create `active_tasks/`" in text


def test_spine_bootstrap_deep_assessment_and_agent_focus() -> None:
    text = _read("commands/spine-bootstrap.md")
    lower = text.lower()
    assert "python .spine/spine.py doctor" in text
    assert "agent-ready" in lower or "agent-optimized" in lower
    assert "maximize detail" in lower or "maximal detail" in lower


def test_spine_bootstrap_hunts_alterations_risks_opportunities() -> None:
    text = _read("commands/spine-bootstrap.md")
    assert "Project-Specific Alterations" in text
    assert "Known Risks" in text
    assert "Known Opportunities" in text
    assert "Alterations" in text


def test_spine_bootstrap_no_roadmap_task_or_plan() -> None:
    text = _read("commands/spine-bootstrap.md")
    lower = text.lower()
    assert "do not modify" in lower and "roadmap.md" in lower
    assert "initial task" not in lower
    assert "when there is delivery scope" not in lower
    assert "do not create" in lower and "active_tasks/" in text
    assert "/spine-plan" in text


def test_spine_bootstrap_no_seed_side_effects() -> None:
    text = _read("commands/spine-bootstrap.md")
    lower = text.lower()
    assert "forbidden" in lower
    assert "copy/seed `docs/`" in lower
    assert "edit anything under `.spine/`" in lower


def test_readme_documents_install_and_doctor() -> None:
    text = _read("README.md")
    assert "spine.py install" in text
    assert "--dry-run" in text
    assert "python .spine/spine.py doctor" in text
    assert "Never overwritten" in text


def test_agents_md_documents_installer_contract() -> None:
    text = _read("AGENTS.md")
    assert "spine.py" in text
    assert "UNVERIFIED" in text
    assert "/spine-plan" in text
