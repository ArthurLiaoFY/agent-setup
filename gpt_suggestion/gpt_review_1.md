# Agent Setup — Phase 1 Final Audit

## Objective

Perform a final audit of the Phase 1 implementation.

Do not modify any files.

The purpose is to verify that the actual implementation and tests match the confirmed requirements.

## 1. Adapter Audit

Inspect the final contents of all three adapters:

- `resources/adapters/codex/AGENTS.md`
- `resources/adapters/claude/CLAUDE.md`
- `resources/adapters/copilot/copilot-instructions.md`

Verify:

1. Each adapter references `agent_rules/CORE.md`.
2. Claude uses the native `@agent_rules/CORE.md` import.
3. Codex and Copilot explicitly instruct the Agent to read CORE.
4. No adapter embeds the entire CORE content.
5. No adapter contains outdated paths.
6. Explain whether any adapter was unchanged because its existing content already satisfied the requirements.

Provide the complete final content of all three adapters.

## 2. Installer Ownership Audit

Inspect the actual implementation and confirm:

| Resource | Required Behavior |
|---|---|
| Adapter | Always overwrite |
| CORE | Always overwrite |
| Fundamental | Always overwrite existing files |
| Additional | Preserve existing; install missing |

Verify that:

- `force` has been completely removed from the public API and CLI.
- Additional files cannot be overwritten through any installation code path.
- Existing unrelated files are untouched.
- Stale Fundamental files are not automatically deleted.
- Nested directories are handled correctly.

## 3. Failure Handling Audit

Verify that:

1. All required packaged resources are validated before writing.
2. Missing resources cause failure before installation begins.
3. Invalid target paths produce controlled errors.
4. Filesystem failures produce non-zero CLI exit codes.
5. The error output identifies the failing path where possible.

Identify any remaining possibility of partial installation.

## 4. Test Audit

List the actual test functions and map each one to the requirement it validates.

Do not simply report the total test count.

Identify any requirements that are not covered by automated tests.

## 5. Packaging and Runtime Audit

Provide evidence for:

1. Wheel build command and result.
2. Wheel contents for all adapters and rule resources.
3. Isolated environment installation command and result.
4. CLI execution from outside the source repository.
5. Installation results for all three Agent profiles.
6. Repeated installation behavior.

## 6. Final Git Review

Run:

- `git diff --check`
- `git status --short`

Summarize modified files and any unexpected generated artifacts.

## 7. Final Assessment

Return:

- PASS / WARNING / FAIL for each audit section.
- Remaining known limitations.
- Whether Phase 1 is ready to be considered complete.

Do not modify files.