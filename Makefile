.PHONY: install test lint format clean build publish docs help

help:
	@echo "Available commands:"
	@echo "  install      - Install the package in development mode"
	@echo "  install-dev  - Install the package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  build        - Build the package"
	@echo "  clean        - Clean build artifacts"
	@echo "  docs         - Build documentation"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=textfission --cov-report=html --cov-report=term-missing

test-fast:
	pytest tests/ -v -x --tb=short

lint:
	@echo "Running flake8..."
	flake8 textfission/ tests/
	@echo "Running mypy..."
	mypy textfission/
	@echo "Running black check..."
	black --check textfission/ tests/
	@echo "Running isort check..."
	isort --check-only textfission/ tests/
	@echo "All linting checks passed!"

format:
	@echo "Formatting code with black..."
	black textfission/ tests/
	@echo "Sorting imports with isort..."
	isort textfission/ tests/
	@echo "Code formatting complete!"

build:
	python -m build

publish:
	python -m twine upload dist/*

docs:
	@echo "Building documentation..."
	# Add documentation build commands here when docs are added

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .tox/
	rm -rf .hypothesis/
	rm -rf logs/
	rm -rf output/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@echo "Cleanup complete!"

check-all: lint test
	@echo "All checks passed!"

pre-commit: format lint test
	@echo "Pre-commit checks completed successfully!" 