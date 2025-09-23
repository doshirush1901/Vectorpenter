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
        "gcp.docai", "gcp.vertex",
    ]:
        importlib.import_module(m)

def test_gcp_modules_safe_import():
    """Test that GCP modules import safely even without credentials"""
    from core.config import settings
    
    # Test DocAI module
    from gcp.docai import is_docai_available, test_docai_connection
    
    # Should not crash even without credentials
    docai_available = is_docai_available()
    print(f"DocAI available: {docai_available}")
    
    # Connection test should fail gracefully without credentials
    if not docai_available:
        connection_ok = test_docai_connection()
        assert connection_ok is False  # Should fail gracefully
    
    # Test Vertex module
    from gcp.vertex import is_vertex_available, test_vertex_connection
    
    # Should not crash even without credentials
    vertex_available = is_vertex_available()
    print(f"Vertex AI available: {vertex_available}")
    
    # Connection test should fail gracefully without credentials
    if not vertex_available:
        connection_ok = test_vertex_connection()
        assert connection_ok is False  # Should fail gracefully
    
    print("✅ GCP modules import safely without credentials")

if __name__ == "__main__":
    test_imports()
    print("All imports successful!")
    
    test_gcp_modules_safe_import()
    print("All tests completed!")
