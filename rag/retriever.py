from __future__ import annotations
from typing import List, Dict
from index.pinecone_client import get_index
from core.config import settings


def vector_search(query_vec: List[float], top_k: int = 12, namespace: str | None = None) -> List[Dict]:
    idx = get_index()
    ns = namespace or settings.pinecone_namespace
    res = idx.query(namespace=ns, vector=query_vec, top_k=top_k, include_metadata=True)
    out = []
    for m in res.matches:
        out.append({
            "id": m.id,
            "score": float(m.score),
            "text": None,  # filled by join step
            "meta": m.metadata,
        })
    return out
