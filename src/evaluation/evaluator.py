"""Evaluate pipeline output using LlamaStack Scoring API (LLM-as-Judge)."""

import logging
from dataclasses import dataclass, field

from llama_stack_client import LlamaStackClient

from src.config import COORDINATOR_MODEL
from src.evaluation.scoring_setup import get_scoring_function_ids, register_scoring_functions
from src.state import EvaluationState

logger = logging.getLogger(__name__)

REVIEW_SCORE_THRESHOLD = 2.5


@dataclass
class EvalResult:
    scores: dict[str, float] = field(default_factory=dict)
    average: float = 0.0
    needs_review: bool = False
    details: dict = field(default_factory=dict)


def evaluate_report(
    client: LlamaStackClient,
    state: EvaluationState,
) -> EvalResult:
    """Score a pipeline's final report using LLM-as-Judge.

    Registers scoring functions if needed, then scores the report
    against all configured evaluation dimensions.
    """
    register_scoring_functions(client)

    fn_ids = get_scoring_function_ids()

    # Build the input row — the report text goes into generated_answer
    # which the prompt templates reference via {{generated_answer}}
    input_row = {
        "generated_answer": state.final_report,
        "input_query": state.startup_idea,
    }

    scoring_functions = {
        fn_id: {
            "type": "llm_as_judge",
            "judge_model": COORDINATOR_MODEL,
            "judge_score_regexes": [r"Score:\s*\[?(\d+)\]?"],
            "aggregation_functions": ["average"],
        }
        for fn_id in fn_ids
    }

    response = client.scoring.score(
        input_rows=[input_row],
        scoring_functions=scoring_functions,
    )

    scores = {}
    details = {}
    for fn_id, result in response.results.items():
        short_name = fn_id.removeprefix("multia-")
        if result.aggregated_results:
            avg = result.aggregated_results.get("average", {})
            score_val = avg.get("value", 0.0) if isinstance(avg, dict) else 0.0
            scores[short_name] = score_val
        details[short_name] = {
            "score_rows": result.score_rows if result.score_rows else [],
            "aggregated": result.aggregated_results,
        }

    avg_score = sum(scores.values()) / len(scores) if scores else 0.0

    return EvalResult(
        scores=scores,
        average=avg_score,
        needs_review=avg_score <= REVIEW_SCORE_THRESHOLD,
        details=details,
    )
