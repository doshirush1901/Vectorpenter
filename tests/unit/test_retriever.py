"""
Unit tests for RAG retriever module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict
import numpy as np

from rag.retriever import vector_search
from core.config import settings


class TestVectorRetriever:
    """Test suite for vector retrieval functionality"""
    
    @pytest.fixture
    def mock_pinecone_index(self):
        """Mock Pinecone index for testing"""
        mock_index = Mock()
        mock_result = Mock()
        mock_result.matches = [
            Mock(id="chunk1", score=0.95, metadata={"rid": "chunk1", "meta": "{}"}),
            Mock(id="chunk2", score=0.87, metadata={"rid": "chunk2", "meta": "{}"}),
            Mock(id="chunk3", score=0.73, metadata={"rid": "chunk3", "meta": "{}"})
        ]
        mock_index.query.return_value = mock_result
        return mock_index
    
    @pytest.fixture
    def sample_query_vector(self):
        """Sample query vector for testing"""
        return [0.1] * 1536  # OpenAI embedding dimension
    
    @patch('rag.retriever.get_index')
    def test_vector_search_success(self, mock_get_index, mock_pinecone_index, sample_query_vector):
        """Test successful vector search"""
        mock_get_index.return_value = mock_pinecone_index
        
        results = vector_search(sample_query_vector, top_k=3)
        
        assert len(results) == 3
        assert results[0]['id'] == 'chunk1'
        assert results[0]['score'] == 0.95
        assert results[1]['id'] == 'chunk2'
        assert results[1]['score'] == 0.87
        
        # Verify Pinecone query was called correctly
        mock_pinecone_index.query.assert_called_once_with(
            namespace=settings.pinecone_namespace,
            vector=sample_query_vector,
            top_k=3,
            include_metadata=True
        )
    
    @patch('rag.retriever.get_index')
    def test_vector_search_empty_results(self, mock_get_index, sample_query_vector):
        """Test vector search with empty results"""
        mock_index = Mock()
        mock_result = Mock()
        mock_result.matches = []
        mock_index.query.return_value = mock_result
        mock_get_index.return_value = mock_index
        
        results = vector_search(sample_query_vector, top_k=5)
        
        assert len(results) == 0
    
    @patch('rag.retriever.get_index')
    def test_vector_search_with_namespace(self, mock_get_index, mock_pinecone_index, sample_query_vector):
        """Test vector search with custom namespace"""
        mock_get_index.return_value = mock_pinecone_index
        
        custom_namespace = "test-namespace"
        vector_search(sample_query_vector, top_k=3, namespace=custom_namespace)
        
        mock_pinecone_index.query.assert_called_once_with(
            namespace=custom_namespace,
            vector=sample_query_vector,
            top_k=3,
            include_metadata=True
        )
    
    @patch('rag.retriever.get_index')
    def test_vector_search_pinecone_error(self, mock_get_index, sample_query_vector):
        """Test vector search handles Pinecone errors gracefully"""
        mock_index = Mock()
        mock_index.query.side_effect = Exception("Pinecone connection failed")
        mock_get_index.return_value = mock_index
        
        with pytest.raises(Exception) as exc_info:
            vector_search(sample_query_vector, top_k=3)
        
        assert "Pinecone connection failed" in str(exc_info.value)
    
    def test_vector_search_invalid_input(self):
        """Test vector search with invalid inputs"""
        # Test with empty vector
        with pytest.raises((ValueError, TypeError)):
            vector_search([], top_k=5)
        
        # Test with invalid top_k
        sample_vector = [0.1] * 1536
        with pytest.raises((ValueError, TypeError)):
            vector_search(sample_vector, top_k=0)
        
        with pytest.raises((ValueError, TypeError)):
            vector_search(sample_vector, top_k=-1)
    
    @patch('rag.retriever.get_index')
    def test_vector_search_score_ordering(self, mock_get_index, sample_query_vector):
        """Test that results are properly ordered by score"""
        mock_index = Mock()
        mock_result = Mock()
        # Unordered matches
        mock_result.matches = [
            Mock(id="chunk2", score=0.75, metadata={"rid": "chunk2", "meta": "{}"}),
            Mock(id="chunk1", score=0.95, metadata={"rid": "chunk1", "meta": "{}"}),
            Mock(id="chunk3", score=0.82, metadata={"rid": "chunk3", "meta": "{}"})
        ]
        mock_index.query.return_value = mock_result
        mock_get_index.return_value = mock_index
        
        results = vector_search(sample_query_vector, top_k=3)
        
        # Results should maintain Pinecone's ordering
        assert results[0]['id'] == 'chunk2'
        assert results[1]['id'] == 'chunk1'
        assert results[2]['id'] == 'chunk3'
    
    @patch('rag.retriever.get_index')
    def test_vector_search_metadata_handling(self, mock_get_index, sample_query_vector):
        """Test proper metadata extraction"""
        mock_index = Mock()
        mock_result = Mock()
        test_metadata = {"rid": "test_chunk", "meta": '{"source": "test.pdf", "page": 1}'}
        mock_result.matches = [
            Mock(id="test_chunk", score=0.9, metadata=test_metadata)
        ]
        mock_index.query.return_value = mock_result
        mock_get_index.return_value = mock_index
        
        results = vector_search(sample_query_vector, top_k=1)
        
        assert len(results) == 1
        assert results[0]['meta'] == test_metadata
        assert results[0]['text'] is None  # Should be filled by hydrate step


@pytest.mark.asyncio
class TestVectorRetrieverAsync:
    """Test suite for async vector retrieval patterns"""
    
    @patch('rag.retriever.get_index')
    async def test_concurrent_searches(self, mock_get_index):
        """Test handling of concurrent vector searches"""
        import asyncio
        
        mock_index = Mock()
        mock_result = Mock()
        mock_result.matches = [
            Mock(id="chunk1", score=0.9, metadata={"rid": "chunk1", "meta": "{}"})
        ]
        mock_index.query.return_value = mock_result
        mock_get_index.return_value = mock_index
        
        # Simulate concurrent searches
        query_vector = [0.1] * 1536
        tasks = [
            asyncio.create_task(asyncio.to_thread(vector_search, query_vector, top_k=1))
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(len(result) == 1 for result in results)
        assert mock_index.query.call_count == 5


if __name__ == "__main__":
    pytest.main([__file__])
