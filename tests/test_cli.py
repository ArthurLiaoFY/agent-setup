from pathlib import Path

from agent_setup.cli import main


def test_cli_requires_profile() -> None:
    assert main(["install", "."]) != 0


def test_cli_accepts_exactly_one_profile(tmp_path: Path, capsys) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "AGENTS.md" in output


def test_cli_rejects_multiple_profiles(tmp_path: Path) -> None:
    assert main(["install", "--codex", "--claude", str(tmp_path)]) != 0


def test_cli_rejects_file_target(tmp_path: Path) -> None:
    target = tmp_path / "project"
    target.write_text("file")

    assert main(["install", "--codex", str(target)]) != 0


def test_cli_rejects_force(tmp_path: Path) -> None:
    assert main(["install", "--codex", "--force", str(tmp_path)]) != 0
