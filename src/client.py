"""LlamaStack client wrapper."""

import logging

from llama_stack_client import LlamaStackClient

from src.config import LLAMASTACK_URL

# Suppress noisy httpx request logs
logging.getLogger("httpx").setLevel(logging.WARNING)


def get_client() -> LlamaStackClient:
    """Return a configured LlamaStack client."""
    return LlamaStackClient(base_url=LLAMASTACK_URL)
