# Vectorpenter
The carpenter of context — building vectors into memory.

## What is it?
Vectorpenter is a **local AI Fabric** you can pull into Cursor. Drop files into `data/inputs/`, run one CLI command to build a **vectorized memory** (Pinecone), and chat with your data through Cursor or the optional local API.

- **Local-first**: runs on your machine, no server required.
- **Bring-your-own-keys**: OpenAI / Pinecone / (optional) Voyage, Typesense.
- **RAG-native**: robust chunking, embeddings, retrieval, citations.
- **Company-friendly**: each teammate sets their own keys & namespace.

## Quick start
```bash
# 1) Clone
# git clone https://github.com/<you>/vectorpenter.git && cd vectorpenter

# 2) Setup env
cp env.example .env
# fill your keys in .env (OPENAI, PINECONE, etc.)

# 3) Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4) Put files
mkdir -p data/inputs && cp /path/to/docs/* data/inputs/

# 5) Build index
python -m apps.cli ingest ./data/inputs
python -m apps.cli index

# 6) Ask questions
python -m apps.cli ask "Summarize FRIMO x Machinecraft actions since July 2025" --k 12

# (Optional) Run local API
uvicorn apps.api:app --reload
# Then POST /query {"q":"…"}
```

## Folder hygiene
- `data/inputs/` is your only required folder. Vectorpenter will hash-detect changes and re-embed only modified files.
- `data/cache/` stores transient artifacts. Safe to delete.
- `data/eval/` holds evaluation sets (gold Q&A) for RAG quality.

## Environment (.env)
```
# LLMs
OPENAI_API_KEY=
# Optional rerank
VOYAGE_API_KEY=

# Vector DB (Pinecone)
PINECONE_API_KEY=
PINECONE_INDEX=vectorpenter
PINECONE_CLOUD=gcp
PINECONE_REGION=us-central1
PINECONE_NAMESPACE=default

# State DB
DB_URL=sqlite:///./data/vectorpenter.db

# Optional keyword search (Typesense or Postgres FTS)
TYPESENSE_API_KEY=
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
```

## Design decisions
- **Pinecone** as the default vector index for ease of team usage; **SQLite** for local state (Postgres ready).
- **RAG prompt** enforces citations and rejects hallucinations: if context is insufficient, it tells you what's missing.
- **Hybrid-ready**: optional keyword + vector + rerank for high precision.

## Safety & privacy
- Your files stay local. Only text chunks/embeddings go to Pinecone.
- All API keys are user-provided; nothing is hardcoded.

## License
MIT. See LICENSE.
