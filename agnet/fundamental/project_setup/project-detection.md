# Project Detection

## 1. Purpose

Inspect the existing Python project and identify its current configuration, dependency management strategy, and directory structure before performing any setup operation.

The agent MUST inspect:

- `pyproject.toml`
- `uv.lock`
- `requirements.txt` and related requirements files
- `.python-version`
- Existing project structure

This document defines project detection only. It does not authorize initializing, migrating, installing, upgrading, or modifying project files.

## 2. Mandatory Package Management Rule

**Always use `uv` whenever it is available. Never use `pip` when `uv` can perform the required operation.**

The agent MUST follow these rules throughout project setup:

1. Prefer native `uv` commands such as `uv sync`, `uv add`, `uv remove`, and `uv run`.
2. Never invoke `pip`, `pip install`, or `python -m pip` when the operation can be performed with `uv`.
3. Do not use a standalone `pip` workflow simply because the project contains `requirements.txt`.
4. If `uv` is unavailable, stop before dependency installation and follow the environment-initialization instructions for the approved `uv` setup path.
5. Do not silently switch package managers.
6. Preserve existing dependency declarations and lock files unless a later, explicitly authorized setup or migration step requires a change.

`uv pip` is also a uv command, but native project commands should be preferred for projects managed through `pyproject.toml`.

## 3. Project Root Detection

Identify the project root before inspecting configuration files.

### Requirements

- Start from the current working directory.
- Determine whether the current directory is the repository root or a nested subdirectory.
- Inspect relevant parent directories for project markers when necessary.
- Do not assume that the current working directory is the project root.
- Do not inspect unrelated directories outside the project.

Common project-root indicators include:

- `.git/`
- `pyproject.toml`
- `uv.lock`
- `requirements.txt`
- `README.md`
- `src/`
- `tests/`

If multiple candidate roots exist, report the candidates and identify which one is being inspected. Do not silently combine configurations from different projects.

## 4. pyproject.toml Detection

Check whether `pyproject.toml` exists in the project root.

If it exists, inspect its contents and identify:

- Project name and metadata.
- Python version requirement (`requires-python`).
- Build system (`build-system`).
- Runtime dependencies (`project.dependencies`).
- Optional dependency groups (`project.optional-dependencies`).
- Dependency groups (`dependency-groups`), if present.
- Tool-specific configurations.
- Build backend and package configuration.

### Requirements

- Do not assume every `pyproject.toml` is a uv-managed project.
- Identify whether the project configuration is compatible with the intended uv workflow.
- Do not overwrite existing project metadata.
- Do not add dependencies during detection.
- If the file is malformed or incomplete, report the issue without repairing it automatically.

If `pyproject.toml` does not exist, record it as missing.

## 5. uv.lock Detection

Check whether `uv.lock` exists in the project root.

If it exists, identify:

- Whether the lock file is present and readable.
- Whether it appears to belong to the current project.
- Whether it is consistent with the project's `pyproject.toml`, where this can be established without modifying files.
- Whether the project appears to use uv for dependency resolution.

### Requirements

- Treat an existing `uv.lock` as important project state.
- Do not delete or regenerate the lock file during detection.
- Do not run commands that update the lock file as part of this step.
- Do not assume that the presence of `uv.lock` alone proves the environment is synchronized.

If `uv.lock` is missing, record it as missing. Do not generate it during detection.

## 6. requirements.txt Detection

Check for common requirements files in the project root and relevant subdirectories, including:

- `requirements.txt`
- `requirements-dev.txt`
- `requirements-test.txt`
- `requirements/*.txt`

For each discovered file, record its path and inspect its dependency declarations.

Identify whether the file contains:

- Standard package requirements.
- Version constraints.
- Editable installs.
- Git or URL-based dependencies.
- Nested requirements through `-r` or `--requirement`.
- Environment markers or platform-specific dependencies.
- Constraints files or other pip-specific options.

### Requirements

- The existence of `requirements.txt` does not mean the project must use pip.
- Do not install packages from requirements files during detection.
- Do not convert requirements files into `pyproject.toml` automatically.
- Do not delete or rewrite requirements files.
- Report unsupported or ambiguous requirement formats for later review.

When a later dependency setup step needs to consume a supported requirements file, use an appropriate uv-native workflow. Do not fall back to pip.

## 7. .python-version Detection

Check whether `.python-version` exists in the project root.

If it exists, record:

