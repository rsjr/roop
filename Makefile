.PHONY: help install dev-install lint format test test-cov clean run docker-build docker-up docker-down migrate

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  lint         - Run linting (ruff + mypy)"
	@echo "  format       - Format code (ruff)"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  clean        - Clean cache and build files"
	@echo "  run          - Run the application locally"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up    - Start services with Docker Compose"
	@echo "  docker-down  - Stop Docker Compose services"
	@echo "  migrate      - Run database migrations"

install:
	uv sync --frozen

dev-install:
	uv sync --frozen --all-extras

lint:
	uv run ruff check .
	uv run mypy .

format:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run pytest

test-cov:
	uv run pytest --cov=app --cov-report=html --cov-report=term

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api

migrate:
	uv run alembic upgrade head

migrate-create:
	uv run alembic revision --autogenerate -m "$(msg)"

setup: dev-install
	cp .env.example .env
	uv run pre-commit install
	@echo "Setup complete! Please update .env with your configuration."