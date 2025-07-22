# ZhuchkaKeyboards 🎹

Система управления производством и продажами клавиатур с веб-интерфейсом, API, ботом и GUI-приложением.

---

## 🏗️ Архитектура

- **Gateway** — FastAPI сервис (src)
- **Database** — PostgreSQL (docker-compose)
- **Cache** — Redis (docker-compose)
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
docker-compose up --build
```

- Gateway API: http://localhost:8001
- PostgreSQL: localhost:5432
- Redis: localhost:6379

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
ython main:app --reload --port 8001

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

---

## 🔒 Безопасность
- JWT токены для аутентификации
- Хеширование паролей с bcrypt
- CORS настройки
- Rate limiting
- Валидация данных через Pydantic

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
