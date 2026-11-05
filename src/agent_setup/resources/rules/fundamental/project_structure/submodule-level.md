# Submodule-Level Structure Rules

## Purpose

Describe an optional example layout for a Python submodule when generating or modifying implementation code.

The following layout is an optional example for a submodule that needs multiple interchangeable
implementations. First follow the project's existing architecture and team conventions. Use this
example only when it fits the project or when the user requests it:

The file roles and implementation pattern below apply only when the project uses this structure.
Do not add a factory, version directories, or other layers solely to match this example.

```text
submodule/
├── __init__.py
├── base.py
├── factory.py
├── config.py
├── exceptions.py
├── utils.py
├── module_v1/
│   ├── __init__.py
│   └── implementation.py
├── module_v2/
│   ├── __init__.py
│   └── implementation.py
└── tests/
    ├── conftest.py
    ├── test_contract.py
    ├── test_factory.py
    ├── test_v1.py
    ├── test_v2.py
    └── data/
        ├── input/
        └── expected/
```

Only create files that are required by the submodule. The structure is a responsibility model, not a command to create every file regardless of need.

## File Responsibilities

### `__init__.py`

Expose the submodule's intentional public API.

- Import only stable public classes and functions.
- Keep concrete implementation details internal.
- Avoid exposing every internal module as public API.

### `base.py`

Define the abstract interface or contract shared by implementations.

- Use abstract base classes, protocols, or another established contract mechanism.
- Define only behavior required by clients of the submodule.
- Do not contain concrete provider-specific logic.

Example:

```python
from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    @abstractmethod
    def process(self, value: str) -> str:
        """Process a value and return the result."""
        raise NotImplementedError
```

Each implementation must override `process()` with concrete behavior while preserving the shared method signature and return type.

### `factory.py`

Select and construct implementations.

- Delegate configuration and runtime selection through the factory.
- Instantiate concrete implementations without requiring callers to know provider-specific classes.
- Raise an application-defined error for unsupported or invalid choices.

Example factory dispatch:

```python
from .config import ProcessorConfig
from .exceptions import UnsupportedModuleError
from .module_v1 import ProcessorV1
from .module_v2 import ProcessorV2


IMPLEMENTATIONS = {
    "v1": ProcessorV1,
    "v2": ProcessorV2,
}


def create_processor(config: ProcessorConfig):
    implementation = IMPLEMENTATIONS.get(config.module_version)
    if implementation is None:
        raise UnsupportedModuleError(config.module_version)
    return implementation(config)
```

The configuration selects the implementation version used by the factory:

```python
from .config import ProcessorConfig
from .factory import create_processor


config = ProcessorConfig(module_version="v2")
processor = create_processor(config)
```

Keep the concrete imports in the factory; callers should depend on the factory result or the shared contract in `base.py`, not on `module_v1` or `module_v2` directly.

### `config.py`

Define configuration schemas and validated configuration defaults.

- Keep configuration data separate from implementation logic.
- Validate required fields and supported values.
- Do not read credentials directly or embed secrets in source code.

Example:

```python
from typing import Literal

from pydantic import BaseModel, Field


class ProcessorConfig(BaseModel):
    module_version: Literal["v1", "v2"] = "v1"
    model_name: str = Field(min_length=1)
    timeout_seconds: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
```

Validate configuration by constructing the model rather than passing raw dictionaries or unvalidated values into implementations.

### `exceptions.py`

Define submodule-specific exceptions here.

- Inherit from a shared project exception only when one exists.
- Use exception names that describe the failure.
- Do not use generic exceptions for anticipated domain failures.

### `utils.py`

Contain utilities shared by multiple modules in this submodule.

- Do not turn this file into a catch-all module.
- Move unrelated helpers into focused modules.
- Remove utilities when they are used by only one implementation.

### Implementation directories

Use one directory per implementation or major version, such as `module_v1/` or `module_v2/`.

- Keep concrete, provider-specific, or version-specific logic isolated.
- Export the implementation class through the implementation package only when appropriate.
- Share behavior through the contract in `base.py` instead of duplicating public APIs.

### `tests/`

Keep tests for the contract, factory, implementations, and fixtures together with the submodule.

- Use `test_contract.py` to verify the common contract.
- Use `test_factory.py` to verify implementation selection and construction.
- Use implementation-specific test files for provider or version behavior.
- Place reusable fixtures in `conftest.py`.
- Place fixed test inputs under `data/input/` and expected outputs under `data/expected/`.

## Code Generation Rules

1. Inspect the existing implementations and tests before adding a new version or provider.
2. Add concrete implementations under their own module directory.
3. Add a new implementation to `factory.py` only through an explicit contract-compatible path.
4. Keep `__init__.py`, `base.py`, `factory.py`, and implementation modules free of circular imports.
5. Do not place configuration loading, provider selection, and implementation logic in one file unless the existing project convention requires it.
6. Prefer composition over duplicate implementation code.
7. Preserve backward compatibility with existing factory names and public exports unless migration is explicitly requested.
8. Add contract tests, factory tests, and implementation tests for new behavior.

## Example Implementation Pattern

```text
Client
  -> factory.py: select implementation
  -> base.py: shared contract
  -> module_vN/implementation.py: concrete behavior
```

When using this pattern, client code should call the public API or factory rather than import
concrete implementation classes directly.

## Completion

Before completing code generation, verify:

```text
Public API: PASS / FAIL
Shared contract: PASS / FAIL
Factory selection: PASS / FAIL
Implementation isolation: PASS / FAIL
Configuration and exceptions: PASS / FAIL
Submodule tests: PASS / FAIL
Issues:
```
