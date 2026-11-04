# Dependency Setup

## Purpose

Identify the authoritative dependency source and use uv to install or synchronize dependencies.

## Rules

1. Prefer `uv sync`, `uv add`, `uv remove`, and `uv run`.
2. Do not use pip when uv can perform the operation.
3. Preserve existing dependency declarations and lock files.
4. Do not install globally, upgrade unrelated packages, or remove packages whose purpose is unknown.
5. A requirements file does not require a pip workflow.
6. Report conflicting dependency sources before choosing one.
7. Report a damaged environment or incompatible interpreter instead of rebuilding it automatically.

## Dependency Source

Inspect sources in the following order:

1. User instructions and project documentation.
2. `pyproject.toml`.
3. `uv.lock`.
4. Requirements files.
5. Legacy package configuration.

Common files include `requirements.txt`, `requirements-dev.txt`, `setup.py`, `setup.cfg`, Pipfile, and lock files. Do not assume every detected file is authoritative.

## Setup Strategy

### uv project

Inspect dependencies and dependency groups, then run:

```bash
uv sync
```

Sync only the groups required by the current task.

### pyproject project without a lock file

Preserve `pyproject.toml` and run:

```bash
uv sync
```

### Requirements project

Check constraints, editable installs, URL or Git dependencies, nested requirements, and environment markers.

For a user-approved migration:

```bash
uv init --bare
uv add -r requirements.txt
uv add --dev -r requirements-dev.txt
```

Do not delete the original requirements files. If migration is unsafe or unnecessary, use uv's pip-compatible interface:

```bash
uv pip install -r requirements.txt
```

### Legacy project

Preserve existing configuration and installation behavior. Create uv-native configuration only when migration is safe and authorized.

### New project

Add dependencies only when required:

```bash
uv add <PACKAGE>
uv add --dev <PACKAGE>
uv sync
```

## Common Operations

| Operation | Command |
|---|---|
| Synchronize dependencies | `uv sync` |
| Add a dependency | `uv add <PACKAGE>` |
| Add a development dependency | `uv add --dev <PACKAGE>` |
| Remove a dependency | `uv remove <PACKAGE>` |
| List installed packages | `uv pip list` |
| Check lock file | `uv lock --check` |

Do not run `uv lock --upgrade` unless dependency upgrades are explicitly requested.

## Completion

Confirm:

- Dependencies were synchronized or installed successfully.
- The lock file is consistent with project configuration, when applicable.
- No global environment was modified.
- No unnecessary upgrades or removals were made.

Report the dependency source, actions, and unresolved issues. Proceed to [Project Validation](project-validation.md).
