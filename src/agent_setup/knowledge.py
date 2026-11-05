from pathlib import Path
import re

from .installer import InstallError

NUMBER_PATTERN = re.compile(r"^(PLAN|LESSON)-(\d{4})(?:-.*)?\.md$")


def next_identifier(directory: Path, kind: str) -> str:
    highest = 0
    if directory.exists():
        for path in directory.iterdir():
            match = NUMBER_PATTERN.match(path.name)
            if match and match.group(1) == kind:
                highest = max(highest, int(match.group(2)))
    return f"{kind}-{highest + 1:04d}"


def create_plan(target: Path, name: str) -> Path:
    identifier = next_identifier(target / ".agent_rules" / "additional" / "plans", "PLAN")
    return _create_document(
        target / ".agent_rules" / "additional" / "plans" / _filename(identifier, name),
        _plan_template(identifier),
    )


def create_lesson(target: Path, name: str) -> Path:
    identifier = next_identifier(target / ".agent_rules" / "additional" / "lesson_learned", "LESSON")
    return _create_document(
        target / ".agent_rules" / "additional" / "lesson_learned" / _filename(identifier, name),
        _lesson_template(identifier),
    )


def _filename(identifier: str, name: str) -> str:
    suffix = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    return f"{identifier}-{suffix}.md" if suffix else f"{identifier}.md"


def _create_document(destination: Path, content: str) -> Path:
    if destination.exists():
        raise InstallError(f"Document already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return destination


def _plan_template(identifier: str) -> str:
    return f"""# {identifier}

## Overview

## Scope

## Investigation

## Proposed Approach

## Implementation Steps

## Testing and Verification

## Risks and Open Questions

## Completion Criteria

## Execution Summary
"""


def _lesson_template(identifier: str) -> str:
    return f"""# {identifier}

## Context

## Lesson

## Action

## Verification
"""
