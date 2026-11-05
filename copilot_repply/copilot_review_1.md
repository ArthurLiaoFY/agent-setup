# Agent Setup - Phase 1 Final Audit

Date: 2026-11-05

## Executive Assessment

| Section | Result |
|---|---|
| Adapter Audit | PASS |
| Installer Ownership Audit | WARNING |
| Failure Handling Audit | WARNING |
| Test Audit | WARNING |
| Packaging and Runtime Audit | PASS |
| Final Git Review | PASS |
| Overall Phase 1 Assessment | WARNING - implementation is usable, but final content validation and failure coverage should be closed |

## 1. Adapter Audit

Result: PASS

### Codex

```markdown
# Agent Instructions

The shared core and project rules are installed under `agent_rules/`. Read `agent_rules/CORE.md`
before starting implementation, and follow the rules linked from that entry.
```

Codex explicitly instructs the Agent to read the installed CORE. No CORE body is embedded.

### Claude

```markdown
# Claude Code Adapter

@agent_rules/CORE.md
```

Claude uses the native import syntax and no CORE content is embedded.

### GitHub Copilot

```markdown
# GitHub Copilot Adapter

Apply the repository-wide rules below in full:

The shared core and project rules are installed under `agent_rules/`. Read `agent_rules/CORE.md`
before starting implementation, and follow the rules linked from that entry.
```

GitHub Copilot is explicitly instructed to read CORE. No CORE body is embedded.

### Adapter findings

- All three adapters reference `agent_rules/CORE.md`.
- Claude uses `@agent_rules/CORE.md`.
- Codex and GitHub Copilot use explicit read instructions.
- No adapter duplicates the complete CORE file.
- No outdated `agent/` path was found in the adapters.
- The Codex and Copilot adapters were retained because their existing concise instructions already satisfied the requirement; Claude now uses the reviewed native import.

## 2. Installer Ownership Audit

Result: WARNING

| Resource | Implementation | Result |
|---|---|---|
| Adapter | `_write_resource(..., overwrite=True)` | PASS |
| CORE | `_write_resource(..., overwrite=True)` | PASS |
| Fundamental | `_install_directory(..., overwrite=True)` | PASS |
| Additional | `_install_directory(..., overwrite=False)` | PASS |

Verified code paths:

- `force` is not present in the installer public API or CLI.
- Additional writes call `_write_resource(..., overwrite=False)`, and `_write_resource()` returns without writing when the destination exists.
- `_install_directory()` also preserves an existing destination before copying.
- Unrelated project files are not traversed or written.
- Fundamental source entries that no longer exist remain untouched in the target.
- Nested directories are recursively created under both Fundamental and Additional.

Warnings:

- Packaged `task_objective.md` still says that existing files are overwritten through `--force`. This is stale content and conflicts with the implemented ownership policy.
- The installer accepts an arbitrary `target: Path`, while conversion to `target = Path(target)` is left implicit. Public callers may pass a string and fail before reaching controlled validation. The CLI already normalizes path values to `Path`.
- The generic `force` option is absent from implementation and tests, but the stale rule content must be corrected before Phase 1 can be fully complete.

## 3. Failure Handling Audit

Result: WARNING

Passed behavior:

- Adapter existence is checked before writes.
- CORE existence is checked.
- Directory resources are checked for at least one nested file.
- A regular-file target is rejected with a controlled `InstallError`.
- The CLI catches `InstallError` and `OSError`, prints an error, and returns status 1.
- CLI-specific file-target handling prints the full destination path.

Remaining gaps:

- `_validate_resources()` validates only that an entire directory tree contains at least one file. A missing expected individual file can still pass validation if sibling resources exist.
- CORE and adapter validation happen before rule directory writes, but directory traversal and write failures can still occur after some writes have started.
- Validation does not pre-stage all bytes. A later read failure from a packaged resource can therefore leave partial installation.
- The installer wraps `OSError` raised while copying rules as:

  ```text
  Cannot install files under <target>: <error>
  ```

  Other filesystem failures while reading/copying CORE or an adapter identify the destination.
- Partial installation is possible because the implementation uses sequential writes rather than transaction or rollback. This is acceptable under the stated constraint if resource validation is complete, but the implementation should validate every expected packaged file before any write.

## 4. Test Audit

Result: WARNING

### Installer tests

