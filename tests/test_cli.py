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


def test_cli_creates_numbered_plan(tmp_path: Path, capsys) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    assert main(["plan", "add", "Optimize installer", str(tmp_path)]) == 0

    plan = tmp_path / ".agent_rules" / "additional" / "plans" / "PLAN-0001-optimize-installer.md"
    assert plan.is_file()
    assert "PLAN-0001" in capsys.readouterr().out


def test_cli_creates_next_numbered_lesson(tmp_path: Path) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    lesson_directory = tmp_path / ".agent_rules" / "additional" / "lesson_learned"
    lesson_directory.mkdir(parents=True, exist_ok=True)
    (lesson_directory / "LESSON-0001.md").write_text("old lesson")

    assert main(["lesson", "add", "Installer update", str(tmp_path)]) == 0
    assert (lesson_directory / "LESSON-0002-installer-update.md").is_file()


def test_cli_status_and_uninstall(tmp_path: Path, capsys) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    objective = tmp_path / ".agent_rules" / "additional" / "task_objective.md"
    objective.write_text("user objective")

    assert main(["status", str(tmp_path)]) == 0
    assert "Installed:" in capsys.readouterr().out

    assert main(["uninstall", str(tmp_path)]) == 0
    assert objective.read_text() == "user objective"
    assert not (tmp_path / "AGENTS.md").exists()


def test_uninstall_rejects_manifest_path_traversal(tmp_path: Path, capsys) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    manifest = tmp_path / ".agent_rules" / "manifest.json"
    data = __import__("json").loads(manifest.read_text())
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("outside")
    data["managedFiles"]["../../outside.txt"] = __import__("hashlib").sha256(
        b"outside"
    ).hexdigest()
    manifest.write_text(__import__("json").dumps(data))

    assert main(["uninstall", str(tmp_path)]) == 1
    assert outside.read_text() == "outside"
    assert "invalid" in capsys.readouterr().err.lower()


def test_uninstall_removes_multiple_profiles(tmp_path: Path) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    assert main(["install", "--claude", str(tmp_path)]) == 0
    assert main(["install", "--copilot", str(tmp_path)]) == 0

    assert main(["uninstall", str(tmp_path)]) == 0
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / ".github" / "copilot-instructions.md").exists()
