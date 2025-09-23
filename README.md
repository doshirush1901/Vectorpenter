# Vectorpenter
The carpenter of context — building vectors into memory.

## What is it?
Vectorpenter is a **local AI Fabric** you can pull into Cursor. Drop files into `data/inputs/`, run one CLI command to build a **vectorized memory** (Pinecone + Typesense), and chat with your data through Cursor or the optional local API.

- **Local-first**: runs on your machine, no server required.
- **Hybrid search**: combines vector similarity (Pinecone) + keyword matching (Typesense).
- **Smart reranking**: Voyage AI rerank-2 model for better results.
- **Bring-your-own-keys**: OpenAI / Pinecone / (optional) Voyage, Typesense.
- **RAG-native**: robust chunking, embeddings, retrieval, citations.
- **Company-friendly**: each teammate sets their own keys & namespace.

## Quick start
```bash
# 1) Clone
# git clone https://github.com/doshirush1901/Vectorpenter.git && cd vectorpenter

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
python -m apps.cli ask "Summarize FRIMO x Machinecraft actions since July 2025" --hybrid --rerank

# (Optional) Run local API
uvicorn apps.api:app --reload
# Then POST /query {"q":"…", "hybrid": true, "rerank": true}

# Cursor REPL
python -m apps.cursor_chat
```

## Folder hygiene
- `data/inputs/` is your only required folder. Vectorpenter will hash-detect changes and re-embed only modified files.
- `data/cache/` stores transient artifacts. Safe to delete.
- `data/eval/` holds evaluation sets (gold Q&A) for RAG quality.

## Environment (.env)
```
# LLMs & Embeddings
OPENAI_API_KEY=

# Reranking Service (optional)
# Voyage AI is the reranker (model: rerank-2)
VOYAGE_API_KEY=

# Vector DB (Pinecone)
PINECONE_API_KEY=
PINECONE_INDEX=vectorpenter
PINECONE_CLOUD=gcp
PINECONE_REGION=us-central1
PINECONE_NAMESPACE=default

# State DB
DB_URL=sqlite:///./data/vectorpenter.db

# Keyword Search (Typesense - optional for hybrid search)
TYPESENSE_API_KEY=
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=http
TYPESENSE_COLLECTION=vectorpenter_chunks
```

## CLI Usage

### Basic Commands
```bash
# Ingest documents
vectorpenter ingest ./data/inputs

# Build indexes (both Pinecone and Typesense)
vectorpenter index

# Simple vector search
vectorpenter ask "What are the key features?"

# Hybrid search (vector + keyword)
vectorpenter ask "What are the key features?" --hybrid

# With reranking for better results
vectorpenter ask "What are the key features?" --hybrid --rerank --k 20
```

### Cursor Chat REPL
For the best experience in Cursor IDE:
```bash
python -m apps.cursor_chat
```
- Interactive Q&A with your documents
- Automatic hybrid search and reranking (when available)
- Citation tracking with source references
- Built-in help and configuration commands

### API Usage
```bash
# Start the API server
uvicorn apps.api:app --reload

# Query with curl
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"q": "What are the main topics?", "hybrid": true, "rerank": true, "k": 12}'
```

## GCP Auto-Upgrade for PDFs

Vectorpenter intelligently handles PDF parsing with automatic upgrade to Google Cloud Document AI:

### **Default Behavior**
- **Local parsers first**: Uses `pypdf`, `python-docx`, `python-pptx`, `pandas` for all documents
- **Smart auto-upgrade**: For PDFs with poor local extraction (scanned/low-text), automatically tries Document AI
- **Cost-conscious**: Only uses cloud services when local parsing insufficient

### **Auto-Upgrade Heuristics**
Vectorpenter automatically upgrades to Document AI when:
- **Low text extraction**: Local parser extracts <500 characters
- **High empty page ratio**: >60% of pages have no extractable text
- **Manual override**: `USE_GOOGLE_DOC_AI=true` forces DocAI for all PDFs

### **Configuration**
```env
# GCP / Document AI (optional)
GOOGLE_APPLICATION_CREDENTIALS=./creds/service-account.json
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us
USE_GOOGLE_DOC_AI=false  # Manual override
DOC_AI_PROCESSOR_ID=projects/your-project/locations/us/processors/your-processor-id

# Vertex Chat (optional) - embeddings stay OpenAI
USE_VERTEX_CHAT=false
VERTEX_CHAT_MODEL=gemini-1.5-pro
```

### **GCP Setup Steps**
1. **Enable APIs**: Document AI API, Vertex AI API (if using chat)
2. **Create Processor**: Document OCR processor in Document AI console
3. **Service Account**: Create with roles:
   - `Document AI API User`
   - `Vertex AI User` (if using chat)
4. **Download Credentials**: Save service account JSON to `./creds/service-account.json`

### **Privacy & Cost Notes**
- **Document AI**: Sends file bytes to GCP, charges per page (~$0.015/page)
- **Vertex Chat**: Optional alternative to OpenAI for responses
- **Embeddings**: Always use OpenAI (no GCP embedding dependency)

## Google Search Grounding

**Optional fallback when local retrieval is weak**

### **How It Works**
- **Automatic**: Triggers when local similarity <0.18 or insufficient results
- **Google Custom Search**: Searches web for additional context
- **Cost-conscious**: Only when local knowledge insufficient

### **Configuration**
```env
USE_GOOGLE_GROUNDING=false
GOOGLE_SEARCH_API_KEY=your-api-key
GOOGLE_SEARCH_CX=your-search-engine-id
MAX_GOOGLE_RESULTS=3
GROUNDING_SIM_THRESHOLD=0.18
```

### **Setup**
1. Create [Google Custom Search Engine](https://cse.google.com/)
2. Get API key from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
3. Configure search engine ID (CX) in environment

**⚠️ Privacy Note**: When grounding is enabled, queries may be sent to Google Search. External links in responses should be verified before sharing.

## Translation & Archival

### **Auto-Translation**
- **Before processing**: Translates non-English documents to English
- **Smart detection**: Only translates documents >300 characters
- **Cost-aware**: Skips short documents to save money

### **GCS Archival**
- **Audit trail**: Stores raw, translated, and redacted versions
- **Timestamped**: Each artifact tagged with processing time
- **Organized**: Uses configurable bucket and prefix structure

### **Configuration**
```env
# Translation
USE_TRANSLATION=false
TRANSLATE_TARGET_LANG=en
TRANSLATE_MIN_CHARS=300

# Archival
USE_GCS=false
GCS_BUCKET=gs://your-bucket-name
GCS_PREFIX=vp/ingest
```

## Data Flow

```
Parse (DocAI/local) → [optional Translate→EN] → Chunk → [optional DLP] → Store (SQLite) → Embeddings (OpenAI)
                                                                       ↘ [optional GCS archival]
Ask: Vector/Hybrid(+rerank) → [fallback Google grounding] → Context Pack → LLM Answer (OpenAI/Vertex chat)
```

## Design decisions
- **Pinecone** as the default vector index for ease of team usage; **SQLite** for local state (Postgres ready).
- **RAG prompt** enforces citations and rejects hallucinations: if context is insufficient, it tells you what's missing.
- **Hybrid-ready**: optional keyword + vector + rerank for high precision.
- **Voyage AI**: built-in reranker (model: rerank-2). If not configured, reranking is skipped.
- **Local-first PDF parsing**: Uses local parsers by default, auto-upgrades to DocAI only when needed.

## Safety & privacy
- Your files stay local. Only text chunks/embeddings go to Pinecone.
- All API keys are user-provided; nothing is hardcoded.

## License
MIT. See LICENSE.
