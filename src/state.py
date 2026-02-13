"""Shared state for the multi-agent evaluation pipeline."""

from dataclasses import dataclass, field


@dataclass
class AgentEvaluation:
    """Result from a single specialist agent."""
    agent_name: str
    score: float = 0.0
    analysis: str = ""
    raw_output: str = ""


@dataclass
class EvaluationState:
    """Shared state passed through the evaluation pipeline."""
    startup_idea: str
    brief: str = ""
    evaluations: dict[str, AgentEvaluation] = field(default_factory=dict)
    final_report: str = ""
    recommendation: str = ""  # GO or NO-GO

    def add_evaluation(self, eval: AgentEvaluation):
        self.evaluations[eval.agent_name] = eval

    @property
    def average_score(self) -> float:
        if not self.evaluations:
            return 0.0
        scores = [e.score for e in self.evaluations.values()]
        return sum(scores) / len(scores)
