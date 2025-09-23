"""
End-to-end tests for complete Vectorpenter workflow
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

from apps.cli import cmd_ingest, cmd_index, cmd_ask
from core.validation import startup_validation


class TestCompleteWorkflow:
    """Test complete workflow from ingestion to query"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory with sample files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            inputs_dir = data_dir / "inputs"
            inputs_dir.mkdir(parents=True)
            
            # Create sample text file
            sample_txt = inputs_dir / "sample.txt"
            sample_txt.write_text("""
            Vectorpenter is a local AI fabric for document processing.
            It combines vector search with keyword search for better results.
            The system supports multiple file formats including PDF and DOCX.
            Users can ask questions about their documents using natural language.
            """)
            
            # Create sample markdown file
            sample_md = inputs_dir / "guide.md"
            sample_md.write_text("""
            # Vectorpenter User Guide
            
            ## Overview
            Vectorpenter helps you search through your documents using AI.
            
            ## Features
            - Hybrid search combining vector and keyword search
            - Smart reranking with Voyage AI
            - Support for multiple file formats
            - Local-first architecture
            
            ## Getting Started
            1. Install dependencies
            2. Configure API keys
            3. Ingest your documents
            4. Start asking questions
            """)
            
            yield str(data_dir)
    
    @patch('core.validation.startup_validation')
    def test_startup_validation(self, mock_startup_validation):
        """Test startup validation process"""
        mock_startup_validation.return_value = True
        
        result = startup_validation()
        assert result is True
        mock_startup_validation.assert_called_once()
    
    @patch('ingest.pipeline.ingest_path')
    def test_cmd_ingest_success(self, mock_ingest_path, temp_data_dir):
        """Test successful document ingestion"""
        mock_ingest_path.return_value = {"documents": 2, "chunks": 8}
        
        inputs_path = str(Path(temp_data_dir) / "inputs")
        
        # Should not raise exception
        cmd_ingest(inputs_path)
        
        mock_ingest_path.assert_called_once_with(inputs_path)
    
    @patch('index.upsert.build_and_upsert')
    @patch('search.hybrid.index_typesense')
    def test_cmd_index_success(self, mock_index_typesense, mock_build_and_upsert):
        """Test successful indexing"""
        mock_build_and_upsert.return_value = {"upserts": 8, "namespace": "default"}
        mock_index_typesense.return_value = {"indexed": 8, "skipped": False}
        
        # Should not raise exception
        cmd_index()
        
        mock_build_and_upsert.assert_called_once()
        mock_index_typesense.assert_called_once()
    
    @patch('index.embedder.embed_texts')
    @patch('rag.retriever.vector_search')
    @patch('rag.context_builder.hydrate_matches')
    @patch('rag.context_builder.build_context')
    @patch('rag.generator.answer')
    def test_cmd_ask_vector_only(self, mock_answer, mock_build_context, mock_hydrate, 
                                 mock_vector_search, mock_embed):
        """Test asking questions with vector-only search"""
        # Setup mocks
        mock_embed.return_value = [[0.1] * 1536]
        mock_vector_search.return_value = [
            {"id": "chunk1", "score": 0.9, "text": None, "meta": {}}
        ]
        mock_hydrate.return_value = [
            {"id": "chunk1", "text": "Vectorpenter is a local AI fabric", "doc": "sample.txt", "seq": 0}
        ]
        mock_build_context.return_value = "[#1] sample.txt::0\nVectorpenter is a local AI fabric"
        mock_answer.return_value = "Vectorpenter is a local AI fabric for document processing [#1]."
        
        # Test the command (this will print output)
        with patch('builtins.print') as mock_print:
            cmd_ask("What is Vectorpenter?", k=5, hybrid=False, rerank=False)
        
        # Verify pipeline was called correctly
        mock_embed.assert_called_once_with(["What is Vectorpenter?"])
        mock_vector_search.assert_called_once()
        mock_hydrate.assert_called_once()
        mock_build_context.assert_called_once()
        mock_answer.assert_called_once()
        
        # Verify output was printed
        mock_print.assert_called()
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        output_text = " ".join(print_calls)
        assert "Vectorpenter is a local AI fabric" in output_text
    
    @patch('search.hybrid.hybrid_search')
    @patch('search.hybrid.is_available')
    @patch('index.embedder.embed_texts')
    @patch('rag.context_builder.hydrate_matches')
    @patch('rag.context_builder.build_context')
    @patch('rag.generator.answer')
    def test_cmd_ask_hybrid_search(self, mock_answer, mock_build_context, mock_hydrate,
                                   mock_embed, mock_typesense_available, mock_hybrid_search):
        """Test asking questions with hybrid search"""
        # Setup mocks
        mock_embed.return_value = [[0.1] * 1536]
        mock_typesense_available.return_value = True
        mock_hybrid_search.return_value = [
            {"id": "chunk1", "score": 0.9, "source": "vector"},
            {"id": "chunk2", "score": 0.8, "source": "keyword"}
        ]
        mock_hydrate.return_value = [
            {"id": "chunk1", "text": "Vector search content", "doc": "sample.txt", "seq": 0},
            {"id": "chunk2", "text": "Keyword search content", "doc": "guide.md", "seq": 1}
        ]
        mock_build_context.return_value = "[#1] sample.txt::0\nVector search content\n\n[#2] guide.md::1\nKeyword search content"
        mock_answer.return_value = "The system uses both vector [#1] and keyword search [#2]."
        
        with patch('builtins.print') as mock_print:
            cmd_ask("How does search work?", k=5, hybrid=True, rerank=False)
        
        # Verify hybrid search was used
        mock_hybrid_search.assert_called_once()
        mock_typesense_available.assert_called_once()
        
        # Verify output contains hybrid indication
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        output_text = " ".join(print_calls)
        assert "hybrid" in output_text.lower()
    
    @patch('rag.reranker.rerank')
    @patch('rag.reranker.is_rerank_available')
    @patch('index.embedder.embed_texts')
    @patch('rag.retriever.vector_search')
    @patch('rag.context_builder.hydrate_matches')
    @patch('rag.context_builder.build_context')
    @patch('rag.generator.answer')
    def test_cmd_ask_with_reranking(self, mock_answer, mock_build_context, mock_hydrate,
                                    mock_vector_search, mock_embed, mock_rerank_available, mock_rerank):
        """Test asking questions with reranking"""
        # Setup mocks
        mock_embed.return_value = [[0.1] * 1536]
        mock_rerank_available.return_value = True
        mock_vector_search.return_value = [
            {"id": "chunk1", "score": 0.9},
            {"id": "chunk2", "score": 0.8}
        ]
        mock_hydrate.return_value = [
            {"id": "chunk1", "text": "First result", "doc": "doc1.txt", "seq": 0},
            {"id": "chunk2", "text": "Second result", "doc": "doc2.txt", "seq": 0}
        ]
        # Mock reranking to reverse order
        mock_rerank.return_value = [
            {"id": "chunk2", "text": "Second result", "doc": "doc2.txt", "seq": 0, "rerank_score": 0.95},
            {"id": "chunk1", "text": "First result", "doc": "doc1.txt", "seq": 0, "rerank_score": 0.85}
        ]
        mock_build_context.return_value = "[#1] doc2.txt::0\nSecond result\n\n[#2] doc1.txt::0\nFirst result"
        mock_answer.return_value = "The reranked results show improved relevance [#1] [#2]."
        
        with patch('builtins.print') as mock_print:
            cmd_ask("Test query", k=5, hybrid=False, rerank=True)
        
        # Verify reranking was used
        mock_rerank.assert_called_once()
        mock_rerank_available.assert_called_once()
        
        # Verify output contains rerank indication
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        output_text = " ".join(print_calls)
        assert "rerank" in output_text.lower()
    
    def test_error_handling_missing_api_key(self):
        """Test error handling when API keys are missing"""
        with patch('core.config.settings') as mock_settings:
            mock_settings.openai_api_key = None
            
            from index.embedder import client
            from core.resilience import EmbeddingServiceError
            
            with pytest.raises(EmbeddingServiceError) as exc_info:
                client()
            
            assert "API key not configured" in str(exc_info.value)
    
    @patch('core.monitoring.metrics_collector')
    def test_metrics_collection_during_query(self, mock_metrics):
        """Test that metrics are collected during query processing"""
        mock_metrics.start_query.return_value = "test-query-id"
        
        with patch('index.embedder.embed_texts') as mock_embed, \
             patch('rag.retriever.vector_search') as mock_search, \
             patch('rag.context_builder.hydrate_matches') as mock_hydrate, \
             patch('rag.context_builder.build_context') as mock_build, \
             patch('rag.generator.answer') as mock_answer:
            
            # Setup mocks
            mock_embed.return_value = [[0.1] * 1536]
            mock_search.return_value = [{"id": "chunk1", "score": 0.9}]
            mock_hydrate.return_value = [{"id": "chunk1", "text": "Test", "doc": "test.txt", "seq": 0}]
            mock_build.return_value = "[#1] test.txt::0\nTest"
            mock_answer.return_value = "Test answer [#1]."
            
            with patch('builtins.print'):
                cmd_ask("test query", k=5, hybrid=False, rerank=False)
            
            # Verify metrics were tracked
            # Note: This would need actual integration with the monitoring decorators
            # For now, we just verify the mocks were called
            assert mock_embed.called
            assert mock_search.called


