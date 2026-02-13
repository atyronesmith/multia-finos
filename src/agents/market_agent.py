"""Market evaluation specialist agent."""

from llama_stack_client import LlamaStackClient

from src.agents.base import create_agent, extract_score, run_agent_turn
from src.config import SPECIALIST_MODEL
from src.state import AgentEvaluation
from src.tools.market_data import search_comparables

MARKET_INSTRUCTIONS = """\
You are a market analysis specialist evaluating startup ideas.

When given a startup evaluation brief, you MUST:
1. Use the search_comparables tool to find similar companies in the relevant industry
2. Assess market size and growth potential
3. Evaluate competitive landscape based on comparable companies
4. Assess timing and market readiness

Provide your analysis and end with a score in this exact format:
Score: X/10

Scoring guide:
- 8-10: Large, growing market with few strong competitors
- 5-7: Decent market but competitive or uncertain
- 1-4: Small market, saturated, or poor timing
"""


def run_market_evaluation(
    client: LlamaStackClient, brief: str
) -> AgentEvaluation:
    """Run market evaluation on a startup brief."""
    agent = create_agent(
        client, SPECIALIST_MODEL, MARKET_INSTRUCTIONS, tools=[search_comparables]
    )
    session = agent.create_session("market-eval")

    prompt = (
        f"Evaluate the market opportunity for this startup:\n\n{brief}\n\n"
        f"Use search_comparables to find similar companies, then give your analysis and score."
    )
    output = run_agent_turn(agent, session, prompt)
    score = extract_score(output)

    return AgentEvaluation(
        agent_name="market",
        score=score,
        analysis=output,
        raw_output=output,
    )
