-- Vectorpenter Database Schema
-- SQLite compatible SQL for local state management

-- Documents table: stores metadata about ingested documents
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,                    -- Unique document identifier (file path)
    path TEXT NOT NULL,                     -- File system path to document
    source TEXT DEFAULT 'local',            -- Source type (local, gmail, web, etc.)
    title TEXT,                             -- Document title (extracted or filename)
    author TEXT,                            -- Document author (if available)
    mime TEXT,                              -- MIME type or file extension
    created_at TEXT NOT NULL,               -- ISO timestamp when document was created
    updated_at TEXT NOT NULL,               -- ISO timestamp when document was last modified
    hash TEXT NOT NULL,                     -- SHA256 hash of document content for change detection
    tags TEXT DEFAULT '{}',                 -- JSON array of tags/categories
    metadata TEXT DEFAULT '{}',             -- Additional metadata as JSON
    size_bytes INTEGER DEFAULT 0,          -- Document size in bytes
    page_count INTEGER,                     -- Number of pages (for PDFs)
    word_count INTEGER,                     -- Estimated word count
    language TEXT DEFAULT 'en',            -- Detected or specified language
    indexed_at TEXT,                        -- When document was last indexed
    status TEXT DEFAULT 'pending'          -- Status: pending, processed, error
);

-- Chunks table: stores text chunks extracted from documents
CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,                    -- Unique chunk identifier (doc_id::seq)
    document_id TEXT NOT NULL,              -- Reference to parent document
    seq INTEGER NOT NULL,                   -- Sequence number within document
    text TEXT NOT NULL,                     -- Actual text content of chunk
    tokens INTEGER DEFAULT 0,              -- Estimated token count
    start_char INTEGER,                     -- Start character position in original document
    end_char INTEGER,                       -- End character position in original document
    metadata TEXT DEFAULT '{}',            -- Chunk-specific metadata as JSON
    created_at TEXT NOT NULL,               -- When chunk was created
    embedding_status TEXT DEFAULT 'pending', -- Status: pending, embedded, error
    
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
);

-- Embeddings table: tracks vector embeddings for chunks
CREATE TABLE IF NOT EXISTS embeddings (
    chunk_id TEXT PRIMARY KEY,             -- Reference to chunk
    provider TEXT NOT NULL,                -- Embedding provider (openai, voyage, etc.)
    model TEXT NOT NULL,                   -- Specific model used (text-embedding-3-small)
    dim INTEGER NOT NULL,                  -- Vector dimensions
    vector_id TEXT,                        -- ID in vector database (Pinecone)
    created_at TEXT NOT NULL,              -- When embedding was created
    cost_usd REAL DEFAULT 0.0,            -- Cost of generating embedding
    
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
);

-- Retrieval logs table: tracks search queries and results for analytics
CREATE TABLE IF NOT EXISTS retrieval_logs (
    id TEXT PRIMARY KEY,                    -- Unique log entry ID
    query TEXT NOT NULL,                   -- Original search query
    query_embedding_id TEXT,               -- ID of query embedding if stored
    search_type TEXT DEFAULT 'vector',     -- Type: vector, keyword, hybrid
    filters TEXT DEFAULT '{}',             -- Applied filters as JSON
    candidate_ids TEXT DEFAULT '[]',       -- Retrieved chunk IDs as JSON array
    chosen_ids TEXT DEFAULT '[]',          -- Final selected chunk IDs as JSON array
    scores TEXT DEFAULT '[]',              -- Relevance scores as JSON array
    reranker TEXT,                         -- Reranker used (voyage, cohere, none)
    k INTEGER DEFAULT 12,                  -- Number of results requested
    response_time_ms INTEGER,              -- Query response time in milliseconds
    created_at TEXT NOT NULL,              -- When query was executed
    session_id TEXT,                       -- Session identifier for grouping queries
    user_feedback INTEGER,                 -- User feedback rating (1-5)
    
    -- Indexes for common queries
    INDEX idx_retrieval_logs_created_at ON retrieval_logs(created_at),
    INDEX idx_retrieval_logs_search_type ON retrieval_logs(search_type),
    INDEX idx_retrieval_logs_session_id ON retrieval_logs(session_id)
);

