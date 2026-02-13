"""Coordinator agent -- decomposes ideas and synthesizes final reports."""

from llama_stack_client import LlamaStackClient

from src.agents.base import create_agent, run_agent_turn
from src.config import COORDINATOR_MODEL
from src.state import EvaluationState

COORDINATOR_INSTRUCTIONS = """\
You are the lead coordinator of a startup evaluation team. You have two responsibilities:

1. BRIEF CREATION: When given a startup idea, create a structured evaluation brief with:
   - One-line summary
   - Target market and customer
   - Value proposition
   - Revenue model
   - Key assumptions to validate

2. SYNTHESIS: When given evaluation results from specialist agents, synthesize a final report with:
   - Overall score (average of specialist scores, out of 10)
   - Key strengths (top 2-3)
   - Key risks (top 2-3)
   - Final recommendation: GO or NO-GO
   - One paragraph reasoning

Keep responses concise and structured.
"""


def create_brief(client: LlamaStackClient, state: EvaluationState) -> str:
    """Have the coordinator create a structured brief from the startup idea."""
    agent = create_agent(client, COORDINATOR_MODEL, COORDINATOR_INSTRUCTIONS)
    session = agent.create_session("coordinator-brief")

    prompt = (
        f"Create a structured evaluation brief for this startup idea:\n\n"
        f"{state.startup_idea}\n\n"
        f"Format it clearly with sections: Summary, Target Market, "
        f"Value Proposition, Revenue Model, Key Assumptions."
    )
    brief = run_agent_turn(agent, session, prompt)
    state.brief = brief
    return brief


def synthesize_report(client: LlamaStackClient, state: EvaluationState) -> str:
    """Have the coordinator synthesize specialist evaluations into a final report."""
    agent = create_agent(client, COORDINATOR_MODEL, COORDINATOR_INSTRUCTIONS)
    session = agent.create_session("coordinator-synthesis")

    eval_summary = ""
    for name, evaluation in state.evaluations.items():
        eval_summary += f"\n--- {name.upper()} EVALUATION ---\n"
        eval_summary += f"Score: {evaluation.score}/10\n"
        eval_summary += f"Analysis: {evaluation.analysis}\n"

    prompt = (
        f"Here is the startup brief:\n{state.brief}\n\n"
        f"Here are the specialist evaluations:\n{eval_summary}\n\n"
        f"Synthesize a final evaluation report. Include:\n"
        f"- Overall score (out of 10)\n"
        f"- Top strengths\n"
        f"- Top risks\n"
        f"- Final recommendation: GO or NO-GO\n"
        f"- Brief reasoning"
    )
    report = run_agent_turn(agent, session, prompt)
    state.final_report = report
    state.recommendation = "GO" if state.average_score >= 6.0 else "NO-GO"
    return report
