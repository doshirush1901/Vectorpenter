from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from core.config import settings

engine: Engine = create_engine(settings.db_url, future=True)

INIT_SQL = r"""
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  path TEXT,
  source TEXT,
  title TEXT,
  author TEXT,
  mime TEXT,
  created_at TEXT,
  updated_at TEXT,
  hash TEXT,
  tags TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
  id TEXT PRIMARY KEY,
  document_id TEXT,
  seq INTEGER,
  text TEXT,
  tokens INTEGER,
  metadata TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS embeddings (
  chunk_id TEXT PRIMARY KEY,
  provider TEXT,
  model TEXT,
  dim INTEGER,
  vector_id TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS retrieval_logs (
  id TEXT PRIMARY KEY,
  query TEXT,
  filters TEXT,
  candidate_ids TEXT,
  chosen_ids TEXT,
  scores TEXT,
  created_at TEXT
);
"""

def init_db() -> None:
    with engine.begin() as conn:
        for stmt in INIT_SQL.split(";\n\n"):
            if stmt.strip():
                conn.execute(text(stmt))