| Test | Requirement covered |
|---|---|
| `test_install_claude` | Claude adapter is installed and contains the native CORE import. |
| `test_root_entries_reference_canonical_rules` | Repository root AGENTS references the canonical CORE source path. |
| `test_install_copilot` | Copilot entry is installed at `.github/copilot-instructions.md`. |
| `test_install_codex` | Codex entry is installed as `AGENTS.md`. |
| `test_install_includes_core_and_rules` | CORE and nested Fundamental files are installed. |
| `test_installed_adapter_references_installed_core` | Codex entry references `agent_rules/CORE.md`. |
| `test_repeated_install_overwrites_managed_files` | Repeated installation overwrites an existing managed adapter and records it. |
| `test_multiple_profiles_share_installed_rules` | Multiple API installations share the same rule directory. |
| `test_existing_adapter_is_overwritten` | Existing adapter is overwritten. |
| `test_unknown_profile` | Unsupported profiles raise `InstallError`. |
| `test_existing_core_is_overwritten` | Existing CORE is overwritten. |
| `test_existing_fundamental_is_overwritten` | Existing Fundamental content is overwritten. |
| `test_existing_additional_is_preserved` | Existing Additional content is preserved. |
| `test_missing_additional_is_installed` | Missing Additional files are created. |
| `test_unrelated_file_is_preserved` | Unrelated target files remain untouched. |
| `test_regular_file_target_is_rejected` | Regular-file targets raise `InstallError`. |

### CLI tests

| Test | Requirement covered |
|---|---|
| `test_cli_requires_profile` | Zero profiles are rejected. |
| `test_cli_accepts_exactly_one_profile` | Exactly one profile succeeds. |
| `test_cli_rejects_multiple_profiles` | Multiple profiles are rejected. |
| `test_cli_rejects_file_target` | File targets are rejected with controlled CLI behavior. |

### Coverage gaps

- No test confirms every expected packaged resource is prevalidated before writes.
- No missing-adapter resource test.
- No missing-rule-resource test.
- No nested Additional directory test with multiple levels.
- No stale Fundamental file preservation test.
- No filesystem permission-error test.
- No test verifies that `--force` is rejected by argparse.
- No Copilot or Claude adapter test verifies both adapter reference/loading requirements and absence of duplicated CORE.
- No test verifies a partial-installation scenario caused by failure after writes begin.
- Current test suite: 20 tests pass.

## 5. Packaging and Runtime Audit

Result: PASS

Verified packaging:

```bash
uv build
```

The command produced:

```text
dist/agent_setup-0.1.0-py3-none-any.whl
dist/agent_setup-0.1.0.tar.gz
```

Wheel resources were verified with:

```bash
unzip -l dist/agent_setup-0.1.0-py3-none-any.whl
```

Present resources include:

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

Isolated installation evidence used:

```bash
verify_dir=$(mktemp -d /tmp/agent_setup_verify.XXXXXX)
uv venv "$verify_dir/.venv"
uv pip install --python "$verify_dir/.venv/bin/python" dist/*.whl
cd /tmp
"$verify_dir/.venv/bin/agent-setup" install --codex "$verify_dir/codex"
"$verify_dir/.venv/bin/agent-setup" install --claude "$verify_dir/claude"
"$verify_dir/.venv/bin/agent-setup" install --copilot "$verify_dir/copilot"
```

All three profiles installed successfully. The isolated CLI was executed from `/tmp`, outside
the source repository.

Observed targets:

```text
codex/AGENTS.md
claude/CLAUDE.md
copilot/.github/copilot-instructions.md
```

Each target also received CORE, Fundamental, and Additional resources under `agent_rules/`.

Repeated Codex installation produced:

```text
Overwritten: adapter, CORE, and Fundamental files
Preserved: Additional files
```

The implementation was not run through an actual Codex, Claude Code, or GitHub Copilot
session, so agent-runtime loading remains unverified. This report does not claim such an
integration result.

## 6. Final Git Review

Result: PASS

### `git diff --check`

```text
Exit status: 0
```

### `git status --short`

Expected implementation and review paths are modified or added. The notable unexpected
generated artifact is the existing build output:

```text
dist/
```

Depending on repository state, `build/` and Python egg-info directories should also remain
ignored and should not be staged.

Current status includes source restructuring, implementation changes, tests, documentation,
checklists, and review reports already present in the working tree. These are significant
pre-existing Phase 1 changes, not new edits from this audit.

## 7. Final Assessment

### Known limitations

1. Remove the obsolete `--force` statement from `agent_rules/additional/task_objective.md`.
2. Change resource validation to enumerate and validate every required packaged file.
3. Preload all resource bytes before writes so later packaged read failures cannot cause
   partial writes.
4. Add tests for missing resources, stale Fundamental preservation, nested Additional
   directories, filesystem failures, and rejection of `--force`.
5. Decide whether the public installer API should normalize string targets to `Path`.
6. Actual Agent runtime loading has not been tested by an integration harness.

### Phase 1 readiness

Phase 1 is not ready to be considered fully complete while the stale `--force` instruction
remains in packaged project rules and missing-resource validation is not complete. Core
ownership behavior and packaging/runtime smoke checks are working, but these warnings are
within Phase 1 scope and should be closed before final approval.