- Its contents.
- The Python version or version selector specified.
- Whether it is consistent with `requires-python` in `pyproject.toml`, if both are present.

### Requirements

- Treat `.python-version` as a project-level Python version selection hint.
- Do not change the file during detection.
- Do not assume the requested Python version is installed.
- If the version conflicts with `requires-python`, report the conflict for resolution during environment setup.

If the file is missing, record it as missing. Do not create it during detection.

## 8. Existing Project Structure Detection

Inspect the project directory to understand how the Python code is organized.

At minimum, look for:

| Path / File | Purpose |
|---|---|
| `src/` | Source-layout Python package |
| Project-name directory | Common flat-layout Python package |
| `tests/` | Test code |
| `docs/` | Documentation |
| `scripts/` | Utility and automation scripts |
| `notebooks/` | Jupyter notebooks |
| `examples/` | Usage examples |
| `main.py` | Possible application entry point |
| `__main__.py` | Module execution entry point |
| `setup.py` | Legacy packaging configuration |
| `setup.cfg` | Legacy or tool configuration |
| `tox.ini` | Test and environment configuration |
| `Makefile` | Common development commands |
| `Dockerfile` | Container build configuration |
| `.gitignore` | Git ignore rules |

### Requirements

- Identify whether the project uses a `src/` layout or a flat layout.
- Identify likely application entry points without assuming they are executable.
- Identify existing test, documentation, and script directories.
- Preserve the existing architecture.
- Do not create folders or move files during detection.
- Do not force an existing project into a preferred template.
- For large repositories, inspect the top-level structure first and only expand relevant directories.

## 9. Project Classification

Based on the detected files and structure, classify the project.

Possible classifications:

### A. Existing uv-managed project

Typical indicators:

- `pyproject.toml` exists.
- `uv.lock` exists.
- The project declares dependencies in `pyproject.toml`.

Action: Preserve the current uv configuration. The dependency setup stage will determine whether synchronization is needed.

### B. Existing pyproject-based project without uv.lock

Typical indicators:

- `pyproject.toml` exists.
- `uv.lock` is missing.

Action: Inspect the build backend, dependencies, and existing package-manager configuration before deciding how to proceed with uv.

### C. Requirements-based project

Typical indicators:

- `requirements.txt` or related files exist.
- `pyproject.toml` may be missing.

Action: Preserve the requirements files. Evaluate an appropriate uv-native setup path in the dependency setup stage. Do not migrate automatically.

### D. Legacy Python project

Typical indicators:

- `setup.py`, `setup.cfg`, or other legacy configuration exists.
- Modern project metadata may be absent.

Action: Preserve the existing configuration and assess compatibility before making changes.

### E. New or empty project

Typical indicators:

- No meaningful Python project configuration exists.
- No recognizable Python source structure exists.

Action: Mark the project as a candidate for initialization. Actual initialization belongs to the environment-initialization stage.

### F. Mixed or ambiguous project

Typical indicators:

- Multiple dependency configuration files exist.
- Conflicting Python version declarations exist.
- Multiple package managers or project roots are detected.

Action: Report the ambiguity. Do not choose one configuration or migrate files without justification.

## 10. Detection Summary

Before proceeding to environment initialization or dependency setup, produce a summary using this structure:

```text
Project Detection
-----------------

Project Root:
Project Classification:

Configuration:
  pyproject.toml:
  uv.lock:
  requirements.txt:
  Other requirements files:
  .python-version:

Python Configuration:
  requires-python:
  .python-version value:
  Version conflict:

Dependencies:
  Runtime dependencies:
  Development dependencies:
  Dependency source:
  Package management strategy:

Project Structure:
  Layout: src / flat / unknown
  Source directories:
  Test directories:
  Documentation directories:
  Scripts:
  Entry point candidates:

Issues:
  - Missing configuration:
  - Conflicting configuration:
  - Unsupported or ambiguous dependency declarations:
```

Use `not found`, `not configured`, or `unknown` where appropriate. Do not invent values for unavailable information.

## 11. Completion Criteria

Project detection is complete when:

- The project root has been identified.
- Relevant project configuration files have been inspected.
- Dependency declarations and package-management strategy have been identified.
- Python version requirements have been checked.
- The existing project structure has been summarized.
- The project has been classified.
- Any conflicts or ambiguities have been reported.

After completing detection, proceed to the appropriate environment-initialization and dependency-setup instructions.

Do not install packages, initialize the project, generate lock files, or modify existing files as part of this document.
