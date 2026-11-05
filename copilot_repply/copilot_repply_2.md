# Agent Setup — Adapter Loading Validation & Implementation Plan

## Task 1. Validate Agent Adapter Loading Mechanisms

### Comparison

| Agent | Supported Mechanism | Recommended Syntax | Path Resolution | Concerns |
|---|---|---|---|---|
| Codex | Native discovery of root `AGENTS.md`; no supported Markdown include/import syntax for this entry file. | In `AGENTS.md`: `Read and follow \`agent_rules/CORE.md\` at the start of every task.` | Project-root relative instructions; Codex discovers the root file and walks toward the current working directory. | Instruction files have context-size limits; nested reference loading depends on the Agent reading the referenced file rather than native expansion. |
| Claude Code | Native `@path/to/file` imports in `CLAUDE.md`. | `@agent_rules/CORE.md` | Relative imports resolve from the file containing the import, not the process working directory. | `CLAUDE.md` imports increase context cost and imported files may recursively import up to four hops. External-file imports require approval. This use remains inside the repository. |
| GitHub Copilot | Repository instructions are automatically loaded from `.github/copilot-instructions.md`; no native file-import syntax is documented for repository instruction Markdown. | Natural-language entry: `Read and follow \`agent_rules/CORE.md\` before implementation.` | Root-relative repository instructions; GitHub Copilot can access repository files as context when the Agent has repository file access. | This is an instruction to load a file, not a guarantee that every Copilot surface eagerly reads it. Avoid unsupported Markdown include syntax. |

Official references reviewed:

