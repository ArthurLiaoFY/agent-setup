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
    install_parser.add_argument(
        "--claude",
        action="store_true",
        help="Install Claude instructions as CLAUDE.md",
    )
    install_parser.add_argument(
        "--copilot",
        action="store_true",
        help="Install Copilot instructions in .github/copilot-instructions.md",
    )
    install_parser.add_argument(
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
        "--force",
        action="store_true",
        help="Overwrite existing instruction files",
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
    args = parser.parse_args(argv)

    profiles = list(
        profiles_requested(claude=args.claude, copilot=args.copilot, codex=args.codex)
    )
    if not profiles:
        parser.error("choose at least one of --claude, --copilot, or --codex")
    if args.global_install:
        if args.copilot or args.codex or args.path is not None:
            parser.error("--global currently supports --claude without a target path")
        targets = [Path.home() / ".claude"]
    else:
        targets = [args.path.expanduser() if args.path else Path.cwd()]

    try:
        for target in targets:
            target.mkdir(parents=True, exist_ok=True)
            for profile in profiles:
                written = install(profile, target, force=args.force)
                for path in written:
                    print(f"Installed {path}")
                if not written:
                    print(f"{profile}: no changes (use --force to overwrite)")
    except InstallError as error:
        print(f"agent-setup: error: {error}", file=sys.stderr)
        return 1

    return 0
