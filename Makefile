# Vectorpenter Development Makefile
# The carpenter of context — building vectors into memory

.PHONY: help install install-dev test test-unit test-integration test-e2e lint format type-check security-scan clean build docs serve-docs

# Default target
help:
	@echo "🔨 Vectorpenter Development Commands"
	@echo ""
	@echo "📦 Installation:"
	@echo "  make install      Install production dependencies"
	@echo "  make install-dev  Install development dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test         Run all tests"
	@echo "  make test-unit    Run unit tests only"
	@echo "  make test-integration  Run integration tests"
	@echo "  make test-e2e     Run end-to-end tests"
	@echo "  make test-cov     Run tests with coverage report"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  make lint         Run all linting checks"
	@echo "  make format       Format code with black and isort"
	@echo "  make type-check   Run type checking with mypy"
	@echo "  make security-scan Run security scans"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make clean        Clean build artifacts"
	@echo "  make build        Build package"
	@echo "  make serve-api    Start development API server"
	@echo "  make serve-chat   Start Cursor chat REPL"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  make docs         Build documentation"
	@echo "  make serve-docs   Serve documentation locally"

# Installation targets
install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt
	pre-commit install

# Testing targets
test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v --tb=short

test-cov:
	pytest tests/ --cov=vectorpenter --cov-report=html --cov-report=term-missing

test-smoke:
	python tests/smoke_test.py

# Code quality targets
lint: lint-flake8 lint-mypy lint-bandit

lint-flake8:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

lint-mypy:
	mypy . --ignore-missing-imports --no-strict-optional

lint-bandit:
	bandit -r . -f json -o bandit-report.json || true
	bandit -r . -ll

format:
	black .
	isort .

format-check:
	black --check --diff .
	isort --check-only --diff .

type-check:
	mypy . --ignore-missing-imports

security-scan: lint-bandit
	safety check --json --output safety-report.json || true
	safety check --short-report

# Development targets
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -f bandit-report.json safety-report.json

build: clean
	python -m build

serve-api:
	uvicorn apps.api:app --reload --host 0.0.0.0 --port 8000

serve-chat:
	python -m apps.cursor_chat

# Documentation targets
docs:
	@echo "📚 Building documentation..."
	@echo "README.md, CONTRIBUTING.md, and other docs are already available"
	@echo "For API docs, start the server and visit: http://localhost:8000/docs"

serve-docs: serve-api
	@echo "📚 API documentation available at: http://localhost:8000/docs"

# Development workflow targets
dev-setup: install-dev
	@echo "🔨 Setting up development environment..."
	cp env.example .env
	@echo "✅ Development setup complete!"
	@echo "📝 Next steps:"
	@echo "  1. Edit .env with your API keys"
	@echo "  2. Run 'make test-smoke' to verify setup"
	@echo "  3. Run 'make serve-chat' to start developing"

quick-test: format-check lint-flake8 test-unit
	@echo "✅ Quick development checks passed!"

full-check: format-check lint type-check security-scan test
	@echo "✅ Full quality checks passed!"

# CI targets (used by GitHub Actions)
ci-install:
	pip install --upgrade pip
	pip install -r requirements.txt -r requirements-dev.txt

ci-test: test-cov
	@echo "✅ CI tests completed"

ci-quality: format-check lint type-check security-scan
	@echo "✅ CI quality checks completed"

# Release targets
pre-release: full-check
	@echo "🚀 Pre-release checks completed successfully"
	@echo "Ready for release!"

# Docker targets
docker-build:
	docker build -t vectorpenter:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env vectorpenter:latest

# Local services
up:
	docker compose up -d typesense
	@echo "✅ Typesense started on http://localhost:8108"
	@echo "💡 Set TYPESENSE_API_KEY=xyz in .env to connect"

up-all:
	docker compose up -d
	@echo "✅ All services started:"
	@echo "  • Typesense: http://localhost:8108"
	@echo "  • PostgreSQL: localhost:5432"
	@echo "  • Redis: localhost:6379"

down:
	docker compose down
	@echo "✅ All services stopped"

logs:
	docker compose logs -f

# Quick development workflow with services
dev-full: up dev-setup
	@echo "🚀 Full development environment ready!"
	@echo "  • Services running"
	@echo "  • Dependencies installed"
	@echo "  • Environment configured"

# Utility targets
check-deps:
	pip list --outdated

update-deps:
	pip-review --local --interactive

count-lines:
	find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./build/*" -not -path "./dist/*" | xargs wc -l

# Performance benchmarks
benchmark:
	python -m pytest tests/e2e/test_complete_workflow.py::TestPerformanceWorkflow -v

# Evaluation
eval:
	python apps/eval.py --eval-file data/eval/questions.json
	@echo "✅ Evaluation completed"

eval-hybrid:
	python apps/eval.py --eval-file data/eval/questions.json --hybrid
	@echo "✅ Hybrid evaluation completed"

eval-full:
	python apps/eval.py --eval-file data/eval/questions.json --output results/eval_vector.json
	python apps/eval.py --eval-file data/eval/questions.json --hybrid --output results/eval_hybrid.json
	@echo "✅ Full evaluation completed - check results/ directory"

# Data management
create-sample-data:
	mkdir -p data/inputs
	echo "This is a sample document for testing Vectorpenter." > data/inputs/sample.txt
	echo "# Sample Markdown\n\nThis is a sample markdown document." > data/inputs/sample.md

# Environment management
check-env:
	python -c "from core.validation import validate_environment; import json; print(json.dumps(validate_environment(), indent=2))"

# Cache management
clear-cache:
	rm -rf data/cache/*
	@echo "✅ Cache cleared"

# Quick development cycle
dev: format lint-flake8 test-unit
	@echo "✅ Development cycle complete"

# Production readiness check
production-check: full-check
	python -c "from core.validation import startup_validation; assert startup_validation(), 'Startup validation failed'"
	@echo "✅ Production readiness verified"
