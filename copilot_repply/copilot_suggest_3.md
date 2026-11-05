# Agent Setup - Phase 1 Final Fix

## Implementation Result

The remaining Phase 1 audit issues have been corrected. The implementation preserves the
existing directory structure and ownership policy.

## 1. Modified Files

- `src/agent_setup/installer.py`
- `src/agent_setup/resources/rules/additional/task_objective.md`
- `tests/test_installer.py`
- `tests/test_cli.py`

Generated review output:

- `copilot_repply/copilot_suggest_3.md`

## 2. Resource Validation Changes

The installer now validates:

- The selected adapter resource.
- `resources/core/CORE.md`.
- The complete Fundamental resource tree.
- The complete Additional resource tree.
- The four known required rule files:
  - `fundamental/project_structure/project-level.md`
  - `fundamental/project_structure/submodule-level.md`
  - `additional/task_objective.md`
  - `additional/lesson_learned.md`

Validation no longer relies on a resource directory merely containing one file. Every expected
resource file is checked individually before target writes.

Missing or unreadable resources raise `InstallError` containing the relevant packaged resource
path. Resource validation and preloading occur before target directory creation or writes.

## 3. Preloading Implementation

The execution flow is now:

```text
Validate Resources
        |
        v
Read All Resource Bytes
        |
        v
Build Installation Plan
        |
        v
Verify Destination Containment
        |
        v
Execute Writes
```

The installer builds a plan containing:

- Destination path.
- Preloaded bytes.
- Ownership behavior (`overwrite=True` or `overwrite=False`).

Every plan destination is checked to ensure it remains inside the resolved target project. This
prevents traversal through installed Markdown paths or nested rule paths.

Filesystem errors can still occur during a later write. This implementation intentionally does
not claim atomic installation or implement rollback.

## 4. Public API Target Normalization

`install()` now accepts both `str` and `Path`:

```python
install(profile: str, target: str | Path) -> InstallResult
```

The target is normalized immediately with:

```python
target = Path(target)
```

## 5. Additional Instructions

The packaged `task_objective.md` no longer references `--force` or managed-file overwriting.

It now states that:

- Additional files are project-specific.
- Existing Additional files must be preserved.
- Missing Additional files may be installed.
- Project-specific objectives are maintained independently.

## 6. New Test Cases

The suite was expanded to 27 passing tests.

Added coverage includes:

- String target support.
- Nested Additional preservation.
- Stale Fundamental preservation.
- `--force` CLI rejection.
- Claude native CORE import.
- Codex explicit CORE instruction.
- Copilot explicit CORE instruction.

Existing coverage also verifies:

- Adapter overwrite.
- CORE overwrite.
- Fundamental overwrite.
- Additional preservation.
- Missing Additional installation.
- Nested resource installation.
- Repeated managed-file installation.
- Unrelated-file preservation.
- Invalid target rejection.
- Exactly-one CLI profile selection.

## 7. Verification

### Test Suite

```text
27 passed in 0.09s
```

### Build

```bash
uv build
```

The wheel and source distribution were rebuilt successfully.

### Wheel Resources

The rebuilt wheel contains:

```text
agent_setup/resources/adapters/claude/CLAUDE.md
agent_setup/resources/adapters/codex/AGENTS.md
agent_setup/resources/adapters/copilot/copilot-instructions.md
agent_setup/resources/core/CORE.md
agent_setup/resources/rules/additional/task_objective.md
agent_setup/resources/rules/additional/lesson_learned.md
agent_setup/resources/rules/fundamental/project_structure/project-level.md
agent_setup/resources/rules/fundamental/project_structure/submodule-level.md
```

### Isolated Runtime

The rebuilt wheel was installed into an isolated virtual environment and executed outside the
source repository. Separate Codex, Claude, and GitHub Copilot targets were created successfully.

Verified output:

```text
CORE=PASS
CODEX=PASS
CLAUDE=PASS
COPILOT=PASS
```

The Claude adapter contains the native `@agent_rules/CORE.md` reference. Codex and Copilot
entry points explicitly reference `agent_rules/CORE.md`.

Repeated installation preserves existing Additional files while overwriting Adapter, CORE,
and Fundamental files.

### Git Verification

```text
git diff --check: PASS
```

## 8. Remaining Limitations

- No transaction or rollback framework is implemented; a later disk or permission failure can
  leave a partially written installation.
- Actual loading by a running Codex, Claude Code, or GitHub Copilot process has not been
  independently integration-tested.
- Missing-resource, unreadable-resource, nested Additional, and stale Fundamental tests should
  be strengthened with monkeypatched package resources if this installer becomes a library
  boundary used by callers outside the project tree.

## 9. Phase 1 Assessment

Phase 1 can now be considered complete for implementation, tests, packaging, and CLI/runtime
smoke verification. It remains subject to the documented limitation that Agent runtime loading
requires independent integration testing with each Agent.
