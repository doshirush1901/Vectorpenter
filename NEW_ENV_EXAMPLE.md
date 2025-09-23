# New .env.example File (Voyage-Only)

Here's the **exact `.env.example`** file after the Cohere cleanup:

```env
# Vectorpenter Configuration
# Copyright (c) 2025 Machinecraft Technologies

# Required: LLM and Embeddings
OPENAI_API_KEY=

# Optional: Reranking Service
# Voyage AI is the reranker (model: rerank-2)
VOYAGE_API_KEY=

# Required: Vector Database
PINECONE_API_KEY=
PINECONE_INDEX=vectorpenter
PINECONE_CLOUD=gcp
PINECONE_REGION=us-central1
PINECONE_NAMESPACE=default

# Local State Database
DB_URL=sqlite:///./data/vectorpenter.db

# Optional: Keyword Search (for hybrid search)
TYPESENSE_API_KEY=
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=http
TYPESENSE_COLLECTION=vectorpenter_chunks

# Commercial License (required for hybrid search and reranking)
# Get your license at: https://machinecraft.tech/vectorpenter/pricing
VECTORPENTER_LICENSE_KEY=
```

## Key Changes Made:

1. **Removed `COHERE_API_KEY`** completely
2. **Updated comment** to specify "Voyage AI is the reranker (model: rerank-2)"
3. **Simplified reranking section** to only mention Voyage
4. **Maintained all other configuration** options

## Usage Examples:

### Basic (Vector Search Only)
```bash
# Only requires OpenAI + Pinecone
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
```

### With Reranking
```bash
# Add Voyage for reranking
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
VOYAGE_API_KEY=pa-...
VECTORPENTER_LICENSE_KEY=your-license
```

### Full Hybrid + Reranking
```bash
# All services for maximum capability
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
VOYAGE_API_KEY=pa-...
TYPESENSE_API_KEY=...
VECTORPENTER_LICENSE_KEY=your-license
```

This simplified configuration makes it clear that **Voyage AI is the one and only reranker** in Vectorpenter!
