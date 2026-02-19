"""Shared fixtures for the multia test suite."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.governance.registry import AgentRegistry
from src.governance.policy import PolicyEngine
from src.governance.tool_governance import ToolGovernance
from src.governance.tool_validator import ToolValidator
from src.governance.audit import AuditTrail
from src.mcp.registry import MCPRegistry
from src.mcp.gateway import MCPGateway
from src.state import AgentEvaluation, EvaluationState

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


@pytest.fixture
def agent_registry():
    return AgentRegistry(CONFIG_DIR / "agent-registry.yaml")


@pytest.fixture
def policy_engine(agent_registry):
    return PolicyEngine(agent_registry)


@pytest.fixture
def tool_governance():
    return ToolGovernance(CONFIG_DIR / "tool-policies.yaml")


@pytest.fixture
def tool_validator():
    return ToolValidator(CONFIG_DIR / "tool-policies.yaml")


@pytest.fixture
def mcp_registry():
    return MCPRegistry(CONFIG_DIR / "mcp-registry.yaml")


@pytest.fixture
def mcp_gateway(mcp_registry, tool_governance):
    return MCPGateway(client=None, registry=mcp_registry, governance=tool_governance)


@pytest.fixture
def sample_state():
    state = EvaluationState(startup_idea="AI-powered indoor farming optimizer")
    state.brief = "Evaluate an AI platform for indoor farming."
    state.add_evaluation(AgentEvaluation(agent_name="market", score=7.0, analysis="Strong market"))
    state.add_evaluation(AgentEvaluation(agent_name="tech", score=6.0, analysis="Moderate complexity"))
    state.recommendation = "GO"
    state.final_report = "Overall positive evaluation."
    return state


@pytest.fixture
def sample_audit():
    audit = AuditTrail(evaluation_id="test-001", startup_idea="Test startup")
    audit.started_at = datetime.now(timezone.utc).isoformat()
    audit.record_input_validation(passed=True, detail="length ok")
    audit.record_shield("prompt-guard", "market", passed=True)
    audit.record_policy("market", "search_comparables", allowed=True, reason="ok")
    audit.record_tool_governance("calculator", tier="approved", allowed=True)
    audit.record_evaluation("market", score=7.5)
    audit.record_sanitization(redaction_count=1, types=["email"])
    audit.record_output_filter(passed=True)
    audit.record_encryption("test-001", action="save")
    audit.record_scoring("quality", score=4.0)
    audit.record_mcp_access("market-sentiment", "market_sentiment", allowed=True)
    return audit
