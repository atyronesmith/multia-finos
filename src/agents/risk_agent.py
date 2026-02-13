"""Risk assessment specialist agent."""

from llama_stack_client import LlamaStackClient

from src.agents.base import create_agent, extract_score, run_agent_turn
from src.config import SPECIALIST_MODEL
from src.state import AgentEvaluation
from src.tools.risk_checklist import risk_checklist

RISK_INSTRUCTIONS = """\
You are a risk assessment specialist evaluating startup ideas.

When given a startup evaluation brief, you MUST:
1. Use the risk_checklist tool for at least 2 relevant categories (e.g. market, technology, financial, regulatory, team, operational)
2. Identify the top 3-5 risks for this specific startup
3. Rate the overall risk level
4. Suggest mitigation strategies for the top risks

Provide your analysis and end with a score in this exact format:
Score: X/10

Scoring guide (NOTE: higher score = LOWER risk, i.e. more favorable):
- 8-10: Low risk profile, risks are manageable and well-understood
- 5-7: Moderate risks that can be mitigated with planning
- 1-4: High risk profile, multiple critical risks with no clear mitigation
"""


def run_risk_evaluation(
    client: LlamaStackClient, brief: str
) -> AgentEvaluation:
    """Run risk assessment on a startup brief."""
    agent = create_agent(
        client, SPECIALIST_MODEL, RISK_INSTRUCTIONS, tools=[risk_checklist]
    )
    session = agent.create_session("risk-eval")

    prompt = (
        f"Evaluate the risks for this startup:\n\n{brief}\n\n"
        f"Use risk_checklist for at least 2 categories, then give your analysis and score."
    )
    output = run_agent_turn(agent, session, prompt)
    score = extract_score(output)

    return AgentEvaluation(
        agent_name="risk",
        score=score,
        analysis=output,
        raw_output=output,
    )
