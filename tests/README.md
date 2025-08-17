# 🧪 ZhuchkaKeyboards Test Suite

Комплексный набор тестов для API управления складом клавиатур.

## 📁 Структура тестов

```
tests/
├── conftest.py              # Общие фикстуры и конфигурация
├── unit/                    # Unit тесты (без контейнеров)
│   └── test_inventory_api.py
├── integration/             # Integration тесты (с контейнерами)
│   ├── test_inventory_full.py
│   └── test_performance.py
└── README.md
```

## 🎭 Типы тестов

### 1. Unit тесты (`tests/unit/`)
- **Назначение**: Тестируют бизнес-логику API без внешних зависимостей
- **Особенности**: 
  - Используют моки для базы данных
  - Быстрые (выполняются за секунды)
  - Не требуют запущенных контейнеров
  - Изолированы друг от друга
- **Запуск**: `make test-unit` или `pytest tests/unit/ -m unit`

### 2. Integration тесты (`tests/integration/`)
- **Назначение**: Тестируют полный workflow с реальной базой данных
- **Особенности**:
  - Используют SQLite в памяти для быстроты
  - Тестируют полные сценарии использования
  - Проверяют интеграцию компонентов
  - Требуют запущенный backend (опционально)
- **Запуск**: `make test-integration` или `pytest tests/integration/ -m integration`

### 3. Performance тесты (`tests/integration/test_performance.py`)
- **Назначение**: Тестируют производительность под нагрузкой
- **Особенности**:
  - Измеряют время отклика
  - Тестируют конкурентность
  - Проверяют масштабируемость
  - Анализируют bottlenecks
- **Запуск**: `make test-performance`

## 🚀 Быстрый старт

### Запуск без контейнеров (Unit тесты)
```bash
# Установить зависимости
pip install -r requirements-test.txt

# Запустить unit тесты
make test-unit

# Или конкретный тест
pytest tests/unit/test_inventory_api.py::TestWarehouseAPI::test_create_warehouse_success -v
```

### Запуск с контейнерами (Integration тесты)
```bash
# 1. Запустить backend
make dev

# 2. Запустить integration тесты
make test-integration

# Или полный цикл
make dev-setup && make test
```

## 📊 Покрытые сценарии

### 🏢 Warehouse API
- ✅ CRUD операции (создание, чтение, обновление)
- ✅ Валидация дубликатов кодов
- ✅ Фильтрация по активности
- ✅ Обработка ошибок 404

### 📦 Items API  
- ✅ CRUD операции со всеми полями
- ✅ Поиск и фильтрация (по типу, категории, бренду)
- ✅ Пагинация результатов
- ✅ Валидация уникальности SKU
- ✅ Мягкое удаление (деактивация)

### 📊 Inventory Levels API
- ✅ Управление уровнями запасов
- ✅ Вычисляемые поля (available_quantity)
- ✅ Поиск по складам и товарам
- ✅ Валидация бизнес-правил

### 🔄 Stock Movement API
- ✅ Приход/расход товаров
- ✅ Резервирование/снятие резерва
- ✅ Валидация достаточности товара
- ✅ Конкурентные операции
- ✅ Отслеживание движений

### 📈 Analytics API
- ✅ Товары с низким остатком
- ✅ Сводка по запасам
- ✅ Фильтрация по складам
- ✅ Производительность аналитики

## ⚡ Performance метрики

### Целевые показатели:
- **Создание склада**: < 500ms
- **Поиск товаров**: < 2s (100+ товаров)
- **Движение товара**: < 200ms
- **Резервирование**: < 100ms
- **Аналитика**: < 5s (большой dataset)

### Конкурентность:
- **50 одновременных движений**: без race conditions
- **100 резерваций**: консистентность данных
- **Масштабируемость**: 1000+ товаров

## 🛠️ Полезные команды

```bash
# Все тесты
make test

# Только быстрые тесты
make test-quick

# Конкретный модуль
make test-inventory-unit
make test-inventory-integration

# С покрытием кода
pytest --cov=gateway/src/routers/inventory tests/

# С подробным выводом
pytest tests/ -v -s

# Только неудачные тесты
pytest tests/ --lf

# С бенчмарками
pytest tests/integration/test_performance.py --benchmark-only

# HTML отчет
pytest tests/ --html=report.html
```

## 🔧 Настройка окружения

### Для unit тестов:
```bash
# Только Python зависимости
pip install -r requirements-test.txt
```

### Для integration тестов:
```bash
# Docker окружение
make dev

# Проверить статус
make health

# Логи сервисов
make logs
```

## 📝 Написание новых тестов

### Unit тест (пример):
```python
@pytest.mark.unit
def test_new_feature(mock_app: TestClient):
    # Мокаем зависимости
    with patch('routers.inventory.crud.some_function') as mock_func:
        mock_func.return_value = expected_result
        
        # Тестируем API
        response = mock_app.get("/api/inventory/new-endpoint")
        
        # Проверяем результат
        assert response.status_code == 200
        assert response.json()["field"] == "expected_value"
```

### Integration тест (пример):
```python
@pytest.mark.integration
def test_full_workflow(integration_app: TestClient):
    # Создаем данные
    response = integration_app.post("/api/inventory/items", json=item_data)
    item_id = response.json()["id"]
    
    # Тестируем workflow
    response = integration_app.get(f"/api/inventory/items/{item_id}")
    assert response.status_code == 200
```

## 🚨 Troubleshooting

### Проблема: Тесты падают с ошибкой подключения
```bash
# Решение: Убедитесь что контейнеры запущены
make dev
make health
```

### Проблема: Медленные тесты
```bash
# Решение: Запускайте тесты параллельно
pytest tests/ -n auto

# Или только быстрые тесты
pytest tests/unit/ -m unit
```

### Проблема: Моки не работают
```bash
# Решение: Проверьте путь к функции
# ❌ Неправильно
with patch('crud.get_item'):

# ✅ Правильно  
with patch('routers.inventory.crud.get_item'):
```

## 📚 Дополнительные ресурсы

- [Pytest документация](https://docs.pytest.org/)
- [FastAPI тестирование](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy тестирование](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#testing)
- [Async тестирование](https://pytest-asyncio.readthedocs.io/)
