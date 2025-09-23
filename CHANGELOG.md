# Changelog

All notable changes to Vectorpenter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive GitHub Actions CI/CD pipeline
- Security scanning workflows
- Issue and PR templates
- Contribution guidelines
- Commercial licensing and pricing structure

## [0.1.0] - 2025-09-23

### Added
- **Core RAG Framework**: Complete local-first RAG system
- **Document Ingestion**: Support for PDF, DOCX, PPTX, XLSX, CSV, TXT, MD files
- **Vector Search**: Pinecone integration with serverless indexes
- **Hybrid Search**: Typesense keyword search + vector search merging
- **Smart Reranking**: Voyage AI and Cohere reranking with fallback
- **CLI Interface**: Complete command-line interface with hybrid/rerank flags
- **FastAPI Server**: REST API with structured request/response models
- **Cursor Chat REPL**: Interactive chat interface optimized for Cursor IDE
- **Chunking System**: Token-based chunking with overlap
- **Citation System**: Bracketed citations linking answers to sources
- **Configuration Management**: Environment-based configuration with .env support
- **Error Resilience**: Graceful degradation when services unavailable
- **Logging System**: Structured logging throughout the application

### Technical Details
- **Python ≥3.10** support
- **OpenAI Embeddings**: text-embedding-3-small model
- **LLM Generation**: GPT-4o-mini with temperature control
- **SQLite State**: Local database for documents, chunks, embeddings
- **Hash-based Change Detection**: Efficient re-indexing of modified files
- **Round-robin Hybrid Merging**: Intelligent result combination
- **Batch Processing**: Efficient bulk operations for indexing

### Documentation
- Comprehensive README with quick start guide
- Detailed environment configuration examples
- CLI usage documentation with examples
- API endpoint documentation
- Architecture overview and design decisions

### Development
- Complete project structure with modular design
- Smoke tests for all modules
- Type hints throughout codebase
- Error handling and logging best practices
- Extensible architecture for future enhancements

## [0.0.1] - 2025-09-23

### Added
- Initial project structure
- Basic README with project vision
- MIT License
- Repository setup on GitHub

---

## Release Notes

### v0.1.0 - "The Carpenter's Foundation"

This inaugural release establishes Vectorpenter as a comprehensive local-first RAG framework. The name "The carpenter of context — building vectors into memory" reflects our mission to provide developers with robust tools for building intelligent document processing systems.

**Key Highlights:**
- **Complete Hybrid Search**: Combines the precision of vector similarity with the recall of keyword search
- **Production-Ready**: Comprehensive error handling, logging, and configuration management
- **Developer-Friendly**: Three interfaces (CLI, API, Cursor Chat) for different use cases
- **Extensible Architecture**: Modular design allows easy addition of new features
- **Commercial-Ready**: Dual licensing model supports both open source and commercial use

**Perfect for:**
- Building internal knowledge bases
- Document Q&A systems
- Research and analysis tools
- Customer support automation
- Content discovery platforms

---

## Upgrade Guide

### From Community to Professional
1. Obtain commercial license key
2. Update environment configuration
3. Enable hybrid search features
4. Configure reranking services
5. Access advanced analytics

### From 0.0.1 to 0.1.0
This is the first functional release. Previous version was repository setup only.
1. Follow installation guide in README.md
2. Set up environment variables
3. Run ingestion and indexing
4. Start using CLI, API, or Cursor Chat

---

## Breaking Changes

### v0.1.0
- Initial release - no breaking changes

---

## Security Updates

### v0.1.0
- Implemented secure API key handling
- Added input validation and sanitization
- Included security scanning in CI/CD
- Followed secure coding practices

---

## Performance Improvements

### v0.1.0
- Efficient batch processing for embeddings
- Optimized hybrid search merging algorithm
- Lazy loading of heavy dependencies
- Configurable chunk sizes and overlap

---

## Bug Fixes

### v0.1.0
- Initial release - no bug fixes yet

---

## Deprecations

### v0.1.0
- No deprecations in initial release

---

## Acknowledgments

Special thanks to:
- The open source community for inspiration
- OpenAI for powerful embeddings and LLM APIs
- Pinecone for scalable vector search
- Typesense for fast keyword search
- The Python ecosystem for excellent libraries

---

*For detailed technical changes, see the [commit history](https://github.com/doshirush1901/Vectorpenter/commits/main).*
