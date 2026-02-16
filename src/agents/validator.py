"""Validation agent for semantic checks between agent handoffs.

Catches issues that safety shields can't detect: score manipulation,
format violations, and reasoning inconsistencies.
"""

import re

from llama_stack_client import LlamaStackClient

from src.agents.base import create_agent, run_agent_turn
from src.config import SPECIALIST_MODEL

VALIDATOR_INSTRUCTIONS = """\
You are a validation agent that checks specialist evaluation outputs for quality and integrity.

Given a specialist agent's evaluation output, check for:
1. SCORE MANIPULATION: Does the score match the analysis? A positive analysis with a very low score (or negative analysis with very high score) is suspicious.
2. FORMAT CONFORMANCE: Does the output contain a clear score in X/10 format?
3. REASONING QUALITY: Does the analysis provide specific, substantive points rather than vague generalities?

Respond with exactly one line:
PASS - if the output is valid
FAIL:<reason> - if there is an issue

Examples:
PASS
FAIL:Score 9/10 contradicts analysis listing multiple critical risks
FAIL:No score found in output
FAIL:Analysis contains only vague statements with no specifics
"""


def validate_output(
    client: LlamaStackClient,
    agent_name: str,
    output: str,
) -> tuple[bool, str]:
    """Validate a specialist agent's output using an LLM-based validator.

    Returns (passed, reason) tuple.
    """
    agent = create_agent(client, SPECIALIST_MODEL, VALIDATOR_INSTRUCTIONS)
    session = agent.create_session("validator")

    prompt = (
        f"Validate this output from the {agent_name} agent:\n\n"
        f"---\n{output}\n---"
    )
    result = run_agent_turn(agent, session, prompt).strip()

    if result.startswith("PASS"):
        return True, "ok"

    # Extract reason from FAIL:<reason>
    reason = result.removeprefix("FAIL:").strip() if result.startswith("FAIL") else result
    return False, reason


def validate_score_consistency(output: str) -> tuple[bool, str]:
    """Quick heuristic check that score and sentiment align.

    This runs without an LLM call — a fast sanity check before the
    full LLM validation.
    """
    # Extract score
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", output)
    if not match:
        return False, "No score in X/10 format found"

    score = float(match.group(1))
    lower = output.lower()

    # High score with strongly negative language
    negative_signals = ["critical risk", "major concern", "not viable", "highly unlikely", "fatal flaw"]
    negative_count = sum(1 for s in negative_signals if s in lower)

    if score >= 8 and negative_count >= 2:
        return False, f"Score {score}/10 but found {negative_count} strongly negative signals"

    # Low score with strongly positive language
    positive_signals = ["excellent", "outstanding", "exceptional", "no significant risk", "very strong"]
    positive_count = sum(1 for s in positive_signals if s in lower)

    if score <= 3 and positive_count >= 2:
        return False, f"Score {score}/10 but found {positive_count} strongly positive signals"

    return True, "ok"
