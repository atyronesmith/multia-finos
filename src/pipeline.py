"""Full multi-agent evaluation pipeline."""

from llama_stack_client import LlamaStackClient

from src.agents.coordinator import create_brief, synthesize_report
from src.agents.finance_agent import run_finance_evaluation
from src.agents.market_agent import run_market_evaluation
from src.agents.risk_agent import run_risk_evaluation
from src.agents.tech_agent import run_tech_evaluation
from src.state import EvaluationState


def run_pipeline(client: LlamaStackClient, startup_idea: str) -> EvaluationState:
    """Run the full multi-agent evaluation pipeline.

    Flow:
    1. Coordinator creates structured brief
    2. Four specialists evaluate in sequence (market, tech, finance, risk)
    3. Coordinator synthesizes final report
    """
    state = EvaluationState(startup_idea=startup_idea)

    # Step 1: Create brief
    print("=" * 60)
    print("[Coordinator] Creating evaluation brief...")
    print("=" * 60)
    create_brief(client, state)
    print(state.brief)

    # Step 2: Run specialist evaluations
    specialists = [
        ("Market", run_market_evaluation),
        ("Tech", run_tech_evaluation),
        ("Finance", run_finance_evaluation),
        ("Risk", run_risk_evaluation),
    ]

    for name, run_fn in specialists:
        print(f"\n{'=' * 60}")
        print(f"[{name} Agent] Evaluating...")
        print("=" * 60)
        evaluation = run_fn(client, state.brief)
        state.add_evaluation(evaluation)
        print(f"Score: {evaluation.score}/10")
        print(evaluation.analysis[:500])
        if len(evaluation.analysis) > 500:
            print("...")

    # Step 3: Synthesize final report
    print(f"\n{'=' * 60}")
    print("[Coordinator] Synthesizing final report...")
    print("=" * 60)
    synthesize_report(client, state)
    print(state.final_report)

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    for name, evaluation in state.evaluations.items():
        print(f"  {name:>10}: {evaluation.score}/10")
    print(f"  {'Average':>10}: {state.average_score:.1f}/10")
    print(f"  Recommendation: {state.recommendation}")

    return state
