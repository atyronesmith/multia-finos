"""Phase 3: Coordinator delegates to market agent, then synthesizes."""

from src.agents.coordinator import create_brief, synthesize_report
from src.agents.market_agent import run_market_evaluation
from src.client import get_client
from src.state import EvaluationState


def main():
    client = get_client()

    state = EvaluationState(
        startup_idea=(
            "An AI-powered indoor farming platform that optimizes crop yields "
            "using computer vision and IoT sensors. Target market is urban "
            "restaurants wanting hyper-local produce. Expected first-year "
            "revenue of $2M with 60% gross margins."
        )
    )

    # Step 1: Coordinator creates structured brief
    print("=" * 60)
    print("STEP 1: Coordinator creating brief...")
    print("=" * 60)
    brief = create_brief(client, state)
    print(brief)

    # Step 2: Market agent evaluates
    print("\n" + "=" * 60)
    print("STEP 2: Market agent evaluating...")
    print("=" * 60)
    market_eval = run_market_evaluation(client, state.brief)
    state.add_evaluation(market_eval)
    print(f"Market Score: {market_eval.score}/10")
    print(market_eval.analysis)

    # Step 3: Coordinator synthesizes
    print("\n" + "=" * 60)
    print("STEP 3: Coordinator synthesizing report...")
    print("=" * 60)
    report = synthesize_report(client, state)
    print(report)
    print(f"\nRecommendation: {state.recommendation}")


if __name__ == "__main__":
    main()
