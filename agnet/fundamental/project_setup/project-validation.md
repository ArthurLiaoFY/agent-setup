# Project Validation

## 1. Objective

Verify that the Python project environment has been correctly initialized and that the project is ready for development or execution.

This stage is responsible for:

- Verifying the selected Python interpreter.
- Verifying installed dependencies.
- Verifying critical package imports.
- Verifying the project entry point.
- Identifying environment or configuration issues that may prevent the project from running.

The goal is to confirm that the environment is usable without introducing unnecessary changes to the project.

---

## 2. Prerequisites

Before proceeding, review the results from the previous setup stages:

- `environment-detection.md`
- `project-detection.md`
- `environment-initialization.md`
- `dependency-setup.md`

Use the previous stage summaries to identify:

- Project root directory.
- Expected Python version.
- Expected virtual environment path.
- Dependency declaration source.
- Lockfile location, if applicable.
- Project type and entry point.
- Dependencies that are expected to be available.

Do not assume that previous setup stages completed successfully. Verify their results independently.

---

## 3. Validation Rules

1. Validation must be performed within the project root directory.
2. Use the project's intended virtual environment.
3. Prefer `uv run` for executing Python validation commands in uv-managed projects.
4. Do not use the system Python if a project-local environment is expected.
5. Do not install, upgrade, remove, or modify dependencies during validation.
6. Do not regenerate or modify lockfiles.
7. Do not modify project source code or configuration files to make validation pass.
8. Do not execute destructive commands or operations that modify production data.
9. If a validation step fails, report the error and identify its likely cause.
10. Do not report validation as successful based only on command availability or package installation status.

---

## 4. Python Interpreter Validation

Verify that the project is using the expected Python interpreter.

### 4.1 Verify Python Version

Execute:

```bash
uv run python --version
```

Compare the reported version with:

- The Python version selected during Environment Initialization.
- The `requires-python` constraint in `pyproject.toml`, if available.
- The project's documented Python compatibility requirements.

### 4.2 Verify Interpreter Path

Execute:

```bash
uv run python -c "import sys; print(sys.executable)"
```

Expected interpreter location:

| Platform | Expected Path |
|---|---|
| Windows | `.venv\Scripts\python.exe` |
| macOS / Linux | `.venv/bin/python` |

The actual path should resolve to the intended project environment.

### 4.3 Verify Virtual Environment

Execute:

```bash
uv run python -c "import sys; print('prefix:', sys.prefix); print('base_prefix:', sys.base_prefix); print('is_venv:', sys.prefix != sys.base_prefix)"
```

Verify that:

- Python is running inside the intended virtual environment.
- The interpreter version is compatible with project requirements.
- The interpreter path is consistent with the detected project environment.

If the project intentionally uses a different environment strategy, validate against the documented configuration instead.

### Pass Criteria

- Python interpreter is available.
- Python version satisfies project requirements.
- Interpreter path matches the intended environment.
- Virtual environment is correctly selected when required.

---

## 5. Installed Package Validation

Verify that required dependencies are installed and consistent with the project configuration.

### 5.1 Verify Dependency Synchronization

For uv-managed projects:

```bash
uv sync --check
```

This checks whether the project environment is synchronized with its dependency configuration without performing synchronization.

If the installed uv version does not support this option, use the appropriate non-modifying validation method and report the limitation.

### 5.2 Verify Lockfile Consistency

For projects using `uv.lock`:

```bash
uv lock --check
```

Verify that the lockfile is consistent with `pyproject.toml`.

Do not run:

```bash
uv lock --upgrade
```

or other commands that intentionally change dependency versions.

### 5.3 Inspect Installed Packages

Execute:

```bash
uv pip list
```

Check whether expected dependencies are present.

For a more detailed dependency inspection:

```bash
uv pip tree
```

Use these results to identify:

- Missing dependencies.
- Unexpected dependency versions.
- Potential dependency conflicts.
- Packages installed outside the intended environment.

For requirements-based projects, compare the installed packages against the authoritative requirements files.

### Pass Criteria

- Required dependencies are installed.
- Dependency synchronization check passes, when applicable.
- Lockfile is consistent, when applicable.
- No known dependency conflicts prevent project execution.

---

## 6. Import Validation

Verify that critical dependencies can be imported successfully.

### 6.1 Identify Critical Packages

Determine which packages should be validated based on:

1. Direct dependencies declared in `pyproject.toml`.
2. Dependencies required by the project entry point.
3. Critical third-party packages used by the application.
4. Explicit project documentation.

Do not attempt to import every installed package.

### 6.2 Execute Import Checks

Example:

```bash
uv run python -c "import requests; print('requests: OK')"
```

For multiple packages:

```bash
uv run python -c "import requests, pydantic, fastapi; print('Import validation: OK')"
```

Use the actual packages required by the project.

### 6.3 Import Failure Handling

If an import fails, identify the possible cause:

- Package is not installed.
- Incorrect package or module name.
- Missing system-level dependency.
- Incompatible package version.
- Incorrect Python interpreter.
- Missing environment variables or runtime configuration.
- Import path or project structure issue.

