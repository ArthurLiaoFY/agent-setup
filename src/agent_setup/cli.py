from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .installer import InstallError, install, profiles_requested


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return 0 if error.code == 0 else 1

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
            target.mkdir(parents=True, exist_ok=True)
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
