from __future__ import annotations
from typing import List, Dict
from sqlalchemy import text as sql
from state.db import engine
from index.embedder import embed_texts
from index.pinecone_client import get_index
from core.config import settings


def build_and_upsert(namespace: str | None = None) -> dict:
    ns = namespace or settings.pinecone_namespace
    idx = get_index()
    with engine.begin() as conn:
        rows = conn.execute(sql("SELECT id, text, metadata FROM chunks")).fetchall()
    if not rows:
        return {"upserts": 0}

    texts = [r[1] for r in rows]
    vecs = embed_texts(texts)

    items = []
    for (rid, _t, meta), v in zip(rows, vecs):
        items.append({
            "id": rid,
            "values": v,
            "metadata": {"rid": rid, "meta": meta},
        })

    # upsert in batches
    B = 100
    for i in range(0, len(items), B):
        idx.upsert(vectors=items[i:i+B], namespace=ns)
    return {"upserts": len(items), "namespace": ns}
