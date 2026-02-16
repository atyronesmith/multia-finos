"""Multi-shield runner — runs multiple LlamaStack shields and aggregates results."""

import logging
from dataclasses import dataclass, field

from llama_stack_client import LlamaStackClient

from src.security.shield_gate import ShieldResult, ensure_shield_registered, run_shield

logger = logging.getLogger(__name__)


@dataclass
class MultiShieldResult:
    passed: bool
    results: dict[str, ShieldResult] = field(default_factory=dict)

    @property
    def violations(self) -> dict[str, ShieldResult]:
        return {k: v for k, v in self.results.items() if not v.passed}


def run_shields(
    client: LlamaStackClient,
    text: str,
    shield_ids: list[str],
) -> MultiShieldResult:
    """Run multiple shields on the same text and aggregate results.

    All shields are run regardless of individual failures, so the caller
    gets the full picture of all violations.
    """
    results = {}
    all_passed = True

    for shield_id in shield_ids:
        ensure_shield_registered(client, shield_id)
        result = run_shield(client, text, shield_id)
        results[shield_id] = result
        if not result.passed:
            all_passed = False

    if not all_passed:
        violations = {k: v for k, v in results.items() if not v.passed}
        logger.warning(
            "Shield violations from: %s",
            list(violations.keys()),
        )

    return MultiShieldResult(passed=all_passed, results=results)


# Predefined shield sets for common use cases
INPUT_SHIELDS = ["prompt-guard"]
OUTPUT_SHIELDS = ["prompt-guard"]


def run_input_shields(client: LlamaStackClient, text: str) -> MultiShieldResult:
    """Run all input-boundary shields."""
    return run_shields(client, text, INPUT_SHIELDS)


def run_output_shields(client: LlamaStackClient, text: str) -> MultiShieldResult:
    """Run all output-boundary shields."""
    return run_shields(client, text, OUTPUT_SHIELDS)
