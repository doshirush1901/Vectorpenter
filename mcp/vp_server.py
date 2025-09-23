"""
VP Core MCP Server
Provides Vectorpenter capabilities as MCP tools for department agents
"""

from __future__ import annotations
import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

from core.config import settings
from core.logging import logger
from index.embedder import embed_texts
from rag.retriever import vector_search
from rag.context_builder import hydrate_matches, build_combined_context, expand_with_neighbors
from rag.generator import answer
from rag.reranker import rerank, is_rerank_available
from search.hybrid import hybrid_search, is_available as typesense_available
from ingest.pipeline import ingest_path
from index.upsert import build_and_upsert

class VPMCPServer:
    """VP Core MCP Server providing document intelligence capabilities"""
    
    def __init__(self):
        self.server = Server("vp-core")
        self._register_tools()
        
    def _register_tools(self):
        """Register VP's capabilities as MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List all available VP tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="search_documents",
                        description="Search through ingested documents using VP's hybrid search",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"},
                                "department": {"type": "string", "description": "Department filter (optional)"},
                                "k": {"type": "integer", "default": 12, "description": "Number of results"},
                                "hybrid": {"type": "boolean", "default": True, "description": "Use hybrid search"},
                                "rerank": {"type": "boolean", "default": True, "description": "Apply reranking"},
                                "namespace": {"type": "string", "description": "Pinecone namespace (optional)"}
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="ingest_documents", 
                        description="Ingest new documents into VP's knowledge base",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Path to documents directory"},
                                "department": {"type": "string", "description": "Department tag for documents"},
                                "force_reindex": {"type": "boolean", "default": False}
                            },
                            "required": ["path"]
                        }
                    ),
                    Tool(
                        name="translate_content",
                        description="Translate text content using VP's translation capabilities",
                        inputSchema={
                            "type": "object", 
                            "properties": {
                                "text": {"type": "string", "description": "Text to translate"},
                                "target_language": {"type": "string", "default": "en", "description": "Target language code"},
                                "source_language": {"type": "string", "description": "Source language (auto-detect if not provided)"}
                            },
                            "required": ["text"]
                        }
                    ),
                    Tool(
                        name="capture_webpage",
                        description="Capture webpage screenshot for analysis using VP's web capture",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "URL to capture"},
                                "format": {"type": "string", "default": "png", "enum": ["png", "pdf", "jpeg"]},
                                "device": {"type": "string", "default": "desktop", "enum": ["desktop", "mobile", "tablet"]},
                                "full_page": {"type": "boolean", "default": True}
                            },
                            "required": ["url"]
                        }
                    ),
                    Tool(
                        name="ocr_document",
                        description="Extract text from images/PDFs using VP's OCR capabilities", 
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "file_path": {"type": "string", "description": "Path to image or PDF file"},
                                "use_docai": {"type": "boolean", "default": True, "description": "Use Google DocAI for better accuracy"}
                            },
                            "required": ["file_path"]
                        }
                    ),
                    Tool(
                        name="generate_answer",
                        description="Generate contextual answer using VP's RAG capabilities",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "question": {"type": "string", "description": "Question to answer"},
                                "context": {"type": "string", "description": "Additional context"},
                                "department_focus": {"type": "string", "description": "Department specialization"},
                                "chat_provider": {"type": "string", "default": "openai", "enum": ["openai", "vertex"]}
                            },
                            "required": ["question"]
                        }
                    ),
                    Tool(
                        name="get_document_stats",
                        description="Get statistics about VP's knowledge base",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "department": {"type": "string", "description": "Filter by department (optional)"},
                                "include_details": {"type": "boolean", "default": False}
                            }
                        }
                    ),
                    Tool(
                        name="health_check",
                        description="Check VP's health and service availability",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "detailed": {"type": "boolean", "default": False}
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls from MCP clients"""
            try:
                logger.info(f"VP MCP tool called: {name} with args: {arguments}")
                
                if name == "search_documents":
                    return await self._search_documents(**arguments)
                elif name == "ingest_documents":
                    return await self._ingest_documents(**arguments)
                elif name == "translate_content":
                    return await self._translate_content(**arguments)
                elif name == "capture_webpage":
                    return await self._capture_webpage(**arguments)
                elif name == "ocr_document":
                    return await self._ocr_document(**arguments)
                elif name == "generate_answer":
                    return await self._generate_answer(**arguments)
                elif name == "get_document_stats":
                    return await self._get_document_stats(**arguments)
                elif name == "health_check":
                    return await self._health_check(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"VP MCP tool error: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def _search_documents(self, query: str, department: Optional[str] = None,
                               k: int = 12, hybrid: bool = True, rerank: bool = True,
                               namespace: Optional[str] = None) -> CallToolResult:
        """Search documents using VP's capabilities"""
        try:
            # Override namespace if department specified
            if department:
                namespace = f"machinecraft_{department}"
            
            # Embed query
            vec = embed_texts([query])[0]
            
            # Search with VP's hybrid capabilities
            if hybrid and typesense_available():
                matches, best_score = hybrid_search(query, vec, top_k=k)
                search_type = "hybrid"
            else:
                matches, best_score = vector_search(vec, top_k=k, namespace=namespace)
                search_type = "vector"
            
            # Hydrate and expand with VP's late windowing
            snippets = hydrate_matches(matches)
            if rerank and is_rerank_available():
                snippets = rerank(query, snippets)
                search_type += "+rerank"
            
            snippets = expand_with_neighbors(snippets, left=1, right=1)
            
            # Prepare results
            results = {
                "search_type": search_type,
                "best_score": best_score,
                "total_results": len(snippets),
                "snippets": [
                    {
                        "id": s.get("id"),
                        "text": s.get("text", "")[:500] + "..." if len(s.get("text", "")) > 500 else s.get("text", ""),
                        "score": s.get("score", 0.0),
                        "source": s.get("doc", "unknown"),
                        "sequence": s.get("seq", 0)
                    }
                    for s in snippets
                ]
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def _ingest_documents(self, path: str, department: Optional[str] = None,
                               force_reindex: bool = False) -> CallToolResult:
        """Ingest documents using VP's pipeline"""
        try:
            # Add department metadata if specified
            if department:
                # Set namespace for department
                original_namespace = settings.pinecone_namespace
                settings.pinecone_namespace = f"machinecraft_{department}"
            
            # Run VP's ingestion pipeline
            result = ingest_path(path)
            
            # Build indexes
            index_result = build_and_upsert()
            
            # Restore original namespace
            if department:
                settings.pinecone_namespace = original_namespace
            
            response = {
                "ingestion": result,
                "indexing": index_result,
                "department": department,
                "namespace": f"machinecraft_{department}" if department else settings.pinecone_namespace
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=json.dumps(response, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise
    
    async def _translate_content(self, text: str, target_language: str = "en",
                                source_language: Optional[str] = None) -> CallToolResult:
        """Translate content using VP's translation capabilities"""
        try:
            from gcp.translation import translate_text, detect_language
            from core.config import is_translation_enabled
            
            if not is_translation_enabled():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps({
                            "original_text": text,
                            "translated_text": text,
                            "translated": False,
                            "reason": "Translation not enabled"
                        })
                    )]
                )
            
            # Detect source language if not provided
            if not source_language:
                source_language = detect_language(text)
            
            # Translate if needed
            translated_text, metadata = translate_text(text, target_language)
            
            response = {
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "metadata": metadata
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(response, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise
    
    async def _capture_webpage(self, url: str, format: str = "png", 
                              device: str = "desktop", full_page: bool = True) -> CallToolResult:
        """Capture webpage using VP's screenshot capabilities"""
        try:
            from tools.screenshotone import fetch_url, is_screenshotone_available
            
            if not is_screenshotone_available():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": "ScreenshotOne not configured"
                        })
                    )]
                )
            
            # Configure environment for this capture
            import os
            os.environ["SCREENSHOTONE_FORMAT"] = format
            os.environ["SCREENSHOTONE_DEVICE"] = device
            os.environ["SCREENSHOTONE_FULL_PAGE"] = str(full_page).lower()
            
            # Capture webpage
            saved_path = fetch_url(url)
            
            response = {
                "success": True,
                "url": url,
                "saved_path": str(saved_path),
                "format": format,
                "device": device,
                "full_page": full_page,
                "file_size": saved_path.stat().st_size if saved_path.exists() else 0
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(response, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"Web capture failed: {e}")
            raise
    
    async def _ocr_document(self, file_path: str, use_docai: bool = True) -> CallToolResult:
        """OCR document using VP's parsing capabilities"""
        try:
            from ingest.parsers import read_text
            from core.config import is_docai_enabled
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Parse using VP's intelligent parsing
            text, metadata = read_text(file_path_obj)
            
            response = {
                "file_path": file_path,
                "extracted_text": text,
                "text_length": len(text),
                "metadata": metadata,
                "parser_used": metadata.get("parser", "unknown"),
                "docai_available": is_docai_enabled()
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(response, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            raise
    
    async def _generate_answer(self, question: str, context: Optional[str] = None,
                              department_focus: Optional[str] = None,
                              chat_provider: str = "openai") -> CallToolResult:
        """Generate answer using VP's RAG capabilities"""
        try:
            # Build specialized context for department
            if department_focus:
                dept_context = f"\nDepartment Focus: {department_focus}\n"
                if context:
                    context = dept_context + context
                else:
                    context = dept_context
            
            # Search for relevant documents first
            vec = embed_texts([question])[0]
            
            if typesense_available():
                matches, best_score = hybrid_search(question, vec, top_k=12)
            else:
                matches, best_score = vector_search(vec, top_k=12)
            
            snippets = hydrate_matches(matches)
            if is_rerank_available():
                snippets = rerank(question, snippets)
            
            snippets = expand_with_neighbors(snippets)
            
            # Build context pack
            context_pack = build_combined_context(snippets, [])
            if context:
                context_pack = f"{context}\n\n{context_pack}"
            
            # Generate answer with VP's capabilities
            answer_text = answer(question, context_pack)
            
            response = {
                "question": question,
                "answer": answer_text,
                "sources_used": len(snippets),
                "best_score": best_score,
                "department_focus": department_focus,
                "chat_provider": chat_provider
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(response, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            raise
    
    async def _get_document_stats(self, department: Optional[str] = None,
                                 include_details: bool = False) -> CallToolResult:
        """Get VP's knowledge base statistics"""
        try:
            from state.db import engine
            from sqlalchemy import text as sql
            
            # Get basic stats
            with engine.begin() as conn:
                if department:
                    # Filter by department namespace
                    doc_count = conn.execute(sql(
                        "SELECT COUNT(*) FROM documents WHERE tags LIKE :dept"
                    ), {"dept": f"%{department}%"}).fetchone()[0]
                    
                    chunk_count = conn.execute(sql(
                        "SELECT COUNT(*) FROM chunks c JOIN documents d ON c.document_id = d.id WHERE d.tags LIKE :dept"
                    ), {"dept": f"%{department}%"}).fetchone()[0]
                else:
                    doc_count = conn.execute(sql("SELECT COUNT(*) FROM documents")).fetchone()[0]
                    chunk_count = conn.execute(sql("SELECT COUNT(*) FROM chunks")).fetchone()[0]
            
            response = {
                "total_documents": doc_count,
                "total_chunks": chunk_count,
                "department_filter": department,
                "namespace": f"machinecraft_{department}" if department else "default"
            }
            
            if include_details:
                # Add more detailed stats
                response["avg_chunks_per_doc"] = chunk_count / doc_count if doc_count > 0 else 0
                response["services_available"] = {
                    "typesense": typesense_available(),
                    "reranking": is_rerank_available(),
                    "translation": is_translation_enabled(),
                    "docai": is_docai_enabled()
                }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(response, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"Stats retrieval failed: {e}")
            raise
    
    async def _health_check(self, detailed: bool = False) -> CallToolResult:
        """Check VP's health status"""
        try:
            from core.monitoring import health_check
            from core.validation import validate_environment
            
            # Get comprehensive health data
            health_data = health_check()
            
            if detailed:
                # Add configuration validation
                config_status = validate_environment()
                health_data["configuration"] = config_status
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(health_data, indent=2)
                )]
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise

async def main():
    """Run VP MCP Server"""
    logger.info("🔨 Starting VP Core MCP Server...")
    
    vp_server = VPMCPServer()
    
    # Initialize server options
    options = InitializationOptions(
        server_name="vp-core",
        server_version="1.0.0",
        capabilities={
            "tools": {}
        }
    )
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await vp_server.server.run(
            read_stream,
            write_stream,
            options
        )

if __name__ == "__main__":
    asyncio.run(main())
