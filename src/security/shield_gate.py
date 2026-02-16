"""Shield gate — runs LlamaStack safety shields between agent handoffs."""

import logging
from dataclasses import dataclass

from llama_stack_client import LlamaStackClient

logger = logging.getLogger(__name__)

PROMPT_GUARD_SHIELD_ID = "prompt-guard"


@dataclass
class ShieldResult:
    passed: bool
    violation_level: str | None = None
    message: str | None = None


def ensure_shield_registered(client: LlamaStackClient, shield_id: str = PROMPT_GUARD_SHIELD_ID):
    """Register the prompt-guard shield if not already registered."""
    try:
        client.shields.retrieve(shield_id)
        logger.info("Shield '%s' already registered", shield_id)
    except Exception:
        logger.info("Registering shield '%s'", shield_id)
        client.shields.register(
            shield_id=shield_id,
            provider_id="llama-guard",
            provider_shield_id=shield_id,
        )


def run_shield(
    client: LlamaStackClient,
    text: str,
    shield_id: str = PROMPT_GUARD_SHIELD_ID,
) -> ShieldResult:
    """Run a safety shield on text content.

    Returns a ShieldResult indicating whether the content passed.
    """
    response = client.safety.run_shield(
        shield_id=shield_id,
        messages=[{"role": "user", "content": text}],
        params={},
    )

    if response.violation is None:
        return ShieldResult(passed=True)

    logger.warning(
        "Shield '%s' violation: level=%s message=%s",
        shield_id,
        response.violation.violation_level,
        response.violation.user_message,
    )
    return ShieldResult(
        passed=False,
        violation_level=response.violation.violation_level,
        message=response.violation.user_message,
    )


def gate_agent_output(
    client: LlamaStackClient,
    agent_name: str,
    output: str,
    shield_id: str = PROMPT_GUARD_SHIELD_ID,
) -> ShieldResult:
    """Gate an agent's output through the shield before passing to the next agent."""
    logger.info("Running shield gate on %s output", agent_name)
    result = run_shield(client, output, shield_id)
    if not result.passed:
        logger.warning(
            "GATE BLOCKED: %s output failed shield '%s': %s",
            agent_name, shield_id, result.message,
        )
    return result
