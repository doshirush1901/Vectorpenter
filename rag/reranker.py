from __future__ import annotations
from typing import List, Dict, Optional
from core.config import settings
from core.logging import logger

def rerank(question: str, snippets: List[Dict]) -> List[Dict]:
    """
    Rerank snippets using available reranking services.
    Priority: Voyage → Cohere → identity fallback
    """
    if not snippets:
        return snippets
    
    # Try Voyage AI first
    if settings.voyage_api_key:
        try:
            return _voyage_rerank(question, snippets)
        except Exception as e:
            logger.warning(f"Voyage reranking failed: {e}")
    
    # Try Cohere as fallback
    if settings.cohere_api_key:
        try:
            return _cohere_rerank(question, snippets)
        except Exception as e:
            logger.warning(f"Cohere reranking failed: {e}")
    
    # Identity fallback - return original order
    logger.info("No reranking service available, using original order")
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

def _cohere_rerank(question: str, snippets: List[Dict]) -> List[Dict]:
    """Rerank using Cohere rerank-english-v3.0 model"""
    try:
        import cohere
        
        client = cohere.Client(api_key=settings.cohere_api_key)
        
        # Prepare documents for reranking
        documents = [snippet.get('text', '') for snippet in snippets]
        
        # Call Cohere rerank API
        rerank_result = client.rerank(
            model="rerank-english-v3.0",
            query=question,
            documents=documents,
            top_k=len(snippets)
        )
        
        # Reorder snippets based on reranking scores
        reranked_snippets = []
        for result in rerank_result.results:
            original_index = result.index
            reranked_snippet = snippets[original_index].copy()
            reranked_snippet['rerank_score'] = result.relevance_score
            reranked_snippet['reranker'] = 'cohere'
            reranked_snippets.append(reranked_snippet)
        
        logger.info(f"Cohere reranked {len(reranked_snippets)} snippets")
        return reranked_snippets
        
    except ImportError:
        logger.warning("cohere package not installed")
        return snippets
    except Exception as e:
        logger.warning(f"Cohere reranking error: {e}")
        return snippets

def is_rerank_available() -> bool:
    """Check if any reranking service is available"""
    return bool(settings.voyage_api_key or settings.cohere_api_key)
