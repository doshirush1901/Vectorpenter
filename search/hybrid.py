from __future__ import annotations
from typing import List, Dict
from sqlalchemy import text as sql
from state.db import engine
from search.typesense_client import ensure_collection, delete_collection, index_documents, search_keywords, is_available
from core.logging import logger
import time

def index_typesense() -> dict:
    """Index all chunks from SQLite to Typesense"""
    if not is_available():
        logger.warning("Typesense indexing skipped (no server or key)")
        return {"indexed": 0, "skipped": True}
    
    try:
        # Delete and recreate collection for clean reindex
        if not delete_collection():
            return {"indexed": 0, "error": "Failed to recreate collection"}
        
        # Fetch all chunks from SQLite
        with engine.begin() as conn:
            rows = conn.execute(sql(
                "SELECT c.id, c.document_id, c.seq, c.text, c.created_at, d.path "
                "FROM chunks c JOIN documents d ON c.document_id = d.id"
            )).fetchall()
        
        if not rows:
            logger.info("No chunks found for Typesense indexing")
            return {"indexed": 0, "total": 0}
        
        # Convert to Typesense document format
        documents = []
        for row in rows:
            chunk_id, doc_id, seq, text, created_at, doc_path = row
            
            # Extract filename from path for doc field
            doc_name = doc_path.split('/')[-1] if '/' in doc_path else doc_path.split('\\')[-1]
            
            documents.append({
                'id': chunk_id,
                'doc': doc_name,
                'seq': seq,
                'text': text,
                'created_at': int(time.time()) if not created_at else int(time.mktime(time.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%f')))
            })
        
        # Index to Typesense
        indexed_count = index_documents(documents)
        
        return {
            "indexed": indexed_count,
            "total": len(documents),
            "skipped": False
        }
        
    except Exception as e:
        logger.error(f"Typesense indexing failed: {e}")
        return {"indexed": 0, "error": str(e)}

def keyword_search(query: str, k: int = 24) -> List[Dict]:
    """Search Typesense for keyword matches"""
    if not is_available():
        return []
    
    return search_keywords(query, k)

def hybrid_merge(keyword_results: List[Dict], vector_results: List[Dict], k: int = 12) -> List[Dict]:
    """Merge keyword and vector search results using round-robin with deduplication"""
    seen_ids = set()
    merged = []
    
    # Convert to iterators for round-robin
    keyword_iter = iter(keyword_results)
    vector_iter = iter(vector_results)
    
    keyword_done = False
    vector_done = False
    
    while len(merged) < k and not (keyword_done and vector_done):
        # Try to add from keyword results
        if not keyword_done:
            try:
                kw_result = next(keyword_iter)
                if kw_result['id'] not in seen_ids:
                    seen_ids.add(kw_result['id'])
                    kw_result['source'] = 'keyword'
                    merged.append(kw_result)
            except StopIteration:
                keyword_done = True
        
        # Try to add from vector results
        if not vector_done and len(merged) < k:
            try:
                vec_result = next(vector_iter)
                if vec_result['id'] not in seen_ids:
                    seen_ids.add(vec_result['id'])
                    vec_result['source'] = 'vector'
                    merged.append(vec_result)
            except StopIteration:
                vector_done = True
    
    return merged[:k]

def hybrid_search(query: str, query_vec: List[float], k: int = 12) -> List[Dict]:
    """Perform hybrid search combining keyword and vector results"""
    from rag.retriever import vector_search
    from core.config import has_commercial_license
    
    # Commercial license check for hybrid search
    if not has_commercial_license():
        logger.warning("Hybrid search requires commercial license. Using vector-only search.")
        logger.info("Get your license at: https://vectorpenter.com/pricing")
        return vector_search(query_vec, top_k=k)
    
    # Oversample for better hybrid merging
    oversample_k = k * 2
    
    # Get keyword results
    keyword_results = keyword_search(query, oversample_k)
    
    # Get vector results  
    vector_results = vector_search(query_vec, top_k=oversample_k)
    
    # Merge results
    merged_results = hybrid_merge(keyword_results, vector_results, k)
    
    logger.info(f"Hybrid search: {len(keyword_results)} keyword + {len(vector_results)} vector → {len(merged_results)} merged")
    
    return merged_results
