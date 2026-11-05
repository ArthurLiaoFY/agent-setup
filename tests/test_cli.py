from pathlib import Path
import hashlib
import json

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


def test_status_reports_invalid_utf8_manifest(tmp_path: Path, capsys) -> None:
    manifest = tmp_path / ".agent_rules" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_bytes(b"\xff")

    assert main(["status", str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "agent-setup: error: Invalid installation manifest" in captured.err


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


def test_uninstall_rejects_unowned_agent_rules_path(tmp_path: Path, capsys) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    note = tmp_path / ".agent_rules" / "additional" / "my-notes.md"
    note.write_text("user notes")
    manifest = tmp_path / ".agent_rules" / "manifest.json"
    data = json.loads(manifest.read_text())
    data["managedFiles"][".agent_rules/additional/my-notes.md"] = hashlib.sha256(
        note.read_bytes()
    ).hexdigest()
    manifest.write_text(json.dumps(data))

    assert main(["uninstall", str(tmp_path)]) == 1
    assert note.read_text() == "user notes"
    assert "invalid managed path" in capsys.readouterr().err.lower()


def test_uninstall_accepts_legacy_managed_files(tmp_path: Path) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    manifest = tmp_path / ".agent_rules" / "manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    retired = {
        ".agent_rules/additional/plan_template.md": b"old plan template",
        ".agent_rules/additional/lesson_learned.md": b"old lesson notes",
    }
    for relative, content in retired.items():
        path = tmp_path / relative
        path.write_bytes(content)
        data["managedFiles"][relative] = hashlib.sha256(content).hexdigest()
    manifest.write_text(json.dumps(data), encoding="utf-8")

    assert main(["uninstall", str(tmp_path)]) == 0
    assert all(not (tmp_path / relative).exists() for relative in retired)


def test_uninstall_preserves_modified_legacy_managed_file(tmp_path: Path) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    manifest = tmp_path / ".agent_rules" / "manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    relative = ".agent_rules/additional/lesson_learned.md"
    path = tmp_path / relative
    path.write_text("original packaged lessons", encoding="utf-8")
    data["managedFiles"][relative] = hashlib.sha256(
        b"original packaged lessons"
    ).hexdigest()
    manifest.write_text(json.dumps(data), encoding="utf-8")
    path.write_text("user-edited lessons", encoding="utf-8")

    assert main(["uninstall", str(tmp_path)]) == 0
    assert path.read_text(encoding="utf-8") == "user-edited lessons"


def test_uninstall_reuses_validated_manifest_data(tmp_path: Path, monkeypatch) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    import agent_setup.cli as cli_module

    original_read = cli_module.read_install_manifest
    calls = 0

    def count_reads(target):
        nonlocal calls
        calls += 1
        return original_read(target)

    monkeypatch.setattr(cli_module, "read_install_manifest", count_reads)
    assert main(["uninstall", str(tmp_path)]) == 0
    assert calls == 1


def test_uninstall_removes_multiple_profiles(tmp_path: Path) -> None:
    assert main(["install", "--codex", str(tmp_path)]) == 0
    assert main(["install", "--claude", str(tmp_path)]) == 0
    assert main(["install", "--copilot", str(tmp_path)]) == 0

    assert main(["uninstall", str(tmp_path)]) == 0
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / ".github" / "copilot-instructions.md").exists()
