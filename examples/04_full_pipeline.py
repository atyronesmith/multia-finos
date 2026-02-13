"""Phase 4: Full multi-agent evaluation pipeline."""

from src.client import get_client
from src.pipeline import run_pipeline


def main():
    client = get_client()

    startup_idea = (
        "An AI-powered indoor farming platform that optimizes crop yields "
        "using computer vision and IoT sensors. Target market is urban "
        "restaurants wanting hyper-local produce. Expected first-year "
        "revenue of $2M with 60% gross margins."
    )

    state = run_pipeline(client, startup_idea)
    print(f"\nDone. Final recommendation: {state.recommendation}")


if __name__ == "__main__":
    main()
