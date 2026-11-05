# Agent Setup — Architecture Review Checklist

## 1. Review Objective

Review the current Agent Setup project architecture and implementation based on the confirmed requirements.

The goal is to verify whether the current implementation correctly separates CLI installation, Agent adapters, and project rules, while ensuring that file installation and update behavior follow the intended ownership model.

**Do not modify or refactor the code during this review.**

First, inspect the existing implementation, identify issues, and provide recommendations.

---

## 2. Confirmed Requirements

### 2.1 Project Support
- Currently support Python projects only.
- Keep the architecture extensible for other programming languages in the future.
- Avoid unnecessary abstraction or plugin systems at this stage.

### 2.2 Agent Installation
- Install only one Agent profile per installation command.
- Supported profiles:
  - Codex
  - Claude Code
  - GitHub Copilot

### 2.3 Rules Installation
- Always install all Rules.
- No rule-selection mechanism is required.

### 2.4 File Update Strategy

The installation files have different ownership policies:

| Resource | Ownership | Update Behavior |
|---|---|---|
| Agent adapter entry file | Central-managed | Overwrite |
| `agent_rules/CORE.md` | Central-managed | Overwrite |
| `agent_rules/fundamental/` | Central-managed | Overwrite |
| `agent_rules/additional/` | Project-specific / User-managed | Preserve existing files; do not overwrite |

Important:
- `additional/` contains project-specific settings and accumulated project knowledge.
- Existing files under `additional/` must be preserved during installation or update.
- New files under `additional/` that do not already exist may be installed.
- Core and fundamental rules must always follow the latest centrally maintained version.

### 2.5 Distribution
- Distribute the CLI through a Git repository.
- Support installation using `uv tool install`.
- CLI installation and deployment of Agent configuration into a target project must remain separate operations.

### 2.6 Target Project Structure

The expected installed structure is:

```text
target_project/
├── AGENTS.md
└── agent_rules/
    ├── CORE.md
    ├── additional/
    │   ├── lesson_learned.md
    │   └── task_objective.md
    └── fundamental/
        └── project_structure/
            ├── project-level.md
            └── submodule-level.md
```

The Agent adapter entry filename depends on the selected Agent profile.

---

## 3. Files to Inspect

### 3.1 `pyproject.toml`

**Review focus: Packaging and CLI distribution**

Check:

1. Whether the project uses a valid `src/` layout.
2. Whether the package configuration correctly includes `src/agent_setup`.
3. Whether all resource files under `resources/` are included in the built wheel.
4. Whether package-data configuration is correct.
5. Whether the CLI entry point is correctly configured for `uv tool install`.
6. Whether dependencies and Python version constraints are explicitly defined.
7. Whether the package can be installed directly from the Git repository.

Expected result:
- Installing the CLI should not depend on the current working directory or the original source repository.
- All required resource files should remain accessible after package installation.

### 3.2 `src/agent_setup/cli.py`

**Review focus: CLI behavior and user interface**

Check:

1. How Agent profiles are selected.
2. Whether only one Agent profile can be selected per command.
3. Whether the CLI supports specifying the target project directory.
4. Whether the default target directory is clearly defined.
5. Whether overwrite behavior is communicated clearly.
6. Whether invalid profiles and invalid paths are handled properly.
7. Whether the CLI output distinguishes newly created, overwritten, preserved, and failed files.
8. Whether CLI responsibilities are separated from installation logic.

Expected result:
- CLI handles argument parsing and user interaction.
- Installation and file-management logic should remain in `installer.py`.

### 3.3 `src/agent_setup/installer.py`

**Review focus: Core installation logic and file ownership**

This is the most important file to inspect.

Check:

1. Whether Agent adapter files are correctly mapped to their destination paths.
2. Whether all Rules are installed regardless of Agent profile.
3. Whether `CORE.md` and `fundamental/` are always overwritten with centrally maintained versions.
4. Whether existing files under `additional/` are preserved.
5. Whether missing files under `additional/` are installed.
6. Whether the implementation handles nested directories correctly.
7. Whether the installer avoids modifying unrelated files in the target project.
8. Whether path resolution works independently of the current working directory.
9. Whether installation is safe when executed repeatedly.
10. Whether partial installation failures are handled consistently.
11. Whether `force` is still necessary or should be redesigned given the new ownership policy.

Expected result:
- Central-managed resources are consistently updated.
- User-managed resources are preserved.
- Repeated installation should be predictable and idempotent.

### 3.4 `src/agent_setup/resources/core/CORE.md`

**Review focus: Shared Agent instructions**

Check:

