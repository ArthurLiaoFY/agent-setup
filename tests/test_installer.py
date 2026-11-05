from pathlib import Path
import hashlib
import json
import re
import shutil

import agent_setup.installer as installer_module

from agent_setup.installer import InstallError, install, read_install_manifest


def copy_resources(tmp_path: Path) -> Path:
    package_root = tmp_path / "package"
    source = Path(__file__).parents[1] / "src" / "agent_setup" / "resources"
    shutil.copytree(source, package_root / "resources")
    return package_root


def assert_target_unchanged(target: Path, snapshot: dict[str, bytes] | None = None) -> None:
    if not target.exists():
        return
    if snapshot is None:
        assert [path.name for path in target.iterdir()] == []
        return
    actual = {
        str(path.relative_to(target)): path.read_bytes()
        for path in target.rglob("*")
        if path.is_file()
    }
    assert actual == snapshot


def test_install_claude(tmp_path: Path) -> None:
    written = install("claude", tmp_path)

    assert tmp_path / "CLAUDE.md" in written
    installed = (tmp_path / "CLAUDE.md").read_text()
    assert "# Claude Code Adapter" in installed
    assert "@.agent_rules/CORE.md" in installed


def test_root_entries_reference_canonical_rules(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    canonical_link = "src/agent_setup/resources/core/CORE.md"

    assert canonical_link in (root / "AGENTS.md").read_text()


def test_readme_resource_inventory_matches_packaged_files() -> None:
    root = Path(__file__).parents[1]
    resource_root = root / "src" / "agent_setup" / "resources"
    readme_lines = (root / "README.md").read_text().splitlines()
    inventory_start = readme_lines.index("src/agent_setup/resources/") + 1

    documented: set[Path] = set()
    directories: list[str] = []
    for line in readme_lines[inventory_start:]:
        if not line.strip():
            break
        match = re.fullmatch(r"((?:│   |    )*)(?:├── |└── )(.+)", line)
        assert match is not None, f"Invalid resource tree line: {line}"

        depth = len(match.group(1)) // 4
        entry = match.group(2)
        directories = directories[:depth]
        if entry.endswith("/"):
            directories.append(entry[:-1])
        else:
            documented.add(Path(*directories, entry))

    actual = {
        path.relative_to(resource_root)
        for path in resource_root.rglob("*")
        if path.is_file() and path.name != ".DS_Store"
    }
    assert documented == actual


def test_install_includes_every_packaged_rule_resource(tmp_path: Path) -> None:
    resource_root = Path(__file__).parents[1] / "src" / "agent_setup" / "resources" / "rules"

    install("codex", tmp_path)

    expected = {
        Path(".agent_rules") / path.relative_to(resource_root)
        for path in resource_root.rglob("*")
        if path.is_file() and path.name != ".DS_Store"
    }
    installed = {
        path.relative_to(tmp_path)
        for path in (tmp_path / ".agent_rules").rglob("*")
        if path.is_file()
        and path.name not in {"CORE.md", "manifest.json"}
    }
    assert installed == expected


def test_install_copilot(tmp_path: Path) -> None:
    written = install("copilot", tmp_path)

    assert tmp_path / ".github" / "copilot-instructions.md" in written
    assert (tmp_path / ".github" / "copilot-instructions.md").is_file()


def test_install_skips_retired_resources_in_stale_package(
    tmp_path: Path, monkeypatch
) -> None:
    package_root = copy_resources(tmp_path)
    additional = package_root / "resources" / "rules" / "additional"
    (additional / "plan_template.md").write_text("stale template", encoding="utf-8")
    (additional / "lesson_learned.md").write_text("stale lessons", encoding="utf-8")
    monkeypatch.setattr(installer_module, "files", lambda _package: package_root)
    target = tmp_path / "target"

    install("codex", target)

    manifest = json.loads(
        (target / ".agent_rules" / "manifest.json").read_text(encoding="utf-8")
    )
    for name in ("plan_template.md", "lesson_learned.md"):
        relative = Path(".agent_rules/additional") / name
        assert not (target / relative).exists()
        assert relative.as_posix() not in manifest["managedFiles"]


def test_install_codex(tmp_path: Path) -> None:
    written = install("codex", tmp_path)

    assert tmp_path / "AGENTS.md" in written
    assert (tmp_path / "AGENTS.md").is_file()


def test_install_includes_core_and_rules(tmp_path: Path) -> None:
    install("codex", tmp_path)

    assert (tmp_path / ".agent_rules" / "CORE.md").is_file()
    assert (
        tmp_path / ".agent_rules" / "fundamental" / "project_structure" / "project-level.md"
    ).is_file()
    assert (
        tmp_path / ".agent_rules" / "fundamental" / "project_structure" / "submodule-level.md"
    ).is_file()


def test_installed_adapter_references_installed_core(tmp_path: Path) -> None:
    install("codex", tmp_path)

    entry = tmp_path / "AGENTS.md"
    assert ".agent_rules/CORE.md" in entry.read_text()


def test_repeated_install_overwrites_managed_files(tmp_path: Path) -> None:
    install("codex", tmp_path)
    destination = tmp_path / "AGENTS.md"
    original = destination.read_text()

    written = install("codex", tmp_path)

    assert destination.read_text() == original
    assert destination in written.overwritten


def test_multiple_profiles_share_installed_rules(tmp_path: Path) -> None:
    written = (
        install("claude", tmp_path)
        + install("copilot", tmp_path)
        + install("codex", tmp_path)
    )

    assert tmp_path / "CLAUDE.md" in written
    assert tmp_path / ".github" / "copilot-instructions.md" in written
    assert tmp_path / "AGENTS.md" in written
    assert (tmp_path / ".agent_rules" / "CORE.md").is_file()


def test_existing_adapter_is_preserved(tmp_path: Path) -> None:
    destination = tmp_path / "CLAUDE.md"
    destination.write_text("existing")

    written = install("claude", tmp_path)
    assert destination.read_text() == "existing"
    assert destination in written.preserved


def test_unknown_profile(tmp_path: Path) -> None:
    try:
        install("unknown", tmp_path)
    except InstallError:
        return
    raise AssertionError("InstallError was not raised")


def test_existing_core_is_preserved(tmp_path: Path) -> None:
    core = tmp_path / ".agent_rules" / "CORE.md"
    core.parent.mkdir(parents=True)
    core.write_text("custom core")

    written = install("codex", tmp_path)

    assert core.read_text() == "custom core"
    assert core in written.preserved


def test_existing_fundamental_is_preserved(tmp_path: Path) -> None:
    rule = tmp_path / ".agent_rules" / "fundamental" / "project_structure" / "project-level.md"
    rule.parent.mkdir(parents=True)
    rule.write_text("custom rule")

    written = install("codex", tmp_path)

    assert rule.read_text() == "custom rule"
    assert rule in written.preserved


def test_existing_additional_is_preserved(tmp_path: Path) -> None:
    rule = tmp_path / ".agent_rules" / "additional" / "task_objective.md"
    rule.parent.mkdir(parents=True)
    rule.write_text("user objective")

    written = install("codex", tmp_path)

    assert rule.read_text() == "user objective"
    assert rule in written.preserved


def test_missing_additional_is_installed(tmp_path: Path) -> None:
    install("codex", tmp_path)

    assert (tmp_path / ".agent_rules" / "additional" / "task_objective.md").is_file()
    assert (
        tmp_path / ".agent_rules" / "fundamental" / "plan_template_instruction.md"
    ).is_file()
    assert (
        tmp_path / ".agent_rules" / "additional" / "plans"
    ).is_dir()
    assert (
        tmp_path / ".agent_rules" / "additional" / "lesson_learned"
    ).is_dir()
    assert not (tmp_path / ".agent_rules" / "additional" / "plan_template.md").exists()
    assert not (tmp_path / ".agent_rules" / "additional" / "lesson_learned.md").exists()


def test_reinstall_removes_unchanged_retired_managed_files(tmp_path: Path) -> None:
    install("codex", tmp_path)
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

    result = install("codex", tmp_path)

    for relative in retired:
        assert not (tmp_path / relative).exists()
        assert relative not in json.loads(manifest.read_text(encoding="utf-8"))["managedFiles"]
        assert tmp_path / relative in result.removed


def test_reinstall_preserves_modified_retired_files_and_unmanages_them(tmp_path: Path) -> None:
    install("codex", tmp_path)
    manifest = tmp_path / ".agent_rules" / "manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    relative = ".agent_rules/additional/plan_template.md"
    path = tmp_path / relative
    path.write_text("original packaged template", encoding="utf-8")
    data["managedFiles"][relative] = hashlib.sha256(b"original packaged template").hexdigest()
    manifest.write_text(json.dumps(data), encoding="utf-8")
    path.write_text("user-customized template", encoding="utf-8")

    install("codex", tmp_path)

    assert path.read_text(encoding="utf-8") == "user-customized template"
    assert relative not in json.loads(manifest.read_text(encoding="utf-8"))["managedFiles"]


def test_unrelated_file_is_preserved(tmp_path: Path) -> None:
    unrelated = tmp_path / "README.md"
    unrelated.write_text("keep me")

    install("codex", tmp_path)

    assert unrelated.read_text() == "keep me"


def test_regular_file_target_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "project"
    target.write_text("file")

    try:
        install("codex", target)
    except InstallError:
        return
    raise AssertionError("InstallError was not raised")


def test_install_accepts_string_target(tmp_path: Path) -> None:
    written = install("codex", str(tmp_path))
    assert tmp_path / "AGENTS.md" in written


def test_nested_additional_is_preserved(tmp_path: Path) -> None:
    nested = tmp_path / ".agent_rules" / "additional" / "nested" / "custom.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("custom")

    install("codex", tmp_path)

    assert nested.read_text() == "custom"


def test_stale_fundamental_is_not_deleted(tmp_path: Path) -> None:
    stale = tmp_path / ".agent_rules" / "fundamental" / "stale.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("keep stale")

    install("codex", tmp_path)

    assert stale.read_text() == "keep stale"


def test_claude_adapter_uses_native_core_import() -> None:
    source = Path(__file__).parents[1] / "src/agent_setup/resources/adapters/claude/CLAUDE.md"
    content = source.read_text()
    assert "@.agent_rules/CORE.md" in content
    assert content.count("@.agent_rules/CORE.md") == 1


def test_codex_adapter_explicitly_reads_core() -> None:
    source = Path(__file__).parents[1] / "src/agent_setup/resources/adapters/codex/AGENTS.md"
    content = source.read_text()
    assert "Read `.agent_rules/CORE.md`" in content
    assert "# Scope" not in content


def test_copilot_adapter_explicitly_reads_core() -> None:
    source = Path(__file__).parents[1] / "src/agent_setup/resources/adapters/copilot/copilot-instructions.md"
    content = source.read_text()
    assert "Read `.agent_rules/CORE.md`" in content
    assert "# Scope" not in content


def test_missing_adapter_resource_does_not_modify_target(tmp_path: Path, monkeypatch) -> None:
    package_root = copy_resources(tmp_path)
    (package_root / "resources" / "adapters" / "codex" / "AGENTS.md").unlink()
    monkeypatch.setattr(installer_module, "files", lambda _package: package_root)
    target = tmp_path / "target"

    try:
        install("codex", target)
    except InstallError as error:
        assert "AGENTS.md" in str(error)
    else:
        raise AssertionError("InstallError was not raised")
    assert not target.exists()


def test_missing_core_resource_does_not_modify_target(tmp_path: Path, monkeypatch) -> None:
    package_root = copy_resources(tmp_path)
    (package_root / "resources" / "core" / "CORE.md").unlink()
    monkeypatch.setattr(installer_module, "files", lambda _package: package_root)
    target = tmp_path / "target"

    try:
        install("codex", target)
    except InstallError as error:
        assert "CORE.md" in str(error)
    else:
        raise AssertionError("InstallError was not raised")
    assert not target.exists()


def test_missing_fundamental_resource_does_not_modify_existing_target(
    tmp_path: Path, monkeypatch
) -> None:
    package_root = copy_resources(tmp_path)
    (package_root / "resources" / "rules" / "fundamental" / "project_structure" / "project-level.md").unlink()
    monkeypatch.setattr(installer_module, "files", lambda _package: package_root)
    target = tmp_path / "target"
    target.mkdir()
    sentinel = target / "sentinel.txt"
    sentinel.write_text("unchanged")

    try:
        install("codex", target)
    except InstallError:
        pass
    else:
        raise AssertionError("InstallError was not raised")
    assert sentinel.read_text() == "unchanged"


def test_missing_additional_resource_does_not_modify_existing_target(
    tmp_path: Path, monkeypatch
) -> None:
    package_root = copy_resources(tmp_path)
    (package_root / "resources" / "rules" / "additional" / "task_objective.md").unlink()
    monkeypatch.setattr(installer_module, "files", lambda _package: package_root)
    target = tmp_path / "target"
    target.mkdir()
    sentinel = target / "sentinel.txt"
    sentinel.write_text("unchanged")

    try:
        install("codex", target)
    except InstallError:
        pass
    else:
        raise AssertionError("InstallError was not raised")
    assert sentinel.read_text() == "unchanged"


def test_resource_read_failure_does_not_modify_target(tmp_path: Path, monkeypatch) -> None:
    package_root = copy_resources(tmp_path)
    monkeypatch.setattr(installer_module, "files", lambda _package: package_root)
    original_read_resource = installer_module._read_resource

    def unreadable(source, display_path):
        if Path(str(display_path)).name == "task_objective.md":
            raise installer_module.InstallError(f"Cannot read packaged resource {display_path}: simulated")
        return original_read_resource(source, display_path)

    monkeypatch.setattr(installer_module, "_read_resource", unreadable)
    target = tmp_path / "target"

    try:
        install("codex", target)
    except InstallError as error:
        assert "task_objective.md" in str(error)
    else:
        raise AssertionError("InstallError was not raised")
    assert not target.exists()


def test_modified_adapter_is_preserved_on_reinstall(tmp_path: Path) -> None:
    install("codex", tmp_path)
    adapter = tmp_path / "AGENTS.md"
    adapter.write_text("user customization")

    written = install("codex", tmp_path)

    assert adapter.read_text() == "user customization"
    assert adapter in written.preserved


def test_manifest_rejects_invalid_legacy_profile(tmp_path: Path) -> None:
    manifest = tmp_path / ".agent_rules" / "manifest.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({"version": 1, "profile": ["codex"], "managedFiles": {}}))

    try:
        read_install_manifest(tmp_path)
    except InstallError as error:
        assert "profile" in str(error)
    else:
        raise AssertionError("InstallError was not raised")


def test_manifest_rejects_non_hex_digest(tmp_path: Path) -> None:
    manifest = tmp_path / ".agent_rules" / "manifest.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({
        "version": 1,
        "profile": "codex",
        "managedFiles": {"AGENTS.md": "g" * 64},
    }))

    try:
        read_install_manifest(tmp_path)
    except InstallError as error:
        assert "path" in str(error)
    else:
        raise AssertionError("InstallError was not raised")


def test_write_failure_rolls_back_previous_files(tmp_path: Path, monkeypatch) -> None:
    original_write = installer_module._write_bytes
    write_count = 0

    def fail_after_first(*args, **kwargs):
        nonlocal write_count
        write_count += 1
        if write_count == 2:
            raise TypeError("simulated non-I/O failure")
        original_write(*args, **kwargs)

    monkeypatch.setattr(installer_module, "_write_bytes", fail_after_first)

    try:
        install("codex", tmp_path)
    except InstallError:
        pass
    else:
        raise AssertionError("InstallError was not raised")
    assert_target_unchanged(tmp_path, {})
