# ZhuchkaKeyboards 🎹

**Система управления производством клавиатур** — комплексное решение для управления производством, складом, заказами и качеством продукции с полным мониторингом и аналитикой.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-orange.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7+-red.svg)

---

## 📋 Содержание

- [Обзор системы](#-обзор-системы)
- [Архитектура](#-архитектура)
- [Функциональность](#-функциональность)
- [Модель данных](#-модель-данных)
- [Быстрый старт](#-быстрый-старт)
- [API Documentation](#-api-documentation)
- [Мониторинг и метрики](#-мониторинг-и-метрики)
- [Конфигурация](#-конфигурация)
- [Разработка](#-разработка)
- [Производительность](#-производительность)
- [Безопасность](#-безопасность)
- [Развертывание](#-развертывание)

---

## 🎯 Обзор системы

ZhuchkaKeyboards — это современная система управления производством клавиатур, построенная на микросервисной архитектуре с использованием FastAPI, PostgreSQL и Redis. Система обеспечивает полный жизненный цикл производства от заказа до доставки.

### Ключевые возможности

- 🏭 **Управление производством** — планирование, отслеживание и контроль производственных процессов
- 📦 **Управление складом** — учет товаров, движение запасов, многосклады
- 👥 **Управление пользователями** — аутентификация, авторизация, роли
- 🔍 **Контроль качества** — проверки качества, чек-листы, отчеты
- 📊 **Аналитика** — KPI, отчеты, дашборды в реальном времени
- 🚀 **Высокая производительность** — orjson, кеширование, оптимизированные запросы
- 📈 **Полный мониторинг** — Prometheus, Grafana, Loki

---

## 🏗️ Архитектура

### Общая архитектура системы

Система построена по принципам микросервисной архитектуры с единой точкой входа через API Gateway:

- **API Gateway** — FastAPI приложение, единая точка входа
- **Middleware Stack** — аутентификация, rate limiting, CORS, кеширование
- **Core Services** — модульные сервисы для разных доменов
- **Data Layer** — PostgreSQL для основных данных, Redis для кеша и сессий
- **Monitoring Stack** — Prometheus, Grafana, Loki для наблюдения за системой

### Технологический стек

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| **API Framework** | FastAPI 0.115+ | Высокопроизводительный REST API |
| **Database** | PostgreSQL 15+ | Основное хранилище данных |
| **Cache** | Redis 7+ | Кеширование и сессии |
| **ORM** | SQLAlchemy 2.0+ | Работа с базой данных |
| **Migrations** | Alembic | Управление схемой БД |
| **JSON** | orjson | Высокопроизводительная JSON сериализация |
| **Monitoring** | Prometheus + Grafana | Метрики и дашборды |
| **Logs** | Loki + Promtail | Агрегация и поиск логов |
| **Container** | Docker + Compose | Контейнеризация и оркестрация |

---

## 🚀 Функциональность

### 👥 Управление пользователями
- **Регистрация и аутентификация** — JWT токены, подтверждение email
- **Смена пароля** — безопасное обновление паролей
- **Сброс пароля** — восстановление через email
- **Управление сессиями** — Redis-based сессии

### 📦 Управление складом
- **Товары (Items)**
  - Создание, редактирование, удаление товаров
  - Категоризация: компоненты, готовые изделия, упаковка, инструменты
  - SKU, штрих-коды, физические характеристики
  - Настройки минимального/максимального запаса
  
- **Склады и зоны**
  - Многосклады с географическим разделением
  - Зоны внутри складов (хранение, получение, отгрузка)
  - Контроль температуры и влажности
  
- **Уровни запасов**
  - Текущие остатки по складам
  - Резервирование товаров
  - Отслеживание местоположения (ячейки, полки)
  
- **Движение товаров**
  - Приход, расход, перемещения
  - История всех операций
  - Инвентаризация и корректировки

### 🏭 Управление производством
- **Заказы клиентов**
  - Прием и обработка заказов
  - Статусы: ожидание → производство → контроль качества → выполнен
  - Приоритизация и планирование
  
- **Производственные задачи**
  - Этапы: дизайн → закупка → сборка → пайка → тестирование → упаковка → отгрузка
  - Назначение ресурсов (люди, оборудование)
  - Отслеживание прогресса и времени выполнения
  
- **Ресурсы**
  - Человеческие ресурсы (навыки, доступность)
  - Оборудование (станки, инструменты)
  - Материалы и расходники

### 🔍 Контроль качества
- **Проверки качества**
  - Чек-листы для каждого этапа
  - Статусы: ожидание → в процессе → пройдено → не пройдено → переделка
  - Назначение инспекторов
  
- **Элементы проверки**
  - Детализированные пункты проверки
  - Обязательные и опциональные проверки
  - Комментарии и примечания

### 🤝 Управление поставщиками
- **Поставщики**
  - База поставщиков с контактной информацией
  - Рейтинги и статусы (активный, заблокированный)
  - Условия оплаты и кредитные лимиты
  
- **Товары поставщиков**
  - Связь товаров с поставщиками
  - Цены, минимальные партии, сроки поставки
  - Предпочтительные поставщики
  
- **Заказы поставщикам**
  - Создание и отслеживание PO (Purchase Orders)
  - Статусы: черновик → отправлен → подтвержден → получен
  - Контроль поставок и приемка товаров

### 📊 Аналитика и отчеты
- **Складская аналитика**
  - Товары с низким остатком
  - Оборачиваемость запасов
  - ABC/XYZ анализ
  
- **Производственная аналитика**
  - Эффективность производства
  - Загрузка ресурсов
  - Соблюдение сроков
  
- **Качественная аналитика**
  - Процент брака
  - Время на контроль качества
  - Статистика по проверкам

---

## 🚀 Быстрый старт

### Предварительные требования

- **Docker** и **Docker Compose** v2.0+
- **Python** 3.11+ (для локальной разработки)
- **Git**
- **Make** (опционально, для удобства)

### Клонирование и запуск

```bash
# Клонируем репозиторий
git clone <repository-url>
cd ZhuchkaKeyboards

# Запуск через Docker Compose
docker-compose up --build

# Или используя Makefile (если доступен)
make dev
```

### Доступные сервисы

После запуска будут доступны следующие сервисы:

| Сервис | URL | Описание |
|--------|-----|----------|
| **API Gateway** | http://localhost:8001 | Основное API приложения |
| **PostgreSQL** | localhost:5432 | База данных (zhuchechka/root) |
| **Redis** | localhost:6379 | Кеш и сессии |
| **Swagger UI** | http://localhost:8001/api/docs | Интерактивная документация API |
| **ReDoc** | http://localhost:8001/api/redoc | Альтернативная документация API |
| **Health Check** | http://localhost:8001/api/health | Проверка здоровья системы |

### Запуск с мониторингом

```bash
# Запуск основного приложения
docker-compose up -d

# Запуск стека мониторинга
docker-compose --profile monitoring up -d

# Проверка статуса
docker-compose ps
```

### Дополнительные сервисы мониторинга

| Сервис | URL | Логин | Пароль |
|--------|-----|-------|--------|
| **Grafana** | http://localhost:3000 | admin | admin123 |
| **Prometheus** | http://localhost:9090 | - | - |
| **Loki** | http://localhost:3100 | - | - |

---

## 📚 API Documentation

### Основные эндпоинты

#### 👥 User Management (`/api/user/`)

```bash
# Регистрация пользователя
POST /api/user/sign-up
{
    "email": "user@example.com",
    "password": "secure_password",
    "phone_number": "+1234567890"
}

# Вход в систему
POST /api/user/sign-in
{
    "username": "user@example.com",
    "password": "secure_password"
}

# Смена пароля
PATCH /api/user/password/change
{
    "old_password": "old_password",
    "new_password": "new_password"
}

# Сброс пароля
POST /api/user/password/reset/request
{
    "email": "user@example.com"
}
```

#### 📦 Inventory Management (`/api/inventory/`)

```bash
# Создание товара
POST /api/inventory/items
{
    "sku": "KB-001",
    "name": "Mechanical Keyboard",
    "item_type": "FINISHED_PRODUCT",
    "category": "OTHER",
    "unit_of_measure": "PIECE",
    "min_stock_level": 10
}

# Поиск товаров
GET /api/inventory/items?search=keyboard&page=1&size=20

# Создание склада
POST /api/inventory/warehouses
{
    "name": "Main Warehouse",
    "code": "WH-001",
    "address": "123 Storage St",
    "city": "City",
    "country": "Country"
}

# Движение товаров (приход)
POST /api/inventory/move
{
    "item_id": "uuid",
    "warehouse_id": "uuid",
    "quantity": 50,
    "reason": "Purchase order receipt"
}

# Резервирование товара
POST /api/inventory/reserve?item_id=uuid&warehouse_id=uuid&quantity=5

# Аналитика складских остатков
GET /api/inventory/analytics/low-stock
GET /api/inventory/analytics/summary
```

#### 💚 Health Checks (`/api/health/`)

```bash
# Базовая проверка
GET /api/health/

# Глубокая проверка всех зависимостей
GET /api/health/deep

# Kubernetes liveness probe
GET /api/health/liveness

# Kubernetes readiness probe
GET /api/health/readiness

# Сводка метрик
GET /api/health/metrics-summary
```

### Интерактивная документация

- **Swagger UI**: http://localhost:8001/api/docs (требует basic auth: 123/123)
- **ReDoc**: http://localhost:8001/api/redoc
- **OpenAPI Schema**: http://localhost:8001/api/openapi.json

---

## 📊 Мониторинг и метрики

### Стек мониторинга

- **Prometheus** — сбор и хранение метрик
- **Grafana** — визуализация и дашборды  
- **Loki** — агрегация логов
- **Promtail** — отправка логов
- **Exporters** — дополнительные метрики (PostgreSQL, Redis, Node)

### HTTP Метрики

Система собирает детальные метрики HTTP запросов:

- **Request Rate** — количество запросов в секунду
- **Response Time** — время ответа (средн., 95%, 99%)  
- **Error Rate** — процент ошибок
- **Status Codes** — распределение по кодам ответа
- **User Agents** — анализ клиентов (браузеры, curl, etc.)
- **Request/Response Sizes** — размеры данных
- **Slow Requests** — медленные запросы (>1s)
- **IP Tracking** — запросы по IP адресам

### Эндпоинты метрик

```bash
# Все метрики Prometheus
curl http://localhost:8001/metrics

# Краткая сводка всех метрик  
curl http://localhost:8001/api/health/metrics-summary
```

### Готовые дашборды в Grafana

1. **ZhuchkaKeyboards - Application Overview** — основная панель мониторинга
2. **HTTP Metrics Dashboard** — детальная аналитика HTTP запросов

### Алерты и уведомления

Настроены алерты для критических ситуаций:
- Высокая загрузка CPU/памяти
- Медленные запросы к БД
- Ошибки приложения
- Недоступность сервисов

---

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `POSTGRES_HOST` | Хост PostgreSQL | `localhost` |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
| `POSTGRES_USER` | Пользователь БД | `zhuchechka` |
| `POSTGRES_PASSWORD` | Пароль БД | `root` |
| `POSTGRES_DB` | Имя базы данных | `zhuchka` |
| `REDIS_HOST` | Хост Redis | `localhost` |
| `REDIS_PORT` | Порт Redis | `6379` |
| `REDIS_DB` | Номер БД Redis | `0` |
| `JWT_SECRET` | Секретный ключ JWT | `your-secret-key-here` |
| `JWT_ALGORITHM` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена (мин) | `30` |

### Настройка базы данных

```bash
# Настройки пула соединений
POSTGRES_POOL_SIZE=10
POSTGRES_MAX_OVERFLOW=20
POSTGRES_POOL_TIMEOUT=30
POSTGRES_POOL_RECYCLE=1800
POSTGRES_POOL_PING=1
POSTGRES_ECHO=0  # Логирование SQL запросов
```

### Настройка производительности

```bash
# Настройки orjson для высокой производительности
PYDANTIC_USE_ORJSON=true

# Настройки rate limiting
RATE_LIMIT_REQUESTS=999999  # Для production тестов
RATE_LIMIT_WINDOW=60
```

---

## 🛠️ Разработка

### Структура проекта

```
ZhuchkaKeyboards/
├── gateway/                          # Основное API приложение
│   ├── src/
│   │   ├── main.py                  # Точка входа приложения
│   │   ├── config.py                # Конфигурация
│   │   ├── configuration/
│   │   │   └── app.py              # Настройка FastAPI
│   │   ├── database/
│   │   │   ├── core.py             # Подключение к БД
│   │   │   ├── dependencies.py     # DI для сессий БД
│   │   │   └── alembic/            # Миграции
│   │   ├── routers/
│   │   │   ├── user/               # Управление пользователями
│   │   │   ├── inventory/          # Управление складом
│   │   │   ├── production/         # Управление производством
│   │   │   └── health/             # Health checks
│   │   ├── services/
│   │   │   ├── redis/              # Подключение к Redis
│   │   │   ├── cache/              # Кеширование
│   │   │   ├── metrics/            # Метрики Prometheus
│   │   │   └── session/            # Управление сессиями
│   │   ├── security/               # Аутентификация и авторизация
│   │   ├── middleware/             # Middleware компоненты
│   │   └── utils/                  # Утилиты и helpers
│   ├── requirements.txt            # Python зависимости
│   └── Dockerfile                  # Docker образ
├── monitoring/                      # Конфигурация мониторинга
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   └── promtail/
├── tests/                          # Тесты
│   ├── unit/                       # Юнит тесты
│   ├── integration/                # Интеграционные тесты
│   └── performance/                # Нагрузочные тесты
├── docker-compose.yaml             # Основной compose файл
└── README.md                       # Документация
```

### Локальная разработка

```bash
# Установка зависимостей
cd gateway
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Запуск в режиме разработки
cd src
uvicorn main:app --reload --port 8001

# Или через переменные окружения
export POSTGRES_HOST=localhost
export REDIS_HOST=localhost
uvicorn main:app --reload --port 8001
```

### Управление миграциями

```bash
# Создание новой миграции
docker-compose exec gateway bash -c "cd /app/src/database && alembic revision --autogenerate -m 'описание изменений'"

# Применение миграций
docker-compose exec gateway bash -c "cd /app/src/database && alembic upgrade head"

# Откат миграции
docker-compose exec gateway bash -c "cd /app/src/database && alembic downgrade -1"

# Просмотр истории миграций
docker-compose exec gateway bash -c "cd /app/src/database && alembic history"
```

### Тестирование

```bash
# Запуск всех тестов
pytest

# Юнит тесты
pytest tests/unit/

# Интеграционные тесты
pytest tests/integration/

# Нагрузочные тесты
pytest tests/performance/

# Тест с покрытием
pytest --cov=src --cov-report=html
```

### Линтеры и форматтеры

```bash
# Проверка типов
mypy src/

# Проверка стиля кода
flake8 src/
black src/ --check

# Автоформатирование
black src/
isort src/
```

---

## ⚡ Производительность

### Оптимизация JSON

- **orjson**: Используется для высокопроизводительной сериализации/десериализации JSON
- **Pydantic + orjson**: Все Pydantic модели настроены для использования orjson
- **FastAPI ORJSONResponse**: API ответы используют orjson по умолчанию

### Преимущества orjson

- В 2-3 раза быстрее стандартного `json` модуля
- Поддержка numpy массивов и datetime объектов
- Более строгая валидация JSON
- Меньше потребление памяти

### Тестирование производительности

```bash
# Тест производительности orjson
cd gateway
python test_orjson.py

# Нагрузочные тесты
cd tests/performance
python test_realistic_load.py
python test_high_rps.py
```

### Кеширование

- **Redis** для кеширования API ответов
- **Session storage** в Redis
- **Database query caching** для часто используемых запросов
- **HTTP response caching** с настраиваемым TTL

### Оптимизация базы данных

- **Connection pooling** с настраиваемыми параметрами
- **Асинхронные запросы** через asyncpg
- **Индексы** на часто используемых полях
- **Партиционирование** больших таблиц (на будущее)

---

## 🔒 Безопасность

### Аутентификация и авторизация

- **JWT токены** для аутентификации
- **Refresh tokens** для обновления сессий
- **Session management** через Redis
- **Role-based access control** (планируется)

### Безопасность данных

- **Хеширование паролей** с bcrypt
- **Валидация входных данных** через Pydantic
- **SQL injection protection** через SQLAlchemy ORM
- **XSS protection** через escaping

### Сетевая безопасность

- **CORS настройки** для контроля доступа
- **Rate limiting** для защиты от DDoS
- **HTTPS** в production (требует настройки reverse proxy)
- **Input sanitization** для всех пользовательских данных

### Мониторинг безопасности

- **Логирование** всех критических операций
- **Алерты** на подозрительную активность
- **Audit trail** для отслеживания изменений
- **Регулярные security updates** зависимостей

---

## 🚢 Развертывание

### Docker Compose (рекомендуемый способ)

```bash
# Production развертывание
docker-compose -f docker-compose.yaml up -d

# С мониторингом
docker-compose --profile monitoring up -d

# Проверка здоровья
docker-compose ps
curl http://localhost:8001/api/health
```

### Kubernetes (планируется)

```yaml
# Пример конфигурации для Kubernetes
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zhuchka-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: zhuchka-gateway
  template:
    metadata:
      labels:
        app: zhuchka-gateway
    spec:
      containers:
      - name: gateway
        image: zhuchka/gateway:latest
        ports:
        - containerPort: 8001
        env:
        - name: POSTGRES_HOST
          value: "postgres-service"
        - name: REDIS_HOST
          value: "redis-service"
```

### Масштабирование

- **Horizontal scaling** — увеличение количества реплик Gateway
- **Database scaling** — read replicas для PostgreSQL
- **Cache scaling** — Redis Cluster для больших нагрузок
- **Load balancing** — nginx/traefik для распределения трафика

### Резервное копирование

```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U zhuchechka zhuchka > backup.sql

# Backup Redis (если нужно)
docker-compose exec redis redis-cli --rdb backup.rdb

# Restore PostgreSQL
docker-compose exec -T db psql -U zhuchechka zhuchka < backup.sql
```

---

## 🤝 Участие в разработке

### Процесс разработки

1. **Форкните** репозиторий
2. **Создайте ветку** для новой функции: `git checkout -b feature/new-feature`
3. **Внесите изменения** и добавьте тесты
4. **Запустите тесты**: `pytest`
5. **Зафиксируйте изменения**: `git commit -am 'Add new feature'`
6. **Отправьте в ветку**: `git push origin feature/new-feature`
7. **Создайте Pull Request**

### Стандарты кода

- **PEP 8** для Python кода
- **Type hints** обязательны
- **Docstrings** для всех публичных функций
- **Тесты** для новой функциональности
- **Meaningful commit messages**

### Архитектурные принципы

- **SOLID принципы**
- **Clean Architecture**
- **Domain Driven Design** для бизнес-логики
- **API-First подход**
- **Microservices готовность**

---

## 📄 Лицензия

Этот проект лицензирован под **MIT License**. См. файл [LICENSE](LICENSE) для подробностей.

---

## 📞 Поддержка

### Сообщение об ошибках

1. **Проверьте** [существующие issues](../../issues)
2. **Создайте новый issue** с подробным описанием
3. **Приложите логи** и конфигурацию
4. **Укажите шаги** для воспроизведения

### Документация и помощь

- **API Documentation**: http://localhost:8001/api/docs
- **Monitoring Guides**: [monitoring/README.md](monitoring/README.md)
- **Performance Testing**: [tests/performance/README.md](tests/performance/README.md)

### Контакты

- **Issues**: Используйте GitHub Issues для вопросов и предложений
- **Discussions**: GitHub Discussions для общих вопросов
- **Security**: Отправляйте security issues приватно

---

**ZhuchkaKeyboards** — Современная система управления производством клавиатур 🎹

*Создано с ❤️ для эффективного производства и качественного продукта*

---

## 📊 Статистика проекта

- **Языки**: Python 3.11+, SQL, YAML, Markdown
- **Фреймворки**: FastAPI, SQLAlchemy, Pydantic, Alembic
- **Базы данных**: PostgreSQL, Redis
- **Мониторинг**: Prometheus, Grafana, Loki
- **Тестирование**: pytest, mypy, flake8
- **Контейнеризация**: Docker, Docker Compose
- **CI/CD**: GitHub Actions (планируется)

[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/your-repo)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-green.svg)](https://fastapi.tiangolo.com)
