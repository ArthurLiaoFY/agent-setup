# Agent Setup — Phase 1 Final Fix

## Objective

Resolve the remaining issues identified in the Phase 1 Final Audit.

This is a focused corrective task, not an architecture redesign.

Preserve the existing project structure, CLI behavior, installation directory structure, and confirmed ownership policy.

## 1. Fix Stale Additional Instructions

Inspect:

`src/agent_setup/resources/rules/additional/task_objective.md`

Remove all obsolete references to:

- `--force`
- Overwriting existing Additional files
- Any installation behavior that conflicts with the current ownership policy

Ensure the instructions clearly communicate:

- Additional files are project-specific.
- Existing Additional files must be preserved.
- New Additional files may be installed if they do not exist.
- Project-specific objectives should be maintained independently.

Do not modify any existing user-installed Additional files.

## 2. Strengthen Resource Validation

Inspect:

`src/agent_setup/installer.py`

Current validation only verifies that a resource directory contains at least one file.

Replace this with complete resource validation.

Requirements:

1. Enumerate every expected resource file for the selected profile.
2. Validate the selected adapter resource.
3. Validate CORE.
4. Validate every file under Fundamental.
5. Validate every file under Additional.
6. Reject missing or unreadable resources.
7. Include the resource path in error messages.
8. Complete all validation before writing anything to the target project.

Do not rely on directory existence alone.

## 3. Preload Resource Contents

Before writing any files:

1. Read all validated resources into memory.
2. Build an installation plan containing source content and destination paths.
3. Verify destination paths remain within the target project.
4. Only begin writing after all resource reads succeed.

Expected execution flow:

```text
Validate Resources
       ↓
Read All Resource Bytes
       ↓
Build Installation Plan
       ↓
Execute Installation
```

Do not introduce a manifest, transaction framework, or rollback system.

Note: This protects against resource validation and read failures before installation. It does not guarantee atomic filesystem writes if a later disk or permission error occurs.

## 4. Normalize Public Installer Target

Inspect the public `install()` API.

Support both:

- `str`
- `Path`

Normalize the input immediately using `Path(target)`.

Keep the existing installation behavior unchanged.

## 5. Add Missing Tests

Extend the existing test suite.

### Resource Validation

- Missing adapter resource fails before any target writes.
- Missing CORE fails before any target writes.
- Missing individual Fundamental file fails before any target writes.
- Missing individual Additional file fails before any target writes.
- Resource read failure occurs before any target writes.

### Ownership

- Existing Additional files remain unchanged.
- Nested Additional files are preserved.
- Missing nested Additional files are installed.
- Stale Fundamental files are not deleted.
- Unrelated target files remain unchanged.

### CLI and API

- `--force` is rejected by argparse.
- `install()` accepts a string target.
- `install()` accepts a Path target.

### Adapter Tests

- Claude adapter uses `@agent_rules/CORE.md`.
- Codex adapter explicitly instructs reading CORE.
- Copilot adapter explicitly instructs reading CORE.
- No adapter embeds the full CORE content.

## 6. Verification

After implementation:

1. Run the complete test suite.
2. Build the wheel.
3. Verify all required resources are included.
4. Verify the installed package still works outside the source repository.
5. Verify all three Agent profiles.
6. Verify repeated installation behavior.
7. Run `git diff --check`.
8. Run `git status --short`.

## 7. Constraints

- Do not redesign the directory structure.
- Do not add runtime dependencies.
- Do not reintroduce `--force`.
- Never overwrite existing Additional files.
- Do not automatically delete stale Fundamental files.
- Do not modify unrelated project files.
- Do not introduce unnecessary abstractions.

## 8. Final Report

Report:

1. Modified files.
2. Resource validation changes.
3. Preloading implementation.
4. Updated Additional instructions.
5. New test cases and results.
6. Wheel verification.
7. Remaining limitations.
8. Whether Phase 1 can now be considered complete.

Do not claim atomic installation or actual Agent runtime integration unless those properties have been independently verified.