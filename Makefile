# ZhuchkaKeyboards Makefile
# Commands for development, testing, and deployment

.PHONY: help dev monitoring test test-unit test-integration test-performance test-rps test-all-methods-rps test-rps-benchmarks test-metrics-performance load-test-data-small load-test-data-medium load-test-data-large load-test-data-stress generate-test-data clean build

# Default target
help:
	@echo "Available commands:"
	@echo "  dev              - Start development environment (postgres, redis, gateway)"
	@echo "  monitoring       - Start monitoring stack (prometheus, grafana, loki)"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests (no containers required)"
	@echo "  test-integration - Run integration tests (requires containers)"
	@echo "  test-performance - Run all performance tests"
	@echo "  test-rps         - Run high RPS performance tests"
	@echo "  test-all-methods-rps - Run RPS tests for all API methods"
	@echo "  test-rps-benchmarks - Run comprehensive RPS benchmarks"
	@echo "  test-metrics-performance - Run metrics performance tests"
	@echo "  load-test-data-small - Load small test dataset into API"
	@echo "  load-test-data-medium - Load medium test dataset into API"
	@echo "  load-test-data-large - Load large test dataset into API"
	@echo "  generate-test-data - Generate realistic test data files"
	@echo "  build            - Build all containers"
	@echo "  clean            - Stop and remove all containers"
	@echo "  migrate          - Run database migrations"
	@echo "  logs             - Show gateway logs"
	@echo "  shell            - Open shell in gateway container"

# Development environment
dev:
	@echo "🚀 Starting development environment..."
	docker-compose up -d db redis gateway
	@echo "✅ Development environment is running!"
	@echo "   - Gateway API: http://localhost:8001"
	@echo "   - Health check: http://localhost:8001/api/health"
	@echo "   - API docs: http://localhost:8001/docs"

# Monitoring stack
monitoring:
	@echo "📊 Starting monitoring stack..."
	docker-compose --profile monitoring up -d
	@echo "✅ Monitoring stack is running!"
	@echo "   - Grafana: http://localhost:3000 (admin/admin123)"
	@echo "   - Prometheus: http://localhost:9090"
	@echo "   - Loki: http://localhost:3100"

# Database migrations
migrate:
	@echo "🗄️ Running database migrations..."
	docker-compose --profile migrate up

# Testing commands
test: test-unit test-integration
	@echo "✅ All tests completed!"

test-unit:
	@echo "🧪 Running unit tests (no containers required)..."
	pytest tests/unit/ -m unit -v --tb=short
	@echo "✅ Unit tests completed!"

test-integration:
	@echo "🔗 Running integration tests (requires containers)..."
	@echo "⚠️  Make sure containers are running: make dev"
	pytest tests/integration/ -m integration -v --tb=short
	@echo "✅ Integration tests completed!"

test-performance:
	@echo "⚡ Running performance tests..."
	@echo "⚠️  Make sure containers are running: make dev"
	pytest tests/performance/ -m performance -v --tb=short -s
	@echo "✅ Performance tests completed!"

test-rps:
	@echo "🚀 Running high RPS tests..."
	@echo "⚠️  Make sure containers are running: make dev"
	pytest tests/performance/test_high_rps.py -m performance -v --tb=short -s
	@echo "✅ RPS tests completed!"

test-all-methods-rps:
	@echo "🔥 Running RPS tests for all API methods..."
	@echo "⚠️  Make sure containers are running: make dev"
	pytest tests/performance/test_all_methods_rps.py -m performance -v --tb=short -s
	@echo "✅ All methods RPS tests completed!"

test-rps-benchmarks:
	@echo "📊 Running comprehensive RPS benchmarks..."
	@echo "⚠️  Make sure containers are running: make dev"
	pytest tests/performance/test_rps_benchmarks.py -m performance -v --tb=short -s
	@echo "✅ RPS benchmarks completed!"

test-metrics-performance:
	@echo "📈 Running metrics performance tests..."
	@echo "⚠️  Make sure containers are running: make dev"
	pytest tests/performance/test_metrics_load.py -m performance -v --tb=short -s
	@echo "✅ Metrics performance tests completed!"

