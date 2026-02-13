"""Phase 1: Basic agent conversation using LlamaStack Agent API."""

from llama_stack_client import Agent

from src.client import get_client
from src.config import COORDINATOR_MODEL


def main():
    client = get_client()

    agent = Agent(
        client,
        model=COORDINATOR_MODEL,
        instructions="You are a helpful startup evaluation assistant. "
        "When given a startup idea, provide a brief initial assessment.",
    )
    session = agent.create_session("hello-session")

    response = agent.create_turn(
        session_id=session,
        messages=[
            {"role": "user", "content": "What do you think about a startup that uses AI to optimize indoor farming?"}
        ],
        stream=False,
    )

    print("Agent response:")
    print(response.output_message.content)


if __name__ == "__main__":
    main()
