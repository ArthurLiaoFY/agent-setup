# Project-Level Structure Rules

## Purpose

Define the required layout for a Python project when generating or modifying code.

Use the following layout when it matches a new or existing Python project:

```text
project/
├── config.yaml
├── main.py
├── pyproject.toml
├── src/
│   ├── submodule_a/
│   ├── submodule_b/
│   └── ...
└── tests/
```

## Required Files

### `config.yaml`

Store runtime configuration in this file. Keep credentials and secrets out of configuration committed to the repository. Document required configuration keys when needed.

### `main.py`

Use this file as the application entry point.

- Keep startup orchestration here.
- Load configuration and construct application dependencies.
- Delegate feature behavior to modules under `src/`.
- Avoid implementing reusable domain or service logic in this file.

### `pyproject.toml`

Use this file for Python metadata and dependency declarations.

- Define the supported Python version.
- Declare runtime and development dependencies.
- Keep build and tool configuration consistent with the project package layout.
- Preserve existing project configuration unless migration is explicitly requested.

### `src/`

Place reusable implementation modules under `src/`.

- Use one directory per major feature, subsystem, or implementation domain.
- Each major directory must be a self-contained Python submodule.
- Do not place application-wide reusable logic only in `main.py`.

### `tests/`

Place project-level integration and cross-submodule tests here.

- Test interactions between application components.
- Keep submodule implementation tests inside that submodule's own `tests/` directory.
- Do not duplicate submodule unit tests at project level.

## Code Generation Rules

1. Inspect the existing project before creating files.
2. Follow the existing project root; do not create a second `src/`, `tests/`, or configuration hierarchy.
3. Create files only in locations corresponding to their responsibility.
4. Keep `main.py` small and delegate implementation to `src/`.
5. Prefer focused modules over adding unrelated classes or functions to project-level files.
6. Do not generate an alternative entry point, package layout, or dependency-management configuration unless explicitly requested.
7. Preserve existing public APIs and project conventions.
8. Add or update tests for generated behavior.

## Module Boundary

Each directory under `src/` represents a distinct submodule. Generated code must:

- Own its public API through an appropriate `__init__.py`.
- Keep implementation details private to the submodule.
- Import another submodule only through its documented public API.
- Avoid circular dependencies between submodules.

## Completion

Before completing code generation, verify:

```text
Project-level structure: PASS / FAIL
Entry point: PASS / FAIL
Dependency configuration: PASS / FAIL
Project-level tests: PASS / FAIL
Cross-module boundary: PASS / FAIL
Issues:
```
