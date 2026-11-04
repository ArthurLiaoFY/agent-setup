from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist


root = Path(__file__).parent
source = root / "AGENT.md"
templates = (
    root / "src/agent_setup/templates/claude/CLAUDE.md",
    root / "src/agent_setup/templates/copilot/AGENT.md",
    root / "src/agent_setup/templates/codex/AGENTS.md",
)


def sync_templates() -> None:
    for destination in templates:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())


class BuildPy(_build_py):
    def run(self) -> None:
        sync_templates()
        super().run()


class Sdist(_sdist):
    def run(self) -> None:
        sync_templates()
        super().run()


setup(cmdclass={"build_py": BuildPy, "sdist": Sdist})
