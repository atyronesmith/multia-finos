"""Phase 5: Streaming agent output with EventLogger."""

from src.client import get_client
from src.streaming import run_streaming_agent


def main():
    client = get_client()

    print("Streaming agent response:\n")
    run_streaming_agent(
        client,
        "Give a brief assessment of the autonomous delivery robot market. "
        "What are the key players and challenges?",
    )


if __name__ == "__main__":
    main()
