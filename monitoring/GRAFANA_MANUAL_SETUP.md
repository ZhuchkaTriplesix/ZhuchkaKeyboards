# 🛠️ Ручная настройка Grafana для HTTP метрик

## 🚀 Быстрый старт

1. **Откройте Grafana**: http://localhost:3000
2. **Войдите**: `admin` / `admin123`

## 📊 Шаг 1: Добавление Prometheus datasource

1. Перейдите в **Configuration** → **Data Sources**
2. Нажмите **"Add data source"**
3. Выберите **"Prometheus"**
4. Настройте:
   - **Name**: `Prometheus`
   - **URL**: `http://prometheus:9090`
   - **Access**: `Server (default)`
5. Нажмите **"Save & test"**

✅ Должно появиться: "Data source is working"

## 📈 Шаг 2: Импорт Dashboard "Application Overview"

1. Перейдите в **+** → **Import**
2. Скопируйте и вставьте JSON:

```json
{
  "id": null,
  "title": "ZhuchkaKeyboards - Application Overview",
  "uid": "zhuchka-overview",
  "tags": ["zhuchka", "application", "overview"],
  "style": "dark",
  "timezone": "browser",
  "panels": [
    {
      "id": 1,
      "title": "HTTP Requests Rate",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total[5m]))",
          "refId": "A"
        }
      ],
      "gridPos": { "h": 4, "w": 6, "x": 0, "y": 0 },
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
    },
    {
      "id": 2,
      "title": "HTTP Request Rate by Endpoint",
      "type": "timeseries",
      "targets": [
        {
          "expr": "sum by (endpoint) (rate(http_requests_total[5m]))",
          "refId": "A",
          "legendFormat": "{{endpoint}}"
        }
      ],
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 4 },
      "fieldConfig": {
        "defaults": {
          "unit": "reqps"
        }
      }
    },
    {
      "id": 3,
      "title": "HTTP Status Codes",
      "type": "piechart",
      "targets": [
        {
          "expr": "sum by (status_code) (rate(http_requests_total[5m]))",
          "refId": "A",
          "legendFormat": "{{status_code}}"
        }
      ],
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 4 }
    }
  ],
  "time": { "from": "now-30m", "to": "now" },
  "refresh": "5s",
  "schemaVersion": 30,
  "version": 1
}
```

3. Нажмите **"Load"**
4. Выберите **Prometheus** datasource
5. Нажмите **"Import"**

## 🎯 Шаг 3: Создание простого HTTP метрики dashboard

1. Перейдите в **+** → **Dashboard**
2. Нажмите **"Add visualization"**
3. Выберите **Prometheus** datasource
4. Добавьте метрики:

### Panel 1: Request Rate
- **Query**: `rate(http_requests_total[5m])`
- **Legend**: `{{method}} {{endpoint}} ({{status_code}})`
- **Visualization**: Time series

### Panel 2: Response Time
- **Query**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Legend**: `95th percentile`
- **Unit**: seconds

### Panel 3: Error Rate
- **Query**: `rate(http_errors_by_type_total[5m]) / rate(http_requests_total[5m])`
- **Legend**: `Error Rate`
- **Unit**: percent (0.0-1.0)

### Panel 4: User Agents
- **Query**: `sum by (user_agent_family) (rate(http_requests_by_user_agent_total[5m]))`
- **Visualization**: Pie chart

## 🔍 Полезные запросы

```promql
# Общий RPS
sum(rate(http_requests_total[5m]))

# Топ эндпоинтов
topk(10, sum by (endpoint) (rate(http_requests_total[5m])))

# Медленные запросы
rate(http_slow_requests_total[5m])

# Активные запросы
sum(http_requests_in_progress)

# Размер ответов
rate(http_response_size_bytes_sum[5m]) / rate(http_response_size_bytes_count[5m])
```

## 🎨 Настройка алертов

1. В dashboard нажмите на панель → **Edit**
2. Перейдите в **Alert** tab
3. Нажмите **"Create alert rule"**
4. Настройте условия (например, error rate > 5%)

## ✅ Проверка

Сгенерируйте трафик для тестирования:

```bash
# PowerShell
for ($i=1; $i -le 20; $i++) { 
  curl http://localhost:8001/api/health -UseBasicParsing | Out-Null
  curl http://localhost:8001/api/metrics-summary -UseBasicParsing | Out-Null
  Start-Sleep 1 
}
```

Теперь в Grafana должны появиться данные! 🎉

## 🔧 Экспорт/Импорт

- **Экспорт**: Dashboard settings → JSON Model → Copy
- **Импорт**: + → Import → Paste JSON

---

Готово! Ваши HTTP метрики теперь визуализированы в Grafana! 📊
