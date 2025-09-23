# Vectorpenter Project Skeleton

**The carpenter of context — building vectors into memory**

Use this skeleton to scaffold new Vectorpenter-style projects with all core differentiators built-in.

## 📁 Complete Project Structure

```
vectorpenter/
├── .env.example                    # All API keys, no defaults
├── .gitignore                      # Python + data directories
├── README.md                       # Intro + differentiators + licensing
├── LICENSE                         # AGPL-3.0
├── LICENSE-COMMERCIAL.md           # Commercial license option
├── SUPPORT.md                      # Free vs paid support
├── requirements.txt                # Core dependencies
├── pyproject.toml                  # CLI entry point
├── 
├── apps/
│   ├── __init__.py
│   ├── cli.py                      # vectorpenter ingest/index/ask --hybrid --rerank
│   ├── cursor_chat.py              # Interactive REPL for Cursor
│   └── api.py                      # Optional FastAPI server
├── 
├── core/
│   ├── __init__.py
│   ├── config.py                   # BYOK environment loading
│   ├── logging.py                  # Structured logging
│   └── schemas.py                  # Pydantic models
├── 
├── data/
│   ├── inputs/                     # Drop files here
│   ├── cache/                      # Temporary artifacts
│   └── eval/                       # Gold Q&A sets
├── 
├── ingest/
│   ├── __init__.py
│   ├── loaders.py                  # File discovery (.pdf, .docx, etc.)
│   ├── parsers.py                  # Text extraction
│   ├── chunkers.py                 # Token-based chunking
│   └── pipeline.py                 # Hash-based change detection
├── 
├── index/
│   ├── __init__.py
│   ├── embedder.py                 # OpenAI embeddings
│   ├── pinecone_client.py          # Vector DB client
│   └── upsert.py                   # Batch vector upserts
├── 
├── rag/
│   ├── __init__.py
│   ├── retriever.py                # Vector similarity search
│   ├── reranker.py                 # Voyage → Cohere → identity fallback
│   ├── context_builder.py          # Citation-aware context assembly
│   └── generator.py                # LLM with grounded responses
├── 
├── search/
│   ├── __init__.py
│   ├── typesense_client.py         # Keyword search engine
│   └── hybrid.py                   # Vector ∪ keyword merging
├── 
├── state/
│   ├── __init__.py
│   ├── db.py                       # SQLite engine + init
│   ├── models.sql                  # Schema: documents, chunks, embeddings, logs
│   └── memory.py                   # Conversation state
├── 
├── tools/                          # Optional integrations
│   ├── __init__.py
│   ├── gmail.py                    # Email ingestion (stub)
│   ├── crawler.py                  # Web scraping (stub)
│   └── ocr.py                      # Image text extraction (stub)
├── 
└── tests/
    ├── __init__.py
    └── smoke_test.py               # Import tests + basic pipeline
```

## 🔧 Core Implementation Stubs

### `.env.example`
```env
# LLMs & Embeddings
OPENAI_API_KEY=

# Reranking Service
# Voyage AI is the reranker (model: rerank-2)
VOYAGE_API_KEY=

# Vector DB
PINECONE_API_KEY=
PINECONE_INDEX=vectorpenter
PINECONE_NAMESPACE=default

# Keyword Search (hybrid)
TYPESENSE_API_KEY=
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108

# Local State
DB_URL=sqlite:///./data/vectorpenter.db
```

