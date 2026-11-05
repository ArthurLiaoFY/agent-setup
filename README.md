src/agent_setup/resources/
├── core/
│   └── CORE.md
├── adapters/
│   ├── claude/
│   │   └── CLAUDE.md
│   ├── codex/
│   │   └── AGENTS.md
│   └── copilot/
│       └── copilot-instructions.md
└── rules/
    ├── fundamental/
    │   └── project_structure/
    │       ├── project-level.md
    │       └── submodule-level.md
    └── additional/
        ├── lesson_learned.md
        └── task_objective.md

# agent-setup

`agent-setup` is a command-line installer for shared AI coding-agent instructions. It installs packaged core rules, agent adapters, and project rules without requiring Python code to be added to the target project.

## Install the command

Choose one installation method below. The first step only installs the `agent-setup` command; it does not write instructions into your project.

### Windows

From GitHub:

```powershell
py -m pip install "git+https://github.com/ArthurLiaoFY/agent-setup.git"
```


With uv:

```powershell
cd C:\path\to\agent-setup
uv tool install .
```


If `agent-setup` is not found after installation, restart the terminal and confirm that the Python Scripts directory or uv tools directory is included in `PATH`.

### Linux / macOS

From GitHub:

```bash
python3 -m pip install "git+https://github.com/ArthurLiaoFY/agent-setup.git"
```

With uv:

```bash
cd /path/to/agent-setup
uv tool install .
```

## Install instructions into a project

After installing the command, change to the target project directory.

**Windows (PowerShell):**

```powershell
cd C:\path\to\project
agent-setup install --claude
```

**Linux / macOS:**

```bash
cd /path/to/project
agent-setup install --claude
```

This creates:

```text
/path/to/project/CLAUDE.md
```

It also creates the shared rules used by the adapter:

```text
/path/to/project/agent_rules/
├── CORE.md
├── fundamental/
└── additional/
```

For GitHub Copilot:

```bash
agent-setup install --copilot
```

This creates:

```text
/path/to/project/.github/copilot-instructions.md
```

Copilot also receives the shared rules under `/path/to/project/agent_rules/`.

For Codex:

```bash
agent-setup install --codex
```

This creates:

```text
/path/to/project/AGENTS.md
```

Codex also receives:

```text
/path/to/project/agent_rules/
├── CORE.md
├── fundamental/
└── additional/
```

To install all supported profiles:

```bash
agent-setup install --claude --copilot --codex
```

Installing multiple profiles installs their entry files and shares the same `agent_rules/` rules directory. Existing files are preserved unless `--force` is specified.

## Rebuild after updating Agent resources

Shared behavior lives in `src/agent_setup/resources/core/CORE.md`. Tool-specific entry points live under `src/agent_setup/resources/adapters/`. After changing them, run the following from the repository root:

```bash
uv run pytest -q
uv build
ls -l dist
```

The build creates a wheel and source distribution containing all resources:

```text
dist/agent_setup-<version>.whl
dist/agent_setup-<version>.tar.gz
```

To replace an existing local uv tool installation:

```bash
uv tool install --force .
```

If the project version in `pyproject.toml` is changed, rebuild with the same command:

```bash
uv build
```
