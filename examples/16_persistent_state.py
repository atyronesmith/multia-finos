"""Phase 14: Demonstrate encrypted state persistence.

Shows save/load with per-agent encryption and integrity verification.
"""

from src.security.state_manager import save_state, load_state, list_saved_evaluations
from src.state import AgentEvaluation, EvaluationState


def main():
    # Create a sample evaluation state
    state = EvaluationState(startup_idea="AI indoor farming platform")
    state.brief = "An AI-powered farming platform targeting urban restaurants."
    state.add_evaluation(AgentEvaluation(agent_name="market", score=7.0, analysis="Strong market opportunity"))
    state.add_evaluation(AgentEvaluation(agent_name="tech", score=6.5, analysis="Feasible with existing tech"))
    state.add_evaluation(AgentEvaluation(agent_name="finance", score=7.0, analysis="Solid unit economics"))
    state.add_evaluation(AgentEvaluation(agent_name="risk", score=6.0, analysis="Moderate risk profile"))
    state.final_report = "Overall positive evaluation with manageable risks."
    state.recommendation = "GO"

    eval_id = "demo-eval-001"

    # Save with encryption
    print("Saving encrypted state...")
    save_state(state, eval_id, agent_name="pipeline")
    print(f"  Saved as: {eval_id}")

    # Load it back
    print("\nLoading encrypted state...")
    loaded = load_state(eval_id, agent_name="pipeline")
    print(f"  Idea: {loaded.startup_idea}")
    print(f"  Recommendation: {loaded.recommendation}")
    print(f"  Average score: {loaded.average_score:.1f}")
    for name, ev in loaded.evaluations.items():
        print(f"    {name}: {ev.score}/10")

    # Verify isolation — different agent key can't read it
    print("\nTesting agent isolation...")
    try:
        load_state(eval_id, agent_name="different_agent")
        print("  ERROR: Should not have been able to read with different key")
    except (ValueError, Exception) as e:
        print(f"  Correctly blocked: {type(e).__name__}")

    # List saved evaluations
    print(f"\nSaved evaluations: {list_saved_evaluations()}")


if __name__ == "__main__":
    main()
