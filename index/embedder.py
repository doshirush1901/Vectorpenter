from __future__ import annotations
from typing import List
from core.config import settings
from core.resilience import (
    retry_embedding_service, embedding_circuit_breaker, 
    EmbeddingServiceError, track_service_call
)
from core.cache import cache_embeddings
from core.logging import logger
from openai import OpenAI

EMBED_MODEL = "text-embedding-3-small"

_client: OpenAI | None = None

def client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise EmbeddingServiceError("openai", "API key not configured")
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


@cache_embeddings(ttl=3600)  # Cache for 1 hour
@track_service_call("openai_embeddings")
@retry_embedding_service(max_attempts=3)
@embedding_circuit_breaker
def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for text using OpenAI API with caching and resilience
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
        
    Raises:
        EmbeddingServiceError: If embedding generation fails
    """
    if not texts:
        return []
    
    # Validate input
    if not all(isinstance(text, str) for text in texts):
        raise ValueError("All inputs must be strings")
    
    # Filter out empty texts
    non_empty_texts = [text.strip() for text in texts if text.strip()]
    if not non_empty_texts:
        logger.warning("No non-empty texts provided for embedding")
        return []
    
    try:
        c = client()
        logger.debug(f"Generating embeddings for {len(non_empty_texts)} texts")
        
        resp = c.embeddings.create(
            model=EMBED_MODEL, 
            input=non_empty_texts,
            encoding_format="float"
        )
        
        embeddings = [d.embedding for d in resp.data]
        
        logger.debug(f"Successfully generated {len(embeddings)} embeddings")
        return embeddings
        
    except Exception as e:
        error_msg = f"Failed to generate embeddings: {str(e)}"
        logger.error(error_msg)
        raise EmbeddingServiceError("openai", str(e))


def health_check() -> bool:
    """Check if embedding service is healthy"""
    try:
        # Test with a simple embedding
        test_result = embed_texts(["health check"])
        return len(test_result) == 1 and len(test_result[0]) == 1536
    except Exception as e:
        logger.warning(f"Embedding service health check failed: {e}")
        return False
