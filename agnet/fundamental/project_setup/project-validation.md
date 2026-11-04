# Project Validation

## Purpose

Verify that the project environment, dependencies, and entry point are usable without changing configuration or source code.

## Rules

1. Run validation from the project root.
2. Use the intended `.venv` and Python interpreter.
3. Prefer `uv run` for Python commands.
4. Do not install, upgrade, remove, or synchronize packages during validation.
5. Do not update lock files.
6. Do not modify source code to make validation pass.
7. Do not run commands that access external services, modify data, or perform destructive operations.
8. Report `NOT VERIFIED` when validation cannot be completed.

## Validate the Environment

Check the Python version and interpreter:

```bash
uv run python --version
uv run python -c "import sys; print(sys.executable)"
```

Confirm compatibility with `requires-python`, `.python-version`, and project documentation. Expected environments are:

- Windows: `.venv\Scripts\python.exe`
- macOS / Linux: `.venv/bin/python`

## Validate Dependencies

For uv projects, run:

```bash
uv lock --check
uv pip list
```

Check synchronization only when supported. Do not bypass a dependency failure with arbitrary package installation. Validate only packages relevant to the project.

## Validate Imports

Determine critical imports from:

- Direct dependencies.
- Dependencies required by the entry point.
- Packages identified by project documentation.

```bash
uv run python -c "import <PACKAGE>; print('<PACKAGE>: OK')"
```

Record import failures and their likely causes. Do not install missing packages automatically.

## Validate the Entry Point

Find the entry point in:

- `pyproject.toml` `[project.scripts]`.
- Project documentation.
- `main.py`, `__main__.py`, or framework application objects.

Run only a minimal, safe check:

```bash
uv run python <ENTRYPOINT> --help
uv run <CONFIGURED_COMMAND> --help
uv run python -m <MODULE> --help
```

Run startup commands only when they do not modify data or require unavailable external services.

## Error Handling

When validation fails:

1. Preserve the complete error message.
2. Identify the relevant category: Python, virtual environment, dependencies, imports, entry point, or external service.
3. Recommend the smallest corrective action.
4. Return environment or dependency fixes to the corresponding setup stage.
5. Report source-code issues separately instead of modifying application code.

## Validation Summary

```text
Project Validation
Python / virtual environment: PASS / FAIL
Dependencies / lock file: PASS / FAIL / NOT APPLICABLE
Critical imports: PASS / FAIL
Entry point: PASS / FAIL / NOT VERIFIED
Overall: PASS / PARTIAL / FAIL
Issues:
Recommended actions:
```

Status definitions:

- `PASS`: All applicable checks passed.
- `PARTIAL`: Environment checks passed, but external prerequisites prevented validation.
- `FAIL`: One or more critical checks failed.

## Completion

Report that the project is ready only when all critical checks pass. Otherwise, document unresolved issues and do not declare setup complete.
