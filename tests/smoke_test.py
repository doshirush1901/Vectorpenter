# Basic smoke test to confirm imports and CLI wiring.
import importlib

def test_imports():
    for m in [
        "apps.cli", "apps.api", "apps.cursor_chat",
        "core.config", "core.logging", "core.schemas",
        "state.db",
        "ingest.loaders", "ingest.parsers", "ingest.chunkers", "ingest.pipeline",
        "index.embedder", "index.pinecone_client", "index.upsert",
        "rag.retriever", "rag.reranker", "rag.context_builder", "rag.generator",
        "search.typesense_client", "search.hybrid",
    ]:
        importlib.import_module(m)

if __name__ == "__main__":
    test_imports()
    print("All imports successful!")
