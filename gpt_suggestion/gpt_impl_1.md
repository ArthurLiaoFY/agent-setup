# Agent Setup — Implementation Phase 1

## Objective

Implement the approved architecture changes based on the previous Architecture Review and Adapter Loading Validation.

The goal is to correct installer ownership behavior, simplify Agent adapters, enforce single-profile installation, improve failure handling, and add sufficient tests.

Do not redesign the existing project structure.

---

## 1. Confirmed Design Decisions

### 1.1 File Ownership Policy

| Resource | Installation Behavior |
|---|---|
| Agent Adapter | Always overwrite |
| `agent_rules/CORE.md` | Always overwrite |
| `agent_rules/fundamental/` | Always overwrite existing files |
| `agent_rules/additional/` | Preserve existing files; install missing files only |

Additional constraints:

- Existing additional files must never be overwritten.
- This rule applies regardless of installation options.
- Missing additional files should be installed.
- Do not modify unrelated target-project files.
- Do not delete existing files under `fundamental/` merely because they no longer exist in the central package.
- Do not delete existing files under `additional/`.

### 1.2 Remove `--force`

Remove the generic `--force` option from the CLI and installer API.

The ownership policy already determines overwrite behavior. A global force option is unnecessary and potentially dangerous.

### 1.3 Adapter Loading

Use the previously validated mechanisms:

**Codex**

Use explicit instructions to read:

`agent_rules/CORE.md`

**Claude Code**

Use native import syntax:

`@agent_rules/CORE.md`

**GitHub Copilot**

Use explicit instructions to read:

`agent_rules/CORE.md`

Do not append or duplicate the full CORE content inside adapter files.

### 1.4 Single Agent Profile

Each installation command must select exactly one profile:

- `--codex`
- `--claude`
- `--copilot`

Zero or multiple profiles must be rejected.

Prefer argparse `mutually_exclusive_group` with required selection if compatible with the current CLI design.

---

## 2. Implementation Tasks

### Task A. Installer

Modify:

`src/agent_setup/installer.py`

Requirements:

1. Separate central-managed and user-managed resource installation.
2. Always overwrite the selected adapter.
3. Always overwrite `agent_rules/CORE.md`.
4. Recursively overwrite existing files under `agent_rules/fundamental/`.
5. Install missing files under `agent_rules/additional/`.
6. Preserve existing additional files without modification.
7. Remove generic `force` behavior.
8. Preserve the current target directory structure.
9. Resolve package resources independently of the current working directory.
10. Validate all required packaged resources before starting writes.
11. Provide clear errors containing the failing destination path where possible.

Do not introduce a manifest, version-management system, or transaction framework.

### Task B. CLI

Modify:

`src/agent_setup/cli.py`

Requirements:

1. Enforce exactly one Agent profile.
2. Remove `--force`.
3. Validate the target path.
4. Reject a regular file used as the target directory.
5. Normalize filesystem errors into clear CLI errors.
6. Return a non-zero exit status on installation failure.
7. Clearly report:
   - Created files
   - Overwritten files
   - Preserved files

Keep CLI argument handling separate from installer implementation.

### Task C. Agent Adapters

Modify:

`src/agent_setup/resources/adapters/`

Update all three adapter files.

Requirements:

- Codex: explicitly instruct the Agent to read CORE.
- Claude: use native `@agent_rules/CORE.md` import.
- Copilot: explicitly instruct the Agent to read CORE.
- Do not embed CORE content in any adapter.
- Keep adapter files concise.

### Task D. Tests

Modify:

`tests/test_installer.py`

Add or update tests for:

1. Adapter overwrite behavior.
2. CORE overwrite behavior.
3. Fundamental overwrite behavior.
4. Additional preservation behavior.
5. Additional missing-file installation.
6. Additional preservation even when the old `force=True` behavior is no longer available.
7. Nested directory handling.
8. Repeated installation.
9. Unrelated file preservation.
10. Invalid target path.
11. Missing packaged resources failing before writes.
12. Correct adapter-to-CORE references.
13. No duplicated CORE content inside adapters.

Add:

`tests/test_cli.py`

Test:

1. No profile selected.
2. Exactly one profile selected.
3. Multiple profiles selected.
4. Invalid target directory.
5. Controlled filesystem error handling.

### Task E. Documentation

Update:

- `README.md`
- `README_cn.md`

Document:

1. Installation using `uv tool install`.
2. Agent profile selection.
3. Target project installation.
4. Central-managed versus user-managed resources.
5. Reinstallation behavior.
6. Removal of `--force`.

Keep both README versions consistent.

---

## 3. Implementation Constraints

- Preserve the current source directory structure.
- Preserve the current installed target directory structure.
- Do not introduce new runtime dependencies.
- Do not add unnecessary abstractions.
- Do not change the existing Python version requirement.
- Do not delete unrelated target-project files.
- Do not implement automatic deletion of stale fundamental files.
- Do not overwrite additional files under any circumstances.

---

## 4. Verification

After implementation:

1. Run the complete test suite.
2. Build the wheel.
3. Verify that all required Markdown resources are included.
4. Install the built wheel in an isolated environment.
5. Run the CLI from a working directory outside the source repository.
6. Install each Agent profile into a temporary Python project.
7. Verify the final directory structure.
8. Verify that central-managed files are updated.
9. Verify that additional files are preserved.
10. Verify that repeated installation produces the expected results.

---

## 5. Final Report

Return:

1. Summary of implemented changes.
2. Modified files.
3. Test results.
4. Wheel packaging verification results.
5. CLI installation verification results.
6. Any unresolved issues.

Do not claim that an Agent actually loads CORE unless this has been verified through an integration test using that Agent.