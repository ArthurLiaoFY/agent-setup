# Architecture Review Result

## 1. Overall Architecture Assessment

- **Result: WARNING**
- The `src/` package layout and separation among CLI, installer, adapters, core instructions, and rules are appropriate.
- The package resources are packaged correctly, and the focused test suite passes (`10 passed`).
- The central ownership policy is not implemented correctly. Fundamental and CORE files are preserved on normal installation instead of always being updated, while `force=True` can overwrite user-managed files under `additional/`.
- Adapter entries installed by the current implementation contain a copy of `CORE.md`, so adapters do not act purely as references to the shared core.
- The CLI currently permits multiple Agent profiles in one command, contrary to the confirmed requirement that one profile may be selected per installation.

## 2. File-by-File Findings

| File | Status | Findings | Recommended Changes |
|---|---|---|---|
| `pyproject.toml` | PASS | Valid `src/` layout; package directory, CLI entry point, Python requirement, development dependency, and resource package data are defined. All inspected resources were present in the built wheel. | Add a test that installs the wheel in isolation and verifies resources remain accessible. |
| `MANIFEST.in` | PASS | Source Distribution includes Markdown and YAML resources under the package resources directory. | Remove the YAML pattern if YAML resources are intentionally not part of the current package, or add the expected YAML resources. |
| `src/agent_setup/cli.py` | FAIL | `--claude`, `--copilot`, and `--codex` can all be selected together. Invalid paths may escape `InstallError` handling. Output does not distinguish preserved, overwritten, and failed files. CLI and target-directory responsibilities are otherwise separated from installer logic. | Enforce exactly one Agent profile; reject an existing file used as the target path; catch and report relevant filesystem failures; classify output. |
| `src/agent_setup/installer.py` | FAIL | Adapter and destination mappings are mostly correct. `CORE.md` and `fundamental/` are installed only when missing unless `force=True`. Existing user-managed `additional/` files are overwritten when `force=True`. `--force` also globally changes adapter, core, fundamental, and additional ownership. | Replace generic `force` behavior with explicit ownership rules: adapters/core/fundamental always overwrite; additional only creates missing files and never overwrites existing files. Remove or repurpose global force semantics. |
| `src/agent_setup/resources/core/CORE.md` | PASS | Shared, Agent-neutral behavior; installed target paths use `agent_rules/`. It distinguishes fundamental and additional rules and defines task-start loading and objective updates. | Clarify that additional files are project-specific and preserve the current assumption; add plan-directory creation guidance if plans are expected. |
| `src/agent_setup/resources/adapters/codex/AGENTS.md` | WARNING | Path convention and target entry are correct. The installed file is not a pure adapter because the installer appends the complete core contents. | Keep adapter text minimal and either reference the shared core file or compose core content once during installation without duplicating concepts across source files. |
| `src/agent_setup/resources/adapters/claude/CLAUDE.md` | WARNING | Claude destination conventions and agent_rules reference are correct. The installed file also contains a duplicated copy of CORE via installer composition. | Make the installed adapter responsible for loading `agent_rules/CORE.md`; avoid embedding shared instructions. |
| `src/agent_setup/resources/adapters/copilot/copilot-instructions.md` | WARNING | Copilot destination conventions and agent_rules reference are correct. The installed file also contains a duplicated copy of CORE via installer composition. | Make the installed adapter responsible for loading `agent_rules/CORE.md`; avoid embedding shared instructions. |
| `src/agent_setup/resources/rules/fundamental/project_structure/project-level.md` | PASS | Stable engineering principles and relative `agent_rules/` references are consistent with the installed structure. | No structural change required; verify Markdown references in automated path checks. |
| `src/agent_setup/resources/rules/fundamental/project_structure/submodule-level.md` | PASS | Stable implementation conventions with no apparent target-installation dependency. | No structural change required. |
| `src/agent_setup/resources/rules/additional/task_objective.md` | WARNING | This file is suitable for project-specific content, but the installer must not overwrite it once it exists. | Add installer ownership tests and preserve the file without `--force`. |
| `src/agent_setup/resources/rules/additional/lesson_learned.md` | WARNING | This file is suitable as accumulated project knowledge, but the installer currently treats it as globally overwritable with force. | Add installer ownership tests and preserve the file without `--force`. |
| `tests/test_installer.py` | FAIL | Basic profile, existence, repeated-install, and unknown-profile coverage passes. Ownership behavior and output-content coverage are insufficient. | Add the tests listed in the Missing Test Coverage section. |
| `README.md` | WARNING | Packaging and resource concepts are documented, but the ownership policy should explicitly state overwrite/preserve behavior and that `--force` does not override user-managed additional files. | Update ownership and update-command documentation once installer behavior is corrected. |
| `README_cn.md` | WARNING | Same ownership documentation gap as the English README. | Keep translated behavior synchronized with the implementation. |

