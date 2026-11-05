from __future__ import annotations

import argparse
import hashlib
import json
import sys
from importlib.resources import files
from pathlib import Path

from .installer import InstallError, install, profiles_requested, read_install_manifest
from .knowledge import create_lesson, create_plan
from .manifest import (
    ADDITIONAL_DESTINATION,
    ADAPTER_DESTINATIONS,
    CORE_DESTINATION,
    FUNDAMENTAL_DESTINATION,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-setup",
        description="Install shared AI coding-agent instructions.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    install_parser = commands.add_parser("install", help="Install an instruction profile")
    profile_group = install_parser.add_mutually_exclusive_group(required=True)
    profile_group.add_argument(
        "--claude",
        action="store_true",
        help="Install Claude instructions as CLAUDE.md",
    )
    profile_group.add_argument(
        "--copilot",
        action="store_true",
        help="Install Copilot instructions in .github/copilot-instructions.md",
    )
    profile_group.add_argument(
        "--codex",
        action="store_true",
        help="Install Codex instructions as AGENTS.md",
    )
    install_parser.add_argument(
        "--global",
        action="store_true",
        dest="global_install",
        help="Install for Claude under the current user's ~/.claude directory",
    )
    install_parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="Target project directory (defaults to the current directory)",
    )
    plan_parser = commands.add_parser("plan", help="Manage implementation plans")
    plan_commands = plan_parser.add_subparsers(dest="plan_command", required=True)
    plan_add = plan_commands.add_parser("add", help="Create the next implementation plan")
    plan_add.add_argument("name")
    plan_add.add_argument("path", nargs="?", type=Path)

    lesson_parser = commands.add_parser("lesson", help="Manage lessons")
    lesson_commands = lesson_parser.add_subparsers(dest="lesson_command", required=True)
    lesson_add = lesson_commands.add_parser("add", help="Create the next lesson")
    lesson_add.add_argument("name")
    lesson_add.add_argument("path", nargs="?", type=Path)

    status_parser = commands.add_parser("status", help="Show an agent-rule installation")
    status_parser.add_argument("path", nargs="?", type=Path)

    uninstall_parser = commands.add_parser("uninstall", help="Remove an agent-rule installation")
    uninstall_parser.add_argument("path", nargs="?", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return 0 if error.code == 0 else 1

    if args.command == "plan":
        target = args.path.expanduser() if args.path else Path.cwd()
        try:
            print(create_plan(target, args.name))
        except (InstallError, OSError) as error:
            print(f"agent-setup: error: {error}", file=sys.stderr)
            return 1
        return 0
    if args.command == "lesson":
        target = args.path.expanduser() if args.path else Path.cwd()
        try:
            print(create_lesson(target, args.name))
        except (InstallError, OSError) as error:
            print(f"agent-setup: error: {error}", file=sys.stderr)
            return 1
        return 0
    if args.command == "status":
        target = args.path.expanduser() if args.path else Path.cwd()
        manifest = target / ".agent_rules" / "manifest.json"
        if manifest.is_file():
            try:
                data = read_install_manifest(target)
            except InstallError as error:
                print(f"agent-setup: error: {error}", file=sys.stderr)
                return 1
            print(f"Installed: {target}")
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(f"Not installed: {target}")
        return 0
    if args.command == "uninstall":
        target = args.path.expanduser() if args.path else Path.cwd()
        manifest = target / ".agent_rules" / "manifest.json"
        if not manifest.is_file():
            print(f"Not installed: {target}")
            return 0
        try:
            data = read_install_manifest(target)
        except InstallError as error:
            print(f"agent-setup: error: {error}", file=sys.stderr)
            return 1
        if target.resolve() != manifest.parent.resolve().parent.resolve():
            print("agent-setup: error: invalid installation manifest location", file=sys.stderr)
            return 1
        profiles = data.get("profiles", [data.get("profile")] if data.get("profile") else [])
        allowed = {CORE_DESTINATION.as_posix()}
        for installed_profile in profiles:
            for relative in ADAPTER_DESTINATIONS.get(installed_profile, ()):
                allowed.add(relative.as_posix())
        rules_root = files("agent_setup").joinpath("resources", "rules")
        for section, destination in (
            ("fundamental", FUNDAMENTAL_DESTINATION),
            ("additional", ADDITIONAL_DESTINATION),
        ):
            section_root = rules_root.joinpath(section)
            for relative in _resource_file_paths(section_root):
                allowed.add((destination / relative).as_posix())
        for relative in data["managedFiles"]:
            path = (target / relative).resolve()
            if target.resolve() not in path.parents or relative not in allowed:
                print(f"agent-setup: error: invalid managed path: {relative}", file=sys.stderr)
                return 1
        managed_files = data["managedFiles"]
        for relative, expected_hash in managed_files.items():
            path = target / relative
            if path.is_file():
                current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                if current_hash == expected_hash:
                    path.unlink()
        manifest.unlink(missing_ok=True)
        rules = target / ".agent_rules"
        for directory in sorted(rules.rglob("*"), key=lambda path: len(path.parts), reverse=True):
            if directory.is_dir():
                try:
                    directory.rmdir()
                except OSError:
                    pass
        if rules.exists() and not any(rules.iterdir()):
            rules.rmdir()
        print(f"Uninstalled: {target}")
        return 0

    profiles = list(
        profiles_requested(claude=args.claude, copilot=args.copilot, codex=args.codex)
    )
    if args.global_install:
        if args.copilot or args.codex or args.path is not None:
            parser.error("--global currently supports --claude without a target path")
        targets = [Path.home() / ".claude"]
    else:
        targets = [args.path.expanduser() if args.path else Path.cwd()]
    target_files = [target for target in targets if target.exists() and target.is_file()]
    if target_files:
        print(
            f"agent-setup: error: target path must be a directory: {target_files[0]}",
            file=sys.stderr,
        )
        return 1

    try:
        for target in targets:
            for profile in profiles:
                result = install(profile, target)
                for path in result.created:
                    print(f"Created {path}")
                for path in result.overwritten:
                    print(f"Overwritten {path}")
                for path in result.preserved:
                    print(f"Preserved {path}")
                if not result:
                    print(f"{profile}: no changes")
    except (InstallError, OSError) as error:
        print(f"agent-setup: error: {error}", file=sys.stderr)
        return 1

    return 0


def _resource_file_paths(directory, prefix: Path = Path()) -> list[Path]:
    paths: list[Path] = []
    for entry in directory.iterdir():
        relative = prefix / entry.name
        if entry.is_dir():
            paths.extend(_resource_file_paths(entry, relative))
        elif entry.is_file() and entry.name != ".DS_Store":
            paths.append(relative)
    return paths
