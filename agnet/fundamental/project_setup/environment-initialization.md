# Environment Initialization

## Purpose

Prepare the Python interpreter and project `.venv` according to the detection results without overwriting existing project configuration.

## Rules

1. Prefer `uv` for all supported environment operations.
2. Complete environment and project detection before making changes.
3. Do not run `uv init` in an existing uv project.
4. Do not delete or recreate a valid `.venv`.
5. Do not create or replace an environment when configuration is conflicting or unclear.
6. Explain migration or configuration changes before applying them.

## Project Decision

### Existing uv project

When `pyproject.toml` or `uv.lock` indicates uv management:

- Do not run `uv init`.
- Preserve the existing metadata and lock file.
- Proceed to [Dependency Setup](dependency-setup.md).

### Requirements or legacy project

Preserve the existing configuration and installation behavior:

- Inspect existing dependency declarations and migration options.
- Do not delete requirements, `setup.py`, or `setup.cfg` files.
- Report proposed migration changes before applying them.
- Use a compatible uv workflow when migration is unsafe or not requested.

### New project

Initialize only when project detection identifies a new or empty project:

```bash
uv init
```

Review the generated `pyproject.toml`, Python requirement, and files. Do not overwrite conflicting files.

## Install uv

Reuse an existing uv installation. If uv is unavailable, use the official installation method for the detected OS and verify:

```bash
uv --version
```

Stop on installation failure. Do not fall back to pip.

## Select Python

Use the following priority:

1. Explicit user or project instruction.
2. `requires-python` in `pyproject.toml`.
3. `.python-version`.
4. Existing environment compatibility requirements.

Report conflicts instead of silently selecting or changing a version:

```bash
uv python list
uv python find <VERSION>
uv python install <VERSION>
```

## Create or Reuse `.venv`

Reuse a valid `.venv` with a compatible Python interpreter:

```bash
uv venv
uv venv --python <VERSION>
```

If an existing environment is invalid or incompatible, report it and obtain authorization before replacing or deleting it.

## Completion

Report the selected Python version, `.venv` status, and unresolved issues. Proceed to [Dependency Setup](dependency-setup.md).
