# Agent Instructions

## Scope

Follow these instructions for every task performed in this workspace.

## Code Implementation

When the user asks to implement, modify, add, refactor, or generate code, consult the project structure guidelines before changing files:

- Project-level rules: `/Users/wr80340/WorkSpace/agent_setup/agnet/fundamental/project_structure/project-level.md`
- Submodule-level rules: `/Users/wr80340/WorkSpace/agent_setup/agnet/fundamental/project_structure/submodule-level.md`

Read the applicable guideline(s), then apply them to the generated code.

### Required Behavior

1. If the task affects the project root, entry point, top-level configuration, `src/`, or project-level tests, follow `project-level.md`.
2. If the task creates or modifies code inside a submodule, follow both `project-level.md` and `submodule-level.md`.
3. Preserve existing public APIs, file responsibilities, module boundaries, and project conventions.
4. Do not create files or directories that conflict with the documented project structure.
5. Add or update tests according to the project-level and submodule-level requirements.
6. Report the files changed and verify the smallest relevant test suite.

## General Rules

- Inspect the existing implementation before modifying it.
- Keep changes focused and avoid unrelated cleanup.
- Do not overwrite existing configuration or dependency declarations without authorization.
- Ask for clarification when requirements affect project structure and no existing convention resolves the decision.
- For non-code tasks, use the most relevant workspace documentation instead of applying implementation rules automatically.
