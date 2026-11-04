# Project Detection

## Purpose

Identify the project root, configuration, dependency sources, Python requirement, and project structure without modifying files.

## Required Information

- Project root directory.
- `pyproject.toml`.
- `uv.lock`.
- `requirements*.txt` or a `requirements/` directory.
- `.python-version`.
- Source layout, tests, package configuration, and entry-point candidates.

## Rules

1. Locate the project root from the current directory; do not assume it is the current directory.
2. Report multiple candidate roots and do not merge configurations from different projects.
3. Do not infer uv management from `pyproject.toml` alone.
4. Do not create, edit, delete, or regenerate project files or lock files.
5. Do not install dependencies or select a Python interpreter.
6. Report conflicting or ambiguous configuration instead of choosing automatically.

## Project Configuration

Inspect `pyproject.toml` for:

- `requires-python`.
- `[project]` metadata and dependencies.
- Dependency groups and optional dependencies.
- Build system and package layout.

Determine the dependency source in this order:

1. User instructions and project documentation.
2. `pyproject.toml` and its lock file.
3. Existing project-specific package-manager configuration.
4. Requirements files.
5. Dependencies inferred from source code.

A requirements file does not require pip. Dependency setup will select the appropriate uv workflow.

## Project Classification

| Type | Indicators |
|---|---|
| uv project | `pyproject.toml` and uv configuration or lock file |
| pyproject project | `pyproject.toml` without `uv.lock` |
| requirements project | Requirements files are the primary dependency source |
| legacy project | Uses `setup.py`, `setup.cfg`, or another existing package manager |
| new project | No project configuration or recognizable source structure |
| ambiguous project | Conflicting configuration or multiple project roots |

## Detection Summary

```text
Project Detection
Project root:
Classification:
Python requirement:
pyproject.toml: found / missing / status
uv.lock: found / missing / status
Requirements files:
Dependency source:
Layout: src / flat / unknown
Tests / entry points:
Conflicts / ambiguity:
```

## Completion

The detection is complete when the project root, configuration, structure, and conflicts are summarized. Proceed to [Environment Initialization](environment-initialization.md), or to [Dependency Setup](dependency-setup.md) for an already initialized uv project.
