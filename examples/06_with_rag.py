"""Phase 5: RAG-enhanced evaluation using knowledge documents."""

from llama_stack_client import AgentEventLogger

from src.client import get_client
from src.rag.knowledge import create_rag_agent
from src.rag.setup import ingest_knowledge, setup_vector_db


def main():
    client = get_client()

    # Setup: register vector DB and ingest knowledge docs
    print("Setting up vector DB...")
    setup_vector_db(client)

    print("Ingesting knowledge documents...")
    count = ingest_knowledge(client)
    print(f"Ingested {count} documents.\n")

    # Create RAG-enhanced agent
    agent, session = create_rag_agent(client)

    # Ask a question that benefits from the knowledge base
    print("=" * 60)
    print("RAG-enhanced evaluation query:")
    print("=" * 60)

    response = agent.create_turn(
        session_id=session,
        messages=[
            {
                "role": "user",
                "content": (
                    "I'm evaluating a B2B SaaS startup with $500K MRR, 4% monthly churn, "
                    "and a CAC of $5000 with LTV of $12000. The market is growing at 20% CAGR. "
                    "Using relevant frameworks and metrics, how would you assess this startup? "
                    "What are the key risks?"
                ),
            }
        ],
        stream=True,
    )

    for event in AgentEventLogger().log(response):
        event.print()


if __name__ == "__main__":
    main()
