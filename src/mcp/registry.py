"""MCP server registry backed by YAML configuration."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "mcp-registry.yaml"


@dataclass
class MCPServerRecord:
    """A registered MCP server's metadata."""
    name: str
    description: str
    endpoint: str
    status: str  # active, inactive
    tools_provided: list[str] = field(default_factory=list)
    health_check: str = ""
    metadata: dict = field(default_factory=dict)


class MCPRegistry:
    """Registry of MCP servers, loaded from YAML."""

    def __init__(self, config_path: Path = CONFIG_FILE):
        self._servers: dict[str, MCPServerRecord] = {}
        self._load(config_path)

    def _load(self, config_path: Path):
        with open(config_path) as f:
            data = yaml.safe_load(f)
        for name, info in data.get("servers", {}).items():
            self._servers[name] = MCPServerRecord(
                name=name,
                description=info.get("description", ""),
                endpoint=info.get("endpoint", ""),
                status=info.get("status", "inactive"),
                tools_provided=info.get("tools_provided", []),
                health_check=info.get("health_check", ""),
                metadata=info.get("metadata", {}),
            )

    def get(self, server_name: str) -> MCPServerRecord | None:
        return self._servers.get(server_name)

    def list_servers(self) -> list[MCPServerRecord]:
        return list(self._servers.values())

    def list_active(self) -> list[MCPServerRecord]:
        return [s for s in self._servers.values() if s.status == "active"]

    def is_registered(self, server_name: str) -> bool:
        return server_name in self._servers
