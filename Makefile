# Run all steps: linting, formatting, and testing
all: lint format test

# Linting target
lint:
	flake8 olympics_data_project/data_cleaning/*.py

# Formatting target
format:
	black olympics_data_project/data_cleaning/*.py

# Testing target
test:
	pytest *

# Clean up unnecessary files (e.g., cache)
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

# Show help
help:
	@echo "make all      - Run linting, formatting, and testing"
	@echo "make lint     - Run linting only"
	@echo "make format   - Run formatting only"
	@echo "make test     - Run tests only"
	@echo "make clean    - Clean up __pycache__ folders"
