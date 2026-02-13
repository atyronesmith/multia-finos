"""Configuration for the multi-agent startup evaluator.

All settings can be overridden via environment variables or a .env file
in the project root.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Ollama server URL (can point to a remote machine)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# LlamaStack server URL (can point to a remote machine)
LLAMASTACK_URL = os.getenv("LLAMASTACK_URL", "http://localhost:8321")

# Coordinator uses larger model for better reasoning
COORDINATOR_MODEL = os.getenv("COORDINATOR_MODEL", "ollama/llama3.1:8b")

# Specialist agents use smaller model
SPECIALIST_MODEL = os.getenv("SPECIALIST_MODEL", "ollama/llama3.2:3b")

# Embedding model for RAG
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "ollama/nomic-embed-text")

# Gateway settings
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8080"))
RATE_LIMIT_CAPACITY = int(os.getenv("RATE_LIMIT_CAPACITY", "5"))
RATE_LIMIT_REFILL_RATE = float(os.getenv("RATE_LIMIT_REFILL_RATE", "0.1"))
