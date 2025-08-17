# 📊 Настройка HTTP Метрик в Grafana

## 🚀 Быстрый доступ

1. **Откройте Grafana**: http://localhost:3000
2. **Логин**: `admin`
3. **Пароль**: `admin123`

## 📈 Доступные Dashboards

### 1. **ZhuchkaKeyboards - Application Overview**
- Основная панель мониторинга приложения
- HTTP метрики, статистика ошибок, производительность
- Обновляется каждые 5 секунд

### 2. **HTTP Metrics Dashboard**
- Детальная аналитика HTTP запросов
- 10+ графиков и панелей для анализа API

## 🔧 Основные метрики

### HTTP Метрики
- **Request Rate**: Количество запросов в секунду
- **Response Time**: Время ответа (средн., 95%, 99%)
- **Error Rate**: Процент ошибок
- **Status Codes**: Распределение по кодам ответа
- **User Agents**: Анализ клиентов (браузеры, curl, etc.)
- **Request/Response Sizes**: Размеры данных
- **Slow Requests**: Медленные запросы (>1s)

### Системные метрики
- **Database Connections**: Подключения к PostgreSQL
- **Redis Operations**: Операции с Redis
- **Memory/CPU Usage**: Использование ресурсов
- **Application Errors**: Ошибки приложения

## 📋 Полезные Prometheus запросы

```promql
# Топ-10 эндпоинтов по трафику
topk(10, sum by (endpoint) (rate(http_requests_total[5m])))

# Процент ошибок по эндпоинтам
rate(http_errors_by_type_total[5m]) / rate(http_requests_total[5m])

# 95-й процентиль времени ответа
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Медленные запросы
rate(http_slow_requests_total[5m])

# Запросы по User Agent
sum by (user_agent_family) (rate(http_requests_by_user_agent_total[5m]))

# Активные запросы
sum(http_requests_in_progress)
```

## 🎨 Настройка алертов

### Рекомендуемые алерты:
1. **Высокий процент ошибок** (>5%)
2. **Медленные запросы** (>1s)
3. **Высокое время ответа** (95% >500ms)
4. **Много активных запросов** (>20)

### Создание алерта:
1. Перейдите в Dashboard
2. Нажмите на панель → Edit
3. Alert tab → Create Alert
4. Настройте условия и уведомления

## 🔍 Анализ производительности

### Что смотреть:
- **Request Rate**: Нормальный ли трафик?
- **Error Rate**: Есть ли проблемы с API?
- **Response Time**: Быстро ли отвечает приложение?
- **Status Codes**: Много ли 4xx/5xx ошибок?
- **User Agents**: Кто использует API?

### Типичные проблемы:
- **Spike в Error Rate** → Проблемы с кодом/БД
- **Высокий Response Time** → Медленные запросы к БД
- **Много 404** → Неправильные URL в клиентах
- **Высокий Request Rate** → Возможная атака/бот

## 🛠️ Дополнительные настройки

### Добавление новых панелей:
1. Dashboard → Add Panel
2. Выберите тип визуализации
3. Настройте Prometheus запрос
4. Добавьте лейблы и форматирование

### Экспорт/Импорт:
- **Экспорт**: Dashboard Settings → JSON Model
- **Импорт**: + → Import → Upload JSON

### Переменные:
- Создайте переменные для фильтрации по endpoint, method, status_code
- Settings → Variables → Add Variable

## 📱 Мобильное приложение

Grafana имеет мобильное приложение для мониторинга:
- iOS: Grafana Mobile
- Android: Grafana Mobile

## 🔗 Полезные ссылки

- **Grafana Documentation**: https://grafana.com/docs/
- **Prometheus Queries**: https://prometheus.io/docs/prometheus/latest/querying/
- **PromQL Tutorial**: https://prometheus.io/docs/prometheus/latest/querying/basics/

---

## 🎯 Готовые команды для тестирования

```bash
# Генерация трафика для тестирования
for i in {1..20}; do
  curl http://localhost:8001/api/health
  curl http://localhost:8001/api/metrics-summary  
  curl http://localhost:8001/api/metrics/http
  sleep 1
done

# Проверка метрик
curl http://localhost:8001/metrics | grep http_requests

# Проверка Grafana
curl http://localhost:3000/api/health
```

Теперь ваши HTTP метрики полностью интегрированы в Grafana! 🎉
