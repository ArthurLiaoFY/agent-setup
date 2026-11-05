from pathlib import Path

from agent_setup.installer import InstallError, install


def test_install_claude(tmp_path: Path) -> None:
    written = install("claude", tmp_path)

    assert tmp_path / "CLAUDE.md" in written
    installed = (tmp_path / "CLAUDE.md").read_text()
    assert "# Claude Code Adapter" in installed
    assert "# Agent Instructions" in installed


def test_root_entries_reference_canonical_rules(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    canonical_link = "src/agent_setup/resources/core/CORE.md"

    assert canonical_link in (root / "AGENTS.md").read_text()


def test_install_copilot(tmp_path: Path) -> None:
    written = install("copilot", tmp_path)

    assert tmp_path / ".github" / "copilot-instructions.md" in written
    assert (tmp_path / ".github" / "copilot-instructions.md").is_file()


def test_install_codex(tmp_path: Path) -> None:
    written = install("codex", tmp_path)

    assert tmp_path / "AGENTS.md" in written
    assert (tmp_path / "AGENTS.md").is_file()


def test_install_includes_core_and_rules(tmp_path: Path) -> None:
    install("codex", tmp_path)

    assert (tmp_path / "agent_rules" / "CORE.md").is_file()
    assert (
        tmp_path / "agent_rules" / "fundamental" / "project_structure" / "project-level.md"
    ).is_file()
    assert (
        tmp_path / "agent_rules" / "fundamental" / "project_structure" / "submodule-level.md"
    ).is_file()


def test_installed_adapter_references_installed_core(tmp_path: Path) -> None:
    install("codex", tmp_path)

    entry = tmp_path / "AGENTS.md"
    assert "agent_rules/CORE.md" in entry.read_text()


def test_repeated_install_does_not_overwrite(tmp_path: Path) -> None:
    install("codex", tmp_path)
    destination = tmp_path / "AGENTS.md"
    original = destination.read_text()

    written = install("codex", tmp_path)

    assert destination.read_text() == original
    assert destination not in written


def test_multiple_profiles_share_installed_rules(tmp_path: Path) -> None:
    written = (
        install("claude", tmp_path)
        + install("copilot", tmp_path)
        + install("codex", tmp_path)
    )

    assert tmp_path / "CLAUDE.md" in written
    assert tmp_path / ".github" / "copilot-instructions.md" in written
    assert tmp_path / "AGENTS.md" in written
    assert (tmp_path / "agent_rules" / "CORE.md").is_file()


def test_existing_file_requires_force(tmp_path: Path) -> None:
    destination = tmp_path / "CLAUDE.md"
    destination.write_text("existing")

    written = install("claude", tmp_path)
    assert destination not in written

    install("claude", tmp_path, force=True)
    assert destination.read_text() != "existing"


def test_unknown_profile(tmp_path: Path) -> None:
    try:
        install("unknown", tmp_path)
    except InstallError:
        return
    raise AssertionError("InstallError was not raised")
