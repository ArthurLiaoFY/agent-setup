from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Iterable
import json
import hashlib

from .manifest import (
    ADDITIONAL_DESTINATION,
    ADDITIONAL_DIRECTORIES,
    ADAPTER_DESTINATIONS,
    CORE_DESTINATION,
    FUNDAMENTAL_DESTINATION,
    MANAGED_LOCAL_MANIFEST,
    REQUIRED_RULE_FILES,
)


class InstallError(RuntimeError):
    """Raised when an installation cannot be completed safely."""


class InstallResult(list[Path]):
    def __init__(self) -> None:
        super().__init__()
        self.created: list[Path] = []
        self.overwritten: list[Path] = []
        self.preserved: list[Path] = []

    @property
    def written(self) -> list[Path]:
        return self.created + self.overwritten


def install(profile: str, target: str | Path) -> InstallResult:
    """Install one profile into target and return the files that were written."""
    target = Path(target)
    if profile not in ADAPTER_DESTINATIONS:
        raise InstallError(f"Unsupported profile: {profile}")

    resource_root = files("agent_setup").joinpath("resources")
    adapter_root = resource_root.joinpath("adapters", profile)
    core_rules = resource_root.joinpath("core", "CORE.md")
    result = InstallResult()

    if target.exists() and not target.is_dir():
        raise InstallError(f"Target path is not a directory: {target}")

    adapter_name = destinations_source_name(profile)
    adapter_source = adapter_root.joinpath(adapter_name)
    plan = _build_installation_plan(
        profile=profile,
        adapter_source=adapter_source,
        core_source=core_rules,
        rules_root=resource_root.joinpath("rules"),
        target=target,
    )

    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise InstallError(f"Cannot install files under {target}: {error}") from error

    for item in plan:
        try:
            _write_bytes(item.destination, item.content, result, overwrite=item.overwrite)
        except OSError as error:
            raise InstallError(f"Cannot write {item.destination}: {error}") from error
    try:
        for relative in ADDITIONAL_DIRECTORIES:
            (target / Path(*relative.parts)).mkdir(parents=True, exist_ok=True)
        _write_local_manifest(target, profile, result)
    except OSError as error:
        raise InstallError(f"Cannot initialize agent rule directories under {target}: {error}") from error
    result.sort()
    result.created.sort()
    result.overwritten.sort()
    result.preserved.sort()
    return result


def destinations_source_name(profile: str) -> str:
    return {
        "claude": "CLAUDE.md",
        "codex": "AGENTS.md",
        "copilot": "copilot-instructions.md",
    }[profile]


def _write_local_manifest(target: Path, profile: str, result: InstallResult) -> None:
    destination = target / Path(*MANAGED_LOCAL_MANIFEST.parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            {
                "version": 1,
                "profile": profile,
                "managedDirectories": ["/".join(path.parts) for path in ADDITIONAL_DIRECTORIES],
                "managedFiles": {
                    path.relative_to(target).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in result.written
                    if path.is_file()
                    and path != target / Path(*MANAGED_LOCAL_MANIFEST.parts)
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


class InstallPlanItem:
    def __init__(self, destination: Path, content: bytes, *, overwrite: bool) -> None:
        self.destination = destination
        self.content = content
        self.overwrite = overwrite


def _build_installation_plan(
    *,
    profile: str,
    adapter_source,
    core_source,
    rules_root,
    target: Path,
) -> list[InstallPlanItem]:
    adapter = _read_resource(adapter_source, adapter_source)
    core = _read_resource(core_source, Path("resources/core/CORE.md"))

    resources = [(core_source, core, target / Path(*CORE_DESTINATION.parts), True)]
    _validate_resource_directory(rules_root.joinpath("fundamental"))
    _validate_resource_directory(rules_root.joinpath("additional"))

    fundamental_root = rules_root.joinpath("fundamental")
    additional_root = rules_root.joinpath("additional")
    for relative in REQUIRED_RULE_FILES:
        _read_resource(rules_root.joinpath(relative), Path("resources/rules") / relative)
    for source, relative in _iter_resource_files(fundamental_root):
        content = _read_resource(source, Path("resources/rules/fundamental") / relative)
        resources.append((source, content, target / Path(*FUNDAMENTAL_DESTINATION.parts) / relative, True))
    for source, relative in _iter_resource_files(additional_root):
        content = _read_resource(source, Path("resources/rules/additional") / relative)
        resources.append((source, content, target / Path(*ADDITIONAL_DESTINATION.parts) / relative, False))

    adapter_destination = target / Path(*ADAPTER_DESTINATIONS[profile][0].parts)
    resources.append((adapter_source, adapter, adapter_destination, True))

    target_resolved = target.resolve()
    plan: list[InstallPlanItem] = []
    for source, content, destination, overwrite in resources:
        destination_resolved = destination.resolve()
        if destination_resolved != target_resolved and target_resolved not in destination_resolved.parents:
            raise InstallError(f"Destination is outside target project: {destination} (source: {source})")
        plan.append(InstallPlanItem(destination, content, overwrite=overwrite))
    return plan


def _validate_resource_directory(directory) -> None:
    if not directory.is_dir():
        raise InstallError(f"Missing packaged resource directory: {directory}")
    if not list(_iter_resource_files(directory)):
        raise InstallError(f"Missing packaged resources: {directory}")


def _iter_resource_files(directory):
    for source in sorted(directory.iterdir(), key=lambda item: item.name):
        if source.name == ".DS_Store":
            continue
        if source.is_dir():
            for child, child_relative in _iter_resource_files(source):
                yield child, Path(source.name) / child_relative
        elif source.is_file():
            yield source, Path(source.name)


def _read_resource(source, display_path) -> bytes:
    try:
        if not source.is_file():
            raise InstallError(f"Missing packaged resource: {display_path}")
        return source.read_bytes()
    except InstallError:
        raise
    except (OSError, IOError) as error:
        raise InstallError(f"Cannot read packaged resource {display_path}: {error}") from error


def _write_bytes(destination: Path, data: bytes, result: InstallResult, *, overwrite: bool) -> None:
    existed = destination.exists()
    if existed and not overwrite:
        result.preserved.append(destination)
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    result.append(destination)
    (result.overwritten if existed else result.created).append(destination)


def profiles_requested(*, claude: bool, copilot: bool, codex: bool) -> Iterable[str]:
    if claude:
        yield "claude"
    if copilot:
        yield "copilot"
    if codex:
        yield "codex"