## 3. Critical Issues

1. **FAIL — Central-managed files are not updated by default**
   - `CORE.md` and all files under `fundamental/` are preserved unless the user supplies `--force`.
   - This prevents centrally maintained rules from following the latest package version.

2. **FAIL — User-managed files may be overwritten**
   - `additional/lesson_learned.md` and `additional/task_objective.md` use the same recursive copy path as fundamental rules.
   - `force=True` overwrites these files, risking project knowledge loss.

3. **FAIL — Adapter duplication**
   - Installed adapter entry files include adapter text plus the full contents of `CORE.md`.
   - This conflicts with the intended separation where adapters are entry points and CORE remains a shared source.

4. **FAIL — Profile selection contradicts requirements**
   - The CLI permits selecting multiple profiles in one invocation.
   - `profiles_requested()` will return multiple values and the installer will install all selected adapters.

5. **WARNING — Partial installation ordering**
   - Rules and CORE are installed before adapter source validation and adapter writing.
   - Missing adapter resources could leave a partial or inconsistent installation.

6. **WARNING — Filesystem errors are not fully normalized**
   - `target.mkdir()` may raise `FileExistsError` for an invalid target path and is not caught by `cli.py`, which catches only `InstallError`.

## 4. Missing Test Coverage

- Exactly one Agent profile is required; zero or multiple profiles must be rejected.
- Installing Codex, Claude, and Copilot must always produce the complete expected rule set.
- Adapter files are overwritten by subsequent installation regardless of existing content.
- Existing `CORE.md` is overwritten without affecting user-managed additional files.
- Existing fundamental files are overwritten without `--force`.
- Existing additional files are preserved without and with `--force`.
- Missing additional files are created.
- Nested directories under rules are created correctly.
- Installing profiles repeatedly is idempotent.
- Installation does not modify unrelated target-project files.
- User-managed file changes are preserved when central resources change.
- Invalid Agent profiles are rejected.
- An invalid target path, such as a regular file, produces a controlled CLI error.
- Missing packaged adapter resources cause a predictable failure without partial rule installation.
- Each installed entry and CORE reference resolves to an existing target-project file.
- Adapter source content does not duplicate CORE; instead it references it.
- Installed resources match source resources in a built wheel.

## 5. Recommended Implementation Order

1. Split rule copying by ownership:
   - adapter, CORE, fundamental: central-managed and overwrite;
   - additional: create if missing and otherwise preserve.
2. Remove `force` from rule ownership decisions and define its adapter behavior explicitly.
3. Change adapter-installed output so adapters reference `agent_rules/CORE.md` rather than embedding core content.
4. Validate exactly one Agent profile in the CLI.
5. Validate target paths and normalize filesystem errors.
6. Stage and validate resources before writing files to reduce partial installation.
7. Add ownership and installed-content tests.
8. Run wheel and installed-package verification after the ownership changes.

## 6. Questions Requiring Design Decisions

No unresolved architecture question is required to implement the confirmed requirements. The remaining policy decision is already resolved:

- `--force` must not be allowed to overwrite `agent_rules/additional/`.
- If user-visible manual override behavior is desired later, it should be a separate, explicit opt-in command rather than generic force semantics.
