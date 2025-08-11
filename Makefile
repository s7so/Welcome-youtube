.PHONY: help test test-unit test-integration test-api test-sync test-bulk test-coverage test-docker clean

# Default target
help:
	@echo "Available commands:"
	@echo "  test              - Run all tests"
	@echo "  test-unit         - Run unit tests only"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-api          - Run API tests only"
	@echo "  test-sync         - Run sync tests only"
	@echo "  test-bulk         - Run bulk upload tests only"
	@echo "  test-coverage     - Run tests with coverage"
	@echo "  test-docker       - Run tests using Docker"
	@echo "  test-docker-unit  - Run unit tests using Docker"
	@echo "  test-docker-int   - Run integration tests using Docker"
	@echo "  test-docker-cov   - Run tests with coverage using Docker"
	@echo "  setup-test-env    - Setup test environment only"
	@echo "  clean             - Clean up test artifacts"
	@echo "  clean-docker      - Clean up Docker test containers"

# Local test commands (requires local PostgreSQL)
test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-api:
	pytest -m api

test-sync:
	pytest -m sync

test-bulk:
	pytest -m bulk_upload

test-coverage:
	pytest --cov=apps --cov-report=html --cov-report=term

# Docker test commands
test-docker:
	./scripts/run-tests.sh

test-docker-unit:
	./scripts/run-tests.sh -u

test-docker-int:
	./scripts/run-tests.sh -i

test-docker-api:
	./scripts/run-tests.sh -a

test-docker-sync:
	./scripts/run-tests.sh -s

test-docker-bulk:
	./scripts/run-tests.sh -b

test-docker-cov:
	./scripts/run-tests.sh -c

setup-test-env:
	./scripts/run-tests.sh --setup

# Cleanup commands
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-docker:
	docker-compose -f docker-compose.test.yml down -v
	docker system prune -f

# Development helpers
install-dev:
	pip install -r requirements-dev.txt

install-all:
	pip install -r requirements.txt -r requirements-dev.txt

migrate:
	python manage.py migrate

migrate-test:
	DATABASE_URL=postgresql+psycopg://atlas_test:atlas_test@localhost:5433/atlas_test python manage.py migrate

shell:
	python manage.py shell

shell-test:
	DATABASE_URL=postgresql+psycopg://atlas_test:atlas_test@localhost:5433/atlas_test python manage.py shell

# Linting
lint:
	flake8 .

lint-fix:
	autopep8 --in-place --recursive --aggressive --aggressive apps/

# Quick checks
check:
	python manage.py check
	python manage.py makemigrations --check --dry-run

# Database operations
reset-db:
	python manage.py flush --no-input
	python manage.py seed_initial_data

reset-test-db:
	DATABASE_URL=postgresql+psycopg://atlas_test:atlas_test@localhost:5433/atlas_test python manage.py flush --no-input
	DATABASE_URL=postgresql+psycopg://atlas_test:atlas_test@localhost:5433/atlas_test python manage.py seed_initial_data