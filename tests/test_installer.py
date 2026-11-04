from pathlib import Path

from agent_setup.installer import InstallError, install


def test_install_claude(tmp_path: Path) -> None:
    written = install("claude", tmp_path)

    assert written == [tmp_path / "CLAUDE.md"]
    assert written[0].read_text() == (
        Path(__file__).parents[1]
        / "src/agent_setup/templates/claude/CLAUDE.md"
    ).read_text()


def test_install_copilot(tmp_path: Path) -> None:
    written = install("copilot", tmp_path)

    assert written == [tmp_path / ".github" / "copilot-instructions.md"]
    assert written[0].is_file()


def test_install_codex(tmp_path: Path) -> None:
    written = install("codex", tmp_path)

    assert written == [tmp_path / "AGENTS.md"]
    assert written[0].is_file()


def test_existing_file_requires_force(tmp_path: Path) -> None:
    destination = tmp_path / "CLAUDE.md"
    destination.write_text("existing")

    assert install("claude", tmp_path) == []
    assert install("claude", tmp_path, force=True)
    assert destination.read_text() != "existing"


def test_unknown_profile(tmp_path: Path) -> None:
    try:
        install("unknown", tmp_path)
    except InstallError:
        return
    raise AssertionError("InstallError was not raised")
