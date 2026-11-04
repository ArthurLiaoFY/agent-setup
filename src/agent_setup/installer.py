from __future__ import annotations

import shutil
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
            "AGENT.md": target / ".github" / "copilot-instructions.md",
        }
    elif profile == "codex":
        destinations = {
            "AGENTS.md": target / "AGENTS.md",
        }
    else:
        raise InstallError(f"Unsupported profile: {profile}")

    template_root = files("agent_setup").joinpath("templates", profile)
    written: list[Path] = []

    for source_name, destination in destinations.items():
        source = template_root.joinpath(source_name)
        if not source.is_file():
            raise InstallError(f"Missing packaged template: {source_name}")
        if destination.exists() and not force:
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        with as_file(source) as source_path:
            shutil.copyfile(source_path, destination)
        written.append(destination)

    return written


def profiles_requested(*, claude: bool, copilot: bool, codex: bool) -> Iterable[str]:
    if claude:
        yield "claude"
    if copilot:
        yield "copilot"
    if codex:
        yield "codex"
