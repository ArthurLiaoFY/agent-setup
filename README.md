├── agent/
│   ├── AGENT.md
│   │
│   ├── fundamental/
│   │   ├── environment.md
│   │   ├── project-startup.md
│   │   ├── project-structures.md
│   │   ├── dependency-management.md
│   │   ├── coding-conventions.md
│   │   └── verification.md
│   │
│   └── additional/
│       ├── tooling/
│       │   ├── git.md
│       │   ├── linting.md
│       │   └── testing.md
│       │
│       ├── skills/
│       │   ├── code-search/
│       │   │   └── SKILL.md
│       │   └── code-review/
│       │       └── SKILL.md
│       │
│       └── integrations/
│           ├── mcp.md
│           └── external-tools.md
│
└── ...

# agent-setup

`agent-setup` is a command-line installer for shared AI coding-agent instructions. It installs packaged instruction templates without requiring Python code to be added to the target project.

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

For GitHub Copilot:

```bash
agent-setup install --copilot
```

This creates:

```text
/path/to/project/.github/copilot-instructions.md
```

For Codex:

```bash
agent-setup install --codex
```

This creates:

```text
/path/to/project/AGENTS.md
```

To install all supported profiles:

```bash
agent-setup install --claude --copilot --codex
```

## Rebuild after updating AGENT.md

`AGENT.md` at the repository root is the canonical instruction source. After changing it, run the following from the repository root:

```bash
uv run pytest -q
uv build
ls -l dist
```

The build synchronizes `AGENT.md` into the Claude, GitHub Copilot, and Codex templates, then creates a wheel and source distribution:

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
