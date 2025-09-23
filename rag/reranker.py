"""
Reranker for Vectorpenter.
Voyage AI (model rerank-2) is the only supported reranker.
If VOYAGE_API_KEY is not configured, returns identity order.
"""

from __future__ import annotations
from typing import List, Dict
from core.config import settings
from core.logging import logger

def rerank(question: str, snippets: List[Dict]) -> List[Dict]:
    """
    Rerank snippets using Voyage AI rerank-2 model.
    If VOYAGE_API_KEY is not configured, returns identity order.
    """
    if not snippets:
        return snippets
    
    # Check if Voyage AI is configured
    if settings.voyage_api_key:
        try:
            logger.info("Reranking with Voyage (rerank-2)")
            return _voyage_rerank(question, snippets)
        except Exception as e:
            logger.warning(f"Voyage reranking failed: {e}")
            logger.info("Falling back to original order")
            return snippets
    else:
        logger.info("No VOYAGE_API_KEY set, skipping rerank")
        return snippets

def _voyage_rerank(question: str, snippets: List[Dict]) -> List[Dict]:
    """Rerank using Voyage AI rerank-2 model"""
    try:
        import voyageai
        
        client = voyageai.Client(api_key=settings.voyage_api_key)
        
        # Prepare documents for reranking
        documents = [snippet.get('text', '') for snippet in snippets]
        
        # Call Voyage rerank API
        rerank_result = client.rerank(
            query=question,
            documents=documents,
            model="rerank-2",
            top_k=len(snippets)
        )
        
        # Reorder snippets based on reranking scores
        reranked_snippets = []
        for result in rerank_result.results:
            original_index = result.index
            reranked_snippet = snippets[original_index].copy()
            reranked_snippet['rerank_score'] = result.relevance_score
            reranked_snippet['reranker'] = 'voyage'
            reranked_snippets.append(reranked_snippet)
        
        logger.info(f"Voyage reranked {len(reranked_snippets)} snippets")
        return reranked_snippets
        
    except ImportError:
        logger.warning("voyageai package not installed")
        return snippets
    except Exception as e:
        logger.warning(f"Voyage reranking error: {e}")
        return snippets

def is_rerank_available() -> bool:
    """Check if Voyage AI reranking is available"""
    return bool(settings.voyage_api_key)
