# OpenMetadata Migration Tool Makefile
# Provides common development and deployment tasks

.PHONY: help setup clean test export export-clean export-core import import-dry install dev-install lint format check-format type-check all-checks

# Default target
help:
	@echo "OpenMetadata Migration Tool"
	@echo "=========================="
	@echo ""
	@echo "Available commands:"
	@echo "  setup         - Set up virtual environment and install dependencies"
	@echo "  clean         - Clean up generated files and virtual environment"
	@echo "  install       - Install production dependencies"
	@echo "  dev-install   - Install development dependencies"
	@echo "  test          - Run test suite"
	@echo "  export        - Run export with default configuration"
	@echo "  export-clean  - Run clean export (clears existing exports)"
	@echo "  export-core   - Export core entities (domains, data_products, teams)"
	@echo "  import        - Run import with default configuration"
	@echo "  import-dry    - Run import in dry-run mode"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code with black"
	@echo "  check-format  - Check code formatting"
	@echo "  type-check    - Run type checking with mypy"
	@echo "  all-checks    - Run all code quality checks"
	@echo ""
	@echo "Development workflow:"
	@echo "  make setup         # Initial setup"
	@echo "  make test          # Run tests"
	@echo "  make export-clean  # Test clean export"
	@echo "  make export-core   # Export core entities only"

# Variables
VENV_NAME = omd_venv
PYTHON = $(VENV_NAME)/bin/python
PIP = $(VENV_NAME)/bin/pip
PYTEST = $(VENV_NAME)/bin/pytest

# Setup virtual environment and install everything
setup:
	@echo "🚀 Setting up development environment..."
	./setup.sh
	@echo "✅ Setup complete! Run 'source $(VENV_NAME)/bin/activate' to activate"

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	rm -rf $(VENV_NAME)/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf exports/
	rm -rf imports/
	rm -rf *.log
	rm -rf *.ndjson
	rm -rf export_summary.json
	rm -rf import_summary.json
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Cleanup complete!"

# Install production dependencies
install:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(PIP) install -r requirements.txt

# Install development dependencies
dev-install:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(PIP) install -r requirements-dev.txt

# Run tests
test:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🧪 Running tests..."
	$(PYTEST) test_migration.py -v

# Run export with default settings
export:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "📤 Running export..."
	$(PYTHON) export.py

# Run clean export (clears existing exports first)
export-clean:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "📤 Running clean export..."
	$(PYTHON) export.py --clear

# Export core entities only
export-core:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "📤 Exporting core entities (domains, data_products, teams)..."
	$(PYTHON) export.py --clear --entities domains --entities data_products --entities teams

# Run import with default settings  
import:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "📥 Running import..."
	$(PYTHON) import.py

# Run import in dry-run mode
import-dry:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "📥 Running import (dry-run)..."
	$(PYTHON) import.py --dry-run

# Lint code
lint:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🔍 Running linting..."
	$(VENV_NAME)/bin/flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	$(VENV_NAME)/bin/flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Format code with black
format:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🎨 Formatting code..."
	$(VENV_NAME)/bin/black *.py

# Check code formatting
check-format:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🎨 Checking code formatting..."
	$(VENV_NAME)/bin/black --check *.py

# Type checking
type-check:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "🔍 Running type checks..."
	$(VENV_NAME)/bin/mypy *.py --ignore-missing-imports

# Run all code quality checks
all-checks: lint check-format type-check test
	@echo "✅ All checks passed!"

# Quick development cycle
dev: clean setup test
	@echo "🎯 Development environment ready!"