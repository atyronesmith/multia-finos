"""Agent registry backed by YAML configuration."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "agent-registry.yaml"


@dataclass
class AgentRecord:
    """A registered agent's metadata and permissions."""
    name: str
    role: str
    description: str
    allowed_models: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)


class AgentRegistry:
    """Registry of agents and their permissions, loaded from YAML."""

    def __init__(self, config_path: Path = CONFIG_FILE):
        self._agents: dict[str, AgentRecord] = {}
        self._load(config_path)

    def _load(self, config_path: Path):
        with open(config_path) as f:
            data = yaml.safe_load(f)
        for name, info in data.get("agents", {}).items():
            self._agents[name] = AgentRecord(
                name=name,
                role=info.get("role", ""),
                description=info.get("description", ""),
                allowed_models=info.get("allowed_models", []),
                allowed_tools=info.get("allowed_tools", []),
            )

    def get(self, agent_name: str) -> AgentRecord | None:
        return self._agents.get(agent_name)

    def list_agents(self) -> list[AgentRecord]:
        return list(self._agents.values())
