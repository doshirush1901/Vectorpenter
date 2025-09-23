# Contributing to Vectorpenter

Welcome to Vectorpenter! 🔨 We're excited that you want to contribute to "The carpenter of context — building vectors into memory."

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Project Structure](#project-structure)
- [Release Process](#release-process)
- [Getting Help](#getting-help)

## Code of Conduct

This project follows a simple code of conduct:
- **Be respectful** and constructive in all interactions
- **Be inclusive** and welcoming to contributors of all backgrounds
- **Focus on what's best** for the community and the project
- **Show empathy** towards other community members

## Getting Started

### Prerequisites

- **Python ≥ 3.10**
- **Git** for version control
- **API Keys** for testing (OpenAI, Pinecone, optionally Voyage/Cohere/Typesense)

### First Time Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Vectorpenter.git
   cd Vectorpenter
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/doshirush1901/Vectorpenter.git
   ```
4. **Create a development environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

## Development Setup

### Development Dependencies

Install additional development tools:

```bash
pip install black isort flake8 mypy pytest pytest-cov
```

### IDE Setup

**For VS Code/Cursor:**
- Install Python extension
- Set Python interpreter to your virtual environment
- Enable format on save with Black

**For PyCharm:**
- Configure Python interpreter
- Enable Black as external tool
- Set up pytest as test runner

## Making Changes

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: New features (`feature/hybrid-search-improvements`)
- **bugfix/**: Bug fixes (`bugfix/typesense-connection-error`)
- **hotfix/**: Critical fixes for production

### Workflow

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our [coding standards](#coding-standards)

3. **Test your changes**:
   ```bash
   python tests/smoke_test.py
   pytest tests/ -v
   ```

4. **Format your code**:
   ```bash
   black .
   isort .
   flake8 .
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add hybrid search improvements

   - Improved round-robin merging algorithm
   - Added better error handling for Typesense
   - Updated documentation
   
   Fixes #123"
   ```

6. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Testing

### Test Types

1. **Smoke Tests**: Basic import and functionality tests
   ```bash
   python tests/smoke_test.py
   ```

2. **Unit Tests**: Component-specific tests
   ```bash
   pytest tests/unit/ -v
   ```

3. **Integration Tests**: End-to-end workflow tests
   ```bash
   pytest tests/integration/ -v
   ```

4. **Manual Testing**: Test CLI and API manually
   ```bash
   # Test CLI
   python -m apps.cli --help
   python -m apps.cli ingest ./data/inputs
   
   # Test API
   uvicorn apps.api:app --reload
   # Test endpoints with curl or Postman
   
   # Test Cursor Chat
   python -m apps.cursor_chat
   ```

### Writing Tests

- Place tests in appropriate `tests/` subdirectories
- Use descriptive test names: `test_hybrid_search_merges_results_correctly`
- Mock external services (OpenAI, Pinecone, Typesense)
- Test both success and error cases
- Include docstrings for complex test cases

Example test:
```python
def test_hybrid_merge_deduplicates_results():
    """Test that hybrid_merge removes duplicate chunk IDs."""
    keyword_results = [{"id": "chunk1", "score": 0.8}]
    vector_results = [{"id": "chunk1", "score": 0.9}, {"id": "chunk2", "score": 0.7}]
    
    merged = hybrid_merge(keyword_results, vector_results, k=5)
    
    assert len(merged) == 2
    assert merged[0]["id"] == "chunk1"
    assert merged[1]["id"] == "chunk2"
```

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Code is formatted with Black and isort
- [ ] No linting errors from flake8
- [ ] Documentation is updated if needed
- [ ] CHANGELOG.md is updated (for significant changes)

### PR Guidelines

1. **Use descriptive titles**: `feat: add Cohere reranking support`
2. **Fill out the PR template** completely
3. **Link related issues**: `Fixes #123` or `Relates to #456`
4. **Keep PRs focused**: One feature or fix per PR
5. **Update documentation** as needed
6. **Add tests** for new functionality

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Manual testing** for significant changes
4. **Documentation review** if docs are updated
5. **Final approval** and merge by maintainer

## Coding Standards

### Python Style

- **PEP 8** compliance (enforced by flake8)
- **Black** for code formatting (88 character line limit)
- **isort** for import sorting
- **Type hints** for function signatures
- **Docstrings** for all public functions and classes

### Code Organization

```python
"""Module docstring describing purpose."""

from __future__ import annotations  # For forward references
import standard_library_imports
import third_party_imports
from local_imports import something

# Constants at module level
DEFAULT_TIMEOUT = 30

class ExampleClass:
    """Class docstring with purpose and usage examples."""
    
    def __init__(self, param: str):
        self.param = param
    
    def public_method(self, arg: int) -> str:
        """Public method with clear docstring."""
        return self._private_method(arg)
    
    def _private_method(self, arg: int) -> str:
        """Private method (single underscore prefix)."""
        return f"{self.param}: {arg}"

def utility_function(param: str, optional: bool = False) -> dict:
    """Utility function with type hints and docstring."""
    return {"param": param, "optional": optional}
```

### Error Handling

```python
# Good: Specific exception handling with logging
try:
    result = external_api_call()
except APITimeoutError as e:
    logger.warning(f"API timeout: {e}")
    return default_value
except APIError as e:
    logger.error(f"API error: {e}")
    raise ProcessingError(f"Failed to process request: {e}")

# Good: Input validation
def process_query(query: str, k: int = 12) -> List[Dict]:
    if not query.strip():
        raise ValueError("Query cannot be empty")
    if k <= 0:
        raise ValueError("k must be positive")
    # ... process query
```

### Logging

```python
from core.logging import logger

# Use appropriate log levels
logger.debug("Detailed debugging information")
logger.info("General information about program execution")
logger.warning("Something unexpected happened, but we can continue")
logger.error("A serious error occurred")
logger.critical("A critical error that may cause the program to abort")

# Include context in log messages
logger.info(f"Processing {len(documents)} documents")
logger.warning(f"Typesense unavailable, falling back to vector-only search")
```

## Project Structure

Understanding the codebase architecture:

```
vectorpenter/
├── apps/                   # Application entry points
│   ├── cli.py             # Command-line interface
│   ├── api.py             # FastAPI web server
│   └── cursor_chat.py     # Interactive REPL
├── core/                   # Core utilities and configuration
│   ├── config.py          # Environment configuration
│   ├── logging.py         # Logging setup
│   └── schemas.py         # Pydantic models
├── ingest/                 # Document ingestion pipeline
│   ├── loaders.py         # File discovery and loading
│   ├── parsers.py         # Text extraction from various formats
│   ├── chunkers.py        # Text chunking strategies
│   └── pipeline.py        # Orchestration of ingestion process
├── index/                  # Vector indexing and embedding
│   ├── embedder.py        # OpenAI embeddings client
│   ├── pinecone_client.py # Pinecone vector database client
│   └── upsert.py          # Vector upserting logic
├── rag/                    # Retrieval-Augmented Generation
│   ├── retriever.py       # Vector similarity search
│   ├── reranker.py        # Result reranking (Voyage/Cohere)
│   ├── context_builder.py # Context assembly with citations
│   └── generator.py       # LLM answer generation
├── search/                 # Hybrid search functionality
│   ├── typesense_client.py # Keyword search engine
│   └── hybrid.py          # Vector + keyword search merging
├── state/                  # State management and persistence
│   ├── db.py              # SQLite database setup
│   └── memory.py          # Conversation memory utilities
└── tools/                  # Optional integrations
    ├── gmail.py           # Gmail ingestion (placeholder)
    ├── crawler.py         # Web crawling (placeholder)
    └── ocr.py             # OCR processing (placeholder)
```

### Key Design Principles

1. **Modularity**: Each module has a clear, single responsibility
2. **Dependency Injection**: Configuration and clients passed as parameters
3. **Error Resilience**: Graceful degradation when services unavailable
4. **Local-First**: No required cloud dependencies beyond APIs
5. **Extensibility**: Easy to add new file formats, search engines, LLMs

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create release PR** to main branch
4. **Tag release**: `git tag v0.2.0`
5. **Push tag**: `git push origin v0.2.0`
6. **GitHub Actions** will handle the rest (build, package, Docker image)

## Getting Help

### Documentation

- **README.md**: Quick start and basic usage
- **This file**: Contribution guidelines
- **Code comments**: Inline documentation
- **GitHub Issues**: Bug reports and feature requests

### Communication

- **GitHub Issues**: Bug reports, feature requests, questions
- **GitHub Discussions**: General discussion, ideas, help
- **Pull Request comments**: Code-specific discussions

### Maintainers

Current maintainers:
- **@doshirush1901**: Project lead and primary maintainer

### Response Times

- **Bug reports**: 1-3 business days
- **Feature requests**: 3-7 business days  
- **Pull requests**: 2-5 business days
- **Questions**: 1-2 business days

## Recognition

Contributors are recognized in:
- **GitHub contributors page**
- **Release notes** for significant contributions
- **CONTRIBUTORS.md** file (coming soon)

Thank you for contributing to Vectorpenter! 🎉

---

*This document is living and evolving. Please suggest improvements via issues or PRs.*
