from __future__ import annotations
from typing import List, Dict, Optional
import typesense
from core.config import settings
from core.logging import logger

_client: Optional[typesense.Client] = None

def get_client() -> typesense.Client:
    """Get or create Typesense client"""
    global _client
    if _client is None:
        if not settings.typesense_api_key:
            raise ValueError("TYPESENSE_API_KEY not configured")
        
        _client = typesense.Client({
            'api_key': settings.typesense_api_key,
            'nodes': [{
                'host': settings.typesense_host,
                'port': settings.typesense_port,
                'protocol': settings.typesense_protocol
            }],
            'connection_timeout_seconds': 10
        })
    return _client

def ensure_collection() -> bool:
    """Ensure the Typesense collection exists with correct schema"""
    try:
        client = get_client()
        collection_name = settings.typesense_collection
        
        # Try to get existing collection
        try:
            client.collections[collection_name].retrieve()
            logger.info(f"Typesense collection '{collection_name}' already exists")
            return True
        except typesense.exceptions.ObjectNotFound:
            pass
        
        # Create collection with schema
        schema = {
            'name': collection_name,
            'fields': [
                {'name': 'id', 'type': 'string'},
                {'name': 'doc', 'type': 'string'},
                {'name': 'seq', 'type': 'int32'},
                {'name': 'text', 'type': 'string'},
                {'name': 'tags', 'type': 'string[]', 'optional': True},
                {'name': 'created_at', 'type': 'int64', 'optional': True}
            ]
        }
        
        client.collections.create(schema)
        logger.info(f"Created Typesense collection '{collection_name}'")
        return True
        
    except Exception as e:
        logger.warning(f"Typesense collection setup failed: {e}")
        return False

def delete_collection() -> bool:
    """Delete and recreate the collection (for reindexing)"""
    try:
        client = get_client()
        collection_name = settings.typesense_collection
        
        try:
            client.collections[collection_name].delete()
            logger.info(f"Deleted existing collection '{collection_name}'")
        except typesense.exceptions.ObjectNotFound:
            pass
        
        return ensure_collection()
        
    except Exception as e:
        logger.warning(f"Failed to delete Typesense collection: {e}")
        return False

def index_documents(documents: List[Dict]) -> int:
    """Bulk index documents to Typesense"""
    try:
        client = get_client()
        collection_name = settings.typesense_collection
        
        if not documents:
            return 0
        
        # Import documents in batches
        batch_size = 100
        total_indexed = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                result = client.collections[collection_name].documents.import_(batch)
                # Count successful imports
                for item in result:
                    if item.get('success'):
                        total_indexed += 1
            except Exception as e:
                logger.warning(f"Batch import failed: {e}")
        
        logger.info(f"Indexed {total_indexed}/{len(documents)} documents to Typesense")
        return total_indexed
        
    except Exception as e:
        logger.warning(f"Typesense indexing failed: {e}")
        return 0

def search_keywords(query: str, k: int = 24) -> List[Dict]:
    """Search Typesense for keyword matches"""
    try:
        client = get_client()
        collection_name = settings.typesense_collection
        
        search_params = {
            'q': query,
            'query_by': 'text',
            'limit': k,
            'sort_by': '_text_match:desc'
        }
        
        result = client.collections[collection_name].documents.search(search_params)
        
        matches = []
        for hit in result.get('hits', []):
            doc = hit['document']
            matches.append({
                'id': doc['id'],
                'score': hit.get('text_match', 0) / 100.0,  # Normalize to 0-1
                'doc': doc['doc'],
                'seq': doc['seq'],
                'text': doc['text'],
                'source': 'typesense'
            })
        
        return matches
        
    except Exception as e:
        logger.warning(f"Typesense search failed: {e}")
        return []

def is_available() -> bool:
    """Check if Typesense is configured and available"""
    try:
        if not settings.typesense_api_key:
            return False
        client = get_client()
        # Try a simple health check
        client.collections.retrieve()
        return True
    except Exception:
        return False
