"""Base helpers for creating and running agents."""

import re
from typing import Callable

from llama_stack_client import Agent, LlamaStackClient


def create_agent(
    client: LlamaStackClient,
    model: str,
    instructions: str,
    tools: list[Callable] | None = None,
) -> Agent:
    """Create a LlamaStack agent with the given config."""
    return Agent(
        client,
        model=model,
        instructions=instructions,
        tools=tools or [],
    )


def run_agent_turn(agent: Agent, session_id: str, message: str) -> str:
    """Run a single agent turn and return the text output."""
    response = agent.create_turn(
        session_id=session_id,
        messages=[{"role": "user", "content": message}],
        stream=False,
    )
    content = response.output_message.content
    if isinstance(content, list):
        return " ".join(str(c) for c in content)
    return str(content)


def extract_score(text: str) -> float:
    """Extract a numeric score (0-10) from agent output.

    Looks for patterns like 'Score: 7/10', 'score: 7', '7/10', etc.
    """
    patterns = [
        r"[Ss]core[:\s]+(\d+(?:\.\d+)?)\s*/\s*10",
        r"[Ss]core[:\s]+(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*/\s*10",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            score = float(match.group(1))
            return min(score, 10.0)
    return 5.0  # default if no score found