Do not automatically install missing packages.

Report the issue and hand it back for correction through the appropriate setup stage.

### Pass Criteria

- All identified critical packages can be imported.
- No unresolved import errors prevent the project from starting.

---

## 7. Project Entry Point Validation

Verify that the project has a valid and identifiable execution entry point.

### 7.1 Identify Entry Point

Inspect the project structure and configuration to identify how the application is intended to start.

Common entry points include:

| Project Type | Possible Entry Point |
|---|---|
| Python script | `main.py` |
| Python package | `python -m package_name` |
| FastAPI | `uvicorn main:app` |
| Flask | `flask --app app run` |
| Streamlit | `streamlit run app.py` |
| CLI application | Configured console script |
| Test project | `pytest` |

These are examples only. Do not assume that a project uses a particular entry point based solely on its project type.

Check:

- `pyproject.toml` for `[project.scripts]`.
- Project documentation such as `README.md`.
- Existing application structure.
- Framework-specific application definitions.
- Existing startup scripts or configuration.

### 7.2 Verify Entry Point Availability

Confirm that:

- The entry point file or module exists.
- Required application objects or functions are defined.
- Referenced modules can be resolved.
- Required configuration files are present.

For a Python script:

```bash
uv run python -c "import main; print('Entry point import: OK')"
```

Replace `main` with the actual module name.

For a Python package:

```bash
uv run python -m package_name --help
```

For a CLI application:

```bash
uv run <command> --help
```

Use the actual configured command.

### 7.3 Verify Application Startup

If the project has a documented, safe startup command, execute it when appropriate.

Examples:

```bash
uv run python main.py
```

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Important:

- Prefer startup checks that do not modify external systems or persistent data.
- Do not start long-running services without a clear reason.
- Do not assume that a successful process launch proves all application features work.
- If startup requires credentials, external services, databases, or unavailable infrastructure, report the missing prerequisites.
- Do not invent environment variables, credentials, or configuration values.

### Pass Criteria

- The intended entry point has been identified.
- Required entry point files and modules exist.
- The entry point can be resolved.
- A safe startup check succeeds when applicable.

If startup cannot be tested because external services or credentials are unavailable, report `NOT VERIFIED` rather than `PASS`.

---

## 8. Error Handling

If any validation step fails:

1. Capture the complete error message.
2. Identify the failing validation category.
3. Determine whether the issue is related to:
   - Python interpreter selection.
   - Virtual environment configuration.
   - Missing dependencies.
   - Dependency version conflicts.
   - Import errors.
   - Project structure.
   - Missing configuration.
   - External service dependencies.
   - Application startup errors.
4. Report the root cause when identifiable.
5. Recommend the smallest corrective action.
6. Do not modify the project automatically to force validation to pass.

If the issue requires changes to the environment or dependencies, hand it back to the appropriate setup stage.

If the issue requires source code changes, report it separately instead of modifying application code during Project Validation.

---

## 9. Validation Summary

After completing validation, provide a concise report:

```text
Project Validation Summary

Project Root:
Project Type:
Package Manager: uv

Python Interpreter:
- Expected Version:
- Actual Version:
- Interpreter Path:
- Virtual Environment: PASS / FAIL

Installed Packages:
- Dependency Synchronization: PASS / FAIL / NOT APPLICABLE
- Lockfile Consistency: PASS / FAIL / NOT APPLICABLE
- Required Packages: PASS / FAIL

Import Validation:
- Critical Imports: PASS / FAIL
- Failed Imports:

Project Entry Point:
- Entry Point:
- Entry Point Exists: PASS / FAIL
- Module Resolution: PASS / FAIL
- Startup Check: PASS / FAIL / NOT VERIFIED

Overall Status:
PASS / FAIL / PARTIAL

Issues:
- None / List unresolved issues

Recommended Actions:
- None / List required actions
```

### Overall Status Rules

- `PASS`: All applicable validation checks passed.
- `FAIL`: One or more critical checks failed.
- `PARTIAL`: Environment checks passed, but some checks could not be completed due to unavailable external services, credentials, or other prerequisites.

Do not mark the project as `PASS` if a critical validation step remains unresolved.

---

## 10. Completion Criteria

Project Validation is complete when:

- [ ] Python interpreter version is verified.
- [ ] Python executable path is verified.
- [ ] The intended virtual environment is verified.
- [ ] Required dependencies are verified.
- [ ] Lockfile consistency is checked when applicable.
- [ ] Critical package imports are verified.
- [ ] Project entry point is identified.
- [ ] Entry point availability is verified.
- [ ] Application startup is tested when safe and applicable.
- [ ] Validation summary is generated.
- [ ] All unresolved issues are documented.

---

## 11. Final Handoff

After completing Project Validation:

1. Report the overall validation status.
2. List any unresolved environment or dependency issues.
3. Do not automatically modify source code or dependency configurations.
4. If all critical checks pass, report that the project environment is ready for development.

Project Setup is complete.