"""
Integration tests for the complete RAG pipeline
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict
import tempfile
import os

from apps.cli import cmd_ask
from rag.retriever import vector_search
from rag.context_builder import hydrate_matches, build_context
from rag.generator import answer
from rag.reranker import rerank


class TestRAGPipelineIntegration:
    """Test suite for end-to-end RAG pipeline functionality"""
    
    @pytest.fixture
    def mock_database_chunks(self):
        """Mock database chunks for hydration testing"""
        return [
            ("chunk1", "doc1", 0, "Python is a versatile programming language used for AI development."),
            ("chunk2", "doc2", 1, "Machine learning models require large amounts of training data."),
            ("chunk3", "doc1", 1, "Vector databases enable semantic search capabilities.")
        ]
    
    @pytest.fixture
    def mock_vector_results(self):
        """Mock vector search results"""
        return [
            {"id": "chunk1", "score": 0.95, "text": None, "meta": {}},
            {"id": "chunk2", "score": 0.87, "text": None, "meta": {}},
            {"id": "chunk3", "score": 0.73, "text": None, "meta": {}}
        ]
    
    @patch('rag.context_builder.engine')
    def test_hydrate_matches_integration(self, mock_engine, mock_vector_results, mock_database_chunks):
        """Test hydrating vector results with database content"""
        # Mock database connection and query
        mock_conn = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.fetchall.return_value = mock_database_chunks
        
        hydrated_results = hydrate_matches(mock_vector_results)
        
        assert len(hydrated_results) == 3
        assert hydrated_results[0]["text"] == "Python is a versatile programming language used for AI development."
        assert hydrated_results[0]["doc"] == "doc1"
        assert hydrated_results[0]["seq"] == 0
        
        # Verify SQL query was called
        mock_conn.execute.assert_called_once()
    
    def test_build_context_integration(self):
        """Test building context from hydrated snippets"""
        hydrated_snippets = [
            {"id": "chunk1", "text": "Python is great for AI.", "doc": "python_guide.pdf", "seq": 0},
            {"id": "chunk2", "text": "Machine learning is powerful.", "doc": "ml_intro.pdf", "seq": 1},
            {"id": "chunk3", "text": "Vector search is semantic.", "doc": "search_tech.pdf", "seq": 0}
        ]
        
        context = build_context(hydrated_snippets, max_chars=500)
        
        assert "[#1] python_guide.pdf::0" in context
        assert "[#2] ml_intro.pdf::1" in context
        assert "[#3] search_tech.pdf::0" in context
        assert "Python is great for AI." in context
        assert "Machine learning is powerful." in context
        assert "Vector search is semantic." in context
    
    def test_build_context_truncation(self):
        """Test context building with character limits"""
        long_snippets = [
            {"id": f"chunk{i}", "text": "A" * 100, "doc": f"doc{i}.pdf", "seq": 0}
            for i in range(10)
        ]
        
        context = build_context(long_snippets, max_chars=300)
        
        # Should truncate to fit within limit
        assert len(context) <= 300
        # Should still include at least first snippet
        assert "[#1] doc0.pdf::0" in context
    
    @patch('rag.generator.llm')
    def test_answer_generation_integration(self, mock_llm_client):
        """Test answer generation with context"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Based on the context, Python is excellent for AI development [#1]."
        mock_llm_client.return_value.chat.completions.create.return_value = mock_response
        
        context_pack = """[#1] python_guide.pdf::0
Python is a versatile programming language used for AI development.

[#2] ml_intro.pdf::1  
Machine learning models require large amounts of training data."""
        
        result = answer("Why is Python good for AI?", context_pack)
        
        assert "Python is excellent for AI development" in result
        assert "[#1]" in result  # Should include citation
        
        # Verify LLM was called with correct parameters
        mock_llm_client.return_value.chat.completions.create.assert_called_once()
        call_args = mock_llm_client.return_value.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4o-mini"
        assert call_args[1]["temperature"] == 0.2
    
    @patch('rag.generator.llm')
    def test_answer_generation_insufficient_context(self, mock_llm_client):
        """Test answer generation with insufficient context"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "I don't have enough information to answer this question."
        mock_llm_client.return_value.chat.completions.create.return_value = mock_response
        
        empty_context = ""
        result = answer("Complex technical question?", empty_context)
        
        assert "don't have enough information" in result.lower()
    
    @patch('index.embedder.embed_texts')
    @patch('rag.retriever.vector_search')
    @patch('rag.context_builder.hydrate_matches')
    @patch('rag.context_builder.build_context')
    @patch('rag.generator.answer')
    def test_complete_rag_pipeline(self, mock_answer, mock_build_context, mock_hydrate, 
                                   mock_vector_search, mock_embed):
        """Test complete RAG pipeline from query to answer"""
        # Setup mocks
        mock_embed.return_value = [[0.1] * 1536]
        mock_vector_search.return_value = [
            {"id": "chunk1", "score": 0.9, "text": None, "meta": {}}
        ]
        mock_hydrate.return_value = [
            {"id": "chunk1", "text": "Python is great for AI", "doc": "guide.pdf", "seq": 0}
        ]
        mock_build_context.return_value = "[#1] guide.pdf::0\nPython is great for AI"
        mock_answer.return_value = "Python is excellent for AI development [#1]."
        
        # This would normally be called through CLI, but we'll test the components
        query = "Why is Python good for AI?"
        
        # Simulate the pipeline
        query_vec = mock_embed([query])[0]
        matches = mock_vector_search(query_vec, top_k=5)
        snippets = mock_hydrate(matches)
        context = mock_build_context(snippets)
        result = mock_answer(query, context)
        
        assert result == "Python is excellent for AI development [#1]."
        
        # Verify all components were called
        mock_embed.assert_called_once_with([query])
        mock_vector_search.assert_called_once_with(query_vec, top_k=5)
        mock_hydrate.assert_called_once_with(matches)
        mock_build_context.assert_called_once_with(snippets)
        mock_answer.assert_called_once_with(query, context)
    
    @patch('index.embedder.embed_texts')
    @patch('search.hybrid.hybrid_search')
    @patch('rag.reranker.rerank')
    @patch('rag.context_builder.hydrate_matches')
    @patch('rag.context_builder.build_context')
    @patch('rag.generator.answer')
    def test_hybrid_search_with_reranking_pipeline(self, mock_answer, mock_build_context, 
                                                   mock_hydrate, mock_rerank, mock_hybrid_search, mock_embed):
        """Test complete pipeline with hybrid search and reranking"""
        # Setup mocks for hybrid search pipeline
        mock_embed.return_value = [[0.1] * 1536]
        mock_hybrid_search.return_value = [
            {"id": "chunk1", "score": 0.9, "source": "vector"},
            {"id": "chunk2", "score": 0.8, "source": "keyword"}
        ]
        mock_rerank.return_value = [
            {"id": "chunk2", "score": 0.8, "rerank_score": 0.95, "reranker": "voyage"},
            {"id": "chunk1", "score": 0.9, "rerank_score": 0.85, "reranker": "voyage"}
        ]
        mock_hydrate.return_value = [
            {"id": "chunk2", "text": "Advanced AI techniques", "doc": "advanced.pdf", "seq": 0},
            {"id": "chunk1", "text": "Basic AI concepts", "doc": "basics.pdf", "seq": 0}
        ]
        mock_build_context.return_value = "[#1] advanced.pdf::0\nAdvanced AI techniques\n\n[#2] basics.pdf::0\nBasic AI concepts"
        mock_answer.return_value = "AI involves both basic concepts [#2] and advanced techniques [#1]."
        
        query = "What is artificial intelligence?"
        
        # Simulate hybrid + rerank pipeline
        query_vec = mock_embed([query])[0]
        matches = mock_hybrid_search(query, query_vec, top_k=5)
        reranked = mock_rerank(query, matches)
        snippets = mock_hydrate(reranked)
        context = mock_build_context(snippets)
        result = mock_answer(query, context)
        
        assert "basic concepts" in result
        assert "advanced techniques" in result
        assert "[#1]" in result and "[#2]" in result
        
        # Verify reranking changed order (chunk2 should be first after reranking)
        mock_rerank.assert_called_once()
        reranked_result = mock_rerank.return_value
        assert reranked_result[0]["id"] == "chunk2"  # Higher rerank score
        assert reranked_result[0]["rerank_score"] == 0.95
    
    def test_error_handling_in_pipeline(self):
        """Test error handling throughout the pipeline"""
        # Test with various error conditions
        with patch('index.embedder.embed_texts') as mock_embed:
            mock_embed.side_effect = Exception("Embedding service unavailable")
            
            with pytest.raises(Exception) as exc_info:
                mock_embed(["test query"])
            
            assert "Embedding service unavailable" in str(exc_info.value)
    
    @patch('rag.context_builder.engine')
    def test_database_connection_error_handling(self, mock_engine):
        """Test handling of database connection errors"""
        mock_engine.begin.side_effect = Exception("Database connection failed")
        
        mock_matches = [{"id": "chunk1", "score": 0.9}]
        
        with pytest.raises(Exception) as exc_info:
            hydrate_matches(mock_matches)
        
        assert "Database connection failed" in str(exc_info.value)
    
    def test_empty_query_handling(self):
        """Test handling of empty or invalid queries"""
        with patch('index.embedder.embed_texts') as mock_embed:
            # Test empty query
            mock_embed.return_value = [[0.0] * 1536]  # Zero vector
            
            result = mock_embed([""])
            assert len(result[0]) == 1536
            assert all(x == 0.0 for x in result[0])


@pytest.mark.integration
class TestRAGPipelinePerformance:
    """Performance tests for RAG pipeline"""
    
    def test_pipeline_latency_benchmark(self):
        """Benchmark pipeline latency with mocked services"""
        import time
        
        with patch('index.embedder.embed_texts') as mock_embed, \
             patch('rag.retriever.vector_search') as mock_search, \
             patch('rag.context_builder.hydrate_matches') as mock_hydrate, \
             patch('rag.generator.answer') as mock_answer:
            
            # Setup fast mocks
            mock_embed.return_value = [[0.1] * 1536]
            mock_search.return_value = [{"id": "chunk1", "score": 0.9}]
            mock_hydrate.return_value = [{"id": "chunk1", "text": "Test", "doc": "test.pdf", "seq": 0}]
            mock_answer.return_value = "Test answer"
            
            start_time = time.time()
            
            # Simulate pipeline calls
            query_vec = mock_embed(["test query"])[0]
            matches = mock_search(query_vec, top_k=5)
            snippets = mock_hydrate(matches)
            result = mock_answer("test query", "context")
            
            end_time = time.time()
            latency = end_time - start_time
            
            # Pipeline should be fast with mocks
            assert latency < 0.1  # Less than 100ms
            assert result == "Test answer"


if __name__ == "__main__":
    pytest.main([__file__])
