from __future__ import annotations
from typing import List, Dict, Tuple
from index.pinecone_client import get_index
from core.config import settings


def vector_search(query_vec: List[float], top_k: int = 12, namespace: str | None = None) -> Tuple[List[Dict], float]:
    """
    Perform vector search and return results with best score
    
    Returns:
        Tuple of (results_list, best_score)
    """
    idx = get_index()
    ns = namespace or settings.pinecone_namespace
    res = idx.query(namespace=ns, vector=query_vec, top_k=top_k, include_metadata=True)
    out = []
    best_score = 0.0
    
    for m in res.matches:
        score = float(m.score)
        if score > best_score:
            best_score = score
            
        out.append({
            "id": m.id,
            "score": score,
            "text": None,  # filled by join step
            "meta": m.metadata,
        })
    
    return out, best_score
