from __future__ import annotations
from pathlib import Path
from datetime import datetime
import hashlib
import json
from ingest.loaders import iter_files
from ingest.parsers import read_text
from ingest.chunkers import simple_chunks
from state.db import init_db, engine
from sqlalchemy import text as sql


def _hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def ingest_path(root: str | Path) -> dict:
    init_db()
    root = Path(root)
    docs = 0
    chs = 0
    with engine.begin() as conn:
        for f in iter_files(root):
            raw = f.read_bytes()
            h = _hash_bytes(raw)
            # skip if same hash exists
            exists = conn.execute(sql("SELECT id FROM documents WHERE id=:id"), {"id": str(f)}).fetchone()
            if exists:
                prev = conn.execute(sql("SELECT hash FROM documents WHERE id=:id"), {"id": str(f)}).fetchone()
                if prev and prev[0] == h:
                    continue
            text, meta = read_text(f)
            now = datetime.utcnow().isoformat()
            conn.execute(sql(
                "REPLACE INTO documents(id,path,source,title,author,mime,created_at,updated_at,hash,tags)"
                " VALUES(:id,:path,:source,:title,:author,:mime,:created_at,:updated_at,:hash,:tags)"
            ), {
                "id": str(f),
                "path": str(f),
                "source": "local",
                "title": f.name,
                "author": "",
                "mime": f.suffix.lower(),
                "created_at": now,
                "updated_at": now,
                "hash": h,
                "tags": json.dumps({}),
            })
            seqs = simple_chunks(text)
            for c in seqs:
                chunk_id = f"{f}::#{c['seq']}"
                conn.execute(sql(
                    "REPLACE INTO chunks(id,document_id,seq,text,tokens,metadata,created_at)"
                    " VALUES(:id,:document_id,:seq,:text,:tokens,:metadata,:created_at)"
                ), {
                    "id": chunk_id,
                    "document_id": str(f),
                    "seq": c["seq"],
                    "text": c["text"],
                    "tokens": len(c["text"].split()),
                    "metadata": json.dumps({"source": str(f)}),
                    "created_at": now,
                })
            docs += 1
            chs += len(seqs)
    return {"documents": docs, "chunks": chs}