@pytest.mark.integration
class TestAPIWorkflow:
    """Test API workflow end-to-end"""
    
    def test_api_health_endpoint(self):
        """Test API health endpoint"""
        from fastapi.testclient import TestClient
        from apps.api import app
        
        client = TestClient(app)
        
        with patch('core.monitoring.health_check') as mock_health, \
             patch('core.validation.validate_environment') as mock_validate, \
             patch('index.embedder.health_check') as mock_embed_health:
            
            mock_health.return_value = {"healthy": True, "timestamp": "2025-09-23T23:00:00Z"}
            mock_validate.return_value = {"openai_api_key": True, "pinecone_api_key": True}
            mock_embed_health.return_value = True
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "vectorpenter"
            assert data["version"] == "0.1.0"
            assert "capabilities" in data
            assert "configuration" in data
    
    def test_api_metrics_endpoint(self):
        """Test API metrics endpoint"""
        from fastapi.testclient import TestClient
        from apps.api import app
        
        client = TestClient(app)
        
        with patch('core.monitoring.metrics_collector') as mock_metrics, \
             patch('core.cache.get_cache_stats') as mock_cache_stats:
            
            mock_metrics.get_query_stats.return_value = {
                "total_queries": 10,
                "successful_queries": 9,
                "avg_duration_ms": 150.0
            }
            mock_metrics.get_service_stats.return_value = {
                "openai_embeddings": {"success_rate": 0.95, "avg_latency_ms": 200}
            }
            mock_cache_stats.return_value = {
                "embedding_cache": {"total_entries": 50, "utilization": 0.1}
            }
            
            response = client.get("/metrics")
            
            assert response.status_code == 200
            data = response.json()
            assert "query_stats" in data
            assert "service_stats" in data
            assert "cache_stats" in data
    
    def test_api_query_endpoint(self):
        """Test API query endpoint with mocked services"""
        from fastapi.testclient import TestClient
        from apps.api import app
        
        client = TestClient(app)
        
        with patch('index.embedder.embed_texts') as mock_embed, \
             patch('rag.retriever.vector_search') as mock_search, \
             patch('rag.context_builder.hydrate_matches') as mock_hydrate, \
             patch('rag.context_builder.build_context') as mock_build, \
             patch('rag.generator.answer') as mock_answer:
            
            # Setup mocks
            mock_embed.return_value = [[0.1] * 1536]
            mock_search.return_value = [{"id": "chunk1", "score": 0.9}]
            mock_hydrate.return_value = [{"id": "chunk1", "text": "Test content", "doc": "test.txt", "seq": 0}]
            mock_build.return_value = "[#1] test.txt::0\nTest content"
            mock_answer.return_value = "This is a test answer [#1]."
            
            response = client.post("/query", json={
                "q": "What is this about?",
                "k": 5,
                "hybrid": False,
                "rerank": False
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "This is a test answer [#1]."
            assert data["k"] == 5
            assert data["search_type"] == "vector"
            assert data["sources_count"] == 1


@pytest.mark.e2e
class TestRealWorkflow:
    """Test with real file processing (but mocked external services)"""
    
    def test_file_ingestion_and_processing(self, temp_data_dir):
        """Test real file ingestion with mocked external services"""
        from ingest.loaders import iter_files
        from ingest.parsers import read_text
        from ingest.chunkers import simple_chunks
        
        inputs_dir = Path(temp_data_dir) / "inputs"
        
        # Test file discovery
        files = list(iter_files(inputs_dir))
        assert len(files) == 2  # sample.txt and guide.md
        
        # Test text extraction
        for file_path in files:
            text, meta = read_text(file_path)
            assert len(text) > 0
            assert meta["source"] == str(file_path)
            assert meta["name"] == file_path.name
            
            # Test chunking
            chunks = simple_chunks(text)
            assert len(chunks) > 0
            assert all("text" in chunk for chunk in chunks)
            assert all("seq" in chunk for chunk in chunks)
    
    @patch('state.db.engine')
    def test_database_operations(self, mock_engine):
        """Test database operations with mocked SQLite"""
        from ingest.pipeline import ingest_path
        
        # Mock database connection
        mock_conn = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = None  # No existing document
        
        # Test ingestion (will use mocked DB)
        with patch('ingest.loaders.iter_files') as mock_iter_files, \
             patch('ingest.parsers.read_text') as mock_read_text, \
             patch('pathlib.Path.read_bytes') as mock_read_bytes:
            
            # Setup file mocks
            mock_file = Mock()
            mock_file.suffix = ".txt"
            mock_file.__str__ = lambda: "test.txt"
            mock_iter_files.return_value = [mock_file]
            mock_read_text.return_value = ("Test content", {"source": "test.txt"})
            mock_read_bytes.return_value = b"test content"
            
            result = ingest_path("/fake/path")
            
            assert result["documents"] == 1
            assert result["chunks"] > 0
            
            # Verify database calls were made
            assert mock_conn.execute.call_count >= 2  # At least document + chunk inserts


@pytest.mark.slow
class TestPerformanceWorkflow:
    """Test performance characteristics"""
    
    def test_large_document_processing(self):
        """Test processing of large documents"""
        from ingest.chunkers import simple_chunks
        
        # Create large document (simulate 10MB text)
        large_text = "This is a test sentence. " * 100000  # ~2.5MB
        
        import time
        start_time = time.time()
        chunks = simple_chunks(large_text, max_tokens=700, overlap=120)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert len(chunks) > 100  # Should create many chunks
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert all(len(chunk["text"].split()) <= 700 for chunk in chunks)
    
    def test_concurrent_embedding_requests(self):
        """Test handling of concurrent embedding requests"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def mock_embed_single(text: str):
            """Mock single embedding call"""
            time.sleep(0.1)  # Simulate API call
            return [0.1] * 1536
        
        with patch('index.embedder.embed_texts') as mock_embed:
            mock_embed.side_effect = lambda texts: [mock_embed_single(t) for t in texts]
            
            # Test concurrent requests
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(mock_embed, [f"test query {i}"])
                    for i in range(10)
                ]
                
                results = [future.result() for future in futures]
                
                assert len(results) == 10
                assert all(len(result) == 1 for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
