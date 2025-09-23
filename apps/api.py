from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import time
from index.embedder import embed_texts
from rag.retriever import vector_search
from rag.context_builder import hydrate_matches, build_context
from rag.generator import answer
from rag.reranker import rerank, is_rerank_available
from search.hybrid import hybrid_search, is_available as typesense_available
from core.logging import logger

app = FastAPI(
    title="Vectorpenter API",
    description="The carpenter of context — building vectors into memory",
    version="0.1.0"
)

class QueryRequest(BaseModel):
    q: str
    k: Optional[int] = 12
    hybrid: Optional[bool] = False
    rerank: Optional[bool] = False

class QueryResponse(BaseModel):
    answer: str
    k: int
    hybrid: bool
    rerank: bool
    search_type: str
    sources_count: int

@app.get("/health")
def health():
    """Comprehensive health check endpoint"""
    from core.monitoring import health_check
    from core.validation import validate_environment
    from index.embedder import health_check as embedding_health_check
    
    # Get comprehensive health data
    health_data = health_check()
    
    # Add capability checks
    capabilities = {
        "typesense_available": typesense_available(),
        "rerank_available": is_rerank_available(),
        "embedding_service": embedding_health_check()
    }
    
    # Add configuration validation
    config_validation = validate_environment()
    
    health_data.update({
        "service": "vectorpenter",
        "version": "0.1.0",
        "capabilities": capabilities,
        "configuration": {
            "valid": all(config_validation.values()),
            "details": config_validation
        }
    })
    
    return health_data

@app.get("/metrics")
def metrics():
    """Get system metrics and statistics"""
    from core.monitoring import metrics_collector
    from core.cache import get_cache_stats
    
    return {
        "query_stats": metrics_collector.get_query_stats(window_minutes=60),
        "service_stats": metrics_collector.get_service_stats(),
        "cache_stats": get_cache_stats(),
        "timestamp": time.time()
    }

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """Query the knowledge base with optional hybrid search and reranking"""
    try:
        # Embed the query
        vec = embed_texts([request.q])[0]
        
        # Search for relevant chunks
        best_score = 0.0
        if request.hybrid and typesense_available():
            matches, best_score = hybrid_search(request.q, vec, top_k=request.k)
            search_type = "hybrid"
        else:
            # Oversample for potential reranking
            search_k = request.k * 2 if request.rerank else request.k
            matches, best_score = vector_search(vec, top_k=search_k)
            search_type = "vector"
        
        # Hydrate matches with full text
        snippets = hydrate_matches(matches)
        
        # Optional reranking
        if request.rerank and is_rerank_available() and snippets:
            snippets = rerank(request.q, snippets)
            snippets = snippets[:request.k]  # Trim to final k
            search_type += "+rerank"
        
        # Google grounding fallback
        external_snippets = []
        from core.config import is_grounding_enabled, grounding_threshold, max_google_results
        from gcp.search import google_ground, should_use_grounding
        
        if is_grounding_enabled() and should_use_grounding(best_score, len(snippets), request.k):
            try:
                external_snippets = google_ground(request.q, max_results=max_google_results())
                if external_snippets:
                    logger.info(f"API Grounding: added {len(external_snippets)} Google snippets")
                    search_type += "+grounding"
            except Exception as e:
                logger.warning(f"API Grounding failed: {e}")
        
        # Build context pack (local + external)
        from rag.context_builder import build_combined_context
        pack = build_combined_context(snippets, external_snippets)
        
        # Generate answer
        if pack.strip():
            ans = answer(request.q, pack)
            logger.info(f"API query processed ({search_type}): {len(snippets)} sources")
        else:
            ans = "I don't have enough context to answer this question. Please make sure documents have been ingested and indexed."
        
        return QueryResponse(
            answer=ans,
            k=request.k,
            hybrid=request.hybrid,
            rerank=request.rerank,
            search_type=search_type,
            sources_count=len(snippets) + len(external_snippets)
        )
        
    except Exception as e:
        logger.error(f"API query failed: {e}")
        return QueryResponse(
            answer=f"Sorry, I encountered an error: {e}",
            k=request.k,
            hybrid=request.hybrid,
            rerank=request.rerank,
            search_type="error",
            sources_count=0
        )

# Legacy endpoint for backward compatibility
@app.post("/query_legacy")
def query_legacy(payload: dict):
    """Legacy query endpoint (deprecated)"""
    q = payload.get("q", "")
    k = int(payload.get("k", 12))
    hybrid = payload.get("hybrid", False)
    rerank = payload.get("rerank", False)
    
    request = QueryRequest(q=q, k=k, hybrid=hybrid, rerank=rerank)
    response = query(request)
    
    return {
        "answer": response.answer,
        "k": response.k,
        "hybrid": response.hybrid,
        "rerank": response.rerank
    }
