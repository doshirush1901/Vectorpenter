"""
Google Programmable Search integration for grounding
Fallback when local retrieval is weak
"""

from __future__ import annotations
from typing import List, Dict, Any
import requests
from core.config import settings
from core.logging import logger

def google_ground(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search Google for grounding information when local retrieval is weak
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, link, snippet
    """
    try:
        # Check if required credentials are available
        if not settings.google_search_api_key or not settings.google_search_cx:
            logger.warning("Google Search API key or CX not configured")
            return []
        
        # Prepare search parameters
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": settings.google_search_api_key,
            "cx": settings.google_search_cx,
            "q": query,
            "num": min(max_results, 10),  # Google CSE max is 10
            "safe": "off",
            "fields": "items(title,link,snippet)"
        }
        
        logger.debug(f"Performing Google search: {query} (max_results={max_results})")
        
        # Make the search request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        items = data.get("items", [])
        
        # Format results
        results = []
        for item in items[:max_results]:
            result = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            }
            
            # Only include results with meaningful content
            if result["title"] and result["snippet"]:
                results.append(result)
        
        logger.info(f"Google search completed: {len(results)} results for '{query}'")
        return results
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"Google search request failed: {e}")
        return []
    except requests.exceptions.Timeout:
        logger.warning("Google search request timed out")
        return []
    except Exception as e:
        logger.warning(f"Google search failed: {e}")
        return []


def is_google_search_available() -> bool:
    """
    Check if Google Search is properly configured
    
    Returns:
        True if Google Search can be used, False otherwise
    """
    return bool(settings.google_search_api_key and settings.google_search_cx)


def test_google_search_connection() -> bool:
    """
    Test Google Search API connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        if not is_google_search_available():
            logger.warning("Google Search not properly configured")
            return False
        
        # Test with a simple query
        test_results = google_ground("test", max_results=1)
        
        if test_results:
            logger.info("Google Search connection successful")
            return True
        else:
            logger.warning("Google Search returned no results for test query")
            return False
        
    except Exception as e:
        logger.warning(f"Google Search connection test failed: {e}")
        return False


def estimate_search_cost(num_queries: int) -> dict:
    """
    Estimate Google Custom Search API cost
    
    Args:
        num_queries: Number of search queries
        
    Returns:
        Dictionary with cost estimates
    """
    # Google Custom Search pricing (as of 2025)
    # First 100 queries per day are free
    # Additional queries cost $5 per 1000 queries
    
    free_queries_per_day = 100
    cost_per_1000_queries = 5.0
    
    if num_queries <= free_queries_per_day:
        cost = 0.0
        paid_queries = 0
    else:
        paid_queries = num_queries - free_queries_per_day
        cost = (paid_queries / 1000) * cost_per_1000_queries
    
    return {
        "total_queries": num_queries,
        "free_queries": min(num_queries, free_queries_per_day),
        "paid_queries": paid_queries,
        "estimated_cost_usd": round(cost, 4),
        "note": "First 100 queries/day free, then $5 per 1000 queries"
    }


def format_google_results_for_context(results: List[Dict[str, Any]]) -> str:
    """
    Format Google search results for inclusion in context pack
    
    Args:
        results: List of Google search results
        
    Returns:
        Formatted string for context inclusion
    """
    if not results:
        return ""
    
    formatted_parts = ["### External Web Context (Google)\n"]
    
    for i, result in enumerate(results, 1):
        title = result.get("title", "Unknown Title")
        snippet = result.get("snippet", "No description available")
        link = result.get("link", "")
        
        formatted_parts.append(f"[G#{i}] {title}\n{snippet}\n({link})\n")
    
    return "\n".join(formatted_parts)


def should_use_grounding(best_score: float, num_results: int, k: int) -> bool:
    """
    Determine if grounding should be used based on retrieval quality
    
    Args:
        best_score: Best similarity score from local retrieval
        num_results: Number of results from local retrieval
        k: Requested number of results
        
    Returns:
        True if grounding should be used, False otherwise
    """
    if not is_google_search_available():
        return False
    
    # Use grounding if:
    # 1. Best score is below threshold (weak semantic match)
    # 2. We got significantly fewer results than requested
    weak_similarity = best_score < settings.grounding_sim_threshold
    insufficient_results = num_results < (k // 2)
    
    should_ground = weak_similarity or insufficient_results
    
    if should_ground:
        logger.debug(f"Grounding triggered: best_score={best_score:.3f} (threshold={settings.grounding_sim_threshold}), "
                    f"results={num_results}/{k}")
    
    return should_ground
