from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Iterable
import json
import hashlib
import os
import re
import tempfile

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

    backups: dict[Path, bytes | None] = {}
    try:
        manifest_path = target / Path(*MANAGED_LOCAL_MANIFEST.parts)
        backups.setdefault(manifest_path, manifest_path.read_bytes() if manifest_path.is_file() else None)
        for item in plan:
            _write_bytes(item.destination, item.content, result, overwrite=item.overwrite, target=target, backups=backups)
        for relative in ADDITIONAL_DIRECTORIES:
            (target / Path(*relative.parts)).mkdir(parents=True, exist_ok=True)
        _write_local_manifest(target, profile, result)
    except Exception as error:
        for destination in reversed(list(backups)):
            try:
                if backups[destination] is None:
                    destination.unlink(missing_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(backups[destination])
            except OSError:
                pass
        if isinstance(error, InstallError):
            raise
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


def read_install_manifest(target: Path) -> dict:
    destination = target / Path(*MANAGED_LOCAL_MANIFEST.parts)
    try:
        data = json.loads(destination.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise InstallError(f"Invalid installation manifest: {error}") from error
    if not isinstance(data, dict) or data.get("version") != 1:
        raise InstallError("Invalid installation manifest version")
    profile = data.get("profile")
    if "profile" in data and (not isinstance(profile, str) or profile not in ADAPTER_DESTINATIONS):
        raise InstallError("Invalid installation manifest profile")
    profiles = data.get("profiles", [profile] if profile else [])
    managed = data.get("managedFiles", {})
    if not isinstance(profiles, list) or not all(
        isinstance(item, str) and item in ADAPTER_DESTINATIONS for item in profiles
    ):
        raise InstallError("Invalid installation manifest profiles")
    if not isinstance(managed, dict):
        raise InstallError("Invalid installation manifest managedFiles")
    for relative, digest in managed.items():
        if not isinstance(relative, str) or not isinstance(digest, str):
            raise InstallError("Invalid installation manifest managedFiles entry")
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or re.fullmatch(r"[0-9a-fA-F]{64}", digest) is None:
            raise InstallError(f"Invalid installation manifest path: {relative}")
        resolved = (target / path).resolve()
        if resolved != target.resolve() and target.resolve() not in resolved.parents:
            raise InstallError(f"Installation manifest path escapes target: {relative}")
    return data


def _write_local_manifest(target: Path, profile: str, result: InstallResult) -> None:
    destination = target / Path(*MANAGED_LOCAL_MANIFEST.parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if destination.exists():
        existing = read_install_manifest(target)
    profiles = set(existing.get("profiles", []))
    if existing.get("profile"):
        profiles.add(existing["profile"])
    profiles.add(profile)
    old_managed = existing.get("managedFiles", {})
    managed: dict[str, str] = {}
    for relative, digest in old_managed.items():
        path = target / Path(relative)
        if path.is_file() and sha256(path) == digest:
            managed[relative] = digest
    managed.update({
        path.relative_to(target).as_posix(): sha256(path)
        for path in result.written
        if path.is_file()
    })
    content = json.dumps(
        {
            "version": 1,
            "profile": profile,
            "profiles": sorted(profiles),
            "managedDirectories": ["/".join(path.parts) for path in ADDITIONAL_DIRECTORIES],
            "managedFiles": managed,
        },
        indent=2,
        sort_keys=True,
    ) + "\n"
    fd, temporary = tempfile.mkstemp(dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except OSError:
        if Path(temporary).exists():
            Path(temporary).unlink()
        raise


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_bytes(
    destination: Path,
    data: bytes,
    result: InstallResult,
    *,
    overwrite: bool,
    target: Path,
    backups: dict[Path, bytes | None],
) -> None:
    existed = destination.exists()
    if existed and not overwrite:
        result.preserved.append(destination)
        return
    if existed and overwrite:
        manifest = read_install_manifest(target) if (target / Path(*MANAGED_LOCAL_MANIFEST.parts)).exists() else {}
        relative = destination.relative_to(target).as_posix()
        managed_hash = manifest.get("managedFiles", {}).get(relative)
        if managed_hash != sha256(destination):
            result.preserved.append(destination)
            return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination not in backups:
        backups[destination] = destination.read_bytes() if existed else None
    fd, temporary = tempfile.mkstemp(dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except OSError:
        if Path(temporary).exists():
            Path(temporary).unlink()
        raise
    result.append(destination)
    (result.overwritten if existed else result.created).append(destination)


def profiles_requested(*, claude: bool, copilot: bool, codex: bool) -> Iterable[str]:
    if claude:
        yield "claude"
    if copilot:
        yield "copilot"
    if codex:
        yield "codex"
