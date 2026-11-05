# Agent Setup — Adapter Loading Validation & Implementation Preparation

## Objective

Based on the previous Architecture Review, validate the proposed changes before implementation.

The confirmed file ownership policy is:

| Resource | Behavior |
|---|---|
| Agent Adapter | Always overwrite |
| `agent_rules/CORE.md` | Always overwrite |
| `agent_rules/fundamental/` | Always overwrite |
| `agent_rules/additional/` | Install missing files only; preserve existing files |

Do not modify files yet. First validate the technical design and provide an implementation plan.

---

## Task 1. Validate Agent Adapter Loading Mechanisms

Inspect the current adapters:

```text
resources/adapters/
├── claude/CLAUDE.md
├── codex/AGENTS.md
└── copilot/copilot-instructions.md
```

Determine how each Agent should load or reference:

```text
agent_rules/CORE.md
```

For each Agent, investigate:

1. Does the Agent support native file inclusion/import syntax?
2. If so, what is the correct syntax?
3. Does the referenced path resolve relative to the project root or another location?
4. If native inclusion is unavailable or unsuitable, can the Adapter explicitly instruct the Agent to read the file?
5. Will the mechanism work when the project is opened from a different working directory?
6. Are there any restrictions on referenced Markdown files or nested instruction files?

Evaluate these three Agents independently:

- Codex
- Claude Code
- GitHub Copilot

Do not assume that all three Agents use the same reference mechanism.

### Expected Result

Provide a comparison table:

| Agent | Supported Mechanism | Recommended Syntax | Path Resolution | Concerns |
|---|---|---|---|---|

Then provide the recommended Adapter content for each Agent.

The goal is to keep Adapter files minimal while ensuring that the shared CORE instructions are actually loaded.

---

## Task 2. Define Installer Ownership Logic

Prepare the installation behavior based on the confirmed ownership policy.

Expected behavior:

```text
Adapter:
    Always overwrite

CORE:
    Always overwrite

Fundamental:
    Always overwrite existing files
    Install missing files

Additional:
    Preserve existing files
    Install missing files
    Never overwrite existing files
```

Additional requirements:

- `--force` must not bypass the ownership policy.
- Repeated installation must be predictable.
- Unrelated project files must remain untouched.
- Nested directories must be handled correctly.

Explain whether `--force` should be removed entirely or retained for a narrowly defined purpose.

---

## Task 3. Validate CLI Profile Selection

The CLI must install exactly one Agent profile per command.

Inspect the existing argument parser and recommend the simplest implementation.

Expected behavior:

- Zero profiles: reject.
- Exactly one profile: accept.
- Multiple profiles: reject.

Do not introduce unnecessary profile abstractions.

---

## Task 4. Review Installation Failure Handling

Inspect the current installation sequence.

Determine how to prevent partial installation when:

- An adapter resource is missing.
- A rule resource is missing.
- The target path is invalid.
- A filesystem permission error occurs.

Recommend a simple and maintainable approach.

Avoid introducing a complex transaction or rollback framework unless necessary.

---

## Task 5. Prepare the Implementation Plan

Based on Tasks 1–4, provide:

1. Files that need modification.
2. Specific changes required in each file.
3. Tests that need to be added or modified.
4. Any dependency or packaging changes.
5. Recommended implementation order.

### Important Constraints

- Do not modify files yet.
- Do not redesign the existing directory structure.
- Keep the current installed target structure unchanged.
- Do not introduce unnecessary abstractions.
- Preserve the confirmed ownership policy.
- Prefer the smallest changes that satisfy the requirements.

Return the technical findings and implementation plan for review before proceeding with code changes.