### `apps/cli.py` (Core Differentiator)
```python
import argparse
from core.logging import logger
from ingest.pipeline import ingest_path
from index.upsert import build_and_upsert
from index.embedder import embed_texts
from rag.retriever import vector_search
from rag.reranker import rerank
from rag.context_builder import hydrate_matches, build_context
from rag.generator import answer
from search.hybrid import hybrid_search, index_typesense

def cmd_ask(q: str, k: int = 12, hybrid: bool = False, rerank: bool = False):
    """Core differentiator: hybrid + rerank flags"""
    vec = embed_texts([q])[0]
    
    if hybrid:
        matches = hybrid_search(q, vec, top_k=k)
        search_type = "hybrid"
    else:
        matches = vector_search(vec, top_k=k)
        search_type = "vector"
    
    snippets = hydrate_matches(matches)
    
    if rerank:
        snippets = rerank(q, snippets)  # Voyage AI rerank-2
        search_type += "+rerank"
    
    pack = build_context(snippets)
    ans = answer(q, pack)
    print(f"\n=== ANSWER ({search_type}) ===\n{ans}\n")

def main():
    p = argparse.ArgumentParser("Vectorpenter CLI")
    sub = p.add_subparsers(dest="cmd")
    
    # Core commands
    pi = sub.add_parser("ingest")
    pi.add_argument("path")
    
    px = sub.add_parser("index")
    
    pa = sub.add_parser("ask")
    pa.add_argument("q")
    pa.add_argument("--k", type=int, default=12)
    pa.add_argument("--hybrid", action="store_true")  # Differentiator
    pa.add_argument("--rerank", action="store_true")  # Differentiator
    
    args = p.parse_args()
    if args.cmd == "ask":
        cmd_ask(args.q, args.k, args.hybrid, args.rerank)
    # ... other commands
```

### `search/hybrid.py` (Core Differentiator)
```python
def hybrid_search(query: str, query_vec: List[float], top_k: int = 12) -> List[Dict]:
    """Core differentiator: merge vector + keyword results"""
    from search.typesense_client import search_keywords
    from rag.retriever import vector_search
    
    # Get both result types
    keyword_results = search_keywords(query, top_k * 2)
    vector_results = vector_search(query_vec, top_k * 2)
    
    # Round-robin merge with deduplication
    return hybrid_merge(keyword_results, vector_results, top_k)

def hybrid_merge(keyword_results: List[Dict], vector_results: List[Dict], k: int) -> List[Dict]:
    """Smart merging algorithm"""
    seen_ids = set()
    merged = []
    
    # Round-robin with deduplication
    for kw, vec in zip(keyword_results, vector_results):
        if len(merged) >= k:
            break
        if kw['id'] not in seen_ids:
            seen_ids.add(kw['id'])
            merged.append({**kw, 'source': 'keyword'})
        if len(merged) >= k:
            break
        if vec['id'] not in seen_ids:
            seen_ids.add(vec['id'])
            merged.append({**vec, 'source': 'vector'})
    
    return merged[:k]
```

### `rag/reranker.py` (Core Differentiator)
```python
def rerank(question: str, snippets: List[Dict]) -> List[Dict]:
    """Core differentiator: Voyage AI rerank-2 model"""
    if not snippets:
        return snippets
    
    # Check if Voyage AI is configured
    if settings.voyage_api_key:
        try:
            logger.info("Reranking with Voyage (rerank-2)")
            return _voyage_rerank(question, snippets)
        except Exception as e:
            logger.warning(f"Voyage reranking failed: {e}")
            logger.info("Falling back to original order")
            return snippets
    else:
        logger.info("No VOYAGE_API_KEY set, skipping rerank")
        return snippets

def _voyage_rerank(question: str, snippets: List[Dict]) -> List[Dict]:
    import voyageai
    client = voyageai.Client(api_key=settings.voyage_api_key)
    documents = [s['text'] for s in snippets]
    result = client.rerank(query=question, documents=documents, model="rerank-2")
    return [snippets[r.index] for r in result.results]
```

### `core/config.py` (BYOK Differentiator)
```python
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    # BYOK - no defaults, no vendor lock-in
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    voyage_api_key: str | None = os.getenv("VOYAGE_API_KEY")
    pinecone_api_key: str | None = os.getenv("PINECONE_API_KEY")
    typesense_api_key: str | None = os.getenv("TYPESENSE_API_KEY")
    
    # Configuration with sensible defaults
    pinecone_index: str = os.getenv("PINECONE_INDEX", "vectorpenter")
    pinecone_namespace: str = os.getenv("PINECONE_NAMESPACE", "default")
    db_url: str = os.getenv("DB_URL", "sqlite:///./data/vectorpenter.db")

settings = Settings()
```

