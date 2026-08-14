.PHONY: run dev test lint format migrate upgrade downgrade help

# ─── Dev Server ──────────────────────────────────────────────────────────────────
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# ─── Database Migrations ──────────────────────────────────────────────────────────
migrate:
	alembic upgrade head

downgrade:
	alembic downgrade -1

revision:
	alembic revision --autogenerate -m "$(msg)"

# ─── Testing ──────────────────────────────────────────────────────────────────────
test:
	pytest tests/unit tests/api -v --cov=app --cov-report=term-missing

test-all:
	pytest -v --cov=app --cov-report=term-missing

test-unit:
	pytest tests/unit -v

test-api:
	pytest tests/api -v

test-integration:
	pytest tests/integration -v -s

# ─── Code Quality ─────────────────────────────────────────────────────────────────
lint:
	ruff check app/ cli/ tests/ scripts/
	mypy app/ cli/

format:
	black app/ cli/ tests/ scripts/
	ruff check --fix app/ cli/ tests/ scripts/

# ─── Setup ────────────────────────────────────────────────────────────────────────
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

models:
	bash scripts/download_models.sh

# ─── Benchmark ────────────────────────────────────────────────────────────────────
benchmark:
	python scripts/benchmark.py

# ─── Docker ───────────────────────────────────────────────────────────────────────
docker-build:
	docker build -f deploy/docker/Dockerfile -t video-dubbing-system:latest .

docker-up:
	docker-compose -f deploy/docker/docker-compose.yml up -d

docker-down:
	docker-compose -f deploy/docker/docker-compose.yml down

# ─── Help ─────────────────────────────────────────────────────────────────────────
help:
	@echo "Available targets:"
	@echo "  run          Start production server"
	@echo "  dev          Start dev server with hot-reload"
	@echo "  migrate      Apply pending Alembic migrations"
	@echo "  test         Run unit + API tests with coverage"
	@echo "  test-all     Run full test suite"
	@echo "  lint         Run ruff + mypy"
	@echo "  format       Auto-format with black + ruff"
	@echo "  install      Install runtime deps"
	@echo "  install-dev  Install all deps including dev tools"
	@echo "  models       Download ML model weights"
	@echo "  benchmark    Run 30-min and 2-hr benchmark videos"
	@echo "  docker-build Build Docker image"
	@echo "  docker-up    Start Docker Compose services"
