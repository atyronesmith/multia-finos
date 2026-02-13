"""Technical feasibility specialist agent."""

from llama_stack_client import LlamaStackClient

from src.agents.base import create_agent, extract_score, run_agent_turn
from src.config import SPECIALIST_MODEL
from src.state import AgentEvaluation
from src.tools.complexity import complexity_estimator

TECH_INSTRUCTIONS = """\
You are a technical feasibility specialist evaluating startup ideas.

When given a startup evaluation brief, you MUST:
1. Use the complexity_estimator tool to assess the technical components
2. Evaluate whether the technology is proven or experimental
3. Assess the engineering team size needed
4. Identify key technical risks and dependencies

Provide your analysis and end with a score in this exact format:
Score: X/10

Scoring guide:
- 8-10: Well-understood tech stack, small team can build it, low risk
- 5-7: Some technical challenges but feasible with good team
- 1-4: Unproven technology, massive engineering effort, high risk
"""


def run_tech_evaluation(
    client: LlamaStackClient, brief: str
) -> AgentEvaluation:
    """Run technical feasibility evaluation on a startup brief."""
    agent = create_agent(
        client, SPECIALIST_MODEL, TECH_INSTRUCTIONS, tools=[complexity_estimator]
    )
    session = agent.create_session("tech-eval")

    prompt = (
        f"Evaluate the technical feasibility of this startup:\n\n{brief}\n\n"
        f"Use complexity_estimator to assess the components, then give your analysis and score."
    )
    output = run_agent_turn(agent, session, prompt)
    score = extract_score(output)

    return AgentEvaluation(
        agent_name="tech",
        score=score,
        analysis=output,
        raw_output=output,
    )
