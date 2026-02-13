"""Phase 5: Using the OpenAI-compatible Responses API."""

from src.client import get_client
from src.config import COORDINATOR_MODEL


def get_output_text(response) -> str:
    """Extract text from a ResponseObject's output list."""
    parts = []
    for item in response.output:
        if item.type == "message":
            if isinstance(item.content, str):
                parts.append(item.content)
            elif isinstance(item.content, list):
                for block in item.content:
                    if hasattr(block, "text"):
                        parts.append(block.text)
    return "\n".join(parts)


def main():
    client = get_client()

    # Simple non-streaming example
    print("=" * 60)
    print("Responses API -- Non-streaming")
    print("=" * 60)

    response = client.responses.create(
        model=COORDINATOR_MODEL,
        input="Briefly evaluate a startup that uses AI to match freelancers with projects.",
        instructions="You are a startup evaluation expert. Be concise.",
    )
    print(get_output_text(response))

    # Multi-turn conversation using previous_response_id
    print(f"\n{'=' * 60}")
    print("Responses API -- Multi-turn follow-up")
    print("=" * 60)

    followup = client.responses.create(
        model=COORDINATOR_MODEL,
        input="What are the top 3 risks for that startup idea?",
        previous_response_id=response.id,
    )
    print(get_output_text(followup))

    # Streaming example
    print(f"\n{'=' * 60}")
    print("Responses API -- Streaming")
    print("=" * 60)

    stream = client.responses.create(
        model=COORDINATOR_MODEL,
        input="What metrics should an AI freelancer marketplace track? List the top 5.",
        instructions="You are a startup metrics expert. Be concise.",
        stream=True,
    )
    for chunk in stream:
        if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
            print(chunk.delta.text, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
