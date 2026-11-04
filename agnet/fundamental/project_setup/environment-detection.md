# Environment Detection

## 1. Purpose

Detect the current development environment before performing any Python project setup.

The agent MUST identify:

- Operating system and architecture.
- Available Python interpreters and their versions.
- Whether `uv` is installed and its version.
- Whether `git` is installed and its version.
- Whether the current directory belongs to a Git repository.
- Whether a virtual environment is active or already exists in the project.

This document defines detection only. It does not authorize installing tools, creating virtual environments, changing Python versions, installing dependencies, or modifying Git configurations. Those actions belong to the corresponding setup instructions.

## 2. General Rules

1. Inspect the environment before making changes.
2. Prefer portable checks that work on Windows, macOS, and Linux.
3. Do not assume that `python`, `python3`, or `py` refers to the same interpreter.
4. Do not assume that the currently active Python is the interpreter intended for this project.
5. Do not create, delete, replace, or activate an environment during detection.
6. Record unavailable commands as `not found`; do not treat that alone as a fatal error.
7. Do not expose secrets or dump the complete environment-variable list.
8. Do not initialize a Git repository or modify Git configurations during detection.
9. Do not assume that the current directory belongs to a Git repository.

## 3. Operating System Detection

Identify the operating system and machine architecture.

### Recommended detection

Use Python's standard library where Python is available:

```python
import platform
import sys

print("OS:", platform.system())
print("OS release:", platform.release())
print("Architecture:", platform.machine())
print("Python executable:", sys.executable)
```

Expected `platform.system()` values include:

- `Windows`
- `Darwin` (macOS)
- `Linux`

### Requirements

- Do not infer the OS from the shell name alone. For example, PowerShell may run on more than one platform.
- Record the architecture because it can affect interpreter and package compatibility.
- Do not assume that Linux distributions or macOS versions are interchangeable when later setup steps depend on platform-specific behavior.

## 4. Python Installation and Version Detection

Check which Python commands are available and identify the interpreter each command resolves to.

### Commands to check

| Platform | Commands to check |
|---|---|
| Windows | `python`, `py` |
| macOS / Linux | `python3`, `python` |

For every command found, collect:

- Python version.
- Executable path.
- Whether it is a virtual-environment interpreter.

Example checks:

```bash
python --version
python -c "import sys; print(sys.executable)"
```

On macOS and Linux, also check:

```bash
python3 --version
python3 -c "import sys; print(sys.executable)"
```

On Windows, also check the Python launcher when available:

```powershell
py --version
py -0p
```

`py -0p` lists Python installations known to the Windows Python launcher. It may not be available on every Windows installation.

### Requirements

- Check commands independently; one missing command does not mean Python is absent.
- Record the exact version and executable path for each discovered interpreter.
- Do not select or change the project's Python version at this stage.
- Do not assume the first interpreter found is suitable. Compare it with project requirements during project detection or environment initialization.
- If no Python interpreter is available, report that clearly and defer installation to the environment-initialization procedure.

## 5. uv Availability and Version Detection

Determine whether `uv` is available from the current command environment.

### Commands

```bash
uv --version
```

Check command resolution as appropriate for the current shell:

- Windows PowerShell: `Get-Command uv`
- Windows Command Prompt: `where uv`
- macOS / Linux: `command -v uv`

### Requirements

If `uv` is available, record:

- uv version.
- Resolved executable path, when available.

If `uv` is not available:

- Record `uv: not found`.
- Do not install it in this step.
- Continue collecting the remaining environment information.

Do not assume that `uv` is unavailable merely because one shell cannot resolve it; the command may be installed but absent from that shell's `PATH`.

## 6. Git Availability and Repository Detection

Determine whether Git is available and whether the current directory belongs to a Git repository.

### 6.1 Git Installation and Version Detection

Check whether Git is installed.

Command:

```bash
git --version
```

Check command resolution as appropriate for the current shell:

- Windows PowerShell: `Get-Command git`
- Windows Command Prompt: `where git`
- macOS / Linux: `command -v git`

If Git is available, record:

- Git version.
- Resolved executable path, when available.

