from pathlib import PurePosixPath

ADAPTER_DESTINATIONS = {
    "claude": (PurePosixPath("CLAUDE.md"),),
    "codex": (PurePosixPath("AGENTS.md"),),
    "copilot": (PurePosixPath(".github/copilot-instructions.md"),),
}

CORE_DESTINATION = PurePosixPath(".agent_rules/CORE.md")

FUNDAMENTAL_DESTINATION = PurePosixPath(".agent_rules/fundamental")
ADDITIONAL_DESTINATION = PurePosixPath(".agent_rules/additional")

ADDITIONAL_DIRECTORIES = (
    PurePosixPath(".agent_rules/additional/plans"),
    PurePosixPath(".agent_rules/additional/lesson_learned"),
)

REQUIRED_RULE_FILES = (
    PurePosixPath("fundamental/project_structure/project-level.md"),
    PurePosixPath("fundamental/project_structure/submodule-level.md"),
    PurePosixPath("fundamental/task_objective_instruction.md"),
    PurePosixPath("fundamental/lesson_learned_instruction.md"),
    PurePosixPath("fundamental/plan_template_instruction.md"),
    PurePosixPath("additional/task_objective.md"),
)

MANAGED_LOCAL_MANIFEST = PurePosixPath(".agent_rules/manifest.json")