# Test data loading commands
load-test-data-small:
	@echo "🏭 Loading small test dataset into API..."
	@echo "⚠️  Make sure containers are running: make dev"
	python tests/performance/load_test_data.py --size small
	@echo "✅ Small dataset loaded!"

load-test-data-medium:
	@echo "🏭 Loading medium test dataset into API..."
	@echo "⚠️  Make sure containers are running: make dev"
	python tests/performance/load_test_data.py --size medium
	@echo "✅ Medium dataset loaded!"

load-test-data-large:
	@echo "🏭 Loading large test dataset into API..."
	@echo "⚠️  Make sure containers are running: make dev"
	python tests/performance/load_test_data.py --size large
	@echo "✅ Large dataset loaded!"

load-test-data-stress:
	@echo "💥 Stress testing data loading into API..."
	@echo "⚠️  Make sure containers are running: make dev"
	python tests/performance/load_test_data.py --size stress
	@echo "✅ Stress loading completed!"

# Generate test data files
generate-test-data:
	@echo "📦 Generating realistic test data files..."
	python tests/performance/data_generators.py
	@echo "✅ Test data files generated!"

# Quick test commands
test-quick:
	@echo "⚡ Running quick test suite..."
	pytest tests/unit/ -m unit -x -q
	@echo "✅ Quick tests completed!"

test-inventory-unit:
	@echo "🧪 Running inventory unit tests..."
	pytest tests/unit/test_inventory_api.py -v

test-inventory-integration:
	@echo "🔗 Running inventory integration tests..."
	pytest tests/integration/test_inventory_full.py -v

# Container management
build:
	@echo "🏗️ Building all containers..."
	docker-compose build

clean:
	@echo "🧹 Cleaning up containers..."
	docker-compose down --volumes --remove-orphans
	docker-compose --profile monitoring down --volumes --remove-orphans
	@echo "✅ Cleanup completed!"

# Utility commands
logs:
	@echo "📋 Showing gateway logs..."
	docker-compose logs -f gateway

logs-all:
	@echo "📋 Showing all logs..."
	docker-compose logs -f

shell:
	@echo "🐚 Opening shell in gateway container..."
	docker-compose exec gateway sh

shell-db:
	@echo "🗄️ Opening database shell..."
	docker-compose exec db psql -U zhuchechka -d zhuchka

# Health checks
health:
	@echo "🏥 Checking service health..."
	@echo "Gateway:"
	@curl -s http://localhost:8001/api/health | jq . || echo "Gateway not responding"
	@echo "\nPrometheus:"
	@curl -s http://localhost:9090/-/ready || echo "Prometheus not responding"
	@echo "\nGrafana:"
	@curl -s http://localhost:3000/api/health | jq . || echo "Grafana not responding"

# Development helpers
dev-setup: build dev migrate
	@echo "🎉 Development environment is ready!"
	@echo "   Run 'make health' to check all services"
	@echo "   Run 'make test-unit' to run unit tests"
	@echo "   Run 'make monitoring' to start monitoring"

# Install development dependencies (for local testing)
install-deps:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-asyncio httpx

# Code quality
lint:
	@echo "🔍 Running linters..."
	flake8 gateway/src/ tests/ || echo "flake8 not installed"
	black --check gateway/src/ tests/ || echo "black not installed"

format:
	@echo "🎨 Formatting code..."
	black gateway/src/ tests/ || echo "black not installed"
	isort gateway/src/ tests/ || echo "isort not installed"

# Database utilities
db-reset:
	@echo "🗄️ Resetting database..."
	docker-compose down db
	docker volume rm zhuchkakeyboards_postgres_data || true
	docker-compose up -d db
	sleep 5
	make migrate
	@echo "✅ Database reset completed!"

# Backup and restore
backup:
	@echo "💾 Creating database backup..."
	docker-compose exec -T db pg_dump -U zhuchechka zhuchka > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created!"

# Example data
load-example-data:
	@echo "📊 Loading example data..."
	pytest tests/integration/test_inventory_full.py::TestInventoryIntegration::test_complete_warehouse_lifecycle -v
	@echo "✅ Example data loaded!"