If Git is not available:

- Record `git: not found`.
- Do not install Git in this step.
- Continue collecting the remaining environment information.

### 6.2 Git Repository Detection

Determine whether the current working directory belongs to a Git repository.

Commands:

```bash
git rev-parse --is-inside-work-tree
git rev-parse --show-toplevel
```

If the current directory belongs to a Git repository, collect:

- Repository root directory.
- Current branch.
- Working tree status.

To identify the current branch:

```bash
git branch --show-current
```

To inspect the working tree:

```bash
git status --short --branch
```

### 6.3 Requirements

- Check Git availability independently from repository detection.
- Do not assume that Git is available just because a `.git` directory exists.
- Do not assume that the current directory is the repository root; it may be a subdirectory.
- Use Git commands to identify the actual repository root.
- If the current directory is not inside a Git repository, report `not a Git repository`.
- If Git is unavailable, report repository detection as `not checked`.
- Distinguish a clean working tree from modified or untracked files.
- Do not execute `git init`, `git clone`, `git checkout`, `git switch`, `git pull`, `git add`, `git commit`, or other commands that modify repository state.
- Do not modify Git configuration, remotes, branches, or repository files.
- If the repository is in a detached HEAD state, report it instead of assuming a branch name.

## 7. Existing Virtual Environment Detection

Check both the currently active environment and project-local environment directories.

### 7.1 Active virtual environment

Inspect these Python values when Python is available:

```python
import sys

print("sys.prefix:", sys.prefix)
print("sys.base_prefix:", sys.base_prefix)
print("Is virtual environment:", sys.prefix != sys.base_prefix)
```

Also check whether `VIRTUAL_ENV` is set. This variable is commonly set by activated `venv` environments, but its absence does not prove that Python is not running inside a virtual environment.

On Windows, `CONDA_PREFIX` may indicate an active Conda environment. Record it as an environment indicator rather than treating it as a standard `venv`.

### 7.2 Project-local environment

Inspect the project root for common environment directories:

- `.venv/`
- `venv/`
- `env/`

Check whether the directory contains a recognizable Python executable:

| Platform | Typical interpreter path |
|---|---|
| Windows | `.venv\Scripts\python.exe` |
| macOS / Linux | `.venv/bin/python` |

Apply the same check to `venv/` or `env/` if those directories exist.

### Requirements

- Distinguish an active environment from an environment directory that merely exists.
- Record the environment directory and interpreter path when identifiable.
- Do not activate, delete, recreate, or modify an existing environment.
- Do not assume that a directory named `.venv` is valid until its interpreter can be located and checked.
- If multiple environments exist, report all candidates. Do not choose one silently.

## 8. Detection Summary

Before proceeding to the next setup stage, produce a concise summary using this structure:

```text
Environment Detection
---------------------
OS:
Architecture:

Python:
  - Command:
    Version:
    Executable:
  - Command:
    Version:
    Executable:

uv:
  Available:
  Version:
  Executable:

Git:
  Available:
  Version:
  Executable:
  Repository:
  Repository Root:
  Current Branch:
  Working Tree:

Virtual Environment:
  Active:
  Active interpreter:
  VIRTUAL_ENV:
  CONDA_PREFIX:

Project-local Environments:
  - Path:
    Interpreter:
    Exists:
  - Path:
    Interpreter:
    Exists:
```

Use `not found`, `not set`, `not detected`, or `not checked` where appropriate. Do not invent values for unavailable information.

For Git:

- `Repository`: YES / NO / NOT CHECKED
- `Working Tree`: CLEAN / MODIFIED / UNTRACKED / UNKNOWN

If the repository is in a detached HEAD state, report `DETACHED HEAD` as the current branch state.

## 9. Completion Criteria

Environment detection is complete when:

- The operating system and architecture have been identified, where possible.
- Available Python commands, versions, and executable paths have been checked.
- uv availability and version have been checked.
- Git availability and version have been checked.
- Git repository status has been identified when applicable.
- Active and project-local virtual environments have been inspected.
- The detection summary has been produced.

After completing detection, proceed to the project-detection instructions. Do not install or modify anything as part of this document.