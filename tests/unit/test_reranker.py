"""
Unit tests for RAG reranker module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict

from rag.reranker import rerank, _voyage_rerank, is_rerank_available
from core.config import settings


class TestReranker:
    """Test suite for reranking functionality"""
    
    @pytest.fixture
    def sample_snippets(self):
        """Sample snippets for testing"""
        return [
            {"id": "chunk1", "text": "Python is a programming language", "score": 0.8},
            {"id": "chunk2", "text": "Machine learning with Python", "score": 0.7},
            {"id": "chunk3", "text": "Data science applications", "score": 0.6}
        ]
    
    @pytest.fixture
    def mock_voyage_client(self):
        """Mock Voyage AI client"""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.results = [
            Mock(index=1, relevance_score=0.95),  # Reordered: chunk2 first
            Mock(index=0, relevance_score=0.85),  # chunk1 second
            Mock(index=2, relevance_score=0.75)   # chunk3 third
        ]
        mock_client.rerank.return_value = mock_result
        return mock_client
    
    def test_rerank_empty_snippets(self):
        """Test reranking with empty snippets"""
        result = rerank("test query", [])
        assert result == []
    
    @patch('rag.reranker.settings')
    def test_rerank_no_voyage_key(self, mock_settings, sample_snippets):
        """Test reranking when no Voyage API key is available"""
        mock_settings.voyage_api_key = None
        
        with patch('rag.reranker.logger') as mock_logger:
            result = rerank("test query", sample_snippets)
            
            assert result == sample_snippets  # Should return original order
            mock_logger.info.assert_called_with("No VOYAGE_API_KEY set, skipping rerank")
    
    @patch('rag.reranker.settings')
    @patch('rag.reranker.voyageai')
    def test_rerank_voyage_success(self, mock_voyageai, mock_settings, sample_snippets, mock_voyage_client):
        """Test successful Voyage AI reranking"""
        mock_settings.voyage_api_key = "test-key"
        mock_voyageai.Client.return_value = mock_voyage_client
        
        with patch('rag.reranker.logger') as mock_logger:
            result = rerank("test query", sample_snippets)
            
            # Should be reordered according to mock results
            assert len(result) == 3
            assert result[0]["id"] == "chunk2"  # index=1 from mock, highest score
            assert result[1]["id"] == "chunk1"  # index=0 from mock
            assert result[2]["id"] == "chunk3"  # index=2 from mock
            
            # Check reranking scores were added
            assert result[0]["rerank_score"] == 0.95
            assert result[0]["reranker"] == "voyage"
            
            mock_logger.info.assert_called_with("Reranking with Voyage (rerank-2)")
    
    @patch('rag.reranker.settings')
    @patch('rag.reranker.voyageai')
    def test_rerank_voyage_import_error(self, mock_voyageai, mock_settings, sample_snippets):
        """Test handling of missing voyageai package"""
        mock_settings.voyage_api_key = "test-key"
        mock_voyageai.Client.side_effect = ImportError("No module named 'voyageai'")
        
        with patch('rag.reranker.logger') as mock_logger:
            result = rerank("test query", sample_snippets)
            
            assert result == sample_snippets  # Should fallback to original order
            mock_logger.warning.assert_called_with("voyageai package not installed")
    
    @patch('rag.reranker.settings')
    @patch('rag.reranker.voyageai')
    def test_rerank_voyage_api_error(self, mock_voyageai, mock_settings, sample_snippets):
        """Test handling of Voyage API errors"""
        mock_settings.voyage_api_key = "test-key"
        mock_client = Mock()
        mock_client.rerank.side_effect = Exception("API rate limit exceeded")
        mock_voyageai.Client.return_value = mock_client
        
        with patch('rag.reranker.logger') as mock_logger:
            result = rerank("test query", sample_snippets)
            
            assert result == sample_snippets  # Should fallback to original order
            mock_logger.warning.assert_called_with("Voyage reranking failed: API rate limit exceeded")
            mock_logger.info.assert_called_with("Falling back to original order")
    
    @patch('rag.reranker.settings')
    @patch('rag.reranker.voyageai')
    def test_voyage_rerank_direct(self, mock_voyageai, mock_settings, sample_snippets, mock_voyage_client):
        """Test _voyage_rerank function directly"""
        mock_settings.voyage_api_key = "test-key"
        mock_voyageai.Client.return_value = mock_voyage_client
        
        result = _voyage_rerank("test query", sample_snippets)
        
        # Verify API call
        mock_voyage_client.rerank.assert_called_once_with(
            query="test query",
            documents=["Python is a programming language", "Machine learning with Python", "Data science applications"],
            model="rerank-2",
            top_k=3
        )
        
        # Verify reordering
        assert len(result) == 3
        assert result[0]["id"] == "chunk2"  # Reordered based on mock results
        assert result[0]["rerank_score"] == 0.95
        assert result[0]["reranker"] == "voyage"
    
    def test_is_rerank_available_with_key(self):
        """Test is_rerank_available when Voyage key is present"""
        with patch('rag.reranker.settings') as mock_settings:
            mock_settings.voyage_api_key = "test-key"
            assert is_rerank_available() is True
    
    def test_is_rerank_available_no_key(self):
        """Test is_rerank_available when no Voyage key"""
        with patch('rag.reranker.settings') as mock_settings:
            mock_settings.voyage_api_key = None
            assert is_rerank_available() is False
    
    def test_rerank_preserves_original_data(self, sample_snippets):
        """Test that reranking preserves all original snippet data"""
        # Add extra fields to snippets
        enhanced_snippets = []
        for snippet in sample_snippets:
            enhanced_snippet = snippet.copy()
            enhanced_snippet.update({
                "metadata": {"source": "test.pdf", "page": 1},
                "doc": "test_document",
                "seq": 1
            })
            enhanced_snippets.append(enhanced_snippet)
        
        with patch('rag.reranker.settings') as mock_settings:
            mock_settings.voyage_api_key = None
            
            result = rerank("test query", enhanced_snippets)
            
            # Should preserve all original fields
            assert result[0]["metadata"]["source"] == "test.pdf"
            assert result[0]["doc"] == "test_document"
            assert result[0]["seq"] == 1
    
    @patch('rag.reranker.settings')
    @patch('rag.reranker.voyageai')
    def test_rerank_with_single_snippet(self, mock_voyageai, mock_settings, mock_voyage_client):
        """Test reranking with only one snippet"""
        mock_settings.voyage_api_key = "test-key"
        mock_voyage_client.rerank.return_value.results = [
            Mock(index=0, relevance_score=0.9)
        ]
        mock_voyageai.Client.return_value = mock_voyage_client
        
        single_snippet = [{"id": "chunk1", "text": "Single test snippet", "score": 0.8}]
        result = rerank("test query", single_snippet)
        
        assert len(result) == 1
        assert result[0]["id"] == "chunk1"
        assert result[0]["rerank_score"] == 0.9
    
    def test_rerank_with_none_input(self):
        """Test reranking handles None input gracefully"""
        with pytest.raises(TypeError):
            rerank("test query", None)
    
    def test_rerank_with_malformed_snippets(self):
        """Test reranking with malformed snippet data"""
        malformed_snippets = [
            {"id": "chunk1"},  # Missing text
            {"text": "No ID snippet"},  # Missing ID
            {}  # Empty snippet
        ]
        
        with patch('rag.reranker.settings') as mock_settings:
            mock_settings.voyage_api_key = None
            
            # Should not crash, return as-is
            result = rerank("test query", malformed_snippets)
            assert len(result) == 3


@pytest.mark.integration
class TestRerankerIntegration:
    """Integration tests for reranker with real-like scenarios"""
    
    def test_rerank_performance_large_set(self):
        """Test reranking performance with large snippet sets"""
        large_snippets = [
            {"id": f"chunk{i}", "text": f"Test snippet number {i}", "score": 0.5}
            for i in range(100)
        ]
        
        with patch('rag.reranker.settings') as mock_settings:
            mock_settings.voyage_api_key = None
            
            import time
            start_time = time.time()
            result = rerank("test query", large_snippets)
            end_time = time.time()
            
            assert len(result) == 100
            assert (end_time - start_time) < 1.0  # Should be fast for identity fallback


if __name__ == "__main__":
    pytest.main([__file__])
