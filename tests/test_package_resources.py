from pathlib import Path
import subprocess
import zipfile


def test_wheel_contains_agent_markdown_resources(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    wheel = next(tmp_path.glob("*.whl"))

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())

    assert "agent_setup/resources/core/CORE.md" in names
    assert "agent_setup/resources/adapters/codex/AGENTS.md" in names
    assert (
        "agent_setup/resources/rules/fundamental/plan_template_instruction.md" in names
    )
