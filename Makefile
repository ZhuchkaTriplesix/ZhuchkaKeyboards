COMPOSE_FILE=docker-compose.local.yml

# Поднять все сервисы (с пересборкой)
up:
	docker compose --file $(COMPOSE_FILE) up --build

# Остановить все сервисы
down:
	docker compose --file $(COMPOSE_FILE) down

# Перезапустить сервисы
restart:
	docker compose --file $(COMPOSE_FILE) down
	docker compose --file $(COMPOSE_FILE) up --build

# Логи всех сервисов
logs:
	docker compose --file $(COMPOSE_FILE) logs -f

# Логи только приложения fastapi_app
logs-app:
	docker compose --file $(COMPOSE_FILE) logs -f fastapi_app

# Установить зависимости для локальной разработки (Linux/macOS)
install-dev:
	pip install -r requirements.txt

# Проверить статус контейнеров
ps:
	docker compose --file $(COMPOSE_FILE) ps

# Очистить все тома (ОСТОРОЖНО: удалит все данные!)
clean:
	docker compose --file $(COMPOSE_FILE) down -v 