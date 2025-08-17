# ZhuchkaKeyboards 🎹

Система управления производством и продажами клавиатур с веб-интерфейсом, API, ботом и GUI-приложением.

---

## 🏗️ Архитектура

- **Gateway** — FastAPI сервис (src)
- **Database** — PostgreSQL (docker-compose)
- **Cache** — Redis (docker-compose)
- **Monitoring** — Prometheus + Grafana + Loki (docker-compose)
- **Alembic** — миграции в `src/database/alembic`
- **API** — REST API
- **Bot** — Telegram бот
- **GUI** — Десктопное приложение

---

## 🚀 Быстрый старт

### Предварительные требования
- Docker и Docker Compose
- Python 3.11+
- Git

### Запуск через Docker Compose

```bash
git clone <repository-url>
cd ZhuchkaKeyboards

# Запуск разработки
make dev

# Или запуск с мониторингом
make dev
make monitoring
```

### Доступные сервисы

- **Gateway API**: http://localhost:8001
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100

---

## 📦 Миграции Alembic

Миграции и конфиг Alembic находятся в `gateway/src/database/alembic` и `gateway/src/database/alembic.ini`.

### Генерация новой миграции
```bash
docker-compose exec gateway bash -c "cd /app/src/database && alembic revision --autogenerate -m 'описание'"
```

### Применение миграций
```bash
docker-compose exec gateway bash -c "cd /app/src/database && alembic upgrade head"
```

### Откат миграции
```bash
docker-compose exec gateway bash -c "cd /app/src/database && alembic downgrade -1"
```

### Структура Alembic
```
gateway/
└── src/
    └── database/
        ├── alembic.ini
        └── alembic/
            ├── env.py
            ├── script.py.mako
            └── versions/
```

---

## 📁 Структура проекта

```
ZhuchkaKeyboards/
├── README.md
├── docker-compose.yaml
├── docker-compose.local.yml
├── Makefile
├── main.py
├── requirements.txt
├── LICENSE
├── gateway/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── src/
│       ├── config.py
│       ├── main.py
│       ├── main_schemas.py
│       ├── dependencies.py
│       ├── pydantic_config.py
│       ├── configuration/
│       │   └── app.py
│       ├── database/
│       │   ├── alembic.ini
│       │   ├── core.py
│       │   ├── logging.py
│       │   ├── dependencies.py
│       │   └── alembic/
│       │       ├── env.py
│       │       ├── script.py.mako
│       │       └── versions/
│       │           └── __init__.py
│       ├── routers/
│       │   ├── __init__.py
│       │   └── user/
│       │       ├── actions.py
│       │       ├── dal.py
│       │       ├── models.py
│       │       ├── router.py
│       │       ├── schemas.py
│       │       └── __init__.py
│       ├── security/
│       │   ├── hashing.py
|       |   └── security.py
│       ├── services/
│       │   └── redis/
│       │       └── rediska.py
│       └── utils/
│       │   ├── logger.py
│       │   ├── responses_schemas.py
│       │   ├── responses.py
|       |   └── __init__.py
└── .github/
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

---

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `POSTGRES_HOST` | Хост PostgreSQL | `localhost` |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
| `POSTGRES_USER` | Пользователь БД | `postgres` |
| `POSTGRES_PASSWORD` | Пароль БД | `password` |
| `POSTGRES_DB` | Имя базы данных | `postgres` |
| `REDIS_HOST` | Хост Redis | `localhost` |
| `REDIS_PORT` | Порт Redis | `6379` |
| `JWT_SECRET` | Секретный ключ JWT | Генерируется |
| `JWT_ALGORITHM` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `11520` |

---

## 🛠️ Разработка

### Установка зависимостей

```bash
# Gateway
cd gateway
pip install -r requirements.txt

# API
cd ../api
pip install -r requirements.txt
```

### Запуск в режиме разработки

```bash
# Gateway
cd gateway/src
uvicorn main:app --reload --port 8001

# API
cd ../../api
uvicorn main:app --reload --port 8000
```

### Тестирование

```bash
pytest
mypy .
flake8 .
```

### Тестирование производительности orjson

```bash
# Тест производительности orjson
cd gateway
python test_orjson.py

# Тест в Docker контейнере
docker-compose exec gateway python test_orjson.py
```

---

## 📊 Мониторинг и Метрики

### Стек мониторинга

- **Prometheus** - сбор и хранение метрик
- **Grafana** - визуализация и дашборды  
- **Loki** - агрегация логов
- **Promtail** - отправка логов
- **Exporters** - дополнительные метрики (PostgreSQL, Redis, Node)

### Запуск мониторинга

```bash
# Запуск основного приложения
make dev

# Запуск стека мониторинга
make monitoring
```

### Доступ к интерфейсам

- **Grafana**: http://localhost:3000
  - Пользователь: `admin`
  - Пароль: `admin123`
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100

### Собираемые метрики

#### Метрики приложения
- HTTP запросы (количество, время ответа, статус коды)
- База данных (время выполнения запросов, количество соединений)
- Redis (операции, размер пула соединений)
- Бизнес-логика (заказы, задачи производства, проверки качества)
- Ошибки приложения
- Кеширование (hit/miss ratio)

#### Метрики инфраструктуры
- PostgreSQL (производительность БД, соединения, запросы)
- Redis (использование памяти, операции, клиенты)
- Система (CPU, память, диск, сеть)

### Готовые дашборды

1. **ZhuchkaKeyboards Overview**
   - Обзор производительности приложения
   - HTTP метрики и частота ошибок
   - Производительность БД и Redis
   - Бизнес-метрики (заказы, производство)

### Проверка работоспособности

```bash
# Проверка здоровья всех сервисов
make health

# Просмотр метрик
make metrics

# Логи сервисов
make logs
```

Подробная документация по мониторингу: [monitoring/README.md](monitoring/README.md)

---

## 🔒 Безопасность
- JWT токены для аутентификации
- Хеширование паролей с bcrypt
- CORS настройки
- Rate limiting
- Валидация данных через Pydantic
- Высокопроизводительная сериализация JSON через orjson

---

## 📝 API Документация
- **Swagger UI**: http://localhost:8001/api/docs
- **ReDoc**: http://localhost:8001/api/redoc
- **OpenAPI JSON**: http://localhost:8001/api/openapi.json

---

## 🐳 Docker

### Сборка и запуск
```bash
docker-compose up --build
```

### Генерация и применение миграций (в контейнере)
```bash
docker-compose exec gateway bash -c "cd /app/src/database && alembic revision --autogenerate -m 'описание'"
docker-compose exec gateway bash -c "cd /app/src/database && alembic upgrade head"
```

---

## 🤝 Вклад в проект
1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

---

## 📄 Лицензия
Этот проект лицензирован под MIT License.

---

## 📞 Поддержка
Если у вас есть вопросы или проблемы:
1. Создайте Issue в GitHub
2. Опишите проблему подробно
3. Приложите логи и конфигурацию

---

**ZhuchkaKeyboards** — Система управления производством клавиатур 🎹
