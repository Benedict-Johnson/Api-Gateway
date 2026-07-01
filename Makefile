.PHONY: help up down rebuild logs clean test benchmark lint format health

help: ## Display this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start Docker containers in background
	docker compose up -d

down: ## Stop and remove Docker containers
	docker compose down

rebuild: ## Rebuild and start Docker containers
	docker compose up -d --build

logs: ## Tail Docker container logs
	docker compose logs -f

clean: ## Remove Python cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

test: ## Run unit and regression test suite inside Docker container
	docker compose exec -T gateway pytest -v

benchmark: ## Run benchmark suite against running gateway
	node benchmarks/benchmark.js

lint: ## Check codebase quality with ruff
	python -m ruff check .

format: ## Standardize import ordering and format code with isort and black
	python -m isort .
	python -m black .

health: ## Check live API Gateway health status
	curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' || echo "Gateway unreachable"
