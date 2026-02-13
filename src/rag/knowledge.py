"""RAG-enhanced agent for startup evaluation."""

from llama_stack_client import Agent, LlamaStackClient

from src.config import COORDINATOR_MODEL
from src.rag.setup import VECTOR_DB_ID


def create_rag_agent(client: LlamaStackClient) -> tuple[Agent, str]:
    """Create an agent with RAG knowledge retrieval."""
    agent = Agent(
        client,
        model=COORDINATOR_MODEL,
        instructions=(
            "You are a startup evaluation expert with access to a knowledge base "
            "of startup metrics, market sizing frameworks, and risk analysis methods. "
            "Use the knowledge_search tool to retrieve relevant information before "
            "answering questions about startup evaluation."
        ),
        tools=[
            {
                "name": "builtin::rag/knowledge_search",
                "args": {"vector_db_ids": [VECTOR_DB_ID]},
            }
        ],
    )
    session = agent.create_session("rag-session")
    return agent, session
