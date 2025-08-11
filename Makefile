.PHONY: help test test-unit test-integration test-api test-sync test-bulk test-coverage test-docker clean frontend frontend-dev frontend-build frontend-watch

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "Backend Commands:"
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
	@echo ""
	@echo "Frontend Commands:"
	@echo "  frontend          - Install frontend dependencies"
	@echo "  frontend-dev      - Start frontend development server"
	@echo "  frontend-build    - Build frontend for production"
	@echo "  frontend-watch    - Watch frontend files for changes"
	@echo "  frontend-clean    - Clean frontend build files"
	@echo ""
	@echo "Development Commands:"
	@echo "  install-dev       - Install development dependencies"
	@echo "  install-all       - Install all dependencies"
	@echo "  migrate           - Run database migrations"
	@echo "  migrate-test      - Run test database migrations"
	@echo "  shell             - Open Django shell"
	@echo "  shell-test        - Open Django shell with test database"
	@echo "  lint              - Run code linting"
	@echo "  lint-fix          - Fix linting issues"
	@echo "  check             - Run Django checks"
	@echo "  reset-db          - Reset main database"
	@echo "  reset-test-db     - Reset test database"

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

# Frontend commands
frontend:
	@echo "Installing frontend dependencies..."
	npm install

frontend-dev:
	@echo "Starting frontend development server..."
	npm run dev

frontend-build:
	@echo "Building frontend for production..."
	npm run build

frontend-watch:
	@echo "Watching frontend files for changes..."
	npm run watch

frontend-clean:
	@echo "Cleaning frontend build files..."
	rm -f static/css/output.css
	rm -rf node_modules

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

# Full setup commands
setup-full:
	@echo "Setting up complete development environment..."
	make install-all
	make frontend
	make migrate
	make frontend-build
	@echo "Setup complete! Run 'python manage.py runserver' to start the development server."

setup-frontend:
	@echo "Setting up frontend environment..."
	make frontend
	make frontend-build
	@echo "Frontend setup complete!"

# Production commands
deploy-prepare:
	@echo "Preparing for deployment..."
	make frontend-build
	python manage.py collectstatic --noinput
	python manage.py migrate
	@echo "Deployment preparation complete!"

# Docker production commands
docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-build:
	docker compose build

# Utility commands
status:
	@echo "=== Atlas System Status ==="
	@echo "Python version: $(shell python --version)"
	@echo "Node version: $(shell node --version 2>/dev/null || echo 'Node.js not installed')"
	@echo "Docker version: $(shell docker --version 2>/dev/null || echo 'Docker not installed')"
	@echo "Database: $(shell python manage.py dbshell -c '\l' 2>/dev/null | grep atlas || echo 'Database not accessible')"
	@echo "Frontend build: $(shell test -f static/css/output.css && echo 'Built' || echo 'Not built')"

# Quick development server
dev:
	@echo "Starting development server..."
	python manage.py runserver

dev-with-frontend:
	@echo "Starting development server with frontend watching..."
	make frontend-watch &
	python manage.py runserver