- [Codex AGENTS.md guidance](https://developers.openai.com/codex/guides/agents-md/)
- [Claude Code memory and imports](https://code.claude.com/docs/en/memory)
- [GitHub Copilot repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)

### Recommended adapter content

#### Codex: `AGENTS.md`

```markdown
# Agent Instructions

Read and follow `agent_rules/CORE.md` at the start of every task.
Before starting implementation, inspect all files referenced by CORE that are relevant
to the current task. Keep `agent_rules/additional/` project-specific.
```

Codex discovers root `AGENTS.md` independently of the launch working directory when the
project is opened as a repository. It does not need a native nested Markdown include
to use this adapter.

#### Claude Code: `CLAUDE.md`

```markdown
# Claude Code Instructions

@agent_rules/CORE.md
```

Because `CLAUDE.md` is installed at the target repository root, `@agent_rules/CORE.md`
resolves relative to that adapter. This is the preferred native mechanism and should not
embed CORE into the adapter content.

#### GitHub Copilot: `.github/copilot-instructions.md`

```markdown
# GitHub Copilot Instructions

Read and follow `agent_rules/CORE.md` at the start of every task.
Before starting implementation, inspect all files referenced by CORE that are relevant
to the current task. Keep `agent_rules/additional/` project-specific.
```

GitHub Copilot automatically loads repository-wide instructions from this location. No
native Markdown inclusion syntax should be used in this adapter.

### Working-directory findings

- Codex searches from a Git repository root toward the current working directory, subject
  to its documented project-instruction discovery rules.
- Claude imports resolve relative to the containing `CLAUDE.md`, not the shell working
  directory.
- GitHub Copilot repository instructions are repository-root based and should use
  repository-relative paths.

All three recommended adapters therefore remain stable even when an Agent is launched
from a nested working directory.

---

## Task 2. Define Installer Ownership Logic

### Ownership matrix

| Destination | Policy | Existing content | Missing content |
|---|---|---|---|
| Adapter entry | Always overwrite | Replace with packaged adapter | Create |
| `agent_rules/CORE.md` | Always overwrite | Replace with packaged CORE | Create |
| `agent_rules/fundamental/**` | Always overwrite | Replace with packaged version | Create |
| `agent_rules/additional/**` | User-managed | Preserve unchanged | Create from package once |

### Recommended installer structure

1. Validate the selected profile, adapter resource, CORE resource, and rule resources
   before writing anything.
2. Copy the selected adapter to its destination, always overwriting.
3. Write `agent_rules/CORE.md`, always overwriting.
4. Recursively copy all resources under `rules/fundamental/` to
   `agent_rules/fundamental/`, always overwriting existing files.
5. Recursively copy resources under `rules/additional/` to
   `agent_rules/additional/`; create missing files and skip existing files.
6. Do not copy other source paths or modify unrelated files.

`--force` should be removed for this public ownership model. It has no valid purpose after
the ownership policy is made deterministic:

- Central files are overwritten automatically.
- Project-specific additional files are never overwritten.

If backward compatibility requires retaining the flag temporarily, it should be accepted
for CLI compatibility but ignored. It must never weaken the additional-file preserve rule.
Do not interpret `force=True` in installer internals.

### Repeated installation

Without `--force`, a repeated installation should:

- Report adapter, CORE, and fundamental writes as updates.
- Create missing additional files.
- Preserve and report existing additional files as preserved.
- Leave unrelated project files untouched.

---

## Task 3. Validate CLI Profile Selection

The smallest implementation is to keep the existing boolean flags and validate their
combination after argument parsing.

Recommended validation:

```python
profiles = [
    profile
    for enabled, profile in (
        (args.claude, "claude"),
        (args.copilot, "copilot"),
        (args.codex, "codex"),
    )
    if enabled
]

if len(profiles) == 0:
    parser.error("choose exactly one of --claude, --copilot, or --codex")
if len(profiles) > 1:
    parser.error("choose exactly one Agent profile")

profile = profiles[0]
```

There is no need to add new abstractions or mutually exclusive argument groups at this
stage; validating the three booleans is sufficient and keeps CLI behavior explicit.

---

## Task 4. Review Installation Failure Handling

### Recommended failure model

1. Resolve and validate the target before resource validation or writes:
   - `target` must exist as a directory or be creatable as a directory;
   - a regular file at the requested target path must fail.
2. Convert packaged traversable resources into a small in-memory or temporary staging
   plan before writing.
3. Verify that every required adapter, CORE, and rule resource exists and is a file.
4. Verify writeability for the target directories. This does not guarantee permissions
   atomically, but catches common permission failures before meaningful writes.
5. Write central resources first, then additional resources, while preserving ownership.
6. Catch `OSError` in the CLI boundary and convert it to `InstallError`, with the exact
   failing path where possible.

Avoid full filesystem transactions or rollback unless the installer grows beyond simple
Markdown resources. The minimum maintainable safeguards are:

- Complete resource validation before writes.
- No writes to unrelated files.
- Destination containment checks for nested rule paths.
- Clear `InstallError` messages and non-zero CLI exit status.
- No `force` bypass for additional files.

If a write fails halfway through, central files may be partially updated. The first
implementation should report the failing path and stop; a manifest/version system can
provide transactional or resumable behavior later.

---

## Task 5. Implementation Plan

### 1. Files requiring modification

- `src/agent_setup/installer.py`
- `src/agent_setup/cli.py`
- `src/agent_setup/resources/adapters/codex/AGENTS.md`
- `src/agent_setup/resources/adapters/claude/CLAUDE.md`
- `src/agent_setup/resources/adapters/copilot/copilot-instructions.md`
- `tests/test_installer.py`
- Add focused CLI tests, such as `tests/test_cli.py`
- `README.md`
- `README_cn.md`

### 2. Required changes

#### Installer

- Add separate central and additional copy paths.
- Remove the recursive `force` argument from ownership decisions.
- Always overwrite adapters, CORE, and fundamental resources.
- Preserve additional resources when present.
- Create missing nested additional directories and files.
- Validate packaged adapter and rule resources before writing.
- Return explicit created, overwritten, and preserved file classifications if CLI output
  is expanded.

#### CLI

- Enforce exactly one profile per invocation.
- Resolve and validate the target directory.
- Keep argument parsing and output separate from installation logic.
- Catch both installer and filesystem failures consistently.
- Clarify that adapter/CORE/fundamental updates are central-managed and additional files
  are preserved.
- Remove `--force`, or retain it only as a compatibility flag ignored by installer logic.

#### Adapters

- Codex: explicit instruction to read `agent_rules/CORE.md`.
- Claude: native `@agent_rules/CORE.md` import at repository root.
- Copilot: explicit instruction to read `agent_rules/CORE.md`; do not use unsupported
  Markdown imports.

### 3. Tests

1. Exactly one profile is accepted; zero and multiple profiles fail.
2. All three adapters map to their documented destinations.
3. Adapter changes overwrite existing adapter files.
4. CORE changes overwrite existing CORE files.
5. Fundamental changes overwrite existing fundamental files and create missing nested files.
6. Additional existing files are preserved even when central resources and package
   versions change.
7. Missing additional files are created once.
8. Repeated installation is predictable and does not touch unrelated files.
9. `--force` cannot overwrite additional files; preferably test that removal eliminates
   the ambiguous behavior.
10. Invalid target files and inaccessible target directories produce controlled errors.
11. Missing adapter and missing rule resources fail before writes.
12. Installed adapter reference syntax resolves to `agent_rules/CORE.md`.
13. Package-data tests verify adapters, CORE, fundamental, and additional resources from
    a built wheel.

### 4. Dependencies and packaging

- No new runtime dependency is required.
- Keep Python 3.12 constraint, `setuptools`, package-data configuration, and CLI entry
  point unless compatibility requirements change.
- Add packaging verification to the test suite; no manifest format change is needed for
  the current Markdown resources.

### 5. Recommended implementation order

1. Implement ownership-aware installer copying.
2. Update the three adapters for their verified loading mechanisms.
3. Enforce exactly one CLI profile.
4. Validate targets and normalize filesystem errors.
5. Add ownership, CLI, partial-failure, and nested-directory tests.
6. Update English and Chinese documentation.
7. Build and install the wheel in an isolated temporary project to verify packaged
   resources and runtime behavior.

---

## Decision Summary

- Claude Code has the clearest native file-loading mechanism through `@path`.
- Codex and GitHub Copilot should use a minimal explicit instruction to read the
  project-relative CORE file.
- The ownership policy can be implemented without manifests or transactions.
- Generic `--force` should be removed or ignored; it must not bypass user-managed
  `additional/` preservation.
- No directory redesign, new dependencies, or new runtime abstraction is required.
