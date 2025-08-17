# ZhuchkaKeyboards - Makefile for project management

.PHONY: help build start stop restart logs migrate clean monitoring dev prod

# Default target
help:
	@echo "ZhuchkaKeyboards Management Commands:"
	@echo ""
	@echo "🛠️  Development:"
	@echo "  make dev          - Start development environment (gateway + db + redis)"
	@echo "  make build        - Build Docker images"
	@echo "  make migrate      - Run database migrations"
	@echo ""
	@echo "📊  Monitoring:"
	@echo "  make monitoring   - Start monitoring stack (Prometheus + Grafana + Loki)"
	@echo "  make monitoring-down - Stop monitoring stack"
	@echo ""
	@echo "🚀  Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make start        - Start all services"
	@echo "  make stop         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo ""
	@echo "🔍  Debugging:"
	@echo "  make logs         - Show logs for all services"
	@echo "  make logs-gateway - Show gateway logs"
	@echo "  make logs-db      - Show database logs"
	@echo "  make logs-redis   - Show Redis logs"
	@echo ""
	@echo "🧹  Maintenance:"
	@echo "  make clean        - Clean up containers and volumes"
	@echo "  make reset        - Complete reset (stops everything, cleans volumes)"
	@echo ""
	@echo "🩺  Health checks:"
	@echo "  make health       - Check service health"
	@echo "  make metrics      - Show metrics endpoint"

# Development environment
dev:
	@echo "🚀 Starting development environment..."
	docker-compose up -d db redis
	@echo "⏳ Waiting for database to be ready..."
	docker-compose up migrations
	docker-compose up -d gateway
	@echo "✅ Development environment is ready!"
	@echo "   🌐 API: http://localhost:8001"
	@echo "   🗄️  DB:  localhost:5432"
	@echo "   🔴 Redis: localhost:6379"

# Build all images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Database migrations
migrate:
	@echo "🔄 Running database migrations..."
	docker-compose run --rm migrations

# Production environment
prod:
	@echo "🚀 Starting production environment..."
	docker-compose --profile production up -d

# Monitoring stack
monitoring:
	@echo "📊 Starting monitoring stack..."
	docker-compose --profile monitoring up -d
	@echo "✅ Monitoring stack is ready!"
	@echo "   📊 Grafana: http://localhost:3000 (admin/admin123)"
	@echo "   🔍 Prometheus: http://localhost:9090"
	@echo "   📝 Loki: http://localhost:3100"

monitoring-down:
	@echo "📊 Stopping monitoring stack..."
	docker-compose --profile monitoring down

# Start all services
start:
	@echo "🚀 Starting all services..."
	docker-compose up -d

# Stop all services
stop:
	@echo "🛑 Stopping all services..."
	docker-compose down

# Restart services
restart:
	@echo "🔄 Restarting services..."
	docker-compose restart

# Show logs
logs:
	docker-compose logs -f

logs-gateway:
	docker-compose logs -f gateway

logs-db:
	docker-compose logs -f db

logs-redis:
	docker-compose logs -f redis

logs-prometheus:
	docker-compose logs -f prometheus

logs-grafana:
	docker-compose logs -f grafana

# Health checks
health:
	@echo "🩺 Checking service health..."
	@echo ""
	@echo "Gateway Health:"
	@curl -s http://localhost:8001/api/health | jq . || echo "Gateway not responding"
	@echo ""
	@echo "Gateway Deep Health:"
	@curl -s http://localhost:8001/api/health/deep | jq . || echo "Gateway deep health check failed"

metrics:
	@echo "📊 Gateway Metrics:"
	@curl -s http://localhost:8001/metrics || echo "Metrics not available"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down --volumes
	docker system prune -f

# Complete reset
reset:
	@echo "⚠️  COMPLETE RESET - This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		echo "🗑️  Removing all containers and volumes..."; \
		docker-compose down --volumes --remove-orphans; \
		docker-compose --profile monitoring down --volumes --remove-orphans; \
		docker system prune -f; \
		docker volume prune -f; \
		echo "✅ Reset complete!"; \
	else \
		echo ""; \
		echo "❌ Reset cancelled."; \
	fi

# Quick setup for new developers
setup:
	@echo "🛠️  Setting up ZhuchkaKeyboards development environment..."
	@echo "1️⃣  Building images..."
	@make build
	@echo "2️⃣  Starting database..."
	@make dev
	@echo "3️⃣  Setup complete! Visit http://localhost:8001/api/health"