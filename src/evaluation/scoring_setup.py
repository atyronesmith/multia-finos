"""Register scoring functions with LlamaStack for LLM-as-Judge evaluation."""

import logging
from pathlib import Path

import yaml

from llama_stack_client import LlamaStackClient

from src.config import COORDINATOR_MODEL

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "scoring-functions.yaml"


def _load_scoring_config(path: Path = CONFIG_FILE) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def register_scoring_functions(client: LlamaStackClient, config_path: Path = CONFIG_FILE):
    """Register all scoring functions from config with LlamaStack."""
    config = _load_scoring_config(config_path)

    for fn_id, fn_config in config.get("scoring_functions", {}).items():
        scoring_fn_id = f"multia-{fn_id}"
        try:
            client.scoring_functions.register(
                scoring_fn_id=scoring_fn_id,
                description=fn_config["description"],
                return_type={"type": "number"},
                provider_id="llm-as-judge",
                params={
                    "type": "llm_as_judge",
                    "judge_model": COORDINATOR_MODEL,
                    "prompt_template": fn_config["prompt_template"],
                    "judge_score_regexes": [r"Score:\s*\[?(\d+)\]?"],
                    "aggregation_functions": ["average"],
                },
            )
            logger.info("Registered scoring function: %s", scoring_fn_id)
        except Exception as e:
            logger.warning("Could not register %s: %s", scoring_fn_id, e)


def get_scoring_function_ids(config_path: Path = CONFIG_FILE) -> list[str]:
    """Return the list of scoring function IDs from config."""
    config = _load_scoring_config(config_path)
    return [f"multia-{fn_id}" for fn_id in config.get("scoring_functions", {})]
