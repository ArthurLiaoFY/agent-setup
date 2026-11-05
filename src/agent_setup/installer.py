from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterable


class InstallError(RuntimeError):
    """Raised when an installation cannot be completed safely."""


def install(profile: str, target: Path, *, force: bool = False) -> list[Path]:
    """Install one profile into target and return the files that were written."""
    if profile == "claude":
        destinations = {
            "CLAUDE.md": target / "CLAUDE.md",
        }
    elif profile == "copilot":
        destinations = {
            "copilot-instructions.md": target / ".github" / "copilot-instructions.md",
        }
    elif profile == "codex":
        destinations = {
            "AGENTS.md": target / "AGENTS.md",
        }
    else:
        raise InstallError(f"Unsupported profile: {profile}")

    resource_root = files("agent_setup").joinpath("resources")
    adapter_root = resource_root.joinpath("adapters", profile)
    core_rules = resource_root.joinpath("core", "CORE.md")
    written: list[Path] = []

    written.extend(_install_rules(resource_root.joinpath("rules"), target / "agent_rules", force))
    core_destination = target / "agent_rules" / "CORE.md"
    if not core_destination.exists() or force:
        core_destination.parent.mkdir(parents=True, exist_ok=True)
        core_destination.write_text(core_rules.read_text())
        written.append(core_destination)

    for source_name, destination in destinations.items():
        source = adapter_root.joinpath(source_name)
        if not source.is_file():
            raise InstallError(f"Missing packaged adapter: {source_name}")
        if destination.exists() and not force:
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        with as_file(source) as source_path:
            adapter_text = source_path.read_text()
        output = adapter_text.rstrip() + "\n\n" + core_rules.read_text()
        destination.write_text(output)
        written.append(destination)
    written.sort()

    return written


def _install_rules(
    source_root,
    destination_root: Path,
    force: bool,
) -> list[Path]:
    written: list[Path] = []

    def copy_directory(directory, relative_parent: Path) -> None:
        for source in directory.iterdir():
            relative_path = relative_parent / source.name
            destination = destination_root / relative_path
            if source.is_dir():
                copy_directory(source, relative_path)
            elif source.is_file() and source.name != ".DS_Store":
                if destination.exists() and not force:
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with as_file(source) as source_path:
                    destination.write_bytes(source_path.read_bytes())
                written.append(destination)

    copy_directory(source_root, Path())
    return written


def profiles_requested(*, claude: bool, copilot: bool, codex: bool) -> Iterable[str]:
    if claude:
        yield "claude"
    if copilot:
        yield "copilot"
    if codex:
        yield "codex"