-- Conversations table: tracks chat conversations for context
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,                    -- Unique conversation ID
    title TEXT,                            -- Conversation title/summary
    created_at TEXT NOT NULL,              -- When conversation started
    updated_at TEXT NOT NULL,              -- Last message timestamp
    message_count INTEGER DEFAULT 0,       -- Number of messages in conversation
    metadata TEXT DEFAULT '{}'             -- Additional conversation metadata
);

-- Messages table: individual messages within conversations
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,                    -- Unique message ID
    conversation_id TEXT NOT NULL,         -- Parent conversation
    role TEXT NOT NULL,                    -- Role: user, assistant, system
    content TEXT NOT NULL,                 -- Message content
    created_at TEXT NOT NULL,              -- When message was created
    retrieval_log_id TEXT,                 -- Associated retrieval log if applicable
    tokens INTEGER DEFAULT 0,             -- Token count for the message
    cost_usd REAL DEFAULT 0.0,            -- Cost of generating response
    
    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
    FOREIGN KEY (retrieval_log_id) REFERENCES retrieval_logs (id)
);

-- Usage statistics table: track usage for billing/analytics
CREATE TABLE IF NOT EXISTS usage_stats (
    id TEXT PRIMARY KEY,                    -- Unique stat ID
    date TEXT NOT NULL,                    -- Date (YYYY-MM-DD)
    metric_type TEXT NOT NULL,             -- Type: api_calls, documents, chunks, etc.
    metric_value INTEGER NOT NULL,        -- Numeric value
    metadata TEXT DEFAULT '{}',           -- Additional context as JSON
    created_at TEXT NOT NULL,              -- When stat was recorded
    
    -- Index for efficient time-series queries
    INDEX idx_usage_stats_date ON usage_stats(date),
    INDEX idx_usage_stats_type ON usage_stats(metric_type)
);

-- Configuration table: store application configuration
CREATE TABLE IF NOT EXISTS configuration (
    key TEXT PRIMARY KEY,                   -- Configuration key
    value TEXT NOT NULL,                   -- Configuration value (JSON)
    description TEXT,                      -- Human-readable description
    created_at TEXT NOT NULL,              -- When config was created
    updated_at TEXT NOT NULL               -- When config was last updated
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(hash);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_seq ON chunks(document_id, seq);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_status ON chunks(embedding_status);

CREATE INDEX IF NOT EXISTS idx_embeddings_provider ON embeddings(provider, model);
CREATE INDEX IF NOT EXISTS idx_embeddings_created_at ON embeddings(created_at);

-- Views for common queries
CREATE VIEW IF NOT EXISTS document_stats AS
SELECT 
    d.id,
    d.title,
    d.path,
    d.created_at,
    COUNT(c.id) as chunk_count,
    COUNT(e.chunk_id) as embedded_count,
    d.status
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
LEFT JOIN embeddings e ON c.id = e.chunk_id
GROUP BY d.id;

CREATE VIEW IF NOT EXISTS recent_queries AS
SELECT 
    rl.id,
    rl.query,
    rl.search_type,
    rl.k,
    rl.response_time_ms,
    rl.created_at,
    json_array_length(rl.chosen_ids) as result_count
FROM retrieval_logs rl
ORDER BY rl.created_at DESC
LIMIT 100;

-- Insert default configuration
INSERT OR IGNORE INTO configuration (key, value, description, created_at, updated_at) VALUES
('version', '"0.1.0"', 'Vectorpenter version', datetime('now'), datetime('now')),
('default_chunk_size', '700', 'Default chunk size in tokens', datetime('now'), datetime('now')),
('default_chunk_overlap', '120', 'Default chunk overlap in tokens', datetime('now'), datetime('now')),
('embedding_model', '"text-embedding-3-small"', 'Default embedding model', datetime('now'), datetime('now')),
('llm_model', '"gpt-4o-mini"', 'Default LLM model', datetime('now'), datetime('now'));

-- Triggers for maintaining updated_at timestamps
CREATE TRIGGER IF NOT EXISTS update_documents_updated_at 
    AFTER UPDATE ON documents
BEGIN
    UPDATE documents SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_conversations_updated_at 
    AFTER UPDATE ON conversations
BEGIN
    UPDATE conversations SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_configuration_updated_at 
    AFTER UPDATE ON configuration
BEGIN
    UPDATE configuration SET updated_at = datetime('now') WHERE key = NEW.key;
END;
