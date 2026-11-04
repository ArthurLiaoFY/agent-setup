# Environment Detection

## Purpose

Inspect the current development environment without modifying files or environment state.

## Required Information

- Operating system and architecture: Windows, macOS, or Linux.
- Available Python versions and executable paths.
- Whether `uv` is installed and its version.
- Whether Git is installed and its version.
- Whether the current directory is inside a Git repository.
- Active virtual environment, if any.
- Existing project environments such as `.venv`, `venv`, or `env`.

## Rules

1. Detect first; make no setup changes in this stage.
2. Do not assume that `python`, `python3`, and `py` resolve to the same interpreter.
3. Do not activate, create, delete, or modify an environment.
4. Do not install Python, uv, Git, or dependencies.
5. Do not run commands that change Git state.
6. Record missing commands as `not found` instead of treating them as fatal errors.
7. Do not output environment variables or secrets.
8. Preserve detected values instead of guessing unknown information.

## Detection Commands

```bash
python --version
python -c "import sys; print(sys.executable)"
uv --version
git --version
git rev-parse --is-inside-work-tree
git rev-parse --show-toplevel
git status --short --branch
```

Use platform-specific alternatives when needed:

```bash
python3 --version
py -0p
```

Python can also identify the platform and architecture:

```python
import platform, sys
print(platform.system())
print(platform.machine())
print(sys.executable)
```

## Virtual Environments

Check:

- `VIRTUAL_ENV` or `CONDA_PREFIX`.
- Whether `sys.prefix != sys.base_prefix`.
- Project directories named `.venv`, `venv`, or `env`.

Verify the interpreter exists before considering an environment valid.

| OS | Interpreter path |
|---|---|
| Windows | `.venv\Scripts\python.exe` |
| macOS / Linux | `.venv/bin/python` |

## Detection Summary

```text
Environment Detection
OS / Architecture:
Python commands:
uv: installed / not found / version / executable
Git: installed / not found / repository / root / branch / working tree
Active environment:
Project environments:
Issues:
```

## Completion

The detection is complete when the required environment information and summary are available. Proceed to [Project Detection](project-detection.md). Do not install tools, initialize projects, synchronize dependencies, or modify configuration in this stage.
