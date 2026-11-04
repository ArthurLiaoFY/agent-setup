# Environment Initialization

## 1. Purpose

Prepare the Python development environment based on the results of:

- `environment-detection.md`
- `project-detection.md`

This step is responsible for:

- Installing `uv` when it is required and missing.
- Initializing a new Python project when the project has not already been initialized.
- Creating or reusing the project virtual environment at `.venv`.
- Selecting the Python interpreter that satisfies the project's requirements.

**Important: If the project is already initialized and managed by uv, skip this document's initialization workflow and proceed directly to `dependency-setup.md`.**

Do not reinitialize an existing uv project.

## 2. Mandatory Rules

1. Always prefer `uv` for Python environment and package-management operations.
2. Never use `pip` when uv can perform the required operation.
3. Complete environment and project detection before making changes.
4. Preserve existing project configuration and dependency declarations.
5. Never run `uv init` in an existing initialized project.
6. Reuse a valid `.venv` instead of recreating it.
7. Do not delete or replace an existing virtual environment without explicit authorization.
8. If the project state is ambiguous or conflicting, stop and report the issue before making destructive or irreversible changes.

## 3. Decision: Is the Project Already Initialized with uv?

Use the Project Detection summary to determine the next step.

### 3.1 Already initialized with uv

Typical indicators:

- `pyproject.toml` exists.
- The project is configured as a uv-managed project.
- `uv.lock` may or may not exist.

Action:

1. Do not run `uv init`.
2. Do not recreate project metadata.
3. Do not create another project structure.
4. Proceed directly to `dependency-setup.md`.

The dependency setup stage is responsible for synchronizing dependencies and ensuring the environment is ready.

### 3.2 Existing project, not initialized with uv

Examples:

- A project with `requirements.txt` but no `pyproject.toml`.
- A legacy project with `setup.py` or `setup.cfg`.
- An existing source tree without modern Python project metadata.

Action:

1. Preserve the existing project files.
2. Determine whether the project can be safely initialized or configured for uv.
3. Do not overwrite or discard existing dependency declarations.
4. If migration or metadata conversion is needed, explain the proposed changes before applying them.
5. Initialize only after the project state and migration approach are clear.

Do not assume that the absence of `uv.lock` means the project is not uv-managed.

### 3.3 New or empty project

Typical indicators:

- No existing `pyproject.toml`.
- No existing dependency configuration that must be preserved.
- No meaningful Python package or application structure.

Action:

- Initialize the project with `uv init`.

Choose the appropriate `uv init` mode based on the intended project type. Do not blindly use a package template for an application, or an application template for a library.

## 4. Install uv When Necessary

Check the Environment Detection summary first.

If uv is already available:

- Reuse the installed executable.
- Do not reinstall or upgrade it unnecessarily.

If uv is missing:

1. Explain that uv is required by this setup workflow.
2. Install uv using the official installation method appropriate for the detected operating system.
3. Follow the official uv installation instructions: https://docs.astral.sh/uv/getting-started/installation/
4. Do not use `pip install uv`.
5. Refresh or reopen the shell environment if necessary so that `uv` is available on `PATH`.
6. Verify the installation with:

```bash
uv --version
```

If installation fails:

- Stop the setup workflow.
- Report the error and the required manual action.
- Do not fall back to pip.

## 5. Select the Python Interpreter

Determine the required Python version using the following priority:

1. Explicit user or project instructions.
2. `requires-python` in `pyproject.toml`.
3. `.python-version`.
4. Existing project environment and documented compatibility requirements.
5. A suitable stable Python version supported by the project's dependencies.

If version declarations conflict:

- Report the conflict.
- Do not silently select a version.
- Resolve the conflict before creating or changing the environment.

### Interpreter availability

Use uv to inspect or obtain the required Python interpreter.

Useful commands include:

```bash
uv python list
uv python find <VERSION>
```

If the required version is not installed, use uv's Python management capabilities when appropriate:

```bash
uv python install <VERSION>
```

Do not use system package managers or pip as an automatic fallback.

## 6. Initialize a New Project

Only execute this section when Project Detection classifies the directory as a new or empty project.

Use:

```bash
uv init
```

Choose the appropriate initialization options for the project type.

After initialization:

- Inspect the generated `pyproject.toml`.
- Confirm the project metadata.
- Confirm the Python version requirement.
- Confirm the generated files and directories.
- Do not overwrite existing files.

If the directory contains files that could conflict with initialization, inspect them first and resolve the conflict before proceeding.

## 7. Create or Reuse .venv

The default project virtual environment directory is:

```text
.venv/
```

### 7.1 Existing .venv

If `.venv` already exists:

1. Locate its Python interpreter.
2. Check whether it is usable.
3. Check its Python version against the project's requirements.
4. Reuse it if it is valid and compatible.

Do not recreate it merely because the setup workflow has started.

If it is invalid or incompatible:

- Report the detected issue.
- Explain the proposed repair or recreation.
- Do not delete or replace it without authorization.

### 7.2 No existing .venv

If no valid project `.venv` exists, create one with uv:

```bash
uv venv
```

If a specific interpreter must be selected, specify it explicitly:

```bash
uv venv --python <VERSION>
```

The resulting environment should be located at the project root under `.venv`.

### 7.3 Platform considerations

Typical interpreter paths:

| Platform | Interpreter |
|---|---|
| Windows | `.venv\Scripts\python.exe` |
| macOS / Linux | `.venv/bin/python` |

Do not hardcode one platform's interpreter path in cross-platform scripts.

## 8. Environment Initialization Validation

After initialization, verify:

- uv is executable.
- The selected Python interpreter satisfies the project requirements.
- `.venv` exists when this step is responsible for creating it.
- The virtual environment's interpreter is accessible.
- The project configuration has not been unintentionally overwritten.

Useful checks:

```bash
uv --version
uv python find <VERSION>
```

Check the virtual environment interpreter directly:

```bash
.venv/bin/python --version
```

On Windows PowerShell:

```powershell
.venv\Scripts\python.exe --version
```

Do not install dependencies in this step. Dependency installation and synchronization belong to `dependency-setup.md`.

## 9. Handoff to Dependency Setup

After successful initialization:

- If the project was already uv-initialized, proceed directly to `dependency-setup.md` without running initialization commands.
- If the project was newly initialized or safely configured for uv, proceed to `dependency-setup.md`.
- If uv installation, interpreter selection, or environment creation failed, stop and report the issue.

Provide a concise handoff summary:

```text
Environment Initialization
--------------------------

Project State:
  Classification:
  Already uv-initialized:

uv:
  Installed:
  Version:

Python:
  Selected Version:
  Interpreter:

Virtual Environment:
  Path:
  Created or Reused:
  Validation:

Next Step:
  dependency-setup.md / Blocked
```

## 10. Completion Criteria

Environment initialization is complete when:

- The uv availability requirement has been satisfied.
- The project initialization decision has been made correctly.
- Existing uv-managed projects have not been reinitialized.
- The Python interpreter has been selected and validated.
- A valid `.venv` has been reused or created when needed.
- The handoff summary has been produced.

**Do not install or synchronize project dependencies in this step. Always hand off dependency work to `dependency-setup.md`.**