1. Whether the file describes common instructions rather than Agent-specific behavior.
2. Whether all referenced paths match the actual installed directory structure.
3. Whether references use paths relative to the target project root.
4. Whether it correctly distinguishes fundamental rules from additional project-specific settings.
5. Whether it explains which rules should be read at task start and when they should be updated.
6. Whether it avoids assuming that project-specific settings are identical across projects.

Expected result:
- The installed `agent_rules/CORE.md` should be a valid and consistent entry point to the shared rules.

### 3.5 `src/agent_setup/resources/adapters/`

Inspect all three adapters:

```text
resources/adapters/
├── claude/CLAUDE.md
├── codex/AGENTS.md
└── copilot/copilot-instructions.md
```

**Review focus: Agent-specific integration**

Check:

1. Whether each adapter correctly references `agent_rules/CORE.md`.
2. Whether paths are valid relative to the target project root.
3. Whether each adapter follows the conventions of its target Agent.
4. Whether adapters avoid duplicating the common instructions in `CORE.md`.
5. Whether adapters provide a clear entry point for the Agent to load shared rules.
6. Whether the three adapters provide equivalent core behavior despite different Agent formats.

Expected result:
- Each adapter should act as an Agent-specific entry point.
- Common instructions should remain centrally maintained in `CORE.md`.

### 3.6 `src/agent_setup/resources/rules/`

Inspect:

```text
resources/rules/
├── additional/
│   ├── lesson_learned.md
│   └── task_objective.md
└── fundamental/
    └── project_structure/
        ├── project-level.md
        └── submodule-level.md
```

**Review focus: Rule organization and ownership**

Check:

1. Whether `fundamental/` contains stable, centrally maintained engineering principles.
2. Whether `additional/` contains project-specific settings or accumulated knowledge.
3. Whether the distinction between the two directories is clear.
4. Whether files in `additional/` can safely evolve independently in different projects.
5. Whether fundamental rules contain references to the correct paths.
6. Whether there are unnecessary duplicated instructions across rule files.

Expected result:
- Fundamental rules are centrally maintained.
- Additional rules are independently maintained per target project.

### 3.7 `tests/test_installer.py`

**Review focus: Test coverage and behavioral correctness**

Check whether tests cover:

1. Installation of each supported Agent profile.
2. Installation of all Rules.
3. Overwriting existing adapter files.
4. Overwriting existing `CORE.md`.
5. Overwriting existing files under `fundamental/`.
6. Preserving existing files under `additional/`.
7. Installing missing files under `additional/`.
8. Preserving unrelated files in the target project.
9. Repeated installation behavior.
10. Invalid Agent profile handling.
11. Nested directory creation.
12. Resource availability after package installation.

Expected result:
- Tests should validate actual file contents and ownership behavior, not merely check whether files exist.

---

## 4. Cross-File Consistency Checks

In addition to inspecting individual files, verify the following relationships:

### A. Resource-to-Destination Mapping

Confirm that every resource has the correct destination path:

```text
resources/adapters/codex/AGENTS.md
    → target_project/AGENTS.md

resources/core/CORE.md
    → target_project/agent_rules/CORE.md

resources/rules/fundamental/
    → target_project/agent_rules/fundamental/

resources/rules/additional/
    → target_project/agent_rules/additional/
```

Apply the corresponding adapter mapping for Claude Code and GitHub Copilot.

### B. Instruction Path Consistency

Verify that every path referenced by:
- Adapter files
- `CORE.md`
- Fundamental rules
- Additional rules

matches the actual installed directory structure.

### C. File Ownership Consistency

Verify that the implementation, documentation, and tests all follow the same ownership policy:

- Adapter: overwrite.
- CORE: overwrite.
- Fundamental: overwrite.
- Additional: preserve existing, install missing.

### D. Packaging Consistency

Verify that the resources available in the source repository are exactly the resources available to the installed CLI package.

---

## 5. Expected Review Report

Please return the review in the following format:

### 1. Overall Architecture Assessment
- Is the current architecture appropriate for the confirmed requirements?
- Are responsibilities separated correctly?
- Are there unnecessary abstractions or coupling?

### 2. File-by-File Findings

For each inspected file, report:

| File | Status | Findings | Recommended Changes |
|---|---|---|---|

Use these statuses:
- PASS
- WARNING
- FAIL

### 3. Critical Issues
List issues that may cause:
- Incorrect installation.
- User data loss.
- Invalid Agent instruction references.
- Packaging or distribution failures.

### 4. Missing Test Coverage
List tests that should be added, with the expected behavior of each test.

### 5. Recommended Implementation Order
Prioritize changes by impact and dependency.

### 6. Questions Requiring Design Decisions
Only list questions that cannot be resolved from the current implementation or confirmed requirements.

**Important: Do not modify files during this review. Report findings and recommendations first.**