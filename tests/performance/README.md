# 🚀 Performance Tests - High RPS Testing

Тесты производительности для проверки способности API обрабатывать высокие нагрузки (тысячи RPS).

## 📁 Структура тестов

```
tests/performance/
├── __init__.py
├── test_high_rps.py          # Основные тесты высоких RPS
├── test_metrics_load.py      # Тесты производительности метрик
└── README.md                 # Эта документация
```

## 🎯 Типы тестов

### 1. High RPS Tests (`test_high_rps.py`)

#### `test_health_endpoint_high_rps`
- **Цель**: 1000 RPS на `/api/health` в течение 10 секунд
- **Технология**: aiohttp с async/await
- **Метрики**: RPS, время ответа (avg, P95, P99), процент успеха

#### `test_warehouse_list_high_rps`
- **Цель**: 500 RPS на `/api/inventory/warehouses` в течение 5 секунд
- **Проверяет**: производительность DB-зависимых endpoints

#### `test_mixed_endpoints_load`
- **Цель**: 800 total RPS на смешанные endpoints
- **Распределение**:
  - 30% - `/api/health`
  - 25% - `/api/inventory/warehouses`
  - 25% - `/api/inventory/items`
  - 15% - `/api/inventory/analytics/summary`
  - 5% - `/api/inventory/analytics/low-stock`

#### `test_burst_load_with_threads`
- **Цель**: 1500 RPS burst load с ThreadPoolExecutor
- **Проверяет**: способность выдерживать внезапные пиковые нагрузки

#### `test_sustained_high_load`
- **Цель**: 300 RPS в течение 30 секунд
- **Проверяет**: стабильность под длительной нагрузкой

#### `test_gradual_ramp_up`
- **Цель**: поиск точки отказа API
- **Уровни**: 100, 200, 400, 600, 800, 1000, 1200, 1500 RPS
- **Критерии остановки**: success rate < 80% или avg time > 500ms

### 2. Metrics Performance Tests (`test_metrics_load.py`)

#### `test_metrics_endpoint_performance`
- **Цель**: 200 RPS на `/metrics` endpoint
- **Проверяет**: производительность Prometheus метрик

#### `test_metrics_collection_under_load`
- **Цель**: точность сбора метрик под нагрузкой
- **Проверяет**: что счетчики метрик корректно работают при высоком RPS

#### `test_health_and_metrics_mixed_load`
- **Цель**: 400 RPS смешанной нагрузки (80% health, 20% metrics)
- **Проверяет**: реалистичный сценарий мониторинга

## 🚀 Запуск тестов

### Требования
```bash
# Убедитесь что backend запущен
make dev

# Установите зависимости для performance тестов
pip install aiohttp>=3.8.5
```

### Команды запуска

```bash
# Все performance тесты
make test-performance

# Только тесты высоких RPS
make test-rps

# Только тесты метрик
make test-metrics-performance

# Конкретный тест
pytest tests/performance/test_high_rps.py::TestHighRPSPerformance::test_health_endpoint_high_rps -v -s

# С подробным выводом
pytest tests/performance/ -m performance -v -s --tb=short
```

## 📊 Целевые показатели производительности

### Health Endpoint
- **RPS**: 1000+ RPS
- **Время ответа**: < 100ms average, < 200ms P95
- **Успешность**: > 95%

### Database Endpoints (warehouses, items)
- **RPS**: 500+ RPS
- **Время ответа**: < 200ms average
- **Успешность**: > 90%

### Analytics Endpoints
- **RPS**: 100+ RPS (более тяжелые запросы)
- **Время ответа**: < 500ms average
- **Успешность**: > 85%

### Metrics Endpoint
- **RPS**: 200+ RPS
- **Время ответа**: < 500ms average
- **Успешность**: > 95%

### Sustained Load
- **Длительность**: 30+ секунд без деградации
- **RPS**: 300+ RPS stable
- **Память**: без утечек

## 🔧 Технические детали

### Async HTTP клиент (aiohttp)
```python
# Оптимальная конфигурация для высоких RPS
connector = aiohttp.TCPConnector(
    limit=100,           # Общий лимит соединений
    limit_per_host=100   # Лимит на хост
)
timeout = aiohttp.ClientTimeout(total=30)
```

### Батчи запросов
```python
# Для очень высоких RPS используем батчи
batch_size = 100
for batch in range(total_requests // batch_size):
    tasks = [make_request() for _ in range(batch_size)]
    results = await asyncio.gather(*tasks)
```

### Threading для burst тестов
```python
# ThreadPoolExecutor для имитации burst load
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(make_request) for _ in range(total)]
    results = [f.result() for f in as_completed(futures)]
```

## 📈 Интерпретация результатов

### Успешный тест
```
📊 Results:
  Total requests: 10000
  Successful: 9950
  Failed: 50
  Success rate: 99.50%
  Actual RPS: 987.65
  Avg response time: 45.23ms
  P95 response time: 78.45ms
  P99 response time: 123.67ms
```

### Проблемные сигналы
- **Success rate < 90%**: проблемы со стабильностью
- **Avg response time > 200ms**: узкие места в производительности
- **P99 > 1000ms**: проблемы с outliers
- **Actual RPS << Target RPS**: API не справляется с нагрузкой

## 🛠️ Настройка окружения для максимальной производительности

### Docker compose limits
```yaml
gateway:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

### FastAPI настройки
```python
# В main.py
app = FastAPI(
    title="ZhuchkaKeyboards Gateway",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Uvicorn с оптимизацией
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8001,
    workers=4,  # CPU cores
    loop="uvloop",  # Для максимальной производительности
    http="httptools"
)
```

### PostgreSQL connection pool
```python
# Увеличиваем pool size для высоких RPS
engine = create_async_engine(
    database_url,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

## 🚨 Troubleshooting

### Connection refused / timeout
```bash
# Проверьте лимиты системы
ulimit -n  # file descriptors
ulimit -u  # processes

# Увеличьте если нужно
ulimit -n 65536
```

### Memory leaks
```bash
# Мониторьте память во время тестов
docker stats gateway-keyboards

# Если есть утечки - проверьте connection pooling
```

### High CPU usage
```bash
# Профилируйте gateway
docker exec gateway-keyboards python -m cProfile -s cumulative your_script.py
```

## 📚 Дополнительные ресурсы

- [FastAPI Performance](https://fastapi.tiangolo.com/advanced/async-tests/)
- [aiohttp Performance](https://docs.aiohttp.org/en/stable/client_advanced.html)
- [Load Testing Best Practices](https://k6.io/docs/testing-guides/api-load-testing/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
