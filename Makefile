.PHONY: help epic story test lint format quality check clean
.DEFAULT_GOAL := help

# Virtual environment activation
VENV_ACTIVATE = source venv/bin/activate

# Get ticket argument (first argument after command)
TICKET := $(word 2, $(MAKECMDGOALS))

help: ## Show this help message
	@echo "Jirabot - Jira Download Scripts"
	@echo "Usage:"
	@echo "  make epic <TICKET>     Download epic and all issues"
	@echo "  make story <TICKET>    Download story and sub-tasks"
	@echo "  make test              Run test suite with coverage"
	@echo "  make lint              Run linting checks"
	@echo "  make format            Format code with black"
	@echo "  make quality           Run all quality checks"
	@echo "  make check             Run tests and quality checks"
	@echo "  make clean             Clean temporary files"
	@echo ""
	@echo "Examples:"
	@echo "  make epic ELIZA-1717"
	@echo "  make story ELIZA-1913"

epic: ## Download epic and all issues - Usage: make epic <TICKET>
	@if [ -z "$(TICKET)" ]; then \
		echo "Error: Please provide a ticket number"; \
		echo "Usage: make epic <TICKET>"; \
		echo "Example: make epic ELIZA-1717"; \
		exit 1; \
	fi
	@echo "Downloading epic $(TICKET)..."
	@$(VENV_ACTIVATE) && python scripts/download_epic_issues.py $(TICKET) -v

story: ## Download story and sub-tasks - Usage: make story <TICKET>
	@if [ -z "$(TICKET)" ]; then \
		echo "Error: Please provide a ticket number"; \
		echo "Usage: make story <TICKET>"; \
		echo "Example: make story ELIZA-1913"; \
		exit 1; \
	fi
	@echo "Downloading story $(TICKET)..."
	@$(VENV_ACTIVATE) && python scripts/download_story_subtasks.py $(TICKET) -v

test: ## Run test suite with coverage
	@echo "Running tests with coverage..."
	@$(VENV_ACTIVATE) && python -m pytest tests/ --cov=src --cov=scripts/download_story_subtasks --cov=scripts/download_epic_issues --cov-report=term-missing

lint: ## Run linting checks
	@echo "Running linting checks..."
	@$(VENV_ACTIVATE) && flake8 src tests scripts/*.py

format: ## Format code with black
	@echo "Formatting code..."
	@$(VENV_ACTIVATE) && black src tests scripts/*.py

type-check: ## Run type checking with mypy
	@echo "Running type checks..."
	@$(VENV_ACTIVATE) && mypy src scripts/*.py

quality: format lint type-check ## Run all code quality checks

check: test quality ## Run tests and quality checks

clean: ## Clean temporary files
	@echo "Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name ".coverage" -delete
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/

# Allow ticket arguments to be passed without errors
%:
	@:
