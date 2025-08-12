.PHONY: help install test test-unit test-integration test-cache test-session test-all lint format check-quality coverage clean

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости для тестирования
	pip install -r requirements-test.txt

test: ## Запустить все тесты
	pytest

test-unit: ## Запустить только unit тесты
	pytest -m "not integration"

test-integration: ## Запустить только integration тесты
	pytest -m "integration"

test-cache: ## Запустить тесты кэширования
	pytest -m "cache"

test-session: ## Запустить тесты управления сессиями
	pytest -m "session"

test-all: ## Запустить все тесты с подробным отчетом
	pytest -v --tb=long --cov=src --cov-report=html --cov-report=term-missing

lint: ## Проверить код линтером
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format: ## Отформатировать код
	black src/ tests/
	isort src/ tests/

check-quality: ## Проверить качество кода
	mypy src/
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

coverage: ## Показать покрытие кода
	pytest --cov=src --cov-report=term-missing --cov-report=html

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

test-performance: ## Запустить тесты производительности
	pytest tests/test_orjson.py -v

test-redis: ## Запустить тесты Redis (требует запущенный Redis)
	pytest -m "redis" -v

test-database: ## Запустить тесты базы данных (требует запущенную БД)
	pytest -m "database" -v

quick-test: ## Быстрый тест без покрытия
	pytest -x --tb=short

test-watch: ## Запустить тесты в режиме наблюдения
	pytest-watch src/ tests/ -- -v

install-dev: ## Установить зависимости для разработки
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	pip install -e .

docker-test: ## Запустить тесты в Docker
	docker-compose exec gateway pytest

docker-lint: ## Запустить линтер в Docker
	docker-compose exec gateway make lint

docker-format: ## Отформатировать код в Docker
	docker-compose exec gateway make format
