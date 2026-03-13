.PHONY: up down build migrate test lint shell-backend shell-frontend logs

# ---------------------------------------------------------------------------
# Docker Compose
# ---------------------------------------------------------------------------

up: ## Start all services in detached mode
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build (or rebuild) all service images
	docker compose build

logs: ## Tail logs for all services
	docker compose logs -f

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

migrate: ## Run Alembic migrations to head
	docker compose exec backend alembic upgrade head

migration: ## Create a new auto-generated migration (usage: make migration m="add users table")
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test: ## Run all backend and frontend tests
	docker compose exec backend pytest -v
	docker compose exec frontend npm test

test-backend: ## Run backend tests only
	docker compose exec backend pytest -v

test-frontend: ## Run frontend tests only
	docker compose exec frontend npm test

# ---------------------------------------------------------------------------
# Linting & Formatting
# ---------------------------------------------------------------------------

lint: ## Run linters on backend and frontend
	docker compose exec backend ruff check app/ tests/
	docker compose exec backend ruff format --check app/ tests/
	docker compose exec frontend npm run lint

format: ## Auto-format backend and frontend code
	docker compose exec backend ruff format app/ tests/
	docker compose exec frontend npm run lint -- --fix

# ---------------------------------------------------------------------------
# Interactive Shells
# ---------------------------------------------------------------------------

shell-backend: ## Open a bash shell in the backend container
	docker compose exec backend bash

shell-frontend: ## Open a shell in the frontend container
	docker compose exec frontend sh

shell-db: ## Open psql in the postgres container
	docker compose exec postgres psql -U $${POSTGRES_USER:-migrantsbridge} -d $${POSTGRES_DB:-migrantsbridge}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

seed: ## Run database seed script
	docker compose exec backend python -m app.scripts.seed

reset-db: ## Drop and recreate the database, then migrate
	docker compose down -v
	docker compose up -d postgres redis
	@echo "Waiting for postgres..."
	@sleep 5
	docker compose up -d backend
	@sleep 10
	docker compose exec backend alembic upgrade head

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
