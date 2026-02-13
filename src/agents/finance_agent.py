"""Financial viability specialist agent."""

from llama_stack_client import LlamaStackClient

from src.agents.base import create_agent, extract_score, run_agent_turn
from src.config import SPECIALIST_MODEL
from src.state import AgentEvaluation
from src.tools.calculator import calculator

FINANCE_INSTRUCTIONS = """\
You are a financial analysis specialist evaluating startup ideas.

When given a startup evaluation brief, you MUST:
1. Use the calculator tool to compute key financial metrics
2. Evaluate unit economics and margins
3. Assess funding requirements and runway
4. Project time to profitability

Use calculator for any arithmetic: revenue projections, burn rate, margin calculations, etc.

Provide your analysis and end with a score in this exact format:
Score: X/10

Scoring guide:
- 8-10: Strong unit economics, clear path to profitability, reasonable capital needs
- 5-7: Viable but needs significant capital or has margin pressure
- 1-4: Poor unit economics, unclear revenue model, excessive capital needs
"""


def run_finance_evaluation(
    client: LlamaStackClient, brief: str
) -> AgentEvaluation:
    """Run financial viability evaluation on a startup brief."""
    agent = create_agent(
        client, SPECIALIST_MODEL, FINANCE_INSTRUCTIONS, tools=[calculator]
    )
    session = agent.create_session("finance-eval")

    prompt = (
        f"Evaluate the financial viability of this startup:\n\n{brief}\n\n"
        f"Use calculator to compute key metrics (margins, burn rate, etc.), "
        f"then give your analysis and score."
    )
    output = run_agent_turn(agent, session, prompt)
    score = extract_score(output)

    return AgentEvaluation(
        agent_name="finance",
        score=score,
        analysis=output,
        raw_output=output,
    )
