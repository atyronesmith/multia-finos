"""Secure multi-agent evaluation pipeline with shield gates and validation."""

from llama_stack_client import LlamaStackClient

from src.agents.coordinator import create_brief, synthesize_report
from src.agents.finance_agent import run_finance_evaluation
from src.agents.market_agent import run_market_evaluation
from src.agents.risk_agent import run_risk_evaluation
from src.agents.tech_agent import run_tech_evaluation
from src.agents.validator import validate_output, validate_score_consistency
from src.security.shield_gate import (
    ensure_shield_registered,
    gate_agent_output,
)
from src.state import EvaluationState


class SecurityViolationError(Exception):
    """Raised when an agent output fails security checks."""

    def __init__(self, agent_name: str, reason: str):
        self.agent_name = agent_name
        self.reason = reason
        super().__init__(f"Security violation from {agent_name}: {reason}")


def run_secure_pipeline(
    client: LlamaStackClient,
    startup_idea: str,
    use_llm_validator: bool = True,
) -> EvaluationState:
    """Run the evaluation pipeline with shield gates between agent handoffs.

    Each specialist output goes through:
    1. prompt-guard shield (detects injection attempts)
    2. Heuristic score consistency check (fast, no LLM call)
    3. LLM-based semantic validation (optional, adds latency)

    If any check fails, the pipeline raises SecurityViolationError.
    """
    state = EvaluationState(startup_idea=startup_idea)

    # Register the prompt-guard shield
    ensure_shield_registered(client)

    # Step 1: Shield-check the input
    print("=" * 60)
    print("[Security] Checking input through shield gate...")
    print("=" * 60)
    input_result = gate_agent_output(client, "user-input", startup_idea)
    if not input_result.passed:
        raise SecurityViolationError("user-input", input_result.message or "Shield violation")
    print("Input passed shield check")

    # Step 2: Create brief
    print(f"\n{'=' * 60}")
    print("[Coordinator] Creating evaluation brief...")
    print("=" * 60)
    create_brief(client, state)
    print(state.brief)

    # Step 3: Run specialist evaluations with security gates
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

        # Gate 1: Shield check
        print(f"[Security] Shield gate on {name} output...")
        shield_result = gate_agent_output(client, name, evaluation.analysis)
        if not shield_result.passed:
            raise SecurityViolationError(name, shield_result.message or "Shield violation")

        # Gate 2: Heuristic score check
        heuristic_ok, heuristic_reason = validate_score_consistency(evaluation.analysis)
        if not heuristic_ok:
            print(f"[Security] Heuristic warning: {heuristic_reason}")
            raise SecurityViolationError(name, heuristic_reason)

        # Gate 3: LLM validator (optional)
        if use_llm_validator:
            print(f"[Security] LLM validation of {name} output...")
            valid, reason = validate_output(client, name, evaluation.analysis)
            if not valid:
                raise SecurityViolationError(name, reason)

        print(f"[Security] {name} output passed all checks")
        print(f"Score: {evaluation.score}/10")
        state.add_evaluation(evaluation)

    # Step 4: Synthesize final report
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
