"""Tool governance layer with three-tier classification."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "tool-policies.yaml"


@dataclass
class ToolDecision:
    allowed: bool
    tier: str  # approved, conditional, blocked, unknown
    reason: str
    logged: bool = False


class ToolGovernance:
    """Three-tier tool governance: approved, conditional, blocked."""

    def __init__(self, config_path: Path = CONFIG_FILE):
        self._approved: set[str] = set()
        self._conditional: set[str] = set()
        self._blocked: set[str] = set()
        self._load(config_path)

    def _load(self, config_path: Path):
        with open(config_path) as f:
            data = yaml.safe_load(f)
        tiers = data.get("tiers", {})
        self._approved = set(tiers.get("approved", []))
        self._conditional = set(tiers.get("conditional", []))
        self._blocked = set(tiers.get("blocked", []))

    def check(self, tool_name: str) -> ToolDecision:
        """Check whether a tool is allowed under governance policy."""
        if tool_name in self._blocked:
            logger.warning("TOOL BLOCKED: %s", tool_name)
            return ToolDecision(
                allowed=False,
                tier="blocked",
                reason=f"Tool '{tool_name}' is blocked by policy",
            )

        if tool_name in self._conditional:
            logger.info("TOOL CONDITIONAL: %s (logged)", tool_name)
            return ToolDecision(
                allowed=True,
                tier="conditional",
                reason=f"Tool '{tool_name}' is conditionally allowed (logged)",
                logged=True,
            )

        if tool_name in self._approved:
            return ToolDecision(
                allowed=True,
                tier="approved",
                reason="ok",
            )

        # Unknown tools are denied by default
        logger.warning("TOOL UNKNOWN: %s (not in any tier)", tool_name)
        return ToolDecision(
            allowed=False,
            tier="unknown",
            reason=f"Tool '{tool_name}' is not registered in governance policy",
        )

    def list_tools(self) -> dict[str, list[str]]:
        return {
            "approved": sorted(self._approved),
            "conditional": sorted(self._conditional),
            "blocked": sorted(self._blocked),
        }
