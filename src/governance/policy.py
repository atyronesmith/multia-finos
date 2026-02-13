"""Policy engine for agent access control."""

import logging
from dataclasses import dataclass

from src.governance.registry import AgentRegistry

logger = logging.getLogger(__name__)


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str


class PolicyEngine:
    """Evaluates whether an agent can use a given tool or model."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def check_tool(self, agent_name: str, tool_name: str) -> PolicyDecision:
        record = self.registry.get(agent_name)
        if record is None:
            return PolicyDecision(
                allowed=False,
                reason=f"Agent '{agent_name}' is not registered",
            )
        if tool_name not in record.allowed_tools:
            logger.warning(
                "POLICY DENY: agent=%s tool=%s (not in %s)",
                agent_name, tool_name, record.allowed_tools,
            )
            return PolicyDecision(
                allowed=False,
                reason=(
                    f"Agent '{agent_name}' is not allowed to use tool '{tool_name}'. "
                    f"Allowed tools: {record.allowed_tools}"
                ),
            )
        return PolicyDecision(allowed=True, reason="ok")

    def check_model(self, agent_name: str, model_id: str) -> PolicyDecision:
        record = self.registry.get(agent_name)
        if record is None:
            return PolicyDecision(
                allowed=False,
                reason=f"Agent '{agent_name}' is not registered",
            )
        if model_id not in record.allowed_models:
            logger.warning(
                "POLICY DENY: agent=%s model=%s (not in %s)",
                agent_name, model_id, record.allowed_models,
            )
            return PolicyDecision(
                allowed=False,
                reason=(
                    f"Agent '{agent_name}' is not allowed to use model '{model_id}'. "
                    f"Allowed models: {record.allowed_models}"
                ),
            )
        return PolicyDecision(allowed=True, reason="ok")
