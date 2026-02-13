"""RAG setup -- register vector DB and ingest knowledge documents."""

from pathlib import Path

from llama_stack_client import LlamaStackClient

from src.config import EMBEDDING_MODEL

VECTOR_DB_ID = "startup-knowledge"
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge"


def setup_vector_db(client: LlamaStackClient) -> str:
    """Register a vector DB for startup knowledge."""
    client.vector_dbs.register(
        vector_db_id=VECTOR_DB_ID,
        embedding_model=EMBEDDING_MODEL,
    )
    return VECTOR_DB_ID


def ingest_knowledge(client: LlamaStackClient) -> int:
    """Ingest all knowledge documents into the vector DB."""
    documents = []
    for filepath in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        content = filepath.read_text()
        documents.append({
            "content": content,
            "document_id": filepath.stem,
            "metadata": {"source": filepath.name},
        })

    if documents:
        client.tool_runtime.rag_tool.insert(
            vector_db_id=VECTOR_DB_ID,
            documents=documents,
            chunk_size_in_tokens=512,
        )

    return len(documents)
