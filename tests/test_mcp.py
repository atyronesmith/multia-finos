"""Tests for Phase 16: MCP registry, MCP gateway."""

import pytest


# ── MCPRegistry ──────────────────────────────────────────────────────────

class TestMCPRegistry:
    def test_loads_servers(self, mcp_registry):
        servers = mcp_registry.list_servers()
        assert len(servers) == 3

    def test_get_known_server(self, mcp_registry):
        server = mcp_registry.get("market-sentiment")
        assert server is not None
        assert server.status == "active"

    def test_get_unknown_server(self, mcp_registry):
        assert mcp_registry.get("nonexistent") is None

    def test_list_active(self, mcp_registry):
        active = mcp_registry.list_active()
        assert len(active) == 2
        names = {s.name for s in active}
        assert "market-sentiment" in names
        assert "funding-data" in names

    def test_is_registered(self, mcp_registry):
        assert mcp_registry.is_registered("market-sentiment") is True
        assert mcp_registry.is_registered("ghost-server") is False


# ── MCPGateway ───────────────────────────────────────────────────────────

class TestMCPGateway:
    def test_access_allowed(self, mcp_gateway):
        decision = mcp_gateway.check_access("market-sentiment", "market_sentiment")
        assert decision.allowed is True
        assert decision.server_registered is True

    def test_denied_unregistered_server(self, mcp_gateway):
        decision = mcp_gateway.check_access("ghost-server", "some_tool")
        assert decision.allowed is False
        assert decision.server_registered is False

    def test_denied_inactive_server(self, mcp_gateway):
        decision = mcp_gateway.check_access("external-shell", "shell_command")
        assert decision.allowed is False
        assert "inactive" in decision.reason

    def test_denied_blocked_tool(self, mcp_gateway):
        # Simulate an active server providing a blocked tool
        # external-shell is inactive, so test via a direct governance check instead
        decision = mcp_gateway.check_access("market-sentiment", "shell_command")
        # shell_command via mcp:: prefix should be blocked
        assert decision.allowed is False

    def test_register_without_client(self, mcp_gateway):
        result = mcp_gateway.register_server("market-sentiment")
        assert result is False