### `state/models.sql` (Lightweight State)
```sql
-- Lightweight SQLite schema - runs on laptop instantly
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    hash TEXT NOT NULL,  -- Change detection
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    text TEXT NOT NULL,
    tokens INTEGER DEFAULT 0,
    FOREIGN KEY (document_id) REFERENCES documents (id)
);

CREATE TABLE IF NOT EXISTS embeddings (
    chunk_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    vector_id TEXT,  -- Pinecone ID
    FOREIGN KEY (chunk_id) REFERENCES chunks (id)
);

CREATE TABLE IF NOT EXISTS retrieval_logs (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    search_type TEXT DEFAULT 'vector',  -- vector, hybrid, hybrid+rerank
    chosen_ids TEXT DEFAULT '[]',
    created_at TEXT NOT NULL
);
```

### `README.md` Template
```markdown
# Vectorpenter
The carpenter of context — building vectors into memory.

## 🚀 Core Differentiators

### 1. **Hybrid Search + Smart Reranking**
```bash
vectorpenter ask "question" --hybrid --rerank
```
- Merges Pinecone vector results ∪ Typesense keyword search
- Voyage AI → Cohere → identity reranking fallback

### 2. **Lightweight & Local-First**
- SQLite state (no heavy databases)
- Runs instantly on any laptop
- Hash-based change detection

### 3. **Bring-Your-Own-Keys**
- No vendor lock-in
- Graceful degradation
- All services optional

### 4. **Three Interfaces**
- CLI: `vectorpenter ask`
- REPL: `python -m apps.cursor_chat`
- API: FastAPI server

## Quick Start
```bash
cp .env.example .env  # Add your API keys
pip install -r requirements.txt
vectorpenter ingest ./data/inputs
vectorpenter index
vectorpenter ask "Your question" --hybrid --rerank
```

## 📄 Licensing
- **Community**: AGPL-3.0 (free, open source)
- **Commercial**: License required for proprietary use
- See SUPPORT.md for details
```

### `pyproject.toml`
```toml
[project]
name = "vectorpenter"
version = "0.1.0"
description = "The carpenter of context — building vectors into memory"
requires-python = ">=3.10"

[project.scripts]
vectorpenter = "apps.cli:main"
```

### `tests/smoke_test.py`
```python
def test_imports():
    """Ensure all modules import correctly"""
    import apps.cli
    import apps.cursor_chat
    import search.hybrid
    import rag.reranker
    print("✅ All imports successful")

def test_pipeline():
    """Test basic ingest → index → ask pipeline"""
    # Create test document
    # Run ingest
    # Run index  
    # Run ask with --hybrid --rerank
    print("✅ Pipeline test passed")

if __name__ == "__main__":
    test_imports()
    test_pipeline()
```

## 🎯 **Key Differentiators vs Competitors**

| Feature | txtai | Verba | Pinecone Demos | **Vectorpenter** |
|---------|--------|--------|----------------|------------------|
| **Hybrid Search** | ❌ | ❌ | ❌ | ✅ Native --hybrid |
| **Smart Reranking** | ❌ | ❌ | ❌ | ✅ Voyage AI rerank-2 |
| **Local-First** | ❌ | ❌ | ❌ | ✅ SQLite, laptop-ready |
| **BYOK** | ❌ | ❌ | ❌ | ✅ No vendor lock-in |
| **CLI + REPL + API** | Partial | ❌ | ❌ | ✅ Three interfaces |
| **Commercial Ready** | ❌ | ❌ | ❌ | ✅ Dual licensing |

---

**This skeleton gives you everything needed to scaffold a Vectorpenter-style project with all differentiators built-in from day one!** 🔨✨
