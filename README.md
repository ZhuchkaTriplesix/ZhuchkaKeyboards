# ZhuchkaKeyboards 🎹

Система управления производством и продажами клавиатур с веб-интерфейсом, API, ботом.

## 🏗️ Архитектура

Проект состоит из нескольких компонентов:

- **Gateway** - FastAPI сервис для обработки запросов
- **Database** - PostgreSQL для хранения данных
- **Cache** - Redis для кеширования
- **API** - REST API для работы с данными
- **Bot** - Telegram бот для уведомлений
- **GUI** - Десктопное приложение

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.13+
- Git

### Запуск через Docker Compose

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd ZhuchkaKeyboards
```

2. **Создайте файл .env (опционально):**
```bash
# PostgreSQL
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=zhuchechka
POSTGRES_PASSWORD=root
POSTGRES_DB=zhuchka

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520
```

3. **Запустите все сервисы:**
```bash
docker-compose up --build
```

4. **Проверьте работу:**
- Gateway API: http://localhost:8001
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Локальная разработка

Для разработки используйте локальный compose:

```bash
docker-compose -f docker-compose.local.yml up --build
```

## 📁 Структура проекта

```
ZhuchkaKeyboards/
├── api/                    # Основной API сервис
│   ├── endpoints/         # API эндпоинты
│   ├── functions.py       # CRUD операции
│   ├── models.py          # SQLAlchemy модели
│   └── api.py            # Роутинг API
├── gateway/               # Gateway сервис
│   ├── src/
│   │   ├── configuration/ # Конфигурация приложения
│   │   ├── database/      # Работа с БД
│   │   ├── routers/       # Роутеры
│   │   ├── services/      # Бизнес-логика
│   │   └── main.py       # Точка входа
│   ├── Dockerfile
│   └── requirements.txt
├── core/                  # Общие настройки
│   ├── config.py         # Конфигурация
│   └── security.py       # Безопасность
├── db/                    # Работа с БД
│   └── session.py        # Сессии SQLAlchemy
├── schemas/               # Pydantic схемы
│   ├── dantic.py         # Модели данных
│   └── crud.py           # CRUD схемы
├── docker-compose.yaml    # Продакшн конфигурация
├── docker-compose.local.yml # Локальная разработка
└── README.md
```

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

### Настройки базы данных

```python
# Пример подключения к PostgreSQL
from src.database.core import engine, get_db
from fastapi import Depends

@app.get("/users")
async def get_users(db = Depends(get_db)):
    # Ваш код здесь
    pass
```

## 📊 Модели данных

### Основные сущности

- **Customers** - Клиенты
- **Employees** - Сотрудники
- **Products** - Продукты
- **Orders** - Заказы
- **Services** - Услуги
- **Components** - Компоненты
- **Transactions** - Транзакции
- **Tasks** - Задачи

### Примеры API

```bash
# Получить всех клиентов
GET /api/customers

# Создать нового клиента
POST /api/customers
{
  "vendor_id": 123,
  "vendor_type": 1,
  "first_name": "Иван",
  "second_name": "Иванов",
  "username": "ivan",
  "email": "ivan@example.com"
}

# Получить заказ по ID
GET /api/orders/{id}

# Создать заказ
POST /api/orders
{
  "customer_id": 1,
  "manager_id": 1,
  "transaction_id": 1,
  "product_id": 1
}
```

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
# Запуск тестов
pytest

# Проверка типов
mypy .

# Линтинг
flake8 .
```

## 🔒 Безопасность

- JWT токены для аутентификации
- Хеширование паролей с bcrypt
- CORS настройки
- Rate limiting
- Валидация данных через Pydantic

## 📝 API Документация

После запуска приложения документация доступна по адресам:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## 🐳 Docker

### Сборка образов

```bash
# Сборка gateway
docker build -t zhuchka-gateway ./gateway

# Сборка API
docker build -t zhuchka-api ./api
```

### Запуск контейнеров

```bash
# Продакшн
docker-compose up -d

# Локальная разработка
docker-compose -f docker-compose.local.yml up -d

# Просмотр логов
docker-compose logs -f gateway
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License.

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

1. Создайте Issue в GitHub
2. Опишите проблему подробно
3. Приложите логи и конфигурацию

---

**ZhuchkaKeyboards** - Система управления производством клавиатур 🎹
