"""Phase 2: Agent with custom tool calling."""

from llama_stack_client import Agent

from src.client import get_client
from src.config import COORDINATOR_MODEL
from src.tools.calculator import calculator
from src.tools.market_data import search_comparables


def main():
    client = get_client()

    agent = Agent(
        client,
        model=COORDINATOR_MODEL,
        instructions=(
            "You are a startup evaluation assistant with access to tools. "
            "When evaluating a startup idea:\n"
            "1. Use search_comparables to find similar companies in the industry\n"
            "2. Use calculator to compute relevant financial metrics\n"
            "3. Summarize your findings with data to support your assessment\n"
            "Always use your tools before giving an assessment."
        ),
        tools=[calculator, search_comparables],
    )
    session = agent.create_session("tools-session")

    response = agent.create_turn(
        session_id=session,
        messages=[
            {
                "role": "user",
                "content": (
                    "Evaluate this startup idea: An AI-powered indoor farming platform "
                    "that optimizes crop yields using computer vision and IoT sensors. "
                    "Target market is urban restaurants wanting hyper-local produce. "
                    "Expected first-year revenue of $2M with 60% gross margins."
                ),
            }
        ],
        stream=False,
    )

    # Print tool call steps
    for step in response.steps:
        if hasattr(step, "tool_calls") and step.tool_calls:
            for tc in step.tool_calls:
                print(f"[Tool Call] {tc.tool_name}({tc.arguments})")
        if hasattr(step, "tool_responses") and step.tool_responses:
            for tr in step.tool_responses:
                print(f"[Tool Result] {tr.content[:200]}...")

    print("\nAgent response:")
    print(response.output_message.content)


if __name__ == "__main__":
    main()
