"""Tests for Phase 8, 11: Agent registry, policy engine, tool governance, tool validator, score consistency."""

import pytest

from src.agents.validator import validate_score_consistency


# ── AgentRegistry ────────────────────────────────────────────────────────

class TestAgentRegistry:
    def test_loads_all_agents(self, agent_registry):
        agents = agent_registry.list_agents()
        assert len(agents) == 5

    def test_get_known_agent(self, agent_registry):
        record = agent_registry.get("market")
        assert record is not None
        assert record.role == "specialist"

    def test_get_unknown_agent(self, agent_registry):
        assert agent_registry.get("nonexistent") is None

    def test_coordinator_has_no_tools(self, agent_registry):
        record = agent_registry.get("coordinator")
        assert record.allowed_tools == []

    def test_market_includes_mcp_tools(self, agent_registry):
        record = agent_registry.get("market")
        assert "mcp::market_sentiment" in record.allowed_tools


# ── PolicyEngine ─────────────────────────────────────────────────────────

class TestPolicyEngine:
    def test_allows_registered_tool(self, policy_engine):
        decision = policy_engine.check_tool("market", "search_comparables")
        assert decision.allowed is True

    def test_denies_unregistered_tool(self, policy_engine):
        decision = policy_engine.check_tool("market", "calculator")
        assert decision.allowed is False

    def test_denies_unknown_agent(self, policy_engine):
        decision = policy_engine.check_tool("ghost", "calculator")
        assert decision.allowed is False
        assert "not registered" in decision.reason

    def test_allows_correct_model(self, policy_engine):
        decision = policy_engine.check_model("coordinator", "ollama/llama3.1:8b")
        assert decision.allowed is True

    def test_denies_wrong_model(self, policy_engine):
        decision = policy_engine.check_model("coordinator", "gpt-4")
        assert decision.allowed is False


# ── ToolGovernance ───────────────────────────────────────────────────────

class TestToolGovernance:
    def test_approved_tool(self, tool_governance):
        decision = tool_governance.check("calculator")
        assert decision.allowed is True
        assert decision.tier == "approved"

    def test_conditional_tool(self, tool_governance):
        decision = tool_governance.check("web_search")
        assert decision.allowed is True
        assert decision.tier == "conditional"
        assert decision.logged is True

    def test_blocked_tool(self, tool_governance):
        decision = tool_governance.check("shell_exec")
        assert decision.allowed is False
        assert decision.tier == "blocked"

    def test_unknown_tool(self, tool_governance):
        decision = tool_governance.check("random_tool_xyz")
        assert decision.allowed is False
        assert decision.tier == "unknown"

    def test_list_tools(self, tool_governance):
        tools = tool_governance.list_tools()
        assert "approved" in tools
        assert "calculator" in tools["approved"]
        assert "blocked" in tools
        assert "shell_exec" in tools["blocked"]


# ── ToolValidator ────────────────────────────────────────────────────────

class TestToolValidator:
    def test_valid_params(self, tool_validator):
        result = tool_validator.validate("calculator", {"operation": "add", "x": 1, "y": 2})
        assert result.valid is True
        assert result.errors == []

    def test_missing_required(self, tool_validator):
        result = tool_validator.validate("calculator", {"operation": "add", "x": 1})
        assert result.valid is False
        assert any("Missing required" in e for e in result.errors)

    def test_invalid_value(self, tool_validator):
        result = tool_validator.validate("calculator", {"operation": "modulo", "x": 1, "y": 2})
        assert result.valid is False
        assert any("not in allowed values" in e for e in result.errors)

    def test_unknown_tool_passes(self, tool_validator):
        result = tool_validator.validate("some_new_tool", {"anything": "goes"})
        assert result.valid is True


# ── Score Consistency ────────────────────────────────────────────────────

class TestScoreConsistency:
    def test_valid_output(self):
        output = "Good market opportunity. Score: 7/10"
        passed, reason = validate_score_consistency(output)
        assert passed is True

    def test_high_score_negative_text(self):
        output = (
            "This idea has a critical risk and major concern. "
            "The market is not viable. Score: 9/10"
        )
        passed, reason = validate_score_consistency(output)
        assert passed is False
        assert "negative signals" in reason

    def test_missing_score(self):
        output = "Great idea with no numeric rating."
        passed, reason = validate_score_consistency(output)
        assert passed is False
        assert "No score" in reason
