.PHONY: help install test lint format security docker-build docker-run docker-stop clean

# Default target
help:
	@echo "🚀 ZhuchkaKeyboards CI/CD Commands"
	@echo ""
	@echo "📦 Setup:"
	@echo "  install          Install dependencies"
	@echo "  setup-db         Setup database and run migrations"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  lint             Run linting (flake8, mypy)"
	@echo "  format           Format code (black, isort)"
	@echo "  security         Run security checks"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-build     Build Docker images"
	@echo "  docker-run       Run all services"
	@echo "  docker-stop      Stop all services"
	@echo "  docker-clean     Clean Docker resources"
	@echo ""
	@echo "📊 Monitoring:"
	@echo "  monitoring       Start monitoring stack"
	@echo "  monitoring-stop  Stop monitoring stack"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean            Clean all temporary files"
	@echo "  ci               Run full CI pipeline locally"

# Setup
install:
	@echo "📦 Installing dependencies..."
	cd gateway && pip install -r requirements.txt
	cd gateway && pip install -r requirements-test.txt

setup-db:
	@echo "🗄️ Setting up database..."
	docker-compose up -d db redis
	sleep 10
	docker-compose --profile migrate run --rm migrations

# Testing
test: test-unit test-integration

test-unit:
	@echo "🧪 Running unit tests..."
	cd gateway && pytest tests/unit/ -v --cov=src --cov-report=term-missing

test-integration:
	@echo "🔗 Running integration tests..."
	cd gateway && pytest tests/integration/ -v

test-performance:
	@echo "⚡ Running performance tests..."
	cd tests/performance && python test_simple_rps.py
	cd tests/performance && python test_high_rps.py

# Code Quality
lint:
	@echo "🔍 Running linting..."
	cd gateway && flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
	cd gateway && flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	cd gateway && mypy src/

format:
	@echo "🎨 Formatting code..."
	cd gateway && black src/ --line-length=127
	cd gateway && isort src/ --profile=black

security:
	@echo "🔒 Running security checks..."
	cd gateway && bandit -r src/ -f json -o bandit-report.json || true
	cd gateway && safety check --json --output safety-report.json || true

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-run:
	@echo "🚀 Starting all services..."
	docker-compose up -d

docker-stop:
	@echo "🛑 Stopping all services..."
	docker-compose down

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Monitoring
monitoring:
	@echo "📊 Starting monitoring stack..."
	docker-compose --profile monitoring up -d

monitoring-stop:
	@echo "🛑 Stopping monitoring stack..."
	docker-compose --profile monitoring down

# Maintenance
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +

# Full CI pipeline
ci: install lint test security docker-build
	@echo "✅ CI pipeline completed successfully!"

# Development helpers
dev-setup: install setup-db monitoring
	@echo "🎉 Development environment ready!"
	@echo "📊 Grafana: http://localhost:3000 (admin/admin123)"
	@echo "📈 Prometheus: http://localhost:9090"
	@echo "🔍 Gateway: http://localhost:8001"

dev-stop: docker-stop monitoring-stop
	@echo "🛑 Development environment stopped"