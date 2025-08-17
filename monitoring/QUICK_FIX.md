# 🚀 Быстрое решение проблемы с Grafana Dashboard

## ❌ Проблема
"An unexpected error happened" при импорте JSON dashboard

## ✅ Простое решение

### Вариант 1: Создать dashboard вручную (рекомендуется)

1. **Откройте Grafana**: http://localhost:3000
2. **Войдите**: `admin` / `admin123`
3. **Создайте новый dashboard**: `+` → `Dashboard`
4. **Добавьте панели по одной:**

#### Панель 1: Total Requests per Second
- Нажмите **"Add visualization"**
- Выберите **Prometheus** datasource
- **Query**: `sum(rate(http_requests_total[5m]))`
- **Visualization**: Stat
- **Unit**: reqps (requests per second)
- Сохраните

#### Панель 2: Request Rate by Method  
- **Query**: `sum by (method) (rate(http_requests_total[5m]))`
- **Legend**: `{{method}}`
- **Visualization**: Time series

#### Панель 3: Response Time
- **Query**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Unit**: seconds
- **Visualization**: Time series

#### Панель 4: Status Codes
- **Query**: `sum by (status_code) (rate(http_requests_total[5m]))`
- **Legend**: `{{status_code}}`
- **Visualization**: Pie chart

### Вариант 2: Простой JSON для импорта

Скопируйте этот JSON (из файла `monitoring/simple-http-dashboard.json`):

```json
{
  "dashboard": {
    "id": null,
    "title": "HTTP Metrics - Simple",
    "tags": ["http", "api", "zhuchka"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Total Requests per Second",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m]))",
            "refId": "A",
            "datasource": {
              "type": "prometheus",
              "uid": "prometheus"
            }
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "color": { "mode": "value" },
            "thresholds": {
              "steps": [
                { "color": "green", "value": null },
                { "color": "yellow", "value": 10 },
                { "color": "red", "value": 50 }
              ]
            }
          }
        },
        "options": {
          "reduceOptions": { "calcs": ["lastNotNull"] },
          "colorMode": "background"
        }
      }
    ],
    "time": { "from": "now-30m", "to": "now" },
    "refresh": "5s",
    "schemaVersion": 30,
    "version": 1
  }
}
```

## 🔍 Проверка работы

```bash
# Сгенерируйте трафик
for ($i=1; $i -le 20; $i++) { 
  curl http://localhost:8001/api/health -UseBasicParsing | Out-Null
  curl http://localhost:8001/api/metrics-summary -UseBasicParsing | Out-Null
  Start-Sleep 1 
}
```

## 🎯 Полезные PromQL запросы

```promql
# Общий RPS
sum(rate(http_requests_total[5m]))

# RPS по методам
sum by (method) (rate(http_requests_total[5m]))

# RPS по эндпоинтам
sum by (endpoint) (rate(http_requests_total[5m]))

# 95th процентиль времени ответа
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Медианное время ответа
histogram_quantile(0.5, rate(http_request_duration_seconds_bucket[5m]))

# Статус коды
sum by (status_code) (rate(http_requests_total[5m]))

# Ошибки (5xx)
sum by (status_code) (rate(http_requests_total{status_code=~"5.."}[5m]))

# Медленные запросы (> 1 сек)
rate(http_slow_requests_total[5m])

# Активные запросы
sum(http_requests_in_progress)

# User Agents
sum by (user_agent_family) (rate(http_requests_by_user_agent_total[5m]))

# Топ IP адресов
topk(10, sum by (client_ip) (rate(http_requests_by_ip_total[5m])))
```

## ✅ Результат

После этого вы получите рабочий dashboard с основными HTTP метриками! 🎉

Если возникнут проблемы - создавайте панели по одной, это надежнее чем импорт больших JSON файлов.
