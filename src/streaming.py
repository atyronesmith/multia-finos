"""Streaming output helpers using AgentEventLogger."""

from llama_stack_client import AgentEventLogger, LlamaStackClient

from src.agents.base import create_agent
from src.config import COORDINATOR_MODEL


def run_streaming_agent(client: LlamaStackClient, message: str) -> str:
    """Run an agent with streaming output, printing tokens as they arrive."""
    agent = create_agent(
        client,
        COORDINATOR_MODEL,
        "You are a startup evaluation assistant. Provide detailed, thoughtful analysis.",
    )
    session = agent.create_session("streaming-session")

    response = agent.create_turn(
        session_id=session,
        messages=[{"role": "user", "content": message}],
        stream=True,
    )

    full_output = []
    for event in AgentEventLogger().log(response):
        event.print()
        if hasattr(event, "content") and event.content:
            full_output.append(event.content)

    return "".join(full_output)
