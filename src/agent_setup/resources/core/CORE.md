# Agent Instructions

## Scope

Follow these instructions for every task performed in this workspace.

## Instruction Loading Verification

When the user asks for instruction verification,
report the exact marker: AGENT_SETUP_CORE_LOADED.

## Code Implementation

When the user asks to implement, modify, add, refactor, or generate code, consult the project structure guidelines before changing files:

- Project-level rules: `agent_rules/fundamental/project_structure/project-level.md`
- Submodule-level rules: `agent_rules/fundamental/project_structure/submodule-level.md`

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

## Task Objective

- Read `agent_rules/additional/task_objective.md` at the start of each task to understand the project problem this repository is intended to solve.
- Keep `agent_rules/additional/task_objective.md` accurate when implementation changes affect the project's purpose or scope.
- When the task objective is updated, explain the update briefly to the user.
- `agent_rules/additional/task_objective.md` starts empty and should be updated progressively as facts are established.
- Do not modify the task objective based on assumptions or unverified interpretations.
- Update it only when the project scope or objective is explicitly established or validated.

## Plan History

- Store all plans created in plan mode under `agent_rules/additional/plans/`.
- Use one descriptive Markdown file per plan.
- At the start of a task, review existing plan files for relevant prior decisions and conflicts.
- When plans conflict, explicitly identify the conflict to the user before proceeding and prefer the most recent validated plan.

## Lesson Learned

- Review `agent_rules/additional/lesson_learned.md` before repeating a workflow.
- Record lessons as bullet points only, describing the mistake, the correct approach, and the future prevention rule.
- Add a lesson only when it resulted from observable experience rather than speculation.
- Keep this file concise and update it when the execution approach materially improves.
