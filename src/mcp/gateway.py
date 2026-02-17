"""MCP Gateway — registry check + governance enforcement for MCP tool access."""

import logging
from dataclasses import dataclass

from llama_stack_client import LlamaStackClient

from src.governance.tool_governance import ToolDecision, ToolGovernance
from src.mcp.registry import MCPRegistry

logger = logging.getLogger(__name__)


@dataclass
class MCPAccessDecision:
    allowed: bool
    server_name: str
    tool_name: str
    server_registered: bool
    governance_decision: ToolDecision | None
    reason: str


class MCPGateway:
    """Gateway that checks MCP registry status and delegates to ToolGovernance."""

    def __init__(
        self,
        client: LlamaStackClient | None,
        registry: MCPRegistry,
        governance: ToolGovernance,
    ):
        self.client = client
        self.registry = registry
        self.governance = governance

    def check_access(self, server_name: str, tool_name: str) -> MCPAccessDecision:
        """Check if an MCP tool call is allowed (registry + governance)."""
        server = self.registry.get(server_name)

        if server is None:
            return MCPAccessDecision(
                allowed=False,
                server_name=server_name,
                tool_name=tool_name,
                server_registered=False,
                governance_decision=None,
                reason=f"Server '{server_name}' not found in MCP registry",
            )

        if server.status != "active":
            return MCPAccessDecision(
                allowed=False,
                server_name=server_name,
                tool_name=tool_name,
                server_registered=True,
                governance_decision=None,
                reason=f"Server '{server_name}' is inactive",
            )

        # Check governance using mcp:: prefix
        gov_key = f"mcp::{tool_name}"
        gov_decision = self.governance.check(gov_key)

        return MCPAccessDecision(
            allowed=gov_decision.allowed,
            server_name=server_name,
            tool_name=tool_name,
            server_registered=True,
            governance_decision=gov_decision,
            reason=gov_decision.reason,
        )

    def register_server(self, server_name: str) -> bool:
        """Register an MCP server's tools with LlamaStack. Requires a running server."""
        if self.client is None:
            logger.warning("No LlamaStack client — skipping register_server")
            return False

        server = self.registry.get(server_name)
        if server is None:
            logger.error("Server '%s' not in registry", server_name)
            return False

        try:
            toolgroup_id = f"mcp::{server_name}"
            self.client.toolgroups.register(
                toolgroup_id=toolgroup_id,
                provider_id="model-context-protocol",
                mcp_endpoint={"uri": server.endpoint},
            )
            logger.info("Registered MCP toolgroup: %s", toolgroup_id)
            return True
        except Exception as e:
            logger.error("Failed to register MCP server '%s': %s", server_name, e)
            return False

    def discover_tools(self, server_name: str) -> list[dict]:
        """List tools available from a registered MCP server via LlamaStack."""
        if self.client is None:
            logger.warning("No LlamaStack client — skipping discover_tools")
            return []

        try:
            toolgroup_id = f"mcp::{server_name}"
            tools = self.client.tools.list(toolgroup_id=toolgroup_id)
            return [{"identifier": t.identifier, "description": t.description} for t in tools]
        except Exception as e:
            logger.error("Failed to discover tools for '%s': %s", server_name, e)
            return []

    def unregister_server(self, server_name: str) -> bool:
        """Unregister an MCP server's tools from LlamaStack."""
        if self.client is None:
            logger.warning("No LlamaStack client — skipping unregister_server")
            return False

        try:
            toolgroup_id = f"mcp::{server_name}"
            self.client.toolgroups.unregister(toolgroup_id=toolgroup_id)
            logger.info("Unregistered MCP toolgroup: %s", toolgroup_id)
            return True
        except Exception as e:
            logger.error("Failed to unregister MCP server '%s': %s", server_name, e)
            return False
