.PHONY: help install update run dev test clean fmt lint type check docker-build docker-up docker-down docker-logs migrate migrate-create db-upgrade db-downgrade pre-commit docker-shell

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

## help: Show this help message
help:
	@echo "$(BLUE)FastAPI Web Shop - Available Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make install        - Install/sync dependencies with uv"
	@echo "  make update         - Update all dependencies to latest versions"
	@echo "  make run            - Run development server with auto-reload"
	@echo "  make dev            - Alias for run"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  make fmt            - Format code with ruff and black"
	@echo "  make lint           - Run ruff linter"
	@echo "  make type           - Run mypy type checker (non-blocking)"
	@echo "  make type-strict    - Run mypy type checker (strict mode)"
	@echo "  make check          - Run all checks (fmt + lint + type)"
	@echo "  make pre-commit     - Run pre-commit hooks on all files"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test           - Run all tests with pytest"
	@echo "  make test-v         - Run tests with verbose output"
	@echo "  make test-cov       - Run tests with coverage report"
	@echo "  make test-watch     - Run tests in watch mode"
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@echo "  make migrate        - Create and apply new migration"
	@echo "  make migrate-create - Create new migration without applying"
	@echo "  make db-upgrade     - Apply all pending migrations"
	@echo "  make db-downgrade   - Rollback last migration"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-up      - Start containers in background"
	@echo "  make docker-down    - Stop and remove containers"
	@echo "  make docker-logs    - View container logs"
	@echo "  make docker-shell   - Open shell in app container"
	@echo "  make docker-restart - Restart containers"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean          - Remove cache and temporary files"
	@echo "  make clean-all      - Remove cache, venv, and docker volumes"
	@echo ""

## install: Install/sync dependencies
install:
	@echo "$(GREEN)==> Installing dependencies...$(NC)"
	uv sync

## update: Update all dependencies
update:
	@echo "$(YELLOW)==> Updating dependencies...$(NC)"
	uv lock --upgrade
	uv sync
	@echo "$(GREEN)Done! Check uv.lock for changes$(NC)"

## run: Start development server
run:
	@echo "$(GREEN)==> Starting development server...$(NC)"
	@if [ -d "alembic" ] || [ -f "alembic.ini" ]; then \
		echo "$(BLUE)==> Applying migrations...$(NC)"; \
		uv run python -m alembic upgrade head || echo "$(YELLOW)Migration skipped$(NC)"; \
	fi
	uv run python main.py

## dev: Alias for run
dev: run

## fmt: Format code
fmt:
	@echo "$(GREEN)==> Formatting code...$(NC)"
	uv run ruff format .
	uv run black .
	@echo "$(GREEN)==> Fixing linting issues...$(NC)"
	uv run ruff check --fix .

## lint: Run linter
lint:
	@echo "$(GREEN)==> Running ruff linter...$(NC)"
	uv run ruff check .

## type: Run type checker (non-blocking)
type:
	@echo "$(GREEN)==> Running mypy type checker...$(NC)"
	@uv run mypy app main.py --explicit-package-bases || echo "$(YELLOW)⚠ Type check found issues (non-critical)$(NC)"

## type-strict: Run type checker (blocking on errors)
type-strict:
	@echo "$(GREEN)==> Running mypy type checker (strict)...$(NC)"
	uv run mypy app main.py --explicit-package-bases

## check: Run all checks
check: fmt lint type
	@echo "$(GREEN)==> All checks passed!$(NC)"

## pre-commit: Run pre-commit hooks
pre-commit:
	@echo "$(GREEN)==> Running pre-commit hooks...$(NC)"
	uv run pre-commit run --all-files

## test: Run tests
test:
	@echo "$(GREEN)==> Running tests...$(NC)"
	@if [ ! -d "tests" ]; then \
		echo "$(RED)Error: tests/ directory not found$(NC)"; \
		echo "$(BLUE)Create it with: ./dev.sh init-tests$(NC)"; \
		exit 1; \
	fi
	uv run pytest -v --tb=short

## test-v: Run tests with verbose output
test-v:
	@echo "$(GREEN)==> Running tests (verbose)...$(NC)"
	uv run pytest -vv

## test-cov: Run tests with coverage
test-cov:
	@echo "$(GREEN)==> Running tests with coverage...$(NC)"
	uv run pytest --cov=app --cov-report=html --cov-report=term

## test-watch: Run tests in watch mode
test-watch:
	@echo "$(GREEN)==> Running tests in watch mode...$(NC)"
	uv run pytest-watch

## migrate: Create and apply migration
migrate:
	@read -p "Enter migration message: " msg; \
	if [ -z "$$msg" ]; then \
		echo "$(RED)Error: Migration message cannot be empty$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)==> Creating migration: $$msg$(NC)"; \
	uv run python -m alembic revision --autogenerate -m "$$msg"; \
	echo "$(GREEN)==> Applying migration...$(NC)"; \
	uv run python -m alembic upgrade head

## migrate-create: Create migration without applying
migrate-create:
	@read -p "Enter migration message: " msg; \
	if [ -z "$$msg" ]; then \
		echo "$(RED)Error: Migration message cannot be empty$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)==> Creating migration: $$msg$(NC)"; \
	uv run python -m alembic revision --autogenerate -m "$$msg"

## db-upgrade: Apply all pending migrations
db-upgrade:
	@echo "$(GREEN)==> Applying migrations...$(NC)"
	uv run python -m alembic upgrade head

## db-downgrade: Rollback last migration
db-downgrade:
	@echo "$(YELLOW)==> Rolling back last migration...$(NC)"
	uv run python -m alembic downgrade -1

## docker-build: Build Docker image
docker-build:
	@echo "$(GREEN)==> Building Docker image...$(NC)"
	docker build -t web-shop-fastapi .

## docker-up: Start containers
docker-up:
	@echo "$(GREEN)==> Starting containers...$(NC)"
	docker compose up -d
	@echo "$(GREEN)==> Containers started!$(NC)"

## docker-down: Stop containers
docker-down:
	@echo "$(YELLOW)==> Stopping containers...$(NC)"
	docker compose down

## docker-logs: View container logs
docker-logs:
	@echo "$(BLUE)==> Container logs (Ctrl+C to exit):$(NC)"
	docker compose logs -f

## docker-shell: Open shell in container
docker-shell:
	@echo "$(GREEN)==> Opening shell in app container...$(NC)"
	docker compose exec app /bin/bash

## docker-restart: Restart containers
docker-restart: docker-down docker-up

## clean: Remove cache and temporary files
clean:
	@echo "$(YELLOW)==> Cleaning cache and temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)==> Cleanup complete!$(NC)"

## clean-all: Remove everything including venv and docker volumes
clean-all: clean
	@echo "$(RED)==> Removing .venv and docker volumes...$(NC)"
	rm -rf .venv
	docker compose down -v 2>/dev/null || true
	@echo "$(GREEN)==> Deep cleanup complete!$(NC)"
